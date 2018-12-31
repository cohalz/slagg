import json
import urllib.request
import os
import boto3
from boto3.dynamodb.conditions import Key


def handler(e, context):

    print(e)

    body = json.loads(e['body'])

    print(body)

    out = {}

    if 'challenge' in body:
        out['statusCode'] = 200
        out['body'] = body['challenge']
        return out

    event = body['event']

    post_channel = e['queryStringParameters'].get('channel')

    if 'subtype' in event:
        out['statusCode'] = 200
        out['body'] = 'bot'
        return out

    dynamo = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

    slack_token = os.environ["SLACK_TOKEN"]

    slack_webhook = os.environ["SLACK_WEBHOOK"]

    user_id = event['user']
    channel_id = event['channel']

    user = get_from_dynamo(dynamo, user_id)

    if user is None:
        user = get_user(user_id, slack_token)
        dynamo.put_item(Item=user)

    channel = get_from_dynamo(dynamo, channel_id)

    if channel is None:
        channel = get_channel(channel_id, slack_token)
        dynamo.put_item(Item=channel)

    payload = create_payload(event, user, channel, post_channel)

    post_slack(payload, slack_webhook)

    out['statusCode'] = 200
    out['body'] = "ok"

    return out


def post_slack(payload, slack_webhook):
    headers = {
        "X-Slack-No-Retry": 1
    }
    json_data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        slack_webhook, headers=headers, data=json_data, method='POST')
    with urllib.request.urlopen(request) as response:
        return response.getcode(), response.read().decode('utf-8')


def get_user(user_id, token):
    url = 'https://slack.com/api/users.info?token=' + \
        token + \
        '&user=' + user_id

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    user = json.loads(response.read().decode('utf-8'))['user']
    return {
        'id': user_id,
        'name': user['name'],
        'icon': user['profile']['image_72']
    }


def get_channel(channel_id, token):
    url = 'https://slack.com/api/channels.info?token=' + \
        token + \
        '&channel=' + channel_id

    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    channel = json.loads(response.read().decode('utf-8'))['channel']
    return {
        'id': channel_id,
        'name': channel['name']
    }


def create_payload(event, user, channel, post_channel):
    payload = {
        'icon_url': user['icon'],
        'username': user['name'],
        'unfurl_links': True,
        'unfurl_media': True,
        'link_names': 1,
        'text': event['text'].replace('\\', ''),
        'attachments': [
            {
                'footer': '#' + channel['name'],
                'ts': event['event_ts']
            }
        ]
    }
    if post_channel is not None:
        payload['channel'] = post_channel
    return payload


def get_from_dynamo(dynamo, id):
    items = dynamo.query(KeyConditionExpression=Key('id').eq(id))

    if items['Count'] == 0:
        return None

    return items['Items'][0]

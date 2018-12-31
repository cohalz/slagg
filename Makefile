AWS_PROFILE=default
SERVICE_NAME=slagg
BUCKET_NAME=
CFN_CMD=aws --profile $(AWS_PROFILE) cloudformation
TMP_TEMPLATE=tmp_template.yml
STACK_NAME=$(SERVICE_NAME)-stack

deploy:
	$(CFN_CMD) package \
		--template-file template.yml \
		--output-template-file $(TMP_TEMPLATE) \
		--s3-bucket $(BUCKET_NAME) 
	$(CFN_CMD) deploy \
		--template-file $(TMP_TEMPLATE) \
		--stack-name $(STACK_NAME) \
		--capabilities CAPABILITY_NAMED_IAM
	rm $(TMP_TEMPLATE)

delete:
	$(CFN_CMD) delete-stack \
		--stack-name $(STACK_NAME)
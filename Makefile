.PHONY: clean
clean:
	rm -rf build

.PHONY: install
install:
	poetry install

.PHONY: lint
lint:
	poetry run ruff check cfn_elastic_ip_asg_attachment

.PHONY: test
test: lint

.PHONY: package
package: clean install test
	sh package.sh

.PHONY: template
template: package
	aws cloudformation package --template-file ./stacks/lambda.yml --s3-bucket $$ARTIFACTS_BUCKET --s3-prefix artifacts/cfn-elastic-ip-asg-attachment --output-template-file ./stacks/lambda.yml

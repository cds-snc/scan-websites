# OWASP Zap scan initiator Lambda

## Running locally

Requires that the container defined in *runners/owasp-zap* to be deployed to a ECS cluster using the container definition from *terragrunt/env/owasp-zap/container-definitions*

### Launch Lambda container

`docker run -e CLUSTER="[ECS_CLUSTER_ARN]" -e PRIVATE_SUBNETS="[COMMA_SEPERATED_AWS_SUBNET]" -e REPORT_DATA_BUCKET="[OUTPUT_S3_BUCKET_NAME]" -e SECURITY_GROUP="[AWS_SECURITY_GROUP]" -e TASK_DEF_ARN="[TASK_DEF_ARN]" -e AWS_ACCESS_KEY_ID="foo" -e AWS_SECRET_ACCESS_KEY="bar" -e AWS_SESSION_TOKEN="foobar" -e AWS_DEFAULT_REGION="ca-central-1" -p 9000:8080 scan-websites/scanners/owasp-zap:latest`

### Post SNS event to Lambda container

`curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"Records":[{"EventSource":"aws:sns","EventVersion":"1.0","EventSubscriptionArn":"arn:aws:sns:ca-central-1:507252742351:owasp-zap-urls","Sns":{"Type":"Notification","MessageId":"95df01b4-ee98-5cb9-9903-4c221d41eb5e","TopicArn":"arn:aws:sns:ca-central-1:507252742351:owasp-zap-urls","Subject":"example subject","Message":"{\"id\":\"1\", \"url\":\"https:\/\/www.example.com\"}","Timestamp":"1970-01-01T00:00:00.000Z","SignatureVersion":"1","Signature":"EXAMPLE","SigningCertUrl":"EXAMPLE","UnsubscribeUrl":"EXAMPLE","MessageAttributes":{"Test":{"Type":"String","Value":"TestString"},"TestBinary":{"Type":"Binary","Value":"TestBinary"}}}}]}'`
#!/bin/bash

echo 
#curl "http://scanner-github:8080/2015-03-31/functions/function/invocations" -d '{ }'

curl "http://scanner-github:8080/2015-03-31/functions/function/invocations" -d '{
  "Records": [
    {
      "EventSource": "aws:sns",
      "EventVersion": "1.0",
      "EventSubscriptionArn": "arn:aws:sns:ca-central-1:{{{accountId}}}:ExampleTopic",
      "Sns": {
        "Type": "Notification",
        "MessageId": "",
        "TopicArn": "",
        "Subject": "",
        "Message": "{\"org\": \"cds-snc\", \"repo\": \"covid-alert-server\", \"token\": \"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\"}",
        "Timestamp": "1970-01-01T00:00:00.000Z",
        "SignatureVersion": "1",
        "Signature": "EXAMPLE",
        "SigningCertUrl": "EXAMPLE",
        "UnsubscribeUrl": "EXAMPLE",
        "MessageAttributes": {
          "Test": {
            "Type": "String",
            "Value": "TestString"
          },
          "TestBinary": {
            "Type": "Binary",
            "Value": "TestBinary"
          }
        }
      }
    }
  ]
}' | jq
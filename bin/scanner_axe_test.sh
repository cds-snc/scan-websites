#!/bin/bash

echo 
curl "http://scanner-axe:8080/2015-03-31/functions/function/invocations" -d '{
  "Records": []}' | jq
  
  
 
#   [{
#     "EventVersion": "",
#     "EventSubscriptionArn":  "",
#     "EventSource": "",
#     "Sns": {
#       "SignatureVersion": "",
#       "Timestamp": "",
#       "Signature": "",
#       "SigningCertUrl": "",
#       "MessageId": "",
#       "Message": "",
#       "MessageAttributes": {},
#       "Type": "",
#       "UnsubscribeUrl": "",
#       "TopicArn": "",
#       "Subject": ""
#     },
#   }],
# }' |jq


package main

import (
	"context"
	"encoding/json"
	"log"

	events "github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

type ScanEvent struct {
	Org   string `json:"org"`
	Repo  string `json:"repo"`
	Token string `json:"token"`
}

func HandleRequest(ctx context.Context, e events.SNSEvent) (string, error) {
	log.Print("Starting scanner")
	var msg ScanEvent
	if err := json.Unmarshal([]byte(e.Records[0].SNS.Message), &msg); err != nil {
		log.Panic(err)
	}

	results, err := query(msg.Token, msg.Org, msg.Repo)
	if err != nil {
		log.Panic(err)
	}

	if err := saveResults(*results); err != nil {
		log.Panic(err)
	}
	return "success", nil
}

func main() {
	lambda.Start(HandleRequest)
}

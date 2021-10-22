package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/shurcooL/githubv4"
)

func query(token string, org string, repo string) (*complianceScan, error) {

	log.Printf("Running query on %s/%s", org, repo)

	variables := map[string]interface{}{
		"Name":  githubv4.String(repo),
		"Owner": githubv4.String(org),
	}

	var cQuery complianceQuery

	client := getGHv4Client(token)
	if err := client.Query(context.Background(), &cQuery, variables); err != nil {
		return nil, err
	}

	var scan complianceScan
	scan.QueryResults = cQuery
	scan.ScanId = fmt.Sprintf("%s.%s", org, repo)

	return &scan, nil
}

func saveResults(r complianceScan) error {

	rJson, _ := json.Marshal(r)

	input := &s3.PutObjectInput{
		Bucket: aws.String("local-bucket"),
		Key:    aws.String(r.ScanId),
		Body:   bytes.NewReader(rJson),
	}

	client := getAwsS3Client()

	_, err := client.PutObject(context.TODO(), input)
	if err != nil {
		return err
	}

	return nil
}

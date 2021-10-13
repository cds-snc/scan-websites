package main

import (
	"bytes"
	"context"
	"encoding/json"
	"log"
	"os"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/google/uuid"
	"github.com/shurcooL/githubv4"
	"golang.org/x/oauth2"
)

func getGHv4Client() *githubv4.Client {

	src := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: os.Getenv("COMPLIANCE_CHECKER")},
	)
	httpClient := oauth2.NewClient(context.Background(), src)

	return githubv4.NewClient(httpClient)
}

func query(org string, repo string) (*complianceScan, error) {

	log.Printf("Running query on %s/%s", org, repo)

	variables := map[string]interface{}{
		"Name":  githubv4.String(repo),
		"Owner": githubv4.String(org),
	}

	var cQuery complianceQuery

	client := getGHv4Client()
	if err := client.Query(context.Background(), &cQuery, variables); err != nil {
		return nil, err
	}

	var scan complianceScan
	scan.QueryResults = cQuery
	scan.ScanId = uuid.New()

	return &scan, nil
}

func getAwsS3Client() *s3.Client {

	awsRegion := "ca-central-1"
	awsEndpoint := "http://localstack:4566"

	customResolver := aws.EndpointResolverFunc(func(service, region string) (aws.Endpoint, error) {
		if awsEndpoint != "" {
			return aws.Endpoint{
				PartitionID:   "aws",
				URL:           awsEndpoint,
				SigningRegion: awsRegion,
			}, nil
		}

		// returning EndpointNotFoundError will allow the service to fallback to it's default resolution
		return aws.Endpoint{}, &aws.EndpointNotFoundError{}
	})

	awsCfg, err := config.LoadDefaultConfig(context.TODO(),
		config.WithRegion(awsRegion),
		config.WithEndpointResolver(customResolver),
	)
	if err != nil {
		log.Panicf("Cannot load the AWS configs: %s", err)
	}

	return s3.NewFromConfig(awsCfg)
}

func saveResults(r complianceScan) error {

	rJson, _ := json.Marshal(r)

	input := &s3.PutObjectInput{
		Bucket: aws.String("local-bucket"),
		Key:    aws.String(r.ScanId.String()),
		Body:   bytes.NewReader(rJson),
	}

	client := getAwsS3Client()

	_, err := client.PutObject(context.TODO(), input)
	if err != nil {
		return err
	}

	return nil
}

func main() {
	if len(os.Args) == 2 {
		log.Panic("Missing org and repo name")
	}

	results, err := query(os.Args[1], os.Args[2])
	if err != nil {
		log.Panic(err)
	}

	if err := saveResults(*results); err != nil {
		log.Panic(err)
	}

}

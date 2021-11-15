package main

import (
	"context"
	"log"
	"os"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/shurcooL/githubv4"
	"golang.org/x/oauth2"
)

func getGHv4Client(token string) *githubv4.Client {

	src := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: token},
	)
	httpClient := oauth2.NewClient(context.Background(), src)

	return githubv4.NewClient(httpClient)
}

func getAwsS3Client() *s3.Client {

	if os.Getenv("AWS_LOCALSTACK") == "" {
		cfg, err := config.LoadDefaultConfig(context.TODO())
		if err != nil {
			panic(err)
		}

		return s3.NewFromConfig(cfg)
	}

	awsRegion := "ca-central-1"
	awsEndpoint := "http://localstack:4566"

	customResolver := aws.EndpointResolverFunc(func(service, region string) (aws.Endpoint, error) {
		if awsEndpoint != "" {
			return aws.Endpoint{
				PartitionID:       "aws",
				URL:               awsEndpoint,
				SigningRegion:     awsRegion,
				HostnameImmutable: true,
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

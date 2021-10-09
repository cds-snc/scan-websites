package main

import (
	"context"
	"log"
	"os"

	"github.com/davecgh/go-spew/spew"
	"github.com/shurcooL/githubv4"
	"golang.org/x/oauth2"
)

func getClient() *githubv4.Client {

	src := oauth2.StaticTokenSource(
		&oauth2.Token{AccessToken: os.Getenv("COMPLIANCE_CHECKER")},
	)
	httpClient := oauth2.NewClient(context.Background(), src)

	return githubv4.NewClient(httpClient)
}

func main() {
	if len(os.Args) == 2 {
		log.Panic("Missing org and repo name")
	}

	repo := os.Args[2]
	org := os.Args[1]
	log.Printf("Checking settings for: %s/%s\n", org, repo)

	variables := map[string]interface{}{
		"Name":  githubv4.String(repo),
		"Owner": githubv4.String(org),
	}

	client := getClient()
	// Use client...
	err := client.Query(context.Background(), &complianceQuery, variables)

	if err != nil {
		log.Fatal(err)
		// Handle error.
	}
	spew.Dump(complianceQuery)
}

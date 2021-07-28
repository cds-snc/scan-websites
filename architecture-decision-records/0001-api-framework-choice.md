# 1. API framework Choice

Date: 2021-07-28

## Status

Accepted

## Context

We need to choose an API framework that can run inside a container inside a lambda and has enough out of the box features to make development overly laborious. It should also be performant and provide easy integration with third party tooling to access databases, crawl websites, and dispatch messages into queue infrastructure.

## Decision

We decided to use [Fast API](https://fastapi.tiangolo.com/) for the following reasons

- Python is a widely used language at CDS
- Auto-generates API spec
- It has a smaller setup requirements than Django and Flask
- It works with an ASGI handler inside Lambdas
- Strong documentation and tutorials around integration with ORMs and other Python libraries

## Consequences

- The API needs to be developed in Python
- Third party libraries ideally all be in Python
- We will have a language hegemony because aXe is written in Type/Javascript

import { Impl, convertEventToRecords } from "./impl";
import { SNSEvent, SNSEventRecord, SNSMessage } from "aws-lambda";
import { CreateStateMachineInput } from "aws-sdk/clients/stepfunctions";
import AWS = require("aws-sdk");

const mockResponse = {
  failures: [{}],
  tasks: [
    {
      clusterArn: "12345",
    },
  ],
};

jest.mock("aws-sdk", () => {
  const mockStepFunctions = {
    createStateMachine: jest.fn().mockReturnThis(),
    listStateMachines: jest.fn().mockReturnThis(),
    startExecution: jest.fn().mockReturnThis(),
    promise: jest.fn(() => {
      return { Body: JSON.stringify(mockResponse) };
    }),
  };
  return {
    __esModule: true,
    StepFunctions: jest.fn(() => mockStepFunctions),
  };
});

describe("Impl", () => {
  const OLD_ENV = process.env;
  beforeEach(() => {
    jest.resetModules(); // Most important - it clears the cache
    process.env = { ...OLD_ENV }; // Make a copy
  });
  describe("is trigged by SNS", () => {
    const stepfunctions = new AWS.StepFunctions();
    test("Launches ecs task and returns true", async () => {
      process.env.PRIVATE_SUBNETS = "10.0.0.0/16,10.0.0.0/16";
      process.env.SECURITY_GROUP = "foo,bar";
      process.env.TASK_DEF_ARN =
        "arn:aws:ecs:us-west-2:123456789012:task-definition/TaskDefinitionFamily:1";
      process.env.STEP_FUNC_ROLE_ARN =
        "arn:aws:ecs:us-west-2:123456789012:task-definition/TaskDefinitionFamily:1";
      process.env.CLUSTER = "zap";
      process.env.MIN_ECS_CAPACITY = "1";
      process.env.MAX_ECS_CAPACITY = "5";
      process.env.SCAN_THREADS = "3";
      const records = [
        {
          payload: {
            id: "bar",
            name: "owasp-zap",
            url: "https://example.com/",
          },
          html: "",
        },
        {
          payload: {
            id: "baz",
            name: "nuclei",
            url: "https://example.com/",
          },
          html: "",
        },
      ];

      const response = await Impl(records, stepfunctions);

      const definition = {
        Version: "1.0",
        Comment: "Run ECS/Fargate tasks",
        TimeoutSeconds: 7200 * records.length,
        StartAt: "1",
        States: {
          "1": {
            Type: "Task",
            Resource: "arn:aws:states:::ecs:runTask.waitForTaskToken",
            Parameters: {
              CapacityProviderStrategy: [
                { Base: 1, CapacityProvider: "FARGATE_SPOT", Weight: 5 },
                { Base: 0, CapacityProvider: "FARGATE", Weight: 1 },
              ],
              Cluster: "zap",
              "TaskDefinition.$": "$.payload.task_def",
              Overrides: {
                ContainerOverrides: [
                  {
                    "Name.$": "$.payload.image",
                    Environment: [
                      { Name: "SCAN_URL", "Value.$": "$.payload.url" },
                      { Name: "SCAN_ID", "Value.$": "$.payload.id" },
                      { Name: "SCAN_THREADS", Value: process.env.SCAN_THREADS },
                      {
                        Name: "REPORT_DATA_BUCKET",
                        "Value.$": "$.payload.report_bucket",
                      },
                      {
                        Name: "TASK_TOKEN_ENV_VARIABLE",
                        "Value.$": "$$.Task.Token",
                      },
                    ],
                  },
                ],
              },
              NetworkConfiguration: {
                AwsvpcConfiguration: {
                  SecurityGroups: ["foo,bar"],
                  Subnets: ["10.0.0.0/16", "10.0.0.0/16"],
                },
              },
            },
            Next: "2",
            End: false,
          },
          "2": {
            Type: "Task",
            Resource: "arn:aws:states:::ecs:runTask.waitForTaskToken",
            Parameters: {
              CapacityProviderStrategy: [
                { Base: 1, CapacityProvider: "FARGATE_SPOT", Weight: 5 },
                { Base: 0, CapacityProvider: "FARGATE", Weight: 1 },
              ],
              Cluster: "zap",
              "TaskDefinition.$": "$.payload.task_def",
              Overrides: {
                ContainerOverrides: [
                  {
                    "Name.$": "$.payload.image",
                    Environment: [
                      { Name: "SCAN_URL", "Value.$": "$.payload.url" },
                      { Name: "SCAN_ID", "Value.$": "$.payload.id" },
                      { Name: "SCAN_THREADS", Value: "3" },
                      {
                        Name: "REPORT_DATA_BUCKET",
                        "Value.$": "$.payload.report_bucket",
                      },
                      {
                        Name: "TASK_TOKEN_ENV_VARIABLE",
                        "Value.$": "$$.Task.Token",
                      },
                    ],
                  },
                ],
              },
              NetworkConfiguration: {
                AwsvpcConfiguration: {
                  SecurityGroups: ["foo,bar"],
                  Subnets: ["10.0.0.0/16", "10.0.0.0/16"],
                },
              },
            },
            End: true,
          },
        },
      };

      const req: CreateStateMachineInput = {
        name: "owasp-zap_nuclei",
        definition: JSON.stringify(definition),
        roleArn: process.env.STEP_FUNC_ROLE_ARN,
      };

      expect(stepfunctions.createStateMachine).toHaveBeenCalledWith(req);
      expect(response).toBe(true);
    });
  });
});

describe("convertEventToRecords", () => {
  it("handles sns", async () => {
    const payload = JSON.stringify({
      key: "bar",
      url: "https://example.com/",
      name: "owasp-zap",
    });

    const msg = { Message: payload } as SNSMessage;
    const record = { Sns: msg } as SNSEventRecord;
    const event = { Records: [record] } as SNSEvent;

    const records = await convertEventToRecords(event);
    expect(records.length).toBe(1);
  });

  it("handles sns with multiple scans", async () => {
    const payload = JSON.stringify([
      {
        key: "bar",
        url: "https://example.com/",
        name: "owasp-zap",
      },
      {
        key: "baz",
        url: "https://example.com/",
        name: "nuclei",
      },
    ]);

    const msg = { Message: payload } as SNSMessage;
    const record = { Sns: msg } as SNSEventRecord;
    const event = { Records: [record] } as SNSEvent;

    const records = await convertEventToRecords(event);
    expect(records.length).toBe(2);
  });
});

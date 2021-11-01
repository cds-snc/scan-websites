import { Impl, convertEventToRecords } from "./impl";
import { SNSEvent, SNSEventRecord, SNSMessage } from "aws-lambda";
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
      process.env.TASK_DEF_ARN =
        "arn:aws:ecs:us-west-2:123456789012:task-definition/TaskDefinitionFamily:1";
      process.env.STEP_FUNC_ROLE_ARN = "arn:aws:ecs:us-west-2:123456789012:task-definition/TaskDefinitionFamily:1";
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

      expect(stepfunctions.createStateMachine).toHaveBeenCalledWith({
        name: 'active_scan',
        definition: expect.any(String),
        roleArn: process.env.STEP_FUNC_ROLE_ARN,
      });
      expect(response).toBe(true);
    });
  });
});

describe("convertEventToRecords", () => {
  it("handles sns", async () => {
    const payload = JSON.stringify({
      key: "bar",
      url: "https://example.com/",
    });

    const msg = { Message: payload } as SNSMessage;
    const record = { Sns: msg } as SNSEventRecord;
    const event = { Records: [record] } as SNSEvent;

    const records = await convertEventToRecords(event);
    expect(records.length).toBe(1);
  });
});

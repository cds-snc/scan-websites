import { Impl, convertEventToRecords } from "./impl";
import { SNSEvent, SNSEventRecord, SNSMessage } from "aws-lambda";
import AWS = require("aws-sdk");

jest.mock("aws-sdk", () => {
  const mockStepFunctions = {
    startExecution: jest.fn().mockReturnThis(),
    promise: jest.fn(() => {
      return {
        nextToken: "string",
        stateMachines: [
          {
            creationDate: 123,
            name: "foo",
            stateMachineArn: "123",
            type: "STANDARD",
          },
        ],
      };
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
      process.env.STEP_FUNC_ARN =
        "arn:aws:ecs:us-west-2:123456789012:task-definition/TaskDefinitionFamily:1";
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

      const params = {
        stateMachineArn: process.env.STEP_FUNC_ARN,
        input: JSON.stringify({
          payload: [
            { id: "bar", name: "owasp-zap", url: "https://example.com/" },
            { id: "baz", name: "nuclei", url: "https://example.com/" },
          ],
        }),
      };

      expect(stepfunctions.startExecution).toHaveBeenCalledWith(params);
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

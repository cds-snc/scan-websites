import {
  Impl,
  convertEventToRecords,
  isStringEmptyUndefinedOrNull,
} from "./impl";
import {
  S3Event,
  S3EventRecord,
  SNSEvent,
  SNSEventRecord,
  SNSMessage,
} from "aws-lambda";
import { Page, Browser } from "./common/browser";

const mockHTML = ` <!DOCTYPE html>
      <html lang="en">
        <head>
            <title>Test</title>
        </head>
        <body>
            <main><h1>Test</h1></main>
        </body>
      </html>`;

const mockReport = {
  testEngine: { version: "foo" },
  inapplicable: [{ id: "a" }],
  incomplete: [{ id: "a" }, { id: "b" }],
  violations: [
    { id: "a", impact: "hot", nodes: ["a"], tags: ["a"] },
    { id: "b", impact: "cold", nodes: ["b"], tags: ["a"] },
  ],
  passes: [{ id: "a" }, { id: "b" }, { id: "c" }],
};

const mockFileBody = {
  key: "bar",
  html: { slug: "slug", fragment: mockHTML },
};

const page: Page = {
  goto: async () => null,
  screenshot: async () => Buffer.from("I'm a string!", "utf-8"),
  setBypassCSP: async () => null,
  setContent: async () => null,
  setUserAgent: async () => null,
};

const browser: Browser = {
  close: async () => null,
  newPage: async () => page,
};

jest.mock("@axe-core/puppeteer", () => ({
  __esModule: true,
  default: jest.fn().mockImplementation(() => {
    return {
      withTags: () => ({
        analyze: () => mockReport,
      }),
    };
  }),
}));

const storeMock = {
  getObject: jest.fn().mockReturnThis(),
  putObject: jest.fn().mockReturnThis(),
  promise: jest.fn(),
};

describe("Impl", () => {
  describe("is trigged by SQS", () => {
    test("opens the URL in chrome, runs axe, saves a screenshot, writes a compressed report to a bucket, and returns true", async () => {
      const records = [
        {
          payload: {
            key: "bar",
            url: "https://example.com/",
          },
          html: "",
        },
      ];

      const response = await Impl(
        records,
        browser,
        storeMock,
        "databucketName",
        "screenshotBucketName"
      );

      expect(storeMock.putObject).toHaveBeenCalledWith({
        Bucket: "screenshotBucketName",
        Body: Buffer.from("I'm a string!", "utf-8"),
        ContentType: "image/png",
        Key: "bar.png",
        ACL: "public-read",
      });

      expect(storeMock.putObject).toHaveBeenCalledWith({
        Bucket: "databucketName",
        Body: JSON.stringify({
          url: "https://example.com/",
          key: "bar",
          report: mockReport,
        }),
        ContentType: "application/json",
        Key: "bar.json",
      });
      expect(response).toBe(true);
    });
  });

  test("saves a axe report from an S3 trigger and returns true", async () => {
    const payloads = [
      {
        payload: mockFileBody,
        html: mockFileBody.html,
      },
    ];

    const result = await Impl(
      payloads,
      browser,
      storeMock,
      "databucketName",
      "screenshotBucketName"
    );
    expect(storeMock.putObject).toHaveBeenCalledWith({
      Bucket: "databucketName",
      Body: JSON.stringify({
        url: "slug",
        key: "bar",
        report: mockReport,
      }),
      ContentType: "application/json",
      Key: "bar.json",
    });
    expect(result).toEqual(true);
  });
});

describe("convertEventToRecords", () => {
  it("handles sqs", async () => {
    const payload = JSON.stringify({
      key: "bar",
      url: "https://example.com/",
    });

    const msg = { Message: payload } as SNSMessage;
    const record = { Sns: msg } as SNSEventRecord;
    const event = { Records: [record] } as SNSEvent;

    const records = await convertEventToRecords(event, storeMock);
    expect(records.length).toBe(1);
    expect(records[0].html).toBe("");
  });

  it("handles s3", async () => {
    const record = {
      s3: {
        bucket: { name: "foo" },
        object: { key: "bar" },
      },
    } as S3EventRecord;
    const event = { Records: [record] } as S3Event;

    storeMock.promise = jest.fn(async () => ({
      Body: JSON.stringify(mockFileBody),
    }));

    const records = await convertEventToRecords(event, storeMock);
    expect(storeMock.getObject).toHaveBeenCalledWith({
      Bucket: "foo",
      Key: "bar",
    });
    expect(records.length).toBe(1);
    expect(records[0].html).toStrictEqual({
      slug: "slug",
      fragment: mockHTML,
    });
  });
});

describe("isStringEmpty", () => {
  it("handles undefined", () => {
    expect(isStringEmptyUndefinedOrNull(undefined)).toBe(true);
  });

  it("handles null", () => {
    expect(isStringEmptyUndefinedOrNull(null)).toBe(true);
  });

  it("handles empty string", () => {
    expect(isStringEmptyUndefinedOrNull("")).toBe(true);
  });

  it("handles non-empty strings", () => {
    expect(isStringEmptyUndefinedOrNull("foo")).toBe(false);
  });
});

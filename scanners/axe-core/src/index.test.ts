import {
  handler,
  convertEventToRecords,
  isStringEmptyUndefinedOrNull,
} from "./index";
import {
  S3Event,
  S3EventRecord,
  SNSEvent,
  SNSEventRecord,
  SNSMessage,
} from "aws-lambda";

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
  html: { slug: mockHTML },
};

const browser = {
  close: () => ({}),
  newPage: () => ({
    $$eval: () => [
      "https://example.com/a",
      "https://example.com/a#foo",
      "https://example.com/a.png?#foo",
      "https://example.com/#/foo",
    ],
    goto: () => ({}),
    content: () => mockHTML,
    screenshot: () => Buffer.from("I'm a string!", "utf-8"),
    setBypassCSP: () => ({}),
    setContent: () => mockHTML,
    setUserAgent: () => ({}),
  }),
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
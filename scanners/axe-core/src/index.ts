import { S3Event, SNSEvent } from "aws-lambda";
import { S3, Credentials, ConfigurationOptions } from "aws-sdk";
import puppeteer from "puppeteer";
import { Impl, convertEventToRecords } from "./impl";

const useLocalstack = process.env.AWS_LOCALSTACK || false;

const options: ConfigurationOptions = {};

if (useLocalstack) {
  const creds: Credentials = new Credentials({
    accessKeyId: "foo",
    secretAccessKey: "bar",
  });
  options.credentials = creds;
  options.region = "ca-central-1";
}

const s3 = new S3(options);

export const handler = async (event: SNSEvent | S3Event): Promise<boolean> => {
  const options = [
    "--allow-running-insecure-content",
    "--autoplay-policy=user-gesture-required",
    "--disable-component-update",
    "--disable-domain-reliability",
    "--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process",
    "--disable-print-preview",
    "--disable-setuid-sandbox",
    "--disable-site-isolation-trials",
    "--disable-speech-api",
    "--disable-web-security",
    "--disk-cache-size=33554432",
    "--enable-features=SharedArrayBuffer",
    "--hide-scrollbars",
    "--ignore-gpu-blocklist",
    "--in-process-gpu",
    "--mute-audio",
    "--no-default-browser-check",
    "--no-pings",
    "--no-sandbox",
    "--no-zygote",
    "--use-gl=swiftshader",
    "--window-size=1920,1080",
    "--single-process",
  ];

  const viewport = {
    deviceScaleFactor: 1,
    hasTouch: false,
    height: 1080,
    isLandscape: true,
    isMobile: false,
    width: 1920,
  };

  const browser = await puppeteer.launch({
    args: options,
    defaultViewport: viewport,
    headless: true,
    ignoreHTTPSErrors: true,
  });

  const reportBucket = process.env.REPORT_DATA_BUCKET;
  const screenshotBucket = process.env.SCREENSHOT_BUCKET;
  const records = await convertEventToRecords(event, s3);
  return await Impl(records, browser, s3, reportBucket, screenshotBucket);
};

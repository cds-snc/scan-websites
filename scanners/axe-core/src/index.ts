import { S3Event, SNSEvent } from "aws-lambda";
import { S3 } from "aws-sdk";
import puppeteer from 'puppeteer';
import { Impl, convertEventToRecords } from "./impl";

const s3 = new S3();

export const handler = async (event: SNSEvent | S3Event): Promise<boolean> => {
  const browser = await puppeteer.launch({
    args: ['--disable-dev-shm-usage', '--no-sandbox'],
    ignoreHTTPSErrors: true,
  });

  const report_bucket = process.env.REPORT_DATA_BUCKET;
  const screenshot_bucket = process.env.SCREENSHOT_BUCKET

  const records = await convertEventToRecords(event, s3);
  return Impl(records, browser, s3, report_bucket, screenshot_bucket);
};
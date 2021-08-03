import { S3Event, SNSEvent } from "aws-lambda";
import { SNS, S3 } from "aws-sdk";
import puppeteer from 'puppeteer';
import { Impl, convertEventToRecords } from "./impl";

const s3 = new S3();
const sns = new SNS({ region: "ca-central-1" });

export const handler = async (event: SNSEvent | S3Event): Promise<boolean> => {
  const browser = await puppeteer.launch({
    args: ['--disable-dev-shm-usage', '--no-sandbox'],
    ignoreHTTPSErrors: true,
  });

  const records = await convertEventToRecords(event, s3);
  return Impl(records, browser, s3, sns);
};
import AxePuppeteer from "@axe-core/puppeteer";
import { S3Event, SNSEvent } from "aws-lambda";
import { SNS, S3 } from "aws-sdk";
import puppeteer from 'puppeteer';

const s3 = new S3();
const sns = new SNS({ region: "ca-central-1" });

const USER_AGENT =
  "Mozilla/5.0 (CDS-SNC A11Y Tools; Puppeteer) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36";

export const handler = async (event: SNSEvent | S3Event): Promise<boolean> => {
  console.log("HELLO")
  const browser = await puppeteer.launch({
    args: ['--disable-dev-shm-usage', '--no-sandbox'],
    ignoreHTTPSErrors: true,
  });

  const records = await convertEventToRecords(event);

  try {
    await asyncForEach(records, async (record: any) => {
      const payload = record.payload;
      let url = payload.url || "";
      const html = record.html;
      const page = await createNewPage(browser);

      // Run on URL if not empty
      if (url.trim() !== "") {
        await page.goto(url, { waitUntil: "networkidle0" });
      } else {
        let fragment: any = null;
        let slug: any = null;
        [slug, fragment] = Object.entries(html)[0];
        url = slug;
        await page.setContent(fragment, { waitUntil: "networkidle0" });
      }

      await takeScreenshot(payload.key, page);
      await createReport(page, payload);
    });
  } catch (error) {
    console.log(error);
    return error;
  } finally {
    if (browser !== null) {
      await browser.close();
    }
  }
  return true;
}

export async function convertEventToRecords(
  event: any,
): Promise<any[]> {
  const records: any[] = [];
  await asyncForEach(event.Records, async (record: any) => {
    // Parse the correct message body, SNS or S3
    if (record.hasOwnProperty("s3")) {
      const object = await s3
        .getObject({
          Bucket: record.s3.bucket.name,
          Key: record.s3.object.key,
        })
        .promise();

      const data = JSON.parse(object.Body.toString("utf-8"));
      records.push({
        payload: data,
        html: data.html,
      });
    } else {
      records.push({
        payload: JSON.parse(record.Sns.Message),
        html: "",
      });
    }
  });
  return records;
}

const createNewPage = async (browser: any) => {
  const page = await browser.newPage();
  await page.setBypassCSP(true);
  await page.setUserAgent(USER_AGENT);
  return page;
};

const createReport = async (
  page: any,
  payload: any,
) => {
  if (isStringEmptyUndefinedOrNull(process.env.REPORT_DATA_BUCKET)) {
    return;
  }

  const key = payload.key;
  const results = await new AxePuppeteer(page)
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"])
    .analyze();
  const report = results;

  // Save result to bucket
  const object = {
    key,
    report,
  };
  await s3
    .putObject({
      Bucket: process.env.REPORT_DATA_BUCKET,
      Key: `${key}.json`,
      Body: JSON.stringify(object),
      ContentType: "application/json",
    })
    .promise();
};

const takeScreenshot = async (key: string, page: any) => {
  if (isStringEmptyUndefinedOrNull(process.env.SCREENSHOT_BUCKET)) {
    return;
  }

  const screenshot = await page.screenshot({ fullPage: true });

  await s3
    .putObject({
      Bucket: process.env.SCREENSHOT_BUCKET,
      Key: `${key}.png`,
      Body: screenshot,
      ContentType: "image/png",
      ACL: "public-read",
    })
    .promise();
};

export async function asyncForEach<T>(
  array: T[],
  callback: (item: T, idx: number, ary: T[]) => void,
): Promise<void> {
  for (let index = 0; index < array.length; index++) {
    await callback(array[parseInt(`${index}`)], index, array);
  }
}

export const isStringEmptyUndefinedOrNull = (str: string): boolean =>
  str === undefined || str === null || str === "";
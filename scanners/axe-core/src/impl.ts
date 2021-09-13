import AxePuppeteer from "@axe-core/puppeteer";
import { asyncForEach } from "./common/foreach";
import { BlobStore } from "./common/blobstore";
import { Page, Browser } from "./common/browser";
import { Payload, Record } from "./common/record";

const USER_AGENT =
  "Mozilla/5.0 (CDS-SNC A11Y Tools; Puppeteer) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36";

export async function Impl(
  records: Record[],
  browser: Browser,
  store: BlobStore,
  reportBucket: string,
  screenshotBucket: string
): Promise<boolean> {
  try {
    await asyncForEach(records, async (record: Record) => {
      const payload = record.payload;
      let url = payload.url || "";

      const html = record.html;
      const page = await createNewPage(browser);

      // Run on URL if not empty
      if (url.trim() !== "") {
        await page.goto(url, { waitUntil: "networkidle0" });
      } else {
        let fragment = "";
        let slug = "";
        [slug, fragment] = Object.entries(html)[0];
        url = slug;
        await page.setContent(fragment, { waitUntil: "networkidle0" });
      }
      console.log(`url: ${url}`)
      await takeScreenshot(store, payload.id, page, screenshotBucket);
      console.log("screenshot taken")
      await createReport(store, url, page, payload, reportBucket);
      console.log("report saved")
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
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types
  event: any,
  store: BlobStore
): Promise<Record[]> {
  const records: Record[] = [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  await asyncForEach(event.Records, async (record: any) => {
    // Parse the correct message body, SNS or S3
    // eslint-disable-next-line no-prototype-builtins
    if (record.hasOwnProperty("s3")) {
      console.log("S3 event")
      const object = await store
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
      console.log("SNS event")
      records.push({
        payload: JSON.parse(record.Sns.Message),
        html: "",
      });
    }
  });
  return records;
}

export const isStringEmptyUndefinedOrNull = (str: string): boolean =>
  str === undefined || str === null || str === "";

const createNewPage = async (browser: Browser) => {
  const page = await browser.newPage();
  await page.setBypassCSP(true);
  await page.setUserAgent(USER_AGENT);
  return page;
};

const createReport = async (
  store: BlobStore,
  url: string,
  page: Page,
  payload: Payload,
  reportBucket: string
) => {
  if (isStringEmptyUndefinedOrNull(reportBucket)) {
    return;
  }

  const id = payload.id;
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore TS2345
  const results = await new AxePuppeteer(page)
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"])
    .analyze();
  const report = results;

  // Save result to bucket
  const object = {
    url,
    id,
    report,
  };
  await store
    .putObject({
      Bucket: reportBucket,
      Key: `${id}.json`,
      Body: JSON.stringify(object),
      ContentType: "application/json",
    })
    .promise();
};

const takeScreenshot = async (
  store: BlobStore,
  id: string,
  page: Page,
  screenshotBucket: string
) => {
  if (isStringEmptyUndefinedOrNull(screenshotBucket)) {
    return;
  }
  const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
  await page.setViewport({ width: 1920, height: bodyHeight });
  const screenshot = await page.screenshot({ fullPage: true });

  // Save result to bucket
  await store
    .putObject({
      Bucket: screenshotBucket,
      Key: `${id}.png`,
      Body: screenshot as Buffer | Uint8Array | string,
      ContentType: "image/png",
      ACL: "public-read",
    })
    .promise();
};

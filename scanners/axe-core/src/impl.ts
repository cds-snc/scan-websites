import AxePuppeteer from "@axe-core/puppeteer";
import { asyncForEach } from "./common/foreach";
import { BlobStore } from "./common/blobstore";
import { MessageBus } from "./common/message_bus";

const USER_AGENT =
    "Mozilla/5.0 (CDS-SNC A11Y Tools; Puppeteer) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36";

export async function Impl(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    records: any[],
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types
    browser: any,
    store: BlobStore,
    msgBus: MessageBus,
): Promise<boolean> {
    try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        await asyncForEach(records, async (record: any) => {
            const payload = record.payload;
            let url = payload.url || "";

            const html = record.html;
            const page = await createNewPage(browser);

            // Run on URL if not empty
            if (url.trim() !== "") {
                await page.goto(url, { waitUntil: "networkidle0" });
            } else {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                let fragment: any = null;
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                let slug: any = null;
                [slug, fragment] = Object.entries(html)[0];
                url = slug;
                await page.setContent(fragment, { waitUntil: "networkidle0" });
            }

            await takeScreenshot(store, payload.key, page);
            await createReport(store, url, page, payload);
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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function convertEventToRecords(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types
    event: any,
    store: BlobStore,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
): Promise<any[]> {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const records: any[] = [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    await asyncForEach(event.Records, async (record: any) => {
        // Parse the correct message body, SNS or S3
        // eslint-disable-next-line no-prototype-builtins
        if (record.hasOwnProperty("s3")) {
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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const createNewPage = async (browser: any) => {
    const page = await browser.newPage();
    await page.setBypassCSP(true);
    await page.setUserAgent(USER_AGENT);
    return page;
};

const createReport = async (
    store: BlobStore,
    url: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    page: any,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    payload: any,
) => {
    if (isStringEmptyUndefinedOrNull(process.env.REPORT_DATA_BUCKET)) {
        return;
    }

    const key = payload.key;
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore TS2345
    const results = await new AxePuppeteer(page)
        .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"])
        .analyze();
    const report = results;

    // Save result to bucket
    const object = {
        url,
        key,
        report
    };
    await store
        .putObject({
            Bucket: process.env.REPORT_DATA_BUCKET,
            Key: `${key}.json`,
            Body: JSON.stringify(object),
            ContentType: "application/json",
        })
        .promise();
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const takeScreenshot = async (store: BlobStore, key: string, page: any) => {
    if (isStringEmptyUndefinedOrNull(process.env.SCREENSHOT_BUCKET)) {
        return;
    }

    const screenshot = await page.screenshot({ fullPage: true });

    // Save result to bucket
    await store
        .putObject({
            Bucket: process.env.SCREENSHOT_BUCKET,
            Key: `${key}.png`,
            Body: screenshot,
            ContentType: "image/png",
            ACL: "public-read",
        })
        .promise();
};
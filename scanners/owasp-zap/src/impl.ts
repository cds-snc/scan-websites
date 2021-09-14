import { SNSEvent } from "aws-lambda";
import { asyncForEach } from "./common/foreach";
import { BlobStore } from "./common/blobstore";
import { Record } from "./common/record";
import { Runner } from "./common/runner";
import { WebRequest } from "./common/webrequest";

export async function Impl(
  records: Record[],
  runner: Runner,
  axios: WebRequest
): Promise<boolean> {
  try {
    await asyncForEach(records, async (record: Record) => {
      if (record.payload.hasOwnProperty("reportType")) {
        if (record.payload.reportType === "OWASP-Zap") {
          processZapReport(record, axios);
        }
      } else {
        runZapScan(record, runner);
      }
    });
  } catch (error) {
    console.log(error);
    return false;
  }
  return true;
}

export async function convertEventToRecords(
  event: SNSEvent,
  store: BlobStore
): Promise<Record[]> {
  const records: Record[] = [];
  await asyncForEach(event.Records, async (record: any) => {
    // Parse the correct message body, SNS or S3
    // eslint-disable-next-line no-prototype-builtins
    let payload = null;
    if (record.hasOwnProperty("s3")) {
      const object = await store
        .getObject({
          Bucket: record.s3.bucket.name,
          Key: record.s3.object.key,
        })
        .promise();
      payload = object.Body.toString("utf-8");
    } else {
      payload = record.Sns.Message;
    }

    if (payload !== null) {
      records.push({
        payload: JSON.parse(record.Sns.Message),
      });
    } else {
      throw new Error("payload is null");
    }
  });
  return records;
}

const runZapScan = async (record: Record, runner: Runner) => {
  const params = {
    launchType: "FARGATE",
    cluster: process.env.CLUSTER,
    taskDefinition: process.env.TASK_DEF_ARN,
    overrides: {
      containerOverrides: [
        {
          name: "runners-owasp-zap",
          environment: [{ name: "SCAN_URL", value: record.payload.url }],
        },
      ],
    },
    networkConfiguration: {
      awsvpcConfiguration: {
        securityGroups: [process.env.SECURITY_GROUP],
        subnets: process.env.PRIVATE_SUBNETS.split(","),
      },
    },
  };

  await runner.runTask(params).promise();
};

const processZapReport = async (record: Record, axios: WebRequest) => {
  try {
    await axios.post(`${process.env.DOMAIN}/scans/zapreport`, record.payload, {
      headers: {
        Authorization: process.env.PRIVATE_API_AUTH_TOKEN,
      },
    });
  } catch (exception) {
    throw Error(
      `ERROR received while importing ${record.payload.key}: ${exception}`
    );
  }
};

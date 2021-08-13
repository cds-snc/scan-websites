import { ECS } from "aws-sdk";
import { asyncForEach } from "./common/foreach";
import { Record } from "./common/record";

const ecs = new ECS({ region: "ca-central-1" });

export async function Impl(
  records: Record[],
): Promise<boolean> {
  try {
    await asyncForEach(records, async (record: Record) => {
       const params = {
        launchType: "FARGATE",
        cluster: process.env.CLUSTER,
        taskDefinition: process.env.TASK_DEF_ARN,
        overrides: {containerOverrides: [{name: "owasp_zap",environment: [{name: "SCAN_URL", value: record.payload.url}]}]},
        networkConfiguration: { awsvpcConfiguration: {securityGroups: [process.env.SECURITY_GROUP],subnets: process.env.PRIVATE_SUBNETS.split(',')}},
      };
      
      await ecs.runTask(params).promise();
    });
  } catch (error) {
    console.log(error);
    return false;
  }
  return true;
}

export async function convertEventToRecords(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/explicit-module-boundary-types
  event: any,
): Promise<Record[]> {
  const records: Record[] = [];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  await asyncForEach(event.Records, async (record: any) => {
    // Parse the correct message body, SNS or S3
    // eslint-disable-next-line no-prototype-builtins
    records.push({
      payload: JSON.parse(record.Sns.Message),
      html: "",
    });
  });
  return records;
}

export const isStringEmptyUndefinedOrNull = (str: string): boolean =>
  str === undefined || str === null || str === "";
import { SNSEvent, SNSEventRecord } from "aws-lambda";
import { asyncForEach } from "./common/foreach";
import { Record } from "./common/record";
import { Runner } from "./common/runner";

export async function Impl(
  records: Record[],
  runner: Runner
): Promise<boolean> {
  try {
    const scanInputs: any[] = []; // eslint-disable-line @typescript-eslint/no-explicit-any

    records.forEach((record) => {
      scanInputs.push(record.payload);
    });

    const params = {
      stateMachineArn: process.env.STEP_FUNC_ARN,
      input: JSON.stringify({ payload: scanInputs }),
    };

    await runner.startExecution(params).promise();
  } catch (error) {
    console.log(error);
    return false;
  }
  return true;
}

export async function convertEventToRecords(
  event: SNSEvent
): Promise<Record[]> {
  const records: Record[] = [];
  await asyncForEach(event.Records, async (record: SNSEventRecord) => {
    // Parse the SNS
    // eslint-disable-next-line no-prototype-builtins
    const messagePayload = JSON.parse(record.Sns.Message);
    if (Array.isArray(messagePayload)) {
      messagePayload.forEach((message) =>
        records.push({
          payload: message,
          html: "",
        })
      );
    } else {
      records.push({
        payload: messagePayload,
        html: "",
      });
    }
  });
  return records;
}

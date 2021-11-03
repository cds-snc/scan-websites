import { StepFunctions } from "aws-sdk";
import { SNSEvent } from "aws-lambda";
import { Impl, convertEventToRecords } from "./impl";

const stepfunctions = new StepFunctions({ region: "ca-central-1" });
export const handler = async (event: SNSEvent): Promise<boolean> => {
  const records = await convertEventToRecords(event);
  return Impl(records, stepfunctions);
};

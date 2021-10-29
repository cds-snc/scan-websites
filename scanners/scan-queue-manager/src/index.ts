import { StepFunctions } from "aws-sdk";
import { SNSEvent } from "aws-lambda";
import { Impl, convertEventToRecords } from "./impl";

export const handler = async (event: SNSEvent): Promise<boolean> => {
  const stepfunctions = new StepFunctions({ region: "ca-central-1" });
  const records = await convertEventToRecords(event);
  return Impl(records, stepfunctions);
};

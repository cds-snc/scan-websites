import { SNSEvent } from "aws-lambda";
import { Impl, convertEventToRecords } from "./impl";

export const handler = async (event: SNSEvent): Promise<boolean> => {
  const records = await convertEventToRecords(event);
  return Impl(records);
};

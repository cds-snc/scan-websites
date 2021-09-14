import axios from "axios";
import { ECS } from "aws-sdk";
import { SNSEvent } from "aws-lambda";
import { S3 } from "aws-sdk";
import { Impl, convertEventToRecords } from "./impl";

const s3 = new S3({ region: "ca-central-1" });

export const handler = async (event: SNSEvent): Promise<boolean> => {
  const ecs = new ECS({ region: "ca-central-1" });
  const records = await convertEventToRecords(event, s3);
  return Impl(records, ecs, axios);
};

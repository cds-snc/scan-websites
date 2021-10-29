import { SNSEvent, SNSEventRecord } from "aws-lambda";
import { asyncForEach } from "./common/foreach";
import { Record } from "./common/record";
import { StepFunctions } from "aws-sdk";
import { CreateStateMachineInput } from "aws-sdk/clients/stepfunctions";


export async function Impl(
  records: Record[],
  stepfunctions: StepFunctions,
): Promise<boolean> {
  try {
    const states: any[] = [];
    let stepCount = 1;
    await asyncForEach(records, async (record: Record) => {
      let state = {
        [stepCount.toString()]: {
          Type: "Task",
          Resource: "arn:aws:states:::ecs:runTask.sync",
          Parameters: {
            capacityProviderStrategy: [
              {
                base: parseInt(process.env.MIN_ECS_CAPACITY),
                capacityProvider: "FARGATE_SPOT",
                weight: parseInt(process.env.MAX_ECS_CAPACITY),
              },
              {
                base: 0,
                capacityProvider: "FARGATE",
                weight: parseInt(process.env.MIN_ECS_CAPACITY),
              },
            ],
            cluster: process.env.CLUSTER,
            taskDefinition: process.env.TASK_DEF_ARN,
            overrides: {
              containerOverrides: [
                {
                  name: "runners-owasp-zap",
                  environment: [
                    { name: "SCAN_URL", value: record.payload.url },
                    { name: "SCAN_ID", value: record.payload.id },
                    { name: "SCAN_THREADS", value: process.env.SCAN_THREADS },
                  ],
                },
              ],
            },
            networkConfiguration: {
              awsvpcConfiguration: {
                securityGroups: [process.env.SECURITY_GROUP],
                subnets: process.env.PRIVATE_SUBNETS.split(","),
              },
            },
          },
          End: true
        }
      };

      if (stepCount == records.length) {
        state[stepCount.toString()]["End"] = true;
      }
      states.push(state);
      stepCount++;
    });

    const definition = {
      Version: "1.0",
      Comment: "Run ECS/Fargate tasks",
      TimeoutSeconds: 7200 * records.length,
      StartAt: "0",
      States: states
    }

    const req: CreateStateMachineInput = {
      name: 'Active scan',
      definition: JSON.stringify(definition),
      roleArn: process.env.STEP_FUNC_ROLE_ARN
    };

    await stepfunctions.createStateMachine(req).promise();

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
    records.push({
      payload: JSON.parse(record.Sns.Message),
      html: "",
    });
  });
  return records;
}

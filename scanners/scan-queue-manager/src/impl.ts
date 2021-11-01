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
            CapacityProviderStrategy: [
              {
                Base: parseInt(process.env.MIN_ECS_CAPACITY),
                CapacityProvider: "FARGATE_SPOT",
                Weight: parseInt(process.env.MAX_ECS_CAPACITY),
              },
              {
                Base: 0,
                CapacityProvider: "FARGATE",
                Weight: parseInt(process.env.MIN_ECS_CAPACITY),
              },
            ],
            Cluster: process.env.CLUSTER,
            TaskDefinition: process.env.TASK_DEF_ARN,
            Overrides: {
              ContainerOverrides: [
                {
                  Name: "runners-owasp-zap",
                  Environment: [
                    { Name: "SCAN_URL", Value: record.payload.url },
                    { Name: "SCAN_ID", Value: record.payload.id },
                    { Name: "SCAN_THREADS", Value: process.env.SCAN_THREADS },
                  ],
                },
              ],
            },
            NetworkConfiguration: {
              AwsvpcConfiguration: {
                SecurityGroups: [process.env.SECURITY_GROUP],
                Subnets: process.env.PRIVATE_SUBNETS.split(","),
              },
            },
          },
          Next: "",
          End: false
        }
      };

      // Reached the end of the state machine sequence
      if (stepCount == records.length) {
        state[stepCount.toString()]["End"] = true;
        delete state[stepCount.toString()]["Next"]; 
      }else{
        state[stepCount.toString()]["Next"] = (stepCount+1).toString();
        delete state[stepCount.toString()]["End"]; 
      }
      states.push(state);
      stepCount++;
    });

    const definition = {
      Version: "1.0",
      Comment: "Run ECS/Fargate tasks",
      TimeoutSeconds: 7200 * records.length,
      StartAt: "1",
      States: Object.assign({}, ...states)
    }

    const req: CreateStateMachineInput = {
      name: 'active_scan',
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

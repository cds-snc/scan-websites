import { SNSEvent, SNSEventRecord } from "aws-lambda";
import { asyncForEach } from "./common/foreach";
import { Record } from "./common/record";
import { Runner } from "./common/runner";
import { scanReportBuckets, scanTaskArns } from "./common/config";
import { CreateStateMachineInput } from "aws-sdk/clients/stepfunctions";

export async function Impl(
  records: Record[],
  runner: Runner
): Promise<boolean> {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const states: any[] = [];
    const machineName: string[] = [];
    let stepCount = 1;
    await asyncForEach(records, async (record: Record) => {
      const state = {
        [stepCount.toString()]: {
          Type: "Task",
          Resource: "arn:aws:states:::ecs:runTask.waitForTaskToken",
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
            "TaskDefinition.$": "$.payload.taskDef",
            Overrides: {
              ContainerOverrides: [
                {
                  "Name.$": "$.payload.image",
                  Environment: [
                    { Name: "SCAN_URL", "Value.$": "$.payload.url" },
                    { Name: "SCAN_ID", "Value.$": "$.payload.id" },
                    { Name: "SCAN_THREADS", Value: process.env.OWASP_ZAP_SCAN_THREADS },
                    {
                      Name: "REPORT_DATA_BUCKET",
                      "Value.$": "$.payload.reportBucket",
                    },
                    {
                      Name: "TASK_TOKEN_ENV_VARIABLE",
                      "Value.$": "$$.Task.Token",
                    },
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
          End: false,
        },
      };

      // Reached the end of the state machine sequence
      if (stepCount === records.length) {
        state[stepCount.toString()].End = true;
        delete state[stepCount.toString()].Next;
      } else {
        state[stepCount.toString()].Next = (stepCount + 1).toString();
      }
      states.push(state);
      machineName.push(`${record.payload.name}`);
      stepCount++;
    });

    const definition = {
      Version: "1.0",
      Comment: "Run ECS/Fargate tasks",
      TimeoutSeconds: 7200 * records.length,
      StartAt: "1",
      States: Object.assign({}, ...states),
    };

    const stateMachineName = machineName.join("_");
    const req: CreateStateMachineInput = {
      name: stateMachineName,
      definition: JSON.stringify(definition),
      roleArn: process.env.STEP_FUNC_ROLE_ARN,
    };

    let stateMachineArn = "";
    // Check if state machine already exists that can process this workload
    runner.listStateMachines({}, function (err, data) {
      if (err) console.log(err, err.stack);
      // an error occurred
      else {
        data.stateMachines.forEach((stateMachine) => {
          if (stateMachine.name === stateMachineName) {
            stateMachineArn = stateMachine.stateMachineArn;
          }
        });
      }
    });

    // If state machine doesn't exist create a new one that can process this scan sequence
    if (stateMachineArn === "") {
      const response = await runner.createStateMachine(req).promise();
      stateMachineArn = response.stateMachineArn;
    }

    await asyncForEach(records, async (record: Record) => {
      record.payload.image = `runners-${record.payload.name}`;
      record.payload.taskDef = (scanTaskArns as { [index: string]: string })[
        record.payload.name
      ];
      record.payload.reportBucket = (
        scanReportBuckets as { [index: string]: string }
      )[record.payload.name];

      const params = {
        stateMachineArn: stateMachineArn,
        input: JSON.stringify({ ...record }),
      };
      await runner.startExecution(params).promise();
    });
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

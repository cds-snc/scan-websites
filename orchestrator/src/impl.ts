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
  // Sort so that dynamic items will always be generated in the same order
  records.sort((a: Record, b: Record) => {
    return a.payload.name.localeCompare(b.payload.name);
  });

  try {
    const states: any[] = []; // eslint-disable-line @typescript-eslint/no-explicit-any
    const machineName: string[] = [];
    const scanInputs: any[] = []; // eslint-disable-line @typescript-eslint/no-explicit-any
    let stepCount = 0;
    records.forEach((record: Record) => {
      const state = {
        [record.payload.name]: {
          Type: "Task",
          Resource: "arn:aws:states:::ecs:runTask.waitForTaskToken",
          InputPath: `$.${record.payload.name}`,
          ResultPath: "$.resultPath",
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
            "TaskDefinition.$": "$.taskDef",
            Overrides: {
              ContainerOverrides: [
                {
                  "Name.$": "$.image",
                  Environment: [
                    { Name: "SCAN_URL", "Value.$": "$.url" },
                    { Name: "SCAN_ID", "Value.$": "$.id" },
                    {
                      Name: "SCAN_THREADS",
                      Value: process.env.OWASP_ZAP_SCAN_THREADS,
                    },
                    {
                      Name: "REPORT_DATA_BUCKET",
                      "Value.$": "$.reportBucket",
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
          TimeoutSeconds: 7200,
          HeartbeatSeconds: 300,
          Next: "",
          End: false,
        },
      };

      // Reached the end of the state machine sequence
      if (stepCount === records.length - 1) {
        state[record.payload.name].End = true;
        delete state[record.payload.name].Next;
        delete state[record.payload.name].ResultPath;
      } else {
        state[record.payload.name].Next = records[stepCount + 1].payload.name;
        delete state[record.payload.name].End;
      }
      states.push(state);
      machineName.push(`${record.payload.name}`);

      // Scan inputs for this step
      record.payload.image = `runners-${record.payload.name}`;
      record.payload.taskDef = (scanTaskArns as { [index: string]: string })[
        record.payload.name
      ];
      record.payload.reportBucket = (
        scanReportBuckets as { [index: string]: string }
      )[record.payload.name];
      record.payload.resultPath = null; // Use original input instead of output from previous step
      scanInputs.push({ [record.payload.name]: record.payload });

      stepCount++;
    });

    const definition = {
      Version: "1.0",
      Comment: "Run ECS/Fargate tasks",
      TimeoutSeconds: 7200 * records.length,
      StartAt: records[0].payload.name,
      States: Object.assign({}, ...states),
    };

    // Sort the list of scans so that each group of scans consistently generate the same name
    const stateMachineName: string = machineName.join("_");
    const req: CreateStateMachineInput = {
      name: stateMachineName,
      definition: JSON.stringify(definition),
      roleArn: process.env.STEP_FUNC_ROLE_ARN,
    };

    // Check if state machine already exists that can process this workload
    const listMachinesResult = await runner.listStateMachines({}).promise();
    const machines = listMachinesResult.stateMachines;
    let stateMachineArn = machines.find(
      (machine) => machine.name === stateMachineName
    )?.stateMachineArn;

    // If state machine doesn't exist create a new one that can process this scan sequence
    if (stateMachineArn === undefined) {
      const response = await runner.createStateMachine(req).promise();
      stateMachineArn = response.stateMachineArn;
    }

    const params = {
      stateMachineArn: stateMachineArn,
      input: JSON.stringify(Object.assign({}, ...scanInputs)),
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

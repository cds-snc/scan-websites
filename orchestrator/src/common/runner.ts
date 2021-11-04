import { PromiseResult } from "aws-sdk/lib/request";
import { StepFunctions, AWSError } from "aws-sdk";

export type StartResponse = {
  promise(): Promise<
    PromiseResult<StepFunctions.StartExecutionOutput, AWSError>
  >;
};

export interface Runner {
  startExecution(
    params: StepFunctions.StartExecutionInput,
    callback?: (err: AWSError, data: StepFunctions.StartExecutionOutput) => void
  ): StartResponse;
}

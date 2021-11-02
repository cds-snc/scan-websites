import { PromiseResult } from "aws-sdk/lib/request";
import { StepFunctions, AWSError } from "aws-sdk";

export type ListResponse = {
  promise(): Promise<PromiseResult<StepFunctions.ListStateMachinesOutput, AWSError>>;
};

export type CreateResponse = {
  promise(): Promise<PromiseResult<StepFunctions.CreateStateMachineOutput, AWSError>>;
};

export type StartResponse = {
  promise(): Promise<PromiseResult<StepFunctions.StartExecutionOutput, AWSError>>;
};

export interface Runner {
  listStateMachines(
    params: StepFunctions.ListStateMachinesInput,
    callback?: (err: AWSError, data: StepFunctions.ListStateMachinesOutput) => void
  ): ListResponse;

  createStateMachine(
    params: StepFunctions.CreateStateMachineInput,
    callback?: (err: AWSError, data: StepFunctions.CreateStateMachineOutput) => void
  ): CreateResponse;

  startExecution(
    params: StepFunctions.StartExecutionInput,
    callback?: (err: AWSError, data: StepFunctions.StartExecutionOutput) => void
  ): StartResponse;
}

import { PromiseResult } from "aws-sdk/lib/request";
import { ECS, AWSError } from "aws-sdk";

export type Task = {
    promise(): Promise<PromiseResult<ECS.RunTaskResponse, AWSError>>
}

export interface Runner {
    runTask(params: ECS.Types.RunTaskRequest, callback?: (err: AWSError, data: ECS.Types.RunTaskResponse) => void): Task;
}
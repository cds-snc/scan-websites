import { Promisable } from "./response";

export interface PublishResponse { }

export interface PublishRequest {
    Message: string;
    TopicArn?: string;
}

export interface MessageBusError { }

export interface MessageBus {
    publish(params: PublishRequest): Promisable<PublishResponse, MessageBusError>;
}
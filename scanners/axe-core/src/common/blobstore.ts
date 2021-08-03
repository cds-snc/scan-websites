import { Promisable } from "./response";

export interface Readable { }

export type Body = Buffer | Uint8Array | string | Readable;

export interface GetObjectRequest {
    Bucket: string;
    Key: string;
}

export interface GetObjectResponse {
    Body?: Body;
}

export interface PutObjectRequest {
    Bucket: string;
    Key: string;
    Body: Body;
    ContentType: string;
    ACL?: string;
}

export interface PutObjectResponse { }

export interface BlobstoreError { }

export interface BlobStore {
    getObject(
        params: GetObjectRequest
    ): Promisable<GetObjectResponse, BlobstoreError>;

    putObject(
        params: PutObjectRequest
    ): Promisable<PutObjectResponse, BlobstoreError>;
}
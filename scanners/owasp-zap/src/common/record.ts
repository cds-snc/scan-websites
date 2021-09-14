export type Payload = {
  id: string;
  url?: string;
  messageType?: string;
  reportType?: string;
  createdAt?: string;
  importToSecurityhub?: string;
  s3Bucket?: string;
  key?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  report?: any;
};

export type Record = {
  payload: Payload;
};

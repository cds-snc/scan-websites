export type HtmlPayload = {
  fragment: string;
  slug: string;
};

export type Payload = {
  html?: HtmlPayload;
  id: string;
  name: string;
  url?: string;
  image?: string;
  taskDef?: string;
  reportBucket?: string;
  resultPath?: string | null;
};

export type Record = {
  html: HtmlPayload | string;
  payload: Payload;
};

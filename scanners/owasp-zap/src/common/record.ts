export type HtmlPayload = {
  fragment: string;
  slug: string;
};

export type Payload = {
  html?: HtmlPayload;
  id: string;
  url?: string;
};

export type Record = {
  html: HtmlPayload | string;
  payload: Payload;
};

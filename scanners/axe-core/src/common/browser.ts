import { HTTPResponse, ScreenshotOptions, WaitForOptions } from "puppeteer";

export type Page = {
  goto(S: string, O?: WaitForOptions): Promise<HTTPResponse | void>;
  screenshot(O?: ScreenshotOptions): Promise<string | void | Buffer>;
  setBypassCSP(B: boolean): Promise<void>;
  setContent(S: string, O?: WaitForOptions): Promise<void>;
  setUserAgent(S: string): Promise<void>;
};

export interface Browser {
  close(): Promise<void>;
  newPage(): Promise<Page>;
}

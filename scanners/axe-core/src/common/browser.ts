import { EvaluateFn, HTTPResponse, ScreenshotOptions, Viewport, WaitForOptions } from "puppeteer";

export type Page = {
  evaluate(F: EvaluateFn): Promise<number>;
  goto(S: string, O?: WaitForOptions): Promise<HTTPResponse | void>;
  screenshot(O?: ScreenshotOptions): Promise<string | void | Buffer>;
  setBypassCSP(B: boolean): Promise<void>;
  setContent(S: string, O?: WaitForOptions): Promise<void>;
  setViewport(O?: Viewport): Promise<void>;
  setUserAgent(S: string): Promise<void>;
};

export interface Browser {
  close(): Promise<void>;
  newPage(): Promise<Page>;
}

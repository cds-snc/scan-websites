import { HTTPResponse } from "puppeteer"

export type Page = {
    goto(S: string, O: any): Promise<HTTPResponse | void>;
    screenshot(O: any): Promise<string | void | Buffer>;
    setBypassCSP(B: boolean): Promise<void>;
    setContent(S: string, O: any): Promise<void>;
    setUserAgent(S: string): Promise<void>;
}

export interface Browser {
    close(): Promise<void>;
    newPage(): Promise<Page>;
}
export type Page = {
    goto(S: string, O: any): Promise<any>;
    screenshot(O: any): Promise<string | void | Buffer>;
    setBypassCSP(B: boolean): Promise<any>;
    setContent(S: string, O: any): Promise<any>;
    setUserAgent(S: string): Promise<any>;
}

export interface Browser {
    close(): Promise<void>;
    newPage(): Promise<Page>;
}
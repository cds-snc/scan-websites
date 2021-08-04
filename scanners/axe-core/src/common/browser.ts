export type Page = {
    goto(S: string, O): Promise<void>;
    screenshot(O): Promise<Buffer>;
    setBypassCSP(B: boolean): Promise<void>;
    setContent(S: string, O): Promise<void>;
    setUserAgent(S: string): Promise<void>;
}

export interface Browser {
    close(): Promise<void>;
    newPage(): Promise<Page>;
}
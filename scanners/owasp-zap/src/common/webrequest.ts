import { AxiosRequestConfig, AxiosResponse } from "axios";

export interface WebRequest {
  post(
    url: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse>;
}

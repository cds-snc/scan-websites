import { AxiosRequestConfig, AxiosResponse } from "axios";

export interface WebRequest {
  post(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse>;
}

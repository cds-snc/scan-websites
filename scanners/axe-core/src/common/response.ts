export interface Response<D, E> {
    data: D | void;
    error: E | void;
}

export type PromiseResult<D, E> = D & { $response?: Response<D, E> };

export interface Promisable<D, E> {
    promise: () => Promise<PromiseResult<D, E>>;
}
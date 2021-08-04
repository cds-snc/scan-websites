// Helper function to run asynchronous foreach loop.
export async function asyncForEach<T>(
  array: T[],
  callback: (item: T, idx: number, ary: T[]) => void,
): Promise<void> {
  for (let index = 0; index < array.length; index++) {
    await callback(array[parseInt(`${index}`)], index, array);
  }
}

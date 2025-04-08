from itertools import islice
from typing import Iterator, Iterable, List

def chunked(iterable: Iterable, chunk_size: int) -> Iterator[List]:
    """
    Yields chunks of `chunk_size` from an iterable.
    """
    iterator = iter(iterable)
    while chunk := list(islice(iterator, chunk_size)):
        yield chunk

if __name__ == "__main__":
    a = [2,92,8,2,72,8,30,3,93,92,2,1,9,19,2,932,9,39,29,91,91,92,9,3,2,2,3,3,2,1,1,]
    for c in chunked(a, 4):
        print(c)

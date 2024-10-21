---
layout: sub-navigation
order: 4
title: Async interface
---


An async interface is provided via the function `async_stream_unzip`. Its usage is exactly the same as `stream_zip` except that:

1. The input must be an async iterable of bytes.
2. The member files are output as an async iterable of tuples.
3. The data of each member file is returned as an async iterable of bytes.

```python
from stream_unzip import async_stream_unzip
import httpx

async def zipped_chunks(client):
    # Iterable that yields the bytes of a zip file
    async with client.stream('GET', 'https://www.example.com/my.zip') as r:
        async for chunk in r.aiter_bytes(chunk_size=65536):
            yield chunk

async def main():
    async with httpx.AsyncClient() as client:
        async for file_name, file_size, unzipped_chunks in async_stream_unzip(
                zipped_chunks(client),
                password=b'my-password',
        ):
            async for chunk in unzipped_chunks:
                print(chunk)

asyncio.run(main())
```

The async interface is compatible with both [asyncio](https://docs.python.org/3/library/asyncio.html) and [trio](https://github.com/python-trio/trio).

> ### Warnings
>
> Under the hood `async_stream_unzip` uses threads as a layer over the synchronous `stream_unzip` function. This has two consequences:
>
> 1. A possible performance penalty over a theoretical implementation that is pure async without threads.
>
> 2. The [contextvars](https://docs.python.org/3/library/contextvars.html) context available in the async iterables of files or data is a shallow copy of the context where async_stream_unzip is called from.
>
>   This means that existing context variables are available inside the input iterable, but any changes made to the context itself from inside the iterable will not propagate out to the original context. Changes made to mutable data structures that are part of the context, for example dictionaries, will propagate out.

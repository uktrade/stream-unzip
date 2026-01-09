---
layout: sub-navigation
sectionKey: API reference
eleventyNavigation:
    parent: API reference
order: 1
caption: API reference
title: Functions
---


### stream_unzip.stream_unzip

#### Function signature
```python
def stream_unzip(
    zipfile_chunks: Iterable[bytes],
    password: Optional[bytes]=None,
    chunk_size: int=65536,
    allow_zip64: bool=True,
    allowed_encryption_mechanisms: Container=(
        stream_unzip.NO_ENCRYPTION,
        stream_unzip.ZIP_CRYPTO,
        stream_unzip.AE_1,
        stream_unzip.AE_2,
        stream_unzip.AES_128,
        stream_unzip.AES_192,
        stream_unzip.AES_256,
    ),
) -> Generator[Tuple[bytes, int, Generator[bytes, Any, None]], Any, None]:
```

### stream_unzip.async_stream_unzip

#### Function signature

```python
async def async_stream_unzip(
    chunks: AsyncIterable[bytes],
    password: Optional[bytes]=None,
    chunk_size: int=65536,
    allow_zip64: bool=True,
    allowed_encryption_mechanisms: Container=(
        stream_unzip.NO_ENCRYPTION,
        stream_unzip.ZIP_CRYPTO,
        stream_unzip.AE_1,
        stream_unzip.AE_2,
        stream_unzip.AES_128,
        stream_unzip.AES_192,
        stream_unzip.AES_256,
    ),
) -> AsyncGenerator[Tuple[bytes, int, AsyncGenerator[bytes, None]], None]:
```

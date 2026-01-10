---
layout: sub-navigation
sectionKey: API reference
eleventyNavigation:
    parent: API reference
order: 1
caption: API reference
title: Functions
---


## stream_unzip.stream_unzip

### Signature

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

<hr class="govuk-section-break govuk-section-break--l">

### Parameters

| Name                                    | Type            | Description
| --------------------------------------- | --------------- | -------------------------------------
| zipfile_chunks                          | Iterable[bytes] | The raw bytes of the ZIP
| password                                | Optional[bytes] | The password for all member files of the ZIP
| chunk_size                              | int             | How many bytes to fetch from `zipfile_chunks` before attempting to process them
| allow_zip64                             | bool            | Whether to allow ZIP64 member files.
| allowed_<wbr>encryption_<wbr>mechanisms | Container       | The allowed encryption mechanisms of the ZIP. If a member file with an encryption type is encountered an exception is thrown. See [Encryption types](/api/encryption-types/) for more details.


### Returns

#### Type

Generator[Tuple[bytes, int, Generator[bytes, Any, None]], Any, None]

#### Type

Each item yielded by the generator is a member file, which is a tuple of file name, size in bytes of the member file, and a generator of the bytes of the member file.

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### Raises

See [Exception hierarchy](/api/exception-hierarchy/) for the possible exceptions that can be raised. Exceptions raised from iterating the `zipfile_chunks` iterable are passed through to client code unchanged.

<hr class="govuk-section-break govuk-section-break--l">

## stream_unzip.async_stream_unzip

### Signature

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

<hr class="govuk-section-break govuk-section-break--l">

### Parameters

| Name                                    | Type                 | Description
| --------------------------------------- | -------------------- | -------------------------------------
| chunks                                  | AsyncIterable[bytes] | The raw bytes of the ZIP
| password                                | Optional[bytes]      | The password for all member files of the ZIP
| chunk_size                              | int                  | How many bytes to fetch from `zipfile_chunks` before attempting to process them
| allow_zip64                             | bool                 | Whether to allow ZIP64 member files.
| allowed_<wbr>encryption_<wbr>mechanisms | Container            | The allowed encryption mechanisms of the ZIP. If a member file with an encryption type is encountered an exception is thrown. See [Encryption types](/api/encryption-types/) for more details.


### Returns

#### Type

AsyncGenerator[Tuple[bytes, int, AsyncGenerator[bytes, None]], None]

#### Description

Each item yielded by the async generator is a member file, which is a tuple of file name, size in bytes of the member file, and a async generator of the bytes of the member file.

<hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible">

### Raises

See [Exception hierarchy](/api/exception-hierarchy/) for the possible exceptions that can be raised. Exceptions raised from iterating the `zipfile_chunks` iterable are passed through to client code unchanged.

---
layout: sub-navigation
order: 1
title: Get started
---


## Prerequisites

Python 3.7.1+


## Installation

You can install stream-unzip and its dependencies from [PyPI](https://pypi.org/project/stream-unzip/) using pip.

```shell
pip install stream-unzip
```

This installs the latest version of stream-unzip, and the latest compatible version of all of its dependencies.

If you regularly install stream-unzip, such as during application deployment, to avoid unexpected changes as new versions are released, you can pin to specific versions. [Poetry](https://python-poetry.org/) or [pip-tools](https://pip-tools.readthedocs.io/en/latest/) are popular tools that can be used for this.


## Usage

A single function is exposed, `stream_unzip`, that takes a single argument: an iterable that should yield the bytes of a ZIP file [with no zero-length chunks]. It returns an iterable, where each yielded item is a tuple of the file name, file size [`None` if this is not known], and another iterable itself yielding the unzipped bytes of that file.

```python
from stream_unzip import stream_unzip
import httpx

def zipped_chunks():
    # Iterable that yields the bytes of a zip file
    with httpx.stream('GET', 'https://www.example.com/my.zip') as r:
        yield from r.iter_bytes(chunk_size=65536)

for file_name, file_size, unzipped_chunks in stream_unzip(zipped_chunks()):
    # unzipped_chunks must be iterated to completion or UnfinishedIterationError will be raised
    for chunk in unzipped_chunks:
        print(chunk)
```

The file name and file size are extracted as reported from the file. If you don't trust the creator of the ZIP file, these should be treated as untrusted input.


## Decrypting password protected files

The `stream_unzip` function can decrypt password-protected ZIP files by passing a `bytes` instance password as the `password` argument. The basic usage is as follows.

```python
from stream_unzip import stream_unzip

for file_name, file_size, unzipped_chunks in stream_unzip(zipped_chunks(), password=b'my-password'):
    for chunk in unzipped_chunks:
        pass
```

This by default decrypts files encrypted with ZipCrypto, WinZip's AE-1 and AE-2 that use any of AES 128, 192 and 256, and silently allows member files that are not password-protected at all even if a password has been passed. For security reasons, for example to give a stronger guarantee a file has not been modified during transit, you can tighten this, and only allow certain encryption mechanisms. You can do this by overriding the `allowed_encryption_mechanisms` argument. The default behaviour of allowing all mechanisms is shown below.

```python
from stream_unzip import stream_unzip, NO_ENCRYPTION, ZIP_CRYPTO, AE_1, AE_2, AES_128, AES_192, AES_256

for file_name, file_size, unzipped_chunks in stream_unzip(
    zipped_chunks(),
    password=b'my-password', allowed_encryption_mechanisms=(
        NO_ENCRYPTION,
        ZIP_CRYPTO,
        AE_1,
        AE_2,
        AES_128,
        AES_192,
        AES_256,
    ),
):
    for chunk in unzipped_chunks:
        pass
```

To forbid a mechanism remove its corresponding constant from the tuple passed as the `allowed_encryption_mechanisms` parameter. If a password is supplied but a file is encrypted with a mechanism not allowed by the `allowed_encryption_mechanisms` parameter, an exception will be raised.

Note that the decryption of AES-encrypted ZIP files requires a combination of at least one of the AE_* constants, and at least one of the AES_* constants. The most secure combination would be AE_2 and AE_256, as in the following example.

```python
from stream_unzip import stream_unzip, AE_2, AES_256

for file_name, file_size, unzipped_chunks in stream_unzip(
    zipped_chunks(),
    password=b'my-password', allowed_encryption_mechanisms=(
        AE_2,
        AES_256,
    ),
):
    for chunk in unzipped_chunks:
        pass
```

Future versions of stream-unzip fewer mechanisms may have a stricter default, for example by only allowing AE-2 with AES 256 as in this example.

While the ZIP format allows for a different password per member file, stream-unzip only allows a single password that is applied to all the member files. Also, if no password is supplied, the `allowed_encryption_mechanisms` parameter is ignored, which means non-encrypted files will be uncompressed until reaching an encrypted file at which point an exception will be raised.

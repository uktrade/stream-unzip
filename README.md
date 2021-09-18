# stream-unzip [![CircleCI](https://circleci.com/gh/uktrade/stream-unzip.svg?style=shield)](https://circleci.com/gh/uktrade/stream-unzip) [![Test Coverage](https://api.codeclimate.com/v1/badges/02144f986cd3eecf4a0b/test_coverage)](https://codeclimate.com/github/uktrade/stream-unzip/test_coverage)

Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or any of its uncompressed files. Both AES and legacy (ZipCrypto/Zip 2.0) encrypted/password-protected ZIPs are supported.

While the ZIP format does have its main directory at the end, each compressed file in the archive is prefixed with a header that contains its name. Also, the Deflate algorithm that most ZIP files use indicates when it has reached the end of the stream of a member file. These facts make the streaming decompression of ZIP archives possible.


## Installation

```bash
pip install stream-unzip
```


## Usage

A single function is exposed, `stream_unzip`, that takes a single argument: an iterable that should yield the bytes of a ZIP file [with no zero-length chunks]. It returns an iterable, where each yielded item is a tuple of the file name, file size [`None` if this is not known], and another iterable itself yielding the unzipped bytes of that file.

```python
from stream_unzip import stream_unzip
import httpx

def zipped_chunks():
    # Iterable that yields the bytes of a zip file
    with httpx.stream('GET', 'https://www.example.com/my.zip') as r:
        yield from r.iter_bytes(chunk_size=65536)

for file_name, file_size, unzipped_chunks in stream_unzip(zipped_chunks(), password=b'my-password'):
    for chunk in unzipped_chunks:
        print(chunk)
```

The file name and file size are extracted as reported from the file. If you don't trust the creator of the ZIP file, these should be treated as untrusted input.


## Exceptions

Exceptions raised by the source iterable are passed through `stream_unzip` unchanged. Other exceptions derive from `UnzipError` which itself derives from Python's built-in `ValueError`.

### Hierarchy

- **ValueError**

  - **UnzipError**

    Base class for all explicitly-thrown exceptions

    - **PasswordError**

        - **MissingPasswordError**

          A file requires a password, but it was not supplied.

          - **MissingZipCryptoPasswordError**

            A file is legacy (ZipCrypto/Zip 2.0) encrypted, but a password was not supplied.

          - **MissingAESPasswordError**

            A file is AES encrypted, but a password was not supplied.

        - **IncorrectPasswordError**

          An incorrect password was supplied. Note that due to nature of the ZIP file format, some incorrect passwords would not raise this exception, and instead raise a `DataError`, or even in pathalogical cases, not raise any exception.

          - **IncorrectZipCryptoPasswordError**

            An incorrect password was supplied for a legacy (ZipCrypto/Zip 2.0) encrypted file.

          - **IncorrectAESPasswordError**

            An incorrect password was supplied for an AES encrypted file.

    - **DataError**

      An issue with the ZIP bytes themselves was encountered.

      - **UnsupportedFeatureError**

        A file in the ZIP uses features that are unsupported.

        - **UnsupportedFlagsError**

        - **UnsupportedCompressionTypeError**

      - **UncompressError**

        - **DeflateError**

          An error in the deflate-compressed data meant it could not be decompressed.

      - **IntegrityError**

        - **HMACIntegrityError**

          The HMAC integrity check on AES encrypted bytes failed

        - **CRC32IntegrityError**

          The CRC32 integrity check on decrypted and decompressed bytes failed.

      - **TruncatedDataError**

        The stream of bytes ended unexpectedly.

      - **UnexpectedSignatureError**

        Each section of a ZIP file starts with a _signature_, and an unexpected one was encountered.

      - **MissingExtraError**

        Metadata known as *extra* that some ZIP files require is missing.

        - **MissingZip64ExtraError**

        - **MissingAESExtraError**

      - **TruncatedExtraError**

        Metadata known as *extra* that some ZIP files require is present, but too short.

        - **TruncatedZip64ExtraError**

        - **TruncatedAESExtraError**

      - **InvalidExtraError**

        Metadata known as *extra* that some ZIP files require is present, long enough, but holds an invalid value.

        - **InvalidAESKeyLengthError**

        AES key length specified in the ZIP is not any of 1, 2, or 3 (which correspond to 128, 192, and 256 bits respectively).

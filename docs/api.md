---
layout: sub-navigation
sectionKey: API reference
order: 2
title: API reference
---


## Modules

stream-unzip exposes a single Python module: `stream_unzip`.


## Functions

The `stream_unzip` module exposes two functions:

- [`stream_unzip.stream_unzip`](/api/functions/#stream-unzip)
- [`stream_unzip.async_stream_unzip`](/api/functions/#async-stream-unzip)


## Encryption types

The `stream_unzip.stream_unzip` and `stream_unzip.async_stream_unzip` functions take an `allowed_encryption_mechanisms` argument, which is a container of zero or more of the following constants:

- [`stream_unzip.NO_ENCRYPTION`](/api/encryption-types/#stream-unzip-no-encryption)
- [`stream_unzip.ZIP_CRYPTO`](/api/encryption-types/#stream-unzip-zip-crypto)
- [`stream_unzip.AE_1`](/api/encryption-types/#stream-unzip-ae_1)
- [`stream_unzip.AE_2`](/api/encryption-types/#stream-unzip-ae_2)
- [`stream_unzip.AES_128`](/api/encryption-types/#stream-unzip-aes_128)
- [`stream_unzip.AES_192`](/api/encryption-types/#stream-unzip-aes_192)
- [`stream_unzip.AES_256`](/api/encryption-types/#stream-unzip-aes_256)


## Exceptions

Exceptions raised by the source iterable are passed through the `stream_unzip.stream_unzip` and `stream_unzip.async_stream_unzip` functions unchanged. All explicitly-thrown exceptions derive from `stream_unzip.UnzipError`.

Visit the [Exception hierarchy](/api/exception-hierarchy/) for details on all the exception types and how they relate to each other.

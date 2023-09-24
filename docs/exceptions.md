---
layout: sub-navigation
order: 3
title: Exceptions
---


Exceptions raised by the source iterable are passed through `stream_unzip` unchanged. Other exceptions are in the `stream_unzip` module, and derive from its `UnzipError`.


## Exception hierarchy

  - **UnzipError**

    Base class for all explicitly-thrown exceptions

    - **InvalidOperationError**

        - **UnfinishedIterationError**

            The unzipped chunks iterator of a member file has not been iterated to completion.

    - **UnzipValueError** (also inherits from the **ValueError** built-in)

        Base class for errors relating to invalid arguments

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

                - **UnsupportedZip64Error**

                    A Zip64 member file has been encounted but support has been disabled.

            - **UncompressError**

                - **BZ2Error**

                    An error in the bz2-compressed data meant it could not be decompressed.

                - **DeflateError**

                    An error in the deflate-compressed data meant it could not be decompressed.

            - **IntegrityError**

                - **HMACIntegrityError**

                    The HMAC integrity check on AES encrypted bytes failed

                - **CRC32IntegrityError**

                    The CRC32 integrity check on decrypted and decompressed bytes failed.

              - **SizeIntegrityError**

                - **UncompressedSizeIntegrityError**

                    The amount of uncompressed bytes of a member file did not match its metadata.

                - **CompressedSizeIntegrityError**

                    The amount of compressed bytes of a member file did not match its metadata.

            - **TruncatedDataError**

                The stream of bytes ended unexpectedly.

            - **UnexpectedSignatureError**

                Each section of a ZIP file starts with a _signature_, and an unexpected one was encountered.

            - **MissingExtraError**

                Metadata known as *extra* that some ZIP files require is missing.

                - **MissingAESExtraError**

            - **TruncatedExtraError**

                Metadata known as *extra* that some ZIP files require is present, but too short.

                - **TruncatedZip64ExtraError**

                - **TruncatedAESExtraError**

            - **InvalidExtraError**

                Metadata known as *extra* that some ZIP files require is present, long enough, but holds an invalid value.

                - **InvalidAESKeyLengthError**

                    AES key length specified in the ZIP is not any of 1, 2, or 3 (which correspond to 128, 192, and 256 bits respectively).

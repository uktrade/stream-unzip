# stream-unzip

[![PyPI version](https://badge.fury.io/py/stream-unzip.svg)](https://pypi.org/project/stream-unzip/) [![CircleCI](https://circleci.com/gh/uktrade/stream-unzip.svg?style=shield)](https://circleci.com/gh/uktrade/stream-unzip) [![Test Coverage](https://api.codeclimate.com/v1/badges/02144f986cd3eecf4a0b/test_coverage)](https://codeclimate.com/github/uktrade/stream-unzip/test_coverage)

Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or any of its uncompressed files.

To create ZIP files on the fly try [stream-zip](https://github.com/uktrade/stream-zip).


## Features

In addition to being memory efficient, stream-unzip supports:

- Deflate-compressed ZIPs. The is the historical standard for ZIP files.

- Deflate64-compressed ZIPs. These are created by certain versions of Windows Explorer in some circumstances. Python's zipfile module cannot open Deflate64-compressed ZIPs.

- Zip64 ZIP files. These are ZIP files that allow sizes far beyond the approximate 4GiB limit of the original ZIP format.

- WinZip-style AES-encryped ZIPs. Python's zipfile module cannot open AES-encryped ZIPs.

- Legacy-encrypted ZIP files. This is also known as ZipCrypto/Zip 2.0.

- ZIP files created by Java's ZipOutputStream that are larger than 4GiB. At the time of writing libarchive-based stream readers cannot read these without error.

---

Visit the [stream-unzip documentation](https://stream-unzip.docs.data.trade.gov.uk/) for usage instructions.

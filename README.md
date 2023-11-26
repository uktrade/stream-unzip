<!-- --8<-- [start:intro] -->
# stream-unzip

[![conda-forge package](https://img.shields.io/conda/v/conda-forge/stream-unzip?label=conda-forge&color=%234c1)](https://anaconda.org/conda-forge/stream-unzip) [![PyPI package](https://img.shields.io/pypi/v/stream-unzip?label=PyPI%20package&color=%234c1)](https://pypi.org/project/stream-unzip/) [![Test suite](https://img.shields.io/github/actions/workflow/status/uktrade/stream-unzip/test.yml?label=Test%20suite)](https://github.com/uktrade/stream-unzip/actions/workflows/test.yml) [![Code coverage](https://img.shields.io/codecov/c/github/uktrade/stream-unzip?label=Code%20coverage)](https://app.codecov.io/gh/uktrade/stream-unzip)

Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or any of its uncompressed files.
<!-- --8<-- [end:intro] -->

To create ZIP files on the fly try [stream-zip](https://github.com/uktrade/stream-zip).

<!-- --8<-- [start:features] -->
## Features

In addition to being memory efficient, stream-unzip supports:

- Deflate-compressed ZIPs. The is the historical standard for ZIP files.

- Deflate64-compressed ZIPs. These are created by certain versions of Windows Explorer in some circumstances. Python's zipfile module cannot open Deflate64-compressed ZIPs.

- Zip64 ZIP files. These are ZIP files that allow sizes far beyond the approximate 4GiB limit of the original ZIP format.

- WinZip-style AES-encrypted ZIPs. Python's zipfile module cannot open AES-encrypted ZIPs.

- Legacy-encrypted ZIP files. This is also known as ZipCrypto/Zip 2.0.

- ZIP files created by Java's ZipOutputStream that are larger than 4GiB. At the time of writing libarchive-based stream readers cannot read these without error.

- BZip2-compressed ZIPs.
<!-- --8<-- [end:features] -->

---

Visit the [stream-unzip documentation](https://stream-unzip.docs.trade.gov.uk/) for usage instructions.

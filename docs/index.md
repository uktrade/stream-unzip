# stream-unzip

[![PyPI version](https://badge.fury.io/py/stream-unzip.svg)](https://pypi.org/project/stream-unzip/) [![CircleCI](https://circleci.com/gh/uktrade/stream-unzip.svg?style=shield)](https://circleci.com/gh/uktrade/stream-unzip) [![Test Coverage](https://api.codeclimate.com/v1/badges/02144f986cd3eecf4a0b/test_coverage)](https://codeclimate.com/github/uktrade/stream-unzip/test_coverage)

Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or any of its uncompressed files. Deflate and Deflate64/Enhanced Deflate ZIPs are supported, as well as AES and legacy (ZipCrypto/Zip 2.0) encrypted/password-protected ZIPs.

To create ZIP files on the fly try [stream-zip](https://stream-zip.docs.data.trade.gov.uk/).

---

Visit [Getting started](getting-started.md) to get started.

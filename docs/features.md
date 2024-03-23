---
layout: sub-navigation
order: 2
title: Features
---


In addition to being memory efficient, stream-unzip supports:

- Deflate-compressed ZIPs. The is the historical standard for ZIP files.

- Deflate64-compressed ZIPs. These are created by certain versions of Windows Explorer in some circumstances. Python's zipfile module cannot open Deflate64-compressed ZIPs.

- Zip64 ZIP files. These are ZIP files that allow sizes far beyond the approximate 4GiB limit of the original ZIP format.

- WinZip-style AES-encrypted ZIPs. Python's zipfile module cannot open AES-encrypted ZIPs.

- Legacy-encrypted ZIP files. This is also known as ZipCrypto/Zip 2.0.

- ZIP files created by Java's ZipOutputStream that are larger than 4GiB. At the time of writing libarchive-based stream readers cannot read these without error.

- BZip2-compressed ZIPs.

- An async interface (that uses threads under the hood).

# stream-unzip [![CircleCI](https://circleci.com/gh/uktrade/stream-unzip.svg?style=shield)](https://circleci.com/gh/uktrade/stream-unzip) [![Test Coverage](https://api.codeclimate.com/v1/badges/02144f986cd3eecf4a0b/test_coverage)](https://codeclimate.com/github/uktrade/stream-unzip/test_coverage)

Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or any of its uncompressed files.

While the ZIP format does have its main directory at the end, each compressed file in the archive is prefixed with a header that contains its name. Also, the Deflate algorithm that most ZIP files use indicates when it has reached the end of the stream of a member file. These facts make the streaming decompression of ZIP archives possible.


## Installation

```bash
pip install stream-unzip
```


## Usage

A single function is exposed, `stream_unzip`, that takes a single argument: an iterable that should yield the bytes of a ZIP file. It returns an iterable, where each yielded item is a tuple of the file name, file size [`None` if this is not known], and another iterable itself yielding the unzipped bytes of that file.

```python
from stream_unzip import stream_unzip
import httpx

def zipped_chunks():
    # Any iterable that yields a zip file
    with httpx.stream('GET', 'https://www.example.com/my.zip') as r:
        yield from r.iter_bytes()

for file_name, file_size, unzipped_chunks in stream_unzip(zipped_chunks()):
    for chunk in unzipped_chunks:
        print(chunk)
```

The file name and file size are extracted as reported from the file. If you don't trust the creator of the ZIP file, these should be treated as untrusted input.

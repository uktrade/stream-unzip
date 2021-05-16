# stream-unzip

Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or any of its uncompressed files.


## Installation

```bash
pip install stream-unzip
```


## Usage

A single function is exposed, `stream_unzip`, that takes a single argument: an iterable that should yield the bytes of a ZIP file. It returns an iterable, where each yielded item is a tuple of the file name, file size, and another iterable itself yielding the unzipped bytes of that file.

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

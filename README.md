# stream-unzip

Python function to stream unzip all the files in a ZIP archive, without loading the entire ZIP file into memory or requiring multiple passes through the data.

> Work-in-progress. This README serves as a rough design spec.

## Usage

```python
from stream_unzip import stream_unzip
import httpx

def zipped_chunks():
	# Any iterable that yields a zip file
    with httpx.stream('GET', 'https://www.example.com/my.zip') as r:
        yield from r.iter_bytes()

for file_name, metadata, unzipped_chunks in stream_unzip(zipped_chunks()):
	for chunk in unzipped_chunks:
		print(chunk)
```

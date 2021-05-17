import io
import unittest
import uuid
import zipfile

from stream_unzip import stream_unzip


class TestIterableSubprocess(unittest.TestCase):

    def test_large_chunk_multiple_methods(self):
        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        contents = b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])

        def yield_input(method):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', contents)
                zf.writestr('second.txt', b'second')

            yield file.getvalue()

        for method in methods:
            files = [(name, size, b''.join(chunks)) for name, size, chunks in stream_unzip(yield_input(method))]
            self.assertEqual(files[0][0], b'first.txt')
            self.assertEqual(files[0][1], len(contents))
            self.assertEqual(files[0][2], contents)

            self.assertEqual(files[1][0], b'second.txt')
            self.assertEqual(files[1][1], 6)
            self.assertEqual(files[1][2], b'second')

            self.assertEqual(len(files), 2)

    def test_small_chunk(self):
        contents = b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])

        def yield_input():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', contents)

            zip_bytes = file.getvalue()
            chunk_size = 1

            for i in range(0, len(zip_bytes), chunk_size):
                yield zip_bytes[i:i + chunk_size]

        files = [(name, size, b''.join(chunks)) for name, size, chunks in stream_unzip(yield_input())]
        self.assertEqual(files[0][0], b'first.txt')
        self.assertEqual(files[0][1], len(contents))
        self.assertEqual(files[0][2], contents)

    def test_streaming(self):
        contents = b''.join([uuid.uuid4().hex.encode() for _ in range(0, 10000)])
        latest = None

        def yield_input():
            nonlocal latest

            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', contents)

            zip_bytes = file.getvalue()
            chunk_size = 1

            for i in range(0, len(zip_bytes), chunk_size):
                yield zip_bytes[i:i + chunk_size]
                latest = i

        latest_inputs = [[latest for _ in chunks] for _, _, chunks in stream_unzip(yield_input())][0]

        # Make sure the input is progressing during the output. In test, there
        # are about 100k steps, so checking that it's greater than 1000
        # shouldn't make this test too flakey
        num_steps = 0
        prev_i = 0
        for i in latest_inputs:
            if i != prev_i:
                num_steps += 1
            prev_i = i
        self.assertGreater(num_steps, 1000)

    def test_python_large(self):
        def yield_input():
            with open('fixtures/python38_zip64.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        num_received_bytes = 0
        for name, size, chunks in stream_unzip(yield_input()):
            for chunk in chunks:
                num_received_bytes += len(chunk)

        self.assertEqual(size, 5000000000)
        self.assertEqual(num_received_bytes, 5000000000)

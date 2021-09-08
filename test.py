import itertools
import io
import unittest
import uuid
import zipfile

from stream_unzip import stream_unzip


class TestStreamUnzip(unittest.TestCase):

    def test_methods_and_chunk_sizes(self):
        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])
        ]

        def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        for content, method, input_size, output_size in combinations_iter:
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                files = [
                    (name, size, b''.join(chunks))
                    for name, size, chunks in stream_unzip(yield_input(content, method, input_size), chunk_size=output_size)
                ]
                self.assertEqual(files[0][0], b'first.txt')
                self.assertEqual(files[0][1], len(content))
                self.assertEqual(files[0][2], content)
                self.assertEqual(files[1][0], b'second.txt')
                self.assertEqual(files[1][1], len(content))
                self.assertEqual(files[1][2], content)

    def test_output_size(self):
        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])
        ]

        def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        all_smaller = True
        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        for content, method, input_size, output_size in combinations_iter:
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                for _, _, chunks in stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                    for chunk in chunks:
                        all_smaller = all_smaller and len(chunk) <= output_size
        self.assertTrue(all_smaller)

    def test_exception_propagates(self):
        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])
        ]

        def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]
                raise Exception('Exception from generator')

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        for content, method, input_size, output_size in combinations_iter:
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                with self.assertRaisesRegex(Exception, 'Exception from generator'):
                    for _, _, chunks in stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                        for _ in chunks:
                            pass

    def test_bad_crc_32(self):
        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])
        ]

        def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()
            zip_bytes = zip_bytes[0:16] + bytes([zip_bytes[17] + 1 if zip_bytes[17] < 256 else zip_bytes[17] - 1]) + zip_bytes[17:]

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        for content, method, input_size, output_size in combinations_iter:
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                with self.assertRaisesRegex(Exception, 'CRC-32 does not match'):
                    for _, _, chunks in stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                        for _ in chunks:
                            pass

    def test_break_raises_generator_exit(self):
        input_size = 65536
        content = b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])

        raised_generator_exit = False

        def yield_input():
            nonlocal raised_generator_exit

            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            try:
                for i in range(0, len(zip_bytes), input_size):
                    yield zip_bytes[i:i + input_size]
            except GeneratorExit:
                raised_generator_exit = True

        for name, size, chunks in stream_unzip(yield_input()):
            for chunk in chunks:
                pass
    
        self.assertFalse(raised_generator_exit)

        for name, size, chunks in stream_unzip(yield_input()):
            for chunk in chunks:
                pass
            break

        self.assertTrue(raised_generator_exit)

    def test_truncation_raises_value_error(self):
        input_sizes = [1, 7, 32, 128, 256, 65536]
        content = b''.join([uuid.uuid4().hex.encode() for _ in range(0, 100000)])

        def yield_input(input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', content)

            zip_bytes = file.getvalue()

            yield zip_bytes[:input_size]

        for input_size in input_sizes:
            with self.subTest(input_size=input_size):
                with self.assertRaises(ValueError):
                    for name, size, chunks in stream_unzip(yield_input(input_size)):
                        for chunk in chunks:
                            pass

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

    def test_empty_file(self):
        def yield_input():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', b'')

            yield file.getvalue()

        files = [
            (name, size, b''.join(chunks))
            for name, size, chunks in stream_unzip(yield_input())
        ]

        self.assertEqual(files, [(b'first.txt', 0, b'')])

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

    def test_macos_single_file(self):
        def yield_input():
            with open('fixtures/macos_10_14_5_single_file.zip', 'rb') as f:
                yield f.read()

        num_received_bytes = 0
        files = [(name, size, b''.join(chunks)) for name, size, chunks in stream_unzip(yield_input())]

        self.assertEqual(len(files), 3)
        self.assertEqual(files[0], (b'contents.txt', None, b'Contents of the zip'))

    def test_macos_multiple_files(self):
        def yield_input():
            with open('fixtures/macos_10_14_5_multiple_files.zip', 'rb') as f:
                yield f.read()

        num_received_bytes = 0
        files = [(name, size, b''.join(chunks)) for name, size, chunks in stream_unzip(yield_input())]

        self.assertEqual(len(files), 5)
        self.assertEqual(files[0], (b'first.txt', None, b'Contents of the first file'))
        self.assertEqual(files[1][0], b'__MACOSX/')
        self.assertEqual(files[2][0], b'__MACOSX/._first.txt')
        self.assertEqual(files[3], (b'second.txt', None, b'Contents of the second file'))
        self.assertEqual(files[4][0], b'__MACOSX/._second.txt')

    def test_infozip_large_with_descriptors(self):
        def yield_input():
            with open('fixtures/infozip_3_0_zip64_with_descriptors.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        num_received_bytes = []
        sizes = []
        names = []
        for name, size, chunks in stream_unzip(yield_input()):
            names.append(name)
            sizes.append(size)
            num_received_bytes.append(0)
            for chunk in chunks:
                num_received_bytes[-1] += len(chunk)

        self.assertEqual(names, [b'first.txt', b'second.txt'])
        self.assertEqual(sizes, [None, None])
        self.assertEqual(num_received_bytes, [5000000000, 19])

    def test_password_protected_file_correct_password(self):
        def yield_input():
            with open('fixtures/macos_10_14_5_password.zip', 'rb') as f:
                while True:
                    chunk = f.read(4)
                    if not chunk:
                        break
                    yield chunk

        files = [
            (name, size, b''.join(chunks))
            for name, size, chunks in stream_unzip(yield_input(), password=b'password')
        ]
        self.assertEqual(files, [
            (b'compressed.txt', None, b'Some content to be password protected\n' * 14),
            (b'uncompressed.txt', 37, b'Some content to be password protected'),
        ])

    def test_password_protected_file_bad_password(self):
        def yield_input():
            with open('fixtures/macos_10_14_5_password.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(ValueError):
            for name, size, chunks in stream_unzip(yield_input(), password=b'bad-password'):
                next(chunks)

    def test_password_protected_file_data_descriptor_correct_password(self):
        def yield_input():
            with open('fixtures/macos_10_14_5_password_data_descriptor.zip', 'rb') as f:
                while True:
                    chunk = f.read(4)
                    if not chunk:
                        break
                    yield chunk

        files = [
            (name, size, b''.join(chunks))
            for name, size, chunks in stream_unzip(yield_input(), password=b'password')
        ]
        self.assertEqual(files, [
            (b'-', None, b'Some encrypted content to be compressed. Yes, compressed.'),
        ])

    def test_password_protected_aes(self):
        def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                while True:
                    chunk = f.read(10)
                    if not chunk:
                        break
                    yield chunk

        files = [
            (name, size, b''.join(chunks))
            for name, size, chunks in stream_unzip(yield_input(), password=b'password')
        ]
        self.assertEqual(files, [
            (b'content.txt', 384, b'Some content to be compressed and AES-encrypted\n' * 8),
        ])

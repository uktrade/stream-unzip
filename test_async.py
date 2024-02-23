import itertools
import io
import unittest
import uuid
import random
import zipfile
import asyncio


from stream_unzip import (
    UnfinishedIterationError,
    TruncatedDataError,
    UnsupportedFlagsError,
    UnsupportedCompressionTypeError,
    UnsupportedZip64Error,
    UnexpectedSignatureError,
    HMACIntegrityError,
    CRC32IntegrityError,
    MissingZipCryptoPasswordError,
    MissingAESPasswordError,
    IncorrectZipCryptoPasswordError,
    IncorrectAESPasswordError,
    DeflateError,
)
from async_stream_unzip import async_stream_unzip

class TestStreamUnzipAsync(unittest.IsolatedAsyncioTestCase):

    async def test_methods_and_chunk_sizes_async(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_BZIP2, zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        async def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        async def subtest(content, method, input_size, output_size):
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                files = []
                async for name, size, chunks in async_stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                    byte_text = []
                    async for chunk in chunks:
                        byte_text.append(chunk)
                    files.append((name, size, b''.join(byte_text)))
                # list operations hang for some reason
                self.assertEqual(files[0][0], b'first.txt')
                self.assertEqual(files[0][1], len(content))
                self.assertEqual(files[0][2], content)
                self.assertEqual(files[1][0], b'second.txt')
                self.assertEqual(files[1][1], len(content))
                self.assertEqual(files[1][2], content)

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        tasks = []
        for content, method, input_size, output_size in combinations_iter:
            tasks.append(asyncio.create_task(subtest(content, method, input_size, output_size)))
        await asyncio.gather(*tasks)
            

    async def test_skipping_wrapper(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        async def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        async def skippable(stream_unzip_output):
            async def chunk_gen_func(chunks):
                async for chunk in chunks:
                    yield chunk

            async for name, size, chunks in stream_unzip_output:
                chunks_gen = chunk_gen_func(chunks)
                yield name, size, chunks_gen
                async for a in chunks_gen:
                    pass

        async def subtest(content, method, input_size, output_size):
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                combined = b''

                async for name, size, chunks in skippable(async_stream_unzip(yield_input(content, method, input_size), chunk_size=output_size)):
                    if name == b'first.txt':
                        continue
                    byte_text = []
                    async for chunk in chunks:
                        byte_text.append(chunk)
                    combined = b''.join(byte_text)

                self.assertEqual(combined, content)
        
        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        tasks = []
        for content, method, input_size, output_size in combinations_iter:
            tasks.append(asyncio.create_task(subtest(content, method, input_size, output_size)))
        await asyncio.gather(*tasks)
            

    async def test_exception_on_skip(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        async def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        async def subtest(content, method, input_size, output_size):
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                    with self.assertRaises(UnfinishedIterationError):
                        async for name, size, chunks in async_stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                            if name == b'first.txt':
                                continue
        
        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        tasks = []
        for content, method, input_size, output_size in combinations_iter:
            tasks.append(asyncio.create_task(subtest(content, method, input_size, output_size)))
        await asyncio.gather(*tasks)

    async def test_output_size(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        async def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        all_smaller = True
        async def subtest(content, method, input_size, output_size):
            nonlocal all_smaller
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                async for _, _, chunks in async_stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                    async for chunk in chunks:
                        all_smaller = all_smaller and len(chunk) <= output_size


        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        tasks = []
        for content, method, input_size, output_size in combinations_iter:
            tasks.append(asyncio.create_task(subtest(content, method, input_size, output_size)))
        await asyncio.gather(*tasks)
        self.assertTrue(all_smaller)

    async def test_exception_propagates(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        async def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]
                raise Exception('Exception from generator')
        
        async def subtest(content, method, input_size, output_size):
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                with self.assertRaisesRegex(Exception, 'Exception from generator'):
                    async for _, _, chunks in async_stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                        async for _ in chunks:
                            pass

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        tasks = []
        for content, method, input_size, output_size in combinations_iter:
            tasks.append(asyncio.create_task(subtest(content, method, input_size, output_size)))
        await asyncio.gather(*tasks)

            
    async def test_bad_crc_32(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        async def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()
            zip_bytes = zip_bytes[0:16] + bytes([zip_bytes[17] + 1 % 256]) + zip_bytes[17:]

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        async def subtest(content, method, input_size, output_size):
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                with self.assertRaises(CRC32IntegrityError):
                    async for _, _, chunks in async_stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                        async for _ in chunks:
                            pass

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        tasks = []
        for content, method, input_size, output_size in combinations_iter:
            tasks.append(asyncio.create_task(subtest(content, method, input_size, output_size)))
        await asyncio.gather(*tasks)
            

    async def test_bad_deflate_data(self):
        rnd = random.Random()
        rnd.seed(1)

        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        content = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])

        async def yield_input(input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', content)

            zip_bytes = file.getvalue()
            zip_bytes = zip_bytes[0:500] + b'-' + zip_bytes[502:]

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        async def subtest(input_size, output_size):
            with self.subTest(input_size=input_size, output_size=output_size):
                with self.assertRaises(DeflateError):
                    async for _, _, chunks in async_stream_unzip(yield_input(input_size), chunk_size=output_size):
                        async for _ in chunks:
                            pass

        combinations_iter = itertools.product(input_sizes, output_sizes)
        tasks = []
        for input_size, output_size in combinations_iter:
            tasks.append(asyncio.create_task(subtest(input_size, output_size)))
        await asyncio.gather(*tasks)
            
    #since it is an async generator it wont send generator exit
    async def test_break_not_raises_generator_exit(self):
        rnd = random.Random()
        rnd.seed(1)

        input_size = 65536
        content = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])

        raised_generator_exit = False

        async def yield_input():
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

        async for name, size, chunks in async_stream_unzip(yield_input()):
            async for chunk in chunks:
                pass
    
        self.assertFalse(raised_generator_exit)

        async for name, size, chunks in async_stream_unzip(yield_input()):
            async for chunk in chunks:
                pass
            break

        self.assertFalse(raised_generator_exit)

    async def test_truncation_raises_value_error(self):
        rnd = random.Random()
        rnd.seed(1)

        input_sizes = [65536]
        content = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 100000)])

        async def yield_input(input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', content)

            zip_bytes = file.getvalue()

            yield zip_bytes[:input_size]

        async def subtest(input_size):
            with self.subTest(input_size=input_size):
                with self.assertRaises(TruncatedDataError):
                    async for name, size, chunks in async_stream_unzip(yield_input(input_size)):
                        async for chunk in chunks:
                            pass


        tasks = []
        for input_size in input_sizes:
            tasks.append(asyncio.create_task(subtest(input_size)))
        await asyncio.gather(*tasks)

            
    async def test_streaming(self):
        rnd = random.Random()
        rnd.seed(1)

        contents = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        latest = None

        async def yield_input():
            nonlocal latest

            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', contents)

            zip_bytes = file.getvalue()
            chunk_size = 1

            for i in range(0, len(zip_bytes), chunk_size):
                yield zip_bytes[i:i + chunk_size]
                latest = i

        latest_inputs = [[latest async for _ in chunks] async for _, _, chunks in async_stream_unzip(yield_input())][0]

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

    async def test_empty_file(self):
        async def yield_input():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', b'')

            yield file.getvalue()

        files = []
        async for name, size, chunks in async_stream_unzip(yield_input()):
            byte_text = []
            async for chunk in chunks:
                byte_text.append(chunk)
            files.append((name, size, b''.join(byte_text)))

        self.assertEqual(files, [(b'first.txt', 0, b'')])

    async def test_empty_zip(self):
        async def yield_input():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                pass

            yield file.getvalue()

        l = [z async for z in async_stream_unzip(yield_input())]

        self.assertEqual(l, [])

    async def test_not_zip(self):
        async def yield_input():
            yield b'This is not a zip file'

        with self.assertRaises(UnexpectedSignatureError):
            async for _ in async_stream_unzip(yield_input()):
                pass

    async def test_python_zip64(self):
        async def yield_input():
            with open('fixtures/python38_zip64.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        num_received_bytes = 0
        async for name, size, chunks in async_stream_unzip(yield_input()):
            async for chunk in chunks:
                num_received_bytes += len(chunk)

        self.assertEqual(size, 5000000000)
        self.assertEqual(num_received_bytes, 5000000000)

    async def test_python_zip64_disabled(self):
        async def yield_input():
            with open('fixtures/python38_zip64.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        with self.assertRaises(UnsupportedZip64Error):
            async for name, size, chunks in async_stream_unzip(yield_input(), allow_zip64=False):
                    async for chunk in chunks:
                        pass

    async def test_macos_single_file(self):
        async def yield_input():
            with open('fixtures/macos_10_14_5_single_file.zip', 'rb') as f:
                yield f.read()

        num_received_bytes = 0
        files = []
        async for name, size, chunks in async_stream_unzip(yield_input()):
            byte_str = []
            async for chunk in chunks:
                byte_str.append(chunk)
            files.append((name, size, b''.join(byte_str)))

        self.assertEqual(len(files), 3)
        self.assertEqual(files[0], (b'contents.txt', None, b'Contents of the zip'))

    async def test_macos_multiple_files(self):
        async def yield_input():
            with open('fixtures/macos_10_14_5_multiple_files.zip', 'rb') as f:
                yield f.read()

        num_received_bytes = 0
        files = []
        async for name, size, chunks in async_stream_unzip(yield_input()):
            byte_str = []
            async for chunk in chunks:
                byte_str.append(chunk)
            files.append((name, size, b''.join(byte_str)))

        self.assertEqual(len(files), 5)
        self.assertEqual(files[0], (b'first.txt', None, b'Contents of the first file'))
        self.assertEqual(files[1][0], b'__MACOSX/')
        self.assertEqual(files[2][0], b'__MACOSX/._first.txt')
        self.assertEqual(files[3], (b'second.txt', None, b'Contents of the second file'))
        self.assertEqual(files[4][0], b'__MACOSX/._second.txt')

    async def test_infozip_zip_limit_without_descriptors(self):
        async def yield_input():
            with open('fixtures/infozip_3_0_zip_limit_without_descriptors.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        num_received_bytes = []
        sizes = []
        names = []
        async for name, size, chunks in async_stream_unzip(yield_input()):
            names.append(name)
            sizes.append(size)
            num_received_bytes.append(0)
            async for chunk in chunks:
                num_received_bytes[-1] += len(chunk)

        self.assertEqual(names, [b'-'])
        self.assertEqual(sizes, [4294967295])
        self.assertEqual(num_received_bytes, [4294967295])

    async def test_infozip_zip_limit_with_descriptors(self):
        async def yield_input():
            with open('fixtures/infozip_3_0_zip_limit_with_descriptors.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        num_received_bytes = []
        sizes = []
        names = []
        async for name, size, chunks in async_stream_unzip(yield_input()):
            names.append(name)
            sizes.append(size)
            num_received_bytes.append(0)
            async for chunk in chunks:
                num_received_bytes[-1] += len(chunk)

        self.assertEqual(names, [b'-'])
        self.assertEqual(sizes, [None])
        self.assertEqual(num_received_bytes, [4294967295])

    async def test_infozip_zip_limit_stored(self):
        # This file is uncompressed, so it's double-zipped to just store a zipped
        # one in the repo
        async def yield_input():
            with open('fixtures/infozip_3_0_zip_limit_without_descriptors_stored.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        size = 0
        async for name, _, chunks_outer in async_stream_unzip(yield_input()):
            async for name, _, chunks in async_stream_unzip(chunks_outer):
                async for chunk in chunks:
                    size += len(chunk)

        self.assertEqual(size, 4294967295)

    async def test_infozip_zip64_with_descriptors(self):
        async def yield_input():
            with open('fixtures/infozip_3_0_zip64_with_descriptors.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        num_received_bytes = []
        sizes = []
        names = []
        async for name, size, chunks in async_stream_unzip(yield_input()):
            names.append(name)
            sizes.append(size)
            num_received_bytes.append(0)
            async for chunk in chunks:
                num_received_bytes[-1] += len(chunk)

        self.assertEqual(names, [b'first.txt', b'second.txt'])
        self.assertEqual(sizes, [None, None])
        self.assertEqual(num_received_bytes, [5000000000, 19])

    async def test_infozip_password_protected_file_correct_password(self):
        async def yield_input():
            with open('fixtures/infozip_3_0_password.zip', 'rb') as f:
                while True:
                    chunk = f.read(4)
                    if not chunk:
                        break
                    yield chunk

        files = []
        async for name, size, chunks in async_stream_unzip(yield_input(), password=b'password'):
            byte_str = []
            async for chunk in chunks:
                byte_str.append(chunk)
            files.append((name, size, b''.join(byte_str)))

        self.assertEqual(files, [
            (b'compressed.txt', None, b'Some content to be password protected\n' * 14),
            (b'uncompressed.txt', 37, b'Some content to be password protected'),
        ])

    async def test_infozip_password_protected_file_no_password(self):
        async def yield_input():
            with open('fixtures/infozip_3_0_password.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(MissingZipCryptoPasswordError):
            async for name, size, chunks in async_stream_unzip(yield_input()):
                anext(chunks)

    async def test_infozip_password_protected_file_bad_password(self):
        async def yield_input():
            with open('fixtures/infozip_3_0_password.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(IncorrectZipCryptoPasswordError):
            async for name, size, chunks in async_stream_unzip(yield_input(), password=b'bad-password'):
                anext(chunks)

    async def test_infozip_password_protected_file_data_descriptor_correct_password(self):
        async def yield_input():
            with open('fixtures/infozip_3_0_password_data_descriptor.zip', 'rb') as f:
                while True:
                    chunk = f.read(4)
                    if not chunk:
                        break
                    yield chunk

        files = []
        async for name, size, chunks in async_stream_unzip(yield_input(), password=b'password'):
            byte_str = []
            async for chunk in chunks:
                byte_str.append(chunk)
            files.append((name, size, b''.join(byte_str)))

        self.assertEqual(files, [
            (b'-', None, b'Some encrypted content to be compressed. Yes, compressed.'),
        ])

    async def test_7za_password_protected_aes(self):
        async def yield_input(i):
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                while True:
                    chunk = f.read(i)
                    if not chunk:
                        break
                    yield chunk

        # AES has block sizes of 16 bytes, so try to make sure there
        # isn't some subtle dependency on chunks being a multiple of that
        for i in tuple(range(1, 17)) + (100000,):
            files = []
            async for name, size, chunks in async_stream_unzip(yield_input(i), password=b'password'):
                byte_str = []
                async for chunk in chunks:
                    byte_str.append(chunk)
                files.append((name, size, b''.join(byte_str)))

            self.assertEqual(files, [
                (b'content.txt', 384, b'Some content to be compressed and AES-encrypted\n' * 8),
            ])

    async def test_7za_password_protected_aes_bad_hmac(self):
        async def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                data = f.read()
                yield data[0:130] + b'-' + data[132:]

        with self.assertRaises(HMACIntegrityError):
            async for name, size, chunks in async_stream_unzip(yield_input(), password=b'password'):
                async for chunk in chunks:
                    pass

    async def test_7za_password_protected_aes_data_descriptor(self):
        async def yield_input(i):
            with open('fixtures/7za_17_4_aes_data_descriptor.zip', 'rb') as f:
                while True:
                    chunk = f.read(i)
                    if not chunk:
                        break
                    yield chunk

        # AES has block sizes of 16 bytes, so try to make sure there
        # isn't some subtle dependency on chunks being a multiple of that
        for i in tuple(range(1, 17)) + (100000,):
            files = []
            async for name, size, chunks in async_stream_unzip(yield_input(i), password=b'password'):
                byte_str = []
                async for chunk in chunks:
                    byte_str.append(chunk)
                files.append((name, size, b''.join(byte_str)))

            self.assertEqual(files, [
                (b'', None, b'Some content to be compressed and AES-encrypted\n' * 1000),
            ])

    async def test_7za_password_protected_aes_no_password(self):
        async def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(MissingAESPasswordError):
            async for name, size, chunks in async_stream_unzip(yield_input()):
                anext(chunks)

    async def test_7za_password_protected_aes_bad_password(self):
        async def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(IncorrectAESPasswordError):
            async for name, size, chunks in async_stream_unzip(yield_input(), password=b'not-password'):
                anext(chunks)

    async def test_7za_deflate64(self):
        async def yield_input():
            with open('fixtures/7za_17_4_deflate64.zip', 'rb') as f:
                yield f.read()

        async for name, size, chunks in async_stream_unzip(yield_input()):
            byte_str = []
            async for chunk in chunks:
                byte_str.append(chunk)
            content = b''.join(byte_str)

        self.assertEqual(content, b'Some content to be compressed and AES-encrypted\n' * 1000)

    async def test_7z_password_data_descriptor(self):
        async def yield_input():
            with open('fixtures/7z_17_4_password_data_descriptor.zip', 'rb') as f:
                yield f.read()

        async for name, size, chunks in async_stream_unzip(yield_input(), password=b'password'):
            byte_str = []
            async for chunk in chunks:
                byte_str.append(chunk)
            content = b''.join(byte_str)


        self.assertEqual(content, b'Some content to be compressed and encrypted')

    async def test_java_zip_limit(self):
        async def yield_input():
            with open('fixtures/java_19_0_1_zip_limit.zip', 'rb') as f:
                yield f.read()

        l = 0
        async for name, size, chunks in async_stream_unzip(yield_input()):
            async for chunk in chunks:
                l += len(chunk)

        self.assertEqual(l, 4294967294)

    async def test_java_zip_limit_crc_32_error(self):
        async def yield_input():
            with open('fixtures/java_19_0_1_zip_limit.zip', 'rb') as f:
                b = f.read()
                yield b[:-87] + b'\0' + b[-86:]

        with self.assertRaises(CRC32IntegrityError):
            async for name, size, chunks in async_stream_unzip(yield_input()):
                async for chunk in chunks:
                    pass

    async def test_java_zip64_limit(self):
        async def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit.zip', 'rb') as f:
                yield f.read()

        l = 0
        async for name, size, chunks in async_stream_unzip(yield_input()):
            async for chunk in chunks:
                l += len(chunk)

        self.assertEqual(l, 4294967295)

    async def test_java_zip64_limit_crc_32_error(self):
        async def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit.zip', 'rb') as f:
                b = f.read()
                yield b[:-110] + b'\1' + b[-109:]

        with self.assertRaises(CRC32IntegrityError):
            async for name, size, chunks in async_stream_unzip(yield_input()):
                async for chunk in chunks:
                    pass

    async def test_java_zip64_limit_plus_one(self):
        async def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit_plus_one.zip', 'rb') as f:
                yield f.read()

        l = 0
        async for name, size, chunks in async_stream_unzip(yield_input()):
            async for chunk in chunks:
                l += len(chunk)

        self.assertEqual(l, 4294967296)

    async def test_java_zip64_limit_plus_one_crc_32_error(self):
        async def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit_plus_one.zip', 'rb') as f:
                b = f.read()
                yield b[:-110] + b'\1' + b[-109:]

        with self.assertRaises(CRC32IntegrityError):
            async for name, size, chunks in async_stream_unzip(yield_input()):
                async for chunk in chunks:
                    pass

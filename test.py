import asyncio
import itertools
import io
import platform
import unittest
import uuid
import random
import zipfile

from stream_unzip import (
    NO_ENCRYPTION,
    ZIP_CRYPTO,
    AE_1,
    AE_2,
    AES_128,
    AES_192,
    AES_256,
    async_stream_unzip,
    stream_unzip,
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
    FileIsNotEncrypted,
    ZipCryptoNotAllowed,
    AE1NotAllowed,
    AE2NotAllowed,
    AES128NotAllowed,
    AES192NotAllowed,
    AES256NotAllowed,
    DeflateError,
)


class TestStreamUnzip(unittest.TestCase):

    def test_methods_and_chunk_sizes(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_BZIP2, zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
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

    def test_skipping_wrapper(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        def skippable(stream_unzip_output):
            def chunk_gen_func(chunks):
                yield from chunks

            for name, size, chunks in stream_unzip_output:
                chunks_gen = chunk_gen_func(chunks)
                yield name, size, chunks_gen
                for a in chunks_gen:
                    pass

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        for content, method, input_size, output_size in combinations_iter:
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                combined = b''

                for name, size, chunks in skippable(stream_unzip(yield_input(content, method, input_size), chunk_size=output_size)):
                    if name == b'first.txt':
                        continue

                    combined = b''.join(chunks)

                self.assertEqual(combined, content)

    def test_exception_on_skip(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
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
                with self.assertRaises(UnfinishedIterationError):
                    for name, size, chunks in stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                        if name == b'first.txt':
                            continue

    def test_output_size(self):
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
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
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
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
        rnd = random.Random()
        rnd.seed(1)

        methods = [zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED]
        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        contents = [
            b'short',
            b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
        ]

        def yield_input(content, method, input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', method) as zf:
                zf.writestr('first.txt', content)
                zf.writestr('second.txt', content)

            zip_bytes = file.getvalue()
            zip_bytes = zip_bytes[0:16] + bytes([zip_bytes[17] + 1 % 256]) + zip_bytes[17:]

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        combinations_iter = itertools.product(contents, methods, input_sizes, output_sizes)
        for content, method, input_size, output_size in combinations_iter:
            with self.subTest(content=content[:5], method=method, input_size=input_size, output_size=output_size):
                with self.assertRaises(CRC32IntegrityError):
                    for _, _, chunks in stream_unzip(yield_input(content, method, input_size), chunk_size=output_size):
                        for _ in chunks:
                            pass

    def test_bad_deflate_data(self):
        rnd = random.Random()
        rnd.seed(1)

        input_sizes = [1, 7, 65536]
        output_sizes = [1, 7, 65536]

        content = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])

        def yield_input(input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', content)

            zip_bytes = file.getvalue()
            zip_bytes = zip_bytes[0:500] + b'-' + zip_bytes[502:]

            for i in range(0, len(zip_bytes), input_size):
                yield zip_bytes[i:i + input_size]

        combinations_iter = itertools.product(input_sizes, output_sizes)
        for input_size, output_size in combinations_iter:
            with self.subTest(input_size=input_size, output_size=output_size):
                with self.assertRaises(DeflateError):
                    for _, _, chunks in stream_unzip(yield_input(input_size), chunk_size=output_size):
                        for _ in chunks:
                            pass

    def test_break_raises_generator_exit(self):
        rnd = random.Random()
        rnd.seed(1)

        input_size = 65536
        content = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])

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
        rnd = random.Random()
        rnd.seed(1)

        input_sizes = [65536]
        content = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 100000)])

        def yield_input(input_size):
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', content)

            zip_bytes = file.getvalue()

            yield zip_bytes[:input_size]

        for input_size in input_sizes:
            with self.subTest(input_size=input_size):
                with self.assertRaises(TruncatedDataError):
                    for name, size, chunks in stream_unzip(yield_input(input_size)):
                        for chunk in chunks:
                            pass

    def test_streaming(self):
        rnd = random.Random()
        rnd.seed(1)

        contents = b''.join([uuid.UUID(int=rnd.getrandbits(128), version=4).hex.encode() for _ in range(0, 10000)])
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

    def test_password_supplied_but_not_encrypted(self):
        def yield_input():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', b'anything')

            yield file.getvalue()

        with self.assertRaises(FileIsNotEncrypted):
            next(iter(stream_unzip(yield_input(), password=b'anything', allowed_encryption_mechanisms=())))

    def test_empty_zip(self):
        def yield_input():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                pass

            yield file.getvalue()

        self.assertEqual(list(stream_unzip(yield_input())), [])

    def test_not_zip(self):
        with self.assertRaises(UnexpectedSignatureError):
            next(stream_unzip([b'This is not a zip file']))

    def test_python_zip64(self):
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

    def test_python_zip64_disabled(self):
        def yield_input():
            with open('fixtures/python38_zip64.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        with self.assertRaises(UnsupportedZip64Error):
            next(iter(stream_unzip(yield_input(), allow_zip64=False)))

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

    def test_infozip_zip_limit_without_descriptors(self):
        def yield_input():
            with open('fixtures/infozip_3_0_zip_limit_without_descriptors.zip', 'rb') as f:
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

        self.assertEqual(names, [b'-'])
        self.assertEqual(sizes, [4294967295])
        self.assertEqual(num_received_bytes, [4294967295])

    def test_infozip_zip_limit_with_descriptors(self):
        def yield_input():
            with open('fixtures/infozip_3_0_zip_limit_with_descriptors.zip', 'rb') as f:
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

        self.assertEqual(names, [b'-'])
        self.assertEqual(sizes, [None])
        self.assertEqual(num_received_bytes, [4294967295])

    def test_infozip_zip_limit_stored(self):
        # This file is uncompressed, so it's double-zipped to just store a zipped
        # one in the repo
        def yield_input():
            with open('fixtures/infozip_3_0_zip_limit_without_descriptors_stored.zip', 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk

        size = 0
        for name, _, chunks_outer in stream_unzip(yield_input()):
            for name, _, chunks in stream_unzip(chunks_outer):
                for chunk in chunks:
                    size += len(chunk)

        self.assertEqual(size, 4294967295)

    def test_infozip_zip64_with_descriptors(self):
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

    def test_infozip_password_protected_file_correct_password(self):
        def yield_input():
            with open('fixtures/infozip_3_0_password.zip', 'rb') as f:
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

    def test_infozip_password_protected_file_no_password(self):
        def yield_input():
            with open('fixtures/infozip_3_0_password.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(MissingZipCryptoPasswordError):
            for name, size, chunks in stream_unzip(yield_input()):
                next(chunks)

    def test_infozip_password_protected_zip_crypto_not_allowed(self):
        def yield_input():
            with open('fixtures/infozip_3_0_password.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(ZipCryptoNotAllowed):
            for name, size, chunks in stream_unzip(yield_input(), password=b'any-password', allowed_encryption_mechanisms=()):
                next(chunks)

    def test_infozip_password_protected_file_bad_password(self):
        def yield_input():
            with open('fixtures/infozip_3_0_password.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(IncorrectZipCryptoPasswordError):
            for name, size, chunks in stream_unzip(yield_input(), password=b'bad-password'):
                next(chunks)

    def test_infozip_password_protected_file_data_descriptor_correct_password(self):
        def yield_input():
            with open('fixtures/infozip_3_0_password_data_descriptor.zip', 'rb') as f:
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

    def test_7za_password_protected_aes(self):
        def yield_input(i):
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                while True:
                    chunk = f.read(i)
                    if not chunk:
                        break
                    yield chunk

        # AES has block sizes of 16 bytes, so try to make sure there
        # isn't some subtle dependency on chunks being a multiple of that
        for i in tuple(range(1, 17)) + (100000,):
            files = [
                (name, size, b''.join(chunks))
                for name, size, chunks in stream_unzip(yield_input(i), password=b'password')
            ]
            self.assertEqual(files, [
                (b'content.txt', 384, b'Some content to be compressed and AES-encrypted\n' * 8),
            ])

    def test_7za_password_protected_ae_2_not_allowed(self):
        def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                yield from iter(lambda: f.read(4), b'')

        with self.assertRaises(AE2NotAllowed):
            next(iter(stream_unzip(yield_input(), password=b'password', allowed_encryption_mechanisms=(
                AES_256,
            ))))

    def test_7za_password_protected_aes_256_not_allowed(self):
        def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                yield from iter(lambda: f.read(4), b'')

        with self.assertRaises(AES256NotAllowed):
            next(iter(stream_unzip(yield_input(), password=b'password', allowed_encryption_mechanisms=(
                AE_2,
            ))))

    def test_7za_password_protected_aes_bad_hmac(self):
        def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                data = f.read()
                yield data[0:130] + b'-' + data[132:]

        with self.assertRaises(HMACIntegrityError):
            for name, size, chunks in stream_unzip(yield_input(), password=b'password'):
                for chunk in chunks:
                    pass

    def test_7za_password_protected_aes_data_descriptor(self):
        def yield_input(i):
            with open('fixtures/7za_17_4_aes_data_descriptor.zip', 'rb') as f:
                while True:
                    chunk = f.read(i)
                    if not chunk:
                        break
                    yield chunk

        # AES has block sizes of 16 bytes, so try to make sure there
        # isn't some subtle dependency on chunks being a multiple of that
        for i in tuple(range(1, 17)) + (100000,):
            files = [
                (name, size, b''.join(chunks))
                for name, size, chunks in stream_unzip(yield_input(i), password=b'password')
            ]
            self.assertEqual(files, [
                (b'', None, b'Some content to be compressed and AES-encrypted\n' * 1000),
            ])

    def test_7za_password_protected_aes_no_password(self):
        def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(MissingAESPasswordError):
            for name, size, chunks in stream_unzip(yield_input()):
                next(chunks)

    def test_7za_password_protected_aes_bad_password(self):
        def yield_input():
            with open('fixtures/7za_17_4_aes.zip', 'rb') as f:
                yield f.read()

        with self.assertRaises(IncorrectAESPasswordError):
            for name, size, chunks in stream_unzip(yield_input(), password=b'not-password'):
                next(chunks)

    def test_7za_deflate64(self):
        def yield_input():
            with open('fixtures/7za_17_4_deflate64.zip', 'rb') as f:
                yield f.read()

        for name, size, chunks in stream_unzip(yield_input()):
            content = b''.join(chunks)

        self.assertEqual(content, b'Some content to be compressed and AES-encrypted\n' * 1000)

    def test_7z_password_data_descriptor(self):
        def yield_input():
            with open('fixtures/7z_17_4_password_data_descriptor.zip', 'rb') as f:
                yield f.read()

        for name, size, chunks in stream_unzip(yield_input(), password=b'password'):
            content = b''.join(chunks)

        self.assertEqual(content, b'Some content to be compressed and encrypted')

    def test_java_zip_limit(self):
        def yield_input():
            with open('fixtures/java_19_0_1_zip_limit.zip', 'rb') as f:
                yield f.read()

        l = 0
        for name, size, chunks in stream_unzip(yield_input()):
            for chunk in chunks:
                l += len(chunk)

        self.assertEqual(l, 4294967294)

    def test_java_zip_limit_crc_32_error(self):
        def yield_input():
            with open('fixtures/java_19_0_1_zip_limit.zip', 'rb') as f:
                b = f.read()
                yield b[:-87] + b'\0' + b[-86:]

        with self.assertRaises(CRC32IntegrityError):
            for name, size, chunks in stream_unzip(yield_input()):
                for chunk in chunks:
                    pass

    def test_java_zip64_limit(self):
        def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit.zip', 'rb') as f:
                yield f.read()

        l = 0
        for name, size, chunks in stream_unzip(yield_input()):
            for chunk in chunks:
                l += len(chunk)

        self.assertEqual(l, 4294967295)

    def test_java_zip64_limit_crc_32_error(self):
        def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit.zip', 'rb') as f:
                b = f.read()
                yield b[:-110] + b'\1' + b[-109:]

        with self.assertRaises(CRC32IntegrityError):
            for name, size, chunks in stream_unzip(yield_input()):
                for chunk in chunks:
                    pass

    def test_java_zip64_limit_plus_one(self):
        def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit_plus_one.zip', 'rb') as f:
                yield f.read()

        l = 0
        for name, size, chunks in stream_unzip(yield_input()):
            for chunk in chunks:
                l += len(chunk)

        self.assertEqual(l, 4294967296)

    def test_java_zip64_limit_plus_one_crc_32_error(self):
        def yield_input():
            with open('fixtures/java_19_0_1_zip64_limit_plus_one.zip', 'rb') as f:
                b = f.read()
                yield b[:-110] + b'\1' + b[-109:]

        with self.assertRaises(CRC32IntegrityError):
            for name, size, chunks in stream_unzip(yield_input()):
                for chunk in chunks:
                    pass

    def test_async_stream_unzip(self):
        async def async_bytes():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', b'-' * 100000)
                zf.writestr('second.txt', b'*' * 100000)
            zip_bytes = file.getvalue()

            yield zip_bytes

        results = []

        async def test():
            async for name, size, chunks in async_stream_unzip(async_bytes()):
                b = b''
                async for chunk in chunks:
                    b += chunk
                results.append((name, size, b))

        asyncio.get_event_loop().run_until_complete(test())
        self.assertEqual(results, [
            (b'first.txt', 100000, b'-' * 100000),
            (b'second.txt', 100000, b'*' * 100000),
        ])

    def test_async_exception_from_bytes_propagates(self):
        async def async_bytes():
            yield b'P'
            raise Exception('From async bytes')

        async def test():
            await async_stream_unzip(async_bytes()).__aiter__().__anext__()

        with self.assertRaisesRegex(Exception, 'From async bytes'):
            asyncio.get_event_loop().run_until_complete(test())

    def test_async_does_stream(self):
        state = []

        async def async_bytes():
            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', b'-' * 100000)
                zf.writestr('second.txt', b'*' * 100000)
            zip_bytes = file.getvalue()

            chunk_size = 100
            for i in range(0, len(zip_bytes), chunk_size):
                state.append('in')
                yield zip_bytes[i:i + chunk_size]
                await asyncio.sleep(0)

        async def test():
            async for name, size, chunks in async_stream_unzip(async_bytes()):
                async for chunk in chunks:
                    state.append('out')

        asyncio.get_event_loop().run_until_complete(test())
        self.assertEqual(state, ['in', 'out', 'in', 'out', 'in', 'out', 'out', 'in', 'out', 'in'])

    @unittest.skipIf(
        tuple(int(v) for v in platform.python_version().split('.')) < (3,7,0),
        "contextvars are not supported before Python 3.7.0",
    )
    def test_copy_of_context_variable_available_in_iterable(self):
        # Ideally the context would be identical in the iterables, because that's what a purely asyncio
        # implementation of stream-zip would likely do

        import contextvars

        var = contextvars.ContextVar('test')
        var.set('set-from-outer')

        d = contextvars.ContextVar('d')
        d.set({'key': 'original-value'})

        inner = None

        async def async_bytes():
            nonlocal inner
            inner = var.get()

            var.set('set-from-inner')
            d.get()['key'] = 'set-from-inner'

            file = io.BytesIO()
            with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('first.txt', b'-' * 100000)
                zf.writestr('second.txt', b'*' * 100000)
            zip_bytes = file.getvalue()

            yield zip_bytes

        async def test():
            async for name, size, chunks in async_stream_unzip(async_bytes()):
                async for chunk in chunks:
                    pass

        asyncio.get_event_loop().run_until_complete(test())
        self.assertEqual(var.get(), 'set-from-outer')
        self.assertEqual(inner, 'set-from-outer')
        self.assertEqual(d.get()['key'], 'set-from-inner')

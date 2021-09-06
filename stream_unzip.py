from struct import Struct
import zlib

def stream_unzip(zipfile_chunks, password=None, chunk_size=65536):
    local_file_header_signature = b'\x50\x4b\x03\x04'
    local_file_header_struct = Struct('<H2sHHHIIIHH')
    zip64_compressed_size = 4294967295
    zip64_size_signature = b'\x01\x00'
    central_directory_signature = b'\x50\x4b\x01\x02'

    def get_byte_readers(iterable):
        # Return functions to return/"replace" bytes from/to the iterable
        # - _yield_all: yields chunks as they come up (often for a "body")
        # - _yield_num: yields chunks as the come up, up to a fixed number of bytes
        # - _get_num: returns a single `bytes` of a given length
        # - _return_unused: puts "unused" bytes "back", to be retrieved by a yield/get call

        prev_chunk = b''
        chunk = b''
        offset = 0
        it = iter(iterable)

        def _yield_all():
            nonlocal prev_chunk, chunk, offset

            while True:
                if not chunk:
                    try:
                        chunk = next(it)
                    except StopIteration:
                        break
                prev_offset = offset
                prev_chunk = chunk
                to_yield = min(len(chunk) - offset, chunk_size)
                offset = (offset + to_yield) % len(chunk)
                chunk = chunk if offset else b''
                yield prev_chunk[prev_offset:prev_offset + to_yield]

        def _yield_num(num):
            nonlocal prev_chunk, chunk, offset

            while num:
                if not chunk:
                    try:
                        chunk = next(it)
                    except StopIteration:
                        raise ValueError('Fewer bytes than expected in zip') from None
                prev_offset = offset
                prev_chunk = chunk
                to_yield = min(num, len(chunk) - offset, chunk_size)
                offset = (offset + to_yield) % len(chunk)
                chunk = chunk if offset else b''
                num -= to_yield
                yield prev_chunk[prev_offset:prev_offset + to_yield]

        def _get_num(num):
            return b''.join(chunk for chunk in _yield_num(num))

        def _return_unused(num_unused):
            nonlocal chunk, offset

            if num_unused <= offset:
                offset -= num_unused
            else:
                chunk = prev_chunk[-num_unused:] + chunk[offset:]
                offset = 0

        return _yield_all, _yield_num, _get_num, _return_unused

    def yield_file(yield_all, yield_num, get_num, return_unused):

        def get_flag_bits(flags):
            for b in flags:
                for i in range(8):
                    yield (b >> i) & 1

        def get_extra_data(extra, desired_signature):
            extra_offset = 0
            while extra_offset != len(extra):
                extra_signature = extra[extra_offset:extra_offset+2]
                extra_offset += 2
                extra_data_size, = Struct('<H').unpack(extra[extra_offset:extra_offset+2])
                extra_offset += 2
                extra_data = extra[extra_offset:extra_offset+extra_data_size]
                extra_offset += extra_data_size
                if extra_signature == desired_signature:
                    return extra_data

        def decrypt(chunks):
            key_0 = 305419896
            key_1 = 591751049
            key_2 = 878082192

            def crc32(ch, crc):
                return ~zlib.crc32(bytes([ch]), ~crc) & 0xFFFFFFFF

            def update_keys(byte):
                nonlocal key_0, key_1, key_2
                key_0 = crc32(byte, key_0)
                key_1 = (key_1 + (key_0 & 0xFF)) & 0xFFFFFFFF
                key_1 = ((key_1 * 134775813) + 1) & 0xFFFFFFFF
                key_2 = crc32(key_1 >> 24, key_2)

            def decrypt(chunk):
                chunk = bytearray(chunk)
                for i, byte in enumerate(chunk):
                    temp = key_2 | 2
                    byte ^= ((temp * (temp ^ 1)) >> 8) & 0xFF
                    update_keys(byte)
                    chunk[i] = byte
                return chunk

            yield_all, _, get_num, _ = get_byte_readers(chunks)

            for byte in password:
                update_keys(byte)

            if decrypt(get_num(12))[11] != mod_time >> 8:
                raise ValueError('Incorrect password')

            for chunk in yield_all():
                yield decrypt(chunk)

        def decompress(chunks):
            dobj = zlib.decompressobj(wbits=-zlib.MAX_WBITS)

            while not dobj.eof:
                try:
                    compressed_chunk = next(chunks)
                except StopIteration:
                    raise ValueError('Fewer bytes than expected in zip') from None

                uncompressed_chunk = dobj.decompress(compressed_chunk, chunk_size)
                if uncompressed_chunk:
                    yield uncompressed_chunk

                while dobj.unconsumed_tail and not dobj.eof:
                    uncompressed_chunk = dobj.decompress(dobj.unconsumed_tail, chunk_size)
                    if uncompressed_chunk:
                        yield uncompressed_chunk

            return_unused(len(dobj.unused_data))

        def with_crc_32_check(is_zip64, chunks):

            def _get_crc_32_expected_from_data_descriptor():
                dd_optional_signature = get_num(4)
                dd_so_far_num = \
                    0 if dd_optional_signature == b'PK\x07\x08' else \
                    4
                dd_so_far = dd_optional_signature[:dd_so_far_num]
                dd_remaining = \
                    (20 - dd_so_far_num) if is_zip64 else \
                    (12 - dd_so_far_num)
                dd = dd_so_far + get_num(dd_remaining)
                crc_32_expected, = Struct('<I').unpack(dd[:4])
                return crc_32_expected

            def _get_crc_32_expected_from_file_header():
                return crc_32_expected

            crc_32_actual = zlib.crc32(b'')
            for chunk in chunks:
                crc_32_actual = zlib.crc32(chunk, crc_32_actual)
                yield chunk

            get_crc_32_expected = \
                _get_crc_32_expected_from_data_descriptor if has_data_descriptor else \
                _get_crc_32_expected_from_file_header

            if crc_32_actual != get_crc_32_expected():
                raise ValueError('CRC-32 does not match')

        version, flags, compression, mod_time, mod_date, crc_32_expected, compressed_size, uncompressed_size, file_name_len, extra_field_len = \
            local_file_header_struct.unpack(get_num(local_file_header_struct.size))

        if compression not in [0, 8]:
            raise ValueError('Unsupported compression type {}'.format(compression))

        flag_bits = tuple(get_flag_bits(flags))
        if (
            flag_bits[4]      # Enhanced deflate (Deflate64)
            or flag_bits[5]   # Compressed patched
            or flag_bits[6]   # Strong encrypted
            or flag_bits[13]  # Masked header values
        ):
            raise ValueError('Unsupported flags {}'.format(flag_bits))

        is_weak_encrypted = flag_bits[0]
        has_data_descriptor = flag_bits[3]

        file_name = get_num(file_name_len)
        extra = get_num(extra_field_len)

        is_zip64 = compressed_size == zip64_compressed_size and uncompressed_size == zip64_compressed_size
        uncompressed_size, compressed_size = \
            Struct('<QQ').unpack(get_extra_data(extra, zip64_size_signature)) if is_zip64 else \
            (uncompressed_size, compressed_size)
        uncompressed_size = \
            None if has_data_descriptor else \
            uncompressed_size

        encrypted_bytes = \
            yield_num(compressed_size) if compression == 0 else \
            yield_all()
        decrypted_bytes = \
            decrypt(encrypted_bytes) if is_weak_encrypted else \
            encrypted_bytes
        decompressed_bytes = \
            decompress(decrypted_bytes) if compression == 8 else \
            decrypted_bytes

        return file_name, uncompressed_size, with_crc_32_check(is_zip64, decompressed_bytes)

    yield_all, yield_num, get_num, return_unused = get_byte_readers(zipfile_chunks)

    while True:
        signature = get_num(len(local_file_header_signature))
        if signature == local_file_header_signature:
            yield yield_file(yield_all, yield_num, get_num, return_unused)
        elif signature == central_directory_signature:
            for _ in yield_all():
                pass
            break
        else:
            raise ValueError(b'Unexpected signature ' + signature)

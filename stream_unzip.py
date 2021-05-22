from struct import Struct
import zlib

def stream_unzip(zipfile_chunks, chunk_size=65536):
    local_file_header_signature = b'\x50\x4b\x03\x04'
    local_file_header_struct = Struct('<H2sHHHIIIHH')
    zip64_compressed_size = 4294967295
    zip64_size_signature = b'\x01\x00'

    def get_byte_readers(iterable):
        # Return functions to return a specific number of bytes from the iterable
        # - read_multiple_chunks: yields chunks as they come up (often for a "body")
        # - read_single_chunk: returns a single chunks (often for "header")
        # - _read_remaining: yields any remaining chunks

        chunk = b''
        offset = 0
        it = iter(iterable)

        def _read_remaining():
            nonlocal chunk
            nonlocal offset

            # We only go past the yield on the next iteration, which might
            # not happen, so we have to leave the state right for next time
            prev_offset = offset
            prev_chunk = chunk
            offset = 0
            chunk = b''
            if prev_chunk:
                yield prev_chunk[prev_offset:]
            prev_chunk = b''

            while True:
                try:
                    yield next(it)
                except StopIteration:
                    break

        def _read_multiple_chunks(amt):
            nonlocal chunk
            nonlocal offset

            remaining_iter = read_remaining()

            while amt:
                try:
                    chunk = next(remaining_iter)
                except StopIteration:
                    raise ValueError('Fewer bytes than expected in zip') from None

                to_yield = min(amt, len(chunk) - offset)
                yield chunk[offset:offset + to_yield]
                amt -= to_yield
                offset += to_yield % len(chunk)
                chunk = chunk if offset else b''

        def _read_single_chunk(amt):
            return b''.join(chunk for chunk in _read_multiple_chunks(amt))

        def _return_unused(unused):
            nonlocal chunk
            chunk += unused

        return _read_multiple_chunks, _read_single_chunk, _read_remaining, _return_unused

    read_multiple_chunks, read_single_chunk, read_remaining, return_unused = get_byte_readers(zipfile_chunks)

    def parse_extra(extra):
        extra_offset = 0
        extra_dict = {}
        while extra_offset != len(extra):
            extra_signature = extra[extra_offset:extra_offset+2]
            extra_offset += 2
            extra_data_size, = Struct('<H').unpack(extra[extra_offset:extra_offset+2])
            extra_offset += 2
            extra_data = extra[extra_offset:extra_offset+extra_data_size]
            extra_offset += extra_data_size
            extra_dict[extra_signature] = extra_data
        return extra_dict

    def yield_file():
        version, flags, compression, mod_time, mod_date, crc_32, compressed_size, uncompressed_size, file_name_len, extra_field_len = \
            local_file_header_struct.unpack(read_single_chunk(local_file_header_struct.size))

        if compression not in [0, 8]:
            raise ValueError(f'Unsupported compression type {compression}')

        if flags not in [b'\x00\x00', b'\x08\x00']:
            raise ValueError(f'Unsupported flags {flags}')

        file_name = read_single_chunk(file_name_len)
        extra = parse_extra(read_single_chunk(extra_field_len))

        is_zip64 = compressed_size == zip64_compressed_size and uncompressed_size == zip64_compressed_size
        if is_zip64:
            uncompressed_size, compressed_size = Struct('<QQ').unpack(extra[zip64_size_signature])

        if flags == b'\x08\x00':
            uncompressed_size = None

        def _decompress_deflate():
            dobj = zlib.decompressobj(wbits=-zlib.MAX_WBITS)

            remaining_iter = read_remaining()

            while not dobj.eof:
                try:
                    compressed_chunk = next(remaining_iter)
                except StopIteration:
                    raise ValueError('Fewer bytes than expected in zip') from None

                uncompressed_chunk = dobj.decompress(compressed_chunk, max_length=chunk_size)
                if uncompressed_chunk:
                    yield uncompressed_chunk

                while dobj.unconsumed_tail and not dobj.eof:
                    uncompressed_chunk = dobj.decompress(dobj.unconsumed_tail, max_length=chunk_size)
                    if uncompressed_chunk:
                        yield uncompressed_chunk

            return_unused(dobj.unused_data)

            # Read the data descriptor
            if flags == b'\x08\x00':
                dd_optional_signature = read_single_chunk(4)
                dd_so_far = \
                    0 if dd_optional_signature == b'PK\x07\x08' else \
                    4
                dd_remaining = \
                    (20 - dd_so_far) if is_zip64 else \
                    (12 - dd_so_far)
                read_single_chunk(dd_remaining)

        uncompressed_bytes = \
            read_multiple_chunks(compressed_size) if compression == 0 else \
            _decompress_deflate()

        return file_name, uncompressed_size, uncompressed_bytes

    while True:
        signature = read_single_chunk(len(local_file_header_signature))
        if signature == local_file_header_signature:
            yield yield_file()
        else:
            # We must have reached the central directory record
            for _ in read_remaining():
                pass
            break

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use crc32_v2::crc32;

// ZipCrypto key initialization vector and constants
const ZIPCRYPTO_KEY_0: u32 = 0x12345678;
const ZIPCRYPTO_KEY_1: u32 = 0x23456789;
const ZIPCRYPTO_KEY_2: u32 = 0x34567890;

#[derive(Clone)]
struct ZipCrypto {
    key_0: u32,
    key_1: u32,
    key_2: u32,
}

impl ZipCrypto {
    fn new() -> Self {
        ZipCrypto {
            key_0: ZIPCRYPTO_KEY_0,
            key_1: ZIPCRYPTO_KEY_1,
            key_2: ZIPCRYPTO_KEY_2,
        }
    }

    #[inline(always)]
    fn init_password(&mut self, password: &[u8]) {
        for &b in password {
            self.update_keys(b);
        }
    }

    #[inline(always)]
    fn update_keys(&mut self, byte: u8) {
        self.key_0 = !crc32(!self.key_0, &[byte]);

        self.key_1 = self
            .key_1
            .wrapping_add(self.key_0 & 0xFF)
            .wrapping_mul(134775813)
            .wrapping_add(1);

        let temp_byte = (self.key_1 >> 24) as u8;
        self.key_2 = !crc32(!self.key_2, &[temp_byte]);
    }

    #[inline(always)]
    fn decrypt_byte(&mut self, byte: u8) -> u8 {
        let temp = (self.key_2 | 2) as u16;
        let key = (((temp.wrapping_mul(temp ^ 1)) >> 8) & 0xFF) as u8;
        let decrypted = byte ^ key;
        self.update_keys(decrypted);
        decrypted
    }

    #[inline(always)]
    fn decrypt_chunk(&mut self, chunk: &[u8]) -> Vec<u8> {
        chunk.iter().map(|&b| self.decrypt_byte(b)).collect()
    }
}

#[pyclass(name = "zipcrypto_decryptor")]
struct StreamUnzipZipCryptoDecryptor {
    zipcrypto: ZipCrypto,
}

#[pymethods]
impl StreamUnzipZipCryptoDecryptor {
    #[new]
    fn new(password: &[u8]) -> Self {
        let mut zipcrypto = ZipCrypto::new();
        zipcrypto.init_password(password);
        StreamUnzipZipCryptoDecryptor { zipcrypto }
    }

    // Decrypts a single chunk and returns the decrypted result
    fn __call__<'py>(&mut self, py: Python<'py>, chunk: Vec<u8>) -> PyResult<&'py PyBytes> {
        let result = self.zipcrypto.decrypt_chunk(&chunk);
        // Return the decrypted result as a Python bytes object so it can be used in Python code
        Ok(PyBytes::new(py, &result))
    }
}

#[pymodule]
fn stream_unzip_zipcrypto_decrypt(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<StreamUnzipZipCryptoDecryptor>()?;
    Ok(())
}

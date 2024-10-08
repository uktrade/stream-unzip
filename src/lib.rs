use pyo3::prelude::*;
use crc32fast::Hasher;

// ZipCrypto key initialization vector and constants
const ZIPCRYPTO_KEY0: u32 = 0x12345678;
const ZIPCRYPTO_KEY1: u32 = 0x23456789;
const ZIPCRYPTO_KEY2: u32 = 0x34567890;

#[derive(Clone)]
struct ZipCrypto {
    keys: [u32; 3],
}

impl ZipCrypto {
    fn new() -> Self {
        ZipCrypto {
            keys: [ZIPCRYPTO_KEY0, ZIPCRYPTO_KEY1, ZIPCRYPTO_KEY2],
        }
    }

    fn update_keys(&mut self, byte: u8) {
        // Update key[0]
        self.keys[0] = !crc32_update(!self.keys[0], &[byte]);

        // Update key[1]
        self.keys[1] = self
            .keys[1]
            .wrapping_add(self.keys[0] & 0xFF)
            .wrapping_mul(134775813)
            .wrapping_add(1);

        // Update key[2]
        let temp_byte = (self.keys[1] >> 24) as u8;
        self.keys[2] = !crc32_update(!self.keys[2], &[temp_byte]);
    }

    #[inline(always)]
    fn decrypt_byte(&mut self, byte: u8) -> u8 {
        let temp = (self.keys[2] | 2) as u16;
        let key = (((temp.wrapping_mul(temp ^ 1)) >> 8) & 0xFF) as u8;
        let decrypted = byte ^ key;
        self.update_keys(decrypted);
        decrypted
    }

    fn init_password(&mut self, password: &[u8]) {
        for &b in password {
            self.update_keys(b);
        }
    }

    fn decrypt_chunk(&mut self, chunk: &[u8]) -> Vec<u8> {
        chunk.iter().map(|&b| self.decrypt_byte(b)).collect()
    }
}

fn crc32_update(crc: u32, data: &[u8]) -> u32 {
    let mut hasher = Hasher::new_with_initial(crc);
    hasher.update(data);
    hasher.finalize()
}

#[pyclass]
struct StreamZipCryptoDecryptor {
    zipcrypto: ZipCrypto,
}

#[pymethods]
impl StreamZipCryptoDecryptor {
    #[new]
    fn new(password: &[u8]) -> Self {
        let mut zipcrypto = ZipCrypto::new();
        zipcrypto.init_password(password);
        StreamZipCryptoDecryptor { zipcrypto }
    }

    // This function decrypts a single chunk and returns the decrypted result.
    fn decrypt_chunk(&mut self, chunk: Vec<u8>) -> PyResult<Vec<u8>> {
        Ok(self.zipcrypto.decrypt_chunk(&chunk))
    }
}

#[pymodule]
fn zipcrypto_decrypt(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<StreamZipCryptoDecryptor>()?;
    Ok(())
}

import os
import base64
import hashlib
import hmac
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding, hashes
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger.warning("cryptography not available - encryption disabled")

class EncryptionManager:
    """AES-256-CBC шифрування з HKDF деривацією ключів згідно ТЗ"""
    
    def __init__(self, master_key: str = None):
        self.master_key = master_key or os.getenv('ENCRYPTION_MASTER_KEY') or os.getenv('ENCRYPTION_SECRET', 'shadow_system_master_key_2025')
        self._backend = default_backend() if CRYPTO_AVAILABLE else None
        
        if CRYPTO_AVAILABLE:
            self.session_key = self._derive_key("session_encryption")
            self.proxy_key = self._derive_key("proxy_credentials")
            self.data_key = self._derive_key("data_encryption")
            logger.info("EncryptionManager initialized (AES-256-CBC + HKDF)")
        else:
            self.session_key = hashlib.sha256(self.master_key.encode()).digest()
            self.proxy_key = self.session_key
            self.data_key = self.session_key
            logger.warning("EncryptionManager initialized (fallback mode)")
    
    def _derive_key(self, context: str) -> bytes:
        """HKDF деривація ключа з майстер-ключа"""
        if not CRYPTO_AVAILABLE:
            return hashlib.sha256(f"{self.master_key}{context}".encode()).digest()
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"shadow_system_salt_v2",
            info=context.encode(),
            backend=self._backend
        )
        return hkdf.derive(self.master_key.encode())
    
    def encrypt_session_string(self, session_data: str) -> str:
        """Шифрування строки сесії Telegram (AES-256-CBC)"""
        if not session_data:
            return ""
        
        if not CRYPTO_AVAILABLE:
            return self._fallback_encrypt(session_data)
        
        try:
            iv = os.urandom(16)
            
            cipher = Cipher(
                algorithms.AES(self.session_key),
                modes.CBC(iv),
                backend=self._backend
            )
            
            encryptor = cipher.encryptor()
            
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(session_data.encode()) + padder.finalize()
            
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            
            combined = iv + encrypted
            return base64.b64encode(combined).decode()
            
        except Exception as e:
            logger.error(f"Session encryption error: {e}")
            return self._fallback_encrypt(session_data)
    
    def decrypt_session_string(self, encrypted_data: str) -> Optional[str]:
        """Дешифрування строки сесії"""
        if not encrypted_data:
            return None
        
        if not CRYPTO_AVAILABLE:
            return self._fallback_decrypt(encrypted_data)
        
        try:
            combined = base64.b64decode(encrypted_data)
            
            iv = combined[:16]
            ciphertext = combined[16:]
            
            cipher = Cipher(
                algorithms.AES(self.session_key),
                modes.CBC(iv),
                backend=self._backend
            )
            
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return data.decode()
            
        except Exception as e:
            logger.error(f"Session decryption error: {e}")
            return self._fallback_decrypt(encrypted_data)
    
    def encrypt_proxy_credentials(self, proxy_data: Dict) -> str:
        """Шифрування даних проксі"""
        import json
        data_str = json.dumps(proxy_data)
        
        if not CRYPTO_AVAILABLE:
            return self._fallback_encrypt(data_str)
        
        try:
            iv = os.urandom(16)
            
            cipher = Cipher(
                algorithms.AES(self.proxy_key),
                modes.CBC(iv),
                backend=self._backend
            )
            
            encryptor = cipher.encryptor()
            
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data_str.encode()) + padder.finalize()
            
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            
            combined = iv + encrypted
            return base64.b64encode(combined).decode()
            
        except Exception as e:
            logger.error(f"Proxy encryption error: {e}")
            return self._fallback_encrypt(data_str)
    
    def decrypt_proxy_credentials(self, encrypted_data: str) -> Optional[Dict]:
        """Дешифрування даних проксі"""
        import json
        
        if not CRYPTO_AVAILABLE:
            decrypted = self._fallback_decrypt(encrypted_data)
            return json.loads(decrypted) if decrypted else None
        
        try:
            combined = base64.b64decode(encrypted_data)
            
            iv = combined[:16]
            ciphertext = combined[16:]
            
            cipher = Cipher(
                algorithms.AES(self.proxy_key),
                modes.CBC(iv),
                backend=self._backend
            )
            
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            unpadder = padding.PKCS7(128).unpadder()
            data = unpadder.update(padded_data) + unpadder.finalize()
            
            return json.loads(data.decode())
            
        except Exception as e:
            logger.error(f"Proxy decryption error: {e}")
            return None
    
    def encrypt(self, data: str) -> str:
        """Загальне шифрування даних"""
        return self.encrypt_session_string(data)
    
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Загальне дешифрування даних"""
        return self.decrypt_session_string(encrypted_data)
    
    def encrypt_session(self, session_string: str) -> str:
        """Alias для сумісності"""
        return self.encrypt_session_string(session_string)
    
    def decrypt_session(self, encrypted_session: str) -> Optional[str]:
        """Alias для сумісності"""
        return self.decrypt_session_string(encrypted_session)
    
    def _fallback_encrypt(self, data: str) -> str:
        """XOR шифрування як fallback"""
        if not data:
            return ""
        
        data_bytes = data.encode('utf-8')
        key = self.session_key if isinstance(self.session_key, bytes) else self.session_key.encode()
        encrypted = bytes([data_bytes[i] ^ key[i % len(key)] for i in range(len(data_bytes))])
        
        signature = hmac.new(key, encrypted, hashlib.sha256).digest()[:8]
        result = signature + encrypted
        return base64.urlsafe_b64encode(result).decode()
    
    def _fallback_decrypt(self, encrypted_data: str) -> Optional[str]:
        """XOR дешифрування як fallback"""
        if not encrypted_data:
            return None
        
        try:
            raw = base64.urlsafe_b64decode(encrypted_data.encode())
            
            stored_signature = raw[:8]
            encrypted = raw[8:]
            
            key = self.session_key if isinstance(self.session_key, bytes) else self.session_key.encode()
            expected_signature = hmac.new(key, encrypted, hashlib.sha256).digest()[:8]
            
            if not hmac.compare_digest(stored_signature, expected_signature):
                logger.warning("Signature verification failed")
                return None
            
            decrypted = bytes([encrypted[i] ^ key[i % len(key)] for i in range(len(encrypted))])
            return decrypted.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Fallback decryption error: {e}")
            return None
    
    def hash_data(self, data: str) -> str:
        """SHA-256 хеш даних"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_hash(self, data: str, hash_value: str) -> bool:
        """Перевірка хешу"""
        return hmac.compare_digest(self.hash_data(data), hash_value)
    
    def generate_secure_key(self, prefix: str = "SHADOW") -> str:
        """Генерація безпечного ключа"""
        import secrets
        random_part = secrets.token_hex(8).upper()
        return f"{prefix}-{random_part[:4]}-{random_part[4:]}"
    
    def generate_fingerprint(self, data: Dict) -> str:
        """Генерація унікального fingerprint"""
        import json
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

encryption_manager = EncryptionManager()

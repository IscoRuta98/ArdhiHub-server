from cryptography.fernet import Fernet

from config.settings import settings


# Generate a key for encryption and decryption
# You must store this key securely;
# anyone with access to it can decrypt your data
def generate_encryption_key() -> bytes:
    return Fernet.generate_key()


# Encrypt the given data using the provided key
def encrypt_data(data: str) -> bytes:
    fernet = Fernet(settings.encryption_key.encode())
    encrypted_data = fernet.encrypt(data.encode())
    return encrypted_data


# Decrypt the given data using the provided key
def decrypt_data(encrypted_data: bytes) -> str:
    fernet = Fernet(settings.encryption_key.encode())
    decrypted_data = fernet.decrypt(encrypted_data).decode()
    return decrypted_data

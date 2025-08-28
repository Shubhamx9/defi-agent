def encrypt(data: str) -> str:
    """
    Encrypt wallet data for storage.
    
    In a production system, this would use proper encryption with a master key.
    For now, we'll use a simple base64 encoding (NOT secure for production).
    
    Args:
        data: The wallet data to encrypt
        
    Returns:
        Encrypted data string
    """
    import base64
    # In production, use proper encryption like AES
    # For demo purposes, just base64 encode
    return base64.b64encode(data.encode()).decode()

import base64
import binascii

def decrypt(encrypted_data: str) -> str:
    """
    Decrypt wallet data from storage.

    In production, this should use proper key management (e.g., KMS/HSM).
    Currently attempts base64 decoding for newer records, 
    otherwise returns the raw string (legacy fallback).

    Args:
        encrypted_data (str): The encrypted data from the database.

    Returns:
        str: The decrypted wallet secret (likely a hex string).
    """
    if not encrypted_data:
        raise ValueError("No encrypted data provided")

    try:
        # Attempt base64 decode (newer format)
        decoded_bytes = base64.b64decode(encrypted_data, validate=True)
        return decoded_bytes.decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        # Legacy format (already plain text/hex)
        return encrypted_data

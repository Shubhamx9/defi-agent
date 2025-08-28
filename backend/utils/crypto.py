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

def decrypt(encrypted_data: str) -> str:
    """
    Decrypt wallet data from storage.

    In a true production system with end-to-end encryption, this function 
    would contain logic to decrypt the 'encrypted_data' using a master key.
    
    Args:
        encrypted_data: The encrypted data from the database.

    Returns:
        The decrypted wallet secret.
    """
    import base64
    try:
        # Try to base64 decode first (for new encrypted data)
        decoded = base64.b64decode(encrypted_data).decode()
        return decoded
    except:
        # If decoding fails, assume it's already in the correct format (legacy data)
        return encrypted_data
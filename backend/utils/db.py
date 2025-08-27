import dataclasses

@dataclasses.dataclass
class WalletInfo:
    """A simple data class to represent wallet information."""
    encrypted_wallet_secret: str  # The private key/seed from user's CDP wallet
    wallet_address: str  # The user's wallet address
    network_id: str

# In-memory storage for demo (replace with real database)
_user_wallets = {}

def save_user_wallet(user_id: str, encrypted_wallet_secret: str, wallet_address: str, network_id: str) -> bool:
    """
    Save a user's wallet information to the database.
    
    Args:
        user_id: The user's unique identifier
        encrypted_wallet_secret: The encrypted private key/wallet data
        wallet_address: The user's wallet address
        network_id: The blockchain network (e.g., "base-sepolia")
    
    Returns:
        True if successful, False otherwise
    """
    try:
        _user_wallets[user_id] = WalletInfo(
            encrypted_wallet_secret=encrypted_wallet_secret,
            wallet_address=wallet_address,
            network_id=network_id
        )
        return True
    except Exception as e:
        print(f"Error saving wallet for user {user_id}: {e}")
        return False

def get_wallet_info_from_db(user_id: str) -> WalletInfo:
    """
    Fetches wallet information for a given user.

    Args:
        user_id: The ID of the user.

    Returns:
        A WalletInfo object with the user's wallet details, or None if not found.
    """
    # Check in-memory storage first
    if user_id in _user_wallets:
        return _user_wallets[user_id]
    
    return None

def create_wallet_info_from_request(wallet_address: str, wallet_secret: str, network_id: str = "base-sepolia") -> WalletInfo:
    """
    Create a WalletInfo object from request data (for dynamic wallet handling).
    
    Args:
        wallet_address: The user's wallet address
        wallet_secret: The user's wallet private key/secret
        network_id: The blockchain network
    
    Returns:
        A WalletInfo object
    """
    from backend.utils.crypto import encrypt
    
    # Encrypt the wallet secret for security
    encrypted_secret = encrypt(wallet_secret)
    
    return WalletInfo(
        encrypted_wallet_secret=encrypted_secret,
        wallet_address=wallet_address,
        network_id=network_id
    )

def remove_user_wallet(user_id: str) -> bool:
    """
    Remove a user's wallet information from the database.
    
    Args:
        user_id: The user's unique identifier
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if user_id in _user_wallets:
            del _user_wallets[user_id]
        return True
    except Exception as e:
        print(f"Error removing wallet for user {user_id}: {e}")
        return False

def list_connected_users() -> list:
    """
    Get a list of all users with connected wallets.
    
    Returns:
        List of user IDs with connected wallets
    """
    return list(_user_wallets.keys())
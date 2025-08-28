# import dataclasses

# @dataclasses.dataclass
# class WalletInfo:
#     """A simple data class to represent wallet information."""
#     encrypted_wallet_secret: str  # The private key/seed from user's CDP wallet


async def get_wallet_info_from_db(user_id: str) -> dict:
    """
    Fetches wallet information for a given user.

    Args:
        user_id: The ID of the user.

    Returns:
        A WalletInfo object with the user's wallet details, or None if not found.
    """
    return {
        "encrypted_wallet_secret" : "4c077711d8366461ac171417b7f9e60d701d2427b5464d19f6ce00b8bf74c93ecbdcf8c878d434c0ea52b7494d5ac726b8740ab3cdcf6f177d453755a3fb71dd"
    }

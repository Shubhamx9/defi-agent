"""
CDP Agent initialization module.
Handles SmartWallet + AgentKit configuration.
"""

from backend.logging_setup import logger
from backend.config.settings import cdp_settings
from backend.utils import crypto, db
from backend.utils.db import get_wallet_info_from_db

# Apply nest_asyncio to handle nested event loops
import nest_asyncio

# Try to apply nest_asyncio, but handle uvloop gracefully
try:
    nest_asyncio.apply()
except ValueError as e:
    if "uvloop" in str(e):
        # uvloop detected, patch it manually
        import asyncio
        loop = asyncio.get_event_loop()
        if hasattr(loop, '_nest_patched'):
            pass  # Already patched
        else:
            # Mark as patched to avoid re-patching
            loop._nest_patched = True
    else:
        raise


async def init_cdp_agent(user_id: str, wallet_info=None):
    """
    Initialize a SmartWallet Agent for a given user.
    Returns AgentKit instance.

    """

    try:
        logger.info(f"Initializing SmartWallet Agent for user: {user_id}")

        # Lazy import heavy deps
        from coinbase_agentkit import (
            AgentKit, AgentKitConfig,
            CdpSmartWalletProvider, CdpSmartWalletProviderConfig,
            cdp_api_action_provider,
            erc20_action_provider,
            pyth_action_provider,
            wallet_action_provider,
            x402_action_provider,
        )

        # 🔹 Fetch wallet info if not provided
        if not wallet_info:
            wallet_info = await db.get_wallet_info_from_db(user_id)
            if not wallet_info:
                logger.error(f"No wallet info found for user {user_id}")
                return None

        # 🔹 Decrypt developer wallet secret
        owner_key = crypto.decrypt(wallet_info["encrypted_wallet_secret"])
        logger.info(f"Decrypted wallet secret (truncated): {owner_key[:10]}...")

        # 🔹 Configure SmartWalletProvider
        wallet_provider = CdpSmartWalletProvider(
            CdpSmartWalletProviderConfig(
                api_key_id=cdp_settings.CDP_API_KEY_ID,
                api_key_secret=cdp_settings.CDP_API_KEY_SECRET,
                wallet_secret=cdp_settings.CDP_WALLET_SECRET,   # developer secret
                owner=owner_key,                   # user’s key/address
                network_id=cdp_settings.CDP_NETWORK_ID,
            )
        )

        # 🔹 Init AgentKit with all action providers
        agent = AgentKit(
            AgentKitConfig(
                wallet_provider=wallet_provider,
                action_providers=[
                    cdp_api_action_provider(),
                    erc20_action_provider(),
                    pyth_action_provider(),
                    wallet_action_provider(),
                    x402_action_provider(),
                ],
            )
        )

        logger.info(f"AgentKit initialized for user {user_id}")
        return agent

    except ValueError as e:
        if "uvloop" in str(e) or "event loop is already running" in str(e):
            logger.error(f"Event loop conflict detected. Try running with: uvicorn main:app --loop asyncio")
            return None
        else:
            logger.error("Error initializing SmartWallet Agent", exc_info=True)
            return None
    except Exception:
        logger.error("Error initializing SmartWallet Agent", exc_info=True)
        return None

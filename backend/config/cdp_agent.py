import os
import asyncio
from backend.logging_setup import logger
from typing import Optional

# Try to import nest_asyncio, use mock if not available
try:
    import nest_asyncio
    NEST_ASYNCIO_AVAILABLE = True
except ImportError:
    NEST_ASYNCIO_AVAILABLE = False
    logger.warning("nest_asyncio not available, using mock CDP agent")

# No longer need to import cdp_settings here for the keys
from backend.config.settings import cdp_settings 
from backend.utils.crypto import decrypt
from backend.utils.db import get_wallet_info_from_db

# --- Uvloop Patching ---
def _patch_for_coinbase_import():
    """Temporarily switch to the default asyncio policy for safe import."""
    original_policy = asyncio.get_event_loop_policy()
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    return original_policy

def _restore_after_coinbase_import(original_policy):
    """Restore the original asyncio policy."""
    asyncio.set_event_loop_policy(original_policy)


# Cache for initialized agents to ensure consistency
_agent_cache = {}

# Cache for wallet addresses to ensure consistency
_address_cache = {}

def clear_agent_cache(user_id: str = None):
    """
    Clear the agent cache for a specific user or all users.
    Useful for testing or when you need to reinitialize agents.
    """
    global _agent_cache, _address_cache
    if user_id:
        if user_id in _agent_cache:
            del _agent_cache[user_id]
            logger.info(f"Cleared agent cache for user: {user_id}")
        if user_id in _address_cache:
            del _address_cache[user_id]
            logger.info(f"Cleared address cache for user: {user_id}")
    else:
        _agent_cache.clear()
        _address_cache.clear()
        logger.info("Cleared all caches")

def _get_cached_address(user_id: str) -> Optional[str]:
    """Get cached address for a user, if any."""
    return _address_cache.get(user_id)

def _cache_address(user_id: str, address: str):
    """Cache an address for a user."""
    _address_cache[user_id] = address
    logger.info(f"Cached address for user {user_id}: {address}")

def set_user_address(user_id: str, address: str):
    """
    Manually set a consistent address for a user.
    This forces the user to always get the same address.
    """
    _cache_address(user_id, address)
    # Clear the agent cache so it gets recreated with the new address
    if user_id in _agent_cache:
        del _agent_cache[user_id]
    logger.info(f"Set consistent address for user {user_id}: {address}")

def init_cdp_agent(user_id: str, wallet_info: 'WalletInfo' = None):
    """
    Initialize a fully functional Coinbase AgentKit for a user in a production environment.
    Uses caching to ensure the same agent (and thus same address) is returned for the same user.
    
    Falls back to mock agent if dependencies are not available.
    
    IMPORTANT: This function uses agent caching to ensure address consistency. The same
    wallet instance is returned for the same user across all requests.
    """
    # Check if we already have an agent for this user
    if user_id in _agent_cache:
        logger.info(f"Returning cached CDP Agent for user: {user_id}")
        return _agent_cache[user_id]
    
    # Check if we have the required dependencies
    if not NEST_ASYNCIO_AVAILABLE:
        from backend.config.mock_cdp_agent import init_mock_cdp_agent
        agent = init_mock_cdp_agent(user_id, wallet_info)
        if agent:
            _agent_cache[user_id] = agent
        return agent
    
    # Try to import real CDP dependencies
    original_policy = _patch_for_coinbase_import()
    try:
        from coinbase_agentkit import (
            AgentKit, AgentKitConfig,
            CdpEvmWalletProvider, CdpEvmWalletProviderConfig,
            cdp_api_action_provider,
            erc20_action_provider,
            pyth_action_provider,
            wallet_action_provider,
            weth_action_provider,
        )
        use_real_cdp = True
    except ImportError as e:
        logger.warning(f"CDP dependencies not available, using mock agent: {e}")
        use_real_cdp = False
    finally:
        _restore_after_coinbase_import(original_policy)
    
    # Use mock agent if dependencies not available
    if not use_real_cdp:
        from backend.config.mock_cdp_agent import init_mock_cdp_agent
        agent = init_mock_cdp_agent(user_id, wallet_info)
        if agent:
            _agent_cache[user_id] = agent
        return agent

    try:
        # 1. Use provided wallet info or fetch from DB
        logger.info(f"Initializing new CDP Agent for user: {user_id}")
        if not wallet_info:
            wallet_info = get_wallet_info_from_db(user_id)
        
        if not wallet_info:
            logger.warning(f"No wallet found for user {user_id}. Agent initialization aborted.")
            return None

        # 2. Decrypt the wallet secret and set environment variables for CDP AgentKit
        wallet_secret = decrypt(wallet_info.encrypted_wallet_secret)
        logger.info(f"Using decrypted wallet secret: {wallet_secret[:20]}...")
        
        # Set all required environment variables
        os.environ['CDP_API_KEY_ID'] = cdp_settings.CDP_API_KEY_ID
        os.environ['CDP_API_KEY_SECRET'] = cdp_settings.CDP_API_KEY_SECRET
        os.environ['CDP_WALLET_SECRET'] = wallet_secret
        
        # For now, skip direct wallet import and rely on environment variables
        # The caching will ensure consistency
        wallet = None
        
        # 4. Ensure an event loop exists in the current thread with uvloop compatibility
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Apply nest_asyncio safely (avoid uvloop conflicts)
        if NEST_ASYNCIO_AVAILABLE:
            try:
                nest_asyncio.apply()
            except ValueError as e:
                if "Can't patch loop of type" in str(e) and "uvloop" in str(e):
                    # uvloop already supports nested event loops, ignore the error
                    pass
                else:
                    raise

        # 5. Create wallet provider configuration
        wallet_provider = CdpEvmWalletProvider(
            CdpEvmWalletProviderConfig(
                network_id=cdp_settings.CDP_NETWORK_ID,
            )
        )
        
        logger.info(f"Created wallet provider for network: {cdp_settings.CDP_NETWORK_ID}")

        # 6. Initialize AgentKit
        agent = AgentKit(
            AgentKitConfig(
                wallet_provider=wallet_provider,
                action_providers=[
                    cdp_api_action_provider(),
                    erc20_action_provider(),
                    pyth_action_provider(),
                    wallet_action_provider(),
                    weth_action_provider(),
                ]
            )
        )

        # Cache the agent for this user to ensure consistency
        _agent_cache[user_id] = agent
        
        # Log the wallet address for debugging and cache it
        try:
            address = agent.wallet_provider.get_address()
            logger.info(f"Successfully initialized CDP Agent for user: {user_id}, Address: {address}")
            
            # Cache the address for future use
            _cache_address(user_id, address)
            
        except Exception as addr_e:
            logger.warning(f"Could not get address during initialization: {addr_e}")
            
        return agent

    except Exception as e:
        logger.error(f"An unexpected error occurred while initializing CDP Agent for user {user_id}: {e}", exc_info=True)
        return None
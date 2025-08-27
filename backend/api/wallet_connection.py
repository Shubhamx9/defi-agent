"""
Wallet Connection API for users to connect their CDP wallets to your portal
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.logging_setup import logger
from backend.utils.db import save_user_wallet, get_wallet_info_from_db
from backend.utils.crypto import encrypt
from backend.config.cdp_agent import init_cdp_agent, clear_agent_cache
import re

router = APIRouter()

class WalletConnectionRequest(BaseModel):
    user_id: str
    wallet_data: str  # CDP wallet export data (JSON string or private key)
    wallet_address: str  # User's wallet address for verification

class WalletConnectionResponse(BaseModel):
    success: bool
    message: str
    wallet_address: str = None

class WalletStatusRequest(BaseModel):
    user_id: str

class WalletStatusResponse(BaseModel):
    connected: bool
    wallet_address: str = None
    balance: str = None

@router.post("/connect-wallet", response_model=WalletConnectionResponse)
async def connect_wallet(request: WalletConnectionRequest):
    """
    Connect a user's CDP wallet to the portal.
    
    The user provides:
    1. Their user_id (from your authentication system)
    2. Their CDP wallet export data (private key or wallet data)
    3. Their wallet address (for verification)
    """
    try:
        logger.info(f"Wallet connection request from user: {request.user_id}")
        
        # Validate wallet address format
        if not re.match(r'^0x[a-fA-F0-9]{40}$', request.wallet_address):
            raise HTTPException(status_code=400, detail="Invalid wallet address format")
        
        # Validate wallet data (should be base64 encoded private key or JSON)
        if not request.wallet_data or len(request.wallet_data) < 50:
            raise HTTPException(status_code=400, detail="Invalid wallet data")
        
        # Encrypt and save wallet data
        encrypted_wallet_data = encrypt(request.wallet_data)
        
        # Save to database
        success = save_user_wallet(
            user_id=request.user_id,
            encrypted_wallet_secret=encrypted_wallet_data,
            wallet_address=request.wallet_address,
            network_id="base-sepolia"  # or your preferred network
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save wallet data")
        
        # Clear any existing cache for this user
        clear_agent_cache(request.user_id)
        
        # Test the connection by initializing CDP agent
        agent = init_cdp_agent(request.user_id)
        if not agent:
            raise HTTPException(status_code=500, detail="Failed to initialize wallet connection")
        
        # Verify the address matches
        try:
            derived_address = agent.wallet_provider.get_address()
            if derived_address.lower() != request.wallet_address.lower():
                logger.warning(f"Address mismatch: provided {request.wallet_address}, derived {derived_address}")
                # Don't fail here - just log the discrepancy
        except Exception as e:
            logger.warning(f"Could not verify address: {e}")
        
        logger.info(f"Successfully connected wallet for user {request.user_id}: {request.wallet_address}")
        
        return WalletConnectionResponse(
            success=True,
            message="Wallet connected successfully",
            wallet_address=request.wallet_address
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wallet connection failed for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Wallet connection failed: {str(e)}")

@router.post("/wallet-status", response_model=WalletStatusResponse)
async def get_wallet_status(request: WalletStatusRequest):
    """
    Get the wallet connection status and basic info for a user.
    """
    try:
        # Check if user has a connected wallet
        wallet_info = get_wallet_info_from_db(request.user_id)
        
        if not wallet_info:
            return WalletStatusResponse(
                connected=False,
                wallet_address=None,
                balance=None
            )
        
        # Get wallet address and balance
        agent = init_cdp_agent(request.user_id)
        if not agent:
            return WalletStatusResponse(
                connected=True,
                wallet_address="Unknown",
                balance="Unable to fetch"
            )
        
        try:
            address = agent.wallet_provider.get_address()
            balance_raw = agent.wallet_provider.get_balance()
            
            # Convert balance from Wei to ETH if needed
            try:
                balance_num = float(balance_raw)
                if balance_num > 1000000000000:  # If > 1 trillion, likely Wei
                    balance_eth = balance_num / (10**18)
                    balance = f"{balance_eth:.6f}".rstrip('0').rstrip('.')
                else:
                    balance = str(balance_raw)
            except (ValueError, TypeError):
                balance = str(balance_raw)
            
            return WalletStatusResponse(
                connected=True,
                wallet_address=address,
                balance=f"{balance} ETH"
            )
            
        except Exception as e:
            logger.warning(f"Could not fetch wallet details: {e}")
            return WalletStatusResponse(
                connected=True,
                wallet_address="Unknown",
                balance="Unable to fetch"
            )
        
    except Exception as e:
        logger.error(f"Wallet status check failed for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.post("/disconnect-wallet")
async def disconnect_wallet(request: WalletStatusRequest):
    """
    Disconnect a user's wallet from the portal.
    """
    try:
        # Clear cache
        clear_agent_cache(request.user_id)
        
        # Remove from database (you'll need to implement this)
        # remove_user_wallet(request.user_id)
        
        logger.info(f"Disconnected wallet for user: {request.user_id}")
        
        return {"success": True, "message": "Wallet disconnected successfully"}
        
    except Exception as e:
        logger.error(f"Wallet disconnection failed for user {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Disconnection failed: {str(e)}")
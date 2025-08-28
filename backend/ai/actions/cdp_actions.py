from backend.logging_setup import logger

#=======================================================
async def get_wallet_balance_cdp(user_id: str) -> str:
    """
    Fetch the wallet balance for a given user.
    """
    from backend.config.cdp_agent import init_cdp_agent
    agent = await init_cdp_agent(user_id)
    if not agent:
        return "❌ Unable to initialize wallet"

    wp = agent.wallet_provider
    try:
        address = wp.get_address()
    except Exception as e:
        return f"❌ Failed to get wallet address: {e}"

    try:
        bal = wp.get_balance()
        return f"{float(bal)/1e18:.6f} ETH (Address: {address})"
    except Exception as e:
        logger.warning(f"Balance fetch failed: {e}")
        return f"Wallet connected: {address} (balance check failed)"
    
#=======================================================

async def get_wallet_address_cdp(user_id: str) -> str:
    """
    Fetch the wallet address for a given user.
    """
    from backend.config.cdp_agent import init_cdp_agent
    agent = await init_cdp_agent(user_id)
    if not agent:
        return "❌ Unable to initialize wallet"
    try:
        return agent.wallet_provider.get_address()
    except Exception as e:
        logger.error(f"Get address failed: {e}")
        return f"❌ Error getting address: {str(e)}"
    

#=======================================================

async def send_tokens_cdp(user_id: str, params: dict) -> str:
    """
    Sends tokens using Coinbase CDP AgentKit.
    params: {'amount': float, 'token': 'ETH', 'recipient': '0x...'}
    Returns transaction hash or error string.
    """
    from backend.config.cdp_agent import init_cdp_agent
    agent = await init_cdp_agent(user_id)
    if not agent:
        raise Exception("Failed to initialize CDP agent")

    token = params["token"].upper()
    amount = params["amount"]
    recipient = params["recipient"]
    wallet_provider = agent.wallet_provider

    if token == "ETH":
        try:
            amount_wei = int(float(amount) * 10**18)
            tx = wallet_provider.send_transaction({"to": recipient, "value": amount_wei})
            return tx.hash if hasattr(tx, "hash") else str(tx)
        except AttributeError:
            for attempt in [
                lambda: wallet_provider.transfer(recipient, amount_wei),
                lambda: wallet_provider.transfer(recipient, str(amount)),
            ]:
                try:
                    tx = attempt()
                    return tx.hash if hasattr(tx, "hash") else str(tx)
                except AttributeError:
                    continue
    else:
        try:
            tx = agent.erc20.transfer(token=token, amount=amount, to_address=recipient)
            return tx.hash if hasattr(tx, "hash") else str(tx)
        except Exception as e:
            logger.error(f"ERC20 transfer failed: {e}")
            if "Insufficient balance" in str(e):
                return f"❌ Insufficient balance to send {amount} {token}."
            raise

    return "❌ Transfer failed."


#=======================================================

pending_payments = {}
pending_transfers = {}


# ---------- X402 ----------
def get_service_info(service: str) -> dict:
    return {
        "api_access": {
            "name": "Premium API Access",
            "recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C87",
        },
        "data_feed": {
            "name": "Real-time Data Feed",
            "recipient_address": "0x8ba1f109551bD432803012645E136c22C501e5b5",
        },
        "oracle_query": {
            "name": "Oracle Query Service",
            "recipient_address": "0x1a5F9352Af8Af974bFC03399e3767DF6370d82e4",
        },
    }.get(service)


async def process_x402_request(query: str, user_id: str) -> str:
    from backend.config.cdp_agent import init_cdp_agent
    from backend.ai.extractors import extract_x402_parameters
    q = query.lower().strip()

    ##ADD TYPO CHECKING
    
    if user_id in pending_payments:
        # Check if pending payment has expired
        import time
        payment_data = pending_payments[user_id]
        if time.time() > payment_data.get("expires_at", 0):
            del pending_payments[user_id]
            return "⏰ Your previous payment request has expired. Please make a new request."
        
        if "confirm" in q:
            try:
                agent = await init_cdp_agent(user_id)
                # Remove timeout fields before passing to CDP
                payment_params = {k: v for k, v in payment_data.items() 
                                if k not in ["created_at", "expires_at"]}
                tx = agent.x402.pay(**payment_params)
                del pending_payments[user_id]
                return f"✅ x402 Payment executed. Tx: {tx.hash}"
            except Exception as e:
                del pending_payments[user_id]
                return f"❌ Payment failed: {e}"
        elif "cancel" in q:
            del pending_payments[user_id]
            return "❌ Payment cancelled."
        else:
            remaining_time = int(payment_data.get("expires_at", 0) - time.time())
            return f"🤔 You have a pending payment (expires in {remaining_time}s). Reply 'confirm payment' or 'cancel'."

    try:
        params = extract_x402_parameters(query)
        service, amount, token = params["service"], params["amount"], params.get("token", "ETH")
        
        # Validate extracted parameters
        if not service:
            return "❌ Service type not specified. Please specify which service you want to pay for."
        
        if amount is None:
            return "❌ Payment amount not specified. Please specify how much you want to pay."
        
        # Validate amount is positive number
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return "❌ Payment amount must be greater than zero."
            if amount_float > 1000000:  # Reasonable upper limit
                return "❌ Payment amount too large. Please specify a reasonable amount."
        except (ValueError, TypeError):
            return "❌ Invalid payment amount. Please specify a valid number."
        
        # Basic typo checking for common service names
        service_corrections = {
            "api": "api_access",
            "data": "data_feed", 
            "oracle": "oracle_query",
            "feed": "data_feed"
        }
        if service in service_corrections:
            service = service_corrections[service]
        
        info = get_service_info(service)
        if not info:
            return f"⚠️ Service '{service}' not found. Available services: api_access, data_feed, oracle_query"
        
        # Validate token symbol
        valid_tokens = ["ETH", "USDC", "USDT", "DAI"]
        if token.upper() not in valid_tokens:
            return f"❌ Unsupported token '{token}'. Supported tokens: {', '.join(valid_tokens)}"
        
        # Store validated parameters with timeout (5 minutes from now)
        import time
        pending_payments[user_id] = {
            "service_id": service,
            "amount": amount_float,
            "token": token.upper(),
            "to_address": info["recipient_address"],
            "created_at": time.time(),
            "expires_at": time.time() + 300  # 5 minutes timeout
        }
        return f"🔍 Confirm {amount_float} {token.upper()} for {info['name']} → {info['recipient_address']}"
    except Exception as e:
        logger.error(f"x402 flow failed: {e}")
        return "❌ Could not process x402 request."

#=======================================================

async def get_token_price(symbol: str) -> float:
    from backend.config.cdp_agent import init_cdp_agent
    agent = await init_cdp_agent("oracle_user")
    return agent.pyth.get_price(symbol)

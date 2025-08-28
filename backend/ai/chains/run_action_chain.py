from backend.logging_setup import logger
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable
from backend.utils.model_selector import tiny_model
from backend.ai.extractors.transfer_extractor import extract_transfer_parameters
from backend.ai.extractors.price_extractor import extract_price_parameters
# from backend.ai.extractors.wrap_extractor import extract_wrap_parameters
from backend.ai.extractors.balance_extractor import extract_balance_parameters
from backend.utils.apy import get_top_low_yield_apy_pools
from backend.ai.extractors.x402_extractor import extract_x402_parameters



def send_tokens_cdp(user_id: str, params: dict, wallet_info: 'WalletInfo' = None) -> str:
    """
    Sends tokens using Coinbase CDP AgentKit.
    params: {'amount': float, 'token': 'ETH', 'recipient': '0x...'}
    Returns transaction hash.
    """
    # Lazy import to avoid uvloop conflicts
    from backend.config.cdp_agent import init_cdp_agent
    
    agent = init_cdp_agent(user_id, wallet_info)
    if not agent:
        raise Exception("Failed to initialize CDP agent")
    
    token = params['token'].upper()
    amount = params['amount']
    recipient = params['recipient']
    
    # Use wallet provider directly for transfers
    wallet_provider = agent.wallet_provider
    
    if token == 'ETH':
            # For native ETH transfers, convert amount to Wei and use send_transaction
            try:
                # Convert ETH to Wei (1 ETH = 10^18 Wei)
                amount_wei = int(float(amount) * 10**18)
                
                # Create transaction data
                tx_data = {
                    'to': recipient,
                    'value': amount_wei
                }
                
                # Send the transaction
                tx = wallet_provider.send_transaction(tx_data)
                return tx.hash if hasattr(tx, 'hash') else str(tx)
                
            except AttributeError:
                # If send_transaction doesn't exist, try other methods
                try:
                    # Try transfer method with Wei amount
                    tx = wallet_provider.transfer(recipient, amount_wei)
                    return tx.hash if hasattr(tx, 'hash') else str(tx)
                except AttributeError:
                    # Try with string amount
                    tx = wallet_provider.transfer(recipient, str(amount))
                    return tx.hash if hasattr(tx, 'hash') else str(tx)
    else:
            # For ERC-20 tokens, use the erc20 action provider
        try:
            tx = agent.erc20.transfer(
                token=token,
                amount=amount,
                to_address=recipient
            )
            return tx.hash if hasattr(tx, 'hash') else str(tx)
        except AttributeError as e:
                logger.error(f"ERC20 transfer method not found: {e}")
                raise Exception(f"ERC20 transfer not supported: {e}")
        except Exception as api_error:
            # Handle CDP API errors more gracefully
            error_msg = str(api_error)
            if "Insufficient balance" in error_msg:
                return f"❌ Insufficient balance to send {amount} {token}. Please check your wallet balance."
            elif "invalid_request" in error_msg:
                return f"❌ Invalid transaction request: {error_msg}"
            else:
                logger.error(f"CDP transaction failed: {api_error}")
                raise api_error
    
    return tx.hash if hasattr(tx, 'hash') else str(tx)

def get_wallet_address_cdp(user_id: str, wallet_info: 'WalletInfo' = None) -> str:
    """
    Get just the wallet address for a user.
    """
    # Lazy import to avoid uvloop conflicts
    from backend.config.cdp_agent import init_cdp_agent
    
    agent = init_cdp_agent(user_id, wallet_info)
    if not agent:
        return "❌ Unable to initialize wallet"
    
    try:
        address = agent.wallet_provider.get_address()
        logger.info(f"Wallet address for user {user_id}: {address}")
        return address
    except Exception as e:
        logger.error(f"Failed to get wallet address for user {user_id}: {e}")
        return f"❌ Error getting address: {str(e)}"

def get_wallet_balance_cdp(user_id: str, token: str = None, wallet_info: 'WalletInfo' = None) -> str:
    """
    Fetch user's wallet balance. If token=None, fetch all balances.
    """
    # Lazy import to avoid uvloop conflicts
    from backend.config.cdp_agent import init_cdp_agent
    
    agent = init_cdp_agent(user_id, wallet_info)
    if not agent:
        return "❌ Unable to initialize wallet. Please check your configuration."
    
    try:
        # Get the wallet provider (which has direct balance methods)
        wallet_provider = agent.wallet_provider
        
        # Get wallet address first
        try:
            address = wallet_provider.get_address()
            logger.info(f"Wallet address for user {user_id}: {address}")
        except Exception as e:
            logger.error(f"Failed to get wallet address for user {user_id}: {e}")
            return f"❌ Failed to get wallet address: {str(e)}"
        
        if token and token.upper() != 'ETH':
            # Get balance for specific ERC-20 token
            try:
                balance_raw = wallet_provider.get_balance(asset_id=token.upper())
                
                # Most ERC-20 tokens also use 18 decimals, so convert if needed
                try:
                    balance_num = float(balance_raw)
                    if balance_num > 1000000000000:  # If balance > 1 trillion, likely in smallest unit
                        balance_converted = balance_num / (10**18)  # Convert to token units
                        balance = f"{balance_converted:.6f}".rstrip('0').rstrip('.')  # Format nicely
                        logger.info(f"Converted {token} balance from smallest unit ({balance_raw}) to token units ({balance})")
                    else:
                        balance = str(balance_raw)  # Already in token units
                except (ValueError, TypeError):
                    balance = str(balance_raw)  # Use as-is if conversion fails
                
                return f"{balance} {token.upper()} (Address: {address})"
            except Exception as e:
                logger.warning(f"Failed to get {token} balance: {e}")
                return f"0 {token.upper()} (Address: {address})"
        else:
            # Get ETH balance (default)
            try:
                balance_raw = wallet_provider.get_balance()  # This might return Wei
                
                # Convert from Wei to ETH if the balance looks like Wei (very large number)
                try:
                    balance_num = float(balance_raw)
                    if balance_num > 1000000000000:  # If balance > 1 trillion, likely Wei
                        balance_eth = balance_num / (10**18)  # Convert Wei to ETH
                        balance = f"{balance_eth:.6f}".rstrip('0').rstrip('.')  # Format nicely
                        logger.info(f"Converted balance from Wei ({balance_raw}) to ETH ({balance})")
                    else:
                        balance = str(balance_raw)  # Already in ETH
                except (ValueError, TypeError):
                    balance = str(balance_raw)  # Use as-is if conversion fails
                
                return f"{balance} ETH (Address: {address})"
            except Exception as e:
                logger.warning(f"Failed to get ETH balance with default method: {e}")
                # Try with explicit ETH parameter
                try:
                    balance_raw = wallet_provider.get_balance(asset_id='ETH')
                    
                    # Convert from Wei to ETH if needed
                    try:
                        balance_num = float(balance_raw)
                        if balance_num > 1000000000000:  # If balance > 1 trillion, likely Wei
                            balance_eth = balance_num / (10**18)  # Convert Wei to ETH
                            balance = f"{balance_eth:.6f}".rstrip('0').rstrip('.')  # Format nicely
                            logger.info(f"Converted balance from Wei ({balance_raw}) to ETH ({balance})")
                        else:
                            balance = str(balance_raw)  # Already in ETH
                    except (ValueError, TypeError):
                        balance = str(balance_raw)  # Use as-is if conversion fails
                    
                    return f"{balance} ETH (Address: {address})"
                except Exception as e2:
                    logger.warning(f"Failed to get ETH balance with explicit method: {e2}")
                    return f"Wallet connected: {address} (balance check failed: {str(e2)})"
            
    except Exception as e:
        logger.error(f"Unexpected error getting balance for user {user_id}: {e}")
        return f"❌ Error getting balance: {str(e)}"

def get_token_price(symbol: str) -> float:
    """
    Fetch token price via CDP or Pyth oracle.
    """
    # Lazy import to avoid uvloop conflicts
    from backend.config.cdp_agent import init_cdp_agent
    
    agent = init_cdp_agent("oracle_user") 
    return agent.pyth.get_price(symbol)

# In a production environment, use a database or a user session cache (e.g., Redis) 
# to store pending payments. For this example, we'll use a simple in-memory dictionary.
pending_payments = {}

def get_service_info(service: str) -> dict:
    """
    Get detailed information and the official recipient address for x402 services.
    """
    service_info = {
        "api_access": {
            "name": "Premium API Access",
            "description": "Higher rate limits and advanced features.",
            "recipient_address": "0x742d35Cc6634C0532925a3b8D4C9db96590c6C87"
        },
        "data_feed": {
            "name": "Real-time Data Feed", 
            "description": "Access to real-time market data.",
            "recipient_address": "0x8ba1f109551bD432803012645E136c22C501e5b5"
        },
        "oracle_query": {
            "name": "Oracle Query Service",
            "description": "On-demand oracle queries for smart contracts.",
            "recipient_address": "0x1a5F9352Af8Af974bFC03399e3767DF6370d82e4"
        }
    }
    return service_info.get(service)

def process_x402_request(query: str, user_id: str) -> str:
    """
    Manages the full x402 payment flow: validation, confirmation, and execution.
    
    This function is stateful and handles:
    1. New payment requests by validating details and asking for confirmation.
    2. Confirmed or cancelled requests for a pending payment.
    """
    from backend.config.cdp_agent import init_cdp_agent
    query_lower = query.lower().strip()
    
    # --- Step 1: Check if there is a pending payment for this user ---
    if user_id in pending_payments:
        pending_tx = pending_payments[user_id]
        
        if "confirm" in query_lower:
            try:
                # Execute the confirmed payment
                agent = init_cdp_agent(user_id)
                
                # Use the x402-specific method for payment
                tx = agent.x402.pay(
                    service_id=pending_tx["service"],
                    amount=pending_tx["amount"],
                    token=pending_tx["token"],
                    to_address=pending_tx["recipient"]
                )
                
                # Clear the pending payment after successful execution
                del pending_payments[user_id]
                
                return f"""✅ **x402 Payment Executed Successfully!**

Service: {pending_tx['service_name']}
Amount: {pending_tx['amount']} {pending_tx['token']}
Transaction Hash: `{tx.hash}`

🎉 You now have access to the service!"""

            except Exception as e:
                logger.error(f"x402 payment execution failed for user {user_id}: {e}")
                del pending_payments[user_id] # Clear failed payment
                return "❌ Payment execution failed. The transaction was not sent. Please try again."

        elif "cancel" in query_lower:
            del pending_payments[user_id]
            return "❌ Payment cancelled. No transaction was sent."
        else:
            return f"🤔 You have a pending payment for **{pending_tx['amount']} {pending_tx['token']}** for the **{pending_tx['service_name']}** service. Please say 'confirm payment' or 'cancel payment'."

    # --- Step 2: Handle a new payment request ---
    try:
        params = extract_x402_parameters(query)
        service = params.get("service")
        amount = params.get("amount")
        token = params.get("token", "ETH")
        
        # --- Validation ---
        missing_details = []
        if not service or service == "generic_service":
            return "🤔 Please specify which service you'd like to pay for. Available services are: `API access`, `data feed`, or `oracle query`."
        
        service_info = get_service_info(service)
        if not service_info:
            return f"⚠️ Service '{service}' not found. Please choose a valid service."
        
        # The recipient address is now fetched from the service info, not from the user
        recipient = service_info["recipient_address"]
        
        if not amount:
            missing_details.append("payment amount")
        
        if missing_details:
            return f"I'm sorry, I need a bit more information. Please specify the **{' and '.join(missing_details)}**.\n\n*Example: 'Pay 0.01 ETH for API access.'*"

        # --- Amount Validation ---
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                return "⚠️ Payment amount must be a positive number."
        except (ValueError, TypeError):
            return f"⚠️ Invalid amount '{amount}'. Please specify a valid number."

        # --- Prepare for Confirmation ---
        payment_details = {
            "service": service,
            "service_name": service_info["name"],
            "amount": str(amount_float), # Store as string for consistency
            "token": token,
            "recipient": recipient
        }
        
        # Store the validated details, waiting for user confirmation
        pending_payments[user_id] = payment_details
        
        # --- Ask for Confirmation ---
        confirmation_msg = f"""
🔍 **Please Confirm Your x402 Payment**

**Service**: {payment_details['service_name']}
**Amount**: {payment_details['amount']} {payment_details['token']}
**Recipient**: `{payment_details['recipient']}`

⚠️ This will execute a blockchain transaction.

To proceed, reply with **"confirm payment"**. To abort, reply with **"cancel"**.
        """
        return confirmation_msg.strip()

    except Exception as e:
        logger.error(f"x402 payment processing failed for user {user_id}: {e}")
        return "❌ I'm sorry, I couldn't process that request. Please try rephrasing it with clear details."



_action_sub_intent_prompt = ChatPromptTemplate.from_template(
    """Classify the user's action intent into one of:

- check_balance → user asks about wallet balance
- get_address → user asks for their wallet address
- send_tokens → user wants to transfer tokens
- pay_service → user wants to pay for an API/service (x402)(only classify here if API or service is explicitly mentioned)
- confirm_payment → user confirms a pending x402 payment
- get_price → user asks for token price
- wrap_eth → user wants to wrap or unwrap ETH
- search_APY → user wants to search for best APY
- search_invest → user wants to search for APY investment opportunities

User: {query}

Respond with ONLY one label from the above list.
Label:"""
)

@traceable(name="DeFi Action Sub-Intent Classification")
def classify_action_sub_intent(query: str) -> str:
    """
    Classify action intent into specific sub-intents.
    """
    try:
        model = tiny_model()
        msg = _action_sub_intent_prompt.format_messages(query=query.strip())
        out = model.invoke(msg)
        if not out or not out.content:
            logger.warning("Empty response from action sub-intent classification model")
            return "check_balance"
        return out.content.strip().lower()
    except Exception as e:
        logger.error(f"Action sub-intent classification error: {e}")
        return "check_balance"


# Add this near the top of your file with the other state dictionaries
pending_transfers = {}

@traceable(name="DeFi Action Execution")
def run_action_chain(query: str, user_id: str, wallet_address: str = None, wallet_secret: str = None) -> str:
    """
    Execute the appropriate DeFi action based on the user's query.
    Uses wallet data provided in the request for consistent operations.
    """
    # Create wallet info from request data if provided
    wallet_info = None
    if wallet_address and wallet_secret:
        from backend.utils.db import create_wallet_info_from_request
        wallet_info = create_wallet_info_from_request(wallet_address, wallet_secret)
        logger.info(f"Using wallet data from request: {wallet_address}")
    
    try:
        # Prioritize checking for pending actions before classifying a new intent
        if user_id in pending_transfers:
            sub_intent = "send_tokens"
        elif user_id in pending_payments and ("confirm" in query.lower() or "cancel" in query.lower()):
            sub_intent = "confirm_payment"
        else:
            sub_intent = classify_action_sub_intent(query)
            
        logger.info(f"Executing action for sub-intent: {sub_intent}")
    except Exception as e:
        logger.error(f"Action classification failed: {e}")
        return "Sorry, I couldn't understand your request."

    try:
        if sub_intent == "send_tokens":
            # --- STATEFUL LOGIC START ---
            
            # Start with any pending data for this user
            params = pending_transfers.get(user_id, {})
            
            # Extract new info from the current query
            new_params = extract_transfer_parameters(query)
            
            # Merge new info, overwriting old if necessary but keeping old if new is null
            params.update({k: v for k, v in new_params.items() if v is not None})

            # Check if the combined information is complete
            missing_fields = [f for f in ["amount", "token", "recipient"] if not params.get(f)]
            
            if missing_fields:
                # If still incomplete, save the current state and ask for what's missing
                pending_transfers[user_id] = params
                return f"Got it. Please provide the following details for the transfer: {', '.join(missing_fields)}."
            
            # If complete, execute the transaction
            tx_hash = send_tokens_cdp(user_id, params, wallet_info)
            
            # Clean up the pending transfer state
            if user_id in pending_transfers:
                del pending_transfers[user_id]
                
            return f"✅ Sent {params['amount']} {params['token']} to {params['recipient']}. Tx hash: {tx_hash}"
            # --- STATEFUL LOGIC END ---

        elif sub_intent == "check_balance":
            params = extract_balance_parameters(query)
            tokens = params.get("tokens", "all")
            
            # Handle single token extraction
            if isinstance(tokens, list) and len(tokens) == 1:
                token = tokens[0]
            elif isinstance(tokens, str) and tokens != "all":
                token = tokens
            else:
                token = None
            
            balance = get_wallet_balance_cdp(user_id, token)
            return f"💰 Your balance is {balance}."

        elif sub_intent == "get_address":
            address = get_wallet_address_cdp(user_id)
            if address.startswith("❌"):
                return address
            return f"📍 Your wallet address is: {address}"

        elif sub_intent == "get_price":
            params = extract_price_parameters(query)
            symbol = params.get("symbol") if params else None
            if not symbol:
                return "⚠️ Token symbol is missing for price check."

            price = get_token_price(symbol)
            return f"📈 Current price of {symbol} is {price} USD."
        
        elif sub_intent == "search_apy":
            apy_pools = get_top_low_yield_apy_pools()
            if "error" in apy_pools[0]:
                return apy_pools[0]["error"]
            if not apy_pools:
                return "No APY pools found with yield less than 20%."
            
            response_lines = ["Here are the top 3 APY pools with yields under 20%:"]
            for pool in apy_pools:
                response_lines.append(
                    f"- {pool['protocol']} ({pool['coinpair']} on {pool['chain']}): {pool['apy_percentage']}% APY, TVL: ${pool['tvl_usd']}"
                )
            return "\n".join(response_lines)
        
        elif sub_intent == "search_invest":
            return "Investment search functionality is coming soon!"
        
        elif sub_intent in ["pay_service", "confirm_payment"]:
            return process_x402_request(query, user_id)

        else:
            return "I’m not sure how to handle that request yet."
        
    except Exception as e:
        logger.error(f"Action execution failed: {e}")
        # Clean up pending state on failure
        if user_id in pending_transfers:
            del pending_transfers[user_id]
        
        # Handle specific CDP errors
        error_msg = str(e)
        if "Insufficient balance" in error_msg:
            return "❌ Insufficient balance to complete the transaction. Please check your wallet balance and ensure you have enough funds."
        elif "invalid fields" in error_msg or "invalid_address" in error_msg:
            return "❌ Invalid recipient address. Please provide a valid Ethereum address (starting with 0x)."
        elif "invalid_request" in error_msg:
            return f"❌ Invalid transaction request. Please check the recipient address and amount."
        elif "ApiError" in error_msg:
            return "❌ Transaction failed due to a blockchain error. Please try again or check your wallet status."
        else:
            return "Sorry, something went wrong while performing your action."
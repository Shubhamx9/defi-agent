from typing import Any, Dict
from pydantic import BaseModel, Field
import httpx
import json
import os

from x402.client import X402Client
from coinbase_agentkit import CdpEvmSmartWalletProvider, CdpEvmSmartWalletProviderConfig
from backend.routes.query import extract_action_details_dict
from backend.models.schemas import ActionExtractionResult

# --- SCHEMA DEFINITIONS ---

class TransactionInput(BaseModel):
    """Input schema for a DeFi transaction."""
    user_id: str = Field(..., description="User ID for wallet lookup")
    user_query: str = Field(..., description="Natural language transaction request")

class TransactionResult(BaseModel):
    """Result schema for a DeFi transaction."""
    status: str
    receipt: Any = None
    error: str = None

# --- WALLET DATA LOADER ---

WALLET_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_wallets.json")

def load_user_wallet(user_id: str) -> Dict[str, Any]:
    """Load wallet data for a user from JSON file."""
    if not os.path.exists(WALLET_DATA_PATH):
        raise FileNotFoundError(f"Wallet data file not found: {WALLET_DATA_PATH}")
    with open(WALLET_DATA_PATH, "r") as f:
        wallets = json.load(f)
    return wallets.get(user_id)

# --- TRANSACTION LOGIC ---

def build_payment_details(action: ActionExtractionResult, wallet_data: dict) -> dict:
    """Build payment details dict from extracted action and wallet data."""
    return {
        "protocol": action.protocol or "Unknown",
        "amount": str(action.amount),
        "payTo": wallet_data["payTo"],
        "asset": wallet_data["asset"],
        "network": wallet_data["network"]
    }

def defi_transaction_action(user_id: str, user_query: str) -> TransactionResult:
    """Perform a DeFi transaction based on extracted action and wallet data."""
    # Extract action details from user query
    action_dict = extract_action_details_dict(user_query, user_id)
    if not action_dict or not action_dict.get("amount") or not action_dict.get("action"):
        return TransactionResult(status="failed", error="Could not extract valid transaction details from user query.")

    # Validate and map to ActionExtractionResult schema
    try:
        action = ActionExtractionResult(**action_dict)
    except Exception as e:
        return TransactionResult(status="failed", error=f"Invalid action schema: {e}")

    # Fetch user wallet data
    wallet_data = load_user_wallet(user_id)
    if not wallet_data:
        return TransactionResult(status="failed", error=f"No wallet data found for user: {user_id}")

    # Prepare payment details
    payment_details = build_payment_details(action, wallet_data)

    # Set up the smart wallet provider
    wallet_provider = CdpEvmSmartWalletProvider(
        CdpEvmSmartWalletProviderConfig(
            api_key_id=wallet_data["api_key_id"],
            api_key_secret=wallet_data["api_key_secret"],
            wallet_secret=wallet_data["wallet_secret"],
            owner=wallet_data["owner_private_key"],
            network_id=payment_details["network"],
            paymaster_url=wallet_data.get("paymaster_url", "")
        )
    )

    # Configure the x402 client
    x402_client = X402Client(
        network=payment_details["network"],
        private_key=wallet_data["owner_private_key"],
        facilitator_url=wallet_data.get("facilitator_url", "https://x402.org/facilitator"),
        wallet_provider=wallet_provider
    )

    # Build payment payload
    payment_payload = x402_client.build_payment(
        amount=payment_details["amount"],
        to=payment_details["payTo"],
        asset=payment_details["asset"],
        protocol=payment_details["protocol"]
    )

    # Send the request to the paid endpoint
    headers = {
        "X-PAYMENT": json.dumps(payment_payload)
    }

    try:
        response = httpx.get(
            wallet_data.get("paid_endpoint", "https://api.your-resource.com/paid-endpoint"),
            headers=headers
        )
        if "X-PAYMENT-RESPONSE" in response.headers:
            receipt = json.loads(response.headers["X-PAYMENT-RESPONSE"])
            return TransactionResult(status="success", receipt=receipt)
        else:
            return TransactionResult(status="failed", error=response.text)
    except Exception as e:
        return TransactionResult(status="failed", error=str(e))

# --- ACTION PROVIDER CLASS ---

class TransactionAction:
    """Action class for DeFi transactions."""
    def __init__(self, name: str, description: str, function: callable, args_schema: type):
        self.name = name
        self.description = description
        self.function = function
        self.args_schema = args_schema

class TransactionActionProvider:
    """Provider for DeFi transaction actions."""
    def __init__(self):
        self.name = "defi_transaction_provider"
        self.action_providers = []

    def supports_network(self, network_id: str) -> bool:
        """Supports all EVM networks."""
        return True

    def get_actions(self) -> list:
        return [
            TransactionAction(
                name="defi_transaction",
                description="Perform a DeFi transaction based on user query and wallet data.",
                function=defi_transaction_action,
                args_schema=TransactionInput,
            )
        ]

def transaction_action_provider() -> TransactionActionProvider:
    """Create and return a transaction action provider."""
    return TransactionActionProvider()

# --- CLI ENTRYPOINT ---

if __name__ == "__main__":
    user_query = input("Enter your DeFi transaction request: ")
    user_id = input("Enter your user ID: ")
    result = defi_transaction_action(user_id, user_query)
    print("Transaction result:", result.json())

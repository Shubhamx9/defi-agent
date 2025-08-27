"""
Mock CDP Agent for testing when dependencies are not available
This simulates the CDP agent functionality for demonstration purposes
"""
import time
from typing import Optional
from backend.logging_setup import logger

class MockWalletProvider:
    """Mock wallet provider that simulates CDP functionality"""
    
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address
        
    def get_address(self) -> str:
        """Return the wallet address"""
        return self.wallet_address
    
    def get_balance(self, asset_id: str = None) -> str:
        """Return mock balance data"""
        if asset_id and asset_id.upper() != 'ETH':
            # Mock ERC-20 token balance
            if asset_id.upper() == 'USDC':
                return "1000000000"  # 1000 USDC (6 decimals)
            else:
                return "500000000000000000000"  # 500 tokens (18 decimals)
        else:
            # Mock ETH balance in Wei
            return "100000000000000000"  # 0.1 ETH in Wei
    
    def send_transaction(self, tx_data: dict):
        """Mock transaction sending"""
        class MockTransaction:
            def __init__(self):
                self.hash = f"0x{'a' * 64}"  # Mock transaction hash
        
        # Simulate network delay
        time.sleep(0.1)
        return MockTransaction()

class MockPyth:
    """Mock Pyth oracle for price data"""
    
    def get_price(self, symbol: str) -> float:
        """Return mock price data"""
        prices = {
            'ETH': 3500.50,
            'BTC': 65000.25,
            'USDC': 1.00,
            'USDT': 0.999,
            'LINK': 25.75
        }
        return prices.get(symbol.upper(), 100.0)  # Default price

class MockERC20:
    """Mock ERC-20 provider"""
    
    def transfer(self, token: str, amount: float, to_address: str):
        """Mock ERC-20 transfer"""
        class MockTransaction:
            def __init__(self):
                self.hash = f"0x{'b' * 64}"  # Mock transaction hash
        
        time.sleep(0.1)
        return MockTransaction()

class MockX402:
    """Mock x402 payment provider"""
    
    def pay(self, service_id: str, amount: str, token: str, to_address: str):
        """Mock x402 payment"""
        class MockTransaction:
            def __init__(self):
                self.hash = f"0x{'c' * 64}"  # Mock transaction hash
        
        time.sleep(0.1)
        return MockTransaction()

class MockCDPAgent:
    """Mock CDP Agent that simulates full functionality"""
    
    def __init__(self, wallet_address: str):
        self.wallet_provider = MockWalletProvider(wallet_address)
        self.pyth = MockPyth()
        self.erc20 = MockERC20()
        self.x402 = MockX402()
        logger.info(f"Mock CDP Agent initialized for address: {wallet_address}")

def init_mock_cdp_agent(user_id: str, wallet_info: 'WalletInfo' = None):
    """
    Initialize a mock CDP agent for testing purposes
    This simulates the real CDP agent when dependencies are not available
    """
    if not wallet_info:
        logger.warning(f"No wallet info provided for user {user_id}")
        return None
    
    try:
        # Create mock agent with the wallet address
        agent = MockCDPAgent(wallet_info.wallet_address)
        logger.info(f"Mock CDP Agent successfully initialized for user: {user_id}")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to initialize mock CDP agent for user {user_id}: {e}")
        return None
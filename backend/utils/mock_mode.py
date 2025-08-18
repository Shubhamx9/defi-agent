"""
Mock mode for testing without external API dependencies
"""
import json
import time
from typing import Dict, Any, List

class MockAIModel:
    """Mock AI model for testing"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    def invoke(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Mock AI response"""
        user_message = messages[-1].get("content", "").lower()
        
        # Mock intent classification
        if "swap" in user_message or "trade" in user_message:
            return {"content": "action_request"}
        elif "?" in user_message or "what" in user_message or "how" in user_message:
            return {"content": "general_query"}
        else:
            return {"content": "clarification"}
    
    def predict(self, text: str) -> str:
        """Mock prediction"""
        if "swap" in text.lower():
            return json.dumps({
                "action": "swap",
                "amount": 100,
                "token_in": "USDC",
                "token_out": "ETH",
                "protocol": "Uniswap"
            })
        return "This is a mock response for testing purposes."

class MockVectorDB:
    """Mock vector database for testing"""
    
    def query(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Mock vector search"""
        return [
            {
                "id": "mock-1",
                "score": 0.95,
                "metadata": {
                    "text": "DeFi (Decentralized Finance) refers to financial services built on blockchain technology.",
                    "source": "Mock DeFi Guide"
                }
            },
            {
                "id": "mock-2", 
                "score": 0.87,
                "metadata": {
                    "text": "Yield farming involves providing liquidity to earn rewards.",
                    "source": "Mock Yield Guide"
                }
            }
        ]

class MockRedis:
    """Mock Redis for testing"""
    
    def __init__(self):
        self.data = {}
    
    def set(self, key: str, value: str, ex: int = None):
        self.data[key] = value
        return True
    
    def get(self, key: str):
        return self.data.get(key)
    
    def delete(self, key: str):
        if key in self.data:
            del self.data[key]
        return True
    
    def ping(self):
        return True

# Global mock instances
mock_redis = MockRedis()
mock_vector_db = MockVectorDB()

def get_mock_ai_model(model_name: str = "mock-model"):
    """Get mock AI model"""
    return MockAIModel(model_name)

def get_mock_response(query: str, intent: str = "general_query") -> Dict[str, Any]:
    """Generate mock response based on query"""
    
    if intent == "general_query":
        return {
            "intent": "general_query",
            "answer": f"This is a mock response about: {query}. DeFi involves decentralized financial services built on blockchain technology.",
            "sources": ["Mock DeFi Guide", "Test Documentation"],
            "confidence": 0.95,
            "ai_system": "mock",
            "cost_analysis": {
                "tokens_used": 50,
                "estimated_cost": 0.0,
                "model_used": "mock-model"
            }
        }
    
    elif intent == "action_request":
        return {
            "intent": "action_request",
            "action_details": {
                "action": "swap",
                "amount": 100,
                "token_in": "USDC", 
                "token_out": "ETH",
                "protocol": "Uniswap",
                "readiness_percentage": 75
            },
            "missing_parameters": ["slippage_tolerance"],
            "suggested_questions": ["What slippage tolerance would you prefer? (0.1%, 0.5%, 1%)"],
            "transaction_ready": False,
            "ai_system": "mock"
        }
    
    else:  # clarification
        return {
            "intent": "clarification",
            "clarification": "I understand you're interested in DeFi. Could you be more specific about what you'd like to do?",
            "suggested_queries": [
                "I want to swap tokens",
                "What is yield farming?",
                "How do I provide liquidity?"
            ],
            "ai_system": "mock"
        }

def is_mock_mode() -> bool:
    """Check if we're in demo mode (controlled by USE_DEMO_MODE setting)"""
    from backend.config.settings import settings
    return settings.USE_DEMO_MODE

def get_current_mode() -> str:
    """Get current system mode"""
    return "DEMO" if is_mock_mode() else "PRODUCTION"

def get_mode_info() -> dict:
    """Get detailed mode information"""
    from backend.config.settings import settings
    
    if is_mock_mode():
        return {
            "mode": "DEMO",
            "description": "Using mock responses for reliable testing",
            "ai_system": "Mock AI",
            "external_apis": "Disabled",
            "cost": "Free",
            "reliability": "100%"
        }
    else:
        ai_system = "Gemini (Free)" if settings.USE_GEMINI else "GPT-5 (Paid)"
        return {
            "mode": "PRODUCTION", 
            "description": "Using real AI APIs and external services",
            "ai_system": ai_system,
            "external_apis": "Enabled",
            "cost": "Variable",
            "reliability": "Depends on external services"
        }
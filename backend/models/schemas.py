"""
Pydantic schemas for API requests and responses.
Defines data models for the DeFi AI Assistant API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from datetime import datetime


class IntentType(str, Enum):
    """Supported intent types for query classification."""
    GENERAL_QUERY = "general_query"
    ACTION_REQUEST = "action_request"
    CLARIFICATION = "clarification"


class DeFiAction(str, Enum):
    """Supported DeFi actions."""
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    SWAP = "swap"
    BORROW = "borrow"
    LEND = "lend"
    STAKE = "stake"
    UNSTAKE = "unstake"
    CLAIM_REWARDS = "claim_rewards"


class TokenSymbol(str, Enum):
    """Common DeFi token symbols."""
    ETH = "ETH"
    USDC = "USDC"
    USDT = "USDT"
    DAI = "DAI"
    WBTC = "WBTC"
    AAVE = "AAVE"
    UNI = "UNI"
    COMP = "COMP"


# Request Schemas
class UserQuery(BaseModel):
    """Schema for user query requests."""
    query: str = Field(..., min_length=1, max_length=1000, description="User's query text")
    session_id: Optional[str] = Field(None, description="Optional session ID for context")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()


class SessionRequest(BaseModel):
    """Schema for session management requests."""
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional session metadata")


# Response Schemas
class SessionResponse(BaseModel):
    """Schema for session creation response."""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation timestamp")


class ActionDetails(BaseModel):
    """Schema for extracted DeFi action details."""
    action: Optional[DeFiAction] = Field(None, description="Type of DeFi action")
    token_in: Optional[str] = Field(None, description="Input token symbol")
    token_out: Optional[str] = Field(None, description="Output token symbol")
    amount: Optional[Union[float, str]] = Field(None, description="Transaction amount")
    protocol: Optional[str] = Field(None, description="DeFi protocol name")
    pool_address: Optional[str] = Field(None, description="Liquidity pool address")
    slippage: Optional[float] = Field(None, ge=0, le=100, description="Slippage tolerance percentage")
    deadline: Optional[int] = Field(None, description="Transaction deadline in seconds")
    gas_price: Optional[str] = Field(None, description="Gas price in gwei")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            try:
                float_val = float(v)
                if float_val <= 0:
                    raise ValueError('Amount must be positive')
            except (ValueError, TypeError):
                raise ValueError('Amount must be a valid number')
        return v


class IntentClassificationResponse(BaseModel):
    """Schema for intent classification response."""
    intent: IntentType = Field(..., description="Classified intent type")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Classification confidence score")
    reasoning: Optional[str] = Field(None, description="Explanation of classification")


class GeneralQueryResponse(BaseModel):
    """Schema for general query response."""
    intent: IntentType = Field(default=IntentType.GENERAL_QUERY)
    answer: str = Field(..., description="AI-generated response")
    sources: Optional[List[str]] = Field(default_factory=list, description="Information sources used")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Response confidence score")
    session_id: Optional[str] = Field(None, description="Session identifier")


class ActionRequestResponse(BaseModel):
    """Schema for action request response."""
    intent: IntentType = Field(default=IntentType.ACTION_REQUEST)
    action_details: ActionDetails = Field(..., description="Extracted action parameters")
    next_step: str = Field(..., description="Next step in the action flow")
    confirmation_required: bool = Field(default=True, description="Whether user confirmation is needed")
    estimated_gas: Optional[str] = Field(None, description="Estimated gas cost")
    session_id: Optional[str] = Field(None, description="Session identifier")


class ClarificationResponse(BaseModel):
    """Schema for clarification response."""
    intent: IntentType = Field(default=IntentType.CLARIFICATION)
    clarification_question: str = Field(..., description="Question to clarify user intent")
    suggested_queries: Optional[List[str]] = Field(default_factory=list, description="Example queries")
    session_id: Optional[str] = Field(None, description="Session identifier")


class QueryResponse(BaseModel):
    """Unified schema for all query responses."""
    intent: IntentType = Field(..., description="Classified intent type")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # General query fields
    answer: Optional[str] = Field(None, description="AI-generated response")
    sources: Optional[List[str]] = Field(None, description="Information sources")
    
    # Action request fields
    action_details: Optional[ActionDetails] = Field(None, description="Extracted action parameters")
    next_step: Optional[str] = Field(None, description="Next step in action flow")
    confirmation_required: Optional[bool] = Field(None, description="Whether confirmation is needed")
    estimated_gas: Optional[str] = Field(None, description="Estimated gas cost")
    
    # Clarification fields
    clarification_question: Optional[str] = Field(None, description="Clarification question")
    suggested_queries: Optional[List[str]] = Field(None, description="Example queries")
    
    # Common fields
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Response confidence")
    intent_confidence: Optional[float] = Field(None, ge=0, le=1, description="Intent classification confidence")


# Error Schemas
class ErrorDetail(BaseModel):
    """Schema for error details."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error type")
    details: Optional[List[ErrorDetail]] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request identifier for debugging")


# Health Check Schema
class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(default="ok", description="Service status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(default="1.0.0", description="API version")


# Internal Chain Schemas
class VectorMatch(BaseModel):
    """Schema for vector database match results."""
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    
    
class QueryChainResult(BaseModel):
    """Schema for query chain processing results."""
    source: str = Field(..., description="Source of the answer (vector_db, llm_fallback, etc.)")
    confidence: float = Field(..., ge=0, le=1, description="Answer confidence score")
    answer: str = Field(..., description="Generated answer")
    top_matches: List[VectorMatch] = Field(default_factory=list, description="Top vector matches")
    sources: Optional[List[str]] = Field(default_factory=list, description="Source references")


class ConversationTurn(BaseModel):
    """Schema for a single conversation turn."""
    query: str = Field(..., description="User query")
    response: str = Field(..., description="Bot response")
    intent: IntentType = Field(..., description="Query intent")
    timestamp: float = Field(default_factory=lambda: __import__('time').time(), description="Turn timestamp")
    confidence: Optional[float] = Field(None, description="Response confidence")
    source: Optional[str] = Field(None, description="Response source (vector_db, llm_fallback, etc.)")


class SessionData(BaseModel):
    """Schema for user session data."""
    user_id: str = Field(..., description="User identifier")
    last_query: Optional[str] = Field(None, description="Last user query")
    last_updated: float = Field(default_factory=lambda: __import__('time').time(), description="Last update timestamp")
    conversation_history: List[ConversationTurn] = Field(default_factory=list, description="Conversation history")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session data")
    
    def add_turn(self, query: str, response: str, intent: IntentType, confidence: Optional[float] = None, source: Optional[str] = None):
        """Add a new conversation turn to history."""
        turn = ConversationTurn(
            query=query,
            response=response,
            intent=intent,
            confidence=confidence,
            source=source
        )
        self.conversation_history.append(turn)
        self.last_query = query
        self.last_updated = __import__('time').time()
        
        # Keep only last 10 turns to manage memory
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_smart_context(self, current_query: str) -> str:
        """Get intelligent context - only relevant previous exchanges."""
        if not self.conversation_history:
            return ""
        
        # Strategy 1: Only include context if current query seems like a follow-up
        follow_up_indicators = [
            "what about", "how about", "and", "also", "but", "however", 
            "what if", "can you", "tell me more", "explain", "clarify",
            "that", "this", "it", "they", "those", "these"
        ]
        
        current_lower = current_query.lower()
        is_followup = any(indicator in current_lower for indicator in follow_up_indicators)
        
        if not is_followup:
            return ""  # No context needed for standalone questions
        
        # Strategy 2: Only include the most recent exchange (not full history)
        if self.conversation_history:
            last_turn = self.conversation_history[-1]
            # Only include if recent (within 2 minutes)
            if (__import__('time').time() - last_turn.timestamp) < 120:
                return f"Previous: User asked '{last_turn.query}' and I answered '{last_turn.response[:100]}...'"
        
        return ""
    
    def needs_context(self, current_query: str) -> bool:
        """Determine if current query needs conversation context."""
        if not self.conversation_history:
            return False
            
        # Check for follow-up patterns
        follow_up_patterns = [
            r'\b(what about|how about|and what|but what|however)\b',
            r'\b(that|this|it|they|those|these)\b',
            r'\b(tell me more|explain|clarify|elaborate)\b',
            r'\b(can you|could you|would you)\b.*\b(also|too|as well)\b'
        ]
        
        import re
        current_lower = current_query.lower()
        return any(re.search(pattern, current_lower) for pattern in follow_up_patterns)


class IntentClassificationResult(BaseModel):
    """Schema for intent classification results."""
    intent: IntentType = Field(..., description="Classified intent")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Classification confidence")
    raw_output: Optional[str] = Field(None, description="Raw LLM output for debugging")


class ActionExtractionResult(BaseModel):
    """Schema for action extraction results."""
    action: Optional[DeFiAction] = Field(None, description="Extracted DeFi action")
    amount: Optional[Union[float, str]] = Field(None, description="Transaction amount")
    asset: Optional[str] = Field(None, description="Asset/token symbol")
    protocol: Optional[str] = Field(None, description="DeFi protocol")
    chain: Optional[str] = Field(None, description="Blockchain network")
    apy_min: Optional[float] = Field(None, description="Minimum APY requirement")
    apy_max: Optional[float] = Field(None, description="Maximum APY requirement")
    slippage: Optional[float] = Field(None, ge=0, le=100, description="Slippage tolerance")
    notes: Optional[str] = Field(None, description="Additional notes")
    recipient: Optional[str] = Field(None, description="Recipient address")
    duration: Optional[int] = Field(None, description="Duration in seconds")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v is not None:
            try:
                float_val = float(v)
                if float_val <= 0:
                    raise ValueError('Amount must be positive')
            except (ValueError, TypeError):
                raise ValueError('Amount must be a valid number')
        return v


# Configuration Schemas
class ModelConfig(BaseModel):
    """Schema for AI model configuration."""
    model_name: str = Field(..., description="Model identifier")
    temperature: float = Field(default=0.0, ge=0, le=2, description="Model temperature")
    max_tokens: Optional[int] = Field(None, gt=0, description="Maximum tokens in response")
    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")

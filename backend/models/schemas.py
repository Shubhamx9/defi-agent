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
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: Optional[str] = Field(None, description="Auto-generated session ID (optional for new sessions)")
    new_chat: Optional[bool] = Field(False, description="Set to true to force new session creation")
    
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
    
    def get_completion_status(self) -> Dict[str, Any]:
        """Analyze transaction readiness and return completion status."""
        required_fields = self._get_required_fields()
        optional_fields = self._get_optional_fields()
        
        missing_required = []
        missing_optional = []
        
        # Check required fields
        for field in required_fields:
            if getattr(self, field) is None:
                missing_required.append(field)
        
        # Check optional fields
        for field in optional_fields:
            if getattr(self, field) is None:
                missing_optional.append(field)
        
        is_ready = len(missing_required) == 0
        completion_percentage = self._calculate_completion_percentage()
        
        return {
            "is_ready_for_execution": is_ready,
            "completion_percentage": completion_percentage,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "next_questions": self._generate_next_questions(missing_required),
            "confirmation_message": self._generate_confirmation_message() if is_ready else None,
            "risk_warnings": self._get_risk_warnings(),
            "estimated_gas": self._estimate_gas_cost()
        }
    
    def _get_required_fields(self) -> List[str]:
        """Get required fields based on action type."""
        if not self.action:
            return ["action"]
        
        base_required = ["action", "amount"]
        
        action_requirements = {
            DeFiAction.SWAP: ["token_in", "token_out", "protocol"],
            DeFiAction.DEPOSIT: ["token_in", "protocol"],
            DeFiAction.WITHDRAW: ["token_in", "protocol"],
            DeFiAction.STAKE: ["token_in", "protocol"],
            DeFiAction.UNSTAKE: ["token_in", "protocol"],
            DeFiAction.BORROW: ["token_out", "protocol"],
            DeFiAction.LEND: ["token_in", "protocol"],
            DeFiAction.CLAIM_REWARDS: ["protocol"]
        }
        
        specific_requirements = action_requirements.get(self.action, [])
        return base_required + specific_requirements
    
    def _get_optional_fields(self) -> List[str]:
        """Get optional fields that improve transaction quality."""
        return ["slippage", "deadline", "gas_price"]
    
    def _calculate_completion_percentage(self) -> int:
        """Calculate completion percentage based on filled fields."""
        required_fields = self._get_required_fields()
        optional_fields = self._get_optional_fields()
        
        total_fields = len(required_fields) + len(optional_fields)
        filled_fields = 0
        
        for field in required_fields + optional_fields:
            if getattr(self, field) is not None:
                filled_fields += 1
        
        return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
    
    def _generate_next_questions(self, missing_required: List[str]) -> List[str]:
        """Generate user-friendly questions for missing information."""
        questions = []
        
        question_map = {
            "action": "What DeFi action would you like to perform? (swap, deposit, stake, etc.)",
            "amount": "How much would you like to transact?",
            "token_in": "Which token would you like to use?",
            "token_out": "Which token would you like to receive?",
            "protocol": "Which DeFi protocol would you prefer? (Uniswap, Aave, Compound, etc.)",
            "slippage": "What slippage tolerance would you like? (default: 0.5%)",
            "deadline": "Transaction deadline in minutes? (default: 20 minutes)"
        }
        
        for field in missing_required:
            if field in question_map:
                questions.append(question_map[field])
        
        return questions
    
    def _generate_confirmation_message(self) -> str:
        """Generate confirmation message for ready transactions."""
        if not self.action:
            return "Transaction details incomplete"
        
        action_messages = {
            DeFiAction.SWAP: f"Swap {self.amount} {self.token_in} for {self.token_out} on {self.protocol}",
            DeFiAction.DEPOSIT: f"Deposit {self.amount} {self.token_in} to {self.protocol}",
            DeFiAction.WITHDRAW: f"Withdraw {self.amount} {self.token_in} from {self.protocol}",
            DeFiAction.STAKE: f"Stake {self.amount} {self.token_in} on {self.protocol}",
            DeFiAction.UNSTAKE: f"Unstake {self.amount} {self.token_in} from {self.protocol}",
            DeFiAction.BORROW: f"Borrow {self.amount} {self.token_out} from {self.protocol}",
            DeFiAction.LEND: f"Lend {self.amount} {self.token_in} to {self.protocol}",
            DeFiAction.CLAIM_REWARDS: f"Claim rewards from {self.protocol}"
        }
        
        base_message = action_messages.get(self.action, f"Execute {self.action} transaction")
        
        # Add optional parameters
        extras = []
        if self.slippage:
            extras.append(f"slippage: {self.slippage}%")
        if self.deadline:
            extras.append(f"deadline: {self.deadline}s")
        
        if extras:
            base_message += f" ({', '.join(extras)})"
        
        return base_message
    
    def _get_risk_warnings(self) -> List[str]:
        """Generate risk warnings based on transaction details."""
        warnings = []
        
        if self.action == DeFiAction.SWAP and self.slippage and self.slippage > 5:
            warnings.append("High slippage tolerance may result in significant price impact")
        
        if self.amount:
            try:
                amount_val = float(self.amount)
                if amount_val > 10000:  # Large transaction
                    warnings.append("Large transaction amount - consider splitting into smaller trades")
            except (ValueError, TypeError):
                pass
        
        if not self.slippage and self.action == DeFiAction.SWAP:
            warnings.append("No slippage tolerance set - transaction may fail in volatile markets")
        
        return warnings
    
    def _estimate_gas_cost(self) -> str:
        """Estimate gas cost based on action type."""
        gas_estimates = {
            DeFiAction.SWAP: "~150,000 gas (~$15-30)",
            DeFiAction.DEPOSIT: "~200,000 gas (~$20-40)",
            DeFiAction.WITHDRAW: "~180,000 gas (~$18-35)",
            DeFiAction.STAKE: "~250,000 gas (~$25-50)",
            DeFiAction.UNSTAKE: "~200,000 gas (~$20-40)",
            DeFiAction.BORROW: "~300,000 gas (~$30-60)",
            DeFiAction.LEND: "~250,000 gas (~$25-50)",
            DeFiAction.CLAIM_REWARDS: "~100,000 gas (~$10-20)"
        }
        
        return gas_estimates.get(self.action, "~200,000 gas (~$20-40)")


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


class TransactionReadiness(BaseModel):
    """Schema for transaction readiness analysis."""
    is_ready_for_execution: bool = Field(..., description="Whether transaction is ready to execute")
    completion_percentage: int = Field(..., ge=0, le=100, description="Completion percentage")
    readiness_level: str = Field(..., description="Readiness level for frontend")
    missing_required: List[str] = Field(default_factory=list, description="Missing required fields")
    next_questions: List[str] = Field(default_factory=list, description="Questions to ask user")
    next_question_details: Optional[Dict[str, Any]] = Field(None, description="Detailed next question with suggestions")
    user_guidance: Dict[str, Any] = Field(default_factory=dict, description="User guidance")
    frontend_actions: Dict[str, Any] = Field(default_factory=dict, description="Frontend UI actions")
    risk_warnings: List[str] = Field(default_factory=list, description="Risk warnings")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")

class ActionRequestResponse(BaseModel):
    """Schema for action request response."""
    intent: IntentType = Field(default=IntentType.ACTION_REQUEST)
    action_details: ActionDetails = Field(..., description="Extracted action parameters")
    transaction_readiness: TransactionReadiness = Field(..., description="Transaction readiness analysis")
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
    transaction_readiness: Optional[TransactionReadiness] = Field(None, description="Transaction readiness analysis")
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


# Detailed Health Check Schema
class HealthResponse(BaseModel):
    status: str
    timestamp: float
    services: Dict[str, Dict[str, Any]]
    response_time_ms: float
    demo_mode: bool | None = None
    note: str | None = None
    mode: str | None = None



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
    session_id: Optional[str] = Field(None, description="Session identifier")


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


class LoginRequest(BaseModel):
    username: str
    password: str
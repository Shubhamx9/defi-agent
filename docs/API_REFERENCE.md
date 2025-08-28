# API Reference 📚

Complete API documentation for the DeFi AI Assistant backend system.

## Base URL
```
Development: http://localhost:8000
Production: https://your-domain.com/api
```

## Authentication
Currently using session-based authentication. JWT/OAuth2 integration planned for production.

## Core Endpoints

### Session Management

#### Start Session
Creates a new user session with secure UUID generation.

```http
POST /query/start-session
Content-Type: application/json

{
  "user_id": "optional_user_identifier",
  "metadata": {
    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96590b5b8c",
    "preferred_protocols": ["uniswap", "aave", "compound"],
    "risk_tolerance": "medium"
  }
}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "expires_at": "2024-01-01T12:05:00Z",
  "status": "active",
  "user_id": "optional_user_identifier"
}
```

#### Get Session Details
```http
GET /query/session/{session_id}
```

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "created_at": "2024-01-01T12:00:00Z",
  "expires_at": "2024-01-01T12:05:00Z",
  "status": "active",
  "conversation_history": [
    {
      "query": "What is yield farming?",
      "response": "Yield farming is...",
      "timestamp": "2024-01-01T12:01:00Z"
    }
  ],
  "transaction_state": {
    "current_action": null,
    "accumulated_params": {},
    "readiness_percentage": 0
  }
}
```

#### End Session
```http
DELETE /query/session/{session_id}
```

**Response:**
```json
{
  "message": "Session ended successfully",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Query Processing

#### Process Query
Main endpoint for handling user queries and DeFi actions.

```http
POST /query/
Content-Type: application/json

{
  "query": "I want to provide liquidity to the ETH/USDC pool on Uniswap",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response Types:**

#### General Query Response
```json
{
  "intent": "general_query",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": "Providing liquidity to Uniswap involves depositing equal values of two tokens into a liquidity pool...",
  "sources": [
    "Uniswap V3 Documentation",
    "DeFi Pulse Liquidity Guide"
  ],
  "confidence": 0.95,
  "ai_system": "gpt-5",
  "cost_analysis": {
    "tokens_used": 245,
    "estimated_cost": 0.0612,
    "model_used": "gpt-5-mini"
  },
  "follow_up_suggestions": [
    "Would you like to know about impermanent loss?",
    "What's the current APY for ETH/USDC pools?"
  ]
}
```

#### Action Request Response (Incomplete)
```json
{
  "intent": "action_request",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "action_details": {
    "action": "provide_liquidity",
    "protocol": "uniswap",
    "token_a": "ETH",
    "token_b": "USDC",
    "readiness_percentage": 40
  },
  "missing_parameters": [
    "amount_token_a",
    "amount_token_b",
    "fee_tier",
    "price_range"
  ],
  "suggested_questions": [
    "How much ETH would you like to provide?",
    "How much USDC would you like to provide?",
    "Which fee tier would you prefer? (0.05%, 0.3%, 1%)",
    "What price range would you like to provide liquidity for?"
  ],
  "transaction_state": {
    "accumulated_params": {
      "action": "provide_liquidity",
      "protocol": "uniswap",
      "token_a": "ETH",
      "token_b": "USDC"
    },
    "completion_status": "gathering_parameters"
  },
  "next_step": "gather_missing_parameters",
  "transaction_ready": false
}
```

#### Action Request Response (Complete)
```json
{
  "intent": "action_request",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "action_details": {
    "action": "provide_liquidity",
    "protocol": "uniswap",
    "token_a": "ETH",
    "token_b": "USDC",
    "amount_token_a": 1.0,
    "amount_token_b": 3000,
    "fee_tier": 0.3,
    "price_range": {
      "min": 2800,
      "max": 3200
    },
    "readiness_percentage": 100
  },
  "transaction_ready": true,
  "estimated_gas": "150000",
  "estimated_fees": {
    "gas_fee": "0.005 ETH",
    "protocol_fee": "0.3%"
  },
  "confirmation_required": true,
  "next_step": "execute_transaction",
  "blockchain_params": {
    "contract_address": "0x...",
    "function_name": "mint",
    "parameters": {
      "token0": "0x...",
      "token1": "0x...",
      "fee": 3000,
      "tickLower": -887220,
      "tickUpper": 887220,
      "amount0Desired": "1000000000000000000",
      "amount1Desired": "3000000000",
      "amount0Min": "950000000000000000",
      "amount1Min": "2850000000",
      "recipient": "0x...",
      "deadline": 1704110700
    }
  }
}
```

#### Clarification Response
```json
{
  "intent": "clarification",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "clarification": "I understand you're interested in DeFi. Could you be more specific about what you'd like to do?",
  "suggested_queries": [
    "I want to swap tokens",
    "I want to provide liquidity",
    "I want to borrow against my assets",
    "What is yield farming?"
  ],
  "ai_system": "gpt-5",
  "cost_analysis": {
    "tokens_used": 89,
    "estimated_cost": 0.0
  }
}
```

### Health & Monitoring

#### Basic Health Check
```http
GET /health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

#### Detailed Health Check
```http
GET /health/detailed
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "redis": {
      "status": "healthy",
      "response_time_ms": 2.3,
      "connection_pool": "active"
    },
    "pinecone": {
      "status": "healthy",
      "response_time_ms": 45.2,
      "index_stats": {
        "total_vectors": 15420,
        "dimension": 384
      }
    },
    "embedding_model": {
      "status": "healthy",
      "model": "sentence-transformers/all-MiniLM-L6-v2",
      "load_time_ms": 1250
    }
  },
  "ai_system": {
    "active_system": "gpt-5",
    "models": {
      "intent": "gpt-5-nano",
      "query": "gpt-5-mini",
      "action": "gpt-5-mini"
    },
    "cost_analysis": {
      "total_requests_today": 1247,
      "total_cost_today": 0.0,
      "average_tokens_per_request": 156
    }
  },
  "performance": {
    "average_response_time_ms": 234,
    "requests_per_minute": 45,
    "cache_hit_rate": 0.78
  }
}
```

#### AI System Information
```http
GET /health/models
```

**Response:**
```json
{
  "active_system": "gpt-5",
  "system_config": {
    "use_gpt": true,
    "models": {
      "intent_model": "gpt-5-nano",
      "query_model": "gpt-5-mini",
      "action_model": "gpt-5-mini"
    }
  },
  "cost_info": {
    "system_type": "paid",
    "pricing": {
      "gpt-5-nano": "$0.001 per 1K tokens",
      "gpt-5-mini": "$0.003 per 1K tokens",
      "gpt-5": "$0.01 per 1K tokens"
    },
    "current_usage": {
      "tokens_today": 15420,
      "estimated_cost_today": "$0.47"
    }
  },
  "fallback_available": true
}
```

#### Application Probes
```http
GET /health/ready    # Application readiness probe
GET /health/live     # Application liveness probe
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Query length exceeds maximum allowed (1000 characters)",
    "details": {
      "field": "query",
      "provided_length": 1250,
      "max_length": 1000
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input parameters |
| `SESSION_NOT_FOUND` | 404 | Session ID not found or expired |
| `SESSION_EXPIRED` | 401 | Session has expired |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `AI_SERVICE_ERROR` | 503 | AI service temporarily unavailable |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## Rate Limits

| Endpoint | Rate Limit | Burst Limit |
|----------|------------|-------------|
| `/query/start-session` | 10/minute | 20 |
| `/query/` | 60/minute | 100 |
| `/health/*` | 120/minute | 200 |

## WebSocket Support (Planned)

### Real-time Query Processing
```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/{session_id}');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'query_progress') {
    // Handle query processing updates
  } else if (data.type === 'transaction_update') {
    // Handle transaction state changes
  }
};
```

## SDK Examples

### JavaScript/TypeScript
```typescript
class DeFiAIClient {
  private baseUrl: string;
  private sessionId?: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async startSession(userId?: string, metadata?: any): Promise<string> {
    const response = await fetch(`${this.baseUrl}/query/start-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, metadata })
    });
    const data = await response.json();
    this.sessionId = data.session_id;
    return this.sessionId;
  }

  async query(query: string): Promise<any> {
    if (!this.sessionId) throw new Error('No active session');
    
    const response = await fetch(`${this.baseUrl}/query/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: this.sessionId })
    });
    return response.json();
  }
}
```

### Python
```python
import requests
from typing import Optional, Dict, Any

class DeFiAIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    def start_session(self, user_id: Optional[str] = None, 
                     metadata: Optional[Dict] = None) -> str:
        response = requests.post(
            f"{self.base_url}/query/start-session",
            json={"user_id": user_id, "metadata": metadata or {}}
        )
        data = response.json()
        self.session_id = data["session_id"]
        return self.session_id
    
    def query(self, query: str) -> Dict[str, Any]:
        if not self.session_id:
            raise ValueError("No active session")
        
        response = requests.post(
            f"{self.base_url}/query/",
            json={"query": query, "session_id": self.session_id}
        )
        return response.json()
```

## Testing

### Health Check Test
```bash
curl -X GET http://localhost:8000/health/detailed
```

### Session Flow Test
```bash
# 1. Start session
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/query/start-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}')

SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.session_id')

# 2. Send query
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is DeFi?\", \"session_id\": \"$SESSION_ID\"}"

# 3. Send action request
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"I want to swap 100 USDC for ETH\", \"session_id\": \"$SESSION_ID\"}"
```

---

**For more examples and integration guides, see [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md)**
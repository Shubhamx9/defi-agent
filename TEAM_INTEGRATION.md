# Team Integration Guide 🤝

Quick setup guide for frontend and blockchain teams to integrate with the DeFi AI Assistant backend.

## 🚀 Quick Start (5 minutes)

### 1. Start the Backend
```bash
# In the backend directory
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test Integration
```bash
# Run integration tests
python integration_test.py
```

### 3. Check Health
```bash
curl http://localhost:8000/health/detailed
```

## 🔗 Frontend Integration

### API Base URL
```
Development: http://localhost:8000
```

### CORS Configuration
Already configured for:
- `http://localhost:3000` (React/Next.js)
- `http://localhost:8080` (Vue/Angular)
- `http://localhost:8501` (Streamlit)

### Key Endpoints

#### Start Session
```javascript
const response = await fetch('http://localhost:8000/query/start-session', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user123',
    metadata: {
      wallet_address: '0x...',
      preferred_protocols: ['uniswap', 'aave']
    }
  })
});

const { session_id } = await response.json();
```

#### Send Query
```javascript
const response = await fetch('http://localhost:8000/query/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'I want to swap 100 USDC for ETH',
    session_id: session_id
  })
});

const result = await response.json();
```

### Response Types

#### General Query
```typescript
interface GeneralQueryResponse {
  intent: 'general_query';
  session_id: string;
  answer: string;
  sources: string[];
  confidence: number;
  ai_system: 'gemini' | 'gpt-5';
}
```

#### Action Request (Incomplete)
```typescript
interface ActionRequestResponse {
  intent: 'action_request';
  session_id: string;
  action_details: {
    action: string;
    readiness_percentage: number;
    [key: string]: any;
  };
  missing_parameters: string[];
  suggested_questions: string[];
  transaction_ready: false;
}
```

#### Action Request (Complete)
```typescript
interface TransactionReadyResponse {
  intent: 'action_request';
  session_id: string;
  action_details: {
    action: string;
    readiness_percentage: 100;
    [key: string]: any;
  };
  transaction_ready: true;
  estimated_gas: string;
  next_step: 'execute_transaction';
}
```

## ⛓️ Blockchain Integration

### Transaction Ready Detection
```python
# When transaction_ready is True, all parameters are collected
if response['transaction_ready']:
    params = response['action_details']
    # Execute blockchain transaction with params
    tx_hash = execute_transaction(params)
```

### Parameter Format
```json
{
  "action": "swap",
  "amount": 100,
  "token_in": "USDC",
  "token_out": "ETH", 
  "protocol": "Uniswap",
  "slippage_tolerance": 0.5,
  "deadline": 600,
  "readiness_percentage": 100
}
```

## 🧪 Testing Your Integration

### 1. Health Check
```bash
curl http://localhost:8000/health/detailed
```

### 2. Session Flow Test
```bash
# Start session
SESSION_ID=$(curl -s -X POST http://localhost:8000/query/start-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test"}' | jq -r '.session_id')

# Send query
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is DeFi?\", \"session_id\": \"$SESSION_ID\"}"
```

### 3. Action Request Test
```bash
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"I want to swap 100 USDC for ETH\", \"session_id\": \"$SESSION_ID\"}"
```

## 🚨 Error Handling

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Query length exceeds maximum allowed",
    "details": {},
    "request_id": "req_123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` (400): Invalid input
- `SESSION_NOT_FOUND` (404): Session expired/invalid
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `AI_SERVICE_ERROR` (503): AI service unavailable

## 📊 Monitoring

### Health Endpoints
- `GET /health/` - Basic health
- `GET /health/detailed` - Full system status
- `GET /health/models` - AI system info
- `GET /health/ready` - Kubernetes readiness
- `GET /health/live` - Kubernetes liveness

### Performance Expectations
- Health checks: <50ms
- Vector search queries: <200ms
- AI processing: 1-3 seconds
- Session operations: <100ms

## 🔧 Configuration

### Environment Variables
```bash
# System Mode Selection
USE_DEMO_MODE=true   # true = Demo Mode, false = Production Mode

# AI System Selection (Production Mode only)
USE_GEMINI=true      # true = Free Gemini, false = Paid GPT-5

# CORS Origins (add your frontend URL)
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Mode Switching
```bash
# For reliable demo/testing (Recommended for development)
USE_DEMO_MODE=true

# For production with real APIs
USE_DEMO_MODE=false
```

## 🎯 Demo Preparation

### Key Features to Showcase
1. **Dual AI System**: Switch between Gemini (free) and GPT-5 (paid)
2. **Transaction Intelligence**: Parameter accumulation and readiness tracking
3. **Cost Optimization**: 65% cost reduction through smart routing

### Demo Flow
1. Start session
2. Ask general DeFi question (shows vector search)
3. Request transaction (shows parameter extraction)
4. Follow up with missing details (shows intelligent questioning)
5. Show transaction ready state (shows blockchain integration point)

## 📞 Support

### Backend Team Contact
- **Email**: aayushkr646@gmail.com
- **GitHub**: https://github.com/Aayush2005/defi-agent

### Quick Debug Commands
```bash
# Check if backend is running
curl http://localhost:8000/health/

# Check AI system status
curl http://localhost:8000/health/models

# Test session creation
curl -X POST http://localhost:8000/query/start-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "debug"}'
```

### Integration Checklist
- [ ] Backend running on port 8000
- [ ] Health endpoints responding
- [ ] CORS configured for your frontend URL
- [ ] Session creation working
- [ ] Query processing working
- [ ] Error handling tested
- [ ] Transaction ready detection implemented

---

**Ready to integrate! 🚀**

Your backend is production-ready and waiting for frontend/blockchain integration. All APIs are documented and tested.
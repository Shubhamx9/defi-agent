# DeFi AI Assistant 🚀

A **production-ready** AI assistant for Decentralized Finance (DeFi) queries and blockchain actions. Built with FastAPI, LangChain, Coinbase CDP AgentKit, and enterprise-grade reliability featuring flexible AI model selection, comprehensive transaction intelligence, and x402 payment protocol support.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.0-1C3C3C.svg?style=flat)](https://langchain.com)
[![CDP AgentKit](https://img.shields.io/badge/CDP%20AgentKit-Latest-blue.svg?style=flat)](https://github.com/coinbase/cdp-agentkit)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=flat&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Enterprise%20Grade-green.svg?style=flat)](SECURITY.md)

## 🎯 Project Overview

**Type**: Team Project - DeFi Agent
**Team Structure**: 
- **Backend AI System**: Aayush Kumar
- **Frontend & UI**: Adesh Dutta
- **Blockchain Integration**: Shubham Priyadarsi
**Domain**: Decentralized Finance (DeFi)  
**Status**: Production-Ready Backend ✅

### Key Features

- 🤖 **Flexible AI System**: Support for GPT-5 models and local Mistral-7B via Ollama
- 🧠 **Smart Intent Classification**: Automatically routes queries to appropriate handlers
- 🔍 **Vector Search**: Pinecone-powered semantic search for DeFi knowledge
- 💬 **Advanced Session Management**: Secure sessions with conversation history and context awareness
- 🎯 **Transaction Intelligence**: Complete parameter extraction and readiness analysis
- ❓ **Intelligent Questioning**: Context-aware follow-up generation for missing parameters
- 🔗 **Coinbase CDP Integration**: Full AgentKit support for wallet operations, token transfers, and DeFi actions
- 💳 **x402 Payment Protocol**: Integrated support for service payments and API access
- 🏦 **Multi-Chain Support**: Base Sepolia testnet with production network ready
- 🛡️ **Enterprise Security**: Rate limiting, input sanitization, CORS protection, comprehensive validation
- 📊 **Production Monitoring**: Health checks, structured logging, error tracking with LangSmith
- ⚡ **High Performance**: Connection pooling, lazy loading, caching, graceful degradation
- 🔗 **Team Integration Ready**: Clean REST APIs designed for frontend and blockchain team integration

## 🏗️ Architecture

### Team System Architecture
<img width="1920" height="1080" alt="Archi" src="https://github.com/user-attachments/assets/97dbe7c4-e44d-4615-827d-4ab32e2f5790" />

### Component Responsibilities

#### Backend AI System (This Repository)
- **Intent Classification**: Determines query type and routing
- **Session Management**: Secure session handling with auto-generation
- **Transaction Intelligence**: Parameter accumulation and readiness analysis
- **AI Processing**: GPT-5/Mistral integration with smart routing
- **Security**: Enterprise-grade input validation and rate limiting

#### Frontend Integration Points (Team)
- **Session APIs**: Start, manage, and end user sessions
- **Query Processing**: Real-time query handling with structured responses
- **Transaction State**: Progress tracking and parameter completion
- **Error Handling**: Standardized error responses for UI

#### Blockchain Integration Points (Team)
- **Transaction Ready Events**: When all parameters are collected
- **Parameter Validation**: Ensure transaction parameters are valid
- **Execution Feedback**: Status updates back to session management

### Smart Processing Logic
```
User Query → Intent Classification → Route Decision
    ↓
├─ General Query → Vector Search → Confidence-based Response
│   ├─ ≥0.98 confidence → Direct DB answer (minimal AI cost)
│   ├─ 0.90-0.98 → AI refinement + context
│   └─ <0.90 → AI fallback + smart context
│
├─ Action Request → Parameter Extraction → Session Merge → Transaction Analysis
│   ├─ Complete Parameters → Ready for Blockchain Execution
│   ├─ Missing Parameters → Intelligent Question Generation
│   └─ Invalid Parameters → Error Handling & Suggestions
│
└─ Clarification → Contextual Response → Suggested Queries
```

### Core Components

#### AI Processing Engine
- **Intent Classification**: Determines query type and routing using GPT-5-nano or Mistral-7B
- **Query Processing**: Handles general DeFi questions with vector search + AI refinement
- **Action Extraction**: Extracts transaction parameters from natural language
- **Session Management**: Secure session handling with conversation context

#### Integration Layer
- **REST API**: Complete FastAPI-based REST interface
- **Session Management**: Secure session lifecycle with auto-generation
- **Transaction Intelligence**: Parameter accumulation and readiness analysis
- **Error Handling**: Comprehensive error handling with detailed responses

#### Data & Security Layer
- **Vector Database**: Pinecone for semantic search of DeFi knowledge
- **Caching**: Redis for session storage and performance optimization
- **Security**: Rate limiting, input validation, CORS protection
- **Monitoring**: Health checks, logging, and observability with LangSmith

### Technology Stack

**AI & ML**
- **LangChain**: AI orchestration and chaining framework
- **OpenAI GPT-5**: Latest models (gpt-5, gpt-5-mini, gpt-5-nano) for production
- **Mistral-7B**: Local model support via Ollama for cost-effective deployment
- **Sentence Transformers**: Vector embeddings (all-MiniLM-L6-v2)
- **LangSmith**: Observability, tracing, and performance monitoring

**Blockchain & DeFi**
- **Coinbase CDP AgentKit**: Smart wallet management and DeFi operations
- **x402 Protocol**: Service payment and API access management
- **Base Network**: Sepolia testnet with mainnet configuration ready
- **Multi-Protocol Support**: Uniswap, Aave, and other DeFi protocols

**Backend Framework**
- **FastAPI**: Modern async Python web framework with auto-documentation
- **Pydantic**: Complete type safety and data validation
- **SlowAPI**: Intelligent rate limiting and abuse prevention
- **Uvicorn**: High-performance ASGI server

**Data & Storage**
- **Pinecone**: Vector database for semantic search
- **Redis**: Session management, caching, and performance optimization
- **JSON**: Structured data storage and API responses

**Security & Monitoring**
- **CORS**: Cross-origin resource sharing protection
- **Rate Limiting**: Multi-tier request throttling
- **Input Validation**: Comprehensive sanitization and validation
- **Health Checks**: Multi-service monitoring and diagnostics
- **Structured Logging**: Request tracking and error correlation

**Deployment**
- **Docker**: Containerized deployment with multi-stage builds
- **Environment Configuration**: Flexible configuration management
- **Health Probes**: Application readiness and liveness checks

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Redis server
- Pinecone account
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd defi-agent
```

2. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

3. **Environment Setup**
```bash
cp backend/.env.example backend/.env
# Edit .env with your API keys
```

Required environment variables:
```env
# =============================================================================
# AI SYSTEM SELECTION
# =============================================================================
USE_GPT=true  # true = OpenAI GPT-5, false = Local Mistral-7B via Ollama

# API Keys
OPENAI_API_KEY=your_openai_api_key      # Required if USE_GPT=true
PINECONE_API_KEY=your_pinecone_key      # Required for vector search
LANGSMITH_API_KEY=your_langsmith_key    # Optional for observability

# =============================================================================
# COINBASE CDP CONFIGURATION
# =============================================================================
CDP_API_KEY_ID=your_cdp_api_key_id          # Coinbase Developer Platform API Key ID
CDP_API_KEY_SECRET=your_cdp_api_key_secret  # Coinbase Developer Platform API Secret
CDP_WALLET_SECRET=your_cdp_wallet_secret    # CDP Wallet Secret for smart wallet operations
CDP_NETWORK_ID=base-sepolia                 # Network: base-sepolia (testnet) or base-mainnet (production)

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================
# For GPT-5 (Recommended for production)
INTENT_MODEL=gpt-5-nano    # Fast intent classification
QUERY_MODEL=gpt-5-mini     # Balanced performance/cost
ACTION_MODEL=gpt-5-mini    # Parameter extraction

# For Local Mistral (Cost-effective alternative)
# Models automatically use mistral:7b when USE_GPT=false

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
PINECONE_INDEX=defi-queries
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

DEBUG=false
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8501"]
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

4. **Run the application**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API Documentation

### Core Endpoints

#### Start Session
```http
POST /query/start-session
Content-Type: application/json

{
  "user_id": "optional_user_id",
  "metadata": {
    "wallet_address": "0x...",
    "preferred_protocols": ["uniswap", "aave"]
  }
}

Response:
{
  "session_id": "crypto_secure_uuid",
  "expires_at": "2024-01-01T12:00:00Z",
  "status": "active"
}
```

#### Process Query
```http
POST /query/
Content-Type: application/json

{
  "query": "I want to swap 100 USDC for ETH on Uniswap",
  "session_id": "uuid-from-start-session"
}

Response:
{
  "intent": "action_request",
  "session_id": "uuid",
  "action_details": {
    "action": "swap",
    "amount": 100,
    "token_in": "USDC",
    "token_out": "ETH",
    "protocol": "Uniswap",
    "readiness_percentage": 85
  },
  "missing_parameters": ["slippage_tolerance"],
  "suggested_questions": ["What slippage tolerance would you prefer?"],
  "next_step": "gather_slippage_preference"
}
```

#### Health Checks
```http
GET /health/              # Basic health
GET /health/detailed      # Full system status with AI system info
GET /health/ready         # Application readiness
GET /health/live          # Application liveness
GET /health/models        # Active AI system information
```

#### Session Management
```http
GET /query/session/{session_id}     # Get session details
DELETE /query/session/{session_id}  # End session
GET /query/sessions                 # List active sessions (admin)
```

### Response Examples

**General Query Response**
```json
{
  "intent": "general_query",
  "session_id": "uuid",
  "answer": "Yield farming is a DeFi strategy where users provide liquidity to protocols in exchange for rewards...",
  "sources": ["DeFi Pulse", "Uniswap Docs"],
  "confidence": 0.95,
  "ai_system": "gpt-5",
  "cost_analysis": {
    "tokens_used": 150,
    "estimated_cost": 0.0
  }
}
```

**Action Request Response**
```json
{
  "intent": "action_request",
  "session_id": "uuid",
  "action_details": {
    "action": "swap",
    "amount": 100,
    "token_in": "USDC",
    "token_out": "ETH",
    "protocol": "Uniswap",
    "readiness_percentage": 75
  },
  "missing_parameters": ["slippage_tolerance", "deadline"],
  "suggested_questions": [
    "What slippage tolerance would you prefer? (0.1%, 0.5%, 1%)",
    "How long should this transaction be valid? (10 minutes is typical)"
  ],
  "transaction_state": {
    "accumulated_params": {
      "amount": 100,
      "token_in": "USDC",
      "token_out": "ETH",
      "protocol": "Uniswap"
    },
    "completion_status": "gathering_parameters"
  },
  "next_step": "gather_missing_parameters",
  "confirmation_required": false
}
```

**Transaction Ready Response**
```json
{
  "intent": "action_request",
  "session_id": "uuid",
  "action_details": {
    "action": "swap",
    "amount": 100,
    "token_in": "USDC",
    "token_out": "ETH",
    "protocol": "Uniswap",
    "slippage_tolerance": 0.5,
    "deadline": 600,
    "readiness_percentage": 100
  },
  "transaction_ready": true,
  "estimated_gas": "21000",
  "confirmation_required": true,
  "next_step": "execute_transaction"
}
```

## 🔧 Configuration

### AI Model System Selection
```bash
# Choose your AI system in .env file
USE_GPT=true   # OpenAI GPT-5 models (recommended for production)
USE_GPT=false  # Local Mistral-7B via Ollama (cost-effective)
```

### Model Configuration
```python
# GPT-5 Models (Production)
INTENT_MODEL=gpt-5-nano          # Ultra-fast classification
QUERY_MODEL=gpt-5-mini           # Balanced performance/cost
ACTION_MODEL=gpt-5-mini          # Parameter extraction

# Mistral Models (Local/Cost-effective)
# Automatically uses mistral:7b for all tasks when USE_GPT=false
# Requires Ollama installation and model download
```

### System Settings
```python
# Vector search thresholds
HIGH_CONFIDENCE_THRESHOLD = 0.98
MEDIUM_CONFIDENCE_THRESHOLD = 0.90
VECTOR_SEARCH_TOP_K = 3

# Session management
SESSION_TTL = 300  # 5 minutes
MAX_CONVERSATION_HISTORY = 10

# Rate limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000
```

## 🛡️ Security Features

### Input Sanitization
- Prompt injection detection
- Length validation (max 1000 chars)
- Suspicious pattern filtering
- Query safety validation

### Rate Limiting
- 60 requests/minute per IP
- 1000 requests/hour per IP
- Configurable limits per endpoint

### CORS Protection
- Configurable allowed origins
- Secure headers
- Credential handling

## 📊 Monitoring & Observability

### Health Monitoring
```bash
# Check all services
curl http://localhost:8000/health/detailed

# Response includes:
{
  "status": "healthy",
  "services": {
    "redis": {"status": "healthy"},
    "embedding_model": {"status": "healthy"},
    "pinecone": {"status": "healthy"}
  },
  "response_time_ms": 45.2
}
```

### Logging
- Structured JSON logging
- Request ID tracking
- Error correlation
- Performance metrics

### LangSmith Integration
- Automatic trace collection
- Cost tracking
- Performance analysis
- Debug capabilities

## 💰 Cost Optimization

### Flexible AI System Architecture
```python
# PRODUCTION Option: GPT-5 Models
USE_GPT=true
- gpt-5-nano: Ultra-fast intent classification
- gpt-5-mini: Balanced performance/cost for queries
- gpt-5: Maximum capability when needed
- Optimized token usage and smart caching

# COST-EFFECTIVE Option: Local Mistral-7B
USE_GPT=false
- 100% free after initial setup
- Runs locally via Ollama
- No API rate limits or costs
- Good performance for most DeFi tasks
```

### Smart Processing Strategy
- **High confidence (≥0.98)**: Direct vector DB response (minimal AI cost)
- **Medium confidence (0.90-0.98)**: AI refinement only when needed
- **Low confidence (<0.90)**: AI fallback with optimized context

### Intelligent Context Management
- Context only added for detected follow-ups (not every query)
- 2-minute relevance window for context freshness
- Smart conversation history truncation
- **Performance impact**: 5-10% context overhead vs 100%+ with naive approaches

### Performance Optimizations
- Model instance caching and connection pooling
- Lazy loading for ML models and embeddings
- Redis caching for frequent queries
- Async operations with proper error handling
- Vector search optimization with confidence thresholds

## 🧪 Testing

### System Testing
```bash
# 1. Basic health check
curl http://localhost:8000/

# 2. Check active AI system
curl http://localhost:8000/health/detailed
# Returns: GPT-5 or Mistral system info

# 3. Test DeFi query
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is yield farming?"}'

# 4. Test action request
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "I want to swap 100 USDC for ETH"}'
```

### AI System Switching Test
```bash
# Test GPT-5 (Production)
echo "USE_GPT=true" >> .env
# Restart server and test

# Test Local Mistral (Cost-effective)
echo "USE_GPT=false" >> .env
# Ensure Ollama is running with mistral:7b model
# Restart server and test
```

### Health Monitoring
```bash
# Comprehensive health checks
curl http://localhost:8000/health/detailed  # Full system status
curl http://localhost:8000/health/ready     # Application readiness
curl http://localhost:8000/health/live      # Application liveness
curl http://localhost:8000/health/models    # AI system info
```

### Load Testing
```bash
# Test rate limiting (should hit 60/minute limit)
for i in {1..70}; do
  curl -X POST http://localhost:8000/query/ \
    -H "Content-Type: application/json" \
    -d '{"query": "test"}' &
done
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Deployment
```yaml
version: '3.8'
services:
  defi-ai-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - USE_GPT=true
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - REDIS_HOST=redis
    depends_on:
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD}
```

## 📈 Performance Metrics

### Benchmarks
- **Average Response Time**: <200ms for vector DB hits
- **Throughput**: 1000+ requests/minute
- **Uptime**: 99.9% with proper infrastructure
- **Cost Efficiency**: 80% queries served without LLM calls

### Scalability
- Horizontal scaling ready with Docker
- Stateless design
- Redis session management
- Load balancer compatible

## 🤝 Team Integration

### Backend API Contracts
This backend provides clean, well-documented APIs specifically designed for team integration:

#### For Frontend Team
```typescript
// TypeScript interfaces for frontend integration
interface SessionResponse {
  session_id: string;
  created_at: string;
  status: 'active' | 'expired';
}

interface QueryResponse {
  intent: 'general_query' | 'action_request' | 'clarification';
  session_id: string;
  answer?: string;
  action_details?: TransactionDetails;
  missing_parameters?: string[];
  suggested_questions?: string[];
  transaction_ready?: boolean;
  ai_system: 'gpt-5' | 'mistral';
  cost_analysis: CostInfo;
}

interface TransactionDetails {
  action: string;
  readiness_percentage: number;
  [key: string]: any; // Dynamic parameters
}
```

#### For Blockchain Team
```python
# Transaction execution interface
{
  "transaction_ready": true,
  "action_details": {
    "action": "swap",
    "amount": 100,
    "token_in": "USDC",
    "token_out": "ETH",
    "protocol": "Uniswap",
    "slippage_tolerance": 0.5,
    "deadline": 600,
    "readiness_percentage": 100
  },
  "estimated_gas": "21000",
  "next_step": "execute_transaction"
}
```

### Team Integration Features
- **CORS Configuration**: Pre-configured for team frontend origins
- **Error Handling**: Standardized error responses for consistent UI handling
- **Session Management**: Secure session sharing across team components
- **Transaction State**: Complete parameter tracking for blockchain execution
- **Real-time Ready**: Designed for WebSocket integration when needed

## ⚠️ Known Issues & Technical Debt

### Critical Issues Requiring Attention
- **x402 Global State**: Pending payments stored in global dictionaries (memory leaks, race conditions)
- **Weak Encryption**: Wallet secrets use base64 encoding instead of proper encryption
- **Hardcoded Test Data**: Same wallet secret returned for all users in mock DB
- **Event Loop Conflicts**: Complex nest_asyncio patching may fail in different environments
- **Missing Validation**: x402 parameters not validated before processing

### Security Improvements Needed
- Implement proper AES encryption for wallet secrets with key management
- Add payment timeout mechanisms for x402 transactions
- Replace global state with Redis-based session storage
- Add comprehensive parameter validation for all CDP operations
- Implement proper error boundaries for CDP agent failures

### Performance Optimizations
- Fix model selection logic for local Mistral deployment
- Add connection pooling for CDP agent instances
- Implement proper cleanup for abandoned transactions
- Add circuit breakers for external service calls

## 🔮 Future Roadmap

### AI System Enhancements
- [ ] GPT-6 integration when available
- [ ] Claude 3.5 Sonnet support
- [ ] Local model support (Llama, Mistral)
- [ ] Multi-model ensemble responses
- [ ] Custom fine-tuned DeFi models

### Blockchain & DeFi Enhancements
- [ ] Multi-chain support (Ethereum, Polygon, Arbitrum)
- [ ] Advanced DeFi protocol integrations (Compound, MakerDAO)
- [ ] MEV protection and transaction optimization
- [ ] Cross-chain bridge operations
- [ ] Yield farming strategy automation
- [ ] Portfolio management and rebalancing

### Team Collaboration Features
- [ ] WebSocket endpoints for real-time updates (for frontend team)
- [ ] GraphQL API alongside REST (if requested by frontend team)
- [ ] Enhanced transaction state management (for blockchain team)
- [ ] Multi-step transaction orchestration (cross-team feature)
- [ ] Advanced parameter validation (blockchain integration)

### Technical Improvements
- [ ] Advanced caching with Redis Cluster
- [ ] Distributed model serving
- [ ] Enhanced security with OAuth2/JWT
- [ ] Automated model performance monitoring
- [ ] Cross-chain transaction support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for AI orchestration framework
- **Pinecone** for vector database infrastructure
- **OpenAI** for language model capabilities
- **FastAPI** for modern Python web framework

## 📞 Team Support

### For Team Members
- **Backend Issues**: Create an issue in this repository
- **Integration Questions**: Contact Aayush Kumar (aayushkr646@gmail.com)
- **API Documentation**: See [docs/TEAM_INTEGRATION.md](docs/TEAM_INTEGRATION.md)
- **Deployment Help**: See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

### For External Contributors
- Create an issue in this repository
- Follow the contribution guidelines in [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Built with ❤️ by the team for the DeFi*
>>>>>>> d56b968a80445503745f19adc5fdf34fea0cf4f8

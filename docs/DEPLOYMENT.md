# Deployment Guide 🚀

This guide covers different deployment options for the DeFi AI Assistant.

## 📋 Prerequisites

- Python 3.9+
- Redis server
- Pinecone account with index created
- OpenAI API key
- LangSmith account (optional, for observability)

## 🔧 Local Development

### 1. Environment Setup
```bash
# Clone repository
git clone <your-repo-url>
cd defi-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit .env with your API keys
nano backend/.env
```

### 3. Start Services
```bash
# Start Redis (if not running)
redis-server

# Start the API
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Verify Installation
```bash
# Check health
curl http://localhost:8000/health/detailed

# Test query
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is DeFi?"}'
```

## 🐳 Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose Setup
```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data

  defi-ai:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - LANGSMITH_API_KEY=${LANGSMITH_API_KEY}
    depends_on:
      - redis
    restart: unless-stopped

volumes:
  redis_data:
```

### 3. Deploy with Docker Compose
```bash
# Create .env file with your secrets
echo "REDIS_PASSWORD=your-secure-password" > .env
echo "OPENAI_API_KEY=your-openai-key" >> .env
echo "PINECONE_API_KEY=your-pinecone-key" >> .env
echo "LANGSMITH_API_KEY=your-langsmith-key" >> .env

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f defi-ai
```

## 🚀 Production Docker Deployment

### 1. Create Environment File
```bash
# Create production environment file
cat > .env.prod << EOF
# AI System Configuration
USE_GPT=true
OPENAI_API_KEY=your-openai-key
PINECONE_API_KEY=your-pinecone-key
LANGSMITH_API_KEY=your-langsmith-key

# Database Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-secure-redis-password

# Security Configuration
DEBUG=false
ALLOWED_ORIGINS=["https://yourdomain.com"]
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Application Configuration
PINECONE_INDEX=defi-queries
SESSION_TTL=300
EOF
```

### 2. Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - defi-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  defi-ai:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - defi-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      defi-ai:
        condition: service_healthy
    networks:
      - defi-network

volumes:
  redis_data:

networks:
  defi-network:
    driver: bridge
```

### 3. Production Dockerfile
```dockerfile
# Dockerfile.prod
FROM python:3.9-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 4. Deploy Production Stack
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f defi-ai

# Scale application
docker-compose -f docker-compose.prod.yml up -d --scale defi-ai=3
```

## 🌐 Cloud Deployment Options

### AWS ECS
```json
{
  "family": "defi-ai-assistant",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "defi-ai",
      "image": "your-ecr-repo/defi-ai-assistant:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "REDIS_HOST", "value": "your-redis-cluster.cache.amazonaws.com"},
        {"name": "REDIS_PORT", "value": "6379"}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:openai-key"},
        {"name": "PINECONE_API_KEY", "valueFrom": "arn:aws:secretsmanager:region:account:secret:pinecone-key"}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health/live || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### Google Cloud Run
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: defi-ai-assistant
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
      - image: gcr.io/your-project/defi-ai-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: "your-redis-instance-ip"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
        resources:
          limits:
            cpu: "1"
            memory: "1Gi"
```

## 📊 Monitoring Setup

### Prometheus Metrics
```yaml
# Add to your deployment
- name: prometheus-metrics
  image: prom/node-exporter:latest
  ports:
  - containerPort: 9100
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "DeFi AI Assistant",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      }
    ]
  }
}
```

## 🔒 Security Checklist

### Application Security
- [ ] API keys stored in secrets management (never in code)
- [ ] Debug mode disabled (`DEBUG=false`)
- [ ] Rate limiting configured and tested
- [ ] Input sanitization enabled for all endpoints
- [ ] CORS properly configured with specific origins
- [ ] Session security with secure UUID generation
- [ ] Logging configured (no sensitive data exposure)
- [ ] Error messages sanitized (no internal details)

### Infrastructure Security
- [ ] HTTPS enabled with valid certificates
- [ ] Firewall rules configured
- [ ] Database/Redis access restricted
- [ ] Container running as non-root user
- [ ] Resource limits set (CPU, memory)
- [ ] Health checks implemented
- [ ] Network security configured
- [ ] Secrets rotation strategy in place

### Team Integration Security
- [ ] Frontend CORS origins whitelisted
- [ ] API authentication strategy defined
- [ ] Session sharing security between components
- [ ] Transaction parameter validation
- [ ] Audit logging for all actions

For detailed security information, see [SECURITY.md](SECURITY.md)

## 🚨 Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check Redis connectivity
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

# Check logs
docker-compose logs redis
```

**Pinecone Index Not Found**
```bash
# Verify index exists
curl -X GET "https://api.pinecone.io/indexes" \
  -H "Api-Key: $PINECONE_API_KEY"
```

**High Memory Usage**
```bash
# Check model loading
curl http://localhost:8000/health/detailed

# Monitor memory
docker stats
docker-compose top
```

### Performance Tuning

**Optimize for High Traffic**
```python
# In settings.py
RATE_LIMIT_PER_MINUTE = 120
VECTOR_SEARCH_TOP_K = 5
SESSION_TTL = 600  # 10 minutes
```

**Reduce Memory Usage**
```python
# In settings.py
MAX_CONVERSATION_HISTORY = 5
MAX_TOKENS = 500
```

## 👥 Team Development Setup

### Multi-Component Development
For teams working on frontend, backend, and blockchain components:

#### Backend Development (This Repo)
```bash
# Backend team setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start backend API
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Integration
```bash
# Configure CORS for frontend development
echo "ALLOWED_ORIGINS=[\"http://localhost:3000\",\"http://localhost:8501\"]" >> .env

# Test frontend integration
curl -X POST http://localhost:8000/query/start-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "frontend_test"}'
```

#### Blockchain Integration Testing
```bash
# Test transaction readiness endpoint
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I want to swap 100 USDC for ETH on Uniswap with 0.5% slippage",
    "session_id": "your_session_id"
  }'

# Should return transaction_ready: true when all parameters collected
```

### Team Deployment Strategy

#### Development Environment
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  backend-ai:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
    
  frontend:
    # Frontend team's container
    ports:
      - "3000:3000"
    depends_on:
      - backend-ai
      
  blockchain:
    # Blockchain team's container  
    ports:
      - "8080:8080"
    depends_on:
      - backend-ai
```

#### Production Deployment
```bash
# Coordinated deployment
docker-compose -f docker-compose.team.yml up -d

# Verify all components
docker-compose -f docker-compose.team.yml ps
```

## 📞 Support

### For Deployment Issues
1. Check the health endpoints first: `GET /health/detailed`
2. Review application logs: `docker-compose logs -f defi-ai`
3. Verify all environment variables are set
4. Test external service connectivity (Redis, Pinecone, AI APIs)
5. Check team integration points (CORS, session sharing)

### Team Coordination
- **Backend Issues**: Check this repository's issues (Aayush Kumar)
- **Frontend Integration**: Coordinate through team communication channels
- **Blockchain Integration**: Coordinate transaction execution and parameter validation
- **Security Concerns**: Follow [SECURITY.md](SECURITY.md) reporting procedures

### Team Contact Information
- **Backend Team (Aayush)**: aayushkr646@gmail.com
- **Frontend Team**: [Contact Info]
- **Blockchain Team**: [Contact Info]
- **Project Repository**: [GitHub Issues](https://github.com/team-repo/issues)
- **Team Communication**: [Discord/Slack/Teams channel]

---

**Happy Team Deploying! 🚀**

The backend is ready for team integration and production deployment. Coordinate with frontend and blockchain teams for complete system deployment.
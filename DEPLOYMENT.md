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

## ☸️ Kubernetes Deployment

### 1. Create Secrets
```bash
kubectl create secret generic defi-ai-secrets \
  --from-literal=openai-api-key=your-openai-key \
  --from-literal=pinecone-api-key=your-pinecone-key \
  --from-literal=langsmith-api-key=your-langsmith-key \
  --from-literal=redis-password=your-redis-password
```

### 2. Redis Deployment
```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        env:
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: defi-ai-secrets
              key: redis-password
        command: ["redis-server", "--requirepass", "$(REDIS_PASSWORD)"]
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

### 3. Application Deployment
```yaml
# defi-ai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: defi-ai-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: defi-ai-assistant
  template:
    metadata:
      labels:
        app: defi-ai-assistant
    spec:
      containers:
      - name: api
        image: your-registry/defi-ai-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: defi-ai-secrets
              key: redis-password
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: defi-ai-secrets
              key: openai-api-key
        - name: PINECONE_API_KEY
          valueFrom:
            secretKeyRef:
              name: defi-ai-secrets
              key: pinecone-api-key
        - name: LANGSMITH_API_KEY
          valueFrom:
            secretKeyRef:
              name: defi-ai-secrets
              key: langsmith-api-key
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: defi-ai-service
spec:
  selector:
    app: defi-ai-assistant
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 4. Deploy to Kubernetes
```bash
# Apply deployments
kubectl apply -f redis-deployment.yaml
kubectl apply -f defi-ai-deployment.yaml

# Check status
kubectl get pods
kubectl get services

# Check logs
kubectl logs -f deployment/defi-ai-assistant
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

- [ ] API keys stored in secrets management
- [ ] HTTPS enabled with valid certificates
- [ ] Rate limiting configured
- [ ] Input sanitization enabled
- [ ] CORS properly configured
- [ ] Debug mode disabled in production
- [ ] Logging configured (no sensitive data)
- [ ] Health checks implemented
- [ ] Resource limits set
- [ ] Network policies applied (K8s)

## 🚨 Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check Redis connectivity
redis-cli -h $REDIS_HOST -p $REDIS_PORT ping

# Check logs
kubectl logs deployment/redis
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
kubectl top pods
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

## 📞 Support

For deployment issues:
1. Check the health endpoints first
2. Review application logs
3. Verify all environment variables
4. Test external service connectivity
5. Create an issue with deployment details

---

**Happy Deploying! 🚀**
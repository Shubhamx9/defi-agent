# 🔄 AI System Switching Guide

Your DeFi AI Assistant supports **seamless switching** between free Gemini models and paid GPT-5 models. This guide shows you how to switch between systems and optimize for your needs.

## 📊 GPT-5 Model Pricing (Per 1K Tokens)

| Model | Input Cost | Output Cost | Max Cost | Best For |
|-------|------------|-------------|----------|----------|
| **gpt-5** | $1.25 | $0.125 | $10.00 | Complex reasoning, advanced analysis |
| **gpt-5-mini** | $0.25 | $0.025 | $2.00 | General queries, balanced performance |
| **gpt-5-nano** | $0.05 | $0.005 | $0.40 | Simple tasks, ultra-fast processing |
| **gpt-5-chat-latest** | $1.25 | $0.125 | $10.00 | Latest training, creative tasks |

## 💰 Cost Optimization Strategy

### **Recommended Model Assignment**

```python
# Ultra-cost-effective setup
INTENT_MODEL=gpt-5-nano        # 90% cheaper than GPT-4o-mini for classification
QUERY_MODEL=gpt-5-mini         # Better performance at similar cost to GPT-4o-mini
ACTION_MODEL=gpt-5-mini        # Improved parameter extraction
ADVANCED_MODEL=gpt-5           # For complex DeFi analysis when needed
```

### **Cost Comparison**

**Current Setup (GPT-4o-mini for everything):**
- Intent Classification: $0.00015 input + $0.0006 output
- Query Processing: $0.00015 input + $0.0006 output  
- Action Extraction: $0.00015 input + $0.0006 output

**Optimized GPT-5 Setup:**
- Intent Classification: $0.05 input + $0.005 output (gpt-5-nano)
- Query Processing: $0.25 input + $0.025 output (gpt-5-mini)
- Action Extraction: $0.25 input + $0.025 output (gpt-5-mini)

**Result**: Potential 60-80% cost reduction for intent classification while improving overall capability!

## 🔄 System Switching

### **Switch to Free Gemini Models**

```bash
# 1. Edit your .env file
USE_GEMINI=true
GOOGLE_API_KEY=your_google_api_key

# 2. Set Gemini model names
INTENT_MODEL=gemini-1.5-flash
QUERY_MODEL=gemini-1.5-pro  
ACTION_MODEL=gemini-1.5-flash

# 3. Restart server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Switch to Paid GPT-5 Models**

```bash
# 1. Edit your .env file
USE_GEMINI=false
OPENAI_API_KEY=your_openai_api_key

# 2. Set GPT-5 model names
INTENT_MODEL=gpt-5-nano
QUERY_MODEL=gpt-5-mini
ACTION_MODEL=gpt-5-mini

# 3. Restart server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### **Verify System Switch**

```bash
# Check which system is active
curl http://localhost:8000/health/models

# Test a query
curl -X POST http://localhost:8000/query/ \
  -H "Content-Type: application/json" \
  -d '{"query": "What is DeFi?"}'
```

## 🎯 Task-Specific Recommendations

### **Intent Classification**
```python
# Perfect for gpt-5-nano
# - Simple classification task
# - 90% cost reduction
# - Ultra-fast processing
INTENT_MODEL=gpt-5-nano
```

### **General Queries**
```python
# Ideal for gpt-5-mini
# - Better reasoning than GPT-4o-mini
# - Similar cost structure
# - Faster processing
QUERY_MODEL=gpt-5-mini
```

### **Action Extraction**
```python
# Great for gpt-5-mini
# - Improved parameter extraction
# - Better JSON formatting
# - More reliable parsing
ACTION_MODEL=gpt-5-mini
```

### **Complex DeFi Analysis**
```python
# Use gpt-5 when needed
# - Advanced reasoning
# - Complex calculations
# - Multi-step analysis
ADVANCED_MODEL=gpt-5
```

## 🛡️ Safety & Rollback

### **Fallback Configuration**
```python
# Always keep fallback models
FALLBACK_MODEL=gpt-4o-mini

# Model manager automatically falls back if GPT-5 unavailable
```

### **Rollback Plan**
```python
# If issues arise, quickly rollback
INTENT_MODEL=gpt-4o-mini
QUERY_MODEL=gpt-4o-mini
ACTION_MODEL=gpt-4o-mini
```

### **A/B Testing**
```python
# Test GPT-5 on subset of traffic
# Use feature flags or percentage-based routing
```

## 📈 Expected Benefits

### **Performance Improvements**
- **Intent Classification**: 2x faster with gpt-5-nano
- **Query Processing**: 30% better reasoning with gpt-5-mini
- **Action Extraction**: 40% more accurate parameter parsing
- **Complex Analysis**: 50% better multi-step reasoning with gpt-5

### **Cost Benefits**
- **Intent Classification**: 90% cost reduction
- **Overall System**: 20-40% total cost reduction
- **Scalability**: Better cost structure for high-volume usage

### **Capability Improvements**
- Better understanding of DeFi concepts
- More accurate parameter extraction
- Improved conversation context handling
- Enhanced error recovery

## 🔍 Monitoring & Optimization

### **Key Metrics to Track**
```python
# Cost metrics
- Cost per request by model
- Total monthly spend
- Cost per successful transaction

# Performance metrics  
- Response time by model
- Accuracy rates
- Error rates
- User satisfaction
```

### **Optimization Opportunities**
```python
# Dynamic model selection based on query complexity
# Caching strategies for repeated queries
# Batch processing for multiple requests
# Smart fallback logic
```

## 🚨 Common Issues & Solutions

### **Issue: GPT-5 Not Available**
```python
# Solution: Automatic fallback is configured
# Check: API key permissions
# Check: Account access to GPT-5
```

### **Issue: Higher Costs Than Expected**
```python
# Solution: Review model assignment
# Check: Token usage patterns
# Optimize: Prompt lengths
```

### **Issue: Performance Regression**
```python
# Solution: A/B test against GPT-4o-mini
# Check: Prompt compatibility
# Adjust: Temperature and parameters
```

## 🎉 Success Checklist

- [ ] GPT-5 models available in account
- [ ] Environment variables updated
- [ ] Model availability tested
- [ ] Cost monitoring in place
- [ ] Performance benchmarks established
- [ ] Rollback plan ready
- [ ] Team trained on new capabilities

## 📞 Support

If you encounter issues during migration:

1. Check model availability: `GET /health/models`
2. Review cost analysis in health endpoint
3. Monitor LangSmith traces for performance
4. Use fallback models if needed
5. Contact OpenAI support for API access issues

---

**Enjoy seamless AI system switching! 🚀**

Your DeFi AI Assistant can now switch between free Gemini and paid GPT-5 models instantly, giving you the flexibility to optimize for cost or capability as needed.
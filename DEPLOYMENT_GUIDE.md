# 🚀 MIPA Deployment Guide

## 📋 **System Requirements**

### **Production Environment**
- **Backend**: Python 3.11+, 2GB RAM, 1 CPU core
- **Frontend**: Node.js 18+, Static hosting (Vercel/Netlify)
- **Database**: PostgreSQL (Neon/AWS RDS)
- **APIs**: OpenAI GPT-4, Smarty Streets

## 🔧 **Environment Setup**

### **Backend Environment Variables**
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4-1106-preview

# Database (Neon Cloud)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Smarty Streets API
SMARTY_AUTH_ID=your-smarty-auth-id
SMARTY_AUTH_TOKEN=your-smarty-auth-token

# CORS Settings
ALLOWED_HOSTS=["http://localhost:3000", "https://your-domain.com"]
```

### **Frontend Environment Variables**
```env
REACT_APP_API_URL=http://localhost:8003
# For production: REACT_APP_API_URL=https://your-api-domain.com
```

## 🌐 **Deployment Options**

### **Option 1: Cloud Deployment (Recommended)**

#### **Backend - Railway/Render**
```bash
# Deploy to Railway
railway login
railway new
railway add
railway deploy

# Or Render
# Connect GitHub repo
# Set environment variables
# Auto-deploy on push
```

#### **Frontend - Vercel**
```bash
# Deploy to Vercel
npm install -g vercel
cd frontend
vercel

# Set environment variables in Vercel dashboard
```

### **Option 2: Docker Deployment**

#### **Backend Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8003

CMD ["python", "api.py"]
```

#### **Frontend Dockerfile**
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
```

#### **Docker Compose**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8003:8003"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - SMARTY_AUTH_ID=${SMARTY_AUTH_ID}
      - SMARTY_AUTH_TOKEN=${SMARTY_AUTH_TOKEN}
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_API_URL=http://localhost:8003
```

## 🔐 **Security Checklist**

### **Production Security**
- ✅ **Environment Variables**: Never commit API keys
- ✅ **HTTPS**: Use SSL certificates for production
- ✅ **CORS**: Configure allowed origins properly
- ✅ **Rate Limiting**: Add API rate limits
- ✅ **Input Validation**: Sanitize all user inputs

### **API Security**
```python
# Add to api.py for production
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```

## 📊 **Monitoring & Analytics**

### **Backend Monitoring**
```python
# Add logging and monitoring
import logging
from prometheus_client import Counter, Histogram

# Track API usage
api_requests = Counter('api_requests_total', 'Total API requests')
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')
```

### **Cost Monitoring**
- **Daily Cost Tracking**: Monitor OpenAI API usage
- **Usage Alerts**: Set up cost alerts at $10, $50, $100
- **Optimization**: Track cost per analysis for optimization

## 🧪 **Testing**

### **Backend Tests**
```bash
cd backend
pytest tests/
```

### **Frontend Tests**
```bash
cd frontend
npm test
```

### **Integration Tests**
```bash
# Test complete workflow
curl -X POST http://localhost:8003/start-analysis \
  -H "Content-Type: application/json" \
  -d '{"address": "123 Main St", "smarty_data": {}}'
```

## 📈 **Performance Optimization**

### **Backend Optimization**
- **Caching**: Redis for session storage
- **Database**: Connection pooling
- **API**: Async/await for all operations

### **Frontend Optimization**
- **Code Splitting**: Lazy load components
- **Caching**: Service worker for static assets
- **CDN**: Use CDN for faster loading

## 🔄 **CI/CD Pipeline**

### **GitHub Actions**
```yaml
name: Deploy MIPA
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy Backend
        run: |
          # Deploy to your cloud provider
      - name: Deploy Frontend
        run: |
          # Deploy to Vercel/Netlify
```

## 📊 **Analytics & Insights**

### **Usage Metrics**
- **Properties Analyzed**: Track total analyses
- **Research Mode Usage**: Manual vs automatic
- **Average Session Duration**: User engagement
- **Most Analyzed Locations**: Popular areas

### **Performance Metrics**
- **API Response Time**: < 2 seconds target
- **Analysis Completion Rate**: > 95% target
- **User Satisfaction**: Based on conversation length

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Backend Won't Start**
```bash
# Check port availability
netstat -an | findstr ":8003"

# Verify environment variables
python -c "from config import OPENAI_API_KEY; print('API key loaded')"
```

#### **Frontend Build Errors**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

#### **Database Connection Issues**
```bash
# Test database connection
python -c "from sqlalchemy import create_engine; engine = create_engine('your_db_url'); print('DB connected')"
```

## 📞 **Support & Maintenance**

### **Regular Maintenance**
- **Weekly**: Check API usage and costs
- **Monthly**: Update dependencies
- **Quarterly**: Review and optimize prompts

### **Scaling Considerations**
- **High Volume**: Consider fine-tuning for cost reduction
- **Multiple Users**: Add authentication and user management
- **Enterprise**: Implement multi-tenant architecture

---

**🏢 MIPA - Transforming Commercial Real Estate Analysis with AI**

*For technical support, create an issue or contact the development team*

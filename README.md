# 🏢 MIPA - Intelligent CRE Chatbot & Analysis Tool

## 🎯 Advanced IMST Property Analysis System

A comprehensive AI-powered commercial real estate analysis platform specializing in gas station and convenience store site selection using the **IMST (Independent Multi-Site Testing)** methodology.

## ✨ **Key Features**

### 🤖 **Intelligent AI Analyst - "Rohit"**
- **Conversational Analysis**: Professional CRE analyst with 15+ years experience
- **IMST Methodology**: Specialized in gas station/convenience store evaluation
- **Context Awareness**: Remembers entire conversation and property details
- **Short, Focused Responses**: Direct, professional communication

### 🔍 **Advanced Research Mode**
- **Automatic Data Research**: AI researches missing property data
- **Traffic Analysis**: Estimates daily vehicle counts
- **Competition Research**: Finds nearby gas stations and stores
- **Demographics**: Population and income analysis
- **Visibility Assessment**: Highway visibility and access evaluation

### 📊 **Complete IMST Scoring**
- **7-Elements+ System**: Location, Market, Brand, Facility, etc.
- **Weighted Scoring**: Professional methodology with transparent calculations
- **Investment Recommendations**: BUY/INVESTIGATE/PASS decisions
- **Risk Assessment**: Red flags and concerns identification

### 🎨 **Modern UI Design**
- **Clean White/Black Theme**: Consistent with professional standards
- **Real-time Progress**: Visual progress tracking and data checklist
- **Responsive Design**: Works on desktop and mobile
- **Professional Layout**: Left panel (data) + Right panel (chat)

## 🏗️ **Architecture**

### **Backend (Python FastAPI)**
```
backend/
├── api.py                              # Main FastAPI application
├── services/
│   ├── intelligent_property_analyst.py # Rohit - AI analyst
│   ├── advanced_research_agent.py      # Automatic data research
│   ├── llm_scoring_system.py          # IMST scoring engine
│   └── scoring_api.py                 # API endpoints
├── conversation_storage.py            # Chat memory system
├── cost_calculator.py                # API cost analysis
└── smarty_address_analyzer_new.py    # Smarty API integration
```

### **Frontend (React + Tailwind CSS)**
```
frontend/src/
├── components/
│   ├── Chatbot/
│   │   ├── SmartAnalyst.jsx          # Main analysis interface
│   │   ├── AddressDetailsMode.jsx    # Address lookup
│   │   └── Chatbot.jsx              # Chat coordinator
│   └── PropertyGallery/             # Property browsing
├── services/
│   ├── api.js                       # Backend API calls
│   └── chatService.js               # Chat functionality
└── pages/                           # Main application pages
```

## 🚀 **Getting Started**

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- PostgreSQL (Neon cloud database)
- OpenAI API Key
- Smarty Streets API Key

### **Installation**

#### **1. Clone Repository**
```bash
git clone <your-repo-url>
cd MIPA-Intelliegent-CRE-chatbot-and-analysis-research-tool-using-llama-index-and-langraph-
```

#### **2. Backend Setup**
```bash
cd backend
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_openai_key" > .env
echo "DATABASE_URL=your_neon_db_url" >> .env
echo "SMARTY_AUTH_ID=your_smarty_id" >> .env
echo "SMARTY_AUTH_TOKEN=your_smarty_token" >> .env

# Start backend
python api.py
```

#### **3. Frontend Setup**
```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

### **4. Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8003
- **API Documentation**: http://localhost:8003/docs

## 🎯 **How to Use**

### **Property Analysis Workflow**

1. **Address Lookup**:
   - Go to AI Assistant → Address Details
   - Enter property address
   - Click "Get Details" → See Smarty API data

2. **Start AI Analysis**:
   - Click "🤖 Start AI Analysis"
   - Meet Rohit - your AI property analyst
   - See complete property context displayed

3. **Choose Analysis Mode**:
   - **Manual**: Answer Rohit's questions step by step
   - **Research**: Click "🤖 Activate Advanced Research Mode"

4. **Get Results**:
   - Receive complete IMST score (0-10)
   - View detailed breakdown by criteria
   - Get investment recommendation
   - See strengths and concerns

## 📊 **IMST Scoring Criteria**

| Criteria | Weight | Description |
|----------|--------|-------------|
| **Location** | 30% | Traffic count, visibility, highway access |
| **Demographics** | 30% | Population density, income levels |
| **Competition** | 20% | Nearby gas stations and stores |
| **Facility** | 20% | Building size, lot size, condition |

## 🔍 **Advanced Features**

### **🤖 AI Research Agent**
- **Traffic Estimation**: Based on road type and location
- **Competition Analysis**: Suburban density patterns
- **Demographics**: Census tract analysis
- **Cost**: ~$0.06 per complete analysis

### **💾 Conversation Memory**
- **Learning System**: Stores all conversations
- **Feedback Loop**: Improves recommendations over time
- **Session Management**: Maintains context throughout analysis

### **📈 Data Sources**
- **Smarty Streets API**: Property records, financials, ownership
- **AI Research**: Traffic, competition, demographics
- **User Input**: Local knowledge and insights

## 🛠️ **API Endpoints**

### **Core Analysis**
- `POST /start-analysis` - Begin property analysis with Rohit
- `POST /continue-analysis/{session_id}` - Continue conversation
- `POST /research-property/{session_id}` - Activate research mode

### **Property Data**
- `GET /properties` - Browse property database
- `POST /address-analysis` - Smarty API address lookup
- `POST /score-address` - Combined analysis + scoring

### **Utilities**
- `GET /cost-analysis` - API usage cost breakdown
- `GET /analysis-status/{session_id}` - Check analysis progress

## 💰 **Cost Analysis**

### **Per Property Analysis**
- **Manual Mode**: ~$0.03 (user provides data)
- **Research Mode**: ~$0.06 (AI researches data)
- **Hybrid Mode**: ~$0.04 (mixed approach)

### **Bulk Analysis (1000 properties)**
- **Research Mode**: ~$60
- **Manual Mode**: ~$30
- **Extremely cost-effective** for professional analysis

## 🔧 **Configuration**

### **Environment Variables**
```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4-1106-preview

# Database
DATABASE_URL=postgresql://user:pass@host/db

# Smarty Streets API
SMARTY_AUTH_ID=your_auth_id
SMARTY_AUTH_TOKEN=your_auth_token
```

## 📱 **Screenshots**

### **Smart Analyst Interface**
- Clean white/black professional theme
- Real-time progress tracking
- IMST data checklist with ✅/❌ indicators
- Conversational AI analysis

### **Property Data Display**
- Complete Smarty API integration
- Financial information and ownership details
- Market analysis and investment scoring

## 🚀 **Future Enhancements**

### **Phase 1: Model Optimization**
- **Fine-tune GPT-4o**: 75% cost reduction
- **Multi-agent System**: Specialized AI agents
- **Real-time APIs**: Live traffic and competition data

### **Phase 2: Advanced Features**
- **Image Analysis**: Satellite imagery assessment
- **Market Trends**: Historical data analysis
- **Portfolio Management**: Multi-property tracking

## 🛡️ **Security & Privacy**

- **API Key Protection**: Environment variables only
- **Data Encryption**: All API communications secured
- **Conversation Storage**: Local JSON files (can be encrypted)
- **No PII Storage**: Only property and analysis data

## 📚 **Documentation**

- **Technical Documentation**: `TECHNICAL_DOCUMENTATION.md`
- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Site Flow Analysis**: `SITE_FLOW_ANALYSIS.md`
- **Data Pipeline Plan**: `REAL_ESTATE_DATA_PIPELINE_PLAN.md`

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **IMST Methodology**: Independent Multi-Site Testing for gas station analysis
- **Smarty Streets**: Property data and address verification
- **OpenAI**: GPT-4 for intelligent analysis
- **React + Tailwind**: Modern, responsive UI framework

## 📞 **Support**

For questions, issues, or feature requests:
- **Create an Issue**: Use GitHub Issues
- **Documentation**: Check the docs folder
- **API Reference**: Visit `/docs` endpoint when running

---

**Built with ❤️ for Commercial Real Estate Intelligence**

*Transform property analysis with AI-powered IMST methodology*
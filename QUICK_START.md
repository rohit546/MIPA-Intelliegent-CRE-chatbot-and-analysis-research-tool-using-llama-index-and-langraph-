# ⚡ MIPA Quick Start Guide

## 🚀 **Get Running in 5 Minutes**

### **Step 1: Environment Setup**
```bash
# Backend
cd backend
echo "OPENAI_API_KEY=your-key" > .env
echo "DATABASE_URL=your-neon-db-url" >> .env
echo "SMARTY_AUTH_ID=your-smarty-id" >> .env
echo "SMARTY_AUTH_TOKEN=your-smarty-token" >> .env

pip install -r requirements.txt
python api.py
```

### **Step 2: Frontend Setup**
```bash
# Frontend (new terminal)
cd frontend
npm install --legacy-peer-deps
npm start
```

### **Step 3: Test the System**
1. **Open**: http://localhost:3000
2. **Navigate**: AI Assistant → Address Details
3. **Enter**: "526 Flint River Rd, Jonesboro, GA"
4. **Click**: "Get Details" → See Smarty data
5. **Click**: "🤖 Start AI Analysis" → Meet Rohit!

## 🎯 **Key Features to Test**

### **🤖 Intelligent Analyst - Rohit**
- **Context Awareness**: Shows complete property details
- **Short Responses**: Professional, focused questions
- **Memory**: Remembers entire conversation

### **🔍 Research Mode**
- **Click**: "🤖 Activate Advanced Research Mode"
- **Watch**: AI research traffic, competition, demographics
- **Get**: Complete analysis in 30 seconds

### **📊 IMST Scoring**
- **Automatic**: Generates when enough data collected
- **Transparent**: Shows exactly what data was used
- **Professional**: Investment recommendations

## 🎨 **UI Features**

### **Modern Design**
- ✅ **White/Black Theme**: Professional, clean
- ✅ **Progress Tracking**: Real-time analysis progress
- ✅ **Data Checklist**: ✅/❌ indicators for data points
- ✅ **Responsive**: Works on all devices

### **Behind-the-Scenes**
- 🧠 **AI Model**: Shows "GPT-4 Turbo" working
- 📊 **Data Sources**: "Smarty API + User Input"
- 🎯 **Analysis Stage**: Progress indicators

## 💰 **Cost Information**

- **Per Analysis**: ~$0.06 (6 cents)
- **Research Mode**: Automatic data completion
- **Manual Mode**: User provides data (~$0.03)

## 🛠️ **Troubleshooting**

### **Backend Issues**
```bash
# Check if running
curl http://localhost:8003/

# View logs
# Check terminal for error messages
```

### **Frontend Issues**
```bash
# Check if running
curl http://localhost:3000/

# Clear cache
rm -rf node_modules
npm install --legacy-peer-deps
```

## 📚 **Next Steps**

### **For Development**
1. **Read**: `TECHNICAL_DOCUMENTATION.md`
2. **Explore**: API docs at http://localhost:8003/docs
3. **Customize**: Modify prompts in `intelligent_property_analyst.py`

### **For Production**
1. **Read**: `DEPLOYMENT_GUIDE.md`
2. **Setup**: Cloud hosting (Railway, Vercel)
3. **Monitor**: API usage and costs

---

**🎉 Ready to analyze properties with AI!**

*Professional IMST analysis in under 6 cents per property*

# MIPA - Intelligent CRE Chatbot and Analysis Research Tool

A professional Commercial Real Estate (CRE) analysis platform powered by LlamaIndex and modern web technologies.

## 🚀 Features

- **AI-Powered Property Search**: Natural language queries for property search
- **Advanced Analytics**: Property analysis with market insights
- **Interactive Chat Interface**: Conversational property recommendations
- **Professional UI**: Modern, responsive design with dark/light theme
- **Real-time Data**: Connected to live property databases
- **Property Gallery**: Visual property browsing with filters

## 🏗️ Tech Stack

**Frontend:**
- React 18 with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- Modern UI components

**Backend:**
- Python FastAPI
- LlamaIndex for AI/LLM integration
- PostgreSQL database
- OpenAI GPT integration

## 📋 Prerequisites

- Node.js 16+ and npm
- Python 3.9+
- PostgreSQL database
- OpenAI API key

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rohit546/MIPA-Intelliegent-CRE-chatbot-and-analysis-research-tool-using-llama-index-and-langraph-.git
   cd MIPA-Intelliegent-CRE-chatbot-and-analysis-research-tool-using-llama-index-and-langraph-
   ```

2. **Setup Python environment**
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API keys and database URL
   ```

5. **Start the backend server**
   ```bash
   python -m uvicorn api_server:app --host 127.0.0.1 --port 8002 --reload
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment (optional)**
   ```bash
   cp .env.example .env.local
   # Edit if you need to change API URLs
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   ```
   http://localhost:3000
   ```

## 🔧 Configuration

### Environment Variables

**Backend (.env):**
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=your_postgresql_connection_string
```

**Frontend (.env.local) - Optional:**
```env
REACT_APP_API_URL=http://localhost:8002
```

## 📚 Usage

1. **Start both servers** (backend on :8002, frontend on :3000)
2. **Browse properties** using the gallery interface
3. **Ask natural language questions** like:
   - "Show me commercial properties under $500k"
   - "Find retail spaces near highways"
   - "Properties with good ROI potential"

## 🏢 Project Structure

```
├── backend/
│   ├── api_server.py          # Main FastAPI application
│   ├── app_enhanced.py        # Enhanced query engine setup
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── services/         # API services
│   │   └── ...
│   ├── package.json          # Node dependencies
│   └── ...
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review environment variable setup

---

Built with ❤️ for the Commercial Real Estate industry
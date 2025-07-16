# 🧠 GenAI-Powered Dynamic Team Skill Recommendation System

> 🌟 **AI-powered system that generates real-time, personalized skill recommendations based on current industry trends and market demands.**

**Landing page**
<img width="2072" height="1302" alt="image" src="https://github.com/user-attachments/assets/01347a56-e584-47ff-9ae9-e1f3372e4b66" />

**App Execution**

Upload team memeber and skills here:
<img width="1154" height="1227" alt="image" src="https://github.com/user-attachments/assets/027dc6dc-9650-4cfd-97ae-0677c25e17e0" />

Select team member:
<img width="1555" height="1048" alt="image" src="https://github.com/user-attachments/assets/4659d048-8823-44d6-a25b-ed4f8915e556" />

Get Recommendations
<img width="1526" height="1214" alt="image" src="https://github.com/user-attachments/assets/ebc94b59-fbca-4b63-a103-a00071aa79b8" />

Show Trends:
<img width="1496" height="703" alt="image" src="https://github.com/user-attachments/assets/d44b2a2e-228c-4c95-b8fc-4f8d76739565" />

Cross-Skill:
<img width="634" height="1239" alt="image" src="https://github.com/user-attachments/assets/55745aec-f96e-47f0-99d2-e79136e0b37f" />

## 🎯 **Key Features**

### **🚀 Dynamic & Real-Time**
- **No static mappings** - Uses live industry data and trends
- **Real-time trend analysis** from GitHub, tech blogs, learning platforms
- **Market-driven recommendations** based on current job demands
- **AI-powered insights** using Groq's open-source LLMs

### **🔍 Multi-Source Intelligence**
- **GitHub Trends** - Trending repositories and technologies
- **Tech Blogs** - Latest industry insights and best practices
- **Learning Platforms** - Course popularity and skill demand
- **Job Market Data** - Current hiring trends and skill requirements
- **AI/ML Trends** - Emerging technologies and research

### **🎯 Personalized Recommendations**
- **Role-based upskilling** - Skills to advance in current role
- **Cross-skilling opportunities** - Adjacent role skills for career expansion
- **Experience-aware** - Recommendations tailored to career level
- **Market-relevant** - Skills with high demand and growth potential

## 🏗️ **Architecture**

### **Backend (Python + FastAPI + LangChain + LangGraph)**
```
backend/
├── api/                    # FastAPI endpoints
│   ├── endpoints/
│   │   ├── recommend.py    # Dynamic recommendations
│   │   └── ingest.py       # Data ingestion
│   └── main.py            # FastAPI app
├── agents/                 # LangGraph agents
│   ├── dynamic_upskill_agent.py      # Real-time upskilling
│   └── dynamic_crossskill_agent.py   # Cross-skilling paths
├── data_sources/           # Live data fetching
│   └── trend_analyzer.py   # Multi-source trend analysis
├── llm/                    # Groq LLM integration
│   └── groq_client.py      # Open-source LLM client
├── vectorizer/             # Document processing
│   ├── embedder.py         # Sentence transformers
│   └── vectorstore.py      # FAISS vector store
└── models/                 # Data schemas
    └── schemas.py          # Pydantic models
```

### **Frontend (React + Tailwind CSS)**
```
frontend/
├── src/
│   ├── components/         # React components
│   ├── pages/             # Page components
│   │   ├── Dashboard.js    # Overview dashboard
│   │   ├── TeamUpload.js   # Team data upload
│   │   └── Recommendations.js # Dynamic recommendations
│   └── App.js             # Main app
└── tailwind.config.js     # Styling configuration
```

## 🚀 **Quick Start**

### **1. Prerequisites**
- Python 3.8+
- Node.js 16+
- Groq API key

### **2. Backend Setup**
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your_groq_api_key_here"

# Run the server
python -m uvicorn api.main:app --reload
```

### **3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install lucide-react react-hot-toast react-dropzone

# Start development server
npm start
```

### **4. Access the System**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
DEFAULT_MODEL=llama3-8b-8192  # Fast, balanced, or powerful
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=INFO
```

### **Available Groq Models**
- **Fast**: `llama3-8b-8192` - Quick responses, good for real-time
- **Balanced**: `mixtral-8x7b-32768` - Balanced performance
- **Powerful**: `llama3-70b-8192` - Most capable, slower

## 📊 **API Endpoints**

### **Recommendations**
```bash
POST /api/v1/recommend
{
  "member_name": "John Doe",
  "role": "Data Engineer",
  "skills": ["Python", "SQL", "Airflow"],
  "recommendation_type": "upskill",
  "years_experience": 3
}
```

### **Trends**
```bash
GET /api/v1/trends/{role}
# Returns current industry trends for a specific role
```

### **Team Upload**
```bash
POST /api/v1/ingest/team/file
# Upload CSV/JSON team data
```

## 🎯 **How It Works**

### **1. Real-Time Data Collection**
The system continuously fetches data from multiple sources:
- **GitHub Trending** - Popular repositories and technologies
- **Tech Blogs** - Industry insights and best practices
- **Learning Platforms** - Course popularity and demand
- **Job Market** - Hiring trends and skill requirements
- **AI Research** - Emerging technologies and breakthroughs

### **2. Dynamic Analysis**
- **Relevance Scoring** - Ranks trends by relevance to role and skills
- **Market Demand** - Analyzes job market demand for skills
- **Growth Potential** - Identifies emerging and trending skills
- **Cross-Role Opportunities** - Finds adjacent role skills

### **3. AI-Powered Recommendations**
- **Groq LLMs** - Uses open-source models for analysis
- **Context-Aware** - Considers current skills and experience
- **Trend-Driven** - Recommendations based on live market data
- **Personalized** - Tailored to individual career goals

### **4. Learning Paths**
- **Structured Steps** - Clear learning progression
- **Time Estimates** - Realistic time commitments
- **Resource Links** - Relevant learning materials
- **Priority Levels** - High, medium, low priority skills

## 📈 **Example Output**

```json
{
  "member_name": "Sarah Chen",
  "recommendation_type": "upskill",
  "recommendations": [
    {
      "skill_name": "Apache Airflow",
      "description": "Essential for modern data engineering workflows",
      "priority": "High",
      "learning_path": [
        "Learn Airflow fundamentals",
        "Practice with real data pipelines",
        "Master advanced scheduling"
      ],
      "estimated_time": "4-6 weeks",
      "market_demand": "High",
      "trend_relevance": "Growing adoption in data engineering",
      "source_evidence": ["GitHub trending", "Job market analysis"]
    }
  ],
  "reasoning": "Based on current industry trends showing 25% growth in Airflow adoption",
  "context_sources": ["github: 15 items", "blogs: 8 items", "job_market: 12 items"]
}
```

## 🔍 **Data Sources**

### **GitHub Trends**
- Trending repositories by language
- Popular frameworks and tools
- Developer activity patterns

### **Tech Blogs**
- Role-specific insights
- Industry best practices
- Emerging technology coverage

### **Learning Platforms**
- Course enrollment trends
- Skill demand metrics
- Learning path popularity

### **Job Market**
- Skill requirement analysis
- Salary trend data
- Hiring demand patterns

## 🛠️ **Development**

### **Adding New Data Sources**
1. Extend `TrendAnalyzer` class
2. Implement new fetch method
3. Add to comprehensive trends gathering
4. Update relevance scoring

### **Customizing Models**
```python
# Switch to different Groq model
agent.switch_model("powerful")  # Use Llama 3 70B
```

### **Extending Recommendations**
- Add new recommendation types
- Customize prompt templates
- Implement role-specific logic

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details

## 🆘 **Support**

- **Issues**: GitHub Issues
- **Documentation**: API docs at `/docs`
- **Health Check**: `/health` endpoint

---

**Built with ❤️ using Groq's open-source LLMs and real-time industry data** 

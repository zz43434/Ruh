# Ruh - Islamic Spiritual Wellness Platform

**Ruh** (Arabic: روح - meaning "soul" or "spirit") is a comprehensive AI-powered Islamic spiritual wellness platform that provides intelligent conversations, semantic Quranic verse search, and personalized spiritual guidance through modern technology.

## 🌟 Project Overview

Ruh combines artificial intelligence with Islamic teachings to create a holistic spiritual wellness experience. The platform consists of three main components:

- **Backend API**: Flask-based REST API with AI integration and vector search capabilities
- **Frontend Mobile App**: React Native cross-platform mobile application
- **Vector Database**: Qdrant-powered semantic search for 6,236+ Quranic verses

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Native  │    │   Flask API     │    │   PostgreSQL    │
│   Frontend      │◄──►│   Backend       │◄──►│   Database      │
│   (Mobile App)  │    │   (REST API)    │    │   (User Data)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Qdrant        │    │   Groq API      │
                       │   Vector DB     │    │   (AI/LLM)      │
                       │   (Embeddings)  │    │   (Chat & NLP)  │
                       └─────────────────┘    └─────────────────┘
```

## ✨ Key Features

### 🤖 AI-Powered Spiritual Guidance
- Natural language conversations with Islamic context
- Personalized spiritual advice and recommendations
- Intelligent verse suggestions based on user needs
- Groq API integration for advanced language processing

### 🔍 Semantic Verse Search
- RAG-based search across 6,236+ Quranic verses
- 768-dimensional vector embeddings using sentence transformers
- Theme-based chapter discovery with contextual scoring
- Intelligent verse recommendations with similarity matching

### 📱 Cross-Platform Mobile Experience
- Native iOS and Android support via React Native
- Modern, intuitive UI with Islamic design elements
- Offline capabilities for core features
- Comprehensive verse library with all 114 Surahs

### 📊 Wellness Tracking
- Spiritual and emotional well-being monitoring
- Progress tracking with AI-powered insights
- Personalized recommendations based on user patterns
- Historical data analysis and trends

### 🔧 Technical Excellence
- Docker containerization for seamless deployment
- PostgreSQL for reliable data persistence
- Qdrant vector database for high-performance search
- Rate limiting and security features
- Comprehensive API documentation

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask (Python 3.11+)
- **Database**: PostgreSQL 15+
- **Vector Search**: Qdrant
- **AI/LLM**: Groq API
- **Embeddings**: Sentence Transformers
- **ORM**: SQLAlchemy with Alembic migrations
- **Containerization**: Docker & Docker Compose

### Frontend
- **Framework**: React Native with Expo
- **Language**: TypeScript
- **Navigation**: React Navigation
- **State Management**: React Query
- **Storage**: Async Storage
- **API Client**: Apisauce
- **Internationalization**: i18next

### Infrastructure
- **Vector Database**: Qdrant (latest)
- **Database**: PostgreSQL 15
- **Deployment**: Docker Compose
- **Development**: Hot reload and debugging support

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Groq API key
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Ruh
```

### 2. Backend Setup
```bash
cd ruh-backend
cp .env.example .env
# Edit .env with your Groq API key and other configurations
```

### 3. Start the Backend Services
```bash
# From the root directory
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Qdrant vector database on port 6333
- Flask API on port 5000

### 4. Frontend Setup
```bash
cd ruh-frontend
npm install
npm start
```

## 📚 API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `POST /chat` - AI-powered chat interface
- `GET /chat/init` - Get welcome message

### Verse & Chapter Search
- `GET /chapters` - List all Quranic chapters
- `GET /chapters/<surah_number>` - Get specific chapter details
- `GET|POST /chapters/search` - Semantic chapter search by theme
- `POST /verses/search` - Search verses by theme or keyword
- `GET /verses/random` - Get random verse

### Wellness & Progress
- `GET /wellness` - Get wellness history and stats
- `POST /wellness/checkin` - Submit wellness check-in
- `POST /wellness/ai-analysis` - Get AI-powered wellness analysis
- `DELETE /wellness/clear` - Clear user wellness data

### Conversations
- `GET /conversations` - Get conversation history
- `GET /conversations/<id>` - Get specific conversation
- `DELETE /conversations/clear` - Clear conversation history

### Translation
- `POST /translate` - Translate Arabic text to English

## 🔧 Development

### Backend Development
```bash
cd ruh-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Frontend Development
```bash
cd ruh-frontend
npm install
npm start
# Use Expo Go app or simulator to test
```

### Database Migrations
```bash
cd ruh-backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## 🧪 Testing

### Backend Tests
```bash
cd ruh-backend
python -m pytest tests/
```

### API Testing
```bash
# Test endpoints
python test_endpoint.py
```

## 📦 Deployment

### Production Deployment
```bash
# Update environment variables for production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
Key environment variables to configure:
- `GROQ_API_KEY`: Your Groq API key
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key
- `QDRANT_HOST`: Qdrant server host
- `FLASK_ENV`: Environment (development/production)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Quranic text and translations from authentic sources
- Islamic scholars and communities for guidance
- Open source community for tools and libraries
- Groq for AI/LLM capabilities
- Qdrant for vector search technology

---

**May this project serve as a means of spiritual benefit and guidance for the Muslim community. Barakallahu feekum.**
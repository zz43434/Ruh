# Ruh Backend

A Flask-based backend API for **Ruh** (Arabic: روح - meaning "soul" or "spirit"), providing AI-powered Islamic spiritual guidance through intelligent conversations and semantic Quranic verse search.

## 🌟 Features

- **AI-powered chat interface** using Groq API for natural language processing
- **RAG-based semantic verse search** using sentence transformers and Qdrant vector database
- **Intelligent verse recommendations** with similarity scoring and contextual matching
- **Vector embeddings** for 6,236+ Quranic verses with 768-dimensional representations
- **Conversation history management** with PostgreSQL persistence
- **Wellness progress tracking** for spiritual journey monitoring
- **Multi-endpoint API** with rate limiting and security features
- **Docker containerization** for seamless deployment
- **Qdrant integration** for high-performance vector search

## 🛠️ Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (for containerized deployment)
- Groq API key
- **Qdrant** (vector database for embeddings)
- **Sentence Transformers** (for RAG embeddings)
- **scikit-learn** (for vector similarity calculations)

## 🚀 Setup

### 1. Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=true

# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ruh_db

# Groq API Configuration
GROQ_API_KEY=your-groq-api-key-here

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:19006
```

### 2. Local Development

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Database Setup

Make sure PostgreSQL is running and create the database:

```bash
createdb ruh_db
```

Run migrations:

```bash
alembic upgrade head
```

#### Initialize RAG Embeddings

Generate vector embeddings for all Quranic verses (required for semantic search):

```bash
python initialize_embeddings.py --verbose
```

This will:
- Load all 6,236 Quranic verses from 114 Surahs
- Generate embeddings using `paraphrase-multilingual-MiniLM-L12-v2` model
- Create 768-dimensional vectors for semantic understanding
- Store embeddings in Qdrant vector database
- Enable intelligent verse search functionality

**Note**: This process may take several minutes on first run. Subsequent runs will load existing embeddings unless you use the `--force` flag.

#### Start the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

### 3. Docker Development

#### Build and Run with Docker Compose

```bash
docker-compose up --build
```

This will:
- Start a PostgreSQL container
- Start a Qdrant vector database container
- Build and run the Flask application
- Run database migrations automatically
- **Initialize RAG embeddings automatically**
- Expose the API on port 5000

## 📡 API Endpoints

### Chat
- `POST /api/chat` - Send a message to the AI assistant
- `POST /api/chat/verse-choice` - Handle user's choice about viewing verses
- `GET /api/chat/init` - Get initial welcome message

### Conversations
- `GET /api/conversations` - Get conversation history
- `GET /api/conversations/<id>` - Get specific conversation

### Verses
- `GET /api/verses` - Get all Surahs (chapters) overview
- `GET /api/verses/search` - Search verses by topic (uses semantic RAG search)
- `GET /api/verses/<int:surah_number>` - Get specific Surah with verses
- **Semantic Search**: Powered by Qdrant and sentence transformers for contextual verse matching

### Wellness
- `POST /api/wellness` - Submit wellness progress
- `GET /api/wellness` - Get wellness history

### Translation
- `GET /api/translation` - Translation-related endpoints

## 🏗️ Project Structure

```
ruh-backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── core/                    # Core functionality
│   │   ├── groq_client.py       # Groq API client
│   │   ├── prompts.py           # AI prompts
│   │   └── qdrant_client.py     # Qdrant vector database client
│   ├── models/                  # Database models
│   │   ├── database.py          # Database configuration
│   │   ├── conversation.py      # Conversation models
│   │   └── wellness_progress.py # Wellness tracking models
│   ├── routes/                  # API endpoints
│   │   ├── chat.py              # Chat and verse choice endpoints
│   │   ├── conversations.py     # Conversation management
│   │   ├── verses.py            # Verse search and retrieval
│   │   ├── wellness.py          # Wellness tracking
│   │   └── translation.py       # Translation services
│   ├── services/                # Business logic
│   │   ├── chat_service.py      # Chat and RAG logic
│   │   ├── conversation_service.py # Conversation management
│   │   ├── verse_service.py     # Verse search and retrieval
│   │   ├── embedding_service.py # RAG embeddings management
│   │   ├── vector_store.py      # Vector similarity search
│   │   └── wellness_service.py  # Wellness tracking logic
│   └── utils/                   # Utility functions
│       ├── error_handlers.py    # Error handling
│       ├── helpers.py           # Helper functions
│       └── logging_config.py    # Logging configuration
├── migrations/                  # Database migrations
├── tests/                       # Test files
│   ├── test_rag.py             # RAG system testing
│   ├── compare_search_methods.py # Search comparison tools
│   └── test_services/          # Service-specific tests
├── initialize_embeddings.py    # RAG setup script
├── test_endpoint.py            # API endpoint testing
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
└── run.py                      # Application entry point
```

## 🗄️ Database Schema

### Conversations
- `id` (String, Primary Key)
- `user_id` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `status` (String)

### Messages
- `id` (String, Primary Key)
- `conversation_id` (String, Foreign Key)
- `sender` (String)
- `content` (Text)
- `timestamp` (DateTime)

### Wellness Progress
- `id` (Integer, Primary Key)
- `user_id` (String)
- `mood` (String)
- `energy_level` (Integer)
- `stress_level` (Integer)
- `notes` (Text)
- `analysis` (Text)

## 🤖 RAG System Architecture

### Vector Database (Qdrant)
- **6,236 Quranic verses** indexed with 768-dimensional embeddings
- **Semantic similarity search** using cosine similarity
- **Sub-500ms response times** for real-time spiritual guidance
- **Multilingual support** for Arabic and English queries

### AI Pipeline
1. **Sentiment Analysis**: Groq API analyzes user emotional state
2. **Context Collection**: Last 5 user messages for conversation context
3. **Emotional Analysis**: Deeper understanding of user's spiritual needs
4. **Vector Search**: Qdrant finds semantically similar verses
5. **Response Generation**: Groq creates contextual, empathetic responses

## 🧪 Development

### RAG System Testing

Test the semantic search functionality:

```bash
# Test RAG implementation
python test_rag.py

# Compare semantic vs keyword search
python compare_search_methods.py

# Test API endpoints
python test_endpoint.py

# Regenerate embeddings (if needed)
python initialize_embeddings.py --force
```

### Running Tests

```bash
python -m pytest tests/
```

### Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:

```bash
alembic upgrade head
```

### Code Style

The project follows PEP 8 style guidelines. Use tools like `black` and `flake8` for code formatting and linting.

## 🚀 Deployment

### Production Environment

1. Set `FLASK_ENV=production` in your environment variables
2. Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

3. Configure a reverse proxy (nginx) for better performance
4. Use environment variables for sensitive configuration
5. Set up proper logging and monitoring
6. Ensure Qdrant is running and accessible

### Docker Production

Build production image:

```bash
docker build -t ruh-backend:latest .
```

Run with production settings:

```bash
docker run -d \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=your-production-db-url \
  -e GROQ_API_KEY=your-api-key \
  -e QDRANT_HOST=your-qdrant-host \
  ruh-backend:latest
```

## 📊 Performance Metrics

- **Vector Search**: Sub-500ms response times
- **Database**: 6,236+ verses indexed with full metadata
- **Embeddings**: 768-dimensional vectors for semantic understanding
- **Model**: `paraphrase-multilingual-MiniLM-L12-v2` for Arabic-English support
- **Similarity Threshold**: Configurable (default: 0.1 for broader guidance)

## 🌍 Real-World Impact

- **Target Audience**: 1.8+ billion Muslims seeking digital spiritual guidance
- **Use Cases**: Daily reflection, crisis support, Islamic learning, wellness tracking
- **Accessibility**: Makes Quranic wisdom discoverable through natural language
- **24/7 Availability**: Instant access to Islamic guidance and comfort

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
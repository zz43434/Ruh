# Ruh Backend

A Flask-based backend API for the Ruh application, providing Islamic spiritual guidance through AI-powered conversations and Quranic verses.

## Features

- AI-powered chat interface using Groq API
- Quranic verse matching and recommendations
- Conversation history management
- Wellness progress tracking
- Rate limiting and security features
- PostgreSQL database with SQLAlchemy ORM
- Docker containerization

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker and Docker Compose (for containerized deployment)
- Groq API key

## Setup

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

# Rate Limiting
RATELIMIT_DEFAULT=200 per day;50 per hour

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
- Build and run the Flask application
- Run database migrations automatically
- Expose the API on port 5000

## API Endpoints

### Chat
- `POST /api/chat` - Send a message to the AI assistant
- `GET /api/chat/init` - Get initial welcome message

### Conversations
- `GET /api/conversations` - Get conversation history
- `GET /api/conversations/<id>` - Get specific conversation

### Verses
- `GET /api/verses` - Get Quranic verses
- `GET /api/verses/search` - Search verses by topic

### Wellness
- `POST /api/wellness` - Submit wellness progress
- `GET /api/wellness` - Get wellness history

## Project Structure

```
ruh-backend/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration settings
│   ├── core/                # Core functionality
│   │   ├── groq_client.py   # Groq API client
│   │   └── prompts.py       # AI prompts
│   ├── models/              # Database models
│   │   ├── database.py      # Database configuration
│   │   ├── conversation.py  # Conversation models
│   │   └── wellness_progress.py
│   ├── routes/              # API endpoints
│   │   ├── chat.py
│   │   ├── conversations.py
│   │   ├── verses.py
│   │   └── wellness.py
│   ├── services/            # Business logic
│   │   ├── chat_service.py
│   │   ├── conversation_service.py
│   │   ├── verse_service.py
│   │   └── wellness_service.py
│   └── utils/               # Utility functions
│       ├── error_handlers.py
│       ├── helpers.py
│       └── logging_config.py
├── migrations/              # Database migrations
├── tests/                   # Test files
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Docker image definition
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Database Schema

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

## Development

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

## Deployment

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
  ruh-backend:latest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License.
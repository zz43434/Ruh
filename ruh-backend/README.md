# ruh-backend

## Overview
The `ruh-backend` project is a backend application designed to handle various functionalities related to chat, verses, wellness, and conversations. It is structured to facilitate easy maintenance and scalability.

## Project Structure
```
ruh-backend/
├── app/                     # Main application package
│   ├── __init__.py         # Initializes the app package
│   ├── routes/              # Contains route handlers
│   │   ├── __init__.py     # Initializes the routes package
│   │   ├── chat.py         # Chat-related route handlers
│   │   ├── verses.py       # Verse-related route handlers
│   │   ├── wellness.py     # Wellness-related route handlers
│   │   └── conversations.py # Conversation-related route handlers
│   ├── services/           # Contains business logic
│   │   ├── __init__.py     # Initializes the services package
│   │   ├── chat_service.py  # Chat business logic
│   │   ├── verse_service.py  # Verse business logic
│   │   ├── wellness_service.py # Wellness business logic
│   │   └── conversation_service.py # Conversation business logic
│   ├── models/             # Contains data models
│   │   ├── __init__.py     # Initializes the models package
│   │   ├── response_generator.py # Response generation logic
│   │   ├── verse_matcher.py # Verse matching logic
│   │   └── sentiment_analyzer.py # Sentiment analysis logic
│   ├── core/               # Core infrastructure
│   │   ├── __init__.py     # Initializes the core package
│   │   ├── groq_client.py   # Groq client singleton
│   │   └── prompts.py       # Prompt templates
│   ├── data/               # Data files
│   │   ├── quran_analysis.json # Quran analysis data
│   │   └── embeddings.npy   # Embeddings data
│   ├── utils/              # Utility functions
│   │   ├── __init__.py     # Initializes the utils package
│   │   ├── helpers.py      # Helper functions
│   │   ├── logging_config.py # Logging configuration
│   │   └── error_handlers.py # Error handling utilities
│   └── config.py           # Configuration settings
├── tests/                  # Test suite
│   ├── __init__.py         # Initializes the tests package
│   ├── test_services/      # Tests for service layer
│   └── test_routes/        # Tests for route handlers
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables
├── run.py                  # Entry point to run the application
└── README.md               # Project documentation
```

## Installation
To install the required dependencies, run:
```
pip install -r requirements.txt
```

## Usage
To start the application, run:
```
python run.py
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
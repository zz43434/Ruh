class Config:
    DEBUG = True  # Set to False in production
    TESTING = False
    DATABASE_URI = 'sqlite:///app.db'  # Example database URI
    SECRET_KEY = 'your_secret_key'  # Change this to a random secret key
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Allowed hosts for the application
    LOGGING_LEVEL = 'INFO'  # Set logging level
    JSON_SORT_KEYS = False  # Do not sort keys in JSON responses

    @staticmethod
    def init_app(app):
        pass  # Initialize app with configuration settings if needed
from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config

limiter = Limiter(key_func=get_remote_address)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Initialize rate limiting
    limiter.init_app(app)
    
    # Register blueprints
    from .routes.chat import chat_bp
    from .routes.verses import verses_bp
    from .routes.wellness import wellness_bp
    from .routes.conversations import conversations_bp
    
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(verses_bp, url_prefix='/api')
    app.register_blueprint(wellness_bp, url_prefix='/api')
    app.register_blueprint(conversations_bp, url_prefix='/api')
    
    # Register error handlers
    from .utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app
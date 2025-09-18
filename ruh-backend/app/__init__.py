from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    cors_origins = Config.CORS_ORIGINS if Config.CORS_ORIGINS and Config.CORS_ORIGINS != [''] else "*"
    CORS(app, origins=cors_origins)
    
    # Initialize database
    from .models import init_db
    with app.app_context():
        init_db()
    
    # Register blueprints
    from .routes.chat import chat_bp
    from .routes.verses import verses_bp
    from .routes.wellness import wellness_bp
    from .routes.conversations import conversations_bp
    from .routes.translation import translation_bp
    
    app.register_blueprint(chat_bp, url_prefix='/api')
    app.register_blueprint(verses_bp, url_prefix='/api')
    app.register_blueprint(wellness_bp, url_prefix='/api')
    app.register_blueprint(conversations_bp, url_prefix='/api')
    app.register_blueprint(translation_bp, url_prefix='/api')
    
    # Register error handlers
    from .utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app
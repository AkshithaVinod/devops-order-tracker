from flask import Flask
from flask_cors import CORS
from app.database import db, init_db

def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    if config:
        app.config.update(config)
    
    # Initialize extensions
    CORS(app)
    init_db(app)
    
    # Register blueprints
    from app.main import api_bp
    app.register_blueprint(api_bp)
    
    return app
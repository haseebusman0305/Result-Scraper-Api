from flask import Flask
from flask_cors import CORS
import os
from config import Config
from .api import api


def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.update(
        DEBUG=os.getenv("DEBUG", "False").lower() == "true",
        ENVIRONMENT=os.getenv("ENVIRONMENT", "production"),
        HOST=os.getenv("HOST", "0.0.0.0"),
        PORT=int(os.getenv("PORT", 8000)),
    )

    # Enable CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "https://uaf-cgpa-frontend.azurewebsites.net",
                    "http://localhost:3000",
                ],
                "supports_credentials": False,
            }
        },
    )

    # Register blueprints
    app.register_blueprint(api, url_prefix="/api")

    return app

from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from config import Config
from .api import api
import logging
import traceback

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Load configuration from Config class
    app.config.update(
        DEBUG=Config.DEBUG,
        ENVIRONMENT=Config.ENVIRONMENT,
        HOST=Config.HOST,
        PORT=Config.PORT,
    )

    # Enable CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    "https://uafcalculator.live",
                    "http://localhost:3000",
                ],
                "supports_credentials": False,
            }
        },
    )

    # Root endpoint
    @app.route('/')
    def index():
        return {
            'status': 'online',
            'message': 'UAF Calculator API is running'
        }

    # Favicon handler
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    # Register blueprints
    app.register_blueprint(api, url_prefix="/api")

    @app.errorhandler(Exception)
    def handle_error(error):
        logger.error(f"Unhandled error: {str(error)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return {
            'error': str(error),
            'status': 'error'
        }, 500

    # Log startup information
    logger.info(f"Application starting in {app.config['ENVIRONMENT']} mode")
    logger.info(f"Debug mode: {app.config['DEBUG']}")

    return app

from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitation : 16 MB
    from app.routes import main
    app.register_blueprint(main)
    return app
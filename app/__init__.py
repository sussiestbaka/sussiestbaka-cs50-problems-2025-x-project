from flask import Flask
from config import Config
from .extensions import db
from .auth import auth
from .dashboard import dashboard
from .camera import camera_preview
from flask_file_explorer.file_explorer import file_explorer_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["FFE_BASE_DIRECTORY"] = '/path/to/your/directory'

    db.init_app(app)
    
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(camera_preview)
    app.register_blueprint(file_explorer_bp, url_prefix='/file-explorer')

    return app

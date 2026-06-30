from flask import Flask, render_template, url_for
from config import DevelopmentConfig

def create_app():
    # 1) setup app
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)    

    # 2) import blueprints
    from app.blueprints.user.routes import user_bp

    # 3) register blueprints
    app.register_blueprint(user_bp, url_prefix='/user')

    return app




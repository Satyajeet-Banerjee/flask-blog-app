from flask import Flask
import os
from config import Config, DevelopmentConfig, ProductionConfig
from app.extensions import db, bootstrap, ckeditor, login_manager, mail
from app.models import User
from app.routes import register_routes
from app.utils import gravatar_url


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    if os.getenv("FLASK_ENV") == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    bootstrap.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.jinja_env.globals["gravatar_url"] = gravatar_url

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app
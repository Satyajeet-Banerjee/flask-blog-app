from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from flask_mail import Mail

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
bootstrap = Bootstrap5()
ckeditor = CKEditor()
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "warning"
mail = Mail()
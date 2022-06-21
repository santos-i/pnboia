from flask_login import LoginManager
from application.models import User

login_manager = LoginManager()


def init_app(app):
    login_manager.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

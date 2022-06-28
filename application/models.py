from application.extensions.database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__= 'user'
    username = db.Column(db.String(140), primary_key=True)
    password = db.Column(db.String(512))
    authenticated = db.Column(db.Boolean, default=False)
    
    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
    
    def check_password(self,password):
        if self.password == password:
            return True
        return False
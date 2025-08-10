from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    password = db.Column(db.String(150), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)

    def _repr__(self):
        # classe debug
        return f"<User {self.email}>"

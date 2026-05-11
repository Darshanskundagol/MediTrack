"""models_db.py — SQLAlchemy ORM models for Meditrack"""
from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="pharmacist")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.username}>"


class PredictionLog(db.Model):
    __tablename__ = "prediction_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    filename = db.Column(db.String(200))
    total_records = db.Column(db.Integer)
    high_risk = db.Column(db.Integer)
    slow_moving = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

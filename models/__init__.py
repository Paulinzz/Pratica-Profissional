from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    name = db.Column(db.String(150), nullable=True)
    photo = db.Column(db.String(255), nullable=True)
    materias = db.relationship("Materia", backref="usuario", lazy=True)
    atividades = db.relationship("Atividade", backref="usuario", lazy=True)


class Materia(db.Model):
    __tablename__ = "tb_materias"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Atividade(db.Model):
    __tablename__ = "tb_atividades"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    materia = db.Column(db.String(100), nullable=False)
    assunto_primario = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    duracao = db.Column(db.String(10), nullable=True)
    data = db.Column(db.Date, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

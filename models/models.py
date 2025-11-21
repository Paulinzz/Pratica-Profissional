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
    reset_token = db.Column(db.String(100), nullable=True)
    reset_expires = db.Column(db.DateTime, nullable=True)
    tema_escuro = db.Column(db.Boolean, default=False)
    notificacoes_email = db.Column(db.Boolean, default=True)
    notificacoes_push = db.Column(db.Boolean, default=False)
    lembretes = db.Column(db.Boolean, default=True)
    idioma = db.Column(db.String(10), default="pt-br")
    materias = db.relationship("Materia", backref="usuario", lazy=True)
    atividades = db.relationship("Atividade", backref="usuario", lazy=True)
    metas = db.relationship("Meta", backref="usuario", lazy=True)
    badges = db.relationship("UserBadge", backref="usuario", lazy=True)
    notificacoes = db.relationship(
        "Notificacao", backref="usuario", lazy=True, cascade="all, delete-orphan"
    )


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


class Notificacao(db.Model):
    __tablename__ = "tb_notificacoes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    tipo = db.Column(
        db.String(50), nullable=False
    )  # 'lembrete', 'conquista', 'sistema'
    titulo = db.Column(db.String(200), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(255), nullable=True)  # URL para redirecionar
    icone = db.Column(db.String(50), default="fa-bell")  # Ícone Font Awesome


class Meta(db.Model):
    __tablename__ = "tb_metas"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_limite = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="ativo")  # 'ativo', 'concluido'
    materia_id = db.Column(db.Integer, db.ForeignKey("tb_materias.id"), nullable=True)
    materia = db.relationship("Materia", backref="metas", lazy=True)


class Badge(db.Model):
    __tablename__ = "tb_badges"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    icone = db.Column(db.String(50), nullable=False)  # FontAwesome icon
    categoria = db.Column(
        db.String(50), nullable=False
    )  # 'atividade', 'meta', 'tempo', etc.
    criterio = db.Column(db.String(100), nullable=False)  # Condition to earn
    pontos = db.Column(db.Integer, default=10)


class UserBadge(db.Model):
    __tablename__ = "tb_user_badges"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("tb_badges.id"), nullable=False)
    data_conquista = db.Column(db.DateTime, default=datetime.utcnow)
    badge = db.relationship("Badge", backref="user_badges", lazy=True)

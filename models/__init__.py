from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import enum

db = SQLAlchemy()


class StatusAtividade(enum.Enum):
    Pendente = "Pendente"
    Atrasada = "Atrasada"
    Em_andamento = "Em andamento"
    Concluida = "Concluída"


class Usuario(db.Model, UserMixin):
    __tablename__ = "tb_usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_usuario = db.Column(db.String(255), nullable=False)
    email_usuario = db.Column(db.String(320), nullable=False, unique=True)
    senha_usuario = db.Column(db.String(255), nullable=False)
    criacao_usuario = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())

    # Relação com tb_materias (um usuário tem várias matérias)
    materias = db.relationship(
        "Materia", backref="usuario", lazy=True, cascade="all, delete-orphan"
    )

    def get_id(self):
        return str(self.id_usuario)

    def __repr__(self):
        return f"<Usuario {self.nome_usuario}>"


class Materia(db.Model):
    __tablename__ = "tb_materias"

    id_mat = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_mat = db.Column(db.String(255), nullable=False)
    data_adicao_mat = db.Column(db.DateTime, default=db.func.current_timestamp())
    descricao_mat = db.Column(db.Text)
    assunto_atual_mat = db.Column(db.Text)
    id_usu_mat = db.Column(
        db.Integer,
        db.ForeignKey("tb_usuarios.id_usuario", ondelete="CASCADE"),  # <-- removido o espaço extra
        nullable=False,
    )

    # Relação com tb_atividades (uma matéria tem várias atividades)
    atividades = db.relationship(
        "Atividade", backref="materia", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Materia {self.nome_mat}>"


class Atividade(db.Model):
    __tablename__ = "tb_atividades"

    id_ati = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_ati = db.Column(db.String(255), nullable=False)
    data_cadastro_ati = db.Column(db.DateTime, default=db.func.current_timestamp())
    data_conclusao_ati = db.Column(db.Date, nullable=False)
    status_ati = db.Column(db.Enum(StatusAtividade), nullable=False)
    id_mat_ati = db.Column(
        db.Integer,
        db.ForeignKey("tb_materias.id_mat", ondelete="CASCADE"),
        nullable=False,
    )

    def __repr__(self):
        return f"<Atividade {self.nome_ati}>"

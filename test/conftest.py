import pytest
import sys
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar variáveis de ambiente antes de importar app
import os
os.environ['TESTING'] = 'True'

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_mail import Mail

from models.models import db, User
from config.logging_config import setup_logging


@pytest.fixture(scope="session")
def test_app():
    """Cria aplicação Flask para testes com SQLite em memória"""
    app = Flask(__name__)

    # Configurações de teste
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = "test-secret-key-123"
    app.config["MAIL_SUPPRESS_SEND"] = True

    # Inicializar extensões
    db.init_app(app)
    bcrypt = Bcrypt(app)
    mail = Mail(app)
    CSRFProtect(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Setup logging
    setup_logging(app)

    with app.app_context():
        db.create_all()

    return app


@pytest.fixture(scope="function")
def client(test_app):
    """Cliente de teste para fazer requisições HTTP"""
    with test_app.app_context():
        db.create_all()
        yield test_app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def runner(test_app):
    """CLI runner para testes de linha de comando"""
    return test_app.test_cli_runner()


@pytest.fixture(scope="function")
def db_session(test_app):
    """Sessão do banco de dados para testes"""
    with test_app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def test_user(db_session, test_app):
    """Cria um usuário de teste padrão"""
    with test_app.app_context():
        bcrypt = Bcrypt(test_app)
        hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

        user = User(
            name="Test User",
            email="test@example.com",
            password=hashed_password,
            tema_escuro=False,
            notificacoes_email=True,
        )
        db_session.session.add(user)
        db_session.session.commit()
        return user


@pytest.fixture(scope="function")
def authenticated_client(client, test_user, test_app):
    """Cliente autenticado (login já feito)"""
    with test_app.app_context():
        from flask_login import login_user
        login_user(test_user)
    return client


@pytest.fixture(scope="function")
def csrf_token(test_app):
    """Gera um token CSRF válido para testes"""
    with test_app.app_context():
        return generate_csrf()

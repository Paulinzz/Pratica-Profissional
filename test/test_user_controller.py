import pytest
from pathlib import Path
import sys
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from controllers.user_controller import init_user_routes
from models.models import User, db


@pytest.fixture
def app():
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(__name__, template_folder=str(project_root / "templates"))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["WTF_CSRF_ENABLED"] = True

    db.init_app(app)
    bcrypt = Bcrypt(app)
    CSRFProtect(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/_csrf")
    def csrf_token_endpoint():
        return generate_csrf()

    init_user_routes(app, bcrypt)

    with app.app_context():
        db.create_all()
        user = User(
            name="Usuario Teste",
            email="teste@example.com",
            password=bcrypt.generate_password_hash("Senha@123").decode("utf-8"),
        )
        db.session.add(user)
        db.session.commit()

    return app


@pytest.fixture
def client(app):
    return app.test_client()


def login_user_session(client, user_id):
    with client.session_transaction() as session:
        session["_user_id"] = str(user_id)
        session["_fresh"] = True


def get_csrf_token(client):
    response = client.get("/_csrf")
    return response.get_data(as_text=True)


def post_form_with_csrf(client, url, data):
    token = get_csrf_token(client)
    data = dict(data)
    data["csrf_token"] = token
    return client.post(url, data=data, follow_redirects=False)


def post_json_with_csrf(client, url, payload):
    token = get_csrf_token(client)
    return client.post(
        url,
        json=payload,
        headers={"X-CSRFToken": token},
    )


def test_atualizar_perfil_rejeita_email_invalido(client, app):
    with app.app_context():
        user = User.query.filter_by(email="teste@example.com").first()
        user_id = user.id

    login_user_session(client, user_id)
    response = post_form_with_csrf(
        client,
        "/atualizar_perfil",
        {"nome": "Usuario Válido", "email": "email-invalido"},
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.get(user_id)
        assert user.email == "teste@example.com"


def test_atualizar_perfil_rejeita_nome_invalido(client, app):
    with app.app_context():
        user = User.query.filter_by(email="teste@example.com").first()
        user_id = user.id

    login_user_session(client, user_id)
    response = post_form_with_csrf(
        client,
        "/atualizar_perfil",
        {"nome": "A", "email": "novo@example.com"},
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.get(user_id)
        assert user.name == "Usuario Teste"


def test_alterar_senha_rejeita_senha_fraca(client, app):
    with app.app_context():
        user = User.query.filter_by(email="teste@example.com").first()
        user_id = user.id
        old_hash = user.password

    login_user_session(client, user_id)
    response = post_form_with_csrf(
        client,
        "/alterar_senha",
        {
            "senha_atual": "Senha@123",
            "nova_senha": "fraca",
            "confirmar_senha": "fraca",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.get(user_id)
        assert user.password == old_hash


def test_alterar_senha_com_senha_valida(client, app):
    with app.app_context():
        user = User.query.filter_by(email="teste@example.com").first()
        user_id = user.id
        old_hash = user.password

    login_user_session(client, user_id)
    response = post_form_with_csrf(
        client,
        "/alterar_senha",
        {
            "senha_atual": "Senha@123",
            "nova_senha": "NovaSenha@123",
            "confirmar_senha": "NovaSenha@123",
        },
    )

    assert response.status_code == 302
    with app.app_context():
        user = User.query.get(user_id)
        assert user.password != old_hash


def test_atualizar_configuracoes_exige_csrf(client, app):
    with app.app_context():
        user = User.query.filter_by(email="teste@example.com").first()
        user_id = user.id

    login_user_session(client, user_id)
    response = client.post(
        "/atualizar_configuracoes",
        json={"notificacoes_email": False},
    )
    assert response.status_code == 400


def test_atualizar_configuracoes_com_csrf(client, app):
    with app.app_context():
        user = User.query.filter_by(email="teste@example.com").first()
        user_id = user.id

    login_user_session(client, user_id)
    response = post_json_with_csrf(
        client,
        "/atualizar_configuracoes",
        {"notificacoes_email": False, "notificacoes_push": True, "lembretes": True},
    )

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True

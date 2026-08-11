import pytest
from flask_login import current_user
from models.models import User, db


class TestRegisterRoute:
    """Testes para a rota de registro"""

    @pytest.mark.auth
    def test_register_get_page(self, client):
        """Testa se a página de registro carrega com GET"""
        response = client.get("/cadastro")
        assert response.status_code == 200

    @pytest.mark.auth
    def test_register_sucesso(self, client):
        """Testa registro bem-sucedido"""
        response = client.post(
            "/cadastro",
            data={
                "name": "Novo Usuario",
                "email": "novo@example.com",
                "password": "SecurePass123!",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        user = User.query.filter_by(email="novo@example.com").first()
        assert user is not None
        assert user.name == "Novo Usuario"

    @pytest.mark.auth
    def test_register_email_duplicado(self, client, test_user):
        """Testa registro com email já existente"""
        response = client.post(
            "/cadastro",
            data={
                "name": "Outro Usuario",
                "email": test_user.email,
                "password": "SecurePass123!",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "cadastrado" in response_text.lower()

    @pytest.mark.auth
    @pytest.mark.parametrize(
        "name,email,password,erro_esperado",
        [
            ("", "test@example.com", "Pass123!", "nome"),
            ("Jo", "test@example.com", "Pass123!", "nome"),
            ("User", "invalid-email", "Pass123!", "email"),
            ("User", "test@example.com", "short", "senha"),
            ("User", "test@example.com", "NoUpper123!", "senha"),
        ],
    )
    def test_register_validacoes(self, client, name, email, password, erro_esperado):
        """Testa validações no registro"""
        response = client.post(
            "/cadastro",
            data={"name": name, "email": email, "password": password},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert User.query.filter_by(email=email).first() is None

    @pytest.mark.auth
    def test_register_rate_limit(self, client):
        """Testa rate limiting no registro"""
        for i in range(3):
            response = client.post(
                "/cadastro",
                data={
                    "name": f"User{i}",
                    "email": f"user{i}@example.com",
                    "password": "SecurePass123!",
                },
                follow_redirects=False,
            )
            assert response.status_code in [200, 302]

        response = client.post(
            "/cadastro",
            data={
                "name": "User4",
                "email": "user4@example.com",
                "password": "SecurePass123!",
            },
            follow_redirects=True,
        )

        response_text = response.data.decode('utf-8', errors='ignore')
        assert "tentativas" in response_text.lower()


class TestLoginRoute:
    """Testes para a rota de login"""

    @pytest.mark.auth
    def test_login_get_page(self, client):
        """Testa se a página de login carrega com GET"""
        response = client.get("/login")
        assert response.status_code == 200

    @pytest.mark.auth
    def test_login_sucesso(self, client, test_user):
        """Testa login bem-sucedido"""
        response = client.post(
            "/login",
            data={"email": test_user.email, "password": "TestPass123!"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        with client:
            client.get("/")
            assert current_user.is_authenticated

    @pytest.mark.auth
    def test_login_email_incorreto(self, client, test_user):
        """Testa login com email incorreto"""
        response = client.post(
            "/login",
            data={"email": "incorrect@example.com", "password": "TestPass123!"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "invalido" in response_text.lower() or "inválido" in response_text.lower()

    @pytest.mark.auth
    def test_login_senha_incorreta(self, client, test_user):
        """Testa login com senha incorreta"""
        response = client.post(
            "/login",
            data={"email": test_user.email, "password": "WrongPassword123!"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "invalido" in response_text.lower() or "inválido" in response_text.lower()

    @pytest.mark.auth
    def test_login_rate_limit(self, client, test_user):
        """Testa rate limiting no login"""
        for i in range(5):
            response = client.post(
                "/login",
                data={"email": test_user.email, "password": "WrongPassword123!"},
                follow_redirects=False,
            )
            assert response.status_code in [200, 302]

        response = client.post(
            "/login",
            data={"email": test_user.email, "password": "TestPass123!"},
            follow_redirects=True,
        )

        response_text = response.data.decode('utf-8', errors='ignore')
        assert "tentativas" in response_text.lower()

    @pytest.mark.auth
    def test_login_email_invalido(self, client):
        """Testa login com email inválido"""
        response = client.post(
            "/login",
            data={"email": "invalid-email", "password": "TestPass123!"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "invalido" in response_text.lower() or "inválido" in response_text.lower()


class TestLogoutRoute:
    """Testes para a rota de logout"""

    @pytest.mark.auth
    def test_logout_autenticado(self, client, test_user):
        """Testa logout de usuário autenticado"""
        client.post(
            "/login",
            data={"email": test_user.email, "password": "TestPass123!"},
            follow_redirects=True,
        )

        response = client.get("/logout", follow_redirects=True)

        assert response.status_code == 200
        with client:
            client.get("/")
            assert not current_user.is_authenticated

    @pytest.mark.auth
    def test_logout_nao_autenticado(self, client):
        """Testa logout sem estar autenticado"""
        response = client.get("/logout", follow_redirects=True)

        assert response.status_code == 200


class TestForgotPasswordRoute:
    """Testes para recuperação de senha"""

    @pytest.mark.auth
    def test_forgot_password_get(self, client):
        """Testa carregamento da página de esqueci a senha"""
        response = client.get("/esqueci_senha")
        assert response.status_code == 200

    @pytest.mark.auth
    def test_forgot_password_usuario_existe(self, client, test_user):
        """Testa requisição de reset de senha com usuário existente"""
        response = client.post(
            "/esqueci_senha",
            data={"email": test_user.email},
            follow_redirects=True,
        )

        assert response.status_code == 200
        test_user = User.query.get(test_user.id)
        assert test_user.reset_token is not None
        assert test_user.reset_expires is not None

    @pytest.mark.auth
    def test_forgot_password_usuario_nao_existe(self, client):
        """Testa requisição de reset de senha com usuário inexistente"""
        response = client.post(
            "/esqueci_senha",
            data={"email": "nonexistent@example.com"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "email" in response_text.lower()

    @pytest.mark.auth
    def test_forgot_password_email_invalido(self, client):
        """Testa requisição de reset com email inválido"""
        response = client.post(
            "/esqueci_senha",
            data={"email": "invalid-email"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "invalido" in response_text.lower() or "inválido" in response_text.lower()


class TestResetPasswordRoute:
    """Testes para reset de senha"""

    @pytest.mark.auth
    def test_reset_password_token_valido(self, client, test_user):
        """Testa reset de senha com token válido"""
        from datetime import datetime, timedelta
        import secrets

        token = secrets.token_urlsafe(32)
        test_user.reset_token = token
        test_user.reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        response = client.post(
            f"/resetar_senha/{token}",
            data={
                "senha": "NewSecurePass123!",
                "confirmar_senha": "NewSecurePass123!",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        test_user = User.query.get(test_user.id)
        assert test_user.reset_token is None
        assert test_user.reset_expires is None

    @pytest.mark.auth
    def test_reset_password_token_expirado(self, client, test_user):
        """Testa reset de senha com token expirado"""
        from datetime import datetime, timedelta
        import secrets

        token = secrets.token_urlsafe(32)
        test_user.reset_token = token
        test_user.reset_expires = datetime.utcnow() - timedelta(hours=1)
        db.session.commit()

        response = client.get(f"/resetar_senha/{token}", follow_redirects=True)

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "invalido" in response_text.lower() or "inválido" in response_text.lower() or "expirado" in response_text.lower()

    @pytest.mark.auth
    def test_reset_password_senhas_nao_coincidem(self, client, test_user):
        """Testa reset com senhas não coincidentes"""
        from datetime import datetime, timedelta
        import secrets

        token = secrets.token_urlsafe(32)
        test_user.reset_token = token
        test_user.reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        response = client.post(
            f"/resetar_senha/{token}",
            data={
                "senha": "NewSecurePass123!",
                "confirmar_senha": "DifferentPass123!",
            },
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "coincidem" in response_text.lower() or "não" in response_text.lower()

    @pytest.mark.auth
    def test_reset_password_fraca(self, client, test_user):
        """Testa reset com senha fraca"""
        from datetime import datetime, timedelta
        import secrets

        token = secrets.token_urlsafe(32)
        test_user.reset_token = token
        test_user.reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        response = client.post(
            f"/resetar_senha/{token}",
            data={"senha": "weak", "confirmar_senha": "weak"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert "invalido" in response_text.lower() or "inválido" in response_text.lower()


class TestAuthIntegracao:
    """Testes de integração de autenticação"""

    @pytest.mark.auth
    @pytest.mark.integration
    def test_fluxo_completo_cadastro_login(self, client):
        """Testa fluxo completo: cadastro -> login -> logout"""
        response = client.post(
            "/cadastro",
            data={
                "name": "Integration User",
                "email": "integration@example.com",
                "password": "SecurePass123!",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        response = client.post(
            "/login",
            data={"email": "integration@example.com", "password": "SecurePass123!"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        response = client.get("/logout", follow_redirects=True)
        assert response.status_code == 200

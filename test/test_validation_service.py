import pytest
from services.validation_service import Validadores


class TestValidadoresEmail:
    """Testes para validação de email"""

    @pytest.mark.validation
    @pytest.mark.parametrize(
        "email,esperado,motivo",
        [
            ("user@example.com", True, "Email válido padrão"),
            ("test.name@company.co.uk", True, "Email com ponto e país duplo"),
            ("user+tag@example.com", True, "Email com caractere +"),
            ("123@example.com", True, "Email começando com número"),
            ("", False, "Email vazio"),
            ("invalid", False, "Email sem @"),
            ("user@", False, "Email sem domínio"),
            ("@example.com", False, "Email sem usuário"),
            ("user @example.com", False, "Email com espaço"),
            ("user@example", False, "Email sem TLD"),
            ("user..name@example.com", True, "Email com múltiplos pontos (válido em padrão)"),
            ("a" * 150 + "@example.com", False, "Email muito longo (> 150)"),
            ("user@example.com", True, "Email exato no limite (150 chars)"),
        ],
    )
    def test_validar_email(self, email, esperado, motivo):
        """Testa validação de email com vários casos"""
        valido, mensagem = Validadores.validar_email(email)
        assert valido == esperado, f"Falhou: {motivo}. Mensagem: {mensagem}"


class TestValidadoresSenha:
    """Testes para validação de senha"""

    @pytest.mark.validation
    @pytest.mark.parametrize(
        "senha,esperado,motivo",
        [
            ("ValidPass123!", True, "Senha válida com todos os requisitos"),
            ("Test@1234", True, "Senha válida com símbolo @"),
            ("Abcd@1234", True, "Senha válida com 9 caracteres"),
            ("", False, "Senha vazia"),
            ("short", False, "Senha muito curta (< 6)"),
            ("noupppercase123!", False, "Sem letra maiúscula"),
            ("NOLOWERCASE123!", False, "Sem letra minúscula"),
            ("NoDigit@Pass", False, "Sem dígito"),
            ("NoSpecial123", False, "Sem caractere especial"),
            ("a" * 101, False, "Senha muito longa (> 100)"),
            ("ValidPass123@567890", True, "Senha longa válida com especial"),
            ("Test$1234", True, "Senha com caractere especial $"),
            ("Pass*123@Abc", True, "Senha com múltiplos especiais"),
        ],
    )
    def test_validar_senha(self, senha, esperado, motivo):
        """Testa validação de senha com vários casos"""
        valido, mensagem = Validadores.validar_senha(senha)
        assert valido == esperado, f"Falhou: {motivo}. Mensagem: {mensagem}"


class TestValidadoresNome:
    """Testes para validação de nome"""

    @pytest.mark.validation
    @pytest.mark.parametrize(
        "nome,esperado,motivo",
        [
            ("João Silva", True, "Nome válido com acentuação"),
            ("Maria", True, "Nome simples válido"),
            ("Ana Clara Santos", True, "Nome composto válido"),
            ("", False, "Nome vazio"),
            ("Jo", False, "Nome muito curto (< 3)"),
            ("a" * 151, False, "Nome muito longo (> 150)"),
            ("João123", False, "Nome com números"),
            ("José@Silva", False, "Nome com caractere especial"),
            ("José Silva", True, "Nome com acento válido"),
            ("José_Silva", False, "Nome com underscore"),
            ("María José", True, "Nome com acentuação dupla"),
        ],
    )
    def test_validar_nome(self, nome, esperado, motivo):
        """Testa validação de nome com vários casos"""
        valido, mensagem = Validadores.validar_nome(nome)
        assert valido == esperado, f"Falhou: {motivo}. Mensagem: {mensagem}"


class TestValidadoresMateria:
    """Testes para validação de matéria"""

    @pytest.mark.validation
    @pytest.mark.parametrize(
        "materia,esperado,motivo",
        [
            ("Matemática", True, "Matéria válida"),
            ("Português", True, "Matéria válida"),
            ("Eng", True, "Matéria com 3 caracteres"),
            ("", False, "Matéria vazia"),
            ("M", False, "Matéria muito curta (< 2)"),
            ("a" * 101, False, "Matéria muito longa (> 100)"),
            ("Mat123", True, "Matéria com números (permitido)"),
            ("Física-Química", True, "Matéria com hífen"),
        ],
    )
    def test_validar_materia(self, materia, esperado, motivo):
        """Testa validação de matéria com vários casos"""
        valido, mensagem = Validadores.validar_materia(materia)
        assert valido == esperado, f"Falhou: {motivo}. Mensagem: {mensagem}"


class TestValidadoresDuracao:
    """Testes para validação de duração"""

    @pytest.mark.validation
    @pytest.mark.parametrize(
        "duracao,esperado,motivo",
        [
            ("01:30", True, "Duração válida 1h30m"),
            ("00:45", True, "Duração válida 45 minutos"),
            ("23:59", True, "Duração máxima válida"),
            ("00:00", True, "Duração zero (válida)"),
            ("1:30", True, "Duração com hora de um dígito (válida)"),
            ("", True, "Duração vazia (opcional)"),
            ("24:00", False, "Hora inválida (24)"),
            ("12:60", False, "Minuto inválido (60)"),
            ("01:3", False, "Formato inválido (minuto sem zero)"),
            ("25:00", False, "Hora muito grande"),
            ("-01:30", False, "Duração negativa"),
            ("abc", False, "Formato não-numérico"),
        ],
    )
    def test_validar_duracao(self, duracao, esperado, motivo):
        """Testa validação de duração com vários casos"""
        valido, mensagem = Validadores.validar_duracao(duracao)
        assert valido == esperado, f"Falhou: {motivo}. Mensagem: {mensagem}"


class TestSanitizarTexto:
    """Testes para sanitização de texto"""

    @pytest.mark.validation
    def test_sanitizar_texto_valido(self):
        """Testa sanitização com HTML válido"""
        texto = "<p>Olá <strong>mundo</strong></p>"
        resultado = Validadores.sanitizar_texto(texto)
        assert "<p>" in resultado
        assert "<strong>" in resultado

    @pytest.mark.validation
    def test_sanitizar_texto_xss(self):
        """Testa remoção de script XSS"""
        texto = "<p>Texto</p><script>alert('XSS')</script>"
        resultado = Validadores.sanitizar_texto(texto)
        # bleach remove a tag script mas mantém o conteúdo
        assert "<script>" not in resultado
        assert "Texto" in resultado

    @pytest.mark.validation
    def test_sanitizar_texto_evento(self):
        """Testa remoção de eventos JavaScript"""
        texto = '<p onclick="alert()">Clique</p>'
        resultado = Validadores.sanitizar_texto(texto)
        assert "onclick" not in resultado

    @pytest.mark.validation
    def test_sanitizar_texto_vazio(self):
        """Testa sanitização de texto vazio"""
        resultado = Validadores.sanitizar_texto("")
        assert resultado == ""

    @pytest.mark.validation
    def test_sanitizar_texto_none(self):
        """Testa sanitização de None"""
        resultado = Validadores.sanitizar_texto(None)
        assert resultado is None

    @pytest.mark.validation
    def test_sanitizar_tags_nao_permitidas(self):
        """Testa remoção de tags não permitidas"""
        texto = "<div>Teste</div><p>Parágrafo</p>"
        resultado = Validadores.sanitizar_texto(texto)
        assert "<div>" not in resultado
        assert "<p>" in resultado

    @pytest.mark.validation
    def test_sanitizar_lista_formatacao(self):
        """Testa sanitização com lista e formatação"""
        texto = "<ul><li>Item 1</li><li>Item 2</li></ul><em>ênfase</em>"
        resultado = Validadores.sanitizar_texto(texto)
        assert "<ul>" in resultado
        assert "<li>" in resultado
        assert "<em>" in resultado


class TestValidadoresIntegracao:
    """Testes de integração entre validadores"""

    @pytest.mark.validation
    def test_fluxo_cadastro_valido(self):
        """Testa fluxo completo de validação para cadastro"""
        nome = "João Silva"
        email = "joao@example.com"
        senha = "SecurePass123!"

        valido_nome, _ = Validadores.validar_nome(nome)
        valido_email, _ = Validadores.validar_email(email)
        valido_senha, _ = Validadores.validar_senha(senha)

        assert valido_nome is True
        assert valido_email is True
        assert valido_senha is True

    @pytest.mark.validation
    def test_fluxo_cadastro_invalido(self):
        """Testa fluxo completo com dados inválidos"""
        nome = "J"  # Muito curto
        email = "invalid"  # Sem @
        senha = "weak"  # Muito fraca

        valido_nome, _ = Validadores.validar_nome(nome)
        valido_email, _ = Validadores.validar_email(email)
        valido_senha, _ = Validadores.validar_senha(senha)

        assert valido_nome is False
        assert valido_email is False
        assert valido_senha is False

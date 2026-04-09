import re
import bleach


class Validadores:
    """Classe com validadores de dados."""

    @staticmethod
    def validar_email(email):
        if not email or len(email) > 150:
            return False, "Email inválido ou muito longo"

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            return False, "Formato de email inválido"

        return True, "Email válido"

    @staticmethod
    def validar_senha(senha):
        if not senha or len(senha) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres"

        if len(senha) > 100:
            return False, "A senha deve ter no máximo 100 caracteres"

        # Corrigido: exige toda a senha, não apenas o primeiro caractere.
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
        if not re.match(pattern, senha):
            return (
                False,
                "A senha deve conter pelo menos uma letra maiúscula, uma minúscula, um dígito e um caractere especial (@$!%*?&)",
            )

        return True, "Senha válida"

    @staticmethod
    def validar_nome(nome):
        if not nome or len(nome) < 3:
            return False, "O nome deve ter no mínimo 3 caracteres"

        if len(nome) > 150:
            return False, "O nome deve ter no máximo 150 caracteres"

        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", nome):
            return False, "O nome deve conter apenas letras"

        return True, "Nome válido"

    @staticmethod
    def validar_materia(nome_materia):
        if not nome_materia or len(nome_materia) < 2:
            return False, "O nome da matéria deve ter no mínimo 2 caracteres"

        if len(nome_materia) > 100:
            return False, "O nome da matéria deve ter no máximo 100 caracteres"

        return True, "Matéria válida"

    @staticmethod
    def validar_duracao(duracao):
        if not duracao:
            return True, "Duração opcional"

        pattern = r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
        if not re.match(pattern, duracao):
            return False, "Formato de duração inválido. Use HH:MM (ex: 02:30)"

        return True, "Duração válida"

    @staticmethod
    def sanitizar_texto(texto):
        if not texto:
            return texto

        allowed_tags = [
            "p",
            "br",
            "strong",
            "em",
            "u",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "ul",
            "ol",
            "li",
            "blockquote",
        ]
        return bleach.clean(texto, tags=allowed_tags, attributes={}, strip=True)

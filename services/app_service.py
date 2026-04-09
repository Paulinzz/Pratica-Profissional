from datetime import datetime, timedelta

from models.models import db, Notificacao


tentativas_login = {}
tentativas_cadastro = {}


def limpar_tentativas_antigas():
    tempo_limite = datetime.utcnow() - timedelta(minutes=15)
    for dicionario in [tentativas_login, tentativas_cadastro]:
        ips_remover = [
            ip for ip, (_, timestamp) in dicionario.items() if timestamp < tempo_limite
        ]
        for ip in ips_remover:
            del dicionario[ip]


def verificar_rate_limit(ip, dicionario, max_tentativas=5):
    limpar_tentativas_antigas()

    if ip in dicionario:
        count, timestamp = dicionario[ip]

        if datetime.utcnow() - timestamp > timedelta(minutes=15):
            dicionario[ip] = (1, datetime.utcnow())
            return True, "Permitido"

        if count >= max_tentativas:
            tempo_restante = 15 - (datetime.utcnow() - timestamp).seconds // 60
            return (
                False,
                f"Muitas tentativas. Tente novamente em {tempo_restante} minutos.",
            )

        dicionario[ip] = (count + 1, timestamp)
        return True, "Permitido"

    dicionario[ip] = (1, datetime.utcnow())
    return True, "Permitido"


def criar_notificacao(user_id, tipo, titulo, mensagem, link=None, icone="fa-bell"):
    try:
        notificacao = Notificacao(
            user_id=user_id,
            tipo=tipo,
            titulo=titulo,
            mensagem=mensagem,
            link=link,
            icone=icone,
        )
        db.session.add(notificacao)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao criar notificação: {e}")
        db.session.rollback()


def parse_duration_to_minutes(duracao):
    if not duracao:
        return 0
    try:
        hours, minutes = map(int, duracao.split(":"))
        return hours * 60 + minutes
    except Exception:
        return 0


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
        "gif",
    }


def parse_date_field(value):
    """Converte YYYY-MM-DD em date, retornando None em valor vazio/inválido."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

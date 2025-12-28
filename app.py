from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from flask_bcrypt import (
    Bcrypt,
)
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
import os
from dotenv import load_dotenv
from sqlalchemy import func
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import secrets

import requests
import re
from functools import wraps
import bleach

from models.models import (
    db,
    User,
    Materia,
    Atividade,
    Notificacao,
    Meta,
    Badge,
    UserBadge,
)



# Carregar variáveis de ambiente
load_dotenv()


app = Flask(__name__)

# =============== CONFIGURAÇÕES DE SEGURANÇA - FocusUp ===============

app.config["SESSION_COOKIE_SECURE"] = True  # somente envios via HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

# Configuração para MySQL usando variáveis de ambiente
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "pratica_profissional")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "FSca*2033")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "Chave1234")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configurações de email
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"]
)

db.init_app(app)
bcrypt = Bcrypt(app)
mail = Mail(app)

# Inicializar proteção CSRF
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =============== VALIDADORES ===============


class Validadores:
    """Classe com validadores de dados"""

    @staticmethod
    def validar_email(email):
        """Valida formato de email"""
        if not email or len(email) > 150:
            return False, "Email inválido ou muito longo"

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            return False, "Formato de email inválido"

        return True, "Email válido"

    @staticmethod
    def validar_senha(senha):
        """Valida complexidade da senha com regex"""
        if not senha or len(senha) < 6:
            return False, "A senha deve ter no mínimo 6 caracteres"

        if len(senha) > 100:
            return False, "A senha deve ter no máximo 100 caracteres"

        # Regex para validar: pelo menos uma maiúscula, uma minúscula, um dígito e um caractere especial
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"
        if not re.match(pattern, senha):
            return (
                False,
                "A senha deve conter pelo menos uma letra maiúscula, uma minúscula, um dígito e um caractere especial (@$!%*?&)",
            )

        return True, "Senha válida"

    @staticmethod
    def validar_nome(nome):
        """Valida nome do usuário"""
        if not nome or len(nome) < 3:
            return False, "O nome deve ter no mínimo 3 caracteres"

        if len(nome) > 150:
            return False, "O nome deve ter no máximo 150 caracteres"

        # Permitir apenas letras, espaços e acentos
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", nome):
            return False, "O nome deve conter apenas letras"

        return True, "Nome válido"

    @staticmethod
    def validar_materia(nome_materia):
        """Valida nome da matéria"""
        if not nome_materia or len(nome_materia) < 2:
            return False, "O nome da matéria deve ter no mínimo 2 caracteres"

        if len(nome_materia) > 100:
            return False, "O nome da matéria deve ter no máximo 100 caracteres"

        return True, "Matéria válida"

    @staticmethod
    def validar_duracao(duracao):
        """Valida formato de duração (HH:MM)"""
        if not duracao:
            return True, "Duração opcional"

        pattern = r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
        if not re.match(pattern, duracao):
            return False, "Formato de duração inválido. Use HH:MM (ex: 02:30)"

        return True, "Duração válida"

    @staticmethod
    def sanitizar_texto(texto):
        """Sanitiza texto removendo tags HTML perigosas"""
        if not texto:
            return texto

        # Lista de tags permitidas (básicas e seguras)
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
        allowed_attributes = {}

        # Sanitizar o texto
        texto_sanitizado = bleach.clean(
            texto, tags=allowed_tags, attributes=allowed_attributes, strip=True
        )

        return texto_sanitizado


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def criar_badges_padrao():
    """Cria badges padrão se não existirem"""
    badges = [
        {
            "nome": "Primeira Atividade",
            "descricao": "Adicionou sua primeira atividade",
            "icone": "fa-plus",
            "categoria": "atividade",
            "criterio": "primeira_atividade",
            "pontos": 10,
        },
        {
            "nome": "Meta Concluída",
            "descricao": "Concluiu sua primeira meta",
            "icone": "fa-check",
            "categoria": "meta",
            "criterio": "primeira_meta_concluida",
            "pontos": 20,
        },
        {
            "nome": "Estudioso",
            "descricao": "Estudou por 10 horas",
            "icone": "fa-clock",
            "categoria": "tempo",
            "criterio": "10_horas",
            "pontos": 30,
        },
        {
            "nome": "Dedicado",
            "descricao": "Adicionou 5 matérias",
            "icone": "fa-book",
            "categoria": "materia",
            "criterio": "5_materias",
            "pontos": 25,
        },
    ]

    for badge_data in badges:
        if not Badge.query.filter_by(nome=badge_data["nome"]).first():
            badge = Badge(**badge_data)
            db.session.add(badge)
    db.session.commit()


def verificar_e_conceder_badge(user_id, criterio):
    """Verifica se o usuário atende ao critério e concede o badge se não tiver"""
    user = User.query.get(user_id)
    badge = Badge.query.filter_by(criterio=criterio).first()
    if not badge:
        return

    # Verificar se já tem
    if UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
        return

    # Verificar condição
    conceder = False
    if criterio == "primeira_atividade":
        conceder = len(user.atividades) >= 1
    elif criterio == "primeira_meta_concluida":
        conceder = (
            Meta.query.filter_by(user_id=user_id, status="concluido").count() >= 1
        )
    elif criterio == "10_horas":
        tempo_total = 0
        for atividade in user.atividades:
            tempo_total += parse_duration_to_minutes(atividade.duracao or "0")
        conceder = tempo_total >= 600  # 10 horas
    elif criterio == "5_materias":
        conceder = len(user.materias) >= 5

    if conceder:
        user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
        db.session.add(user_badge)
        db.session.commit()

        # Notificação
        criar_notificacao(
            user_id=user_id,
            tipo="conquista",
            titulo=f"🏆 Badge Conquistado: {badge.nome}!",
            mensagem=f"Parabéns! Você ganhou o badge '{badge.nome}' - {badge.descricao}",
            icone="fa-trophy",
        )


with app.app_context():
    try:
        db.create_all()
        criar_badges_padrao()
        print("✅ Banco de dados conectado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco de dados: {e}")
        print("Verifique suas credenciais no arquivo .env")


# Dicionário para rastrear tentativas
tentativas_login = {}
tentativas_cadastro = {}


def limpar_tentativas_antigas():
    """Remove tentativas antigas (mais de 15 minutos)"""
    tempo_limite = datetime.utcnow() - timedelta(minutes=15)

    for dicionario in [tentativas_login, tentativas_cadastro]:
        ips_remover = [
            ip
            for ip, (count, timestamp) in dicionario.items()
            if timestamp < tempo_limite
        ]
        for ip in ips_remover:
            del dicionario[ip]


def verificar_rate_limit(ip, dicionario, max_tentativas=5):
    """
    Verifica se o IP excedeu o limite de tentativas

    Args:
        ip: IP do cliente
        dicionario: tentativas_login ou tentativas_cadastro
        max_tentativas: número máximo de tentativas permitidas

    Returns:
        (permitido, mensagem)
    """
    limpar_tentativas_antigas()

    if ip in dicionario:
        count, timestamp = dicionario[ip]

        # Se passou 15 minutos, resetar
        if datetime.utcnow() - timestamp > timedelta(minutes=15):
            dicionario[ip] = (1, datetime.utcnow())
            return True, "Permitido"

        # Se excedeu tentativas
        if count >= max_tentativas:
            tempo_restante = 15 - (datetime.utcnow() - timestamp).seconds // 60
            return (
                False,
                f"Muitas tentativas. Tente novamente em {tempo_restante} minutos.",
            )

        # Incrementar contador
        dicionario[ip] = (count + 1, timestamp)
        return True, "Permitido"
    else:
        dicionario[ip] = (1, datetime.utcnow())
        return True, "Permitido"


def criar_notificacao(user_id, tipo, titulo, mensagem, link=None, icone="fa-bell"):
    """Cria uma nova notificação para o usuário"""
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
    """Converte duração HH:MM para minutos"""
    if not duracao:
        return 0
    try:
        hours, minutes = map(int, duracao.split(":"))
        return hours * 60 + minutes
    except:
        return 0


# =============== PROTEÇÃO CSRF ===============
# Proteção CSRF implementada com flask-wtf (CSRFProtect)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def register():
    get_flashed_messages()

    if request.method == "POST":
        # Rate limiting
        ip = request.remote_addr
        permitido, mensagem = verificar_rate_limit(
            ip, tentativas_cadastro, max_tentativas=3
        )

        if not permitido:
            flash(mensagem, "error")
            return redirect(url_for("register"))

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validar nome
        valido, msg = Validadores.validar_nome(name)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("register"))

        # Validar email
        valido, msg = Validadores.validar_email(email)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("register"))

        # Validar senha
        valido, msg = Validadores.validar_senha(password)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("register"))

        # Verificar se email já existe
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash("Este email já está cadastrado.", "error")
            return redirect(url_for("register"))

        try:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            new_user = User(name=name, email=email, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            # Criar notificação de boas-vindas
            criar_notificacao(
                user_id=new_user.id,
                tipo="sistema",
                titulo="Bem-vindo ao FocusUp!",
                mensagem="Sua conta foi criada com sucesso! Comece adicionando suas primeiras atividades.",
                link="/dashboard",
                icone="fa-rocket",
            )

            flash(
                "Cadastro realizado com sucesso! Faça login para continuar.", "success"
            )
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao criar conta: {str(e)}", "error")
            return redirect(url_for("register"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    get_flashed_messages()

    if request.method == "POST":
        # Rate limiting
        ip = request.remote_addr
        permitido, mensagem = verificar_rate_limit(
            ip, tentativas_login, max_tentativas=5
        )

        if not permitido:
            flash(mensagem, "error")
            return redirect(url_for("login"))

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validar email
        valido, msg = Validadores.validar_email(email)
        if not valido:
            flash("Email ou senha inválidos.", "error")
            return redirect(url_for("login"))

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)

            # Criar notificação de login
            criar_notificacao(
                user_id=user.id,
                tipo="sistema",
                titulo="Login realizado",
                mensagem=f"Você fez login em {datetime.utcnow().strftime('%d/%m/%Y às %H:%M')}",
                icone="fa-right-to-bracket",
            )

            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Email ou senha inválidos.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/esqueci_senha", methods=["GET", "POST"])
def esqueci_senha():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        # Validar email
        valido, msg = Validadores.validar_email(email)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("esqueci_senha"))

        user = User.query.filter_by(email=email).first()
        if user:
            # Gerar token seguro
            token = secrets.token_urlsafe(32)
            expires = datetime.utcnow() + timedelta(hours=1)  # Expira em 1 hora

            user.reset_token = token
            user.reset_expires = expires
            db.session.commit()

            # Enviar email
            try:
                from flask_mail import Message

                msg = Message("Redefinição de Senha - FocusUp", recipients=[email])
                msg.body = f"""
Olá {user.name or 'usuário'},

Você solicitou a redefinição de senha da sua conta no FocusUp.

Para redefinir sua senha, clique no link abaixo:
{url_for('resetar_senha', token=token, _external=True)}

Este link expira em 1 hora.

Se você não solicitou esta redefinição, ignore este email.

Atenciosamente,
Equipe FocusUp
                """
                mail.send(msg)
                flash(
                    "Email de redefinição enviado! Verifique sua caixa de entrada.",
                    "success",
                )
            except Exception as e:
                print(f"Erro ao enviar email: {e}")
                flash("Erro ao enviar email. Tente novamente mais tarde.", "error")
        else:
            # Mesmo se não existir, mostrar mensagem de sucesso para não revelar se email existe
            flash(
                "Se o email estiver cadastrado, você receberá instruções para redefinir a senha.",
                "info",
            )

        return redirect(url_for("login"))

    return render_template("esqueci_senha.html")


@app.route("/resetar_senha/<token>", methods=["GET", "POST"])
def resetar_senha(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or user.reset_expires < datetime.utcnow():
        flash("Link de redefinição inválido ou expirado.", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        senha = request.form.get("senha", "")
        confirmar_senha = request.form.get("confirmar_senha", "")

        if senha != confirmar_senha:
            flash("As senhas não coincidem.", "error")
            return redirect(url_for("resetar_senha", token=token))

        # Validar nova senha
        valido, msg = Validadores.validar_senha(senha)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("resetar_senha", token=token))

        # Atualizar senha
        hashed_password = bcrypt.generate_password_hash(senha).decode("utf-8")
        user.password = hashed_password
        user.reset_token = None
        user.reset_expires = None
        db.session.commit()

        flash("Senha redefinida com sucesso! Faça login com sua nova senha.", "success")
        return redirect(url_for("login"))

    return render_template("resetar_senha.html", token=token)


@app.route("/logout")
@login_required
def logout():
    session.pop("_flashes", None)
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("index"))


# Dicionário de tradução básico, isso é um teste simulando um tradutor
traducoes_comuns = {
    "machine learning": "aprendizado de máquina",
    "deep learning": "aprendizado profundo",
    "neural network": "rede neural",
    "artificial intelligence": "inteligência artificial",
    "data science": "ciência de dados",
    "computer vision": "visão computacional",
    "natural language processing": "processamento de linguagem natural",
}


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    # busca sempre artigos relacionados a métodos de estudo
    query = "pomodoro|spaced repetition|active recall|mind map"
    url = f"https://api.openalex.org/works?filter=title.search:{query},cited_by_count:>3&per-page=10"
    response = requests.get(url)

    artigos = []
    if response.status_code == 200:
        data = response.json()
        artigos = data.get("results", [])

        for artigo in artigos:
            titulo = artigo.get("title", "")
            for eng, pt in traducoes_comuns.items():
                titulo = titulo.replace(eng, pt)
                titulo = titulo.replace(eng.title(), pt.title())
            artigo["title_pt"] = titulo

            resumo = artigo.get("abstract_inverted_index")
            if resumo:
                abstract_words = []
                for word, positions in resumo.items():
                    for pos in positions:
                        if len(abstract_words) <= pos:
                            abstract_words.extend(
                                [""] * (pos - len(abstract_words) + 1)
                            )
                        abstract_words[pos] = word
                abstract = " ".join(abstract_words)
                artigo["abstract_pt"] = abstract[:150] + "..."
            else:
                artigo["abstract_pt"] = "Resumo não disponível"

            artigo["publication_year"] = artigo.get("publication_year")
            artigo["cited_by_count"] = artigo.get("cited_by_count", 0)
            artigo["doi"] = artigo.get("doi")
            artigo["id"] = artigo.get("id")

    # Dados para gráficos - tempo gasto por matéria
    from sqlalchemy import func as sql_func

    atividades_com_duracao = (
        db.session.query(Atividade.materia, Atividade.duracao)
        .filter_by(user_id=current_user.id)
        .filter(Atividade.duracao.isnot(None))
        .all()
    )

    # Calcular tempo total por matéria
    tempo_por_materia = {}
    for materia, duracao in atividades_com_duracao:
        minutos = parse_duration_to_minutes(duracao)
        if materia in tempo_por_materia:
            tempo_por_materia[materia] += minutos
        else:
            tempo_por_materia[materia] = minutos

    # Preparar dados para o gráfico
    labels_materias = list(tempo_por_materia.keys())
    data_materias = list(tempo_por_materia.values())

    # Ordenar matérias por tempo gasto (descendente)
    materia_tempo = []
    for materia in current_user.materias:
        tempo = tempo_por_materia.get(materia.nome, 0)
        materia_tempo.append((materia, tempo))

    def get_tempo(item):
        return item[1]

    materia_tempo.sort(key=get_tempo, reverse=True)
    sorted_materias = [m[0] for m in materia_tempo]
    activities_per_day = (
        db.session.query(func.date(Atividade.data_criacao), func.count(Atividade.id))
        .filter_by(user_id=current_user.id)
        .group_by(func.date(Atividade.data_criacao))
        .all()
    )

    # Preparar dados para Chart.js
    labels_dash = [str(row[0]) for row in activities_per_day]
    data_dash = [row[1] for row in activities_per_day]

    # Estatísticas de metas
    metas_ativas = Meta.query.filter_by(user_id=current_user.id, status="ativo").count()
    metas_concluidas = Meta.query.filter_by(
        user_id=current_user.id, status="concluido"
    ).count()
    total_metas = metas_ativas + metas_concluidas

    return render_template(
        "dashboard.html",
        artigos=artigos,
        labels_dash=labels_dash,
        data_dash=data_dash,
        labels_materias=labels_materias,
        data_materias=data_materias,
        tempo_por_materia=tempo_por_materia,
        sorted_materias=sorted_materias,
        metas_ativas=metas_ativas,
        metas_concluidas=metas_concluidas,
        total_metas=total_metas,
    )


@app.route("/adicionar_materia", methods=["POST"])
@login_required
def adicionar_materia():
    nome_materia = request.form.get("materia", "").strip()

    # Validar nome da matéria
    valido, msg = Validadores.validar_materia(nome_materia)
    if not valido:
        flash(msg, "error")
        return redirect(url_for("dashboard"))

    # Verificar se já existe
    materia_existe = Materia.query.filter_by(
        nome=nome_materia, user_id=current_user.id
    ).first()

    if materia_existe:
        flash(f"A matéria '{nome_materia}' já está cadastrada.", "error")
        return redirect(url_for("dashboard"))

    try:
        nova_materia = Materia(nome=nome_materia, user_id=current_user.id)
        db.session.add(nova_materia)
        db.session.commit()

        # Criar notificação
        criar_notificacao(
            user_id=current_user.id,
            tipo="sistema",
            titulo="Matéria Adicionada! 📚",
            mensagem=f"A matéria '{nome_materia}' foi adicionada com sucesso.",
            icone="fa-book",
        )

        # Verificar badge
        verificar_e_conceder_badge(current_user.id, "5_materias")

        flash(f"Matéria '{nome_materia}' adicionada com sucesso!", "success")
        return redirect(url_for("adicionar_materia_page"))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao adicionar matéria: {str(e)}", "error")

    return redirect(url_for("adicionar_materia_page"))


@app.route("/adicionar_materia", methods=["GET"])
@login_required
def adicionar_materia_page():
    """Página para adicionar matéria"""
    # Calcular tempo por matéria
    atividades_com_duracao = (
        db.session.query(Atividade.materia, Atividade.duracao)
        .filter_by(user_id=current_user.id)
        .filter(Atividade.duracao.isnot(None))
        .all()
    )

    tempo_por_materia = {}
    for materia, duracao in atividades_com_duracao:
        minutos = parse_duration_to_minutes(duracao)
        if materia in tempo_por_materia:
            tempo_por_materia[materia] += minutos
        else:
            tempo_por_materia[materia] = minutos

    # Obter matérias do usuário e ordenar por tempo gasto
    all_materias = Materia.query.filter_by(user_id=current_user.id).all()
    sorted_materias = sorted(
        all_materias, key=lambda m: tempo_por_materia.get(m.nome, 0), reverse=True
    )

    return render_template("adicionar_materia.html", materias=sorted_materias)


@app.route("/adicionar_atividade", methods=["GET", "POST"])
@login_required
def adicionar_atividade():
    # Obter matérias do usuário para o dropdown
    materias = Materia.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        materia = request.form.get("materia", "").strip()
        assunto = Validadores.sanitizar_texto(
            request.form.get("assunto_primario", "").strip()
        )
        descricao = Validadores.sanitizar_texto(
            request.form.get("descricao", "").strip()
        )
        duracao = request.form.get("duracao", "").strip()
        data = request.form.get("data", "").strip()

        # Validações
        if not materia or len(materia) < 2:
            flash("Informe o nome da matéria (mínimo 2 caracteres).", "error")
            return redirect(url_for("adicionar_atividade"))

        if not assunto or len(assunto) < 2:
            flash("Informe o assunto primário (mínimo 2 caracteres).", "error")
            return redirect(url_for("adicionar_atividade"))

        # Validar duração
        if duracao:
            valido, msg = Validadores.validar_duracao(duracao)
            if not valido:
                flash(msg, "error")
                return redirect(url_for("adicionar_atividade"))

        try:
            nova_atividade = Atividade(
                materia=materia,
                assunto_primario=assunto,
                descricao=descricao if descricao else None,
                duracao=duracao if duracao else None,
                data=data if data else None,
                user_id=current_user.id,
            )
            db.session.add(nova_atividade)
            db.session.commit()

            # Criar notificações
            criar_notificacao(
                user_id=current_user.id,
                tipo="sistema",
                titulo="Atividade Criada! ✅",
                mensagem=f"'{assunto}' de {materia} foi adicionada com sucesso.",
                link="/listar_atividades",
                icone="fa-check-circle",
            )

            # Notificação de lembrete para amanhã
            criar_notificacao(
                user_id=current_user.id,
                tipo="lembrete",
                titulo="Lembrete de Estudo 📚",
                mensagem=f"Não esqueça de revisar '{assunto}' amanhã!",
                icone="fa-calendar-check",
            )

            # Verificar badges
            verificar_e_conceder_badge(current_user.id, "primeira_atividade")
            verificar_e_conceder_badge(current_user.id, "10_horas")

            flash("Atividade adicionada com sucesso!", "success")
            return redirect(url_for("adicionar_atividade"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao adicionar atividade: {str(e)}", "error")

    atividades = (
        Atividade.query.filter_by(user_id=current_user.id)
        .order_by(Atividade.data_criacao.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "adicionar_atividade.html", atividades=atividades, materias=materias
    )


@app.route("/listar_atividades")
@login_required
def listar_atividades():
    atividades = Atividade.query.filter_by(user_id=current_user.id).all()
    return render_template("listar_atividades.html", atividades=atividades)


@app.route("/editar_atividade/<int:atividade_id>", methods=["GET", "POST"])
@login_required
def editar_atividade(atividade_id):
    atividade = Atividade.query.filter_by(
        id=atividade_id, user_id=current_user.id
    ).first()
    if not atividade:
        flash(
            "Atividade não encontrada ou você não tem permissão para editá-la.", "error"
        )
        return redirect(url_for("listar_atividades"))

    if request.method == "POST":
        materia = request.form.get("materia")
        assunto = Validadores.sanitizar_texto(request.form.get("assunto_primario"))
        descricao = Validadores.sanitizar_texto(request.form.get("descricao"))
        duracao = request.form.get("duracao")

        if not materia or not assunto:
            flash("Informe pelo menos a matéria e o assunto primário.", "error")
        else:
            atividade.materia = materia
            atividade.assunto_primario = assunto
            atividade.descricao = descricao
            atividade.duracao = duracao

            db.session.commit()
            flash("Atividade atualizada com sucesso!", "success")
            return redirect(url_for("listar_atividades"))

    return render_template("editar_atividade.html", atividade=atividade)


@app.route("/editar_materia/<int:materia_id>", methods=["GET", "POST"])
@login_required
def editar_materia(materia_id):
    materia = Materia.query.filter_by(id=materia_id, user_id=current_user.id).first()
    if not materia:
        flash("Matéria não encontrada ou sem permissão para editar.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()

        # Validar nome da matéria
        valido, msg = Validadores.validar_materia(nome)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("editar_materia", materia_id=materia_id))

        # Verificar se já existe outra matéria com esse nome
        materia_existente = (
            Materia.query.filter_by(nome=nome, user_id=current_user.id)
            .filter(Materia.id != materia_id)
            .first()
        )

        if materia_existente:
            flash(f"Já existe uma matéria com o nome '{nome}'.", "error")
            return redirect(url_for("editar_materia", materia_id=materia_id))

        try:
            materia.nome = nome
            db.session.commit()
            flash("Matéria atualizada com sucesso!", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar matéria: {str(e)}", "error")

    return render_template("editar_materia.html", materia=materia)


@app.route("/excluir_materia/<int:materia_id>", methods=["POST"])
@login_required
def excluir_materia(materia_id):
    materia = Materia.query.filter_by(id=materia_id, user_id=current_user.id).first()
    if not materia:
        flash("Matéria não encontrada ou sem permissão para excluir.", "error")
        return redirect(url_for("dashboard"))
    try:
        db.session.delete(materia)
        db.session.commit()
        flash("Matéria excluída com sucesso.", "success")
    except Exception as e:
        db.session.rollback()
        print(f"ERRO ao excluir materia: {e}")
        flash("Erro ao excluir matéria. Tente novamente mais tarde.", "error")
    return redirect(url_for("dashboard"))


@app.route("/excluir_atividade/<int:atividade_id>", methods=["POST"])
@login_required
def excluir_atividade(atividade_id):
    atividade = Atividade.query.filter_by(
        id=atividade_id, user_id=current_user.id
    ).first()
    if not atividade:
        flash("Atividade não encontrada ou sem permissão para excluir.", "error")
        return redirect(url_for("listar_atividades"))
    try:
        db.session.delete(atividade)
        db.session.commit()
        flash("Atividade excluída com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        print(f"ERRO ao excluir atividade: {e}")
        flash("Erro ao excluir atividade. Tente novamente mais tarde.", "error")
    return redirect(url_for("listar_atividades"))


@app.route("/ajuda")
@login_required
def ajuda():
    return render_template("ajuda.html")


@app.route("/listar_noticacoes")
@login_required
def listar_notificacoes():
    tipo_filtro = request.args.get("tipo", "todos")
    lida_filtro = request.args.get("lida", "todos")

    query = Notificacao.query.filter_by(user_id=current_user.id)

    if tipo_filtro != "todos":
        query = query.filter_by(tipo=tipo_filtro)

    if lida_filtro == "lidas":
        query = query.filter_by(lida=True)
    elif lida_filtro == "nao_lidas":
        query = query.filter_by(lida=False)

    notificacoes = query.order_by(Notificacao.data_criacao.desc()).all()

    # Estatísticas
    total_notificacoes = len(notificacoes)
    nao_lidas = sum(1 for n in notificacoes if not n.lida)

    return render_template(
        "listar_notificacoes.html",
        notificacoes=notificacoes,
        tipo_filtro=tipo_filtro,
        lida_filtro=lida_filtro,
        total_notificacoes=total_notificacoes,
        nao_lidas=nao_lidas,
    )


@app.route("/marcar_notificacao_lida/<int:notificacao_id>", methods=["POST"])
@login_required
def marcar_notificacao_lida(notificacao_id):
    notificacao = Notificacao.query.filter_by(
        id=notificacao_id, user_id=current_user.id
    ).first()

    if notificacao:
        notificacao.lida = True
        db.session.commit()
        return {"success": True}, 200

    return {"success": False, "message": "Notificação não encontrada"}, 404


@app.route("/excluir_notificacao/<int:notificacao_id>", methods=["POST"])
@login_required
def excluir_notificacao(notificacao_id):
    notificacao = Notificacao.query.filter_by(
        id=notificacao_id, user_id=current_user.id
    ).first()

    if notificacao:
        db.session.delete(notificacao)
        db.session.commit()
        return {"success": True}, 200

    return {"success": False, "message": "Notificação não encontrada"}, 404


@app.route("/marcar_todas_lidas", methods=["POST"])
@login_required
def marcar_todas_lidas():
    Notificacao.query.filter_by(user_id=current_user.id, lida=False).update(
        {"lida": True}
    )
    db.session.commit()
    return {"success": True}, 200


@app.route("/api/notificacoes_nao_lidas")
@login_required
def api_notificacoes_nao_lidas():
    nao_lidas = Notificacao.query.filter_by(user_id=current_user.id, lida=False).count()
    return {"nao_lidas": nao_lidas}


@app.route("/sobre_nos")
@login_required
def sobre_nos():
    return render_template("sobre.html")


@app.route("/politica-privacidade")
@login_required
def politica_privacidade():
    return render_template("politica_privacidade.html")


@app.route("/termos-servico")
@login_required
def termos_servico():
    return render_template(
        "termos_servico.html", last_update="01 de Setembro de 2025", version="1.0"
    )


@app.route("/perfil")
@login_required
def perfil():
    """Página de perfil do usuário"""
    # Estatísticas reais
    atividades_count = Atividade.query.filter_by(user_id=current_user.id).count()
    materias_count = Materia.query.filter_by(user_id=current_user.id).count()
    # Sequência: dias consecutivos com atividades (simplificado)
    hoje = datetime.utcnow().date()
    sequencia = 0
    for i in range(30):  # últimos 30 dias
        data = hoje - timedelta(days=i)
        if (
            Atividade.query.filter_by(user_id=current_user.id)
            .filter(db.func.date(Atividade.data_criacao) == data)
            .first()
        ):
            sequencia += 1
        else:
            break

    # Badges do usuário
    user_badges = UserBadge.query.filter_by(user_id=current_user.id).all()

    return render_template(
        "perfil.html",
        atividades_count=atividades_count,
        materias_count=materias_count,
        sequencia=sequencia,
        user_badges=user_badges,
    )


@app.route("/configuracoes")
@login_required
def configuracoes():
    """Página de configurações do usuário"""
    return render_template("configuracoes.html")


@app.route("/atualizar_perfil", methods=["POST"])
@login_required
def atualizar_perfil():
    """Atualiza informações do perfil"""
    nome = Validadores.sanitizar_texto(request.form.get("nome"))
    email = request.form.get("email")

    try:
        # Atualizar dados do usuário
        current_user.name = nome
        current_user.email = email
        db.session.commit()
        flash("Perfil atualizado com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao atualizar perfil: {str(e)}", "error")

    return redirect(url_for("perfil"))


@app.route("/alterar_senha", methods=["POST"])
@login_required
def alterar_senha():
    """Altera a senha do usuário"""
    senha_atual = request.form.get("senha_atual")
    nova_senha = request.form.get("nova_senha")
    confirmar_senha = request.form.get("confirmar_senha")

    # Verificar se a senha atual está correta
    if not bcrypt.check_password_hash(current_user.password, senha_atual):
        flash("Senha atual incorreta!", "error")
        return redirect(url_for("perfil"))

    # Verificar se as novas senhas coincidem
    if nova_senha != confirmar_senha:
        flash("As senhas não coincidem!", "error")
        return redirect(url_for("perfil"))

    try:
        # Atualizar senha
        hashed_password = bcrypt.generate_password_hash(nova_senha).decode("utf-8")
        current_user.password = hashed_password
        db.session.commit()
        flash("Senha alterada com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao alterar senha: {str(e)}", "error")

    return redirect(url_for("perfil"))


@app.route("/upload_foto", methods=["POST"])
@login_required
def upload_foto():
    """Faz upload da foto de perfil"""
    if "foto" not in request.files:
        flash("Nenhum arquivo enviado.", "error")
        return redirect(url_for("perfil"))

    file = request.files["foto"]
    if file.filename == "":
        flash("Nenhum arquivo selecionado.", "error")
        return redirect(url_for("perfil"))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{current_user.id}_{file.filename}")
        filepath = os.path.join(app.root_path, "static", "imagens", filename)
        file.save(filepath)
        current_user.photo = filename
        db.session.commit()
        flash("Foto de perfil atualizada com sucesso!", "success")
    else:
        flash("Tipo de arquivo não permitido.", "error")

    return redirect(url_for("perfil"))


@app.route("/remover_foto", methods=["POST"])
@login_required
def remover_foto():
    """Remove a foto de perfil"""
    try:
        # Remover o arquivo físico se existir
        if current_user.photo:
            filepath = os.path.join(
                app.root_path, "static", "imagens", current_user.photo
            )
            if os.path.exists(filepath):
                os.remove(filepath)

        # Limpar o campo photo no banco
        current_user.photo = None
        db.session.commit()

        return {"success": True, "message": "Foto removida com sucesso!"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}, 500


@app.route("/baixar_dados")
@login_required
def baixar_dados():
    """Permite ao usuário baixar todos os seus dados em PDF"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )
        from reportlab.lib.units import inch
        from io import BytesIO

        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Título do documento
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Centralizado
        )
        story.append(Paragraph("Relatório de Dados - FocusUp", title_style))
        story.append(Spacer(1, 12))

        # Informações do usuário
        story.append(Paragraph("Informações do Usuário", styles["Heading2"]))
        user_data = [
            ["ID", str(current_user.id)],
            ["Nome", current_user.name or "N/A"],
            ["Email", current_user.email],
            [
                "Data de Cadastro",
                (
                    current_user.date_created.strftime("%d/%m/%Y %H:%M")
                    if hasattr(current_user, "date_created")
                    and current_user.date_created
                    else "N/A"
                ),
            ],
            ["Foto", current_user.photo or "N/A"],
        ]

        user_table = Table(user_data, colWidths=[2 * inch, 4 * inch])
        user_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(user_table)
        story.append(Spacer(1, 20))

        # Matérias
        story.append(Paragraph("Matérias Cadastradas", styles["Heading2"]))
        if current_user.materias:
            materias_data = [["Nome", "Data de Criação"]]
            for materia in current_user.materias:
                data_criacao = (
                    materia.date_created.strftime("%d/%m/%Y %H:%M")
                    if hasattr(materia, "date_created") and materia.date_created
                    else "N/A"
                )
                materias_data.append([materia.nome, data_criacao])

            materias_table = Table(materias_data, colWidths=[3 * inch, 3 * inch])
            materias_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgreen),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(materias_table)
        else:
            story.append(Paragraph("Nenhuma matéria cadastrada.", styles["Normal"]))
        story.append(Spacer(1, 20))

        # Atividades
        story.append(Paragraph("Histórico de Atividades", styles["Heading2"]))
        if current_user.atividades:
            atividades_data = [["Matéria", "Assunto", "Duração", "Data", "Descrição"]]

            # Limitar a 50 atividades mais recentes para não sobrecarregar o PDF
            atividades_recentes = sorted(
                current_user.atividades, key=lambda x: x.data_criacao, reverse=True
            )[:50]

            for atividade in atividades_recentes:
                data_formatada = (
                    atividade.data.strftime("%d/%m/%Y") if atividade.data else "N/A"
                )
                descricao_curta = (
                    (atividade.descricao[:50] + "...")
                    if atividade.descricao and len(atividade.descricao) > 50
                    else atividade.descricao or "N/A"
                )
                atividades_data.append(
                    [
                        atividade.materia,
                        atividade.assunto_primario,
                        atividade.duracao or "N/A",
                        data_formatada,
                        descricao_curta,
                    ]
                )

            atividades_table = Table(
                atividades_data,
                colWidths=[1.5 * inch, 1.5 * inch, 1 * inch, 1.2 * inch, 2.3 * inch],
            )
            atividades_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightyellow),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ]
                )
            )
            story.append(atividades_table)

            if len(current_user.atividades) > 50:
                story.append(
                    Paragraph(
                        f"<i>Mostrando as 50 atividades mais recentes de um total de {len(current_user.atividades)}.</i>",
                        styles["Normal"],
                    )
                )
        else:
            story.append(Paragraph("Nenhuma atividade registrada.", styles["Normal"]))
        story.append(Spacer(1, 20))

        # Estatísticas
        story.append(Paragraph("Estatísticas Gerais", styles["Heading2"]))

        # Calcular estatísticas
        total_atividades = len(current_user.atividades)
        total_materias = len(current_user.materias)

        # Calcular tempo total estudado
        tempo_total = 0
        for atividade in current_user.atividades:
            if atividade.duracao:
                try:
                    horas, minutos = map(int, atividade.duracao.split(":"))
                    tempo_total += horas * 60 + minutos
                except:
                    pass

        horas_totais = tempo_total // 60
        minutos_restantes = tempo_total % 60

        # Data e hora de Brasília (UTC-3)
        from datetime import timezone, timedelta

        brasilia_tz = timezone(timedelta(hours=-3))
        data_exportacao = datetime.now(brasilia_tz).strftime("%d/%m/%Y %H:%M:%S")

        stats_data = [
            ["Total de Atividades", str(total_atividades)],
            ["Total de Matérias", str(total_materias)],
            ["Tempo Total Estudado", f"{horas_totais}h {minutos_restantes}min"],
            ["Data de Exportação", data_exportacao + " (Horário de Brasília)"],
        ]

        stats_table = Table(stats_data, colWidths=[3 * inch, 3 * inch])
        stats_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightcoral),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(stats_table)
        story.append(Spacer(1, 20))

        # Rodapé
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.gray,
            alignment=1,
        )
        story.append(
            Paragraph("Relatório gerado automaticamente pelo FocusUp", footer_style)
        )

        # Gerar PDF
        doc.build(story)
        buffer.seek(0)

        # Retornar PDF como resposta
        from flask import Response

        response = Response(
            buffer.getvalue(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f"attachment;filename=relatorio_dados_focusup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
            },
        )

        return response

    except ImportError:
        # Fallback para JSON se reportlab não estiver instalado
        return {
            "error": "Biblioteca PDF não instalada. Execute: pip install reportlab"
        }, 500
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        return {"error": "Erro interno do servidor"}, 500


@app.route("/excluir_conta", methods=["POST"])
@login_required
def excluir_conta():
    """Exclui permanentemente a conta do usuário"""
    try:
        # Remover foto se existir
        if current_user.photo:
            filepath = os.path.join(
                app.root_path, "static", "imagens", current_user.photo
            )
            if os.path.exists(filepath):
                os.remove(filepath)

        # Obter ID do usuário antes de deletar
        user_id = current_user.id

        # Logout do usuário
        logout_user()

        # Deletar todas as atividades e matérias do usuário
        Atividade.query.filter_by(user_id=user_id).delete()
        Materia.query.filter_by(user_id=user_id).delete()

        # Deletar o usuário
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

        return {"success": True, "message": "Conta excluída com sucesso!"}, 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir conta: {e}")
        return {"success": False, "message": "Erro interno do servidor"}, 500


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
        "gif",
    }


@app.route("/salvar_configuracoes", methods=["POST"])
@login_required
def salvar_configuracoes():
    """Salva as configurações do usuário"""
    flash("Configurações salvas com sucesso!", "success")
    return redirect(url_for("configuracoes"))


@app.route("/pomodoro")
@login_required
def pomodoro():
    """Página do timer Pomodoro"""
    return render_template("pomodoro.html")


@app.route("/salvar_sessao_pomodoro", methods=["POST"])
@login_required
def salvar_sessao_pomodoro():
    """Salva uma sessão de Pomodoro concluída"""
    data = request.get_json()

    materia = data.get("materia", "Geral")
    tipo = data.get("tipo", "trabalho")  # trabalho ou pausa
    duracao = data.get("duracao", 25)  # em minutos

    try:
        # Criar notificação de conquista
        if tipo == "trabalho":
            criar_notificacao(
                user_id=current_user.id,
                tipo="conquista",
                titulo="🍅 Pomodoro Concluído!",
                mensagem=f"Você completou {duracao} minutos de foco em {materia}. Continue assim!",
                icone="fa-trophy",
            )

        return {"success": True, "message": "Sessão salva com sucesso!"}, 200
    except Exception as e:
        return {"success": False, "message": str(e)}, 500


# =============== SISTEMA DE METAS ===============


@app.route("/metas")
@login_required
def listar_metas():
    """Lista todas as metas do usuário"""
    status_filtro = request.args.get("status", "todos")
    query = Meta.query.filter_by(user_id=current_user.id)

    if status_filtro != "todos":
        query = query.filter_by(status=status_filtro)

    metas = query.order_by(Meta.data_criacao.desc()).all()
    return render_template(
        "listar_metas.html", metas=metas, status_filtro=status_filtro
    )


@app.route("/criar_meta", methods=["GET", "POST"])
@login_required
def criar_meta():
    """Cria uma nova meta"""
    materias = Materia.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        titulo = Validadores.sanitizar_texto(request.form.get("titulo", "").strip())
        descricao = Validadores.sanitizar_texto(
            request.form.get("descricao", "").strip()
        )
        data_limite = request.form.get("data_limite", "").strip()
        materia_id = request.form.get("materia_id", "").strip()

        # Validações
        if not titulo or len(titulo) < 3:
            flash("Título deve ter no mínimo 3 caracteres.", "error")
            return redirect(url_for("criar_meta"))

        if len(titulo) > 200:
            flash("Título deve ter no máximo 200 caracteres.", "error")
            return redirect(url_for("criar_meta"))

        try:
            nova_meta = Meta(
                user_id=current_user.id,
                titulo=titulo,
                descricao=descricao if descricao else None,
                data_limite=data_limite if data_limite else None,
                materia_id=int(materia_id) if materia_id else None,
            )
            db.session.add(nova_meta)
            db.session.commit()

            # Criar notificação
            criar_notificacao(
                user_id=current_user.id,
                tipo="sistema",
                titulo="Meta Criada! 🎯",
                mensagem=f"Meta '{titulo}' foi criada com sucesso.",
                link="/metas",
                icone="fa-target",
            )

            flash("Meta criada com sucesso!", "success")
            return redirect(url_for("listar_metas"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao criar meta: {str(e)}", "error")

    return render_template("criar_meta.html", materias=materias)


@app.route("/editar_meta/<int:meta_id>", methods=["GET", "POST"])
@login_required
def editar_meta(meta_id):
    """Edita uma meta existente"""
    meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first()
    if not meta:
        flash("Meta não encontrada.", "error")
        return redirect(url_for("listar_metas"))

    materias = Materia.query.filter_by(user_id=current_user.id).all()

    if request.method == "POST":
        titulo = Validadores.sanitizar_texto(request.form.get("titulo", "").strip())
        descricao = Validadores.sanitizar_texto(
            request.form.get("descricao", "").strip()
        )
        data_limite = request.form.get("data_limite", "").strip()
        materia_id = request.form.get("materia_id", "").strip()
        status = request.form.get("status", "ativo")

        # Validações
        if not titulo or len(titulo) < 3:
            flash("Título deve ter no mínimo 3 caracteres.", "error")
            return redirect(url_for("editar_meta", meta_id=meta_id))

        if len(titulo) > 200:
            flash("Título deve ter no máximo 200 caracteres.", "error")
            return redirect(url_for("editar_meta", meta_id=meta_id))

        try:
            meta.titulo = titulo
            meta.descricao = descricao if descricao else None
            meta.data_limite = data_limite if data_limite else None
            meta.materia_id = int(materia_id) if materia_id else None
            meta.status = status
            db.session.commit()

            flash("Meta atualizada com sucesso!", "success")
            return redirect(url_for("listar_metas"))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar meta: {str(e)}", "error")

    return render_template("editar_meta.html", meta=meta, materias=materias)


@app.route("/deletar_meta/<int:meta_id>", methods=["POST"])
@login_required
def deletar_meta(meta_id):
    """Deleta uma meta"""
    meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first()
    if not meta:
        flash("Meta não encontrada.", "error")
        return redirect(url_for("listar_metas"))

    try:
        db.session.delete(meta)
        db.session.commit()
        flash("Meta deletada com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao deletar meta.", "error")

    return redirect(url_for("listar_metas"))


@app.route("/concluir_meta/<int:meta_id>", methods=["POST"])
@login_required
def concluir_meta(meta_id):
    """Marca uma meta como concluída"""
    meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first()
    if not meta:
        flash("Meta não encontrada.", "error")
        return redirect(url_for("listar_metas"))

    try:
        meta.status = "concluido"
        db.session.commit()

        # Criar notificação de conquista
        criar_notificacao(
            user_id=current_user.id,
            tipo="conquista",
            titulo="Meta Concluída! 🏆",
            mensagem=f"Parabéns! Você concluiu a meta '{meta.titulo}'.",
            icone="fa-trophy",
        )

        # Verificar badge
        verificar_e_conceder_badge(current_user.id, "primeira_meta_concluida")

        flash("Meta marcada como concluída!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao concluir meta.", "error")

    return redirect(url_for("listar_metas"))


# =============== CALENDÁRIO VISUAL ===============


@app.route("/calendario")
@login_required
def calendario():
    """Página do calendário interativo"""
    return render_template("calendario.html")


@app.route("/api/calendario_eventos")
@login_required
def api_calendario_eventos():
    """API para obter eventos do calendário"""
    eventos = []

    # Adicionar atividades com data
    atividades = (
        Atividade.query.filter_by(user_id=current_user.id)
        .filter(Atividade.data.isnot(None))
        .all()
    )
    for atividade in atividades:
        eventos.append(
            {
                "id": f"atividade_{atividade.id}",
                "title": f"📚 {atividade.assunto_primario}",
                "start": atividade.data.isoformat(),
                "backgroundColor": "#1a73e8",
                "borderColor": "#0d47a1",
                "extendedProps": {
                    "tipo": "atividade",
                    "materia": atividade.materia,
                    "descricao": atividade.descricao,
                    "duracao": atividade.duracao,
                },
            }
        )

    # Adicionar metas com data limite
    from sqlalchemy.orm import joinedload

    metas = (
        Meta.query.filter_by(user_id=current_user.id)
        .filter(Meta.data_limite.isnot(None))
        .options(joinedload(Meta.materia))
        .all()
    )
    for meta in metas:
        cor = "#2e7d32" if meta.status == "concluido" else "#ff9800"
        eventos.append(
            {
                "id": f"meta_{meta.id}",
                "title": f"🎯 {meta.titulo}",
                "start": meta.data_limite.isoformat(),
                "backgroundColor": cor,
                "borderColor": cor,
                "extendedProps": {
                    "tipo": "meta",
                    "status": meta.status,
                    "descricao": meta.descricao,
                    "materia": meta.materia.nome if meta.materia else None,
                },
            }
        )

    return {"eventos": eventos}


@app.route("/alternar_tema", methods=["POST"])
@login_required
def alternar_tema():
    """Alterna entre modo claro e escuro"""
    data = request.get_json()
    if data and "tema_escuro" in data:
        current_user.tema_escuro = data["tema_escuro"]
    else:
        current_user.tema_escuro = not current_user.tema_escuro
    db.session.commit()
    return {"success": True, "tema_escuro": current_user.tema_escuro}


@app.route("/atualizar_configuracoes", methods=["POST"])
@login_required
def atualizar_configuracoes():
    """Atualiza configurações do usuário"""
    data = request.get_json()
    if not data:
        return {"success": False, "message": "Dados inválidos"}, 400

    try:
        if "notificacoes_email" in data:
            current_user.notificacoes_email = data["notificacoes_email"]
        if "notificacoes_push" in data:
            current_user.notificacoes_push = data["notificacoes_push"]
        if "lembretes" in data:
            current_user.lembretes = data["lembretes"]
        if "idioma" in data:
            current_user.idioma = data["idioma"]

        db.session.commit()
        return {"success": True, "message": "Configurações atualizadas com sucesso"}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}, 500


# =============== HANDLER DE ERROS ===============


@app.errorhandler(404)
def not_found(error):
    flash("Página não encontrada.", "error")
    return redirect(url_for("dashboard"))


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash("Erro interno do servidor. Tente novamente.", "error")
    return redirect(url_for("dashboard"))


@app.errorhandler(403)
def forbidden(error):
    flash("Acesso negado.", "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)

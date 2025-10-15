from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from flask_bcrypt import (
    Bcrypt,
)
import os
from dotenv import load_dotenv

import requests

from models import (
    db,
    User,
    Materia,
    Atividade,
)

# Carregar variáveis de ambiente
load_dotenv()


app = Flask(__name__)

# Configuração para MySQL usando variáveis de ambiente
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "pratica_profissional")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "Chave1234")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    try:
        db.create_all()
        print("✅ Banco de dados conectado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco de dados: {e}")
        print("Verifique suas credenciais no arquivo .env")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def register():
    get_flashed_messages()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash("Este email já está cadastrado.", "error")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash("Cadastro realizado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    get_flashed_messages()

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos.", "error")

    return render_template("login.html")


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

    return render_template("dashboard.html", artigos=artigos)


@app.route("/adicionar_materia", methods=["POST"])
@login_required
def adicionar_materia():
    nome_materia = request.form.get("materia")
    if not nome_materia:
        flash("Por favor, adicione o nome da matéria.", "error")
    else:
        nova_materia = Materia(nome=nome_materia, user_id=current_user.id)
        db.session.add(nova_materia)
        db.session.commit()
        flash("Matéria adicionada com sucesso!", "success")
    return redirect(url_for("dashboard"))


@app.route("/adicionar_atividade", methods=["GET", "POST"])
@login_required
def adicionar_atividade():
    if request.method == "POST":
        materia = request.form.get("materia")
        assunto = request.form.get("assunto_primario")
        descricao = request.form.get("descricao")
        duracao = request.form.get("duracao")

        if not materia or not assunto:
            flash("Informe pelo menos a matéria e o assunto primário.", "error")
        else:
            nova_atividade = Atividade(
                materia=materia,
                assunto_primario=assunto,
                descricao=descricao,
                duracao=duracao,
                user_id=current_user.id,
            )
            db.session.add(nova_atividade)
            db.session.commit()
            flash("Atividade adicionada com sucesso!", "success")
            return redirect(url_for("listar_atividades"))

    atividades = Atividade.query.filter_by(user_id=current_user.id).all()
    return render_template("adicionar_atividade.html", atividades=atividades)


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
        assunto = request.form.get("assunto_primario")
        descricao = request.form.get("descricao")
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


@app.route("/ajuda")
@login_required
def ajuda():
    return render_template("ajuda.html")


@app.route("/listar_noticacoes")
@login_required
def listar_notificacoes():
    return render_template("listar_notificacoes.html")


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


if __name__ == "__main__":
    app.run(debug=True)

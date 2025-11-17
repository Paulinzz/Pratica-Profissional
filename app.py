from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from flask_bcrypt import (
    Bcrypt,
)
import os
from dotenv import load_dotenv
from sqlalchemy import func
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

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
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash("Este email já está cadastrado.", "error")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(name=name, email=email, password=hashed_password)

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

    # Dados para gráficos
    materias_count = (
        db.session.query(Atividade.materia, func.count(Atividade.id))
        .filter_by(user_id=current_user.id)
        .group_by(Atividade.materia)
        .all()
    )
    activities_per_day = (
        db.session.query(func.date(Atividade.data_criacao), func.count(Atividade.id))
        .filter_by(user_id=current_user.id)
        .group_by(func.date(Atividade.data_criacao))
        .all()
    )

    # Preparar dados para Chart.js
    labels_dash = [str(row[0]) for row in activities_per_day]
    data_dash = [row[1] for row in activities_per_day]
    labels_materias = [row[0] for row in materias_count]
    data_materias = [row[1] for row in materias_count]

    return render_template(
        "dashboard.html",
        artigos=artigos,
        labels_dash=labels_dash,
        data_dash=data_dash,
        labels_materias=labels_materias,
        data_materias=data_materias,
    )


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
        data = request.form.get("data")

        if not materia or not assunto:
            flash("Informe pelo menos a matéria e o assunto primário.", "error")
        else:
            try:
                nova_atividade = Atividade(
                    materia=materia,
                    assunto_primario=assunto,
                    descricao=descricao,
                    duracao=duracao,
                    data=data if data else None,
                    user_id=current_user.id,
                )
                db.session.add(nova_atividade)
                db.session.commit()
                flash("Atividade adicionada com sucesso!", "success")
                return redirect(url_for("adicionar_atividade"))
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao adicionar atividade: {str(e)}", "error")
                print(f"ERRO: {e}")

    atividades = (
        Atividade.query.filter_by(user_id=current_user.id)
        .order_by(Atividade.data_criacao.desc())
        .limit(5)
        .all()
    )

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


# Adicione estas rotas no seu app.py, logo antes da rota /ajuda ou no final antes do if __name__ == "__main__":


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

    return render_template(
        "perfil.html",
        atividades_count=atividades_count,
        materias_count=materias_count,
        sequencia=sequencia,
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
    nome = request.form.get("nome")
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
    """Permite ao usuário baixar todos os seus dados"""
    try:
        # Coletar dados do usuário
        user_data = {
            "usuario": {
                "id": current_user.id,
                "email": current_user.email,
                "nome": current_user.name,
                "data_cadastro": (
                    current_user.date_created.isoformat()
                    if hasattr(current_user, "date_created")
                    else None
                ),
                "foto": current_user.photo,
            },
            "materias": [
                {
                    "id": materia.id,
                    "nome": materia.nome,
                    "data_criacao": (
                        materia.date_created.isoformat()
                        if hasattr(materia, "date_created")
                        else None
                    ),
                }
                for materia in current_user.materias
            ],
            "atividades": [
                {
                    "id": atividade.id,
                    "materia": atividade.materia,
                    "assunto_primario": atividade.assunto_primario,
                    "descricao": atividade.descricao,
                    "duracao": atividade.duracao,
                    "data": atividade.data.isoformat() if atividade.data else None,
                    "data_criacao": atividade.data_criacao.isoformat(),
                }
                for atividade in current_user.atividades
            ],
            "exportado_em": datetime.utcnow().isoformat(),
        }

        # Converter para JSON
        import json

        json_data = json.dumps(user_data, ensure_ascii=False, indent=2)

        # Criar resposta com arquivo para download
        from flask import Response

        response = Response(
            json_data,
            mimetype="application/json",
            headers={
                "Content-Disposition": "attachment;filename=meus_dados_focusup.json"
            },
        )

        return response

    except Exception as e:
        print(f"Erro ao baixar dados: {e}")
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
    # Aqui você pode adicionar lógica para salvar preferências em uma tabela separada
    # Por enquanto, apenas retorna sucesso
    flash("Configurações salvas com sucesso!", "success")
    return redirect(url_for("configuracoes"))


if __name__ == "__main__":
    app.run(debug=True)

from flask import *

from flask_sqlalchemy import SQLAlchemy

from flask_login import *

from flask_bcrypt import (
    Bcrypt,
)  # importação do Bcrypt para criptografia de senhas, substituindo a importação de werkzeug.security

from models import (
    db,
    Usuario,
)  # Importação corrigida para o novo arquivo models.py, como especificado pelo coordenador

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "Chave1234"

db.init_app(app)
bcrypt = Bcrypt(app)

# Configura o gerenciador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """Função para carregar o usuário a partir do ID."""
    return Usuario.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cadastro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Verifica se o email já existe
        user_exists = Usuario.query.filter_by(email=email).first()
        if user_exists:
            flash("Este email já está cadastrado.", "danger")
            return redirect(url_for("register"))

        # Criptografa a senha antes de salvar
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = Usuario(email=email, password=hashed_password)

        # Adiciona o novo usuário ao banco de dados
        db.session.add(new_user)
        db.session.commit()

        flash("Cadastro realizado com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = Usuario.query.filter_by(email=email).first()

        # Verifica se o usuário existe e se a senha está correta (usando Bcrypt)
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Rota para deslogar o usuário."""
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)

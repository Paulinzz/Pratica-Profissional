from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
from flask_bcrypt import (
    Bcrypt,
) 

from models import (
    db,
    User,
    Materia,
    Atividade,
) 

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "Chave1234"

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash("Este email já está cadastrado.", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(email=email, password=hashed_password)

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
        user = User.query.filter_by(email=email).first()

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
    logout_user()
    flash("Você foi desconectado.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/adicionar_materia", methods=["POST"])
@login_required
def adicionar_materia():
    nome_materia = request.form.get("materia")
    if not nome_materia:
        flash("Por favor, adicione o nome da matéria.", "danger")
    else:
        nova_materia = Materia(nome=nome_materia, user_id=current_user.id)
        db.session.add(nova_materia)
        db.session.commit()
        flash("Matéria adicionada com sucesso!", "success")
    return redirect(url_for("dashboard"))

@app.route("/adicionar_atividade", methods=["POST"])
@login_required
def adicionar_atividade():
    nome_atividade = request.form.get("atividade")
    if not nome_atividade:
        flash("Por favor, adicione o nome da atividade.", "danger")
    else:
        nova_atividade = Atividade(nome=nome_atividade, user_id=current_user.id)
        db.session.add(nova_atividade)
        db.session.commit()
        flash("Atividade adicionada com sucesso!", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
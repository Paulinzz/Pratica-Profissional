from datetime import datetime, timedelta
import secrets

from flask import flash, get_flashed_messages, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from flask_mail import Message

from models.models import User, db
from services.app_service import (
    criar_notificacao,
    tentativas_cadastro,
    tentativas_login,
    verificar_rate_limit,
)
from services.validation_service import Validadores


def init_auth_routes(app, bcrypt, mail):
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/cadastro", methods=["GET", "POST"])
    def register():
        get_flashed_messages()

        if request.method == "POST":
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

            valido, msg = Validadores.validar_nome(name)
            if not valido:
                flash(msg, "error")
                return redirect(url_for("register"))

            valido, msg = Validadores.validar_email(email)
            if not valido:
                flash(msg, "error")
                return redirect(url_for("register"))

            valido, msg = Validadores.validar_senha(password)
            if not valido:
                flash(msg, "error")
                return redirect(url_for("register"))

            if User.query.filter_by(email=email).first():
                flash("Este email já está cadastrado.", "error")
                return redirect(url_for("register"))

            try:
                hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
                new_user = User(name=name, email=email, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()

                criar_notificacao(
                    user_id=new_user.id,
                    tipo="sistema",
                    titulo="Bem-vindo ao FocusUp!",
                    mensagem="Sua conta foi criada com sucesso! Comece adicionando suas primeiras atividades.",
                    link="/dashboard",
                    icone="fa-rocket",
                )

                flash(
                    "Cadastro realizado com sucesso! Faça login para continuar.",
                    "success",
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
            ip = request.remote_addr
            permitido, mensagem = verificar_rate_limit(
                ip, tentativas_login, max_tentativas=5
            )
            if not permitido:
                flash(mensagem, "error")
                return redirect(url_for("login"))

            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            valido, _ = Validadores.validar_email(email)
            if not valido:
                flash("Email ou senha inválidos.", "error")
                return redirect(url_for("login"))

            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)
                criar_notificacao(
                    user_id=user.id,
                    tipo="sistema",
                    titulo="Login realizado",
                    mensagem=f"Você fez login em {datetime.utcnow().strftime('%d/%m/%Y às %H:%M')}",
                    icone="fa-right-to-bracket",
                )
                flash("Login realizado com sucesso!", "success")
                return redirect(url_for("dashboard"))

            flash("Email ou senha inválidos.", "error")
            return redirect(url_for("login"))

        return render_template("login.html")

    @app.route("/esqueci_senha", methods=["GET", "POST"])
    def esqueci_senha():
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            valido, msg = Validadores.validar_email(email)
            if not valido:
                flash(msg, "error")
                return redirect(url_for("esqueci_senha"))

            user = User.query.filter_by(email=email).first()
            if user:
                token = secrets.token_urlsafe(32)
                expires = datetime.utcnow() + timedelta(hours=1)
                user.reset_token = token
                user.reset_expires = expires
                db.session.commit()
                try:
                    msg = Message("Redefinição de Senha - FocusUp", recipients=[email])
                    msg.body = f"""
Olá {user.name or 'usuário'},

Você solicitou a redefinição de senha da sua conta no FocusUp.

Para redefinir sua senha, clique no link abaixo:
{url_for('resetar_senha', token=token, _external=True)}

Este link expira em 1 hora.

Se você não solicitou esta redefinição, ignore este email.
                    """
                    mail.send(msg)
                    flash(
                        "Email de redefinição enviado! Verifique sua caixa de entrada.",
                        "success",
                    )
                except Exception:
                    flash("Erro ao enviar email. Tente novamente mais tarde.", "error")
            else:
                flash(
                    "Se o email estiver cadastrado, você receberá instruções para redefinir a senha.",
                    "info",
                )

            return redirect(url_for("login"))

        return render_template("esqueci_senha.html")

    @app.route("/resetar_senha/<token>", methods=["GET", "POST"])
    def resetar_senha(token):
        user = User.query.filter_by(reset_token=token).first()
        if not user or not user.reset_expires or user.reset_expires < datetime.utcnow():
            flash("Link de redefinição inválido ou expirado.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            senha = request.form.get("senha", "")
            confirmar_senha = request.form.get("confirmar_senha", "")

            if senha != confirmar_senha:
                flash("As senhas não coincidem.", "error")
                return redirect(url_for("resetar_senha", token=token))

            valido, msg = Validadores.validar_senha(senha)
            if not valido:
                flash(msg, "error")
                return redirect(url_for("resetar_senha", token=token))

            user.password = bcrypt.generate_password_hash(senha).decode("utf-8")
            user.reset_token = None
            user.reset_expires = None
            db.session.commit()

            flash("Senha redefinida com sucesso! Faça login com sua nova senha.", "success")
            return redirect(url_for("login"))

        return render_template("resetar_senha.html", token=token)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Você foi desconectado.", "info")
        return redirect(url_for("index"))

import logging
import os
from datetime import datetime, timedelta

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_mail import Message

from models.models import ContatoMensagem, db
from services.validation_service import Validadores

contact_logger = logging.getLogger("contact")

ASSUNTOS = {
    "duvida": "Dúvida sobre o FocusUp",
    "sugestao": "Sugestão ou ideia",
    "conta": "Problema com minha conta",
    "parceria": "Parceria ou projeto",
    "outro": "Outro assunto",
}

LIMITE_POR_HORA = 3


def _limpar_linha(texto):
    """Remove quebras de linha (evita header injection em e-mails)."""
    return " ".join((texto or "").split())


def _validar(form):
    dados = {
        "nome": _limpar_linha(form.get("nome")),
        "email": form.get("email", "").strip(),
        "assunto": form.get("assunto", "").strip(),
        "mensagem": form.get("mensagem", "").strip(),
    }
    erros = []

    if not 2 <= len(dados["nome"]) <= 100:
        erros.append("Informe seu nome (2 a 100 caracteres).")

    valido, msg = Validadores.validar_email(dados["email"])
    if not valido:
        erros.append(msg + ".")

    if dados["assunto"] not in ASSUNTOS:
        erros.append("Selecione um assunto válido.")

    if not 10 <= len(dados["mensagem"]) <= 3000:
        erros.append("A mensagem deve ter entre 10 e 3000 caracteres.")

    return dados, erros


def _enviar_email(contato):
    """Encaminha a mensagem para a equipe se CONTACT_EMAIL estiver configurado."""
    destino = os.getenv("CONTACT_EMAIL")
    if not destino:
        return
    try:
        mail = current_app.extensions["mail"]
        msg = Message(
            f"[FocusUp Contato] {ASSUNTOS.get(contato.assunto)} - {contato.nome}",
            recipients=[destino],
            reply_to=contato.email,
        )
        msg.body = (
            f"Nome: {contato.nome}\n"
            f"E-mail: {contato.email}\n"
            f"Assunto: {ASSUNTOS.get(contato.assunto)}\n"
            f"Usuário logado: {'sim (ID ' + str(contato.user_id) + ')' if contato.user_id else 'não'}\n\n"
            f"Mensagem:\n{contato.mensagem}\n"
        )
        mail.send(msg)
    except Exception:
        contact_logger.error("Falha ao enviar e-mail de contato", exc_info=True)


def init_contact_routes(app):
    # Página pública: qualquer visitante pode entrar em contato
    @app.route("/contato", methods=["GET", "POST"])
    def contato():
        email_suporte = os.getenv("CONTACT_EMAIL_PUBLIC", "suporte@focusup.com.br")

        def render(form):
            return render_template(
                "contato.html",
                form=form,
                assuntos=ASSUNTOS,
                email_suporte=email_suporte,
            )

        if request.method == "POST":
            # Honeypot: campo invisível que só robôs preenchem
            if request.form.get("website"):
                contact_logger.warning("Contato descartado pelo honeypot")
                flash("Mensagem enviada com sucesso!", "success")
                return redirect(url_for("contato"))

            dados, erros = _validar(request.form)

            # Limite simples por e-mail contra spam
            uma_hora_atras = datetime.utcnow() - timedelta(hours=1)
            recentes = ContatoMensagem.query.filter(
                ContatoMensagem.email == dados["email"],
                ContatoMensagem.data_criacao >= uma_hora_atras,
            ).count()
            if recentes >= LIMITE_POR_HORA:
                erros.append(
                    "Você já enviou várias mensagens na última hora. "
                    "Tente novamente mais tarde."
                )

            if erros:
                for erro in erros:
                    flash(erro, "error")
                return render(dados)

            try:
                contato_msg = ContatoMensagem(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    nome=dados["nome"],
                    email=dados["email"],
                    assunto=dados["assunto"],
                    mensagem=dados["mensagem"],
                )
                db.session.add(contato_msg)
                db.session.commit()
                contact_logger.info(f"Mensagem de contato #{contato_msg.id} recebida")
            except Exception:
                db.session.rollback()
                contact_logger.error(
                    "Erro ao salvar mensagem de contato", exc_info=True
                )
                flash("Erro ao enviar a mensagem. Tente novamente mais tarde.", "error")
                return render(dados)

            _enviar_email(contato_msg)
            flash(
                "Mensagem enviada com sucesso! Responderemos no e-mail informado.",
                "success",
            )
            return redirect(url_for("contato"))

        # GET: se estiver logado, preenche nome e e-mail
        form = {}
        if current_user.is_authenticated:
            form = {"nome": current_user.name or "", "email": current_user.email}
        return render(form)

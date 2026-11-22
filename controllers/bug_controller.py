import logging
import os
from datetime import datetime, timedelta

from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_mail import Message

from models.models import BugReport, db
from services.app_service import criar_notificacao

bug_logger = logging.getLogger("bug")

CATEGORIAS = {
    "visual": "Visual / layout",
    "funcional": "Algo não funciona como deveria",
    "desempenho": "Lentidão ou travamentos",
    "dados": "Dados incorretos ou perdidos",
    "pomodoro": "Modo Pomodoro",
    "outro": "Outro",
}

GRAVIDADES = {
    "baixa": "Baixa - incômodo, mas consigo usar",
    "media": "Média - atrapalha o uso",
    "alta": "Alta - não consigo usar uma função",
}

LIMITE_POR_HORA = 5


def _validar(form):
    """Retorna (dados_limpos, lista_de_erros)."""
    dados = {
        "titulo": form.get("titulo", "").strip(),
        "categoria": form.get("categoria", "").strip(),
        "gravidade": form.get("gravidade", "").strip(),
        "pagina": form.get("pagina", "").strip(),
        "descricao": form.get("descricao", "").strip(),
        "passos": form.get("passos", "").strip(),
    }
    erros = []

    if not 5 <= len(dados["titulo"]) <= 150:
        erros.append("O título deve ter entre 5 e 150 caracteres.")
    if dados["categoria"] not in CATEGORIAS:
        erros.append("Selecione uma categoria válida.")
    if dados["gravidade"] not in GRAVIDADES:
        erros.append("Selecione a gravidade do problema.")
    if not 10 <= len(dados["descricao"]) <= 2000:
        erros.append("Descreva o problema com 10 a 2000 caracteres.")
    if len(dados["passos"]) > 2000:
        erros.append("Os passos para reproduzir devem ter no máximo 2000 caracteres.")
    if len(dados["pagina"]) > 255:
        dados["pagina"] = dados["pagina"][:255]

    return dados, erros


def _enviar_email(report):
    """Avisa a equipe por e-mail, se BUG_REPORT_EMAIL estiver configurado."""
    destino = os.getenv("BUG_REPORT_EMAIL")
    if not destino:
        return
    try:
        mail = current_app.extensions["mail"]
        msg = Message(
            f"[FocusUp] Bug #{report.id} ({report.gravidade}): {report.titulo}",
            recipients=[destino],
        )
        msg.body = (
            f"Reportado por: {current_user.name or current_user.email} "
            f"({current_user.email})\n"
            f"Categoria: {CATEGORIAS.get(report.categoria)}\n"
            f"Gravidade: {GRAVIDADES.get(report.gravidade)}\n"
            f"Página: {report.pagina or '-'}\n"
            f"Navegador: {report.user_agent or '-'}\n\n"
            f"Descrição:\n{report.descricao}\n\n"
            f"Passos para reproduzir:\n{report.passos or '-'}\n"
        )
        mail.send(msg)
    except Exception:
        bug_logger.error("Falha ao enviar e-mail do bug report", exc_info=True)


def init_bug_routes(app):
    @app.route("/reportar_bug", methods=["GET", "POST"])
    @login_required
    def reportar_bug():
        if request.method == "POST":
            dados, erros = _validar(request.form)

            # Limite simples contra spam: máx. 5 reports por hora por usuário
            uma_hora_atras = datetime.utcnow() - timedelta(hours=1)
            recentes = BugReport.query.filter(
                BugReport.user_id == current_user.id,
                BugReport.data_criacao >= uma_hora_atras,
            ).count()
            if recentes >= LIMITE_POR_HORA:
                erros.append(
                    "Você já enviou vários relatórios na última hora. "
                    "Tente novamente mais tarde."
                )

            if erros:
                for erro in erros:
                    flash(erro, "error")
                return render_template(
                    "reportar_bug.html",
                    form=dados,
                    categorias=CATEGORIAS,
                    gravidades=GRAVIDADES,
                )

            try:
                report = BugReport(
                    user_id=current_user.id,
                    titulo=dados["titulo"],
                    categoria=dados["categoria"],
                    gravidade=dados["gravidade"],
                    pagina=dados["pagina"] or None,
                    descricao=dados["descricao"],
                    passos=dados["passos"] or None,
                    user_agent=(request.headers.get("User-Agent") or "")[:255],
                )
                db.session.add(report)
                db.session.commit()
                bug_logger.info(
                    f"Bug #{report.id} reportado por usuário {current_user.id}"
                )
            except Exception:
                db.session.rollback()
                bug_logger.error("Erro ao salvar bug report", exc_info=True)
                flash("Erro ao enviar o relatório. Tente novamente mais tarde.", "error")
                return render_template(
                    "reportar_bug.html",
                    form=dados,
                    categorias=CATEGORIAS,
                    gravidades=GRAVIDADES,
                )

            _enviar_email(report)
            criar_notificacao(
                current_user.id,
                "sistema",
                "Bug reportado",
                f"Recebemos seu relatório #{report.id}: {report.titulo}. Obrigado!",
                icone="fa-bug",
            )
            flash("Relatório enviado com sucesso! Obrigado por ajudar a melhorar o FocusUp.", "success")
            return redirect(url_for("dashboard"))

        # GET: preenche a página de origem automaticamente
        origem = request.args.get("pagina") or request.referrer or ""
        form = {"pagina": origem.replace(request.host_url, "/")[:255]}
        return render_template(
            "reportar_bug.html",
            form=form,
            categorias=CATEGORIAS,
            gravidades=GRAVIDADES,
        )
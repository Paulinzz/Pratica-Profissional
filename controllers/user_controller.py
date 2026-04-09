import os
from datetime import datetime, timedelta, timezone
from io import BytesIO

from flask import Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, logout_user
from werkzeug.utils import secure_filename

from models.models import Atividade, Materia, Meta, UserBadge, User, db
from services.app_service import allowed_file
from services.validation_service import Validadores


def init_user_routes(app, bcrypt):
    @app.route("/perfil")
    @login_required
    def perfil():
        atividades_count = Atividade.query.filter_by(user_id=current_user.id).count()
        materias_count = Materia.query.filter_by(user_id=current_user.id).count()
        hoje = datetime.utcnow().date()
        sequencia = 0
        for i in range(30):
            data = hoje - timedelta(days=i)
            if (
                Atividade.query.filter_by(user_id=current_user.id)
                .filter(db.func.date(Atividade.data_criacao) == data)
                .first()
            ):
                sequencia += 1
            else:
                break
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
        return render_template("configuracoes.html")

    @app.route("/atualizar_perfil", methods=["POST"])
    @login_required
    def atualizar_perfil():
        nome = Validadores.sanitizar_texto(request.form.get("nome"))
        email = request.form.get("email")
        try:
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
        senha_atual = request.form.get("senha_atual")
        nova_senha = request.form.get("nova_senha")
        confirmar_senha = request.form.get("confirmar_senha")
        if not bcrypt.check_password_hash(current_user.password, senha_atual):
            flash("Senha atual incorreta!", "error")
            return redirect(url_for("perfil"))
        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem!", "error")
            return redirect(url_for("perfil"))
        try:
            current_user.password = bcrypt.generate_password_hash(nova_senha).decode("utf-8")
            db.session.commit()
            flash("Senha alterada com sucesso!", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao alterar senha: {str(e)}", "error")
        return redirect(url_for("perfil"))

    @app.route("/upload_foto", methods=["POST"])
    @login_required
    def upload_foto():
        if "foto" not in request.files:
            flash("Nenhum arquivo enviado.", "error")
            return redirect(url_for("perfil"))
        file = request.files["foto"]
        if file.filename == "":
            flash("Nenhum arquivo selecionado.", "error")
            return redirect(url_for("perfil"))
        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{current_user.id}_{file.filename}")
            upload_dir = os.path.join(app.root_path, "static", "imagens")
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
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
        try:
            if current_user.photo:
                filepath = os.path.join(app.root_path, "static", "imagens", current_user.photo)
                if os.path.exists(filepath):
                    os.remove(filepath)
            current_user.photo = None
            db.session.commit()
            return {"success": True, "message": "Foto removida com sucesso!"}, 200
        except Exception as e:
            db.session.rollback()
            return {"success": False, "message": str(e)}, 500

    @app.route("/baixar_dados")
    @login_required
    def baixar_dados():
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
        except ImportError:
            return {
                "error": "Biblioteca PDF não instalada. Execute: pip install reportlab"
            }, 500

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        title_style = ParagraphStyle(
            "CustomTitle", parent=styles["Heading1"], fontSize=24, spaceAfter=30, alignment=1
        )
        story.append(Paragraph("Relatório de Dados - FocusUp", title_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Informações do Usuário", styles["Heading2"]))
        user_data = [
            ["ID", str(current_user.id)],
            ["Nome", current_user.name or "N/A"],
            ["Email", current_user.email],
            ["Foto", current_user.photo or "N/A"],
        ]
        user_table = Table(user_data, colWidths=[2 * inch, 4 * inch])
        user_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(user_table)
        story.append(Spacer(1, 20))

        story.append(Paragraph("Matérias Cadastradas", styles["Heading2"]))
        if current_user.materias:
            materias_data = [["Nome"]]
            for materia in current_user.materias:
                materias_data.append([materia.nome])
            materias_table = Table(materias_data, colWidths=[6 * inch])
            materias_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 1, colors.black)]))
            story.append(materias_table)
        else:
            story.append(Paragraph("Nenhuma matéria cadastrada.", styles["Normal"]))
        story.append(Spacer(1, 20))

        total_atividades = len(current_user.atividades)
        total_materias = len(current_user.materias)
        tempo_total = 0
        for atividade in current_user.atividades:
            if atividade.duracao:
                try:
                    horas, minutos = map(int, atividade.duracao.split(":"))
                    tempo_total += horas * 60 + minutos
                except Exception:
                    pass
        brasilia_tz = timezone(timedelta(hours=-3))
        data_exportacao = datetime.now(brasilia_tz).strftime("%d/%m/%Y %H:%M:%S")
        stats_data = [
            ["Total de Atividades", str(total_atividades)],
            ["Total de Matérias", str(total_materias)],
            ["Tempo Total Estudado", f"{tempo_total // 60}h {tempo_total % 60}min"],
            ["Data de Exportação", data_exportacao + " (Horário de Brasília)"],
        ]
        stats_table = Table(stats_data, colWidths=[3 * inch, 3 * inch])
        stats_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 1, colors.black)]))
        story.append(stats_table)

        doc.build(story)
        buffer.seek(0)
        return Response(
            buffer.getvalue(),
            mimetype="application/pdf",
            headers={
                "Content-Disposition": f"attachment;filename=relatorio_dados_focusup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
            },
        )

    @app.route("/excluir_conta", methods=["POST"])
    @login_required
    def excluir_conta():
        try:
            if current_user.photo:
                filepath = os.path.join(app.root_path, "static", "imagens", current_user.photo)
                if os.path.exists(filepath):
                    os.remove(filepath)
            user_id = current_user.id
            logout_user()
            Atividade.query.filter_by(user_id=user_id).delete()
            Materia.query.filter_by(user_id=user_id).delete()
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
            return {"success": True, "message": "Conta excluída com sucesso!"}, 200
        except Exception:
            db.session.rollback()
            return {"success": False, "message": "Erro interno do servidor"}, 500

    @app.route("/salvar_configuracoes", methods=["POST"])
    @login_required
    def salvar_configuracoes():
        flash("Configurações salvas com sucesso!", "success")
        return redirect(url_for("configuracoes"))

    @app.route("/alternar_tema", methods=["POST"])
    @login_required
    def alternar_tema():
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

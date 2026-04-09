import requests
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from models.models import Atividade, Materia, Meta, Notificacao, db
from services.app_service import criar_notificacao, parse_date_field, parse_duration_to_minutes
from services.badge_service import verificar_e_conceder_badge
from services.validation_service import Validadores


traducoes_comuns = {
    "machine learning": "aprendizado de máquina",
    "deep learning": "aprendizado profundo",
    "neural network": "rede neural",
    "artificial intelligence": "inteligência artificial",
    "data science": "ciência de dados",
    "computer vision": "visão computacional",
    "natural language processing": "processamento de linguagem natural",
}


def init_study_routes(app):
    @app.route("/dashboard", methods=["GET"])
    @login_required
    def dashboard():
        query = "pomodoro|spaced repetition|active recall|mind map"
        url = f"https://api.openalex.org/works?filter=title.search:{query},cited_by_count:>3&per-page=10"
        artigos = []
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                artigos = data.get("results", [])
        except Exception:
            artigos = []

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
                            abstract_words.extend([""] * (pos - len(abstract_words) + 1))
                        abstract_words[pos] = word
                artigo["abstract_pt"] = (" ".join(abstract_words))[:150] + "..."
            else:
                artigo["abstract_pt"] = "Resumo não disponível"

        atividades_com_duracao = (
            db.session.query(Atividade.materia, Atividade.duracao)
            .filter_by(user_id=current_user.id)
            .filter(Atividade.duracao.isnot(None))
            .all()
        )
        tempo_por_materia = {}
        for materia, duracao in atividades_com_duracao:
            tempo_por_materia[materia] = tempo_por_materia.get(materia, 0) + parse_duration_to_minutes(
                duracao
            )

        labels_materias = list(tempo_por_materia.keys())
        data_materias = list(tempo_por_materia.values())
        materia_tempo = [(m, tempo_por_materia.get(m.nome, 0)) for m in current_user.materias]
        materia_tempo.sort(key=lambda item: item[1], reverse=True)
        sorted_materias = [m[0] for m in materia_tempo]

        activities_per_day = (
            db.session.query(func.date(Atividade.data_criacao), func.count(Atividade.id))
            .filter_by(user_id=current_user.id)
            .group_by(func.date(Atividade.data_criacao))
            .all()
        )
        labels_dash = [str(row[0]) for row in activities_per_day]
        data_dash = [row[1] for row in activities_per_day]

        metas_ativas = Meta.query.filter_by(user_id=current_user.id, status="ativo").count()
        metas_concluidas = Meta.query.filter_by(
            user_id=current_user.id, status="concluido"
        ).count()

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
            total_metas=metas_ativas + metas_concluidas,
        )

    @app.route("/adicionar_materia", methods=["POST"])
    @login_required
    def adicionar_materia():
        nome_materia = request.form.get("materia", "").strip()
        valido, msg = Validadores.validar_materia(nome_materia)
        if not valido:
            flash(msg, "error")
            return redirect(url_for("dashboard"))

        materia_existe = Materia.query.filter_by(
            nome=nome_materia, user_id=current_user.id
        ).first()
        if materia_existe:
            flash(f"A matéria '{nome_materia}' já está cadastrada.", "error")
            return redirect(url_for("dashboard"))

        try:
            db.session.add(Materia(nome=nome_materia, user_id=current_user.id))
            db.session.commit()
            criar_notificacao(
                user_id=current_user.id,
                tipo="sistema",
                titulo="Matéria Adicionada! 📚",
                mensagem=f"A matéria '{nome_materia}' foi adicionada com sucesso.",
                icone="fa-book",
            )
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
        atividades_com_duracao = (
            db.session.query(Atividade.materia, Atividade.duracao)
            .filter_by(user_id=current_user.id)
            .filter(Atividade.duracao.isnot(None))
            .all()
        )
        tempo_por_materia = {}
        for materia, duracao in atividades_com_duracao:
            tempo_por_materia[materia] = tempo_por_materia.get(materia, 0) + parse_duration_to_minutes(
                duracao
            )
        all_materias = Materia.query.filter_by(user_id=current_user.id).all()
        sorted_materias = sorted(
            all_materias, key=lambda m: tempo_por_materia.get(m.nome, 0), reverse=True
        )
        return render_template("adicionar_materia.html", materias=sorted_materias)

    @app.route("/adicionar_atividade", methods=["GET", "POST"])
    @login_required
    def adicionar_atividade():
        materias = Materia.query.filter_by(user_id=current_user.id).all()

        if request.method == "POST":
            materia = request.form.get("materia", "").strip()
            assunto = Validadores.sanitizar_texto(
                request.form.get("assunto_primario", "").strip()
            )
            descricao = Validadores.sanitizar_texto(request.form.get("descricao", "").strip())
            duracao = request.form.get("duracao", "").strip()
            data = parse_date_field(request.form.get("data", "").strip())

            if not materia or len(materia) < 2:
                flash("Informe o nome da matéria (mínimo 2 caracteres).", "error")
                return redirect(url_for("adicionar_atividade"))
            if not assunto or len(assunto) < 2:
                flash("Informe o assunto primário (mínimo 2 caracteres).", "error")
                return redirect(url_for("adicionar_atividade"))
            if duracao:
                valido, msg = Validadores.validar_duracao(duracao)
                if not valido:
                    flash(msg, "error")
                    return redirect(url_for("adicionar_atividade"))

            try:
                db.session.add(
                    Atividade(
                        materia=materia,
                        assunto_primario=assunto,
                        descricao=descricao or None,
                        duracao=duracao or None,
                        data=data,
                        user_id=current_user.id,
                    )
                )
                db.session.commit()
                criar_notificacao(
                    user_id=current_user.id,
                    tipo="sistema",
                    titulo="Atividade Criada! ✅",
                    mensagem=f"'{assunto}' de {materia} foi adicionada com sucesso.",
                    link="/listar_atividades",
                    icone="fa-check-circle",
                )
                criar_notificacao(
                    user_id=current_user.id,
                    tipo="lembrete",
                    titulo="Lembrete de Estudo 📚",
                    mensagem=f"Não esqueça de revisar '{assunto}' amanhã!",
                    icone="fa-calendar-check",
                )
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
            flash("Atividade não encontrada ou sem permissão.", "error")
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
            valido, msg = Validadores.validar_materia(nome)
            if not valido:
                flash(msg, "error")
                return redirect(url_for("editar_materia", materia_id=materia_id))

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
        except Exception:
            db.session.rollback()
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
        except Exception:
            db.session.rollback()
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
        Notificacao.query.filter_by(user_id=current_user.id, lida=False).update({"lida": True})
        db.session.commit()
        return {"success": True}, 200

    @app.route("/api/notificacoes_nao_lidas")
    @login_required
    def api_notificacoes_nao_lidas():
        return {
            "nao_lidas": Notificacao.query.filter_by(
                user_id=current_user.id, lida=False
            ).count()
        }

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

    @app.route("/pomodoro")
    @login_required
    def pomodoro():
        return render_template("pomodoro.html")

    @app.route("/salvar_sessao_pomodoro", methods=["POST"])
    @login_required
    def salvar_sessao_pomodoro():
        data = request.get_json() or {}
        materia = data.get("materia", "Geral")
        tipo = data.get("tipo", "trabalho")
        duracao = data.get("duracao", 25)
        if tipo == "trabalho":
            criar_notificacao(
                user_id=current_user.id,
                tipo="conquista",
                titulo="🍅 Pomodoro Concluído!",
                mensagem=f"Você completou {duracao} minutos de foco em {materia}. Continue assim!",
                icone="fa-trophy",
            )
        return {"success": True, "message": "Sessão salva com sucesso!"}, 200

    @app.route("/metas")
    @login_required
    def listar_metas():
        status_filtro = request.args.get("status", "todos")
        query = Meta.query.filter_by(user_id=current_user.id)
        if status_filtro != "todos":
            query = query.filter_by(status=status_filtro)
        metas = query.order_by(Meta.data_criacao.desc()).all()
        return render_template("listar_metas.html", metas=metas, status_filtro=status_filtro)

    @app.route("/criar_meta", methods=["GET", "POST"])
    @login_required
    def criar_meta():
        materias = Materia.query.filter_by(user_id=current_user.id).all()
        if request.method == "POST":
            titulo = Validadores.sanitizar_texto(request.form.get("titulo", "").strip())
            descricao = Validadores.sanitizar_texto(request.form.get("descricao", "").strip())
            data_limite = parse_date_field(request.form.get("data_limite", "").strip())
            materia_id = request.form.get("materia_id", "").strip()
            if not titulo or len(titulo) < 3:
                flash("Título deve ter no mínimo 3 caracteres.", "error")
                return redirect(url_for("criar_meta"))
            if len(titulo) > 200:
                flash("Título deve ter no máximo 200 caracteres.", "error")
                return redirect(url_for("criar_meta"))
            try:
                db.session.add(
                    Meta(
                        user_id=current_user.id,
                        titulo=titulo,
                        descricao=descricao or None,
                        data_limite=data_limite,
                        materia_id=int(materia_id) if materia_id else None,
                    )
                )
                db.session.commit()
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
        meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first()
        if not meta:
            flash("Meta não encontrada.", "error")
            return redirect(url_for("listar_metas"))
        materias = Materia.query.filter_by(user_id=current_user.id).all()
        if request.method == "POST":
            titulo = Validadores.sanitizar_texto(request.form.get("titulo", "").strip())
            descricao = Validadores.sanitizar_texto(request.form.get("descricao", "").strip())
            data_limite = parse_date_field(request.form.get("data_limite", "").strip())
            materia_id = request.form.get("materia_id", "").strip()
            status = request.form.get("status", "ativo")
            if not titulo or len(titulo) < 3:
                flash("Título deve ter no mínimo 3 caracteres.", "error")
                return redirect(url_for("editar_meta", meta_id=meta_id))
            if len(titulo) > 200:
                flash("Título deve ter no máximo 200 caracteres.", "error")
                return redirect(url_for("editar_meta", meta_id=meta_id))
            try:
                meta.titulo = titulo
                meta.descricao = descricao or None
                meta.data_limite = data_limite
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
        meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first()
        if not meta:
            flash("Meta não encontrada.", "error")
            return redirect(url_for("listar_metas"))
        try:
            db.session.delete(meta)
            db.session.commit()
            flash("Meta deletada com sucesso!", "success")
        except Exception:
            db.session.rollback()
            flash("Erro ao deletar meta.", "error")
        return redirect(url_for("listar_metas"))

    @app.route("/concluir_meta/<int:meta_id>", methods=["POST"])
    @login_required
    def concluir_meta(meta_id):
        meta = Meta.query.filter_by(id=meta_id, user_id=current_user.id).first()
        if not meta:
            flash("Meta não encontrada.", "error")
            return redirect(url_for("listar_metas"))
        try:
            meta.status = "concluido"
            db.session.commit()
            criar_notificacao(
                user_id=current_user.id,
                tipo="conquista",
                titulo="Meta Concluída! 🏆",
                mensagem=f"Parabéns! Você concluiu a meta '{meta.titulo}'.",
                icone="fa-trophy",
            )
            verificar_e_conceder_badge(current_user.id, "primeira_meta_concluida")
            flash("Meta marcada como concluída!", "success")
        except Exception:
            db.session.rollback()
            flash("Erro ao concluir meta.", "error")
        return redirect(url_for("listar_metas"))

    @app.route("/calendario")
    @login_required
    def calendario():
        return render_template("calendario.html")

    @app.route("/api/calendario_eventos")
    @login_required
    def api_calendario_eventos():
        eventos = []
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

from models.models import db, User, Meta, Badge, UserBadge
from services.app_service import criar_notificacao, parse_duration_to_minutes


def criar_badges_padrao():
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
            db.session.add(Badge(**badge_data))
    db.session.commit()


def verificar_e_conceder_badge(user_id, criterio):
    user = User.query.get(user_id)
    badge = Badge.query.filter_by(criterio=criterio).first()
    if not badge or not user:
        return

    if UserBadge.query.filter_by(user_id=user_id, badge_id=badge.id).first():
        return

    conceder = False
    if criterio == "primeira_atividade":
        conceder = len(user.atividades) >= 1
    elif criterio == "primeira_meta_concluida":
        conceder = (
            Meta.query.filter_by(user_id=user_id, status="concluido").count() >= 1
        )
    elif criterio == "10_horas":
        tempo_total = sum(
            parse_duration_to_minutes(atividade.duracao or "0")
            for atividade in user.atividades
        )
        conceder = tempo_total >= 600
    elif criterio == "5_materias":
        conceder = len(user.materias) >= 5

    if conceder:
        db.session.add(UserBadge(user_id=user_id, badge_id=badge.id))
        db.session.commit()
        criar_notificacao(
            user_id=user_id,
            tipo="conquista",
            titulo=f"🏆 Badge Conquistado: {badge.nome}!",
            mensagem=f"Parabéns! Você ganhou o badge '{badge.nome}' - {badge.descricao}",
            icone="fa-trophy",
        )

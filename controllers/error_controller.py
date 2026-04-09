from flask import flash, redirect, url_for

from models.models import db


def init_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        flash("Página não encontrada.", "error")
        return redirect(url_for("dashboard"))

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        flash("Erro interno do servidor. Tente novamente.", "error")
        return redirect(url_for("dashboard"))

    @app.errorhandler(403)
    def forbidden(error):
        flash("Acesso negado.", "error")
        return redirect(url_for("dashboard"))

import logging
from flask import request

logger = logging.getLogger('service')


class Paginator:
    """
    Classe para gerenciar paginação de consultas SQLAlchemy.

    Exemplo:
        paginator = Paginator(query, page=1, per_page=10)
        result = paginator.paginate()
        # result contém: items, total, pages, current_page, per_page, has_next, has_prev
    """

    def __init__(self, query, page=1, per_page=10):
        """
        Inicializa o paginador.

        Args:
            query: Query SQLAlchemy a paginar
            page: Número da página (padrão: 1)
            per_page: Itens por página (padrão: 10, máximo: 100)
        """
        self.query = query
        self.page = max(1, page)  # Garantir página >= 1
        self.per_page = max(1, min(per_page, 100))  # Entre 1 e 100

    def paginate(self):
        """
        Realiza a paginação e retorna resultado estruturado.

        Returns:
            dict com chaves:
                - items: Lista de itens da página atual
                - total: Total de itens
                - pages: Total de páginas
                - current_page: Página atual
                - per_page: Itens por página
                - has_next: Se existe próxima página
                - has_prev: Se existe página anterior
        """
        total = self.query.count()
        items = self.query.limit(self.per_page).offset(
            (self.page - 1) * self.per_page
        ).all()
        pages = (total + self.per_page - 1) // self.per_page if total > 0 else 0

        logger.debug(
            f"Paginação: página {self.page}/{pages}, "
            f"{len(items)} itens, total {total}"
        )

        return {
            'items': items,
            'total': total,
            'pages': pages,
            'current_page': self.page,
            'per_page': self.per_page,
            'has_next': self.page < pages,
            'has_prev': self.page > 1,
        }


def get_pagination_params(default_page=1, default_per_page=10):
    """
    Extrai parâmetros de paginação da query string da requisição.

    Args:
        default_page: Página padrão se não fornecida (padrão: 1)
        default_per_page: Itens por página padrão (padrão: 10)

    Returns:
        tuple: (page, per_page) com valores validados
    """
    try:
        page = int(request.args.get('page', default_page))
        per_page = int(request.args.get('per_page', default_per_page))

        # Validações
        page = max(1, page)
        per_page = max(1, min(per_page, 100))

        return page, per_page
    except (ValueError, TypeError):
        logger.warning(
            f"Parâmetros de paginação inválidos: "
            f"page={request.args.get('page')}, "
            f"per_page={request.args.get('per_page')}"
        )
        return default_page, default_per_page
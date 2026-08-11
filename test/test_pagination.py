import pytest
from utils.pagination import Paginator, get_pagination_params
from models.models import Atividade, User


class TestPaginator:
    """Testes para a classe Paginator"""

    @pytest.mark.unit
    def test_paginator_primeira_pagina(self, db_session, test_app):
        """Testa paginação na primeira página"""
        with test_app.app_context():
            # Criar usuário e atividades dentro do contexto
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User",
                email="test@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            # Criar 25 atividades
            for i in range(25):
                atividade = Atividade(
                    materia=f"Matéria {i}",
                    assunto_primario=f"Assunto {i}",
                    user_id=user.id,
                )
                db_session.session.add(atividade)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id)
            paginator = Paginator(query, page=1, per_page=10)
            result = paginator.paginate()

            assert result['current_page'] == 1
            assert len(result['items']) == 10
            assert result['total'] == 25
            assert result['pages'] == 3
            assert result['has_next'] is True
            assert result['has_prev'] is False

    @pytest.mark.unit
    def test_paginator_pagina_do_meio(self, db_session, test_app):
        """Testa paginação em página do meio"""
        with test_app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User 2",
                email="test2@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            for i in range(25):
                atividade = Atividade(
                    materia=f"Matéria {i}",
                    assunto_primario=f"Assunto {i}",
                    user_id=user.id,
                )
                db_session.session.add(atividade)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id)
            paginator = Paginator(query, page=2, per_page=10)
            result = paginator.paginate()

            assert result['current_page'] == 2
            assert len(result['items']) == 10
            assert result['has_next'] is True
            assert result['has_prev'] is True

    @pytest.mark.unit
    def test_paginator_ultima_pagina(self, db_session, test_app):
        """Testa paginação na última página"""
        with test_app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User 3",
                email="test3@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            for i in range(25):
                atividade = Atividade(
                    materia=f"Matéria {i}",
                    assunto_primario=f"Assunto {i}",
                    user_id=user.id,
                )
                db_session.session.add(atividade)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id)
            paginator = Paginator(query, page=3, per_page=10)
            result = paginator.paginate()

            assert result['current_page'] == 3
            assert len(result['items']) == 5
            assert result['has_next'] is False
            assert result['has_prev'] is True

    @pytest.mark.unit
    def test_paginator_pagina_invalida(self, db_session, test_app):
        """Testa paginação com página inválida"""
        with test_app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User 4",
                email="test4@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            for i in range(10):
                atividade = Atividade(
                    materia=f"Matéria {i}",
                    assunto_primario=f"Assunto {i}",
                    user_id=user.id,
                )
                db_session.session.add(atividade)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id)

            # Página 0 deve voltar para 1
            paginator = Paginator(query, page=0, per_page=10)
            result = paginator.paginate()
            assert result['current_page'] == 1

            # Página negativa deve voltar para 1
            paginator = Paginator(query, page=-5, per_page=10)
            result = paginator.paginate()
            assert result['current_page'] == 1

    @pytest.mark.unit
    def test_paginator_per_page_invalido(self, db_session, test_app):
        """Testa paginação com per_page inválido"""
        with test_app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User 5",
                email="test5@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            for i in range(10):
                atividade = Atividade(
                    materia=f"Matéria {i}",
                    assunto_primario=f"Assunto {i}",
                    user_id=user.id,
                )
                db_session.session.add(atividade)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id)

            # per_page > 100 deve ser limitado a 100
            paginator = Paginator(query, page=1, per_page=200)
            result = paginator.paginate()
            assert result['per_page'] == 100

            # per_page 0 deve voltar para 1
            paginator = Paginator(query, page=1, per_page=0)
            result = paginator.paginate()
            assert result['per_page'] == 1

    @pytest.mark.unit
    def test_paginator_query_vazia(self, db_session, test_app):
        """Testa paginação com query vazia"""
        with test_app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User 6",
                email="test6@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id)
            paginator = Paginator(query, page=1, per_page=10)
            result = paginator.paginate()

            assert result['total'] == 0
            assert result['pages'] == 0
            assert len(result['items']) == 0
            assert result['has_next'] is False
            assert result['has_prev'] is False

    @pytest.mark.unit
    def test_paginator_total_calculado_corretamente(self, db_session, test_app):
        """Testa cálculo correto de total de páginas"""
        with test_app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User 7",
                email="test7@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            # Criar 7 atividades
            for i in range(7):
                atividade = Atividade(
                    materia=f"Matéria {i}",
                    assunto_primario=f"Assunto {i}",
                    user_id=user.id,
                )
                db_session.session.add(atividade)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id)

            # 7 itens com 3 por página = 3 páginas (3+3+1)
            paginator = Paginator(query, page=1, per_page=3)
            result = paginator.paginate()
            assert result['pages'] == 3

            # 7 itens com 2 por página = 4 páginas (2+2+2+1)
            paginator = Paginator(query, page=1, per_page=2)
            result = paginator.paginate()
            assert result['pages'] == 4

            # 7 itens com 7 por página = 1 página
            paginator = Paginator(query, page=1, per_page=7)
            result = paginator.paginate()
            assert result['pages'] == 1

    @pytest.mark.unit
    def test_paginator_offset_correto(self, db_session, test_app):
        """Testa se o offset é calculado corretamente"""
        with test_app.app_context():
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt(test_app)
            hashed_password = bcrypt.generate_password_hash("TestPass123!").decode("utf-8")

            user = User(
                name="Test User 8",
                email="test8@example.com",
                password=hashed_password,
            )
            db_session.session.add(user)
            db_session.session.commit()

            # Criar 30 atividades numeradas
            for i in range(30):
                atividade = Atividade(
                    materia=f"Matéria {i}",
                    assunto_primario=f"Assunto {i}",
                    user_id=user.id,
                )
                db_session.session.add(atividade)
            db_session.session.commit()

            query = Atividade.query.filter_by(user_id=user.id).order_by(Atividade.id)

            # Página 1: offset 0, itens 0-9
            paginator = Paginator(query, page=1, per_page=10)
            result = paginator.paginate()
            assert len(result['items']) == 10

            # Página 2: offset 10, itens 10-19
            paginator = Paginator(query, page=2, per_page=10)
            result = paginator.paginate()
            assert len(result['items']) == 10

            # Página 3: offset 20, itens 20-29
            paginator = Paginator(query, page=3, per_page=10)
            result = paginator.paginate()
            assert len(result['items']) == 10


class TestGetPaginationParams:
    """Testes para a função get_pagination_params"""

    @pytest.mark.unit
    def test_get_pagination_params_defaults(self, test_app):
        """Testa valores padrão de paginação"""
        with test_app.test_request_context("/?"):
            page, per_page = get_pagination_params()
            assert page == 1
            assert per_page == 10

    @pytest.mark.unit
    def test_get_pagination_params_customizado(self, test_app):
        """Testa parâmetros customizados"""
        with test_app.test_request_context("/?page=3&per_page=20"):
            page, per_page = get_pagination_params()
            assert page == 3
            assert per_page == 20

    @pytest.mark.unit
    def test_get_pagination_params_invalido(self, test_app):
        """Testa com parâmetros inválidos"""
        with test_app.test_request_context("/?page=abc&per_page=xyz"):
            page, per_page = get_pagination_params()
            assert page == 1  # Valor padrão
            assert per_page == 10  # Valor padrão

    @pytest.mark.unit
    def test_get_pagination_params_negativo(self, test_app):
        """Testa com parâmetros negativos"""
        with test_app.test_request_context("/?page=-5&per_page=-3"):
            page, per_page = get_pagination_params()
            assert page == 1  # Validação força >= 1
            assert per_page == 1  # Validação força >= 1

    @pytest.mark.unit
    def test_get_pagination_params_muito_grande(self, test_app):
        """Testa com per_page muito grande"""
        with test_app.test_request_context("/?page=1&per_page=500"):
            page, per_page = get_pagination_params()
            assert page == 1
            assert per_page == 100  # Limitado a 100

    @pytest.mark.unit
    def test_get_pagination_params_custom_defaults(self, test_app):
        """Testa com defaults customizados"""
        with test_app.test_request_context("/?"):
            page, per_page = get_pagination_params(default_page=5, default_per_page=25)
            assert page == 5
            assert per_page == 25

    @pytest.mark.unit
    def test_get_pagination_params_zero(self, test_app):
        """Testa com zero"""
        with test_app.test_request_context("/?page=0&per_page=0"):
            page, per_page = get_pagination_params()
            assert page == 1  # 0 é inválido, volta a 1
            assert per_page == 1  # 0 é inválido, volta a 1

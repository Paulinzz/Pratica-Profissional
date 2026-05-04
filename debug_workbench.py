import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def debug_completo():
    """Diagnóstico completo do problema"""
    print("🔍 DIAGNÓSTICO COMPLETO DO BANCO DE DADOS")
    print("=" * 60)

    # 1. Verificar variáveis de ambiente
    print("\n1️⃣ VARIÁVEIS DE AMBIENTE:")
    print("-" * 30)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "pratica_profissional")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")

    print(f"Host: {DB_HOST}")
    print(f"Port: {DB_PORT}")
    print(f"Database: {DB_NAME}")
    print(f"User: {DB_USER}")
    print(f"Password: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'VAZIA'}")

    # 2. Testar conexão sem banco específico
    print("\n2️⃣ TESTANDO CONEXÃO MYSQL (sem banco específico):")
    print("-" * 50)
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            charset="utf8mb4",
        )
        print("✅ Conexão MySQL: OK")

        # Listar todos os bancos
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]

        print(f"📋 Bancos disponíveis: {databases}")

        if DB_NAME in databases:
            print(f"✅ Banco '{DB_NAME}' existe!")
        else:
            print(f"❌ Banco '{DB_NAME}' NÃO existe!")
            print(f"💡 Criando banco '{DB_NAME}'...")

            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            print(f"✅ Banco '{DB_NAME}' criado!")

        conn.close()

    except Exception as e:
        print(f"❌ Erro na conexão MySQL: {e}")
        return False

    # 3. Testar conexão com banco específico
    print(f"\n3️⃣ TESTANDO CONEXÃO COM BANCO '{DB_NAME}':")
    print("-" * 50)
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
        )
        print(f"✅ Conexão com '{DB_NAME}': OK")

        # Listar tabelas
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()

        if tabelas:
            print(f"📋 Tabelas encontradas: {[t[0] for t in tabelas]}")
        else:
            print("❌ NENHUMA TABELA ENCONTRADA!")

        conn.close()
        return len(tabelas) > 0

    except Exception as e:
        print(f"❌ Erro na conexão com banco '{DB_NAME}': {e}")
        return False


def testar_flask_models():
    """Testa se os modelos Flask estão sendo carregados"""
    print("\n4️⃣ TESTANDO MODELOS FLASK:")
    print("-" * 30)

    try:
        from models.models import db, User, Materia, Atividade

        print("✅ Modelos importados com sucesso")

        # Verificar se os modelos têm __tablename__
        print(f"📋 User table: {getattr(User, '__tablename__', 'user')}")
        print(f"📋 Materia table: {getattr(Materia, '__tablename__', 'materia')}")
        print(f"📋 Atividade table: {getattr(Atividade, '__tablename__', 'atividade')}")

        return True
    except Exception as e:
        print(f"❌ Erro ao importar modelos: {e}")
        return False


def criar_tabelas_forcado():
    """Força a criação das tabelas"""
    print("\n5️⃣ FORÇANDO CRIAÇÃO DAS TABELAS:")
    print("-" * 40)

    try:
        from app import app, db

        with app.app_context():
            print("🔄 Executando db.drop_all()...")
            db.drop_all()
            print("✅ Tabelas removidas")

            print("🔄 Executando db.create_all()...")
            db.create_all()
            print("✅ Tabelas criadas")

            # Verificar se foram criadas
            from sqlalchemy import inspect

            inspector = inspect(db.engine)
            tabelas = inspector.get_table_names()

            print(f"📋 Tabelas criadas: {tabelas}")

        return len(tabelas) > 0

    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False


def verificar_workbench():
    """Dicas para o MySQL Workbench"""
    print("\n6️⃣ DICAS PARA MYSQL WORKBENCH:")
    print("-" * 40)

    DB_NAME = os.getenv("DB_NAME", "pratica_profissional")

    print("🔄 No MySQL Workbench:")
    print(f"1. Verifique se você está conectado ao servidor correto")
    print(f"2. Clique em 'Schemas' no painel esquerdo")
    print(f"3. Procure pelo schema '{DB_NAME}'")
    print(f"4. Se não aparecer, clique no ícone de refresh (🔄)")
    print(f"5. Se ainda não aparecer, execute: USE {DB_NAME};")
    print(f"6. E depois: SHOW TABLES;")


def main():
    """Executa todos os diagnósticos"""
    print("🚀 INICIANDO DIAGNÓSTICO...")

    # Diagnóstico básico
    tem_tabelas = debug_completo()

    # Testar modelos
    modelos_ok = testar_flask_models()

    # Se não tem tabelas, tenta criar
    if not tem_tabelas and modelos_ok:
        print("\n💡 Tentando criar tabelas...")
        tabelas_criadas = criar_tabelas_forcado()

        if tabelas_criadas:
            print("✅ Tabelas criadas com sucesso!")
            # Verificar novamente
            debug_completo()
        else:
            print("❌ Falha ao criar tabelas")

    # Dicas para o Workbench
    verificar_workbench()

    print("\n" + "=" * 60)
    print("📊 RESUMO:")
    print("=" * 60)
    if tem_tabelas:
        print("✅ Problema resolvido! As tabelas existem.")
        print("💡 No Workbench: Clique em refresh ou reconecte")
    else:
        print("❌ Tabelas ainda não foram criadas.")
        print("💡 Execute: python criar_tabelas.py")


if __name__ == "__main__":
    main()

import os
import pymysql
from dotenv import load_dotenv

class TesteMySQLConfig:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.database = os.getenv('DB_NAME', 'pratica_profissional')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
    
    def verificar_mysql_rodando(self):
        """Verifica se o MySQL está rodando"""
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            connection.close()
            return True, "MySQL está rodando"
        except Exception as e:
            return False, f"MySQL não está acessível: {e}"
    
    def verificar_banco_existe(self):
        """Verifica se o banco de dados existe"""
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            
            with connection.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                databases = [db[0] for db in cursor.fetchall()]
            
            connection.close()
            
            if self.database in databases:
                return True, f"Banco '{self.database}' existe"
            else:
                return False, f"Banco '{self.database}' não encontrado"
                
        except Exception as e:
            return False, f"Erro ao verificar bancos: {e}"
    
    def criar_banco_se_necessario(self):
        """Cria o banco se ele não existir"""
        exists, msg = self.verificar_banco_existe()
        
        if exists:
            return True, msg
        
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset='utf8mb4'
            )
            
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE {self.database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            connection.close()
            return True, f"Banco '{self.database}' criado com sucesso"
            
        except Exception as e:
            return False, f"Erro ao criar banco: {e}"
    
    def testar_conexao_completa(self):
        """Testa conexão com o banco específico"""
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4'
            )
            connection.close()
            return True, f"Conexão com '{self.database}' estabelecida"
        except Exception as e:
            return False, f"Erro na conexão com '{self.database}': {e}"
    
    def executar_todos_testes(self):
        """Executa todos os testes em sequência"""
        print("🔍 Verificando configuração MySQL...\n")
        
        testes = [
            ("MySQL rodando", self.verificar_mysql_rodando),
            ("Banco existe", self.verificar_banco_existe),
            ("Criar banco (se necessário)", self.criar_banco_se_necessario),
            ("Conexão completa", self.testar_conexao_completa)
        ]
        
        resultados = {}
        
        for nome_teste, funcao_teste in testes:
            sucesso, mensagem = funcao_teste()
            resultados[nome_teste] = sucesso
            
            status = "✅" if sucesso else "❌"
            print(f"{status} {nome_teste}: {mensagem}")
        
        print(f"\n{'='*50}")
        if all(resultados.values()):
            print("🎉 Todos os testes MySQL passaram!")
            return True
        else:
            print("⚠️  Alguns testes falharam. Verifique a configuração.")
            return False

# Uso simples:
def teste_mysql_rapido():
    """Função rápida para testar MySQL"""
    teste = TesteMySQLConfig()
    return teste.executar_todos_testes()

if __name__ == "__main__":
    
    print("Testando MySQL...")
    mysql_ok = teste_mysql_rapido()
    
    if mysql_ok:
        print("Prosseguindo com outros testes...")
    else:
        print("Corrija a configuração MySQL antes de prosseguir.")
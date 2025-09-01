# 🗄️ Guia de Conexão com Banco de Dados MySQL

## 📋 Índice
- [Pré-requisitos](#pré-requisitos)
- [Configuração Inicial](#configuração-inicial)
- [Instalação das Dependências](#instalação-das-dependências)
- [Configuração do Projeto](#configuração-do-projeto)
- [Criação do Banco](#criação-do-banco)
- [Verificação da Conexão](#verificação-da-conexão)
- [Visualização das Tabelas](#visualização-das-tabelas)
- [Problemas Comuns](#problemas-comuns)
- [Scripts Úteis](#scripts-úteis)

---

## 🎯 Pré-requisitos

### 1. MySQL Server Instalado
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server

# Fedora/CentOS
sudo dnf install mysql-server

# Verificar se está rodando
sudo systemctl status mysql
sudo systemctl start mysql  # se não estiver rodando
```

### 2. Python 3.8+
```bash
python3 --version
```

---

## ⚙️ Configuração Inicial

### 1. Configurar MySQL (primeira vez)
```bash
# Configuração inicial do MySQL
sudo mysql_secure_installation

# Conectar ao MySQL
sudo mysql -u root -p
```

### 2. Criar usuário (opcional, mas recomendado)
```sql
-- No console do MySQL
CREATE USER 'dev_user'@'localhost' IDENTIFIED BY 'dev_password';
GRANT ALL PRIVILEGES ON *.* TO 'dev_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 📦 Instalação das Dependências

### 1. Ativar o ambiente virtual
```bash
# Navegar para o diretório do projeto
cd /caminho/para/Pratica-Profissional

# Ativar ambiente virtual
source env/bin/activate  # Linux/Mac
# ou
env\Scripts\activate     # Windows
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Se não tiver o requirements.txt, instalar manualmente:
```bash
pip install flask flask-sqlalchemy flask-login flask-bcrypt pymysql python-dotenv requests tabulate
```

---

## 🔧 Configuração do Projeto

### 1. Criar arquivo `.env`
Crie um arquivo `.env` na raiz do projeto:

```bash
# Configurações do MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pratica_profissional
DB_USER=root
DB_PASSWORD=sua_senha_aqui

# Chave secreta da aplicação
SECRET_KEY=Chave1234
```

⚠️ **IMPORTANTE**: 
- Substitua `sua_senha_aqui` pela senha real do MySQL
- Nunca commite o arquivo `.env` no Git
- Adicione `.env` no `.gitignore`

### 2. Verificar estrutura de arquivos
```
Pratica-Profissional/
├── app.py
├── models.py
├── .env
├── requirements.txt
└── templates/
    ├── index.html
    ├── login.html
    └── ...
```

---

## 🏗️ Criação do Banco

### 1. Criar banco manualmente (MySQL CLI)
```bash
mysql -u root -p
```

```sql
CREATE DATABASE pratica_profissional CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
EXIT;
```

### 2. Ou usar script automatizado
```bash
python debug_banco.py
```

---

## ✅ Verificação da Conexão

### 1. Testar conexão básica
```bash
python -c "
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    print('✅ Conexão MySQL: OK!')
    conn.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

### 2. Criar tabelas
```bash
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Tabelas criadas!')
"
```

### 3. Verificar tabelas criadas
```bash
python confirmar_tabelas_existem.py
```

---

## 👁️ Visualização das Tabelas

### 1. MySQL Command Line
```bash
mysql -u root -p
USE pratica_profissional;
SHOW TABLES;
DESCRIBE user;
SELECT * FROM user;
```

### 2. MySQL Workbench
1. Conectar ao servidor MySQL
2. Abrir schema `pratica_profissional`
3. Se as tabelas não aparecerem:
   - Clique com botão direito no schema → "Refresh All"
   - Ou execute: `USE pratica_profissional; SHOW TABLES;`

### 3. phpMyAdmin (Opcional)
```bash
sudo apt install phpmyadmin
# Acesse: http://localhost/phpmyadmin
```

### 4. Script Python
```bash
python verificar_tabelas.py
```

---

## 🚨 Problemas Comuns

### ❌ Erro: "Access denied for user 'root'@'localhost'"

**Solução 1**: Verificar senha
```bash
mysql -u root -p
# Digite a senha correta e teste
```

**Solução 2**: Resetar senha do root
```bash
sudo systemctl stop mysql
sudo mysqld_safe --skip-grant-tables &
mysql -u root

# No MySQL:
USE mysql;
UPDATE user SET authentication_string = PASSWORD('nova_senha') WHERE User = 'root';
UPDATE user SET plugin = 'mysql_native_password' WHERE User = 'root';
FLUSH PRIVILEGES;
EXIT;

sudo pkill mysqld
sudo systemctl start mysql
```

### ❌ Erro: "Unknown database 'pratica_profissional'"

**Solução**:
```sql
CREATE DATABASE pratica_profissional CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### ❌ Tabelas não aparecem no MySQL Workbench

**Isso é normal!** É um bug conhecido do Workbench.

**Soluções**:
1. Clique em "Refresh All" no schema
2. Feche e reabra a conexão  
3. Execute comandos SQL diretamente:
   ```sql
   USE pratica_profissional;
   SHOW TABLES;
   ```

### ❌ Erro: "No module named 'dotenv'"

**Solução**:
```bash
pip install python-dotenv
```

### ❌ Erro: "MySQL server has gone away"

**Soluções**:
1. Reiniciar MySQL: `sudo systemctl restart mysql`
2. Verificar se o processo não travou
3. Aumentar timeout no MySQL

---

## 🛠️ Scripts Úteis

### 1. `debug_banco.py` - Diagnóstico completo
```bash
python debug_banco.py
```
- Testa conexão
- Verifica se o banco existe
- Lista todas as tabelas
- Mostra problemas de configuração

### 2. `confirmar_tabelas_existem.py` - Verificar tabelas
```bash
python confirmar_tabelas_existem.py  
```
- Lista tabelas existentes
- Mostra estrutura das tabelas
- Conta registros
- Testa SELECTs

### 3. `verificar_tabelas.py` - Menu interativo
```bash
python verificar_tabelas.py
```
- Menu para explorar o banco
- Ver estrutura e dados
- Relatórios completos

### 4. `forcar_criacao_tabelas.py` - Recriar tabelas
```bash
python forcar_criacao_tabelas.py
```
- Remove e recria todas as tabelas
- Use apenas quando necessário

### 5. Testar aplicação Flask
```bash
flask run --debug
# ou
python app.py
```

---

## 📝 Checklist de Verificação

Antes de começar a desenvolver, certifique-se de que:

- [ ] MySQL está instalado e rodando
- [ ] Arquivo `.env` está configurado corretamente
- [ ] Dependências Python estão instaladas
- [ ] Conexão com MySQL funciona
- [ ] Banco `pratica_profissional` existe
- [ ] Tabelas foram criadas (`user`, `tb_materias`, `tb_atividades`)
- [ ] Aplicação Flask roda sem erros

---

## 🆘 Comandos de Emergência

### Resetar tudo:
```bash
# 1. Parar aplicação Flask (Ctrl+C)

# 2. Conectar ao MySQL e remover banco
mysql -u root -p
DROP DATABASE IF EXISTS pratica_profissional;
CREATE DATABASE pratica_profissional CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# 3. Recriar tabelas
python forcar_criacao_tabelas.py

# 4. Verificar
python debug_banco.py

# 5. Executar aplicação
flask run --debug
```

### Verificar se MySQL está funcionando:
```bash
sudo systemctl status mysql
sudo systemctl start mysql
sudo systemctl enable mysql  # iniciar automaticamente
```

---

## 👥 Para a Equipe

### 1. Clone do repositório
```bash
git clone <url-do-repositorio>
cd Pratica-Profissional
```

### 2. Configuração do ambiente
```bash
python -m venv env
source env/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 3. Configurar seu `.env`
Cada desenvolvedor deve criar seu próprio `.env` com suas credenciais MySQL.

### 4. Testar setup
```bash
python debug_banco.py
flask run --debug
```

---

## 📞 Suporte

### Se nada funcionar:
1. **Execute**: `python debug_banco.py`
2. **Copie** a saída do comando
3. **Compartilhe** com a equipe no grupo
4. **Inclua** informações do sistema:
   ```bash
   python --version
   mysql --version
   pip list | grep -i mysql
   ```

### Logs úteis:
```bash
# Logs do MySQL
sudo tail -f /var/log/mysql/error.log

# Testar conexão direta
telnet localhost 3306
```

---

## 🎯 Próximos Passos

Após configurar o banco:

1. **Executar aplicação**: `flask run --debug`
2. **Acessar**: http://localhost:5000
3. **Testar funcionalidades**:
   - Cadastro de usuário
   - Login
   - Adicionar matérias
   - Adicionar atividades
4. **Verificar dados** no banco com os scripts

---

**✅ Setup concluído com sucesso!** Agora a equipe pode trabalhar com o banco de dados MySQL configurado.

---
*Última atualização: 01/09/2025*
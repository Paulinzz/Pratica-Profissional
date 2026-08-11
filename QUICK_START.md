# 🚀 Guia Rápido - Implementações FocusUp

## ⚡ Começar Rápido

### 1. Executar os Testes (1 minuto)
```bash
# Instalar dependências (pytest já está no requirements.txt)
pip install -r requirements.txt

# Rodar todos os testes
pytest test/ -v

# Resultado esperado: 81 testes passando ✅
```

### 2. Ver Logs em Ação (5 minutos)
```bash
# Terminal 1: Iniciar a aplicação
python app.py

# Terminal 2: Monitorar logs
tail -f logs/app.log

# Fazer login/registro para ver logs aparecerem
```

### 3. Testar Paginação (3 minutos)
1. Criar múltiplas atividades (>10)
2. Ir para: `http://localhost:5000/listar_atividades`
3. Clicar em páginas para ver paginação em ação
4. Testar filtros: `http://localhost:5000/listar_notificacoes?tipo=sistema&page=1`

---

## 📂 O que Foi Criado

### Logging (`config/logging_config.py`)
```python
import logging
logger = logging.getLogger('auth')
logger.info("Novo usuário registrado: user@example.com")
logger.error("Erro ao conectar ao banco", exc_info=True)
```

**Arquivos gerados:**
- `logs/app.log` - Todos os eventos
- `logs/errors.log` - Apenas erros

---

### Testes (`test/` pasta)
```bash
# Rodar testes específicos
pytest test/test_validation_service.py -v
pytest test/test_pagination.py -v

# Com cobertura de código
pytest --cov=services --cov=utils
```

**Estatísticas:**
- 66 testes de validação ✅
- 15 testes de paginação ✅
- 81 testes no total

---

### Paginação (`utils/pagination.py`)
```python
from utils.pagination import Paginator, get_pagination_params

# Na controladora
page, per_page = get_pagination_params()
query = Atividade.query.filter_by(user_id=current_user.id)
paginator = Paginator(query, page=page, per_page=per_page)
result = paginator.paginate()

# No template
{% for atividade in result['items'] %}
  {{ atividade.nome }}
{% endfor %}
```

**Endpoints com paginação:**
- `/listar_atividades?page=1&per_page=10`
- `/listar_noticacoes?page=1&per_page=15`
- `/metas?page=1&per_page=10`

---

## 📊 Verificar Qualidade

### Cobertura de Testes
```bash
# Ver percentual de cobertura
pytest --cov=services --cov=controllers --cov=utils --cov-report=html

# Abrir relatório HTML
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Analisar Logs
```bash
# Buscar eventos de erro
grep ERROR logs/app.log

# Buscar logins bem-sucedidos
grep "Login bem-sucedido" logs/app.log

# Ver últimas 50 linhas
tail -50 logs/app.log
```

---

## 🔍 Troubleshooting

### Problema: Testes não rodando
**Solução:**
```bash
# Verificar que pytest está instalado
pip install pytest

# Rodar com debug
pytest test/ -vv --tb=long
```

### Problema: Logs não aparecem
**Solução:**
```bash
# Verificar se pasta logs existe
mkdir -p logs

# Verificar permissões
ls -la logs/

# Se vazio, rodar uma ação na app (login, registro)
```

### Problema: Paginação não funciona
**Solução:**
```bash
# Verificar que templates foram atualizados
# Criar múltiplas atividades (>10)
# Verificar que o endpoint retorna result['items']
```

---

## 📝 Exemplos de Uso

### Usar Logger em Novo Controller
```python
import logging

study_logger = logging.getLogger('study')

def meu_endpoint():
    study_logger.info("Ação importante realizada")
    try:
        fazer_algo()
    except Exception as e:
        study_logger.error(f"Erro: {str(e)}", exc_info=True)
        raise
```

### Adicionar Paginação a Novo Endpoint
```python
from utils.pagination import Paginator, get_pagination_params

@app.route("/meus_itens")
def meus_itens():
    page, per_page = get_pagination_params()
    query = Item.query.filter_by(user_id=current_user.id)
    paginator = Paginator(query, page=page, per_page=per_page)
    result = paginator.paginate()
    return render_template("meus_itens.html", **result)
```

### Escrever Novo Teste
```python
import pytest

class TestMeuValidator:
    @pytest.mark.validation
    @pytest.mark.parametrize("valor,esperado", [
        ("valido", True),
        ("", False),
    ])
    def test_validacao(self, valor, esperado):
        valido, msg = Validadores.validar_algo(valor)
        assert valido == esperado
```

---

## 🎯 Checklist de Validação

- [ ] Testes rodando: `pytest test/ -v`
- [ ] Logs sendo criados: `tail -f logs/app.log`
- [ ] Paginação funciona: criar >10 atividades, ir para `/listar_atividades?page=2`
- [ ] Filtros preservados: `/listar_notificacoes?tipo=sistema&page=2`
- [ ] Sem erros de compilação: `python -m py_compile config/logging_config.py utils/pagination.py`

---

## 📞 Suporte

### Documentação Completa
Veja `IMPLEMENTACOES.md` para:
- Instruções detalhadas
- Exemplos completos
- FAQs

### Documentação Técnica
Veja `RESUMO_IMPLEMENTACOES.md` para:
- Estatísticas gerais
- Arquitetura
- Recomendações futuras

---

## 🎁 Bônus: Comandos Úteis

```bash
# Rodar teste específico
pytest test/test_validation_service.py::TestValidadoresEmail::test_validar_email -v

# Rodar testes de um marcador
pytest -m auth -v        # testes de autenticação
pytest -m validation -v  # testes de validação

# Rodar com mais debug
pytest test/ -vv --tb=long

# Parar no primeiro erro
pytest test/ -x

# Mostrar prints durante testes
pytest test/ -s
```

---

**Status:** ✅ Pronto para usar
**Última atualização:** 11 de Agosto de 2026

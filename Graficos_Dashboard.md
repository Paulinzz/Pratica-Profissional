# Implementação de Gráficos no Dashboard

## Visão Geral
Este documento descreve a implementação de gráficos interativos no dashboard da aplicação Flask, utilizando Chart.js para visualização de dados de atividades de estudo.

## Funcionalidades Implementadas

### 1. Gráfico de Atividades por Dia (Card-Dash)
- **Tipo**: Gráfico de linha com gradiente
- **Dados**: Contagem de atividades agrupadas por data de criação
- **Características**:
  - Gradiente azul-turquesa no fundo
  - Pontos interativos com hover
  - Animação suave na renderização
  - Tooltips customizados

### 2. Gráfico de Matérias Mais Estudadas
- **Tipo**: Gráfico de barras com cores variadas
- **Dados**: Contagem de atividades agrupadas por matéria
- **Características**:
  - Cores distintas para cada barra
  - Animação com delay escalonado
  - Bordas arredondadas
  - Tooltips mostrando "X atividades"

## Arquivos Modificados

### app.py
- **Importações**: Adicionado `from sqlalchemy import func`
- **Rota `/dashboard`**:
  - Consulta SQL para contar atividades por matéria
  - Consulta SQL para contar atividades por data
  - Preparação de dados para JavaScript (labels e valores)
  - Passagem de dados para o template

### templates/dashboard.html
- **Estrutura HTML**:
  - Adicionados `<canvas>` para os gráficos
  - Script inline para definir variáveis globais com dados Jinja2
  - Inclusão de Chart.js via CDN
  - Inclusão do script personalizado `grafico.js`

### static/scripts/grafico.js
- **Estrutura**:
  - Event listener `DOMContentLoaded` para garantir carregamento do DOM
  - Verificações de existência dos elementos canvas
  - Configuração completa dos gráficos Chart.js
  - Gradientes e cores customizadas
  - Animações e interações

## Tecnologias Utilizadas
- **Chart.js**: Biblioteca JavaScript para gráficos
- **SQLAlchemy**: Para consultas de agregação no banco de dados
- **Jinja2**: Para passar dados do Python para JavaScript
- **CSS**: Para estilos visuais (gradientes, cores)

## Como Funciona

1. **Backend (Python)**:
   - Executa consultas SQL para obter dados agregados
   - Processa os resultados em listas para JavaScript
   - Renderiza template com dados

2. **Frontend (HTML/JS)**:
   - Define variáveis globais com dados JSON
   - Carrega Chart.js
   - Executa script que cria os gráficos

3. **Interação**:
   - Gráficos responsivos
   - Tooltips ao passar mouse
   - Animações suaves

## Benefícios
- **Visual atraente**: Gráficos modernos e interativos
- **Informações claras**: Dados de estudo visualizados de forma intuitiva
- **Performance**: Código organizado e otimizado
- **Manutenibilidade**: Separação entre backend e frontend

## Testes Realizados
- Aplicação inicia sem erros
- Dashboard carrega com gráficos renderizados
- Dados dinâmicos baseados no usuário logado
- Responsividade em diferentes tamanhos de tela

## Próximos Passos
- Adicionar mais tipos de gráficos (ex: pizza para distribuição por matéria)
- Implementar filtros por período
- Adicionar exportação de gráficos
- Melhorar acessibilidade (alt texts, navegação por teclado)
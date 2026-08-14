# 🔍 Auditoria Inicial - FocusUp Front-End

**Data:** 2026-08-13  
**Status:** ⏳ Em progresso

---

## 📊 Sumário Executivo

O FocusUp possui um front-end funcional com identidade visual, mas apresenta **problemas estruturais significativos** que dificultam manutenção e escalabilidade. É necessário **refatoração moderada**, não reescrita.

---

## 📁 Estrutura de Arquivos

### Templates (23 arquivos)
```
templates/
├── base.html (template pai - 710 linhas)
├── dashboard.html (394 linhas, + 244 linhas CSS inline)
├── autenticação/ (login, cadastro, recuperação senha)
├── páginas internas/ (atividades, metas, calendário, perfil, etc)
└── auxiliares/ (ajuda, sobre, política, termos)
```

**Problemas identificados:**
- 16 templates com `<style>` inline (CSS dentro do HTML)
- Dashboard.html contém 244 linhas de CSS interno
- Base.html contém 450+ linhas de CSS interno
- Duplicação de estilos entre templates

### CSS (831 linhas total)
```
static/css/
├── style.css (2123 linhas) ⚠️ MONOLÍTICO
├── formularios.css (404 linhas)
├── pagina_inicial.css (304 linhas)
```

**Problemas:**
- **CSS não modularizado**: Tudo em 3 arquivos gigantes
- **Sem variáveis CSS**: Cores/espaçamentos repetidos
- **Duplicação de estilos**: Cards, botões, formulários repetidos
- **Dark mode espalhado**: Seletores `.dark-mode` em múltiplos arquivos
- **Sem breakpoints claros**: Media queries desorganizadas

### JavaScript (3470 linhas total)
```
static/scripts/
├── main.js (128 linhas) - Gerencia: dropdown, tema, mobile menu, notificações
├── grafico.js (183 linhas) - Charts
├── calendario.js (178 linhas) - Calendário
├── listar_atividade.js (55 linhas) - Lista atividades
├── ajuda.js (76 linhas) - Ajuda
└── footer.js (19 linhas) - Footer
```

**Problemas:**
- Lógica global em `main.js` carregada em TODAS as páginas
- Sem modularização clara
- Sem separação de concerns
- Scripts específicos carregados globalmente

---

## 🎨 Identidade Visual

### Cores Identificadas
- **Primária:** `#1a73e8` (azul Google-like)
- **Secundária:** `#4285f4` (azul claro)
- **Fundo claro:** `#eff1f3` (cinza muito claro)
- **Fundo escuro:** `#121212` e `#1e1e1e`
- **Verde:** `#2e7d32`, `#43a047` (botões, ações positivas)
- **Vermelho:** `#d32f2f`, `#f44336` (delete, erro)

**Problema:** Cores hard-coded, sem CSS variables

### Tipografia
- **Fonte primária:** Poppins
- **Alternativa:** Kodchasan, Inter
- **Variações:** 100-900 (mas não todas usadas consistentemente)

**Problema:** Múltiplas fontes, inconsistência de pesos

---

## 🔧 Componentes

### Cards
- `.card-dash`, `.card-sobre`, `.card-materias_mais_estudadas`, `.card_artigo`
- **Problema:** 4 classes diferentes para o mesmo conceito
- **Estilos duplicados:** box-shadow, border-radius, padding, animation

### Botões
- `.botao_add_atv` (botão circular para adicionar)
- `.btn-add-materia` (botão para matéria)
- `.btn-delete-materia` (botão delete)
- `.link-pomodoro` (link estilizado como botão)
- **Problema:** Sem sistema de botões coerente (primary, secondary, danger)

### Formulários
- Estilos em `formularios.css`
- Inputs com `.form-add-materia input`
- **Problema:** Sem variação clara (text, email, password, checkbox, radio)

### Modais & Dropdowns
- Dropdown de usuário em base.html (450+ linhas CSS)
- Menu mobile em base.html
- **Problema:** Tudo inline, difícil de manutenção

---

## 📱 Responsividade

### Status Atual
- **Mobile menu:** ✅ Implementado
- **Media queries:** ⚠️ Espalhadas, sem breakpoints padrão
- **Breakpoints encontrados:** 768px, 480px (inconsistente)
- **Gaps no layout:** `gap: 15rem` em desktop pode quebrar em mobile

**Problemas:**
- Layout principal usa `gap: 15rem` (rigid)
- Main é `flex` com `max-width: 65%` + `max-width: 35%` (não adaptável)
- Sem mobile-first approach
- Sem teste claro em tablets

---

## ♿ Acessibilidade

### Status Atual
- ⚠️ **Labels:** Algumas inputs sem `<label>` adequado
- ⚠️ **ARIA:** Minimal (tem aria-label em alguns ícones)
- ⚠️ **Semântica:** `<main>`, `<header>`, `<footer>` presentes ✅
- ⚠️ **Contraste:** Não verificado (potencial problema em light/dark)
- ⚠️ **Foco:** Sem estilos claros de `:focus-visible`
- ⚠️ **Navegação por teclado:** Mobile menu pode ter issues

---

## 🌙 Dark Mode

### Status Atual
- ✅ Implementado com `.dark-mode` class
- ✅ Toggle em header
- ✅ Persistência no servidor
- ⚠️ **Cobertura:** Nem todos os componentes cobertos
  - Cards do dashboard ✅
  - Menu mobile ✅
  - Dropdown ✅
  - Formulários ❌
  - Tabelas ❌
  - Modais ❓

**Problema:** Seletores duplicados (ex: `body.dark-mode .card-sobre` em múltiplos arquivos)

---

## 🎭 Modo Claro

### Problemas
- Muita dependência de cor para transmitir informação
- Sem sistema de bordas/outlines claros
- Sombras inconsistentes

---

## 🔗 Ligação Frontend-Backend

### Estrutura Jinja2
- ✅ Base.html com `{% block %}` bem estruturado
- ✅ Passes de dados corretos
- ✅ Loop e condicionais funcionais
- ⚠️ Lógica misturada em templates (ex: cálculos de tempo em dashboard.html)

### APIs Identificadas
- `/alternar_tema` - POST para salvar preferência
- `/api/notificacoes_nao_lidas` - GET para badge
- Rotas esperadas presentes no Flask

---

## 📈 Performance

### Otimizações Necessárias
- ❌ CSS não minificado
- ❌ Sem lazy-loading de scripts
- ✅ FontAwesome CDN carregado (bom)
- ✅ Chart.js CDN (bom)
- ⚠️ Sem controle de carregamento de scripts por página

---

## 🚩 Problemas Críticos (Prioridade Alta)

1. **CSS Monolítico** - 2123 linhas em style.css, impossível manter
2. **Estilos Inline** - 244 linhas em dashboard.html, 450+ em base.html
3. **Sem Variáveis CSS** - Cores hard-coded em centenas de lugares
4. **Duplicação Massiva** - Cards, botões, formulários com estilos repetidos
5. **Dark Mode Frágil** - Seletores duplicados, fácil quebrar
6. **Mobile Responsividade Fraca** - Gaps rigid, layouts não adaptáveis
7. **Sem Modularização JS** - Scripts globais carregados desnecessariamente
8. **Acessibilidade Mínima** - Foco visível fraco, labels faltando, contraste duvidoso

---

## ✅ O Que Está Bem

- ✅ Arquitetura Jinja2 correta
- ✅ Identidade visual clara (cores, tema)
- ✅ Componentes funcionais
- ✅ Dark mode base implementado
- ✅ Mobile menu implementado
- ✅ FontAwesome icons bem utilizados
- ✅ Animações discretas e agradáveis

---

## 🎯 Próximas Etapas (Fases)

### FASE 1: Fundação (CSS Variables & Modularização)
- [ ] Criar `variables.css` com sistema de design
- [ ] Extrair CSS inline de base.html
- [ ] Extrair CSS inline de dashboard.html
- [ ] Modularizar CSS por componente

### FASE 2: Componentes (Sistema de Componentes)
- [ ] Criar componentes Jinja reutilizáveis
- [ ] Padronizar cards
- [ ] Padronizar botões
- [ ] Padronizar formulários
- [ ] Padronizar dropdowns/modais

### FASE 3: Layout Global
- [ ] Refatorar navbar
- [ ] Refatorar mobile menu
- [ ] Refatorar footer
- [ ] Melhorar dark mode

### FASE 4: Dashboard
- [ ] Redesenhar layout
- [ ] Melhorar hierarquia
- [ ] Cards de métricas

### FASE 5: Páginas Internas
- [ ] Atividades
- [ ] Metas
- [ ] Calendário
- [ ] Perfil

### FASE 6: Autenticação
- [ ] Login
- [ ] Cadastro
- [ ] Recuperação senha

### FASE 7: Responsividade & Acessibilidade
- [ ] Testes em dispositivos
- [ ] Melhorias de contraste
- [ ] Labels ARIA
- [ ] Navegação por teclado

### FASE 8: Limpeza & Validação
- [ ] Remover CSS/JS duplicado
- [ ] Validar todas as rotas
- [ ] Testar dark/light mode
- [ ] Performance review

---

## 📝 Notas

- Sem dependências externas além de FontAwesome e Chart.js
- Backend (Flask) está funcionando bem
- Database está funcionando
- Sem testes automatizados identificados
- Projeto está em produção (não é protótipo)

---

**Próxima ação:** Aguardar resultado completo da auditoria exploratória para detalhes adicionais.

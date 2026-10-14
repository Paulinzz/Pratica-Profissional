# 🚀 FASE 2 - COMPONENTES JINJA2 & REFATORAÇÃO

**Data de Início:** 2026-08-14  
**Duração Estimada:** 2-3 horas  
**Status:** ⏳ EM PROGRESSO

---

## 📋 OBJETIVO

Criar componentes Jinja2 reutilizáveis e remover CSS inline de templates, padronizando toda a interface.

---

## ✅ CHECKLIST DA FASE 2

### Passo 1: Criar Diretório de Componentes
- [ ] Criar `templates/components/` para componentes reutilizáveis

### Passo 2: Componentes de UI Básicos
- [ ] `components/button.html` (botões com variantes)
- [ ] `components/card.html` (cards base)
- [ ] `components/form_group.html` (form groups)
- [ ] `components/input.html` (inputs modernos)
- [ ] `components/badge.html` (badges)
- [ ] `components/alert.html` (alerts/flash messages)

### Passo 3: Componentes de Layout
- [ ] `components/header.html` (navbar completa)
- [ ] `components/footer.html` (footer completa)
- [ ] `components/sidebar.html` (sidebar se necessário)

### Passo 4: Componentes de Dashboard
- [ ] `components/card_metric.html` (cards de métrica)
- [ ] `components/card_activity.html` (cards de atividade)
- [ ] `components/materias_list.html` (lista de matérias)

### Passo 5: Remover CSS Inline
- [ ] Extrair CSS inline de `dashboard.html` (244 linhas)
- [ ] Criar `pages/dashboard.html` component se necessário
- [ ] Testar que tudo funciona

### Passo 6: Validação
- [ ] Testar Flask (sem erros)
- [ ] Verificar visual em light mode
- [ ] Verificar visual em dark mode
- [ ] Testar responsividade

---

## 📊 ARQUIVOS A CRIAR

```
templates/
├── components/
│   ├── __init__.html (vazio, apenas marcador)
│   ├── button.html
│   ├── card.html
│   ├── form_group.html
│   ├── input.html
│   ├── badge.html
│   ├── alert.html
│   ├── card_metric.html
│   ├── card_activity.html
│   └── materias_list.html
│
└── [outros templates - sem mudanças estruturais]
```

---

## 🎯 COMPONENTES A CRIAR

### 1. Button Component
**Uso:** `{% include 'components/button.html' with context %}`
- Variantes: primary, secondary, success, danger, ghost, link
- Tamanhos: sm, md, lg
- Estados: normal, hover, active, disabled, loading
- Suporta ícones

### 2. Card Component
**Uso:** `{% include 'components/card.html' %}`
- Card base com padding, shadow, border-radius
- Slots: header, body, footer
- Dark mode automático

### 3. Form Group Component
**Uso:** `{% include 'components/form_group.html' %}`
- Label + Input + Helper text
- Validação visual (valid/invalid)
- Suporte a ícones

### 4. Input Component
**Uso:** `{% include 'components/input.html' %}`
- Tipos: text, email, password, number, date, etc
- Estados: focus, disabled, valid, invalid
- Placeholder e label

### 5. Badge Component
**Uso:** `{% include 'components/badge.html' %}`
- Variantes: primary, success, danger, warning, info
- Outlined e filled

### 6. Alert Component
**Uso:** `{% include 'components/alert.html' %}`
- Tipos: success, error, warning, info
- Com ícone e mensagem
- Dismissible opcional

### 7. Card Metric Component
**Uso:** `{% include 'components/card_metric.html' %}`
- Especializado para dashboard
- Valor grande + Label + Ícone
- Cores customizáveis

### 8. Card Activity Component
**Uso:** `{% include 'components/card_activity.html' %}`
- Para atividades, metas, etc
- Título + Meta + Status
- Border esquerdo colorido

### 9. Materias List Component
**Uso:** `{% include 'components/materias_list.html' %}`
- Lista horizontal de matérias
- Cada item é um card
- Scrollável

---

## 📝 ESTRUTURA DE COMPONENTES

Cada componente seguirá este padrão:

```html
{# components/button.html #}
{# 
   button.html - Componente de botão reutilizável
   
   Uso:
   {% include 'components/button.html' with context %}
   
   Parâmetros:
   - text: texto do botão
   - type: primary|secondary|success|danger|ghost|link (default: primary)
   - size: sm|md|lg (default: md)
   - href: URL (se for link)
   - disabled: true|false
   - icon: ícone FontAwesome
#}

<button class="btn btn-{{ type|default('primary') }} btn-{{ size|default('md') }}"
        {% if disabled %}disabled{% endif %}>
    {% if icon %}<i class="fa-solid fa-{{ icon }}"></i>{% endif %}
    {{ text }}
</button>
```

---

## 🔄 FLUXO DE TRABALHO

### Passo por Passo

1. **Criar componentes básicos** (buttons, cards, forms)
2. **Testar cada componente** isoladamente
3. **Integrar em templates existentes**
4. **Remover CSS inline** progressivamente
5. **Validar no navegador**
6. **Testar dark mode**
7. **Testar responsividade**

---

## ⚠️ CUIDADOS

- ✓ Não quebrar templates existentes
- ✓ Manter compatibilidade com Flask
- ✓ Testar após cada mudança
- ✓ Validar dark mode funciona
- ✓ Não remover CSS inline muito rápido (fazer gradualmente)

---

## 📅 TEMPO ESTIMADO POR COMPONENTE

| Componente | Tempo | Status |
|-----------|-------|--------|
| button.html | 15min | ⏳ |
| card.html | 15min | ⏳ |
| form_group.html | 20min | ⏳ |
| input.html | 20min | ⏳ |
| badge.html | 10min | ⏳ |
| alert.html | 15min | ⏳ |
| card_metric.html | 15min | ⏳ |
| card_activity.html | 15min | ⏳ |
| materias_list.html | 20min | ⏳ |
| Testes & Validação | 30min | ⏳ |
| **TOTAL** | **~2,5 horas** | ⏳ |

---

## 🎯 SUCESSO ESPERADO

Ao final de FASE 2:
- ✅ Componentes Jinja2 reutilizáveis criados
- ✅ CSS inline removido de templates
- ✅ Sem quebra de funcionalidade
- ✅ Código mais limpo e manutenível
- ✅ Pronto para FASE 3

---

**Próximo:** Começar a criar componentes

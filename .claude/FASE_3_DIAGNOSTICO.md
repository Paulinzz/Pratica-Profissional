# 📊 FASE 3 - DIAGNÓSTICO INICIAL

**Data:** 2026-08-14  
**Status:** Iniciando FASE 3 - Layout Global  
**Objetivo:** Refatorar navbar e footer, remover CSS inline, implementar componentes

---

## 🔍 ANÁLISE DO BASE.HTML

### Estrutura Atual
```
base.html (274 linhas)
├─ Header (24-116) - 92 linhas
│  ├─ Logo (25-31)
│  ├─ Mobile Toggle (34-36)
│  ├─ Links (38-44)
│  ├─ Theme Toggle (46-51)
│  ├─ Notifications (54-59)
│  └─ User Dropdown (62-115)
│
├─ Content Block (119-121)
│
├─ Mobile Menu (125-159) - 35 linhas
│
└─ Footer (161-255) - 95 linhas
   ├─ Footer Header (165-172)
   ├─ Footer Content (174-246)
   │  ├─ Section 1: Sobre
   │  ├─ Section 2: Navegação
   │  ├─ Section 3: Recursos
   │  └─ Section 4: Suporte
   └─ Footer Bottom (250-253)
```

### Inline Styles Encontrados
| Linha | Elemento | Estilo | Ação |
|-------|----------|--------|------|
| 55 | notification-link | `position: relative;` | Mover para header.css |
| 57 | notification-badge | `display: none;` | Mover para header.css |
| 148 | mobile-menu divider | `border-top: 1px solid #e0e0e0; margin: 10px 0;` | Mover para header.css |

**Total CSS Inline:** ~3 estilos (8 linhas aproximadamente)

---

## 🎯 PLANO DE REFATORAÇÃO

### FASE 3.1: Extrair Navbar
**Arquivo novo:** `templates/navbar.html`

**Conteúdo:**
- Header completo (linhas 24-116)
- Mobile menu (linhas 125-159)
- Incluir em base.html como `{% include 'navbar.html' %}`

**CSS:**
- Remover 3 inline styles
- Consolidar em `static/css/layouts/header.css`

### FASE 3.2: Extrair Footer
**Arquivo novo:** `templates/footer.html`

**Conteúdo:**
- Footer completo (linhas 161-255)
- Incluir em base.html como `{% include 'footer.html' %}`

**CSS:**
- Verificar inline styles
- Consolidar em `static/css/layouts/footer.css`

### FASE 3.3: Atualizar base.html
- Remover header direto
- Remover footer direto
- Manter mobile menu global? (precisa decisão)
- Deixar apenas template structure limpa

---

## 📊 MÉTRICAS ESPERADAS

| Métrica | Esperado |
|---------|----------|
| Linhas removidas de base.html | ~180 linhas |
| Inline styles removidos | 3 |
| Novos arquivos | 2 (navbar.html, footer.html) |
| CSS modificado | header.css, footer.css |
| Redução base.html | 274 → ~94 linhas |
| Dark mode coverage | 100% |
| Responsividade | 5 breakpoints ✓ |

---

## ✅ CHECKLIST FASE 3

### Preparação
- [x] Analisar base.html
- [x] Identificar inline styles
- [x] Revisar header.css e footer.css
- [ ] Entender componentes disponíveis

### Desenvolvimento
- [ ] Criar navbar.html
- [ ] Remover header de base.html
- [ ] Remover mobile menu de base.html
- [ ] Criar footer.html
- [ ] Remover footer de base.html
- [ ] Remover inline styles
- [ ] Atualizar header.css
- [ ] Atualizar footer.css

### Validação
- [ ] Testar Jinja2 syntax
- [ ] Testar Flask
- [ ] Verificar dark mode
- [ ] Testar responsividade
- [ ] Verificar mobile menu
- [ ] Verificar dropdown

### Documentação
- [ ] Criar FASE_3_COMPLETA.md
- [ ] Atualizar STATUS_PROJETO.md

---

## 🚀 PRÓXIMO PASSO

Criar `templates/navbar.html` com:
- Header (linhas 24-116 de base.html)
- Mobile menu (linhas 125-159 de base.html)
- Integração com componentes se necessário

**Tempo estimado:** 15 min

---

**Status:** ✅ Diagnóstico completo  
**Próxima ação:** Criar navbar.html

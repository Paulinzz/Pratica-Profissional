// Sistema de Tema Unificado - FocusUp
const ThemeManager = {
    // Chave padronizada
    STORAGE_KEY: 'focusup_theme',
    
    // Inicializar tema ao carregar a página
    init() {
        const savedTheme = localStorage.getItem(this.STORAGE_KEY) || 'light';
        this.applyTheme(savedTheme);
        this.updateButtonIcon(savedTheme);
    },
    
    // Aplicar tema no DOM
    applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
        // Atualizar meta tag para mobile (opcional, mas recomendado)
        this.updateMetaThemeColor(theme);
    },
    
    // Salvar e aplicar tema
    setTheme(theme) {
        localStorage.setItem(this.STORAGE_KEY, theme);
        this.applyTheme(theme);
        this.updateButtonIcon(theme);
        
        // Se tiver AJAX para salvar no servidor (opcional)
        this.saveToServer(theme);
    },
    
    // Toggle usado pelo botão da navbar
    toggle() {
        const currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    },
    
    // Atualizar ícone do botão (sol/lua)
    updateButtonIcon(theme) {
        const themeIcons = document.querySelectorAll('.theme-toggle-icon, #theme-icon, .nav-theme-icon');
        themeIcons.forEach(icon => {
            if (theme === 'dark') {
                icon.classList.remove('fa-moon', 'bi-moon');
                icon.classList.add('fa-sun', 'bi-sun');
            } else {
                icon.classList.remove('fa-sun', 'bi-sun');
                icon.classList.add('fa-moon', 'bi-moon');
            }
        });
    },
    
    // Atualizar cor da barra do navegador mobile
    updateMetaThemeColor(theme) {
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1a2e' : '#ffffff');
        }
    },
    
    // Salvar no servidor via AJAX (para persistir entre dispositivos)
    saveToServer(theme) {
        fetch('/api/preferences/theme', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ theme: theme })
        }).catch(err => console.log('Erro ao salvar tema no servidor:', err));
    }
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    
    // Vincular botões da navbar
    const themeToggleBtns = document.querySelectorAll('#theme-toggle, .theme-toggle, [data-action="toggle-theme"]');
    themeToggleBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            ThemeManager.toggle();
        });
    });
    
    // Vincular select da página de configurações (se existir)
    const themeSelect = document.querySelector('#theme-select, select[name="theme"]');
    if (themeSelect) {
        themeSelect.addEventListener('change', (e) => {
            ThemeManager.setTheme(e.target.value);
        });
    }
});
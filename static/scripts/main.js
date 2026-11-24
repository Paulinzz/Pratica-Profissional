        // Toggle do dropdown de usuário
        function toggleDropdown() {
            const dropdown = document.getElementById('userDropdown');
            const isActive = dropdown.classList.toggle('active');
            const userInfo = dropdown.querySelector('.user-info');
            if (userInfo) {
                userInfo.setAttribute('aria-expanded', isActive ? 'true' : 'false');
            }
        }

        function closeDropdown() {
            const dropdown = document.getElementById('userDropdown');
            dropdown.classList.remove('active');
            const userInfo = dropdown.querySelector('.user-info');
            if (userInfo) {
                userInfo.setAttribute('aria-expanded', 'false');
            }
        }

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('userDropdown');
            if (dropdown && !dropdown.contains(event.target)) {
                closeDropdown();
            }
        });

        // Fechar dropdown ao clicar em links dentro dele
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('userDropdown');
            if (dropdown && dropdown.contains(event.target)) {
                const link = event.target.closest('a');
                if (link && dropdown.contains(link)) {
                    closeDropdown();
                }
            }
        });

        // Fechar dropdown com ESC
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeDropdown();
                closeMobileMenu();
            }
        });

        // Acessibilidade: Enter/Space no trigger do dropdown


        // Footer toggle
        function toggleFooterSection(element) {
            const section = element.parentElement;
            section.classList.toggle('active');
        }

        // Função para atualizar badge de notificações
        function updateNotificationBadge() {
            fetch('/api/notificacoes_nao_lidas')
                .then(response => response.json())
                .then(data => {
                    const badge = document.getElementById('notificationBadge');
                    const previousCount = parseInt(badge.textContent) || 0;
                    if (data.nao_lidas > 0) {
                        badge.textContent = data.nao_lidas > 99 ? '99+' : data.nao_lidas;
                        badge.style.display = 'inline-block';

                        // Mostrar notificação do navegador se houver novas
                        if (data.nao_lidas > previousCount && previousCount > 0) {
                            showBrowserNotification('Novas notificações', `Você tem ${data.nao_lidas} notificações não lidas.`);
                        }
                    } else {
                        badge.style.display = 'none';
                    }
                })
                .catch(error => console.error('Erro ao buscar notificações:', error));
        }

        // Função para mostrar notificações do navegador
        function showBrowserNotification(title, body) {
            if ('Notification' in window) {
                if (Notification.permission === 'granted') {
                    new Notification(title, { body: body, icon: '/static/imagens/correto.png' });
                } else if (Notification.permission !== 'denied') {
                    Notification.requestPermission().then(permission => {
                        if (permission === 'granted') {
                            new Notification(title, { body: body, icon: '/static/imagens/correto.png' });
                        }
                    });
                }
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            // Entrada suave em todas as páginas
            document.body.classList.remove('page-entering');
            window.requestAnimationFrame(function() {
                document.body.classList.add('page-entering');
            });

            // Transição suave para links internos
            document.querySelectorAll('a[href]').forEach(function(link) {
                link.addEventListener('click', function(event) {
                    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
                    if (link.target && link.target !== '_self') return;
                    if (link.hasAttribute('download')) return;

                    const url = new URL(link.href, window.location.href);
                    if (url.origin !== window.location.origin) return;
                    if (url.pathname === window.location.pathname && url.search === window.location.search && url.hash) return;

                    event.preventDefault();
                    document.body.classList.remove('page-entering');
                    document.body.classList.add('page-leaving');

                    window.setTimeout(function() {
                        window.location.href = url.href;
                    }, 180);
                });
            });

            // Transição suave antes do envio de formulários
            document.querySelectorAll('form').forEach(function(form) {
                form.addEventListener('submit', function(event) {
                    if (event.defaultPrevented || form.dataset.noPageTransition === 'true') return;
                    if (form.target && form.target !== '_self') return;
                    if (form.method === 'dialog') return;

                    event.preventDefault();
                    document.body.classList.remove('page-entering');
                    document.body.classList.add('page-leaving');

                    window.setTimeout(function() {
                        form.submit();
                    }, 180);
                });
            });

            document.querySelectorAll('[data-password-toggle]').forEach(function(toggle) {
                toggle.addEventListener('click', function() {
                    const inputId = toggle.getAttribute('data-password-toggle');
                    const input = document.getElementById(inputId);
                    if (!input) return;

                    const isVisible = input.type === 'text';
                    input.type = isVisible ? 'password' : 'text';
                    toggle.setAttribute('aria-pressed', isVisible ? 'false' : 'true');
                    toggle.setAttribute('aria-label', isVisible ? 'Mostrar senha' : 'Ocultar senha');
                    toggle.setAttribute('title', isVisible ? 'Mostrar senha' : 'Ocultar senha');

                    const icon = toggle.querySelector('i');
                    if (icon) {
                        icon.classList.toggle('fa-eye', isVisible);
                        icon.classList.toggle('fa-eye-slash', !isVisible);
                    }
                });
            });

            const footerSections = document.querySelectorAll('.footer-section h3');
            footerSections.forEach(function(header) {
                header.addEventListener('click', function() {
                    footerSections.forEach(function(otherHeader) {
                        if (otherHeader !== header) {
                            otherHeader.parentElement.classList.remove('active');
                        }
                    });
                });
            });

            // Atualizar badge de notificações
            updateNotificationBadge();

            // Atualizar badge a cada 30 segundos
            setInterval(updateNotificationBadge, 30000);
        });

        // Função para alternar tema
        function toggleTheme() {
            const body = document.body;
            const themeToggle = document.getElementById('themeToggle');
            const themeIcon = document.getElementById('themeIcon');

            // Alternar classe do body
            body.classList.toggle('dark-mode');

            // Atualizar ícone
            if (body.classList.contains('dark-mode')) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
                themeToggle.classList.add('dark');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
                themeToggle.classList.remove('dark');
            }

            // Salvar preferência no servidor
            fetch('/alternar_tema', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Erro ao salvar preferência de tema');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
            });
        }


        // Funções do menu mobile
        function toggleMobileMenu() {
            const overlay = document.getElementById('mobileMenuOverlay');
            const menu = document.getElementById('mobileMenu');
            overlay.classList.toggle('active');
            menu.classList.toggle('active');
        }

        function closeMobileMenu() {
            const overlay = document.getElementById('mobileMenuOverlay');
            const menu = document.getElementById('mobileMenu');
            overlay.classList.remove('active');
            menu.classList.remove('active');
        }
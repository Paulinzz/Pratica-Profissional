       // Toggle do dropdown de usuário
        function toggleDropdown() {
            const dropdown = document.getElementById('userDropdown');
            dropdown.classList.toggle('active');
        }

        // Fechar dropdown ao clicar fora
        document.addEventListener('click', function(event) {
            const dropdown = document.getElementById('userDropdown');
            if (!dropdown.contains(event.target)) {
                dropdown.classList.remove('active');
            }
        });

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
       // Função para toggle das seções do footer
        function toggleFooterSection(element) {
            const section = element.parentElement;
            section.classList.toggle('active');
        }

        // Auto-fechar outras seções quando uma é aberta (opcional)
        document.addEventListener('DOMContentLoaded', function() {
            const footerSections = document.querySelectorAll('.footer-section h3');
            footerSections.forEach(function(header) {
                header.addEventListener('click', function() {
                    // Opcional: fechar outras seções quando uma é aberta
                     footerSections.forEach(function(otherHeader) {
                         if (otherHeader !== header) {
                            otherHeader.parentElement.classList.remove('active');
                         }
                     });
                });
            });
        });
        
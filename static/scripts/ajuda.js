function toggleFAQ(element) {
        const faqItem = element.parentElement;
        const wasActive = faqItem.classList.contains('active');
        
        // Fecha todas as FAQs
        document.querySelectorAll('.faq-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Abre a FAQ clicada se não estava ativa
        if (!wasActive) {
            faqItem.classList.add('active');
        }
    }

    function scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Abre automaticamente a FAQ relacionada
            const faqPergunta = section.querySelector('.faq-pergunta');
            if (faqPergunta && !section.classList.contains('active')) {
                setTimeout(() => {
                    toggleFAQ(faqPergunta);
                }, 500);
            }
        }
    }

document.getElementById('busca-input').addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();

        // Filtrar categorias de ajuda
        const categoriaCards = document.querySelectorAll('.categoria-card');
        categoriaCards.forEach(card => {
            const title = card.querySelector('h3').textContent.toLowerCase();
            const description = card.querySelector('p').textContent.toLowerCase();
            const listItems = Array.from(card.querySelectorAll('li')).map(li => li.textContent.toLowerCase()).join(' ');

            if (title.includes(searchTerm) || description.includes(searchTerm) || listItems.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = searchTerm.length > 0 ? 'none' : 'block';
            }
        });

        // Filtrar tutoriais
        const tutorialCards = document.querySelectorAll('.tutorial-card');
        tutorialCards.forEach(card => {
            const title = card.querySelector('h4').textContent.toLowerCase();
            const description = card.querySelector('p').textContent.toLowerCase();

            if (title.includes(searchTerm) || description.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = searchTerm.length > 0 ? 'none' : 'block';
            }
        });

        // Filtrar FAQs
        const faqItems = document.querySelectorAll('.faq-item');
        faqItems.forEach(item => {
            const pergunta = item.querySelector('.faq-pergunta h4').textContent.toLowerCase();
            const resposta = item.querySelector('.faq-resposta p').textContent.toLowerCase();

            if (pergunta.includes(searchTerm) || resposta.includes(searchTerm)) {
                item.style.display = 'block';
                if (searchTerm.length > 2) {
                    item.classList.add('active');
                }
            } else {
                item.style.display = searchTerm.length > 0 ? 'none' : 'block';
                item.classList.remove('active');
            }
        });
    });
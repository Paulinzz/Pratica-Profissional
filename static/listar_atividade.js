function filtrarAtividades() {
            const input = document.getElementById('buscar-atividade');
            const filter = input.value.toLowerCase();
            const atividades = document.querySelectorAll('.atividade-item');
            
            atividades.forEach(atividade => {
                const materia = atividade.dataset.materia.toLowerCase();
                const assunto = atividade.dataset.assunto.toLowerCase();
                
                if (materia.includes(filter) || assunto.includes(filter)) {
                    atividade.style.display = 'flex';
                } else {
                    atividade.style.display = 'none';
                }
            });
        }

        // Função para ordenar atividades
    function ordenarAtividades() {
            const select = document.getElementById('ordenar');
            const lista = document.getElementById('lista-atividades');
            const atividades = Array.from(document.querySelectorAll('.atividade-item'));
            
            atividades.sort((a, b) => {
                switch(select.value) {
                    case 'materia':
                        return a.dataset.materia.localeCompare(b.dataset.materia);
                    case 'recente':
                        return b.dataset.data.localeCompare(a.dataset.data);
                    case 'antiga':
                        return a.dataset.data.localeCompare(b.dataset.data);
                    default:
                        return 0;
                }
            });
            
            atividades.forEach(atividade => lista.appendChild(atividade));
        }

        // Calcular total de horas (exemplo simplificado)
        document.addEventListener('DOMContentLoaded', function() {
            const duracoes = document.querySelectorAll('.meta-item i.fa-clock');
            let totalMinutos = 0;
            
            duracoes.forEach(item => {
                const texto = item.parentElement.textContent.trim();
                const match = texto.match(/(\d+):(\d+)/);
                if (match) {
                    totalMinutos += parseInt(match[1]) * 60 + parseInt(match[2]);
                }
            });
            
            const horas = Math.floor(totalMinutos / 60);
            const minutos = totalMinutos % 60;
            document.getElementById('total-horas').textContent = `${horas}h${minutos > 0 ? minutos + 'm' : ''}`;
        });
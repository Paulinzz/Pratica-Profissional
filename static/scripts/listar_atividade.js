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
            const filterValue = (document.getElementById('buscar-atividade')?.value || '').toLowerCase();
            
            atividades.sort((a, b) => {
                switch(select.value) {
                    case 'materia':
                        return a.dataset.materia.localeCompare(b.dataset.materia);
                    case 'recente':
                        return b.dataset.data.localeCompare(a.dataset.data);
                    case 'antiga':
                        return a.dataset.data.localeCompare(b.dataset.data);
                    case 'duracao':
                        const durA = parseDuration(a.dataset.duracao || '00:00');
                        const durB = parseDuration(b.dataset.duracao || '00:00');
                        return durB - durA;
                    default:
                        return 0;
                }
            });
            
            atividades.forEach(atividade => {
                const materia = atividade.dataset.materia.toLowerCase();
                const assunto = atividade.dataset.assunto.toLowerCase();
                if (!filterValue || materia.includes(filterValue) || assunto.includes(filterValue)) {
                    atividade.style.display = 'flex';
                } else {
                    atividade.style.display = 'none';
                }
                lista.appendChild(atividade);
            });
        }

        function parseDuration(str) {
            if (!str || str === '00:00') return 0;
            const parts = str.split(':');
            if (parts.length === 2) {
                const h = parseInt(parts[0], 10);
                const m = parseInt(parts[1], 10);
                if (isNaN(h) || isNaN(m)) return 0;
                return h * 60 + m;
            }
            return 0;
        }

        // Calcular total de horas (exemplo simplificado)
        document.addEventListener('DOMContentLoaded', function() {
            const duracoes = document.querySelectorAll('.meta-item i.fa-clock, .meta-item i.fa-regular.fa-clock');
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
            const totalHorasEl = document.getElementById('total-horas');
            if (totalHorasEl) {
                const statNumber = totalHorasEl.querySelector('.stat-number');
                if (statNumber) {
                    statNumber.textContent = `${horas}h${minutos > 0 ? minutos + 'm' : ''}`;
                }
            }
        });
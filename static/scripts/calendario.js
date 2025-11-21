document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendario');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'pt-br',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        buttonText: {
            today: 'Hoje',
            month: 'Mês',
            week: 'Semana',
            day: 'Dia'
        },
        events: function(fetchInfo, successCallback, failureCallback) {
            fetch('/api/calendario_eventos')
                .then(response => response.json())
                .then(data => {
                    successCallback(data.eventos);
                })
                .catch(error => {
                    console.error('Erro ao carregar eventos:', error);
                    failureCallback(error);
                });
        },
        eventClick: function(info) {
            mostrarDetalhesEvento(info.event);
        },
        eventDidMount: function(info) {
            // Adicionar tooltip
            info.el.title = info.event.title;
        },
        dayMaxEvents: 3,
        moreLinkClick: 'popover',
        height: 'auto',
        contentHeight: 600,
        aspectRatio: 1.35
    });

    calendar.render();

    // Funções do modal
    window.mostrarDetalhesEvento = function(event) {
        const modal = document.getElementById('eventoModal');
        const titleEl = document.getElementById('eventoTitle');
        const detalhesEl = document.getElementById('eventoDetalhes');
        const btnEditar = document.getElementById('btnEditar');

        titleEl.textContent = event.title;

        const props = event.extendedProps;
        let detalhesHTML = '';

        if (props.tipo === 'atividade') {
            detalhesHTML += `
                <div class="evento-detalhe">
                    <i class="fa-solid fa-tag"></i>
                    <div class="evento-detalhe-content">
                        <div class="evento-detalhe-label">Tipo</div>
                        <div class="evento-detalhe-value">Atividade de Estudo</div>
                    </div>
                </div>
                <div class="evento-detalhe">
                    <i class="fa-solid fa-book"></i>
                    <div class="evento-detalhe-content">
                        <div class="evento-detalhe-label">Matéria</div>
                        <div class="evento-detalhe-value">${props.materia}</div>
                    </div>
                </div>
            `;

            if (props.descricao) {
                detalhesHTML += `
                    <div class="evento-detalhe">
                        <i class="fa-solid fa-align-left"></i>
                        <div class="evento-detalhe-content">
                            <div class="evento-detalhe-label">Descrição</div>
                            <div class="evento-detalhe-value">${props.descricao}</div>
                        </div>
                    </div>
                `;
            }

            if (props.duracao) {
                detalhesHTML += `
                    <div class="evento-detalhe">
                        <i class="fa-solid fa-clock"></i>
                        <div class="evento-detalhe-content">
                            <div class="evento-detalhe-label">Duração</div>
                            <div class="evento-detalhe-value">${props.duracao}</div>
                        </div>
                    </div>
                `;
            }

            btnEditar.onclick = function() {
                // Redirecionar para editar atividade
                const atividadeId = event.id.split('_')[1];
                window.location.href = `/editar_atividade/${atividadeId}`;
            };
            btnEditar.style.display = 'inline-flex';

        } else if (props.tipo === 'meta') {
            detalhesHTML += `
                <div class="evento-detalhe">
                    <i class="fa-solid fa-bullseye"></i>
                    <div class="evento-detalhe-content">
                        <div class="evento-detalhe-label">Tipo</div>
                        <div class="evento-detalhe-value">Meta de Estudo</div>
                    </div>
                </div>
                <div class="evento-detalhe">
                    <i class="fa-solid fa-info-circle"></i>
                    <div class="evento-detalhe-content">
                        <div class="evento-detalhe-label">Status</div>
                        <div class="evento-detalhe-value">${props.status === 'concluido' ? 'Concluída' : 'Ativa'}</div>
                    </div>
                </div>
            `;

            if (props.materia) {
                detalhesHTML += `
                    <div class="evento-detalhe">
                        <i class="fa-solid fa-book"></i>
                        <div class="evento-detalhe-content">
                            <div class="evento-detalhe-label">Matéria</div>
                            <div class="evento-detalhe-value">${props.materia}</div>
                        </div>
                    </div>
                `;
            }

            if (props.descricao) {
                detalhesHTML += `
                    <div class="evento-detalhe">
                        <i class="fa-solid fa-align-left"></i>
                        <div class="evento-detalhe-content">
                            <div class="evento-detalhe-label">Descrição</div>
                            <div class="evento-detalhe-value">${props.descricao}</div>
                        </div>
                    </div>
                `;
            }

            btnEditar.onclick = function() {
                // Redirecionar para editar meta
                const metaId = event.id.split('_')[1];
                window.location.href = `/editar_meta/${metaId}`;
            };
            btnEditar.style.display = 'inline-flex';
        }

        detalhesEl.innerHTML = detalhesHTML;
        modal.classList.add('show');
    };

    window.fecharModal = function() {
        const modal = document.getElementById('eventoModal');
        modal.classList.remove('show');
    };

    // Fechar modal ao clicar fora
    document.getElementById('eventoModal').addEventListener('click', function(e) {
        if (e.target === this) {
            fecharModal();
        }
    });

    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fecharModal();
        }
    });
});

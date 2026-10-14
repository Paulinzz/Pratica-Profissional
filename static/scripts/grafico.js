document.addEventListener('DOMContentLoaded', function() {
    const labelsDash = Array.isArray(window.labelsDash) ? window.labelsDash : [];
    const dataDash = Array.isArray(window.dataDash) ? window.dataDash : [];
    const labelsMaterias = Array.isArray(window.labelsMaterias) ? window.labelsMaterias : [];
    const dataMaterias = Array.isArray(window.dataMaterias) ? window.dataMaterias : [];

    // Helper: detect dark mode
    function isDarkMode() {
        return document.body.classList.contains('dark-mode');
    }

    // Helper: get CSS variable value
    function getCssVar(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }

    // Chart default options with dark mode support
    const getChartDefaults = function() {
        const dark = isDarkMode();
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: dark ? 'rgba(30,30,30,0.95)' : 'rgba(0,0,0,0.8)',
                    titleColor: dark ? '#e0e0e0' : '#fff',
                    bodyColor: dark ? '#b0b0b0' : '#fff',
                    cornerRadius: 8,
                    padding: 12,
                    titleFont: { weight: '600' },
                    bodyFont: { size: 13 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: dark ? 'rgba(255,255,255,0.06)' : 'rgba(200,200,200,0.3)'
                    },
                    ticks: {
                        color: dark ? '#808080' : '#666',
                        font: { size: 12 }
                    }
                },
                x: {
                    grid: {
                        color: dark ? 'rgba(255,255,255,0.06)' : 'rgba(200,200,200,0.3)'
                    },
                    ticks: {
                        color: dark ? '#808080' : '#666',
                        font: { size: 12 }
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeInOutQuart'
            }
        };
    };

    // Line Chart - Activities per day
    const ctxDash = document.getElementById('chartDash');
    if (ctxDash && labelsDash.length > 0 && dataDash.length > 0) {
        const contextDash = ctxDash.getContext('2d');
        const gradientDash = contextDash.createLinearGradient(0, 0, 0, 400);
        gradientDash.addColorStop(0, 'rgba(26, 115, 232, 0.3)');
        gradientDash.addColorStop(1, 'rgba(26, 115, 232, 0.02)');

        const chartDash = new Chart(contextDash, {
            type: 'line',
            data: {
                labels: labelsDash,
                datasets: [{
                    label: 'Atividades Registradas',
                    data: dataDash,
                    borderColor: '#1a73e8',
                    backgroundColor: gradientDash,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#1a73e8',
                    pointBorderColor: isDarkMode() ? '#1e1e1e' : '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                ...getChartDefaults(),
                plugins: {
                    ...getChartDefaults().plugins,
                    title: {
                        display: false
                    }
                }
            }
        });
    }

    // Bar Chart - Study time per subject
    const colors = [
        '#1a73e8', '#2e7d32', '#f57c00', '#0097a7',
        '#7b1fa2', '#c62828', '#00838f', '#e65100'
    ];

    const ctxMaterias = document.getElementById('chartMaterias');
    if (ctxMaterias && labelsMaterias.length > 0 && dataMaterias.length > 0) {
        const contextMaterias = ctxMaterias.getContext('2d');
        const chartMaterias = new Chart(contextMaterias, {
            type: 'bar',
            data: {
                labels: labelsMaterias,
                datasets: [{
                    label: 'Tempo Gasto (minutos)',
                    data: dataMaterias,
                    backgroundColor: colors.slice(0, labelsMaterias.length).map(c => {
                        const r = parseInt(c.slice(1, 3), 16);
                        const g = parseInt(c.slice(3, 5), 16);
                        const b = parseInt(c.slice(5, 7), 16);
                        return `rgba(${r}, ${g}, ${b}, 0.8)`;
                    }),
                    borderColor: colors.slice(0, labelsMaterias.length),
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                    hoverBackgroundColor: colors.slice(0, labelsMaterias.length)
                }]
            },
            options: {
                ...getChartDefaults(),
                plugins: {
                    ...getChartDefaults().plugins,
                    title: {
                        display: false
                    }
                },
                scales: {
                    ...getChartDefaults().scales,
                    y: {
                        ...getChartDefaults().scales.y,
                        ticks: {
                            ...getChartDefaults().scales.y.ticks,
                            callback: function(value) {
                                const horas = Math.floor(value / 60);
                                const mins = value % 60;
                                if (horas > 0 && mins > 0) {
                                    return horas + 'h ' + mins + 'min';
                                } else if (horas > 0) {
                                    return horas + 'h';
                                }
                                return mins + 'min';
                            }
                        }
                    }
                }
            }
        });
    }
});

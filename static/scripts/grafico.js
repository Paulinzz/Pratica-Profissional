document.addEventListener('DOMContentLoaded', function() {
    // Gradiente para o gráfico de linha
    const ctxDash = document.getElementById('chartDash');
    if (ctxDash) {
        const contextDash = ctxDash.getContext('2d');
        const gradientDash = contextDash.createLinearGradient(0, 0, 0, 400);
        gradientDash.addColorStop(0, 'rgba(75, 192, 192, 0.4)');
        gradientDash.addColorStop(1, 'rgba(75, 192, 192, 0.1)');

        const chartDash = new Chart(contextDash, {
            type: 'line',
            data: {
                labels: window.labelsDash,
                datasets: [{
                    label: 'Atividades Registras por Dia',
                    data: window.dataDash,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: gradientDash,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Atividades Registradas por Dia',
                        font: {
                            size: 18,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        cornerRadius: 8
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(200,200,200,0.3)'
                        },
                        ticks: {
                            color: '#666'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(200,200,200,0.3)'
                        },
                        ticks: {
                            color: '#666'
                        }
                    }
                },
                animation: {
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Cores variadas para o gráfico de barras
    const colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 205, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)',
        'rgba(255, 99, 255, 0.8)',
        'rgba(99, 255, 132, 0.8)'
    ];

    const ctxMaterias = document.getElementById('chartMaterias');
    if (ctxMaterias) {
        const contextMaterias = ctxMaterias.getContext('2d');
        const chartMaterias = new Chart(contextMaterias, {
            type: 'bar',
            data: {
                labels: window.labelsMaterias,
                datasets: [{
                    label: 'Número de Atividades',
                    data: window.dataMaterias,
                    backgroundColor: colors.slice(0, window.labelsMaterias.length),
                    borderColor: colors.slice(0, window.labelsMaterias.length).map(color => color.replace('0.8', '1')),
                    borderWidth: 2,
                    borderRadius: 8,
                    borderSkipped: false,
                    hoverBackgroundColor: colors.slice(0, window.labelsMaterias.length).map(color => color.replace('0.8', '1')),
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Matérias Mais Estudadas',
                        font: {
                            size: 18,
                            weight: 'bold'
                        },
                        color: '#333'
                    },
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y + ' atividades';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(200,200,200,0.3)'
                        },
                        ticks: {
                            color: '#666',
                            stepSize: 1
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(200,200,200,0.3)'
                        },
                        ticks: {
                            color: '#666',
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutBounce',
                    delay: function(context) {
                        return context.dataIndex * 200;
                    }
                }
            }
        });
    }
});
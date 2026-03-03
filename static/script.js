document.addEventListener('DOMContentLoaded', function() {
    console.log('Script loaded');
    const uploadForm = document.getElementById('upload-form');
    
    if (!uploadForm) {
        console.error('Form not found!');
        return;
    }
    
    const resultsDiv = document.getElementById('results');
    const dataTableDiv = document.getElementById('data-table');
    const analyticsSummaryDiv = document.getElementById('analytics-summary');
    const loadMoreBtn = document.getElementById('load-more');
    const pdfExportSection = document.getElementById('pdf-export-section');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');
    const analyzeAiBtn = document.getElementById('analyze-ai-btn');
    const aiAnalysisContainer = document.getElementById('ai-analysis-container');
    const aiAnalysisContent = document.getElementById('ai-analysis-content');
    const aiAnalysisTitle = document.getElementById('ai-analysis-title');
    
    // Chart elements
    const chartControls = document.getElementById('chart-controls');
    const chartTypeSelect = document.getElementById('chart-type');
    const xAxisSelect = document.getElementById('x-axis-col');
    const yAxisSelect = document.getElementById('y-axis-col');
    const generateChartBtn = document.getElementById('generate-chart');
    const chartCanvas = document.getElementById('myChart');
    let myChart = null;

    let filepath = null;
    let offset = 100;
    let columnTypes = null;

    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const fileInput = document.getElementById('file-input');
        
        if (!fileInput.files.length) {
            alert('Пожалуйста, выберите файл');
            return;
        }
        
        const formData = new FormData(this);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data);
            if (data.error) {
                alert('Ошибка: ' + data.error);
                return;
            }

            resultsDiv.classList.remove('hidden');

            // Display table
            dataTableDiv.innerHTML = data.table_html;
            filepath = data.filepath;
            columnTypes = data.column_types;
            offset = 100;
            const table = dataTableDiv.querySelector('table');
            if (table && table.rows.length - 1 < 100) {
                loadMoreBtn.classList.add('hidden');
            } else {
                loadMoreBtn.classList.remove('hidden');
            }

            // Display analytics
            let analyticsHtml = '<ul>';
            for (const col in data.analytics) {
                const stats = data.analytics[col];
                analyticsHtml += `<li><strong>${col}:</strong> `;
                let statItems = [];
                for (const statName in stats) {
                    statItems.push(`${statName}: ${stats[statName].toLocaleString()}`);
                }
                analyticsHtml += statItems.join(', ') + '</li>';
            }
            analyticsHtml += '</ul>';
            analyticsSummaryDiv.innerHTML = analyticsHtml;

            // Показываем блок визуализации только если есть данные для графиков
            const hasChartData = (columnTypes.categorical && columnTypes.categorical.length > 0 && 
                                 columnTypes.numerical && columnTypes.numerical.length > 0) ||
                                ((columnTypes.date && columnTypes.date.length > 0 || 
                                  columnTypes.year && columnTypes.year.length > 0) && 
                                 columnTypes.numerical && columnTypes.numerical.length > 0);
            
            const chartsContainer = document.getElementById('charts-container');
            if (!hasChartData) {
                chartsContainer.classList.add('hidden');
            } else {
                chartsContainer.classList.remove('hidden');
                // Setup chart controls только если есть данные
                updateChartSelectors();
            }
            
            if (myChart) {
                myChart.destroy();
            }
            pdfExportSection.classList.remove('hidden');
            aiAnalysisContainer.classList.add('hidden');
            aiAnalysisContent.innerHTML = '';
        })
        .catch(error => {
            console.error('Ошибка при загрузке файла:', error);
            alert('Ошибка при загрузке файла: ' + error.message);
        });
    });

    chartTypeSelect.addEventListener('change', updateChartSelectors);

    function updateChartSelectors() {
        const chartType = chartTypeSelect.value;
        let xOptions, yOptions;

        if (chartType === 'bar') {
            xOptions = columnTypes.categorical;
            yOptions = columnTypes.numerical;
        } else if (chartType === 'line') {
            // Ось X: даты и колонки «год» (числовые)
            const dateCols = columnTypes.date || [];
            const yearCols = columnTypes.year || [];
            xOptions = [...new Set([...dateCols, ...yearCols])];
            yOptions = columnTypes.numerical;
        }

        populateSelect(xAxisSelect, xOptions);
        populateSelect(yAxisSelect, yOptions);

        // Скрываем весь блок визуализации, если нет подходящих данных
        if (!xOptions || xOptions.length === 0 || !yOptions || yOptions.length === 0) {
            chartControls.classList.add('hidden');
            generateChartBtn.classList.add('hidden');
        } else {
            chartControls.classList.remove('hidden');
            generateChartBtn.classList.remove('hidden');
            generateChartBtn.disabled = false;
        }
    }

    function populateSelect(selectElement, options) {
        selectElement.innerHTML = '';
        if (!options || options.length === 0) {
            selectElement.innerHTML = '<option>Нет подходящих колонок</option>';
            selectElement.disabled = true;
        } else {
            options.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt;
                option.textContent = opt;
                selectElement.appendChild(option);
            });
            selectElement.disabled = false;
        }
    }

    generateChartBtn.addEventListener('click', function() {
        if (!filepath || !xAxisSelect.value || !yAxisSelect.value || xAxisSelect.value === 'Нет подходящих колонок' || yAxisSelect.value === 'Нет подходящих колонок') {
            alert('Пожалуйста, выберите корректные колонки для построения диаграммы.');
            return;
        }

        fetch('/generate_chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filepath: filepath,
                chart_type: chartTypeSelect.value,
                x_col: xAxisSelect.value,
                y_col: yAxisSelect.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Ошибка при построении диаграммы: ' + data.error);
                return;
            }
            if (typeof Chart === 'undefined') {
                alert('Библиотека графиков не загрузилась. В настройках браузера отключите блокировку отслеживания для этого сайта (127.0.0.1) или обновите страницу.');
                return;
            }

            if (myChart) {
                myChart.destroy();
            }

            const chartConfig = {
                type: chartTypeSelect.value,
                data: {
                    labels: data.chart_data.labels,
                    datasets: [{
                        label: data.chart_data.label,
                        data: data.chart_data.data,
                        backgroundColor: chartTypeSelect.value === 'line' ? 'rgba(0, 86, 179, 0.1)' : 'rgba(0, 86, 179, 0.7)',
                        borderColor: 'rgba(0, 86, 179, 1)',
                        borderWidth: chartTypeSelect.value === 'line' ? 2 : 1,
                        fill: chartTypeSelect.value === 'line' ? false : true,
                        tension: chartTypeSelect.value === 'line' ? 0.1 : 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            enabled: true
                        }
                    },
                    scales: chartTypeSelect.value === 'line' ? {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Время'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Значение'
                            },
                            beginAtZero: false
                        }
                    } : {}
                }
            };

            myChart = new Chart(chartCanvas.getContext('2d'), chartConfig);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при построении диаграммы.');
        });
    });

    loadMoreBtn.addEventListener('click', function() {
        fetch('/load_more', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filepath: filepath, offset: offset })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Ошибка: ' + data.error);
                return;
            }

            if (data.end) {
                loadMoreBtn.classList.add('hidden');
            }

            const tableBody = dataTableDiv.querySelector('tbody');
            if (tableBody) {
                tableBody.innerHTML += data.html;
                offset += 100;
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка при загрузке данных.');
        });
    });

    function resetButtonState(button, text, spinner, disabledState) {
        const btnText = button.querySelector('.btn-text');
        const btnSpinner = button.querySelector('.btn-spinner');

        btnText.textContent = text;
        if (spinner) spinner.classList.add('hidden');
        button.classList.remove('loading');
        button.disabled = disabledState;
    }

    function setButtonLoadingState(button, loadingText, spinner) {
        const btnText = button.querySelector('.btn-text');
        const btnSpinner = button.querySelector('.btn-spinner');

        btnText.textContent = loadingText;
        if (spinner) spinner.classList.remove('hidden');
        button.classList.add('loading');
        button.disabled = true;
    }

    downloadPdfBtn.addEventListener('click', handleDownloadPdf);

    function handleDownloadPdf() {
        const btnSpinner = downloadPdfBtn.querySelector('.btn-spinner');
        setButtonLoadingState(downloadPdfBtn, 'Генерация', btnSpinner);

        const printWindow = window.open('', '_blank');
        if (!printWindow) {
            alert('Пожалуйста, разрешите всплывающие окна для этого сайта');
            resetButtonState(downloadPdfBtn, 'Скачать PDF', btnSpinner, false);
            return;
        }

        // Build the report HTML
        let reportHtml = `
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Аналитический Отчет</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #0056b3; font-size: 24px; margin-bottom: 10px; }
        .date { font-size: 14px; color: #666; margin-bottom: 20px; }
        h3 { color: #333; font-size: 18px; margin: 20px 0 10px 0; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        ul { margin: 0; padding-left: 20px; }
        img { max-width: 100%; height: auto; margin-bottom: 20px; }
        @media print {
            body { padding: 0; }
            .no-print { display: none; }
        }
    </style>
</head>
<body>
    <h1>Аналитический Отчет</h1>
    <p class="date">Дата формирования: ${new Date().toLocaleDateString('ru-RU')}</p>
    <button class="no-print" onclick="window.print()" style="padding: 10px 20px; background: #0056b3; color: white; border: none; cursor: pointer; margin-bottom: 20px;">Печать / Сохранить как PDF</button>
`;

        // Add data table
        const dataTableDiv = document.getElementById('data-table');
        if (dataTableDiv) {
            reportHtml += '<h3>Данные из файла</h3>';
            reportHtml += dataTableDiv.innerHTML;
        }

        // Add analytics
        const analyticsSummary = document.getElementById('analytics-summary');
        if (analyticsSummary) {
            reportHtml += '<h3>Базовая аналитика</h3>';
            reportHtml += analyticsSummary.innerHTML;
        }

        // Добавляем анализ от ИИ, если он есть
        if (!aiAnalysisContainer.classList.contains('hidden') && aiAnalysisContent.innerHTML.trim() !== '') {
            reportHtml += `
                <div style="page-break-before: always; margin-top: 20px;"></div>
                <h2 style="text-align: center;">Анализ от локальной AI (Ollama)</h2>
                <div>${aiAnalysisContent.innerHTML}</div>
            `;
        }

        // Add chart
        if (myChart) {
            reportHtml += '<h3>Визуализация данных</h3>';
            reportHtml += '<img src="' + myChart.toBase64Image() + '" />';
        }

        reportHtml += `
</body>
</html>
`;

        printWindow.document.write(reportHtml);
        printWindow.document.close();
        
        setTimeout(() => {
            resetButtonState(downloadPdfBtn, 'Скачать PDF', btnSpinner, false);
        }, 2000);
    }

    // --- AI ANALYSIS ---
    analyzeAiBtn.addEventListener('click', handleAnalyzeAi);

    function handleAnalyzeAi() {
        const aiBtnSpinner = analyzeAiBtn.querySelector('.btn-spinner');
        setButtonLoadingState(analyzeAiBtn, '🤖 Анализирую...', aiBtnSpinner);
        
        aiAnalysisContainer.classList.remove('hidden');
        aiAnalysisContent.innerHTML = `
            <div class="ai-loading">
                <div class="cat-analyst">
                    <div class="cat-body">
                        <div class="cat-head">
                            <div class="cat-ear cat-ear-left"></div>
                            <div class="cat-ear cat-ear-right"></div>
                            <div class="cat-face">
                                <div class="cat-eye cat-eye-left"></div>
                                <div class="cat-eye cat-eye-right"></div>
                                <div class="cat-nose"></div>
                                <div class="cat-whiskers cat-whiskers-left"></div>
                                <div class="cat-whiskers cat-whiskers-right"></div>
                            </div>
                        </div>
                        <div class="cat-paws">
                            <div class="cat-paw"></div>
                            <div class="cat-paw"></div>
                        </div>
                    </div>
                    <div class="laptop">
                        <div class="laptop-screen">
                            <div class="code-line"></div>
                            <div class="code-line"></div>
                            <div class="code-line"></div>
                        </div>
                    </div>
                </div>
                <p class="loading-text">Котик-аналитик изучает ваши данные...</p>
                <div class="loading-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;

        const table = dataTableDiv.querySelector('table');
        if (!table) {
            aiAnalysisContent.innerHTML = '<p style="color: #EF4444;">❌ Нет данных для анализа</p>';
            resetButtonState(analyzeAiBtn, '🤖 Проанализировать с AI', aiBtnSpinner, false);
            return;
        }

        const rows = Array.from(table.rows).slice(0, 15);
        const tableData = rows.map(row => Array.from(row.cells).map(cell => cell.innerText.trim()).join(', '));

        fetch('/analyze_data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ table_data: tableData })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                aiAnalysisContent.innerHTML = `<div style="color: #EF4444; border: 2px solid #FEE2E2; padding: 16px; border-radius: 12px; background: #FEF2F2;">
                    <strong>❌ Ошибка:</strong> ${data.error}
                </div>`;
            } else {
                if (typeof marked !== 'undefined') {
                    aiAnalysisContent.innerHTML = marked.parse(data.ai_analysis);
                } else {
                    aiAnalysisContent.innerHTML = `<div style="white-space: pre-wrap;">${data.ai_analysis}</div>`;
                }
            }
        })
        .catch(error => {
            aiAnalysisContent.innerHTML = `<div style="color: #EF4444; border: 2px solid #FEE2E2; padding: 16px; border-radius: 12px; background: #FEF2F2;">
                <strong>❌ Ошибка соединения:</strong> ${error.message}<br>
                <small>Убедитесь, что Ollama запущена и модель загружена.</small>
            </div>`;
        })
        .finally(() => {
            resetButtonState(analyzeAiBtn, '🤖 Проанализировать с AI', aiBtnSpinner, false);
        });
    }
});
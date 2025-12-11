
/**
 * Dashboard Renderer for Tidal Cassini
 * Renders AI JSON analysis into a high-fidelity HTML Dashboard
 */

// Function to render the entire dashboard
function renderDashboard(data) {
    console.log("Rendering Dashboard with data:", data);

    // 1. Get Container
    const container = document.getElementById('reportPreview');
    if (!container) return;

    // Clear previous content
    container.innerHTML = '';
    container.className = 'dashboard-container';

    // 2. Parse Data (Handle potential stringified JSON)
    let aiResult = data;
    if (typeof data === 'string') {
        try {
            aiResult = JSON.parse(data);
        } catch (e) {
            console.error("JSON Parse Error:", e);
            container.innerHTML = `<div class="error-box">數據解析錯誤，請稍後再試。</div>`;
            return;
        }
    }

    // Extract key sections (adapt to your AI JSON structure)
    // Assuming structure: { score: 8.5, analysis: "...", daily_revenue: ..., age_data_csv: "...", ... }
    // If wrapped in 'result', unwrap it
    if (aiResult.result) aiResult = aiResult.result;

    // --- BUILD HTML STRUCTURE ---

    // A. Score & Summary Section (Hero)
    const heroSection = document.createElement('div');
    heroSection.className = 'dashboard-hero';
    heroSection.innerHTML = `
        <div class="score-card">
            <div class="score-ring">
                <canvas id="scoreChart"></canvas>
                <div class="score-value">
                    <span class="number">${aiResult.score || '-'}</span>
                    <span class="label">綜合評分</span>
                </div>
            </div>
        </div>
        <div class="hero-summary">
            <h3><i class="fa-solid fa-robot"></i> AI 評估總結</h3>
            <div class="summary-text">${formatText(aiResult.summary_text || aiResult.summary || '無總結資料')}</div>
        </div>
    `;
    container.appendChild(heroSection);

    // B. Key Metrics Grid (Big Numbers)
    const metricsGrid = document.createElement('div');
    metricsGrid.className = 'dashboard-grid metrics-grid';
    metricsGrid.innerHTML = `
        <div class="metric-card">
            <div class="metric-icon"><i class="fa-solid fa-sack-dollar"></i></div>
            <div class="metric-label">預估月營收</div>
            <div class="metric-value">NT$ ${formatNumber((aiResult.daily_revenue || 0) * 30)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon"><i class="fa-solid fa-shop"></i></div>
            <div class="metric-label">預估翻桌率</div>
            <div class="metric-value">${aiResult.turnover_rate || '-'} <small>次/日</small></div>
        </div>
        <div class="metric-card">
            <div class="metric-icon"><i class="fa-solid fa-users"></i></div>
            <div class="metric-label">目標客群</div>
            <div class="metric-value text-sm">${aiResult.target_audience || '一般大眾'}</div>
        </div>
        <div class="metric-card">
            <div class="metric-icon"><i class="fa-solid fa-location-dot"></i></div>
            <div class="metric-label">商圈屬性</div>
            <div class="metric-value text-sm">${aiResult.location_type || '混合型'}</div>
        </div>
    `;
    container.appendChild(metricsGrid);

    // C. Charts Section (Radar & Bar & Pie)
    const chartsGrid = document.createElement('div');
    chartsGrid.className = 'dashboard-grid charts-grid';
    chartsGrid.innerHTML = `
        <!-- Radar Chart: 5 Force Analysis -->
        <div class="chart-card">
            <h4><i class="fa-solid fa-crosshairs"></i> 商圈五力分析</h4>
            <div class="chart-wrapper">
                <canvas id="radarChart"></canvas>
            </div>
            <div class="chart-insight">
                <p>${aiResult.radar_comment || '該商圈在人流與交通方面具有顯著優勢，但在競爭程度上需要留意。'}</p>
            </div>
        </div>

        <!-- Bar Chart: Revenue vs Cost -->
        <div class="chart-card">
            <h4><i class="fa-solid fa-chart-simple"></i> 收支預估模型</h4>
            <div class="chart-wrapper">
                <canvas id="financeChart"></canvas>
            </div>
        </div>

        <!-- Doughnut: Cost Structure -->
        <div class="chart-card">
             <h4><i class="fa-solid fa-chart-pie"></i> 成本結構佔比</h4>
             <div class="chart-wrapper">
                <canvas id="costChart"></canvas>
            </div>
        </div>
        
        <!-- Bar: Age Distribution -->
        <div class="chart-card">
             <h4><i class="fa-solid fa-people-group"></i> 客群年齡分佈</h4>
             <div class="chart-wrapper">
                <canvas id="ageChart"></canvas>
            </div>
        </div>
    `;
    container.appendChild(chartsGrid);

    // D. Detailed Analysis Grid (The "Meat" of the report)
    const analysisSection = document.createElement('div');
    analysisSection.className = 'dashboard-grid analysis-grid';
    analysisSection.innerHTML = `
        <div class="analysis-card full-width">
             <h4><i class="fa-solid fa-users-viewfinder"></i> 微觀人口與消費力分析</h4>
             <div class="analysis-text">${formatText(aiResult.population_body)}</div>
        </div>
        
        <div class="analysis-card">
             <h4><i class="fa-solid fa-shop-lock"></i> 區域租金行情與門檻</h4>
             <div class="analysis-text">${formatText(aiResult.rent_body)}</div>
        </div>

        <div class="analysis-card">
             <h4><i class="fa-solid fa-chess-rook"></i> 市場競爭態勢分析</h4>
             <div class="analysis-text">${formatText(aiResult.competition_body)}</div>
        </div>

        <div class="analysis-card">
             <h4><i class="fa-solid fa-train-subway"></i> 生活機能與交通節點</h4>
             <div class="analysis-text">${formatText(aiResult.function_body)}</div>
        </div>

        <div class="analysis-card">
             <h4><i class="fa-solid fa-compass-drafting"></i> 空間規劃與坪效優化</h4>
             <div class="analysis-text">${formatText(aiResult.space_body)}</div>
        </div>
        
        <div class="analysis-card full-width bg-highlight">
             <h4><i class="fa-solid fa-calculator"></i> 財務模型與獲利預估</h4>
             <div class="analysis-text">${formatText(aiResult.financial_body)}</div>
        </div>

        <div class="analysis-card full-width">
             <h4><i class="fa-solid fa-bullhorn"></i> SWOT 策略分析</h4>
             <div class="analysis-text">${formatText(aiResult.marketing_body)}</div>
        </div>
        
        <div class="analysis-card full-width final-verdict">
             <h4><i class="fa-solid fa-gavel"></i> 專家總結與行動清單</h4>
             <div class="analysis-text">${formatText(aiResult.conclusion_text)}</div>
        </div>
    `;
    container.appendChild(analysisSection);

    // --- RENDER CHARTS (Chart.js) ---
    requestAnimationFrame(() => {
        initCharts(aiResult);
    });
}

function initCharts(data) {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom', labels: { color: '#ccc' } }
        }
    };

    // 1. Score Gauge (Doughnut)
    const score = parseFloat(data.score) || 0;
    new Chart(document.getElementById('scoreChart'), {
        type: 'doughnut',
        data: {
            labels: ['得分', '剩餘'],
            datasets: [{
                data: [score, 10 - score],
                backgroundColor: ['#ff7e33', 'rgba(255, 255, 255, 0.1)'],
                borderWidth: 0,
                cutout: '85%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            rotation: -90,
            circumference: 180,
        }
    });

    // 2. Radar Chart
    // Fake data logic if not provided (placeholder for now)
    // We can infer some from score or random drift around score
    const baseScore = Math.floor(score);
    new Chart(document.getElementById('radarChart'), {
        type: 'radar',
        data: {
            labels: ['人流人氣', '租金優勢', '競品分析', '消費潛力', '交通便利'],
            datasets: [{
                label: '本案評分',
                data: [baseScore, Math.min(10, baseScore + 1), Math.max(1, baseScore - 1), baseScore, Math.min(10, baseScore + 2)],
                backgroundColor: 'rgba(255, 126, 51, 0.2)',
                borderColor: '#ff7e33',
                pointBackgroundColor: '#fff',
                pointBorderColor: '#ff7e33',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#ff7e33'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    pointLabels: { color: '#ccc', font: { size: 12 } },
                    suggestedMin: 0,
                    suggestedMax: 10
                }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 3. Finance Bar Chart
    const revenue = (data.daily_revenue || 0) * 30;
    // Need Rent? Assuming passed in data or we estimate.
    // Hack: if rent not in AI result, we might need it from backend. 
    // For now, let's look for it in data or default.
    const rent = 50000; // Placeholder if missing
    new Chart(document.getElementById('financeChart'), {
        type: 'bar',
        data: {
            labels: ['預估月營收', '預估月租金'],
            datasets: [{
                label: '金額 (TWD)',
                data: [revenue, rent],
                backgroundColor: ['#2ecc71', '#e74c3c'],
                borderRadius: 5
            }]
        },
        options: {
            ...commonOptions,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255, 255, 255, 0.1)' }, ticks: { color: '#ccc' } },
                x: { grid: { display: false }, ticks: { color: '#ccc' } }
            }
        }
    });

    // 4. Cost Doughnut
    // Parsing CSV string "20,30,10,40"
    let costData = [25, 25, 35, 15]; // default
    if (data.cost_data_csv) {
        costData = data.cost_data_csv.split(',').map(Number);
    }
    // Register Plugin
    if (ChartDataLabels) Chart.register(ChartDataLabels);

    new Chart(document.getElementById('costChart'), {
        type: 'doughnut',
        data: {
            labels: ['租金', '人力', '食材', '其他'],
            datasets: [{
                data: costData,
                backgroundColor: ['#e74c3c', '#f1c40f', '#3498db', '#95a5a6'],
                borderWidth: 0
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#ccc' } },
                datalabels: {
                    color: '#fff',
                    font: { weight: 'bold', size: 14 },
                    formatter: (value, ctx) => {
                        return value + '%';
                    }
                }
            }
        }
    });

    // 5. Age Bar Chart
    let ageData = [5, 15, 30, 25, 15, 5, 5];
    if (data.age_data_csv) {
        ageData = data.age_data_csv.split(',').map(Number);
    }
    new Chart(document.getElementById('ageChart'), {
        type: 'bar',
        data: {
            labels: ['0-15', '16-25', '26-35', '36-45', '46-55', '56-65', '65+'],
            datasets: [{
                label: '佔比 (%)',
                data: ageData,
                backgroundColor: '#ff7e33',
                borderRadius: 4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: { display: false },
                x: { grid: { display: false }, ticks: { color: '#ccc' } }
            }
        }
    });
}

// Helper: Format large numbers with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Helper: Format text (convert newlines to <br>)
function formatText(text) {
    if (!text) return '';
    return text.split('\n').map(line => `<p>${line}</p>`).join('');
}

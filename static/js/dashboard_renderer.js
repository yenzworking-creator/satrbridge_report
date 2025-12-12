
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

    // --- DATA SOURCE EXTRACTION ---
    const dataSources = new Set(); // Use Set to avoid duplicates

    function cleanAndCollectSources(text) {
        if (!text) return '';
        // Regex to find [資料來源：...] or [資料來源:...] or similar
        // Captures the content inside the brackets
        const regex = /\[?資料來源[：:]\s*(.*?)\]/g;

        let cleanedText = text.replace(regex, (match, sourceContent) => {
            if (sourceContent) {
                dataSources.add(sourceContent.trim());
            }
            return ''; // Remove from original text
        });

        // Remove left-over empty brackets if any (optional cleanup)
        // cleanedText = cleanedText.replace(/\[\s*\]/g, ''); 

        return cleanedText;
    }

    // Apply cleaning to all text fields
    aiResult.population_body = cleanAndCollectSources(aiResult.population_body);
    aiResult.rent_body = cleanAndCollectSources(aiResult.rent_body);
    aiResult.competition_body = cleanAndCollectSources(aiResult.competition_body);
    aiResult.function_body = cleanAndCollectSources(aiResult.function_body);
    aiResult.space_body = cleanAndCollectSources(aiResult.space_body);
    aiResult.financial_body = cleanAndCollectSources(aiResult.financial_body);
    aiResult.marketing_body = cleanAndCollectSources(aiResult.marketing_body);
    aiResult.conclusion_text = cleanAndCollectSources(aiResult.conclusion_text);
    // Also check summary just in case
    aiResult.summary_text = cleanAndCollectSources(aiResult.summary_text);


    // --- BUILD HTML STRUCTURE ---

    // --- PDF Header & Footer Injection (Visual Only) ---
    const pdfHeader = document.createElement('div');
    pdfHeader.className = 'pdf-header-visual';
    pdfHeader.innerHTML = `
        <div class="header-left">
            <img src="/static/brand_assets/pdf_logo.png" alt="StarBridge Media" style="height: 40px;">
        </div>
        <div class="header-right">${new Date().toLocaleDateString()} | 專業評估報告</div>
    `;

    const pdfFooter = document.createElement('div');
    pdfFooter.className = 'pdf-footer-visual';
    pdfFooter.innerHTML = `
        <div class="footer-content">
            <p>本報告由 AI 大數據系統自動生成，僅供商業決策參考，不保證獲利。</p>
            <p>Tidal Cassini Intelligent System | © 2025 StarBridge Media</p>
        </div>
    `;

    // Prepend Header
    container.appendChild(pdfHeader);

    // A. Score & Summary Section (Hero)
    const heroSection = document.createElement('div');
    heroSection.className = 'dashboard-hero';

    // Construct Map URL
    let mapHtml = '';
    if (aiResult.lat && aiResult.lng && aiResult.google_maps_key) {
        const mapUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${aiResult.lat},${aiResult.lng}&zoom=15&size=400x300&markers=color:red%7C${aiResult.lat},${aiResult.lng}&key=${aiResult.google_maps_key}`;
        mapHtml = `
            <div class="location-map" style="flex: 0 0 auto; display: flex; align-items: center; justify-content: center;">
                <img src="${mapUrl}" alt="Location Map" style="height: 160px; width: auto; max-width: 100%; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            </div>
        `;
    }

    // New Layout: Top Row (Score + Map), Bottom (Text)
    heroSection.innerHTML = `
        <div class="hero-top-row" style="display: flex; flex-wrap: wrap; gap: 40px; align-items: stretch; margin-bottom: 24px;">
            <!-- Left: Score -->
            <div class="score-card" style="transform: none; flex: 0 0 auto; display: flex; flex-direction: column; align-items: center; justify-content: center; min-width: 200px;">
                <div class="score-ring" style="width: 160px; height: 160px; position: relative;">
                    <canvas id="scoreChart"></canvas>
                </div>
                <div class="score-value-container" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; pointer-events: none; margin-top:20px;">
                    <span class="number" style="font-size: 3.5rem; font-weight: 700; color: #ff7e33; line-height: 1;">${aiResult.score || '-'}</span>
                    <span class="label" style="font-size: 1rem; color: #666;">綜合評分</span>
                </div>
            </div>
            
            <!-- Right: Map -->
            ${mapHtml}
        </div>
        <!-- Bottom: Summary Text -->
        <div class="hero-summary" style="width: 100%; background: #f8f9fa; padding: 20px; border-radius: 12px; border-left: 4px solid #333;">
            <h3 style="margin-top: 0; font-size: 1.1rem; color: #333; margin-bottom: 12px;"><i class="fa-solid fa-robot"></i> AI 評估總結</h3>
            
            <!-- Context Banner -->
            <div style="background: #eef2f5; padding: 8px 12px; border-radius: 6px; margin-bottom: 12px; font-size: 0.9rem; color: #555;">
                <i class="fa-solid fa-circle-check" style="color: #2ecc71;"></i> 
                <strong>評估基準：</strong> 針對 <u>${aiResult.user_target || '一般大眾'}</u> 客群，於 <u>${aiResult.user_hours || '標準時段'}</u> 營業之綜合分析。
            </div>

            <div class="summary-text" style="line-height: 1.6; color: #444;">${formatText(aiResult.summary_text || aiResult.summary || '無總結資料')}</div>
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

    // E. Data Sources Footer (New Section)
    if (dataSources.size > 0) {
        const footerSection = document.createElement('div');
        footerSection.className = 'dashboard-footer source-section full-width';

        let sourceListHtml = '<ul>';
        dataSources.forEach(source => {
            sourceListHtml += `<li><i class="fa-solid fa-quote-left"></i> ${source}</li>`;
        });
        sourceListHtml += '</ul>';

        footerSection.innerHTML = `
            <h4><i class="fa-solid fa-book-open"></i> 資料來源彙整</h4>
            <div class="source-list">
                ${sourceListHtml}
            </div>
        `;
        // Append to the wrapper directly or create a new row? 
        // Let's append to container to keep it at the very bottom
        container.appendChild(footerSection);
    }

    // --- RENDER CHARTS (Chart.js) ---
    requestAnimationFrame(() => {
        initCharts(aiResult);
    });
}

// Global store for chart instances
window.chartInstances = {};

function initCharts(data) {
    // Helper to properly destroy old chart instance
    const destroyChart = (id) => {
        if (window.chartInstances[id]) {
            window.chartInstances[id].destroy();
        }
    };

    // --- CHARTS ---
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { position: 'bottom', labels: { color: '#666' } }
        }
    };

    // Helper for safe parsing
    const safeParseFloat = (value) => {
        const parsed = parseFloat(value);
        return isNaN(parsed) ? 0 : parsed;
    };

    // 1. Score Chart
    try {
        destroyChart('scoreChart');
        const scoreVal = safeParseFloat(data.score);
        console.log("Rendering Score Chart:", scoreVal);
        window.chartInstances['scoreChart'] = new Chart(document.getElementById('scoreChart'), {
            type: 'doughnut',
            data: {
                labels: ['得分', '剩餘'],
                datasets: [{
                    data: [scoreVal, 10 - scoreVal],
                    backgroundColor: ['#ff7e33', '#e0e0e0'],
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
    } catch (e) { console.error("Score Chart Error:", e); }

    // 2. Radar Chart
    try {
        destroyChart('radarChart');
        const scoreVal = safeParseFloat(data.score);
        const baseScore = Math.floor(scoreVal) || 5;
        window.chartInstances['radarChart'] = new Chart(document.getElementById('radarChart'), {
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
                        angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
                        grid: { color: 'rgba(0, 0, 0, 0.1)' },
                        pointLabels: { color: '#666', font: { size: 12 } },
                        suggestedMin: 0,
                        suggestedMax: 10,
                        ticks: { backdropColor: 'transparent', color: '#666' }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    } catch (e) { console.error("Radar Chart Error:", e); }

    // 3. Finance Bar Chart
    try {
        destroyChart('financeChart');
        const revenue = safeParseFloat(data.daily_revenue || 0) * 30;
        const rent = safeParseFloat(data.rent_cost || 50000);

        window.chartInstances['financeChart'] = new Chart(document.getElementById('financeChart'), {
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
                    y: { grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { color: '#666' } },
                    x: { grid: { display: false }, ticks: { color: '#666' } }
                }
            }
        });
    } catch (e) { console.error("Finance Chart Error:", e); }

    // 4. Cost Doughnut
    try {
        destroyChart('costChart');
        let costData = [25, 25, 35, 15]; // default
        if (data.cost_data_csv) {
            costData = data.cost_data_csv.split(',').map(Number);
        } else if (data.cost_data_csv) { // Fallback check
            costData = data.cost_data_csv.split(',').map(Number);
        }

        // Register Plugin Safely
        if (typeof ChartDataLabels !== 'undefined') {
            Chart.register(ChartDataLabels);
        }

        window.chartInstances['costChart'] = new Chart(document.getElementById('costChart'), {
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
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#666',
                            boxWidth: 12,
                            padding: 15,
                            font: { size: 11 }
                        }
                    },
                    datalabels: {
                        color: '#fff',
                        font: { weight: 'bold', size: 14 },
                        formatter: (value) => value + '%'
                    }
                }
            }
        });
    } catch (e) { console.error("Cost Chart Error:", e); }

    // 5. Age Bar Chart
    try {
        destroyChart('ageChart');
        let ageData = [5, 15, 30, 25, 15, 5, 5];
        if (data.age_data_csv) {
            ageData = data.age_data_csv.split(',').map(Number);
        }

        window.chartInstances['ageChart'] = new Chart(document.getElementById('ageChart'), {
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
                    x: { grid: { display: false }, ticks: { color: '#666' } }
                }
            }
        });
    } catch (e) { console.error("Age Chart Error:", e); }
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

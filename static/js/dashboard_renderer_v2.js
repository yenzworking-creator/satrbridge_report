
/**
 * Dashboard Renderer for Tidal Cassini
 * Renders AI JSON analysis into a high-fidelity HTML Dashboard
 */

console.log("DASHBOARD RENDERER LOADED V4.8");

// Function to render the entire dashboard
window.renderDashboard = function (data) {
    console.log("Rendering Dashboard with data:", data);

    // 1. Get Container
    const container = document.getElementById('reportPreview');
    if (!container) return;

    // Clear previous content - DISABLED FOR TEMPLATE MODE
    // container.innerHTML = ''; 
    // container.className = 'dashboard-container';

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

    // --- RENDER FUNCTION (TEMPLATE BASED) ---
    // NO MORE INNERHTML OVERWRITE. We bind data to the existing HTML elements.

    console.log("Renderer V5.0 (Template Mode) - Binding data to elements...");

    // 1. Fill Header Data (Score & Map)
    const scoreEl = document.getElementById('val-score');
    if (scoreEl) scoreEl.textContent = parseFloat(aiResult.score || 0).toFixed(1);

    const mapImg = document.getElementById('val-map-img');
    const mapPlace = document.getElementById('map-placeholder');
    if (mapImg && aiResult.lat && aiResult.lng && aiResult.google_maps_key) {
        const mapUrl = `https://maps.googleapis.com/maps/api/staticmap?center=${aiResult.lat},${aiResult.lng}&zoom=15&size=800x400&markers=color:red%7C${aiResult.lat},${aiResult.lng}&key=${aiResult.google_maps_key}`;
        mapImg.src = mapUrl;
        mapImg.style.display = 'block';
        if (mapPlace) mapPlace.style.display = 'none';
    } else {
        if (mapImg) mapImg.style.display = 'none';
        if (mapPlace) {
            mapPlace.style.display = 'block';
            mapPlace.textContent = '無地圖資料';
        }
    }

    // 2. Fill AI Summary & Context
    const userTarget = document.getElementById('val-user-target');
    if (userTarget) userTarget.textContent = aiResult.user_target || '一般大眾';

    const userHours = document.getElementById('val-user-hours');
    if (userHours) userHours.textContent = aiResult.user_hours || '標準時段';

    const summaryEl = document.getElementById('val-summary');
    if (summaryEl) summaryEl.innerHTML = formatText(aiResult.summary_text || aiResult.summary || '資料產出中...');

    // 3. Fill Key Metrics (Revenue, etc)
    const setMetric = (id, val, prefix = 'NT$ ') => {
        const el = document.getElementById(id);
        if (el) el.textContent = val ? prefix + formatNumber(val) : '-';
    };

    setMetric('val-revenue', (aiResult.daily_revenue || 0) * 30);
    setMetric('val-turnover', aiResult.turnover_rate, '');
    setMetric('val-roi', aiResult.return_period_months, '');
    setMetric('val-traffic', aiResult.est_daily_traffic, '');

    // 5. Fill Analysis Sections
    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = formatText(text || '尚無資料');
    };

    setText('val-pop-body', aiResult.population_body);
    setText('val-rent-body', aiResult.rent_body);
    setText('val-comp-body', aiResult.competition_body);
    setText('val-func-body', aiResult.function_body);
    setText('val-space-body', aiResult.space_body);
    setText('val-fin-body', aiResult.financial_body);
    setText('val-mkt-body', aiResult.marketing_body);
    setText('val-conclusion', aiResult.conclusion_text);

    // 6. Initialize Charts
    requestAnimationFrame(() => {
        initCharts(aiResult);
    });

    // CLEANUP: Legacy container clearing strings are GONE.
    // The Template updates purely by ID binding.
}
    < div class="analysis-card full-width bg-highlight" >
             <h4><i class="fa-solid fa-calculator"></i> 財務模型與獲利預估</h4>
             <div class="analysis-text">${formatText(aiResult.financial_body)}</div>
        </div >

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
            sourceListHtml += `< li > <i class="fa-solid fa-quote-left"></i> ${ source }</li > `;
        });
        sourceListHtml += '</ul>';

        footerSection.innerHTML = `
    < h4 > <i class="fa-solid fa-book-open"></i> 資料來源彙整</h4 >
        <div class="source-list">
            ${sourceListHtml}
        </div>
`;
        container.appendChild(footerSection);
    }

    // --- RENDER CHARTS (Chart.js) ---
    requestAnimationFrame(() => {
        initCharts(aiResult);
    });
}

// AUTO-TEST: Render immediately on load to verify layout (Debug Mode)
setTimeout(() => {
    console.log("Auto-rendering test data...");
    if(window.renderDashboard) {
        window.renderDashboard({
            score: 7.8,
            summary: "【自動測試】若您看到此內容，代表版面渲染正常。請嘗試輸入資料進行正式評估。",
            daily_revenue: 15000,
            rent: 45000,
            turnover_rate: 3.5,
            return_period_months: 14,
            est_daily_traffic: 1200,
            user_target: "測試客群",
            user_hours: "測試時段",
            financial_body: "營收預估正常。",
            marketing_body: "行銷策略建議。",
            conclusion_text: "總體評估良好。",
            lat: 25.0330, lng: 121.5654 // Taipei 101 approx
        });
    }
}, 1000);

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
            legend: { position: 'bottom', labels: { color: '#666', font: { size: 12 } } },
            datalabels: { display: false } // Disable by default to avoid errors
        }
    };

    // Helper for safe parsing
    const safeParseFloat = (value) => {
        const parsed = parseFloat(value);
        return isNaN(parsed) ? 0 : parsed;
    };

    // 1. Score Chart
    try {
        const canvas = document.getElementById('scoreChart');
        if (canvas) {
            destroyChart('scoreChart');
            const scoreVal = safeParseFloat(data.score);
            console.log("Rendering Score Chart:", scoreVal);

            // Explicitly set Doughnut options
            window.chartInstances['scoreChart'] = new Chart(canvas, {
                type: 'doughnut',
                data: {
                    labels: ['Score', 'Remaining'],
                    datasets: [{
                        data: [scoreVal, 10 - scoreVal],
                        backgroundColor: ['#ff7e33', '#eee'],
                        borderWidth: 0,
                        cutout: '90%' // Thinner ring for more text space
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    rotation: -90, // Start from top
                    circumference: 360,
                    plugins: { legend: { display: false }, tooltip: { enabled: false } }
                }
            });
        }
    } catch (e) { console.error("Score Chart Error:", e); }

    // 2. Radar Chart
    try {
        const canvas = document.getElementById('radarChart');
        if (canvas) {
            destroyChart('radarChart');

            // Fallback for Radar Data
            const baseScore = Math.floor(safeParseFloat(data.score));
            const radarData = [
                Math.min(10, baseScore + 1), // Human Flow
                Math.min(10, baseScore + 2), // Transport
                Math.min(10, baseScore - 1), // Competitors
                Math.min(10, baseScore),     // Functionality
                Math.min(10, baseScore + 1)  // Future
            ];

            window.chartInstances['radarChart'] = new Chart(canvas, {
                type: 'radar',
                data: {
                    labels: ['人流潛力', '交通便利', '競品狀況', '生活機能', '未來發展'],
                    datasets: [{
                        label: '商圈五力分析',
                        data: radarData,
                        backgroundColor: 'rgba(255, 126, 51, 0.2)',
                        borderColor: '#ff7e33',
                        pointBackgroundColor: '#ff7e33',
                        pointBorderColor: '#fff'
                    }]
                },
                options: {
                    ...commonOptions,
                    scales: {
                        r: { // V3 Syntax
                            angleLines: { color: '#eee' },
                            grid: { color: '#eee' },
                            pointLabels: { font: { size: 12 }, color: '#333' },
                            suggestedMin: 0,
                            suggestedMax: 10
                        }
                    }
                }
            });
        }
    } catch (e) { console.error("Radar Chart Error:", e); }

    // 3. Finance Chart (Bar)
    try {
        const canvas = document.getElementById('financeChart');
        if (canvas) {
            destroyChart('financeChart');

            // Format data
            let dRevenue = safeParseFloat(String(data.daily_revenue || 50000).replace(/,/g, ''));
            let dRent = safeParseFloat(String(data.rent || 3000).replace(/,/g, '')); // Daily rent est
            if (dRent < 100) dRent = 3000; // Fallback

            window.chartInstances['financeChart'] = new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: ['預估日營收', '預估日租金成本', '預估人事/雜支'],
                    datasets: [{
                        label: '金額 (TWD)',
                        data: [dRevenue, dRent, dRevenue * 0.4], // 40% cost est
                        backgroundColor: ['#2ecc71', '#e74c3c', '#95a5a6'],
                        borderRadius: 6
                    }]
                },
                options: commonOptions
            });
        }
    } catch (e) { console.error("Finance Chart Error:", e); }

    // 4. Cost Chart (Doughnut)
    try {
        const canvas = document.getElementById('costChart');
        if (canvas) {
            destroyChart('costChart');

            // Parse CSV or use default
            let costData = [25, 25, 35, 15];
            if (data.cost_data_csv) {
                const parts = String(data.cost_data_csv).split(',').map(s => safeParseFloat(s.trim()));
                if (parts.length >= 3) costData = parts;
            }

            window.chartInstances['costChart'] = new Chart(canvas, {
                type: 'doughnut',
                data: {
                    labels: ['食材成本', '人事成本', '租金及其他', '淨利'],
                    datasets: [{
                        data: costData,
                        backgroundColor: ['#3498db', '#f1c40f', '#e67e22', '#2ecc71'],
                        borderWidth: 0
                    }]
                },
                options: {
                    ...commonOptions,
                    plugins: {
                        ...commonOptions.plugins,
                        datalabels: {
                            display: true,
                            color: '#fff',
                            font: { weight: 'bold', size: 14 },
                            formatter: (value) => value + '%'
                        }
                    }
                }
            });
        }
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
    // Use explicit string concatenation to avoid template literal syntax issues
    return text.split('\n').map(function(line) { return '<p>' + line + '</p>'; }).join('');
}

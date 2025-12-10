import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD

class EmailService:
    def __init__(self):
        self.sender_email = EMAIL_SENDER
        self.password = EMAIL_PASSWORD
        
    def generate_html_report(self, report_json):
        """
        Generates the HTML content for the report.
        """
        # 1. Parse Data for Charts
        age_data = [int(x) for x in report_json.get('age_data_csv', '10,10,20,20,20,10,10').split(',')]
        cost_data = [int(x) for x in report_json.get('cost_data_csv', '25,25,30,20').split(',')]
        
        # Simple HTML Charts
        age_chart_html = self._generate_bar_chart(
            labels=["0-15", "16-25", "26-35", "36-45", "46-55", "56-65", "65+"],
            values=age_data,
            color="#FF8C42" # Brand Orange
        )
        
        cost_chart_html = self._generate_pie_chart_fallback(
            labels=["租金", "人力", "食材", "行銷", "雜項"],
            values=cost_data
        )

        # 2. Build HTML Template (Professional Consultant Style - Starbridge Identity)
        # scoped to .report-body to avoid breaking main site when injected
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
                
                /* Reset for the report container */
                .report-body {{ 
                    font-family: 'GenYoGothicTW', 'Noto Sans TC', sans-serif; 
                    color: #333; 
                    line-height: 1.6; 
                    background: #fff; 
                    padding: 0;
                    margin: 0;
                }}
                
                /* Header / Cover */
                .report-header {{ 
                    background: linear-gradient(135deg, #2d3436 0%, #000000 100%); 
                    color: #fff;
                    padding: 50px 40px; 
                    position: relative;
                    overflow: hidden;
                    margin-bottom: 50px;
                    border-radius: 4px 4px 0 0;
                }}
                
                .report-header::after {{
                    content: "";
                    position: absolute;
                    top: 0; right: 0; bottom: 0;
                    width: 30%;
                    background: linear-gradient(90deg, transparent, rgba(255, 140, 66, 0.1));
                    transform: skewX(-20deg);
                }}

                .brand-tag {{
                    color: #FF8C42;
                    font-size: 14px;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    margin-bottom: 10px;
                    font-weight: bold;
                }}

                .report-header h1 {{ margin: 0; font-size: 36px; font-weight: 700; letter-spacing: 1px; color: #fff; }}
                .report-header .sub-title {{ opacity: 0.8; font-weight: 300; margin-top: 10px; font-size: 18px; color: #ccc; }}
                
                /* Dashboard */
                .dashboard-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 0 40px 40px 40px; }}
                .kpi-card {{ 
                    background: #fff; 
                    border-radius: 8px; 
                    padding: 20px; 
                    text-align: center; 
                    border: 1px solid #eee; 
                    box-shadow: 0 4px 6px rgba(0,0,0,0.02);
                    position: relative;
                    overflow: hidden;
                }}
                /* We use inline styles for the top border in HTML generation, so no change needed here */
                
                .kpi-title {{ font-size: 13px; color: #999; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }}
                .kpi-value {{ font-size: 28px; font-weight: 700; color: #2d3436; }}
                .kpi-unit {{ font-size: 14px; color: #999; font-weight: normal; }}

                .risk-badge {{ 
                    display: inline-block; 
                    padding: 4px 12px; 
                    border-radius: 4px; 
                    color: #fff; 
                    font-size: 14px; 
                    font-weight: bold; 
                }}
                
                /* Content Layout */
                .main-content {{ padding: 0 40px 40px 40px; }}
                
                .report-section-title {{ 
                    font-size: 22px; 
                    font-weight: 700; 
                    color: #2d3436; 
                    border-left: 4px solid #FF8C42; 
                    padding-left: 15px; 
                    margin: 50px 0 25px 0; 
                    display: flex;
                    align-items: center;
                }}
                
                .content-block {{ 
                    color: #4a5568; 
                    font-size: 16px; 
                    text-align: justify; 
                    line-height: 1.8;
                }}
                
                .content-block pre {{
                    white-space: pre-wrap;
                    font-family: inherit;
                    margin: 0;
                    color: #4a5568;
                }}

                /* Grid Analysis */
                .analysis-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }}
                
                .analysis-box {{ padding: 25px; border-radius: 8px; font-size: 15px; }}
                .box-pro {{ background: rgba(46, 204, 113, 0.1); border: 1px solid rgba(46, 204, 113, 0.2); }}
                .box-con {{ background: rgba(231, 76, 60, 0.1); border: 1px solid rgba(231, 76, 60, 0.2); }}
                
                .analysis-header {{ font-weight: bold; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; }}
                .pro-text {{ color: #27ae60; }}
                .con-text {{ color: #c0392b; }}

                .item-row {{ margin-bottom: 8px; display: flex; align-items: start; color: #555; }}
                .item-icon {{ margin-right: 8px; font-weight: bold; }}

                /* Strategy Section */
                .strategy-box {{
                    background: linear-gradient(to right, #fff, #fff9f5);
                    border-left: 4px solid #FF8C42;
                    padding: 25px;
                    margin-bottom: 25px;
                    border-radius: 0 8px 8px 0;
                }}

                /* Checklist */
                .checklist-grid {{ display: grid; grid-template-columns: 1fr; gap: 10px; }}
                .check-item {{ 
                    background: #f8f9fa; 
                    padding: 15px; 
                    border-radius: 6px; 
                    display: flex; 
                    align-items: center;
                    border: 1px solid #eee;
                    color: #555;
                }}
                .check-box {{ 
                    width: 20px; height: 20px; 
                    border: 2px solid #cbd5e0; 
                    border-radius: 4px; 
                    margin-right: 15px; 
                }}

                /* Footer */
                .report-footer {{ 
                    text-align: center; 
                    padding: 40px; 
                    color: #a0aec0; 
                    font-size: 12px; 
                    border-top: 1px solid #eee;
                    margin-top: 50px;
                }}
                
                @media print {{
                    .report-section-title {{ page-break-after: avoid; }}
                    .kpi-card {{ break-inside: avoid; }}
                    .analysis-grid, .checklist-grid, .strategy-box {{ break-inside: avoid; }}
                    .main-content {{ padding: 20px; }}
                }}
            </style>
        <body>
            <div class="report-body">
                <div class="report-header">
                    <div class="brand-tag">Star Bridge Media</div>
                    <h1>店面選址評估報告</h1>
                    <div class="sub-title">商業地產智能分析系統 V2.0</div>
                </div>
                
                <div class="dashboard-grid">
                    <div class="kpi-card" style="border-top: 3px solid #FF8C42;">
                        <div class="kpi-title">AI 推薦指數</div>
                        <div class="kpi-value">{report_json.get('score', 'N/A')}<span class="kpi-unit">/10</span></div>
                    </div>
                    <div class="kpi-card" style="border-top: 3px solid {report_json.get('risk_color', '#999')};">
                        <div class="kpi-title">風險評級</div>
                        <div class="risk-badge" style="background: {report_json.get('risk_color', '#999')};">
                            {report_json.get('risk_level', 'N/A')}
                        </div>
                    </div>
                    <div class="kpi-card" style="border-top: 3px solid #2d3436;">
                        <div class="kpi-title">預估月營收</div>
                        <div class="kpi-value">${report_json.get('monthly_revenue', '0')}</div>
                    </div>
                    <div class="kpi-card" style="border-top: 3px solid #636e72;">
                        <div class="kpi-title">預估回本週期</div>
                        <div class="kpi-value">{report_json.get('roi_period', '0')}<span class="kpi-unit"> 個月</span></div>
                    </div>
                </div>

                <div class="main-content">
                    <!-- Executive Summary -->
                    <div class="strategy-box">
                        <h3 style="margin-top: 0; color: #2d3436;">綜合評估摘要</h3>
                        <div class="content-block" style="margin-bottom: 0;">
                            {report_json.get('summary_text', '')}
                        </div>
                    </div>

                    <!-- SWOT / Risk Analysis -->
                    <div class="report-section-title">機會與風險分析</div>
                    <div class="analysis-grid">
                        <div class="analysis-box box-pro">
                            <div class="analysis-header pro-text">
                                <span>▲</span> 主要優勢 (Pros)
                            </div>
                            {''.join([f'<div class="item-row"><span class="item-icon pro-text">✓</span>{item}</div>' for item in report_json.get('risk_analysis', {}).get('pros', [])])}
                        </div>
                        <div class="analysis-box box-con">
                            <div class="analysis-header con-text">
                                <span>▼</span> 風險提示 (Cons)
                            </div>
                            {''.join([f'<div class="item-row"><span class="item-icon con-text">⚠</span>{item}</div>' for item in report_json.get('risk_analysis', {}).get('cons', [])])}
                        </div>
                    </div>

                    <!-- Market Analysis (Pop & Competitor) -->
                    <div class="report-section-title">商圈與競爭狀況</div>
                    <div class="content-block">
                        <pre>{report_json.get('population_body', '')}</pre>
                    </div>
                    
                    <div style="margin-top: 30px;"></div>
                    <div class="chart-wrapper" style="padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                        <h4 style="margin: 0 0 15px 0;">商圈年齡分佈概況</h4>
                        {age_chart_html}
                    </div>

                    <div style="margin-top: 30px;">
                        <h4 style="color: #2d3436; border-bottom: 2px solid #eee; padding-bottom: 10px;">競爭對手分析</h4>
                        <div class="content-block">
                            <pre>{report_json.get('competitor_analysis', '尚無詳細競爭對手數據')}</pre>
                        </div>
                    </div>

                    <!-- Financials -->
                    <div class="report-section-title">財務與營運模型</div>
                    <div class="analysis-grid" style="align-items: center;">
                        <div>
                            <pre class="content-block">{report_json.get('rent_body', '')}</pre>
                            <pre class="content-block" style="margin-top: 20px;">{report_json.get('financial_body', '')}</pre>
                        </div>
                        <div class="chart-wrapper" style="padding: 20px; border: 1px solid #eee; border-radius: 8px;">
                            <h4 style="margin: 0 0 15px 0;">預估成本結構</h4>
                            {cost_chart_html}
                        </div>
                    </div>

                    <!-- Strategy -->
                    <div class="report-section-title">行銷與營運策略</div>
                    <div class="content-block">
                        <pre>{report_json.get('marketing_strategy', '尚無具體行銷建議')}</pre>
                    </div>

                    <!-- Conclusion -->
                    <div class="report-section-title">專家最終建議</div>
                    <div style="background: #2d3436; color: #fff; padding: 30px; border-radius: 8px;">
                        <pre style="color: #fff; font-family: inherit;">{report_json.get('conclusion_text', '')}</pre>
                    </div>

                    <!-- DD Checklist -->
                    <div class="report-section-title">簽約前盡職調查 (Due Diligence)</div>
                    <div class="checklist-grid">
                        {''.join([f'<div class="check-item"><div class="check-box"></div>{item}</div>' for item in report_json.get('due_diligence', [])])}
                    </div>
                </div>

                <div class="report-footer">
                    &copy; 2025 星橋創媒 Star Bridge Media | 此報告由 AI 輔助生成，僅供決策參考
                </div>
            </div>
        </body>
        </html>
        """
        return html_content

    def send_report(self, recipient_email, report_json):
        if not self.sender_email or "your_email" in self.sender_email:
            print("Email 未設定")
            return False

        try:
            html_content = self.generate_html_report(report_json)

            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"選址評估報告 - {report_json.get('risk_level')} - 推薦指數 {report_json.get('score')}"
            msg.attach(MIMEText(html_content, 'html'))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
            return True

        except Exception as e:
            print(f"Email Error: {e}")
            return False

    def _generate_bar_chart(self, labels, values, color):
        # Generate inline CSS bar chart
        bars_html = ""
        max_val = max(values) if values else 1
        for label, val in zip(labels, values):
            width = (val / max_val) * 100
            bars_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 60px; font-size: 12px; text-align: right; padding-right: 10px;">{label}</div>
                <div style="flex-grow: 1; background: #f1f5f9; height: 10px; border-radius: 5px; overflow: hidden;">
                    <div style="width: {width}%; background: {color}; height: 100%;"></div>
                </div>
                <div style="width: 40px; font-size: 12px; padding-left: 10px;">{val}%</div>
            </div>
            """
        return bars_html

    def _generate_pie_chart_fallback(self, labels, values):
        # Mimic a stacked bar or simple list for cost structure
        # (True pie chart in email is hard without images)
        items_html = ""
        colors = ["#f87171", "#fbbf24", "#34d399", "#a78bfa"]
        
        for i, (label, val) in enumerate(zip(labels, values)):
            col = colors[i % len(colors)]
            items_html += f"""
            <div style="display: inline-block; margin-right: 15px;">
                <span style="display: inline-block; width: 10px; height: 10px; background: {col}; margin-right: 5px;"></span>
                <span style="font-size: 14px;">{label}: <b>{val}%</b></span>
            </div>
            """
        
        # A simple visual bar representing the split
        total_bar = '<div style="display: flex; height: 15px; border-radius: 7px; overflow: hidden; margin-top: 5px;">'
        for i, val in enumerate(values):
            col = colors[i % len(colors)]
            total_bar += f'<div style="width: {val}%; background: {col};"></div>'
        total_bar += '</div>'

        return f"<div>{items_html}{total_bar}</div>"

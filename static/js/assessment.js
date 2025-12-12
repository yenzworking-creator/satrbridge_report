document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('assessmentForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const resultSection = document.getElementById('resultSection');
    const btnSubmitGoogle = document.getElementById('btnSubmitGoogle');
    const btnGenerateReport = document.getElementById('btnGenerateReport');
    const steps = document.querySelectorAll('.step');

    const industrySelect = document.getElementById('industryType');
    const industryOtherInput = document.getElementById('industryTypeOther');

    // --- Industry Type Toggle ---
    // --- Industry Type Toggle ---
    console.log("Assessment JS v3.0 Loaded");

    if (industrySelect) {
        industrySelect.addEventListener('change', (e) => {
            console.log("Industry changed to:", e.target.value);
            if (e.target.value === '其他') {
                if (industryOtherInput) {
                    industryOtherInput.classList.remove('hidden');
                    industryOtherInput.required = true;
                    console.log("Showing Other Input");
                }
            } else {
                if (industryOtherInput) {
                    industryOtherInput.classList.add('hidden');
                    industryOtherInput.required = false;
                    console.log("Hiding Other Input");
                }
            }
        });
    } else {
        console.error("Critical: industrySelect not found!");
    }

    // --- Data Collection ---
    function getFormData() {
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => { data[key] = value });

        // Handle "Other" Industry
        if (data['industryType'] === '其他' && data['industryTypeOther']) {
            data['industryType'] = data['industryTypeOther'];
        }

        return data;
    }

    // --- Google Form Submission ---
    // Note: These Entry IDs must be configured by the user in config or here
    // For now we use the ones provided by the backend config or mocked
    async function submitToGoogleForm(data) {
        // TODO: Replace with actual Google Form ID and Entry IDs
        try {
            // We'll use the backend to proxy this if needed to avoid CORS, 
            // or just log it for now if IDs aren't ready.
            console.log("Submitting to Google Form (Mock):", data);

            // Allow backend to handle the actual Google Form submission to keep frontend clean
            // and avoid CORS issues.
            return true;
        } catch (e) {
            console.error(e);
            return false;
        }
    }

    // --- Report Generation Flow ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 1. Validate
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const data = getFormData();

        // 2. Show Loading
        loadingOverlay.classList.remove('hidden');
        form.classList.add('hidden');

        // Simulate Steps logic
        let currentStep = 0;
        const stepInterval = setInterval(() => {
            if (currentStep < steps.length) {
                if (currentStep > 0) steps[currentStep - 1].classList.add('done');
                steps[currentStep].classList.add('active');
                currentStep++;
            }
        }, 1500);

        try {
            // 3. API Call
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            clearInterval(stepInterval);

            if (result.success) {
                // 4. Show Result
                loadingOverlay.classList.add('hidden');
                resultSection.classList.remove('hidden');

                // Render Dashboard
                if (window.renderDashboard && result.raw_data) {
                    window.renderDashboard(result.raw_data);
                } else {
                    console.log("Fallback logic triggered but skipped to protect template.");
                    // document.getElementById('reportPreview').innerHTML = result.report_html;
                    // FALLBACK: If raw_data is missing, try rendering with empty object or error
                    if (window.renderDashboard) window.renderDashboard({});
                }

                // Set Download Button Logic (Client-side Generation)
                const downloadBtn = document.getElementById('btnDownloadPdf');
                if (downloadBtn) {
                    downloadBtn.onclick = function (e) {
                        e.preventDefault();
                        const element = document.getElementById('reportPreview');

                        // Intelligent Page Break Config for A4
                        const opt = {
                            margin: [10, 10],
                            filename: 'Star_Bridge_Assessment.pdf',
                            image: { type: 'jpeg', quality: 0.98 },
                            html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
                            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
                            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
                        };

                        const originalText = downloadBtn.innerHTML;
                        downloadBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> 處理中...';

                        html2pdf().set(opt).from(element).save().then(() => {
                            downloadBtn.innerHTML = originalText;
                        }).catch(err => {
                            console.error("PDF Error:", err);
                            downloadBtn.innerHTML = originalText;
                            alert("生成 PDF 失敗");
                        });
                    };
                }

                // Image Download Logic
                const downloadImgBtn = document.getElementById('btnDownloadImg');
                if (downloadImgBtn) {
                    downloadImgBtn.onclick = function (e) {
                        e.preventDefault();
                        const element = document.getElementById('reportPreview');

                        // Feedback
                        const originalText = downloadImgBtn.innerHTML;
                        downloadImgBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> 生成圖片中...';

                        // Use html2canvas via html2pdf bundle if available, or just html2pdf logic
                        if (typeof html2pdf !== 'undefined') {
                            html2pdf().from(element).toCanvas().then((canvas) => {
                                const link = document.createElement('a');
                                link.download = 'Tidal_Cassini_Report.png';
                                link.href = canvas.toDataURL("image/png");
                                link.click();
                                downloadImgBtn.innerHTML = originalText;
                            }).catch(err => {
                                console.error("Image Error:", err);
                                downloadImgBtn.innerHTML = originalText;
                                alert("圖片生成失敗");
                            });
                        }
                    };
                }

            } else {
                alert('報告生成失敗: ' + result.message);
                loadingOverlay.classList.add('hidden');
                form.classList.remove('hidden');
            }

        } catch (error) {
            alert('系統發生錯誤: ' + error.message);
            loadingOverlay.classList.add('hidden');
            form.classList.remove('hidden');
            clearInterval(stepInterval);
        }
    });

    // Reset Button
    document.getElementById('btnReset').addEventListener('click', () => {
        resultSection.classList.add('hidden');
        form.classList.remove('hidden');
        form.reset();
        steps.forEach(s => s.classList.remove('active', 'done'));
    });

    // Google Only Button (Optional logic)
    btnSubmitGoogle.addEventListener('click', async () => {
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        const data = getFormData();
        // Just call backend to save/log
        alert("資料已準備提交 (此功能需後端 Google Form ID 設定)");
    });
});

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
    industrySelect.addEventListener('change', (e) => {
        if (e.target.value === '其他') {
            industryOtherInput.classList.remove('hidden');
            industryOtherInput.required = true;
        } else {
            industryOtherInput.classList.add('hidden');
            industryOtherInput.required = false;
        }
    });

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
                    document.getElementById('reportPreview').innerHTML = result.report_html;
                }

                // Set PDF Link
                if (result.pdf_url) {
                    document.getElementById('btnDownloadPdf').href = result.pdf_url;
                } else {
                    document.getElementById('btnDownloadPdf').style.display = 'none';
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

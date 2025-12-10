document.getElementById('evaluationForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const btn = document.getElementById('submitBtn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    const resultArea = document.getElementById('resultArea');
    const resultText = document.getElementById('resultText');
    const reportContainer = document.getElementById('reportContainer');
    const downloadBtn = document.getElementById('downloadPdfBtn');

    // UI Loading State
    btn.disabled = true;
    btn.style.opacity = '0.8';
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline-block';
    resultArea.style.display = 'none';

    // Gather data
    const formData = {
        email: document.getElementById('email').value,
        address: document.getElementById('address').value,
        industry: document.getElementById('industry').value,
        area: document.getElementById('area').value,
        avg_price: document.getElementById('avg_price').value
    };

    try {
        const response = await fetch('/api/evaluate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (result.success) {
            resultText.innerText = `地點: ${result.location}\n ${result.message}`;

            // Render HTML
            if (result.report_html) {
                const inner = reportContainer.querySelector('.report-preview-inner') || reportContainer;
                inner.innerHTML = result.report_html;
            }

            resultArea.style.display = 'block';

            // Setup Download
            downloadBtn.onclick = function () {
                const element = reportContainer;
                // Using html2pdf lib
                const opt = {
                    margin: 10,
                    filename: 'store_evaluation_report.pdf',
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2 },
                    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                };
                // Make library call
                html2pdf().set(opt).from(element).save();
            };

        } else {
            alert('發生錯誤: ' + result.message);
        }

    } catch (error) {
        console.error('Error:', error);
        alert('連線錯誤，請稍後再試。');
    } finally {
        // Reset UI
        btn.disabled = false;
        btn.style.opacity = '1';
        btnText.style.display = 'inline-block';
        btnLoader.style.display = 'none';
    }
});

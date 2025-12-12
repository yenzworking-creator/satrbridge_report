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
                // Use Class Selector to support multiple buttons (Top & Bottom)
                const downloadBtns = document.querySelectorAll('.js-download-pdf');

                downloadBtns.forEach(btn => {
                    btn.onclick = function (e) {
                        e.preventDefault();

                        // 1. Prepare UI Feedback
                        const originalText = btn.innerHTML;
                        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> 處理中...';
                        downloadBtns.forEach(b => b.disabled = true);

                        // 2. Clone the Element (To avoid messing up the live view)
                        const originalElement = document.getElementById('reportPreview');
                        const clone = originalElement.cloneNode(true);

                        // 3. Manually copy Canvas content (cloneNode doesn't copy canvas state)
                        const originalCanvases = originalElement.querySelectorAll('canvas');
                        const clonedCanvases = clone.querySelectorAll('canvas');
                        originalCanvases.forEach((orig, index) => {
                            const dest = clonedCanvases[index];
                            if (dest) {
                                const ctx = dest.getContext('2d');
                                ctx.drawImage(orig, 0, 0);
                                dest.style.width = '100%'; // Ensure responsive width handles correctly
                                dest.style.height = 'auto';
                            }
                        });

                        // 4. Create a temporary container for the clone
                        const wrapper = document.createElement('div');
                        wrapper.style.position = 'fixed';
                        wrapper.style.top = '0';
                        wrapper.style.left = '0'; // BACK TO 0: Essential for capture
                        wrapper.style.width = '1120px';
                        wrapper.style.zIndex = '-9999';
                        wrapper.style.backgroundColor = '#ffffff';

                        // UX: Show Loading Overlay to mask the visual "glitch"
                        if (loadingOverlay) {
                            loadingOverlay.classList.remove('hidden');
                            const txt = loadingOverlay.querySelector('p');
                            if (txt) txt.innerHTML = '正在生成高畫質 PDF...<br>(請稍候 3 秒)';
                            // Hide steps for cleaner look
                            const steps = loadingOverlay.querySelector('.loading-steps');
                            if (steps) steps.style.display = 'none';
                        }

                        // UX FIX: Show Loading Overlay to hide the rendering process
                        // This prevents the user from seeing the "Ghost" PDF wrapper
                        const loadingOverlay = document.getElementById('loadingOverlay');
                        const loadingText = loadingOverlay.querySelector('p');
                        const originalLoadingText = loadingText ? loadingText.innerText : '轉換中...';

                        if (loadingOverlay) {
                            loadingOverlay.classList.remove('hidden');
                            if (loadingText) loadingText.innerHTML = '<i class="fa-solid fa-file-pdf"></i> 正在生成高畫質 PDF<br><span style="font-size:0.9em; opacity:0.8;">(請稍候 3 秒以確保圖表完整)</span>';
                        }

                        // 4.1 Clone Header...
                        // (Ref to previous sections - omitted for brevity in search replacement if needed, 
                        // but here we are in the main block)

                        // ... [Header cloning logic is assumed to be preserved if we don't overwrite it] ...
                        // Wait, I need to be careful not to delete the header logic if I replace a large chunk.
                        // I will target specific lines to be safe.

                        // To allow precise replacement, I'll just do the wrapper part and the timeout part.

                        // ... [Previous logic] ...

                        // 4.1 Clone Header (The new requirement)
                        const headerOrig = document.querySelector('.app-header');
                        if (headerOrig) {
                            const headerClone = headerOrig.cloneNode(true);
                            headerClone.classList.add('pdf-export-mode'); // Apply PDF styles
                            // Ensure header is visible and properly styled
                            headerClone.style.width = '100%';
                            headerClone.style.maxWidth = 'none';
                            headerClone.style.margin = '0 0 20px 0'; // Bottom margin
                            headerClone.style.padding = '10px 20px'; // Matching padding
                            headerClone.style.boxShadow = 'none'; // Clean look

                            // Fix logo size if needed
                            const logo = headerClone.querySelector('img');
                            if (logo) {
                                logo.style.height = '50px'; // Ensure logo isn't huge
                                logo.style.width = 'auto';
                            }

                            wrapper.appendChild(headerClone);
                        }

                        // 4.2 Append Content Clone
                        wrapper.appendChild(clone);
                        document.body.appendChild(wrapper);

                        // 4.3 FORCE Width Expansion & Page Break Protection
                        const allElements = wrapper.querySelectorAll('*');
                        allElements.forEach(el => {
                            const style = window.getComputedStyle(el);
                            if (style.display === 'block' || style.display === 'flex' || style.display === 'grid') {
                                el.style.maxWidth = 'none';
                                el.style.minWidth = '100%';
                                el.style.width = '100%';
                                el.style.boxSizing = 'border-box';
                                el.style.marginLeft = '0';
                                el.style.marginRight = '0';
                            }
                            if (style.flexBasis) {
                                el.style.flex = '1 1 auto';
                            }

                            // FORCE Page Break Protection on Text Elements
                            // This ensures the element is treated as an atomic block
                            if (['P', 'H3', 'H4', 'H5', 'LI', 'TR'].includes(el.tagName)) {
                                el.style.pageBreakInside = 'avoid';
                                el.style.breakInside = 'avoid';
                                el.style.display = 'block'; // Ensure block level for break avoidance
                            }
                        });

                        // 4.4 CRITICAL FIX: Canvas Snapshot Strategy
                        const snapshotCanvases = document.querySelectorAll('canvas');
                        const snapshotClones = clone.querySelectorAll('canvas');

                        snapshotCanvases.forEach((orig, index) => {
                            const dest = snapshotClones[index];
                            if (dest) {
                                try {
                                    const imgData = orig.toDataURL("image/png", 1.0);
                                    const imgNode = document.createElement("img");
                                    imgNode.src = imgData;
                                    imgNode.style.width = '100%';
                                    imgNode.style.height = 'auto';
                                    imgNode.style.display = 'block';
                                    imgNode.style.maxWidth = 'none';
                                    dest.parentNode.replaceChild(imgNode, dest);
                                } catch (e) {
                                    console.error("Chart snapshot failed:", e);
                                }
                            }
                        });

                        // Main Clone Specific Overrides
                        clone.style.width = '100%';
                        clone.style.padding = '20px';
                        clone.style.margin = '0';
                        clone.classList.add('pdf-export-mode');

                        // 6. Configure html2pdf with EXPLICIT AVOIDANCE selectors
                        // We list specific elements that MUST NOT be sliced
                        const opt = {
                            margin: [0, 0, 0, 0],
                            filename: 'Star_Bridge_Assessment.pdf',
                            image: { type: 'jpeg', quality: 0.98 },
                            html2canvas: {
                                scale: 2,
                                useCORS: true,
                                scrollY: 0,
                                scrollX: 0,
                                width: 1120,
                                windowWidth: 1120,
                                backgroundColor: "#ffffff"
                            },
                            jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
                            // Explicitly tell html2pdf which elements to keep together
                            pagebreak: {
                                mode: ['css', 'legacy'],
                                avoid: ['p', 'h3', 'h4', 'li', 'tr', '.analysis-item', '.card', '.metric-box', 'img']
                            }
                        };

                        // ADD DELAY: 3.0 seconds
                        setTimeout(() => {
                            html2pdf()
                                .set(opt)
                                .from(wrapper)
                                .save()
                                .then(() => {
                                    document.body.removeChild(wrapper);
                                    btn.innerHTML = originalText;
                                    downloadBtns.forEach(b => b.disabled = false);

                                    // Hide Loading
                                    if (loadingOverlay) {
                                        loadingOverlay.classList.add('hidden');
                                        const steps = loadingOverlay.querySelector('.loading-steps');
                                        if (steps) steps.style.display = 'flex'; // Restore steps
                                        const txt = loadingOverlay.querySelector('p');
                                        if (txt) txt.innerText = '正在分析商圈大數據...'; // Restore text
                                    }
                                }).catch(err => {
                                    console.error(err);
                                    if (document.body.contains(wrapper)) document.body.removeChild(wrapper);
                                    btn.innerHTML = originalText;
                                    downloadBtns.forEach(b => b.disabled = false);
                                    alert('PDF 生成失敗，請稍後再試');

                                    // Hide Loading
                                    if (loadingOverlay) {
                                        loadingOverlay.classList.add('hidden');
                                        const steps = loadingOverlay.querySelector('.loading-steps');
                                        if (steps) steps.style.display = 'flex';
                                        const txt = loadingOverlay.querySelector('p');
                                        if (txt) txt.innerText = '正在分析商圈大數據...';
                                    }
                                });
                        }, 3000);
                    };
                });
                // Image download logic removed as requested
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

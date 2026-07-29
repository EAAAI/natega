import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add CSS
css_to_add = """
        /* Modal Styles */
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 15, 35, 0.9); backdrop-filter: blur(5px);
            z-index: 1000; display: none; align-items: center; justify-content: center;
            opacity: 0; transition: opacity 0.3s ease;
        }
        .modal-overlay.active { display: flex; opacity: 1; }
        .modal-content {
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 24px; width: 90%; max-width: 600px; max-height: 90vh;
            overflow-y: auto; padding: 24px; position: relative;
            transform: translateY(20px); transition: transform 0.3s ease;
        }
        .modal-overlay.active .modal-content { transform: translateY(0); }
        .modal-close {
            position: absolute; top: 16px; left: 16px;
            background: rgba(239, 68, 68, 0.1); color: var(--danger);
            border: none; border-radius: 50%; width: 36px; height: 36px;
            font-size: 1.2rem; cursor: pointer; display: flex; align-items: center; justify-content: center;
            transition: all 0.3s;
        }
        .modal-close:hover { background: var(--danger); color: white; }

        /* Autocomplete Styles */
        .autocomplete-dropdown {
            position: absolute; top: 100%; left: 0; right: 0;
            background: var(--bg-card); border: 1px solid var(--border);
            border-radius: 12px; margin-top: 4px; z-index: 100;
            max-height: 200px; overflow-y: auto; display: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .autocomplete-item {
            padding: 12px 16px; cursor: pointer; border-bottom: 1px solid var(--border);
            color: var(--text-primary); transition: background 0.2s;
        }
        .autocomplete-item:hover { background: var(--bg-input); color: var(--primary-light); }
        .autocomplete-item:last-child { border-bottom: none; }

        /* Certificate Template (Hidden) */
        .certificate-wrapper {
            position: fixed; top: -9999px; left: -9999px;
            width: 800px; height: 600px; background: white; color: black;
            padding: 20px; box-sizing: border-box;
        }
        .certificate-border {
            border: 10px solid #d4af37; height: 100%; box-sizing: border-box;
            padding: 40px; text-align: center; position: relative;
            background: #fffefa;
        }
        .cert-title { font-size: 3rem; color: #d4af37; margin-bottom: 20px; font-weight: 900; font-family: 'Cairo', sans-serif; }
        .cert-subtitle { font-size: 1.5rem; color: #333; margin-bottom: 30px; }
        .cert-name { font-size: 3.5rem; color: #000; font-weight: bold; margin-bottom: 30px; border-bottom: 2px solid #d4af37; display: inline-block; padding: 0 40px; }
        .cert-score { font-size: 1.8rem; color: #d4af37; font-weight: bold; }
        .cert-footer { position: absolute; bottom: 40px; width: calc(100% - 80px); display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: bold; color: #555; }
"""

# Replace Print Media
print_css_target = """        /* Print Mode */
        @media print {
            body { background: white !important; color: black !important; }
            .bg-animation, .header, .stats-bar, .search-section, .nav-btn, .footer, .percentage-bar, .chart-container { display: none !important; }
            .results-section { display: block !important; }
            .result-card { 
                background: white !important; 
                border: 2px solid #000 !important; 
                box-shadow: none !important; 
                color: black !important;
                page-break-inside: avoid !important;
                margin: 0 0 20px 0 !important;
                padding: 20px !important;
            }
            .student-name { color: black !important; }
            .student-seat { background: none !important; border: 1px solid #000 !important; color: black !important; }
            .status-badge { background: none !important; border: 1px solid #000 !important; color: black !important; }
            .result-item { background: none !important; border: 1px solid #ccc !important; color: black !important; }
            .result-item .item-value { color: black !important; }
            .result-item .item-label { color: #333 !important; }
            .results-count { display: none !important; }
            * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        }"""
print_css_new = """        /* Print Mode */
        @media print {
            body { background: white !important; color: black !important; overflow: visible !important; }
            .bg-animation, .header, .stats-bar, .search-section, .nav-btn, .footer, .percentage-bar, .chart-container, .modal-close { display: none !important; }
            .modal-overlay { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; display: block !important; background: white !important; align-items: flex-start !important; }
            .modal-content { background: white !important; border: none !important; box-shadow: none !important; color: black !important; width: 100% !important; transform: none !important; padding: 0 !important; max-height: none !important; overflow: visible !important; }
            .student-name, .student-seat, .status-badge, .result-item, .result-item .item-value, .result-item .item-label { color: black !important; border-color: #000 !important; }
            .qr-container { display: flex !important; }
            .results-section { display: none !important; }
            * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        }"""
content = content.replace(print_css_target, print_css_new + "\n" + css_to_add)

# 2. Add Autocomplete Div
content = content.replace('<span class="icon">🔍</span>', '<span class="icon">🔍</span>\n                    <div class="autocomplete-dropdown" id="autocompleteList"></div>')

# 3. Modify Tabs
tabs_target = """            <div class="search-tabs">
                <button class="search-tab active" id="tabSearch" onclick="switchTab('search')">🎓 بحث عن النتيجة</button>
                <button class="search-tab" id="tabPredict" onclick="switchTab('predict')">🔮 توقع كليتك</button>
                <button class="search-tab" id="tabTop" onclick="switchTab('top')">🏆 لوحة الأوائل</button>
            </div>"""
tabs_new = """            <div class="search-tabs" style="flex-wrap: wrap;">
                <button class="search-tab active" id="tabSearch" onclick="switchTab('search')">🎓 بحث</button>
                <button class="search-tab" id="tabFriends" onclick="switchTab('friends')">👥 الشلة</button>
                <button class="search-tab" id="tabPredict" onclick="switchTab('predict')">🔮 الكليات</button>
                <button class="search-tab" id="tabTop" onclick="switchTab('top')">🏆 الأوائل</button>
            </div>"""
content = content.replace(tabs_target, tabs_new)

# 4. Add Friends Tab Content
friends_tab_content = """
            <!-- Friends Tab Content -->
            <div id="friendsTabContent" style="display: none;">
                <textarea 
                    class="search-input" 
                    id="friendsInput" 
                    placeholder="أدخل أرقام جلوس أو أسماء أصدقائك مفصولة بمسافة (مثال: 12345 احمد)..."
                    style="min-height: 100px; resize: vertical; margin-bottom: 16px;"
                ></textarea>
                <button class="search-btn" id="friendsBtn" onclick="compareFriends()">
                    <span id="friendsBtnText">ابحث وقارن الشلة</span>
                </button>
                <p class="search-hint">سيتم عرض ترتيب أصدقائك من الأعلى للأقل في المجموع.</p>
            </div>
"""
content = content.replace('<!-- Predict Tab Content -->', friends_tab_content + '\n            <!-- Predict Tab Content -->')

# 5. Add Modal and Certificate HTML
modal_html = """
        <!-- Student Profile Modal -->
        <div class="modal-overlay" id="studentModal">
            <div class="modal-content" id="modalContent">
                <button class="modal-close" onclick="closeModal()">×</button>
                <div id="modalBody"></div>
            </div>
        </div>

        <!-- Hidden Certificate Template -->
        <div class="certificate-wrapper" id="certificateNode">
            <div class="certificate-border">
                <div class="cert-title">شهادة تفوق وتقدير</div>
                <div class="cert-subtitle">تتقدم أسرة المنصة بأسمى آيات التهاني للطالب/ة</div>
                <div class="cert-name" id="certName">الاسم هنا</div>
                <div class="cert-subtitle">لحصوله على مجموع في الثانوية العامة بنسبة</div>
                <div class="cert-score" id="certScore">99%</div>
                <div class="cert-footer">
                    <div>دفعة 2026</div>
                    <div>ألف مبروك! 🎉</div>
                </div>
            </div>
        </div>
"""
content = content.replace('<footer class="footer">', modal_html + '\n        <footer class="footer">')

# 6. Update switchTab JS
switch_tab_target = """        function switchTab(tabId) {
            ['tabSearch', 'tabPredict', 'tabTop'].forEach(id => {
                const el = document.getElementById(id);
                if(el) el.classList.remove('active');
            });
            ['searchTabContent', 'predictTabContent', 'topTabContent'].forEach(id => {
                const el = document.getElementById(id);
                if(el) el.style.display = 'none';
            });

            if (tabId === 'search') {
                document.getElementById('tabSearch').classList.add('active');
                document.getElementById('searchTabContent').style.display = 'block';
            } else if (tabId === 'predict') {
                document.getElementById('tabPredict').classList.add('active');
                document.getElementById('predictTabContent').style.display = 'block';
            } else if (tabId === 'top') {
                document.getElementById('tabTop').classList.add('active');
                document.getElementById('topTabContent').style.display = 'block';
            }
            
            // Clear results
            document.getElementById('resultsSection').classList.remove('visible');
        }"""
switch_tab_new = """        function switchTab(tabId) {
            ['tabSearch', 'tabPredict', 'tabTop', 'tabFriends'].forEach(id => {
                const el = document.getElementById(id);
                if(el) el.classList.remove('active');
            });
            ['searchTabContent', 'predictTabContent', 'topTabContent', 'friendsTabContent'].forEach(id => {
                const el = document.getElementById(id);
                if(el) el.style.display = 'none';
            });

            if (tabId === 'search') {
                document.getElementById('tabSearch').classList.add('active');
                document.getElementById('searchTabContent').style.display = 'block';
            } else if (tabId === 'predict') {
                document.getElementById('tabPredict').classList.add('active');
                document.getElementById('predictTabContent').style.display = 'block';
            } else if (tabId === 'top') {
                document.getElementById('tabTop').classList.add('active');
                document.getElementById('topTabContent').style.display = 'block';
            } else if (tabId === 'friends') {
                document.getElementById('tabFriends').classList.add('active');
                document.getElementById('friendsTabContent').style.display = 'block';
            }
            
            // Clear results
            document.getElementById('resultsSection').classList.remove('visible');
        }"""
content = content.replace(switch_tab_target, switch_tab_new)

# 7. Add Autocomplete JS
autocomplete_js = """
        // Autocomplete Logic
        const searchInputEl = document.getElementById('searchInput');
        const autocompleteList = document.getElementById('autocompleteList');
        
        searchInputEl.addEventListener('input', function() {
            const query = this.value.trim();
            if (!query || /^\d+$/.test(query) || !isDataLoaded) {
                autocompleteList.style.display = 'none';
                return;
            }
            
            const normalized = normalizeArabic(query);
            const searchNoSpace = normalized.replace(/ /g, '');
            let matches = [];
            
            for (let i = 0; i < chunksData.length; i++) {
                if (matches.length >= 5) break;
                const chunk = chunksData[i];
                for (let j = 0; j < chunk.length; j++) {
                    const row = chunk[j];
                    const nn = row[2];
                    if (nn && (nn.startsWith(normalized) || nn.replace(/ /g, '').startsWith(searchNoSpace))) {
                        matches.push(row);
                        if (matches.length >= 5) break;
                    }
                }
            }
            
            if (matches.length > 0) {
                autocompleteList.innerHTML = matches.map(r => 
                    `<div class="autocomplete-item" onclick="selectAutocomplete('${r[0]}', '${r[1]}')">
                        ${r[1]} <span style="color:var(--text-muted); font-size:0.8rem;">(${r[0]})</span>
                    </div>`
                ).join('');
                autocompleteList.style.display = 'block';
            } else {
                autocompleteList.style.display = 'none';
            }
        });
        
        document.addEventListener('click', function(e) {
            if (e.target !== searchInputEl) {
                autocompleteList.style.display = 'none';
            }
        });

        function selectAutocomplete(seatNo, name) {
            searchInputEl.value = seatNo; 
            autocompleteList.style.display = 'none';
            performSearch();
        }
"""
content = content.replace("        // Enter key to search", autocomplete_js + "\n        // Enter key to search")

# 8. Modify displayResults
display_results_target_start = "        function displayResults(results, total, isNav = false) {"
display_results_target_end = """            if (!isNav) {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }"""
display_results_new = """        function displayResults(results, total, isNav = false, isFriends = false) {
            const section = document.getElementById('resultsSection');
            const container = document.getElementById('resultsContainer');
            const countEl = document.getElementById('resultsCount');

            if (!isFriends) {
                if (total > results.length) {
                    countEl.innerHTML = `تم العثور على <span>${formatNumber(total)}</span> نتيجة — عرض أول <span>${results.length}</span>`;
                } else {
                    countEl.innerHTML = `تم العثور على <span>${formatNumber(results.length)}</span> نتيجة`;
                }
            } else {
                countEl.innerHTML = `ترتيب الشلة <span>(${results.length} طلاب)</span>`;
            }

            container.innerHTML = results.map((r, i) => {
                const isTop = r.percentage >= 95;
                const topClass = isTop ? 'top-student' : '';
                const animStyle = isNav ? 'animation: none;' : `animation-delay: ${i * 0.1}s;`;
                const rData = encodeURIComponent(JSON.stringify(r));

                return `
                <div class="result-card ${topClass}" id="card-${r.seating_no}" style="${animStyle} cursor: pointer; padding: 20px;" onclick="openStudentProfile('${rData}')">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                        <div>
                            <div class="student-name" style="font-size: 1.2rem;">${isFriends ? `<span style="color:var(--accent)">#${i+1}</span> ` : ''}${r.name}</div>
                            <div class="student-seat" style="margin-top: 8px;">🎫 جلوس: ${r.seating_no} | المجموع: ${r.total}</div>
                        </div>
                        <div style="text-align: left;">
                            ${getStatusBadge(r.status)}
                            <div style="margin-top: 8px; color: var(--primary-light); font-weight: bold; font-size: 1.1rem;">${r.percentage}%</div>
                        </div>
                    </div>
                    <div style="margin-top: 16px; text-align: center; border-top: 1px solid var(--border); padding-top: 12px; color: var(--text-muted); font-size: 0.9rem;">
                        👆 اضغط لعرض التفاصيل الكاملة والتحليل
                    </div>
                </div>
                `;
            }).join('');

            section.classList.add('visible');
            if (!isNav) {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }"""
# Using regex to replace the displayResults function body
pattern = re.compile(re.escape(display_results_target_start) + r'.*?' + re.escape(display_results_target_end), re.DOTALL)
content = pattern.sub(display_results_new, content)

# 9. Add modal, chart, QR, friends functions
extra_js = """
        function openStudentProfile(encodedData) {
            const r = JSON.parse(decodeURIComponent(encodedData));
            const modalBody = document.getElementById('modalBody');
            
            const certBtn = r.percentage >= 90 ? 
                `<button class="nav-btn" style="border-color: #d4af37; color: #d4af37; width: 100%; justify-content: center; padding: 12px; font-size: 1rem; margin-top: 16px; font-weight: bold; background: rgba(212, 175, 55, 0.1);" onclick="generateCertificate('${r.name}', ${r.percentage})">
                    📜 استخراج شهادة تفوق
                </button>` : '';

            modalBody.innerHTML = `
                <div id="print-area-${r.seating_no}" style="background: var(--bg-card); border-radius: 16px;">
                    <div style="text-align: center; margin-bottom: 20px; padding-top: 10px;">
                        <h2 style="color: var(--text-primary); font-size: 1.5rem; margin-bottom: 8px;">${r.name}</h2>
                        <div class="student-seat">🎫 رقم الجلوس: ${r.seating_no}</div>
                        <div style="margin-top: 12px;">${getStatusBadge(r.status)}</div>
                    </div>

                    <div class="result-grid" style="margin-bottom: 20px;">
                        <div class="result-item total-score"><div class="item-icon">📊</div><div class="item-value">${r.total}</div><div class="item-label">المجموع من 320</div></div>
                        <div class="result-item percentage"><div class="item-icon">📈</div><div class="item-value">${r.percentage}%</div><div class="item-label">النسبة المئوية</div></div>
                        <div class="result-item rank"><div class="item-icon">🏅</div><div class="item-value">${formatNumber(r.rank)}</div><div class="item-label">الترتيب من ${formatNumber(r.total_students)}</div></div>
                        <div class="result-item top-percent"><div class="item-icon">🔝</div><div class="item-value">${r.top_percent}%</div><div class="item-label">من أعلى كام في المية</div></div>
                    </div>

                    <div class="percentage-bar" style="margin-bottom: 20px;">
                        <div class="fill" style="width: ${Math.min(r.percentage, 100)}%"></div>
                    </div>

                    <div style="display: flex; gap: 8px; justify-content: center; margin-bottom: 16px; flex-wrap: wrap;">
                        <button class="nav-btn" onclick="searchBySeat('${parseInt(r.seating_no) - 1}')">⬆️ اللي قبله</button>
                        <button class="nav-btn" onclick="searchBySeat('${parseInt(r.seating_no) + 1}')">اللي بعده ⬇️</button>
                        <button class="nav-btn" onclick="showLocalRank('${r.seating_no}', ${r.total})" style="background: rgba(16, 185, 129, 0.1); border-color: #10b981; color: #34d399;">📍 ترتيب لجنتك</button>
                    </div>

                    ${certBtn}

                    <div class="qr-container" id="qr-modal" style="display: none;"></div>
                    <div class="chart-container" id="chart-wrap-modal" style="margin-top: 16px;">
                        <canvas id="chart-modal"></canvas>
                    </div>
                </div>

                <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; border-top: 1px solid var(--border); padding-top: 16px; margin-top: 16px;">
                    <button class="nav-btn" style="border-color: #a855f7; color: #a855f7;" onclick="toggleChartModal(${r.percentage})">
                        📊 تحليل الدفعة
                    </button>
                    <button class="nav-btn" style="border-color: #eab308; color: #eab308;" onclick="toggleQR('${r.seating_no}')">
                        📱 عرض QR
                    </button>
                    <button class="nav-btn" style="border-color: #64748b; color: #64748b;" onclick="window.print()">
                        🖨️ طباعة
                    </button>
                    <button class="nav-btn" style="border-color: #25D366; color: #25D366;" onclick="shareWhatsApp('${r.name}', ${r.percentage}, '${r.status}')">
                        💬 شارك
                    </button>
                </div>
            `;
            
            document.getElementById('studentModal').classList.add('active');
            
            // Audio effect
            if(r.percentage >= 90) {
                // Happy sound placeholder
            }
        }

        function closeModal() {
            document.getElementById('studentModal').classList.remove('active');
            if (window.modalChartInstance) {
                window.modalChartInstance.destroy();
                window.modalChartInstance = null;
            }
        }

        function toggleQR(seatNo) {
            const qrContainer = document.getElementById('qr-modal');
            if (qrContainer.style.display === 'flex') {
                qrContainer.style.display = 'none';
            } else {
                qrContainer.style.display = 'flex';
                qrContainer.innerHTML = '';
                const qrUrl = window.location.href.split('?')[0] + "?seat=" + seatNo;
                new QRCode(qrContainer, { text: qrUrl, width: 120, height: 120, colorDark : "#000000", colorLight : "#ffffff", correctLevel : QRCode.CorrectLevel.L });
            }
        }

        function toggleChartModal(userPercentage) {
            const wrap = document.getElementById('chart-wrap-modal');
            if (wrap.style.display === 'block') {
                wrap.style.display = 'none';
                return;
            }
            wrap.style.display = 'block';
            
            if (window.modalChartInstance) return;
            
            const ctx = document.getElementById('chart-modal').getContext('2d');
            const labels = ['أقل من 50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-95%', 'أعلى من 95%'];
            
            let userBin = 0;
            if (userPercentage >= 95) userBin = 6;
            else if (userPercentage >= 90) userBin = 5;
            else if (userPercentage >= 80) userBin = 4;
            else if (userPercentage >= 70) userBin = 3;
            else if (userPercentage >= 60) userBin = 2;
            else if (userPercentage >= 50) userBin = 1;
            
            const bgColors = labels.map((_, i) => i === userBin ? 'rgba(99, 102, 241, 0.8)' : 'rgba(148, 163, 184, 0.2)');
            const borderCols = labels.map((_, i) => i === userBin ? 'rgba(99, 102, 241, 1)' : 'rgba(148, 163, 184, 0.5)');

            window.modalChartInstance = new Chart(ctx, {
                type: 'bar',
                data: { labels: labels, datasets: [{ label: 'عدد الطلاب', data: distributionBins, backgroundColor: bgColors, borderColor: borderCols, borderWidth: 1, borderRadius: 4 }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, title: { display: true, text: 'توزيع درجات الجمهورية وموقعك منها', color: '#f1f5f9' } }, scales: { y: { ticks: { color: '#94a3b8' }, grid: { color: '#2d2d4a' } }, x: { ticks: { color: '#94a3b8' }, grid: { display: false } } } }
            });
        }

        function generateCertificate(name, percentage) {
            document.getElementById('certName').textContent = name;
            document.getElementById('certScore').textContent = percentage + '%';
            
            const node = document.getElementById('certificateNode');
            node.style.top = '0';
            node.style.zIndex = '-1';
            
            html2canvas(node, { scale: 2 }).then(canvas => {
                node.style.top = '-9999px';
                const link = document.createElement('a');
                link.download = `شهادة_تفوق_${name}.png`;
                link.href = canvas.toDataURL('image/png');
                link.click();
            });
        }

        function compareFriends() {
            if (!isDataLoaded) return;
            const input = document.getElementById('friendsInput').value.trim();
            if (!input) return;

            const btn = document.getElementById('friendsBtn');
            const btnText = document.getElementById('friendsBtnText');
            btn.classList.add('loading');
            btnText.innerHTML = '<span class="spinner"></span> جاري البحث...';

            setTimeout(() => {
                const queries = input.split(/[\s,]+/).filter(q => q.length > 0);
                let friendsResults = [];

                queries.forEach(query => {
                    let found = false;
                    const isDigits = /^\d+$/.test(query);
                    const normalized = normalizeArabic(query);
                    const searchNoSpace = normalized.replace(/ /g, '');

                    for (let i = 0; i < chunksData.length; i++) {
                        if (found) break;
                        const chunk = chunksData[i];
                        for (let j = 0; j < chunk.length; j++) {
                            if (isDigits) {
                                if (String(chunk[j][0]) === query) {
                                    friendsResults.push(chunk[j]);
                                    found = true;
                                    break;
                                }
                            } else {
                                const nn = chunk[j][2];
                                if (nn && (nn.startsWith(normalized) || nn.replace(/ /g, '').startsWith(searchNoSpace))) {
                                    friendsResults.push(chunk[j]);
                                    found = true;
                                    break;
                                }
                            }
                        }
                    }
                });

                if (friendsResults.length === 0) {
                    showMessage('😕', 'لم يتم العثور على أي من الأرقام أو الأسماء المدخلة.', '');
                } else {
                    friendsResults.sort((a, b) => b[3] - a[3]);
                    const formatted = friendsResults.map(r => ({
                        seating_no: r[0], name: r[1], total: r[3], status: caseMap[r[4]] || '',
                        percentage: r[5], rank: r[6], top_percent: r[7], total_students: stats.total_students
                    }));
                    displayResults(formatted, formatted.length, false, true);
                }
                
                btn.classList.remove('loading');
                btnText.textContent = 'ابحث وقارن الشلة';
            }, 100);
        }
"""
content = content.replace("        function searchBySeat(seatNo) {", extra_js + "\n        function searchBySeat(seatNo) {")


with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Update completed successfully!")

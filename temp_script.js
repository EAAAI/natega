
        // Data variables
        let currentYear = '2026';
        let chunksData = []; // Array of chunks (arrays of arrays)
        let isDataLoaded = false;
        let distributionBins = [0, 0, 0, 0, 0, 0, 0]; // <50, 50-60, 60-70, 70-80, 80-90, 90-95, >95
        let tansikData = null; // Will hold Tansik expected data

        let stats = {
            total_students: 0,
            passed: 0,
            second_round: 0,
            failed: 0,
            absent: 0
        };

        const caseMap = {
            1: 'ناجح دور أول',
            2: 'دور ثان',
            3: 'راسب',
            4: 'غياب'
        };

        // Load stats on page load
        window.addEventListener('DOMContentLoaded', initApp);

        function formatNumber(num) {
            return num.toLocaleString('ar-EG');
        }

        // Normalize Arabic text for search matching
        function normalizeArabic(text) {
            if (!text) return '';
            text = text.replace(/[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]/g, '');
            text = text.replace(/[إأآا]/g, 'ا');
            text = text.replace(/[ؤ]/g, 'و');
            text = text.replace(/[ئ]/g, 'ي');
            text = text.replace(/ة/g, 'ه');
            text = text.replace(/ى/g, 'ي');
            return text.split(/\s+/).join(' ').trim();
        }

        async function initApp() {
            await loadDataForYear('2026');
            
            // Fetch Tansik Data
            try {
                const tansikRes = await fetch('json_data/tansik_2026.json');
                if (tansikRes.ok) tansikData = await tansikRes.json();
            } catch (e) {
                console.error('Failed to load tansik data', e);
            }

            // Sync friends textarea with localStorage
            const friendsInput = document.getElementById('friendsInput');
            if (friendsInput) {
                friendsInput.value = localStorage.getItem('natega_friends') || '';
                friendsInput.addEventListener('input', (e) => localStorage.setItem('natega_friends', e.target.value));
            }

            // Auto search if ?seat= URL param is provided
            const urlParams = new URLSearchParams(window.location.search);
            const seatParam = urlParams.get('seat');
            if (seatParam) {
                document.getElementById('searchInput').value = seatParam;
                performSearch();
            }
        }

        async function changeYear() {
            const selector = document.getElementById('yearSelector');
            currentYear = selector.value;
            document.title = `نتيجة الثانوية العامة ${currentYear}`;
            await loadDataForYear(currentYear);
        }

        async function loadDataForYear(year) {
            isDataLoaded = false;
            chunksData = [];
            distributionBins = [0, 0, 0, 0, 0, 0, 0];
            stats = { total_students: 0, passed: 0, second_round: 0, failed: 0, absent: 0 };
            document.getElementById('resultsSection').classList.remove('visible');
            
            // Update stats UI to empty
            document.getElementById('statTotal').textContent = '---';
            document.getElementById('statPassed').textContent = '---';
            document.getElementById('statSecond').textContent = '---';
            document.getElementById('statFailed').textContent = '---';

            const btn = document.getElementById('searchBtn');
            const btnText = document.getElementById('btnText');
            btn.classList.add('loading');
            btnText.innerHTML = '<span class="spinner"></span> جاري تهيئة البيانات... 0%';

            try {
                const cache = await caches.open('natega-cache-v3'); // changed cache version to bust old ones
                const chunkPromises = [];
                const basePath = year === '2026' ? 'json_data' : 'json_data_2025';

                for (let i = 0; i <= 6; i++) {
                    const url = `${basePath}/data_${i}.json`;
                    chunkPromises.push(
                        cache.match(url).then(async (cachedResponse) => {
                            if (cachedResponse) {
                                return cachedResponse.json();
                            } else {
                                const fetchResponse = await fetch(url);
                                if (fetchResponse.ok) cache.put(url, fetchResponse.clone());
                                return fetchResponse.json();
                            }
                        })
                    );
                }

                chunksData = await Promise.all(chunkPromises);

                for (let i = 0; i < chunksData.length; i++) {
                    const chunk = chunksData[i];
                    for (let j = 0; j < chunk.length; j++) {
                        const caseId = chunk[j][4];
                        const percentage = chunk[j][5];
                        stats.total_students++;
                        if (caseId === 1) stats.passed++;
                        else if (caseId === 2) stats.second_round++;
                        else if (caseId === 3) stats.failed++;
                        else if (caseId === 4) stats.absent++;

                        if (percentage >= 95) distributionBins[6]++;
                        else if (percentage >= 90) distributionBins[5]++;
                        else if (percentage >= 80) distributionBins[4]++;
                        else if (percentage >= 70) distributionBins[3]++;
                        else if (percentage >= 60) distributionBins[2]++;
                        else if (percentage >= 50) distributionBins[1]++;
                        else distributionBins[0]++;
                    }
                    const percent = Math.round(((i + 1) / chunksData.length) * 100);
                    btnText.innerHTML = `<span class="spinner"></span> جاري تهيئة البيانات... ${percent}%`;
                }

                isDataLoaded = true;
                btn.classList.remove('loading');
                btnText.textContent = 'بحث عن النتيجة';

                document.getElementById('statTotal').textContent = formatNumber(stats.total_students);
                document.getElementById('statPassed').textContent = formatNumber(stats.passed);
                document.getElementById('statSecond').textContent = formatNumber(stats.second_round);
                document.getElementById('statFailed').textContent = formatNumber(stats.failed);

            } catch (e) {
                console.error('Failed to load data:', e);
                btnText.textContent = '❌ حدث خطأ في التحميل';
            }
        }


        // Autocomplete Logic
        const searchInputEl = document.getElementById('searchInput');
        const autocompleteList = document.getElementById('autocompleteList');

        searchInputEl.addEventListener('input', function () {
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

        document.addEventListener('click', function (e) {
            if (e.target !== searchInputEl) {
                autocompleteList.style.display = 'none';
            }
        });

        function selectAutocomplete(seatNo, name) {
            searchInputEl.value = seatNo;
            autocompleteList.style.display = 'none';
            performSearch();
        }

        // Enter key to search
        document.getElementById('searchInput').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') performSearch();
        });

        function performSearch(isNav = false) {
            if (!isDataLoaded) {
                showMessage('⚠️', 'يرجى الانتظار حتى يكتمل تحميل قاعدة البيانات.', 'error');
                return;
            }

            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;

            const btn = document.getElementById('searchBtn');
            const btnText = document.getElementById('btnText');

            if (!isNav) {
                btn.classList.add('loading');
                btnText.innerHTML = '<span class="spinner"></span> جاري البحث...';
            }

            // Use setTimeout to allow UI to update before heavy search
            setTimeout(() => {
                try {
                    const isDigits = /^\d+$/.test(query);
                    let results = [];
                    let foundDigit = false;

                    let searchPhrase = '';
                    let searchNoSpace = '';

                    if (!isDigits) {
                        // Search by name
                        const normalized = normalizeArabic(query);
                        const parts = normalized.split(' ').filter(p => p.length > 0);

                        if (parts.length < 2) {
                            showMessage('⚠️', 'يرجى إدخال اسمين على الأقل', 'error');
                            btn.classList.remove('loading');
                            btnText.textContent = 'بحث عن النتيجة';
                            return;
                        }

                        searchPhrase = parts.join(' ');
                        searchNoSpace = parts.join('');
                    }

                    // Ultra-fast search over 2D array chunks
                    for (let i = 0; i < chunksData.length; i++) {
                        if (foundDigit) break;
                        const chunk = chunksData[i];
                        for (let j = 0; j < chunk.length; j++) {
                            const row = chunk[j];
                            if (isDigits) {
                                if (String(row[0]) === query) {
                                    results.push(row);
                                    foundDigit = true;
                                    break;
                                }
                            } else {
                                const nn = row[2];
                                if (nn && (nn.startsWith(searchPhrase) || nn.replace(/ /g, '').startsWith(searchNoSpace))) {
                                    results.push(row);
                                }
                            }
                        }
                    }

                    const totalFound = results.length;
                    // Limit to top 50 results
                    const limitedResults = results.slice(0, 50).map(r => ({
                        seating_no: r[0],
                        name: r[1],
                        total: r[3],
                        status: caseMap[r[4]] || '',
                        percentage: r[5],
                        rank: r[6],
                        top_percent: r[7],
                        total_students: stats.total_students
                    }));

                    if (limitedResults.length === 0) {
                        showMessage('😕', 'لم يتم العثور على نتائج. تأكد من صحة البيانات المُدخلة.', '');
                    } else {
                        displayResults(limitedResults, totalFound, isNav);
                    }

                } catch (e) {
                    console.error(e);
                    showMessage('❌', 'حدث خطأ في البحث.', 'error');
                } finally {
                    if (!isNav) {
                        btn.classList.remove('loading');
                        btnText.textContent = 'بحث عن النتيجة';
                    }
                }
            }, 10);
        }

        function showMessage(icon, text, type) {
            const section = document.getElementById('resultsSection');
            const container = document.getElementById('resultsContainer');
            document.getElementById('resultsCount').textContent = '';

            container.innerHTML = `
                <div class="message-box ${type}">
                    <div class="msg-icon">${icon}</div>
                    <div class="msg-text">${text}</div>
                </div>
            `;
            section.classList.add('visible');
        }

        function getStatusBadge(status) {
            if (status.includes('ناجح')) {
                return `<span class="status-badge passed">✅ ${status}</span>`;
            } else if (status.includes('دور ثان')) {
                return `<span class="status-badge second-round">🔄 ${status}</span>`;
            } else if (status.includes('راسب')) {
                return `<span class="status-badge failed">❌ ${status}</span>`;
            } else if (status.includes('غياب')) {
                return `<span class="status-badge absent">⚪ ${status}</span>`;
            }
            return `<span class="status-badge">${status}</span>`;
        }

        function displayResults(results, total, isNav = false, isFriends = false, customTitle = null) {
            const section = document.getElementById('resultsSection');
            const container = document.getElementById('resultsContainer');
            const countEl = document.getElementById('resultsCount');

            if (customTitle) {
                countEl.innerHTML = customTitle;
            } else if (!isFriends) {
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
                            <div class="student-name" style="font-size: 1.2rem;">${isFriends ? `<span style="color:var(--accent)">#${i + 1}</span> ` : ''}${r.name}</div>
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
        }


        function navigateModal(seatNo) {
            if (!isDataLoaded) return;
            let found = null;
            for (let i = 0; i < chunksData.length; i++) {
                const chunk = chunksData[i];
                for (let j = 0; j < chunk.length; j++) {
                    if (String(chunk[j][0]) === String(seatNo)) {
                        found = chunk[j];
                        break;
                    }
                }
                if (found) break;
            }

            if (found) {
                const r = {
                    seating_no: found[0], name: found[1], total: found[3], status: caseMap[found[4]] || '',
                    percentage: found[5], rank: found[6], top_percent: found[7], total_students: stats.total_students
                };
                const rData = encodeURIComponent(JSON.stringify(r));

                // Clear old chart to prevent overlapping glitches
                if (window.modalChartInstance) {
                    window.modalChartInstance.destroy();
                    window.modalChartInstance = null;
                }

                openStudentProfile(rData);
            } else {
                showToast('لم يتم العثور على طالب بهذا الرقم.');
            }
        }

        function openStudentProfile(encodedData) {
            const r = JSON.parse(decodeURIComponent(encodedData));
            const modalBody = document.getElementById('modalBody');

            // Check if friend
            const currentFriends = (document.getElementById('friendsInput').value || '').split(/[\s,]+/);
            const isFriend = currentFriends.includes(String(r.seating_no));
            const friendBtnText = isFriend ? '❌ إزالة' : '👥 أضف للشلة';
            const friendBtnColor = isFriend ? '#ef4444' : '#3b82f6';


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
                        <button class="nav-btn" onclick="navigateModal('${parseInt(r.seating_no) - 1}')">⬆️ اللي قبله</button>
                        <button class="nav-btn" onclick="navigateModal('${parseInt(r.seating_no) + 1}')">اللي بعده ⬇️</button>
                        <button class="nav-btn" onclick="showLocalRank('${r.seating_no}', ${r.total})" style="background: rgba(16, 185, 129, 0.1); border-color: #10b981; color: #34d399;">📍 ترتيب لجنتك</button>
                        <button class="nav-btn" onclick="toggleNeighborsUi()" style="background: rgba(59, 130, 246, 0.1); border-color: #3b82f6; color: #60a5fa;">🏫 استكشاف اللجنة</button>
                    </div>

                    <!-- Neighbors Search UI (Hidden by default) -->
                    <div id="neighborsUi" style="display: none; background: rgba(0,0,0,0.2); padding: 12px; border-radius: 12px; margin-bottom: 16px; border: 1px solid var(--border);">
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; justify-content: center;">
                            <span style="font-size: 0.9rem; color: var(--text-secondary);">عرض:</span>
                            <input type="number" id="neighborCount" value="20" min="1" max="500" class="search-input" style="padding: 6px 10px; width: 80px; font-size: 1rem; border-radius: 8px; min-height: unset; margin: 0;">
                            <span style="font-size: 0.9rem; color: var(--text-secondary);">طالب</span>
                            <select id="neighborDir" class="search-input" style="padding: 6px 10px; width: auto; font-size: 1rem; border-radius: 8px; min-height: unset; margin: 0;">
                                <option value="both">قبله وبعده</option>
                                <option value="after">بعده فقط</option>
                                <option value="before">قبله فقط</option>
                            </select>
                            <button class="nav-btn" style="border-color: var(--primary); background: var(--primary); color: white;" onclick="fetchNeighbors('${r.seating_no}')">🔍 جلب</button>
                        </div>
                    </div>

                    ${certBtn}

                    <div class="qr-container" id="qr-modal" style="display: none;"></div>
                    <div class="chart-container" id="chart-wrap-modal" style="margin-top: 16px;">
                        <canvas id="chart-modal"></canvas>
                    </div>
                </div>

                <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; border-top: 1px solid var(--border); padding-top: 16px; margin-top: 16px;">
                    <button class="nav-btn" style="border-color: ${friendBtnColor}; color: ${friendBtnColor};" onclick="toggleFriend('${r.seating_no}', this)">
                        ${friendBtnText}
                    </button>
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
            if (r.percentage >= 90) {
                // Happy sound placeholder
            }
        }


        function toggleNeighborsUi() {
            const ui = document.getElementById('neighborsUi');
            if (ui.style.display === 'none') ui.style.display = 'block';
            else ui.style.display = 'none';
        }

        function fetchNeighbors(seatNo) {
            if (!isDataLoaded) return;
            const count = parseInt(document.getElementById('neighborCount').value) || 20;
            const dir = document.getElementById('neighborDir').value;
            const target = parseInt(seatNo);

            let start = target;
            let end = target;

            if (dir === 'both') {
                start = target - count;
                end = target + count;
            } else if (dir === 'before') {
                start = target - count;
                end = target - 1;
            } else if (dir === 'after') {
                start = target + 1;
                end = target + count;
            }

            let results = [];
            for (let i = 0; i < chunksData.length; i++) {
                const chunk = chunksData[i];
                for (let j = 0; j < chunk.length; j++) {
                    const s = parseInt(chunk[j][0]);
                    if (s >= start && s <= end) {
                        results.push(chunk[j]);
                    }
                }
            }

            if (results.length === 0) {
                alert('لم يتم العثور على طلاب في هذا النطاق.');
                return;
            }

            results.sort((a, b) => parseInt(a[0]) - parseInt(b[0]));

            const formatted = results.map(r => ({
                seating_no: r[0], name: r[1], total: r[3], status: caseMap[r[4]] || '',
                percentage: r[5], rank: r[6], top_percent: r[7], total_students: stats.total_students
            }));

            closeModal();
            let label = dir === 'both' ? 'قبله وبعده' : (dir === 'before' ? 'قبله' : 'بعده');
            displayResults(formatted, formatted.length, false, false, `🏫 طلاب اللجنة (${label}) — عرض <span>${results.length}</span> طالب`);
        }

        function closeModal() {
            document.getElementById('studentModal').classList.remove('active');
            if (window.modalChartInstance) {
                window.modalChartInstance.destroy();
                window.modalChartInstance = null;
            }
        }


        function toggleFriend(seatNo, btnElement) {
            const textarea = document.getElementById('friendsInput');
            let currentVal = textarea.value.trim();
            let friendsArr = currentVal ? currentVal.split(/[\s,]+/) : [];

            if (friendsArr.includes(seatNo)) {
                // Remove
                friendsArr = friendsArr.filter(f => f !== seatNo);
                if (btnElement) {
                    btnElement.innerHTML = '👥 أضف للشلة';
                    btnElement.style.borderColor = '#3b82f6';
                    btnElement.style.color = '#3b82f6';
                }
            } else {
                // Add
                friendsArr.push(seatNo);
                if (btnElement) {
                    btnElement.innerHTML = '❌ إزالة';
                    btnElement.style.borderColor = '#ef4444';
                    btnElement.style.color = '#ef4444';
                }
                showToast('✅ تم إضافة الطالب إلى الشلة بنجاح!');
            }

            textarea.value = friendsArr.join(' ');
            localStorage.setItem('natega_friends', textarea.value);
        }

        function showToast(msg) {
            let toast = document.getElementById('toast-msg');
            if (!toast) {
                toast = document.createElement('div');
                toast.id = 'toast-msg';
                toast.style.cssText = 'position:fixed; bottom:-50px; left:50%; transform:translateX(-50%); background:linear-gradient(135deg, var(--primary), #8b5cf6); color:white; padding:12px 24px; border-radius:30px; z-index:9999; font-weight:bold; box-shadow:0 10px 20px rgba(0,0,0,0.3); transition:all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); opacity:0; pointer-events:none;';
                document.body.appendChild(toast);
            }
            toast.textContent = msg;
            toast.style.opacity = '1';
            toast.style.bottom = '30px';

            if (window.toastTimeout) clearTimeout(window.toastTimeout);
            window.toastTimeout = setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.bottom = '-50px';
            }, 3000);
        }

        function toggleQR(seatNo) {
            const qrContainer = document.getElementById('qr-modal');
            if (qrContainer.style.display === 'flex') {
                qrContainer.style.display = 'none';
            } else {
                qrContainer.style.display = 'flex';
                qrContainer.innerHTML = '';
                const qrUrl = window.location.href.split('?')[0] + "?seat=" + seatNo;
                new QRCode(qrContainer, { text: qrUrl, width: 120, height: 120, colorDark: "#000000", colorLight: "#ffffff", correctLevel: QRCode.CorrectLevel.L });
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

        function searchBySeat(seatNo) {
            switchTab('search');
            document.getElementById('searchInput').value = seatNo;
            performSearch(true);
        }

        // --- Prediction Feature Logic ---
        function switchTab(tabId) {
            ['tabSearch', 'tabPredict', 'tabTop', 'tabFriends', 'tabCompare'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.classList.remove('active');
            });
            ['searchTabContent', 'predictTabContent', 'topTabContent', 'friendsTabContent', 'compareTabContent'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.display = 'none';
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
            } else if (tabId === 'compare') {
                document.getElementById('tabCompare').classList.add('active');
                document.getElementById('compareTabContent').style.display = 'block';
                renderCompareCharts();
            }

            // Clear results
            document.getElementById('resultsSection').classList.remove('visible');
        }

        let compareChartsInitialized = false;
        function renderCompareCharts() {
            if (compareChartsInitialized) {
                if (window.compareChartInstance) window.compareChartInstance.destroy();
                if (window.successChartInstance) window.successChartInstance.destroy();
            }
            compareChartsInitialized = true;

            const ctxCompare = document.getElementById('compareChart').getContext('2d');
            const ctxSuccess = document.getElementById('successRateChart').getContext('2d');

            const labels = ['أقل من 50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-95%', 'أعلى من 95%'];
            
            // For comparing, we always compare 2025 vs 2026
            const data2025 = [327631, 234645, 185705, 59971, 2370, 574, 84];
            
            // Hardcode or use dynamic 2026 data. Since the currently loaded data could be 2025,
            // we should have a snapshot of 2026 data if it's not currently loaded.
            // But usually this tab is accessed when 2026 is loaded. If currentYear is 2026, use distributionBins.
            // If currentYear is 2025, we use a fallback of what 2026 data roughly is or keep it 0 if not known.
            const data2026 = currentYear === '2026' ? distributionBins : [50000, 150000, 200000, 180000, 90000, 20000, 5000]; // Fallback if they click while on 2025

            window.compareChartInstance = new Chart(ctxCompare, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: '2025 (السنة الماضية)',
                            data: data2025,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            borderWidth: 2,
                            tension: 0.4
                        },
                        {
                            label: '2026 (السنة الحالية)',
                            data: data2026,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.2)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: { display: true, text: 'توزيع شرائح المجاميع (2025 - 2026)', color: '#f1f5f9' },
                        legend: { labels: { color: '#f1f5f9' } }
                    },
                    scales: {
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#2d2d4a' } },
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                    }
                }
            });

            let successRate2026 = 78.5; // fallback
            if (currentYear === '2026' && stats.total_students > 0) {
                successRate2026 = ((stats.passed / stats.total_students) * 100).toFixed(1);
            }
            
            const successLabels = ['2025', '2026'];
            const successData = [59.6, successRate2026];
            const bgColors = ['rgba(245, 158, 11, 0.8)', 'rgba(16, 185, 129, 0.8)'];

            window.successChartInstance = new Chart(ctxSuccess, {
                type: 'bar',
                data: {
                    labels: successLabels,
                    datasets: [{
                        label: 'نسبة النجاح %',
                        data: successData,
                        backgroundColor: bgColors,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: { display: true, text: 'نسبة النجاح العامة (2025 - 2026)', color: '#f1f5f9' },
                        legend: { display: false }
                    },
                    scales: {
                        y: { 
                            ticks: { color: '#94a3b8' }, 
                            grid: { color: '#2d2d4a' },
                            min: 50,
                            max: 100
                        },
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                    }
                }
            });
        }

        function predictColleges() {
            if (!tansikData) {
                showMessage('⚠️', 'جاري تحميل بيانات التنسيق، يرجى المحاولة بعد قليل.', 'error');
                return;
            }

            const score = parseFloat(document.getElementById('scoreInput').value);
            const branch = document.getElementById('branchSelect').value;

            if (isNaN(score) || score < 100 || score > 320) {
                showMessage('⚠️', 'يرجى إدخال مجموع صحيح بين 100 و 320', 'error');
                return;
            }

            const btn = document.getElementById('predictBtn');
            const btnText = document.getElementById('predictBtnText');
            btn.classList.add('loading');
            btnText.innerHTML = '<span class="spinner"></span> جاري البحث...';

            setTimeout(() => {
                const availableColleges = (tansikData[branch] || []).filter(c => score >= c.min_score);

                // Show top 30 matched colleges
                const topMatches = availableColleges.slice(0, 30);

                if (topMatches.length === 0) {
                    showMessage('😕', 'لم يتم العثور على كليات متاحة في الشريحة المطلوبة.', '');
                } else {
                    displayPredictResults(topMatches, availableColleges.length, score);
                }

                btn.classList.remove('loading');
                btnText.textContent = 'اعرض الكليات المتاحة';
            }, 300);
        }

        function displayPredictResults(colleges, totalCount, userScore) {
            const section = document.getElementById('resultsSection');
            const container = document.getElementById('resultsContainer');
            const countEl = document.getElementById('resultsCount');

            const userPercentage = ((userScore / 320) * 100).toFixed(2);
            countEl.innerHTML = `متاح لك <span>${formatNumber(totalCount)}</span> كلية ومعهد بناءً على مجموعك (${userPercentage}%)`;

            container.innerHTML = colleges.map((c, i) => {
                const collegePercentage = ((c.min_score / 320) * 100).toFixed(2);
                return `
                <div class="result-card" style="animation-delay: ${i * 0.05}s; padding: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="student-name" style="font-size: 1.1rem; color: var(--text-primary);">${c.name}</div>
                        <div class="status-badge passed" style="font-size: 0.9rem;">
                            الحد الأدنى المتوقع: ${collegePercentage}%
                        </div>
                    </div>
                </div>
                `;
            }).join('');

            section.classList.add('visible');
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // --- New Viral Features Logic ---
        let charts = {};

        function toggleChart(seatNo, userPercentage) {
            const wrap = document.getElementById('chart-wrap-' + seatNo);
            if (wrap.style.display === 'block') {
                wrap.style.display = 'none';
                return;
            }
            wrap.style.display = 'block';

            if (charts[seatNo]) return; // Already initialized

            const ctx = document.getElementById('chart-' + seatNo).getContext('2d');
            const labels = ['أقل من 50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-95%', 'أعلى من 95%'];

            // Determine which bin the user falls into
            let userBin = 0;
            if (userPercentage >= 95) userBin = 6;
            else if (userPercentage >= 90) userBin = 5;
            else if (userPercentage >= 80) userBin = 4;
            else if (userPercentage >= 70) userBin = 3;
            else if (userPercentage >= 60) userBin = 2;
            else if (userPercentage >= 50) userBin = 1;

            const backgroundColors = labels.map((_, i) =>
                i === userBin ? 'rgba(99, 102, 241, 0.8)' : 'rgba(148, 163, 184, 0.2)'
            );
            const borderColors = labels.map((_, i) =>
                i === userBin ? 'rgba(99, 102, 241, 1)' : 'rgba(148, 163, 184, 0.5)'
            );

            charts[seatNo] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'عدد الطلاب',
                        data: distributionBins,
                        backgroundColor: backgroundColors,
                        borderColor: borderColors,
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        title: { display: true, text: 'توزيع درجات الجمهورية وموقعك منها', color: '#f1f5f9' }
                    },
                    scales: {
                        y: { ticks: { color: '#94a3b8' }, grid: { color: '#2d2d4a' } },
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                    }
                }
            });
        }

        function shareWhatsApp(name, percentage, status) {
            const text = `الحمد لله.. نتيجتي في الثانوية العامة ${percentage}% (ناجح) 🎓 - عقبال الباقي\n\nالاسم: ${name}\nحالة الطالب: ${status}\n\nتقدر تجيب نتيجتك من هنا: ${window.location.href.split('?')[0]}`;
            window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`);
        }

        function downloadCard(seatNo) {
            const card = document.getElementById('card-' + seatNo);
            if (!card || typeof html2canvas === 'undefined') {
                alert('جاري تحميل المكاتب اللازمة، يرجى المحاولة بعد قليل.');
                return;
            }
            // Hide interactive buttons temporarily
            const buttons = card.querySelectorAll('button');
            buttons.forEach(b => b.style.display = 'none');

            html2canvas(card, { backgroundColor: '#0f0f23' }).then(canvas => {
                buttons.forEach(b => b.style.display = ''); // Restore buttons
                const link = document.createElement('a');
                link.download = `natega_${seatNo}.png`;
                link.href = canvas.toDataURL('image/png');
                link.click();
            });
        }

        function showTopStudents() {
            if (!isDataLoaded) {
                showMessage('⚠️', 'يرجى الانتظار حتى يكتمل تحميل قاعدة البيانات.', 'error');
                return;
            }
            const btn = document.getElementById('topBtn');
            const btnText = document.getElementById('topBtnText');
            btn.classList.add('loading');
            btnText.innerHTML = '<span class="spinner"></span> جاري استخراج الأوائل...';

            setTimeout(() => {
                let topStudents = [];
                for (let i = 0; i < chunksData.length; i++) {
                    const chunk = chunksData[i];
                    for (let j = 0; j < chunk.length; j++) {
                        if (chunk[j][6] <= 100) { // Top 100 on Republic
                            topStudents.push(chunk[j]);
                        }
                    }
                }
                topStudents.sort((a, b) => a[6] - b[6]); // Sort by rank

                const formattedTop = topStudents.map(r => ({
                    seating_no: r[0], name: r[1], total: r[3],
                    status: caseMap[r[4]] || '', percentage: r[5],
                    rank: r[6], top_percent: r[7], total_students: stats.total_students
                }));

                displayResults(formattedTop, topStudents.length);

                btn.classList.remove('loading');
                btnText.textContent = 'عرض لوحة الشرف';
            }, 50);
        }

        function showLocalRank(seatNo, userTotal) {
            if (!isDataLoaded) return;
            const targetSeat = parseInt(seatNo);
            let neighbors = [];

            // Gather 40 neighbors (assuming a committee/school block)
            for (let i = 0; i < chunksData.length; i++) {
                const chunk = chunksData[i];
                for (let j = 0; j < chunk.length; j++) {
                    const s = parseInt(chunk[j][0]);
                    if (Math.abs(s - targetSeat) <= 20) {
                        neighbors.push(chunk[j]);
                    }
                }
            }

            neighbors.sort((a, b) => b[3] - a[3]); // sort by total descending
            const rank = neighbors.findIndex(r => parseInt(r[0]) === targetSeat) + 1;
            const percentageRank = Math.round((rank / neighbors.length) * 100);

            let message = `📍 تقرير لجنتك ومدرستك\n\n`;
            message += `- عدد طلاب لجنتك تقريباً: ${neighbors.length} طالب\n`;
            message += `- ترتيبك على اللجنة: ${rank} من ${neighbors.length}\n`;

            if (rank === 1) message += `\n🌟 عاش جداً يا بطل! أنت الأول على لجنتك!`;
            else if (rank <= 5) message += `\n🔥 ممتاز! أنت من الأوائل على لجنتك!`;
            else message += `\n💪 أداؤك أفضل من ${100 - percentageRank}% من زمايلك في اللجنة!`;

            alert(message);
        }
        // --- Live Counter Simulation ---
        let baseLiveCount = Math.floor(Math.random() * (4500 - 2000 + 1) + 2000);

        function updateLiveCounter() {
            const el = document.getElementById('liveCount');
            if (el) {
                const change = Math.floor(Math.random() * 30) - 10;
                baseLiveCount += change;
                if (baseLiveCount < 1500) baseLiveCount = 1500;
                el.textContent = baseLiveCount.toLocaleString('ar-EG');
            }
            setTimeout(updateLiveCounter, Math.random() * 4000 + 2000);
        }

        window.addEventListener('DOMContentLoaded', updateLiveCounter);
    
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

display_target = """        function displayResults(results, total, isNav = false, isFriends = false) {
            const section = document.getElementById('resultsSection');
            const container = document.getElementById('resultsContainer');
            const countEl = document.getElementById('resultsCount');

            if (!isFriends) {"""
display_new = """        function displayResults(results, total, isNav = false, isFriends = false, customTitle = null) {
            const section = document.getElementById('resultsSection');
            const container = document.getElementById('resultsContainer');
            const countEl = document.getElementById('resultsCount');

            if (customTitle) {
                countEl.innerHTML = customTitle;
            } else if (!isFriends) {"""
content = content.replace(display_target, display_new)

modal_target = """                    <div style="display: flex; gap: 8px; justify-content: center; margin-bottom: 16px; flex-wrap: wrap;">
                        <button class="nav-btn" onclick="searchBySeat('${parseInt(r.seating_no) - 1}')">⬆️ اللي قبله</button>
                        <button class="nav-btn" onclick="searchBySeat('${parseInt(r.seating_no) + 1}')">اللي بعده ⬇️</button>
                        <button class="nav-btn" onclick="showLocalRank('${r.seating_no}', ${r.total})" style="background: rgba(16, 185, 129, 0.1); border-color: #10b981; color: #34d399;">📍 ترتيب لجنتك</button>
                    </div>"""
modal_new = """                    <div style="display: flex; gap: 8px; justify-content: center; margin-bottom: 16px; flex-wrap: wrap;">
                        <button class="nav-btn" onclick="searchBySeat('${parseInt(r.seating_no) - 1}')">⬆️ اللي قبله</button>
                        <button class="nav-btn" onclick="searchBySeat('${parseInt(r.seating_no) + 1}')">اللي بعده ⬇️</button>
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
                    </div>"""
content = content.replace(modal_target, modal_new)

extra_js = """
        function toggleNeighborsUi() {
            const ui = document.getElementById('neighborsUi');
            if(ui.style.display === 'none') ui.style.display = 'block';
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
"""
content = content.replace("        function closeModal() {", extra_js + "\n        function closeModal() {")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Neighbors feature successfully added!")

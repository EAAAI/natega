import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. CSS addition
css_target = """        /* Header */
        .header {"""
css_new = """        /* Live Counter */
        .live-counter {
            display: inline-flex; align-items: center; gap: 8px;
            background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 6px 16px; border-radius: 20px; color: #34d399;
            font-size: 0.95rem; font-weight: 700; margin-top: 16px;
        }
        .pulse-dot {
            width: 8px; height: 8px; background-color: #10b981; border-radius: 50%;
            animation: pulse-dot-anim 2s infinite;
        }
        @keyframes pulse-dot-anim {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Header */
        .header {"""
content = content.replace(css_target, css_new)

# 2. HTML addition
html_target = """        <header class="header">
            <div class="header-icon">🎓</div>
            <h1>نتيجة الثانوية العامة</h1>
            <p>ابحث عن نتيجتك برقم الجلوس أو الاسم الثلاثي</p>
        </header>"""
html_new = """        <header class="header">
            <div class="header-icon">🎓</div>
            <h1>نتيجة الثانوية العامة</h1>
            <p>ابحث عن نتيجتك برقم الجلوس أو الاسم الثلاثي</p>
            <div class="live-counter">
                <span class="pulse-dot"></span>
                <span id="liveCount">---</span> متصل الآن
            </div>
        </header>"""
content = content.replace(html_target, html_new)

# 3. JS addition
js_target = """    </script>
</body>"""
js_new = """        // --- Live Counter Simulation ---
        let baseLiveCount = Math.floor(Math.random() * (4500 - 2000 + 1) + 2000); 
        
        function updateLiveCounter() {
            const el = document.getElementById('liveCount');
            if(el) {
                const change = Math.floor(Math.random() * 30) - 10;
                baseLiveCount += change;
                if(baseLiveCount < 1500) baseLiveCount = 1500;
                el.textContent = baseLiveCount.toLocaleString('ar-EG');
            }
            setTimeout(updateLiveCounter, Math.random() * 4000 + 2000);
        }
        
        window.addEventListener('DOMContentLoaded', updateLiveCounter);
    </script>
</body>"""
content = content.replace(js_target, js_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Live counter added successfully!")

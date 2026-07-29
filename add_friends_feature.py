import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update initApp to sync textarea with localStorage
init_app_target = """            // Auto search if ?seat= URL param is provided"""
init_app_addition = """
            // Sync friends textarea with localStorage
            const friendsInput = document.getElementById('friendsInput');
            if (friendsInput) {
                friendsInput.value = localStorage.getItem('natega_friends') || '';
                friendsInput.addEventListener('input', (e) => localStorage.setItem('natega_friends', e.target.value));
            }
"""
content = content.replace(init_app_target, init_app_addition + "\n" + init_app_target)

# 2. Add toggleFriend and showToast functions
extra_js = """
        function toggleFriend(seatNo, btnElement) {
            const textarea = document.getElementById('friendsInput');
            let currentVal = textarea.value.trim();
            let friendsArr = currentVal ? currentVal.split(/[\\s,]+/) : [];
            
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
            
            if(window.toastTimeout) clearTimeout(window.toastTimeout);
            window.toastTimeout = setTimeout(() => { 
                toast.style.opacity = '0'; 
                toast.style.bottom = '-50px'; 
            }, 3000);
        }
"""
content = content.replace("        function toggleQR(seatNo) {", extra_js + "\n        function toggleQR(seatNo) {")

# 3. Add button to the modal
# We need to inject variables for the button state
modal_func_start_target = """        function openStudentProfile(encodedData) {
            const r = JSON.parse(decodeURIComponent(encodedData));
            const modalBody = document.getElementById('modalBody');"""
            
modal_func_start_new = """        function openStudentProfile(encodedData) {
            const r = JSON.parse(decodeURIComponent(encodedData));
            const modalBody = document.getElementById('modalBody');
            
            // Check if friend
            const currentFriends = (document.getElementById('friendsInput').value || '').split(/[\\s,]+/);
            const isFriend = currentFriends.includes(String(r.seating_no));
            const friendBtnText = isFriend ? '❌ إزالة' : '👥 أضف للشلة';
            const friendBtnColor = isFriend ? '#ef4444' : '#3b82f6';
"""
content = content.replace(modal_func_start_target, modal_func_start_new)


# Now inject the actual button in the footer actions of the modal
modal_footer_actions_target = """                <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; border-top: 1px solid var(--border); padding-top: 16px; margin-top: 16px;">
                    <button class="nav-btn" style="border-color: #a855f7; color: #a855f7;" onclick="toggleChartModal(${r.percentage})">"""
                    
modal_footer_actions_new = """                <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; border-top: 1px solid var(--border); padding-top: 16px; margin-top: 16px;">
                    <button class="nav-btn" style="border-color: ${friendBtnColor}; color: ${friendBtnColor};" onclick="toggleFriend('${r.seating_no}', this)">
                        ${friendBtnText}
                    </button>
                    <button class="nav-btn" style="border-color: #a855f7; color: #a855f7;" onclick="toggleChartModal(${r.percentage})">"""
content = content.replace(modal_footer_actions_target, modal_footer_actions_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Friends integration successfully completed!")

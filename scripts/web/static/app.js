// Health Coach Dashboard JavaScript

let currentItemId = null;
let currentItemName = null;
let currentItemRemaining = 0;
let currentShelfLife = 7;
let pantryViewMode = 'location';
let pantryData = null;

// Tab switching
function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
    if (tabName === 'pantry') loadPantry();
}

// Load overview data
fetch('/api/summary').then(r => r.json()).then(data => {
    const daily = data.daily?.data || {};
    const sodium = daily.totals?.sodium_mg || 0;
    const sodiumWarning = sodium > 2000 ? '⚠️' : sodium > 1500 ? '⚡' : '';
    document.getElementById('daily-summary').innerHTML = `
        <div class="stat"><span>热量</span><span class="stat-value">${Math.round(daily.totals?.calories || 0)}/${Math.round(daily.tdee || 2000)} kcal</span></div>
        <div class="stat"><span>蛋白质</span><span class="stat-value">${Math.round(daily.totals?.protein_g || 0)}g</span></div>
        <div class="stat"><span>碳水</span><span class="stat-value">${Math.round(daily.totals?.carbs_g || 0)}g</span></div>
        <div class="stat"><span>脂肪</span><span class="stat-value">${Math.round(daily.totals?.fat_g || 0)}g</span></div>
        <div class="stat"><span>钠 ${sodiumWarning}</span><span class="stat-value">${Math.round(sodium)}mg</span></div>
    `;
});

// Load profile
fetch('/api/profile').then(r => r.json()).then(data => {
    const p = data.data || {};
    document.getElementById('profile').innerHTML = `
        <div class="stat"><span>身高</span><span class="stat-value">${p.height_cm} cm</span></div>
        <div class="stat"><span>BMR</span><span class="stat-value">${Math.round(p.bmr || 0)} kcal</span></div>
        <div class="stat"><span>TDEE</span><span class="stat-value">${Math.round(p.tdee || 0)} kcal</span></div>
        <div class="stat"><span>目标</span><span class="stat-value">${p.goal_type === 'lose' ? '减脂' : p.goal_type === 'gain' ? '增肌' : '维持'}</span></div>
    `;
});

// Load weight history and render chart
fetch('/api/weight-history?days=30').then(r => r.json()).then(data => {
    if (data.status === 'success' && data.data?.records?.length > 0) {
        // Take last 10 records, reverse to show chronological order (earliest first)
        const records = data.data.records.slice(-10).reverse();
        const labels = records.map(r => r.recorded_at?.slice(5, 10) || '');
        const weights = records.map(r => r.weight_kg);

        new Chart(document.getElementById('weightChart'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '体重 (kg)',
                    data: weights,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: false }
                }
            }
        });
    } else {
        document.getElementById('weightChart').parentElement.innerHTML = '<p style="text-align:center;color:#999;padding:40px;">暂无体重数据</p>';
    }
});

// Pantry view switching
function showPantryView(mode) {
    pantryViewMode = mode;
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');
    renderPantry();
}

// Get expiry badge
function getExpiryBadge(item) {
    if (!item.expiry_date) return { class: 'expiry-ok', text: '新鲜' };
    const today = new Date();
    today.setHours(0, 0, 0, 0);  // 只比较日期部分
    const expiry = new Date(item.expiry_date);
    expiry.setHours(0, 0, 0, 0);
    const daysLeft = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
    
    if (daysLeft < 0) return { class: 'expiry-expired', text: `已过期 ${Math.abs(daysLeft)} 天` };
    if (daysLeft === 0) return { class: 'expiry-urgent', text: '今天过期' };
    if (daysLeft === 1) return { class: 'expiry-urgent', text: '明天过期' };
    if (daysLeft <= 3) return { class: 'expiry-soon', text: `${daysLeft} 天后过期` };
    return { class: 'expiry-ok', text: `${daysLeft} 天后过期` };
}

// Render pantry item
function renderItem(item) {
    const expiry = getExpiryBadge(item);
    const percent = Math.round((item.remaining_g / item.initial_g) * 100);
    const progressClass = percent > 50 ? 'pantry-progress-high' : percent > 20 ? 'pantry-progress-medium' : 'pantry-progress-low';

    return `
        <div class="pantry-item">
            <div class="pantry-item-header">
                <div>
                    <div class="pantry-name">${item.food_name}</div>
                    <div class="pantry-qty">${item.remaining_g}g / ${item.initial_g}g (${percent}%)</div>
                </div>
                <div>
                    <span class="expiry-badge ${expiry.class}">${expiry.text}</span>
                    <button class="action-btn" onclick="openEditModal(${item.id}, '${item.food_name}', ${item.remaining_g}, ${item.shelf_life_days || 7}, '${item.purchase_date || ''}', '${item.expiry_date || ''}', '${item.location || '冰箱'}')">编辑</button>
                </div>
            </div>
            <div class="pantry-progress">
                <div class="pantry-progress-bar ${progressClass}" style="width: ${percent}%"></div>
            </div>
        </div>
    `;
}

// Render pantry
function renderPantry() {
    if (!pantryData) return;
    let html = '';

    if (pantryViewMode === 'location') {
        const locationNames = {'冰箱': '冰箱', '冷冻': '冷冻', '干货区': '干货区', '台面': '台面'};
        for (const [location, items] of Object.entries(pantryData.grouped || {})) {
            if (items.length === 0) continue;
            html += `<div class="location-section">`;
            html += `<div class="location-title">${locationNames[location]} (${items.length})</div>`;
            html += `<div class="pantry-grid">`;
            for (const item of items) html += renderItem(item);
            html += `</div></div>`;
        }
    } else {
        const categoryIcons = {'蛋白质': '', '蔬菜': '', '碳水': '', '水果': '', '乳制品': '', '脂肪': '', '其他': ''};
        for (const [category, items] of Object.entries(pantryData.by_category || {})) {
            if (items.length === 0) continue;
            html += `<div class="location-section">`;
            html += `<div class="location-title">${categoryIcons[category]} ${category} (${items.length})</div>`;
            html += `<div class="pantry-grid">`;
            for (const item of items) html += renderItem(item);
            html += `</div></div>`;
        }
    }
    document.getElementById('pantry-content').innerHTML = html;
}

// Load pantry
function loadPantry() {
    fetch('/api/pantry').then(r => r.json()).then(data => {
        if (data.status !== 'success') {
            document.getElementById('pantry-content').innerHTML = '<p>加载失败</p>';
            return;
        }
        pantryData = data.data;
        renderPantry();
    });
}

// Calculate expiry
function calculateExpiry() {
    const purchase = document.getElementById('editPurchase').value;
    const shelfLife = parseInt(document.getElementById('editShelfLife').value);
    const expirySpan = document.getElementById('editCalculatedExpiry');
    if (purchase && shelfLife > 0) {
        const pDate = new Date(purchase);
        const eDate = new Date(pDate.getTime() + shelfLife * 24 * 60 * 60 * 1000);
        expirySpan.textContent = eDate.toLocaleDateString('zh-CN');
    } else {
        expirySpan.textContent = '-';
    }
}

// Modal functions
function openEditModal(id, name, remaining, shelfLife, purchase, expiry, location) {
    currentItemId = id;
    currentItemName = name;
    currentItemRemaining = remaining;
    currentShelfLife = shelfLife;
    document.getElementById('editModalItemName').textContent = `${name} (剩余 ${remaining}g)`;
    document.getElementById('editUseAmount').value = '';
    document.getElementById('editPurchase').value = purchase || '';
    document.getElementById('editShelfLife').value = shelfLife || 7;
    document.getElementById('editLocation').value = location || '冰箱';
    calculateExpiry();
    document.getElementById('editModal').classList.add('active');
}

function openAddModal() {
    document.getElementById('addFoodName').value = '';
    document.getElementById('addQuantity').value = '';
    document.getElementById('addExpiry').value = '';
    document.getElementById('addLocation').value = 'auto';
    document.getElementById('addModal').classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

function confirmUseFromEdit() {
    const amount = parseFloat(document.getElementById('editUseAmount').value);
    if (!amount || amount <= 0) {
        alert('请输入有效的使用重量');
        return;
    }
    if (amount > currentItemRemaining) {
        alert(`使用重量不能超过剩余量 (${currentItemRemaining}g)`);
        return;
    }
    fetch('/api/pantry/use', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item_id: currentItemId, amount: amount })
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            showSuccess(`已记录：使用 ${amount}g ${currentItemName}`);
            currentItemRemaining -= amount;
            document.getElementById('editModalItemName').textContent = `${currentItemName} (剩余 ${currentItemRemaining}g)`;
            document.getElementById('editUseAmount').value = '';
            setTimeout(loadPantry, 500);
        } else {
            alert('失败：' + (data.message || data.error));
        }
    });
}

function confirmEdit() {
    const purchase = document.getElementById('editPurchase').value;
    const shelfLife = parseInt(document.getElementById('editShelfLife').value);
    const location = document.getElementById('editLocation').value;

    const body = { item_id: currentItemId };
    if (purchase) body.purchase = purchase;
    if (shelfLife > 0) body.shelf_life = shelfLife;
    if (location) body.location = location;

    fetch('/api/pantry/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            showSuccess(`已更新：${currentItemName}`);
            closeModal('editModal');
            setTimeout(loadPantry, 500);
        } else {
            alert('失败：' + (data.message || data.error));
        }
    });
}

function confirmAdd() {
    const food = document.getElementById('addFoodName').value.trim();
    const quantity = parseFloat(document.getElementById('addQuantity').value);
    const expiry = document.getElementById('addExpiry').value;
    const location = document.getElementById('addLocation').value;

    if (!food || !quantity) {
        alert('请填写完整信息');
        return;
    }

    const body = { food: food, quantity: quantity, location: location };
    if (expiry) body.expiry = expiry;

    fetch('/api/pantry/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    })
    .then(r => r.json())
    .then(data => {
        if (data.status === 'success') {
            showSuccess(`已添加：${food}`);
            closeModal('addModal');
            setTimeout(loadPantry, 500);
        } else {
            alert('失败：' + (data.message || data.error));
        }
    });
}

function showSuccess(msg) {
    const el = document.getElementById('success-msg');
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 3000);
}

// Auto-calculate expiry when inputs change
document.addEventListener('DOMContentLoaded', function() {
    const purchaseInput = document.getElementById('editPurchase');
    const shelfLifeInput = document.getElementById('editShelfLife');
    if (purchaseInput) purchaseInput.addEventListener('change', calculateExpiry);
    if (shelfLifeInput) shelfLifeInput.addEventListener('input', calculateExpiry);
});

window.onclick = function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
};

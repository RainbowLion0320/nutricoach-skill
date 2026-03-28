#!/usr/bin/env python3
"""
Health Coach Web Dashboard Server v2 - Tabbed interface.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

CURRENT_USER = None
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Food default storage locations (中文)
FOOD_STORAGE_DEFAULTS = {
    # 蛋白质
    '鸡胸肉': '冰箱', '牛肉': '冷冻', '猪肉': '冰箱', '羊肉': '冷冻',
    '三文鱼': '冷冻', '虾仁': '冷冻', '鸡蛋': '冰箱',
    # 蔬菜
    '西兰花': '冰箱', '菠菜': '冰箱', '西红柿': '冰箱', '黄瓜': '冰箱',
    '胡萝卜': '冰箱', '土豆': '干货区', '红薯': '干货区',
    # 主食
    '米饭': '冰箱', '燕麦': '干货区', '面条': '干货区',
    # 其他
    '豆腐': '冰箱', '牛奶': '冰箱', '酸奶': '冰箱',
}


def run_script(script_name: str, *args) -> Dict[str, Any]:
    """Run a skill script and return parsed JSON."""
    script_path = os.path.join(SKILL_DIR, 'scripts', script_name)
    cmd = ['python3', script_path, '--user', CURRENT_USER] + list(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_default_storage(food_name: str) -> str:
    """Get default storage location for food."""
    for key, value in FOOD_STORAGE_DEFAULTS.items():
        if key in food_name:
            return value
    return 'fridge'


@app.route('/')
def dashboard():
    """Main dashboard with tabs."""
    return render_template('dashboard_v2.html', user=CURRENT_USER)


@app.route('/api/summary')
def api_summary():
    """Get summary data."""
    daily = run_script('meal_logger.py', 'daily-summary')
    weekly = run_script('report_generator.py', 'nutrition', '--days', '7')
    weight = run_script('body_metrics.py', 'trend', '--days', '30')
    
    return jsonify({
        "daily": daily,
        "weekly": weekly,
        "weight": weight
    })


@app.route('/api/weight-history')
def api_weight_history():
    """Get weight history."""
    days = request.args.get('days', '30')
    result = run_script('body_metrics.py', 'list', '--days', days)
    return jsonify(result)


@app.route('/api/nutrition-history')
def api_nutrition_history():
    """Get nutrition history."""
    days = request.args.get('days', '7')
    result = run_script('meal_logger.py', 'list', '--days', days)
    return jsonify(result)


@app.route('/api/profile')
def api_profile():
    """Get user profile."""
    result = run_script('user_profile.py', 'get')
    return jsonify(result)


@app.route('/api/pantry')
def api_pantry():
    """Get pantry items grouped by location."""
    result = run_script('pantry_manager.py', 'remaining')
    
    if result.get('status') == 'success':
        items = result['data']['items']
        
        # Group by location (中文)
        grouped = {'冰箱': [], '冷冻': [], '干货区': [], '台面': []}
        for item in items:
            loc = item.get('location', '冰箱')
            # 转换旧数据
            loc_map = {
                'fridge': '冰箱',
                'freezer': '冷冻', 
                'pantry': '干货区',
                'counter': '台面'
            }
            loc = loc_map.get(loc, loc)
            if loc in grouped:
                grouped[loc].append(item)
        
        result['data']['grouped'] = grouped
    
    return jsonify(result)


@app.route('/api/pantry/use', methods=['POST'])
def api_pantry_use():
    """Record pantry item usage."""
    data = request.json
    result = run_script('pantry_manager.py', 'use',
                       '--item-id', str(data.get('item_id')),
                       '--amount', str(data.get('amount')),
                       '--notes', data.get('notes', ''))
    return jsonify(result)


@app.route('/api/pantry/add', methods=['POST'])
def api_pantry_add():
    """Add item to pantry."""
    data = request.json
    
    # Auto-detect storage location if not provided
    location = data.get('location')
    if not location or location == 'auto':
        location = get_default_storage(data.get('food', ''))
    
    result = run_script('pantry_manager.py', 'add',
                       '--food', data.get('food'),
                       '--quantity', str(data.get('quantity')),
                       '--expiry', data.get('expiry'),
                       '--location', location)
    return jsonify(result)


def create_templates():
    """Create template."""
    template_dir = os.path.join(SKILL_DIR, 'templates')
    os.makedirs(template_dir, exist_ok=True)
    
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Coach - {{ user }}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        header h1 { font-size: 2em; margin-bottom: 10px; }
        
        /* Tabs */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: white;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        .tab {
            padding: 10px 20px;
            border: none;
            background: #f0f0f0;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }
        .tab:hover { background: #e0e0e0; }
        .tab.active {
            background: #667eea;
            color: white;
        }
        
        /* Tab content */
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        }
        .card h2 {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #667eea;
        }
        .stat {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .stat:last-child { border-bottom: none; }
        .stat-value { font-weight: bold; color: #667eea; }
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        .loading { text-align: center; padding: 40px; color: #999; }
        
        /* Pantry specific */
        .location-section {
            margin-bottom: 25px;
        }
        .location-title {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 10px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .pantry-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        .pantry-item:last-child { border-bottom: none; }
        .pantry-name { font-weight: 500; }
        .pantry-qty { color: #666; font-size: 0.9em; }
        .expiry-badge {
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 500;
        }
        .expiry-urgent { background: #fee; color: #c33; }
        .expiry-soon { background: #ffeaa7; color: #d63031; }
        .expiry-ok { background: #e8f5e9; color: #2e7d32; }
        .action-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 5px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            margin-left: 10px;
        }
        .action-btn:hover { background: #5568d3; }
        .add-btn {
            background: #4caf50;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
        }
        .add-btn:hover { background: #45a049; }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal.active { display: flex; }
        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 12px;
            width: 90%;
            max-width: 400px;
        }
        .modal h3 { margin-bottom: 20px; }
        .modal input, .modal select {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 6px;
            box-sizing: border-box;
        }
        .modal-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .modal-buttons button {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        .modal-buttons .confirm { background: #667eea; color: white; }
        .modal-buttons .cancel { background: #f0f0f0; }
        .success-msg {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏃 Health Coach</h1>
            <p>用户: {{ user }}</p>
        </header>
        
        <!-- Tabs -->
        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">📊 概览</button>
            <button class="tab" onclick="showTab('pantry')">🥬 食材管理</button>
            <button class="tab" onclick="showTab('weight')">⚖️ 体重记录</button>
        </div>
        
        <!-- Overview Tab -->
        <div id="overview" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h2>📊 今日概览</h2>
                    <div id="daily-summary"><div class="loading">加载中...</div></div>
                </div>
                <div class="card">
                    <h2>⚖️ 体重趋势</h2>
                    <div class="chart-container"><canvas id="weightChart"></canvas></div>
                </div>
                <div class="card">
                    <h2>🍽️ 营养趋势</h2>
                    <div class="chart-container"><canvas id="nutritionChart"></canvas></div>
                </div>
                <div class="card">
                    <h2>👤 身体数据</h2>
                    <div id="profile"><div class="loading">加载中...</div></div>
                </div>
            </div>
        </div>
        
        <!-- Pantry Tab -->
        <div id="pantry" class="tab-content">
            <button class="add-btn" onclick="openAddModal()">➕ 添加食材</button>
            <div id="pantry-content"><div class="loading">加载中...</div></div>
            <div id="success-msg" class="success-msg"></div>
        </div>
        
        <!-- Weight Tab -->
        <div id="weight" class="tab-content">
            <div class="card">
                <h2>体重记录功能开发中...</h2>
                <p>请使用命令行记录体重</p>
            </div>
        </div>
    </div>
    
    <!-- Modals -->
    <div id="useModal" class="modal">
        <div class="modal-content">
            <h3>🍳 记录使用</h3>
            <p id="useModalItemName"></p>
            <input type="number" id="useAmount" placeholder="使用重量 (g)" min="1">
            <input type="text" id="useNotes" placeholder="备注（可选）">
            <div class="modal-buttons">
                <button class="confirm" onclick="confirmUse()">确认</button>
                <button class="cancel" onclick="closeModal('useModal')">取消</button>
            </div>
        </div>
    </div>
    
    <div id="addModal" class="modal">
        <div class="modal-content">
            <h3>➕ 添加食材</h3>
            <input type="text" id="addFoodName" placeholder="食材名称">
            <input type="number" id="addQuantity" placeholder="重量 (g)" min="1">
            <input type="date" id="addExpiry">
            <select id="addLocation">
                <option value="auto">🤖 自动检测储藏方式</option>
                <option value="冰箱">❄️ 冰箱</option>
                <option value="冷冻">🧊 冷冻</option>
                <option value="干货区">📦 干货区</option>
                <option value="台面">🌡️ 台面</option>
            </select>
            <div class="modal-buttons">
                <button class="confirm" onclick="confirmAdd()">添加</button>
                <button class="cancel" onclick="closeModal('addModal')">取消</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentItemId = null;
        let currentItemName = null;
        
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
            // Daily summary
            const daily = data.daily?.data || {};
            document.getElementById('daily-summary').innerHTML = `
                <div class="stat"><span>热量</span><span class="stat-value">${Math.round(daily.totals?.calories || 0)}/${Math.round(daily.tdee || 2000)} kcal</span></div>
                <div class="stat"><span>蛋白质</span><span class="stat-value">${Math.round(daily.totals?.protein_g || 0)}g</span></div>
                <div class="stat"><span>碳水</span><span class="stat-value">${Math.round(daily.totals?.carbs_g || 0)}g</span></div>
                <div class="stat"><span>脂肪</span><span class="stat-value">${Math.round(daily.totals?.fat_g || 0)}g</span></div>
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
        
        // Load pantry
        function loadPantry() {
            fetch('/api/pantry').then(r => r.json()).then(data => {
                if (data.status !== 'success') {
                    document.getElementById('pantry-content').innerHTML = '<p>加载失败</p>';
                    return;
                }
                
                const grouped = data.data.grouped;
                const locationNames = {
                    '冰箱': '❄️ 冰箱',
                    '冷冻': '🧊 冷冻',
                    '干货区': '📦 干货区',
                    '台面': '🌡️ 台面'
                };
                
                let html = '';
                for (const [location, items] of Object.entries(grouped)) {
                    if (items.length === 0) continue;
                    
                    html += `<div class="location-section">`;
                    html += `<div class="location-title">${locationNames[location]} (${items.length})</div>`;
                    
                    for (const item of items) {
                        const today = new Date();
                        let expiryClass = 'expiry-ok';
                        let expiryText = '新鲜';
                        
                        if (item.expiry_date) {
                            const expiry = new Date(item.expiry_date);
                            const daysLeft = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
                            
                            if (daysLeft <= 1) {
                                expiryClass = 'expiry-urgent';
                                expiryText = '今天过期';
                            } else if (daysLeft <= 3) {
                                expiryClass = 'expiry-soon';
                                expiryText = `${daysLeft}天后过期`;
                            } else {
                                expiryText = `${daysLeft}天后过期`;
                            }
                        }
                        
                        html += `
                            <div class="pantry-item">
                                <div>
                                    <div class="pantry-name">${item.food_name}</div>
                                    <div class="pantry-qty">剩余 ${item.remaining_g}g / 初始 ${item.initial_g}g</div>
                                </div>
                                <div>
                                    <span class="expiry-badge ${expiryClass}">${expiryText}</span>
                                    ${item.remaining_g > 0 ? `<button class="action-btn" onclick="openUseModal(${item.id}, '${item.food_name}', ${item.remaining_g})">使用</button>` : ''}
                                </div>
                            </div>
                        `;
                    }
                    html += `</div>`;
                }
                
                document.getElementById('pantry-content').innerHTML = html;
            });
        }
        
        // Modal functions
        function openUseModal(id, name, maxAmount) {
            currentItemId = id;
            currentItemName = name;
            document.getElementById('useModalItemName').textContent = `${name} (最多 ${maxAmount}g)`;
            document.getElementById('useAmount').value = '';
            document.getElementById('useNotes').value = '';
            document.getElementById('useModal').classList.add('active');
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
        
        function confirmUse() {
            const amount = parseFloat(document.getElementById('useAmount').value);
            const notes = document.getElementById('useNotes').value;
            
            if (!amount || amount <= 0) {
                alert('请输入有效的使用重量');
                return;
            }
            
            fetch('/api/pantry/use', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: currentItemId, amount: amount, notes: notes })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    showSuccess(`已记录：使用 ${amount}g ${currentItemName}`);
                    closeModal('useModal');
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
            
            fetch('/api/pantry/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ food: food, quantity: quantity, expiry: expiry, location: location })
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
        
        window.onclick = function(e) {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('active');
            }
        };
    </script>
</body>
</html>'''
    
    template_path = os.path.join(template_dir, 'dashboard_v2.html')
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Created template: {template_path}")
    
    return template_dir


def main():
    global CURRENT_USER
    
    parser = argparse.ArgumentParser(description='Health Coach Web Dashboard v2')
    parser.add_argument('--user', required=True, help='Username')
    parser.add_argument('--port', type=int, default=5000, help='Port (default: 5000)')
    
    args = parser.parse_args()
    CURRENT_USER = args.user
    
    template_dir = create_templates()
    app.template_folder = template_dir
    
    print(f"🌐 Health Coach Dashboard v2")
    print(f"   User: {CURRENT_USER}")
    print(f"   URL: http://127.0.0.1:{args.port}")
    print(f"   Press Ctrl+C to stop\n")
    
    try:
        app.run(host='127.0.0.1', port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
        sys.exit(0)


if __name__ == '__main__':
    main()

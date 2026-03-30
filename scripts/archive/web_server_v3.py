#!/usr/bin/env python3
"""
Health Coach Web Dashboard Server v3 - Modular Design
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Dict, Any

from flask import Flask, render_template_string, jsonify, request

TEMPLATE_VERSION = "2026-03-29-008"

app = Flask(__name__)
CURRENT_USER = None
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load HTML template from file
def load_template():
    template_path = os.path.join(SKILL_DIR, 'templates', 'dashboard_v3.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

HTML_TEMPLATE = load_template()


def run_script(script_name: str, *args) -> Dict[str, Any]:
    """Run a skill script and return parsed JSON."""
    script_path = os.path.join(SKILL_DIR, 'scripts', script_name)
    cmd = ['python3', script_path, '--user', CURRENT_USER] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return json.loads(result.stdout) if result.returncode == 0 else {"status": "error", "error": result.stderr}
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Routes
@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, user=CURRENT_USER)


@app.route('/api/summary')
def api_summary():
    daily = run_script('meal_logger.py', 'daily-summary')
    weekly = run_script('report_generator.py', 'nutrition', '--days', '7')
    weight = run_script('body_metrics.py', 'trend', '--days', '30')
    return jsonify({"daily": daily, "weekly": weekly, "weight": weight})


@app.route('/api/profile')
def api_profile():
    return jsonify(run_script('user_profile.py', 'get'))


@app.route('/api/pantry')
def api_pantry():
    result = run_script('pantry_manager.py', 'remaining')
    if result.get('status') == 'success':
        items = result['data']['items']
        loc_map = {'fridge': '冰箱', 'freezer': '冷冻', 'pantry': '干货区', 'counter': '台面'}
        grouped = {'冰箱': [], '冷冻': [], '干货区': [], '台面': []}
        for item in items:
            loc = loc_map.get(item.get('location', '冰箱'), item.get('location', '冰箱'))
            if loc in grouped:
                grouped[loc].append(item)
        result['data']['grouped'] = grouped
    return jsonify(result)


@app.route('/api/pantry/use', methods=['POST'])
def api_pantry_use():
    data = request.json
    result = run_script('pantry_manager.py', 'use',
                       '--item-id', str(data.get('item_id')),
                       '--amount', str(data.get('amount')),
                       '--notes', data.get('notes', ''))
    return jsonify(result)


@app.route('/api/pantry/update', methods=['POST'])
def api_pantry_update():
    data = request.json
    loc_map = {'冰箱': 'fridge', '冷冻': 'freezer', '干货区': 'pantry', '台面': 'counter'}
    args = ['--item-id', str(data.get('item_id'))]
    if data.get('purchase'):
        args.extend(['--purchase', data.get('purchase')])
    if data.get('shelf_life'):
        args.extend(['--shelf-life', str(data.get('shelf_life'))])
    if data.get('location'):
        args.extend(['--location', loc_map.get(data.get('location'), data.get('location'))])
    if data.get('notes'):
        args.extend(['--notes', data.get('notes')])
    return jsonify(run_script('pantry_manager.py', 'update', *args))


@app.route('/api/pantry/add', methods=['POST'])
def api_pantry_add():
    data = request.json
    loc_map = {'冰箱': 'fridge', '冷冻': 'freezer', '干货区': 'pantry', '台面': 'counter'}
    args = ['--food', data.get('food'), '--quantity', str(data.get('quantity')),
            '--location', loc_map.get(data.get('location', '冰箱'), data.get('location', '冰箱'))]
    if data.get('expiry'):
        args.extend(['--expiry', data.get('expiry')])
    return jsonify(run_script('pantry_manager.py', 'add', *args))


def main():
    global CURRENT_USER, HTML_TEMPLATE
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', required=True)
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    CURRENT_USER = args.user

    if HTML_TEMPLATE is None:
        print("Error: Template not found")
        sys.exit(1)

    print(f"🌐 Health Coach Dashboard v3")
    print(f"   User: {CURRENT_USER}")
    print(f"   URL: http://localhost:{args.port}")
    app.run(host='0.0.0.0', port=args.port, debug=False)


if __name__ == '__main__':
    main()

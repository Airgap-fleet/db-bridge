from flask import Flask, render_template, jsonify, request, Response, g
from datetime import datetime
import sqlite3
import json

app = Flask(__name__)

DB_PATH = 'C:/the force/03_Context/projects/mission-control/dashboard.db'


def get_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        return None


@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


@app.route('/api/rules')
def get_all_rules():
    conn = get_db()
    if not conn:
        return jsonify({"detail": {"message": "Database connection failed"}}), 500
    try:
        cursor = conn.execute('SELECT id, name, enabled, decision_text FROM rules')
        rules = [dict(row) for row in cursor.fetchall()]
        return jsonify(rules)
    except sqlite3.Error as e:
        return jsonify({"detail": {"message": str(e)}}), 500


@app.route('/api/rules-tree')
def get_rules_tree():
    try:
        indent = int(request.args.get('indent', '0'))
        conn = get_db()
        if not conn:
            return jsonify({"detail": {"message": "Database connection failed"}}), 500
        cursor = conn.execute('SELECT id, name, enabled, decision_text FROM rules')
        rules = [dict(row) for row in cursor.fetchall()]
        def format_rule(r):
            tree = f"{' ' * indent}- {r['name']} (enabled={r.get('enabled', False)})\n"
            if r.get('decision_text'):
                tree += f"  Text:\n  {json.dumps(json.loads(r['decision_text']), indent=2, ensure_ascii=False)}\n"
            return tree
        return jsonify({"tree": '\n'.join(format_rule(r) for r in rules)})
    except ValueError: # invalid 'indent' param
        return jsonify({'detail': {'message': 'Invalid indent parameter'}}), 400
    except sqlite3.Error as e:
        return jsonify({"detail": {"message": str(e)}}), 500


@app.route('/api/decisions', methods=['GET'])
def get_decisions():
    conn = get_db()
    if not conn:
        return jsonify({'detail': {'message': 'Database connection failed'}}), 500
    try:
        cursor = conn.execute('SELECT id, rule_id, user_approval, timestamp FROM decisions')
        items = [dict(row) for row in cursor.fetchall()]
        return jsonify(items)
    except sqlite3.Error as e:
        return jsonify({'detail': {'message': str(e)}}), 500


@app.route('/api/decisions-stream', methods=['GET'])
def stream_decisions():
    def decision_generator():
        conn = get_db()
        if not conn:
            yield f"data: {json.dumps({'detail': {'message': 'Database connection failed'}})}\n\n"
            return
        cursor = conn.execute('SELECT id, rule_id, user_approval, timestamp FROM decisions')
        items = [dict(row) for row in cursor.fetchall()]
        for item in items:
            yield f"data: {json.dumps(item)}\n\n"
    return Response(decision_generator(), mimetype='text/event-stream')


@app.route('/api/decisions', methods=['POST'])
def approve_decision():
    try:
        data = request.get_json()
        rule_id = data.get('rule_id')
        user_approval = data.get('user_approval', 'master')
        timestamp = datetime.now().isoformat()
        conn = get_db()
        if not conn:
            return jsonify({"detail": {"message": "Database connection failed"}}), 500
        cursor = conn.execute(
            'INSERT INTO decisions (rule_id, user_approval, timestamp) VALUES (?, ?, ?)',
            (rule_id, user_approval, timestamp)
        )
        conn.commit()
        return jsonify({"status": "approved", "timestamp": timestamp})
    except sqlite3.Error as e:
        return jsonify({'detail': {'message': str(e)}}), 500


@app.route('/')
def dashboard():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8420)

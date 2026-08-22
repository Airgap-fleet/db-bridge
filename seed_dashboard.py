import sqlite3, json

DB = r'C:/the force/03_Context/projects/mission-control/dashboard.db'
conn = sqlite3.connect(DB)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS rules (id INTEGER PRIMARY KEY, name TEXT, enabled INTEGER, decision_text TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, rule_id INTEGER, user_approval TEXT, timestamp TEXT)')
cursor.executemany('INSERT INTO rules VALUES (NULL, ?, ?, ?)', [
    ('Deploy Edge Case Tests', 1, json.dumps(['run_tests', 'notify_master'])),
    ('Review Commit Messages', 1, json.dumps({'action': 'scan_commits', 'strictness': 'medium'})),
    ('Sprint Planning', 0, json.dumps({'action': 'estimate_velocity', 'buffer_days': 2}))
])
conn.commit()
conn.close()

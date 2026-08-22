#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'mission_control.db')
print(f'Database path: {DB_PATH}')

# Initialize fresh database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Create the tables with correct schema
exec(open('server.py').read())

# Check messages table structure
cursor.execute('PRAGMA table_info(messages)')
columns = cursor.fetchall()
print('Messages table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# Check agents table structure
cursor.execute('PRAGMA table_info(agents)')
columns = cursor.fetchall()
print('Agents table columns:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

conn.close()
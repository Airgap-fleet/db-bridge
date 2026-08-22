#!/usr/bin/env python3
import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(__file__), 'mission_control.db')

def init_database():
    """Initialize SQLite database with required tables"""
    try:
        # Connect to database
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                color TEXT NOT NULL,
                last_seen INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                rules_of_engagement TEXT
            )
        ''')
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'Backlog',
                priority TEXT DEFAULT 'Medium',
                assignee TEXT,
                agent_id TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            )
        ''')
        
        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        print("Database initialized successfully")
        return conn, cursor
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def seed_initial_data(conn, cursor):
    """Seed initial data for the system"""
    try:
        agents = [
            {
                'id': 'obi-wan',
                'name': 'Obi-Wan Kenobi',
                'role': 'Orchestrator',
                'color': '#00d4aa',
                'last_seen': int(time.time()),
                'status': 'active',
                'rules_of_engagement': '''# Protocol: Oversight
IF message contains "concern" OR "review" AND not @mentioned:
  - Reply with clarification questions
  - Create task in Oversight with priority High
  - Assign to self

# Protocol: Deployment
IF message contains "deploy" OR "launch" OR "release":
  - Create task in Deployment with priority Critical
  - Assign to self
  - Reply "Initiating deployment sequence"

# Protocol: Emergency
IF message contains "urgent" OR "critical" OR "emergency":
  - Create task in Emergency with priority Critical
  - Assign to self
  - Reply "Emergency protocol activated"'''
            },
            {
                'id': 'scotty',
                'name': 'Scotty',
                'role': 'Backend Engineering Agent',
                'color': '#ff6b35',
                'last_seen': int(time.time()),
                'status': 'active',
                'rules_of_engagement': '''# Protocol: Development
IF message contains "implement" OR "develop" OR "build":
  - Create task in Development with priority Medium
  - Assign to self
  - Reply "Starting implementation"

# Protocol: Testing
IF message contains "test" OR "validate" OR "quality":
  - Create task in Testing with priority Medium
  - Assign to self
  - Reply "Running quality checks"

# Protocol: Documentation
IF message contains "document" OR "readme" OR "notes":
  - Create task in Documentation with priority Low
  - Assign to self
  - Reply "Creating documentation"'''
            }
        ]
        
        for agent in agents:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO agents (id, name, role, color, last_seen, status, rules_of_engagement)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    agent['id'],
                    agent['name'],
                    agent['role'],
                    agent['color'],
                    agent['last_seen'],
                    agent['status'],
                    agent['rules_of_engagement']
                ))
                conn.commit()
                print(f"Seeded agent: {agent['id']}")
            except Exception as e:
                print(f"Error seeding agent {agent['id']}: {e}")
        
        print("Initial data seeded successfully")
    except Exception as e:
        print(f"Error seeding initial data: {e}")
        raise

def add_task(cursor, conn, task_data):
    now = int(time.time())
    cursor.execute('''
        INSERT INTO tasks (title, description, status, priority, assignee, agent_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (task_data['title'], task_data['description'], task_data['status'], 
          task_data['priority'], task_data['assignee'], task_data['agent_id'], now, now))
    conn.commit()
    task_id = cursor.lastrowid
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    return dict(cursor.fetchone())

def add_message(cursor, conn, message_data):
    now = int(time.time())
    cursor.execute('''
        INSERT INTO messages (agent_id, content, timestamp)
        VALUES (?, ?, ?)
    ''', (message_data['agent_id'], message_data['content'], now))
    conn.commit()
    msg_id = cursor.lastrowid
    cursor.execute("SELECT * FROM messages WHERE id = ?", (msg_id,))
    return dict(cursor.fetchone())

# Test the database functions
conn, cursor = init_database()
seed_initial_data(conn, cursor)

# Test adding a message
message_data = {
    'agent_id': 'obi-wan',
    'content': 'The deployment completed successfully with zero errors.',
    'created_at': int(time.time())
}

message = add_message(cursor, conn, message_data)
print(f"✓ Message added with ID: {message['id']}")

# Test task creation from action
task_data = {
    'title': 'Deployment task from Obi-Wan',
    'description': 'Generated from message: The deployment completed successfully with zero errors.',
    'status': 'Backlog',
    'priority': 'Critical',
    'assignee': 'obi-wan',
    'agent_id': 'obi-wan',
    'created_at': int(time.time()),
    'updated_at': int(time.time())
}

task = add_task(cursor, conn, task_data)
print(f"✓ Task created with ID: {task['id']}")

# Verify the task exists
cursor.execute("SELECT * FROM tasks WHERE agent_id = ? ORDER BY created_at DESC", ('obi-wan',))
results = cursor.fetchall()
print(f"Tasks for obi-wan: {len(results)} tasks found")

# Clean up
conn.close()
print("Database test completed successfully!")
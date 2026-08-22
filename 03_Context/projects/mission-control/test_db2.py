import sqlite3
import os

DB_PATH = r"C:\the force\03_Context\projects\mission-control\mission_control.db"

print("Testing database creation with simpler approach...")

# Remove existing database
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Removed existing database")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Create tables using proper SQL with correct quoting
try:
    # Create agents table
    sql_agents = """
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            color TEXT NOT NULL,
            last_seen INTEGER NOT NULL,
            status TEXT DEFAULT 'active',
            rules_of_engagement TEXT
        )
    """
    cursor.execute(sql_agents)
    print("Agents table created")
    
    # Create tasks table
    sql_tasks = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Backlog',
            priority TEXT DEFAULT 'Medium',
            assignee TEXT,
            agent_id TEXT,
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL,
            FOREIGN KEY (assignee) REFERENCES agents(id)
        )
    """
    cursor.execute(sql_tasks)
    print("Tasks table created")
    
    # Create messages table
    sql_messages = """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """
    cursor.execute(sql_messages)
    print("Messages table created")
    
    # Create agent_listeners table
    sql_listeners = """
        CREATE TABLE IF NOT EXISTS agent_listeners (
            agent_id TEXT PRIMARY KEY,
            last_processed_message_id INTEGER,
            rules_of_engagement TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """
    cursor.execute(sql_listeners)
    print("Agent listeners table created")
    
    # Create workflows table
    sql_workflows = """
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version INTEGER NOT NULL,
            definition_yaml TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at INTEGER NOT NULL
        )
    """
    cursor.execute(sql_workflows)
    print("Workflows table created")
    
    # Create agent_skills table
    sql_skills = """
        CREATE TABLE IF NOT EXISTS agent_skills (
            agent_id TEXT,
            skill_name TEXT,
            proficiency REAL DEFAULT 0.0,
            evidence_count INTEGER DEFAULT 0,
            last_demonstrated INTEGER NOT NULL,
            PRIMARY KEY (agent_id, skill_name),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """
    cursor.execute(sql_skills)
    print("Agent skills table created")
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_agent ON messages(agent_id)')
    
    print("Indexes created")
    
    conn.commit()
    print("Database created successfully!")
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    print(f"Tables in database: {[t['name'] for t in tables]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()
    print("Database connection closed")
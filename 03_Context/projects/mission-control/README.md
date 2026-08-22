# Mission Control Dashboard

A real-time Kanban dashboard and agent communication system for managing development workflows.

## Quick Start

```bash
cd "C:\the force\03_Context\projects\mission-control"
python3 server.py
```

Open your browser and navigate to: `http://localhost:8420`

## Features

### Kanban Board
- **5 Columns**: Backlog → Todo → In Progress → Review → Done
- **Task Cards**: Title, assignee, priority, and action buttons
- **Real-time Updates**: Automatic synchronization across all open tabs
- **Agent Status**: Visual status indicators (Active/Idle/Dormant)

### Chat Panel
- **Agent Communication**: Real-time messaging between team members
- **Auto-scroll**: Messages automatically scroll to latest
- **Enter to Send**: Quick message submission

### Agent Management
- **Pre-seeded Agents**: Obi-Wan (Orchestrator) and Scotty (Coding)
- **Registration**: Add new agents with custom colors and roles
- **Status Tracking**: Automatic status updates based on last activity
  - Active: ≤5 minutes since last activity
  - Idle: 5-120 minutes since last activity  
  - Dormant: >120 minutes since last activity

### Real-time Updates
- **SSE Broadcasting**: Server-Sent Events push updates every 10 seconds
- **Last-Event-ID**: Resume capability for disconnected clients
- **Heartbeat System**: Keep connections alive

## Technology Stack

- **Backend**: Python 3.11+ with standard library only
- **Web Server**: `socketserver.ThreadingTCPServer`
- **Database**: SQLite 3 with agents, tasks, and messages tables
- **Real-time**: Server-Sent Events (SSE) for live updates
- **Frontend**: HTML/CSS/JavaScript (single-page application)

## API Endpoints

### GET /api/agents
Returns all agents with current status
```json
[
  {
    "id": "obi-wan",
    "name": "Obi-Wan",
    "role": "Orchestrator",
    "color": "#00d4aa",
    "last_seen": 1786433324,
    "status": "active"
  }
]
```

### POST /api/agents
Add a new agent
```json
{
  "id": "new-agent",
  "name": "Agent Name",
  "role": "Agent Role",
  "color": "#color-code"
}
```

### GET /api/tasks
Returns all tasks in Kanban order

### POST /api/tasks
Add a new task
```json
{
  "title": "Task Title",
  "description": "Task description",
  "status": "Backlog",
  "priority": "Medium",
  "assignee": "obi-wan"
}
```

### GET /api/messages
Returns all messages in chronological order

### POST /api/messages
Send a message
```json
{
  "agent_id": "obi-wan",
  "content": "Hello team!"
}
```

## SSE Endpoint

### GET /events
Server-Sent Events endpoint for real-time updates

```javascript
const eventSource = new EventSource('http://localhost:8420/events');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  if (data.type === 'update') {
    // Update your UI with new agents, tasks, or messages
    handleUpdate(data);
  }
};
```

## Usage

### 1. Starting the Server
The server runs on port 8420 and serves the dashboard interface:

```bash
# From the project directory
python3 server.py
```

### 2. Accessing the Dashboard
Open your web browser and go to:
```
http://localhost:8420
```

### 3. Adding an Agent
Click the "+ Add Agent" button (bottom-right) to open the agent modal:
- Enter agent ID, name, role, and color
- Click "Save"

### 4. Creating a Task
Click the "+ New Task" button (top-right of Kanban) to add tasks:
- Enter title and description
- Set priority (High/Medium/Low)
- Assign to an agent
- Click "Create"

### 5. Managing Tasks
Each task card has action buttons:
- **Claim**: Assign task to yourself
- **Move**: Change task status
- **Edit**: Modify task details
- **Delete**: Remove task

### 6. Chat
Use the chat panel on the right:
- Select an agent from the list
- Type messages and press Enter
- Messages appear in real-time for all users

## Agent Status Indicators

The dashboard shows agent status with colored dots:

🟢 **Active**: Agent active within last 5 minutes
🟡 **Idle**: Agent inactive 5-120 minutes ago
🔴 **Dormant**: Agent inactive over 120 minutes ago

## Browser Compatibility

Works in modern browsers including:
- Chrome
- Firefox
- Safari
- Edge

## Troubleshooting

### Server Won't Start
```bash
# Check if port 8420 is in use
netstat -ano | findstr "8420"

# Kill any processes using port 8420
netstat -ano | findstr "8420" | awk '{print $2}' | xargs kill -9
```

### Database Issues
If you encounter database errors:
```bash
# Remove corrupted database file
cd "C:\the force\03_Context\projects\mission-control"
rm -f mission_control.db

# Restart server
python3 server.py
```

### SSE Not Working
Ensure your browser allows pop-ups and real-time connections:
- Check browser console for JavaScript errors
- Ensure no ad-blockers are interfering
- Try refreshing the page

## License

Mission Control Dashboard - Real-time Kanban and Agent Communication
Copyright © 2026

This project is part of the AFaaS (Agentic Framework as a Service) initiative.

## Credits

- Inspired by Atlassian Jira and Trello Kanban interfaces
- Real-time synchronization using Server-Sent Events (SSE)
- Built with Python standard library for maximum portability
- Designed for agent coordination and task tracking

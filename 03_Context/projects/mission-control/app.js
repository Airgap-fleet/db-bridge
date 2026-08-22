// Mission Control Dashboard Frontend — Vanilla ES6 Module
const API_BASE = '/api/';

class MissionControlDashboard {
  constructor() {
    // State
    this.agents = [];
    this.tasks = [];
    this.messages = { general: [] };
    this.currentChannel = 'general';
    this.selectedAgentFilter = null;
    this.sse = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
    this.draggedTaskId = null;
    
    // DOM Elements
    this.elements = {};
    
    // Initialize
    this.cacheElements();
    this.bindEvents();
    this.init();
  }

  // ========== INITIALIZATION ==========
  
  async init() {
    this.showLoading(true);
    try {
      await Promise.all([this.fetchAgents(), this.fetchTasks()]);
      this.renderAll();
      this.setupSSE();
    } catch (err) {
      console.error('Initialization failed:', err);
      this.showToast('Failed to initialize dashboard', 'error');
    } finally {
      this.showLoading(false);
    }
  }

  cacheElements() {
    // Main layout
    this.elements.dashboardLayout = document.getElementById('dashboard-layout');
    this.elements.agentSidebar = document.getElementById('agent-sidebar');
    this.elements.chatPanel = document.getElementById('chat-panel');
    this.elements.sidebarCollapse = document.getElementById('sidebar-collapse');
    this.elements.chatCollapse = document.getElementById('chat-collapse');
    this.elements.sidebarContent = document.getElementById('sidebar-content');
    
    // Kanban columns
    this.columns = ['triage', 'todo', 'ready', 'running', 'blocked', 'done'];
    this.columnElements = {};
    this.countElements = {};
    this.columns.forEach(col => {
      this.columnElements[col] = document.getElementById(`column-${col}`);
      this.countElements[col] = document.getElementById(`count-${col}`);
    });
    
    // Agent list
    this.elements.agentList = document.getElementById('agent-list');
    
    // Chat
    this.elements.chatTabs = document.getElementById('chat-tabs');
    this.elements.chatMessages = document.getElementById('chat-messages');
    this.elements.chatInput = document.getElementById('chat-input');
    this.elements.chatSendBtn = document.getElementById('chat-send-btn');
    this.elements.chatInputArea = document.getElementById('chat-input-area');
    
    // Modals
    this.elements.createTaskModal = document.getElementById('createTaskModal');
    this.elements.createTaskForm = document.getElementById('create-task-form');
    this.elements.taskTitle = document.getElementById('task-title');
    this.elements.taskDescription = document.getElementById('task-description');
    this.elements.taskAssignee = document.getElementById('task-assignee');
    this.elements.taskPriority = document.getElementById('task-priority');
    this.elements.createTaskSubmit = document.getElementById('create-task-submit');
    
    this.elements.taskDetailModal = document.getElementById('taskDetailModal');
    this.elements.taskDetailBody = document.getElementById('task-detail-body');
    this.elements.taskDeleteBtn = document.getElementById('task-delete-btn');
    
    // Toast container
    this.elements.toastContainer = document.getElementById('toast-container');
    
    // Header buttons
    this.elements.createTaskBtn = document.getElementById('create-task-btn');
    
    // Bootstrap modal instances
    this.createTaskModal = new bootstrap.Modal(this.elements.createTaskModal);
    this.taskDetailModal = new bootstrap.Modal(this.elements.taskDetailModal);
  }

  bindEvents() {
    // Create task button
    this.elements.createTaskBtn.addEventListener('click', () => this.openCreateTaskModal());
    
    // Create task form submit
    this.elements.createTaskForm.addEventListener('submit', (e) => this.handleCreateTask(e));
    
    // Task detail modal delete
    this.elements.taskDeleteBtn.addEventListener('click', () => this.handleDeleteTask());
    
    // Sidebar collapse
    this.elements.sidebarCollapse.addEventListener('click', () => this.toggleSidebar());
    
    // Chat collapse
    this.elements.chatCollapse.addEventListener('click', () => this.toggleChat());
    
    // Chat send
    this.elements.chatSendBtn.addEventListener('click', () => this.sendMessage());
    this.elements.chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    
    // Chat tabs delegation
    this.elements.chatTabs.addEventListener('click', (e) => {
      const tab = e.target.closest('.chat-tab');
      if (tab) this.switchChannel(tab.dataset.channel);
    });
    
    // Kanban drag and drop
    this.columns.forEach(col => {
      const columnEl = this.columnElements[col];
      columnEl.addEventListener('dragover', (e) => this.handleDragOver(e, col));
      columnEl.addEventListener('dragleave', (e) => this.handleDragLeave(e, col));
      columnEl.addEventListener('drop', (e) => this.handleDrop(e, col));
    });
    
    // Task card click delegation (for detail modal)
    document.getElementById('kanban-board').addEventListener('click', (e) => {
      const card = e.target.closest('.task-card');
      if (card && !e.target.closest('button')) {
        this.openTaskDetailModal(card.dataset.taskId);
      }
    });
    
    // Drag start delegation
    document.getElementById('kanban-board').addEventListener('dragstart', (e) => {
      const card = e.target.closest('.task-card');
      if (card) {
        this.handleDragStart(e);
      }
    });
    
    // Drag end delegation (cleanup)
    document.getElementById('kanban-board').addEventListener('dragend', (e) => {
      const card = e.target.closest('.task-card');
      if (card) {
        card.classList.remove('dragging');
      }
    });
    
    // Agent click delegation
    this.elements.agentList.addEventListener('click', (e) => {
      const agentItem = e.target.closest('.agent-item');
      if (agentItem) this.filterByAgent(agentItem.dataset.agentId);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    
    // Modal cleanup
    this.elements.createTaskModal.addEventListener('hidden.bs.modal', () => this.resetCreateTaskForm());
    this.elements.taskDetailModal.addEventListener('hidden.bs.modal', () => this.resetTaskDetailModal());
  }

  // ========== API CALLS ==========
  
  async fetchAgents() {
    const res = await fetch(API_BASE + 'agents');
    if (!res.ok) throw new Error('Failed to fetch agents');
    this.agents = await res.json();
  }

  async fetchTasks() {
    const res = await fetch(API_BASE + 'tasks');
    if (!res.ok) throw new Error('Failed to fetch tasks');
    this.tasks = await res.json();
  }

  async fetchMessages(taskRef = null) {
    const url = taskRef 
      ? `${API_BASE}messages?task_ref=${encodeURIComponent(taskRef)}`
      : `${API_BASE}messages`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch messages');
    return await res.json();
  }

  async createTaskAPI(taskData) {
    const res = await fetch(API_BASE + 'tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(taskData)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail?.message || 'Failed to create task');
    }
    return res.json();
  }

  async updateTaskStatusAPI(taskId, status) {
    const res = await fetch(`${API_BASE}tasks/${taskId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail?.message || 'Failed to update task status');
    }
    return res.json();
  }

  async updateTaskAPI(taskId, data) {
    const res = await fetch(`${API_BASE}tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail?.message || 'Failed to update task');
    }
    return res.json();
  }

  async deleteTaskAPI(taskId) {
    const res = await fetch(`${API_BASE}tasks/${taskId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail?.message || 'Failed to delete task');
    }
    return res.json();
  }

  async sendMessageAPI(messageData) {
    const res = await fetch(API_BASE + 'messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(messageData)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail?.message || 'Failed to send message');
    }
    return res.json();
  }

  // ========== SSE (SERVER-SENT EVENTS) ==========
  
  setupSSE() {
    if (this.sse) {
      this.sse.close();
    }
    
    this.sse = new EventSource('/events');
    
    this.sse.onopen = () => {
      console.log('SSE connected');
      this.reconnectAttempts = 0;
      this.showToast('Real-time connected', 'success');
    };
    
    this.sse.addEventListener('init', (e) => this.handleSSEInit(e));
    this.sse.addEventListener('task_created', (e) => this.handleSSETaskCreated(e));
    this.sse.addEventListener('task_updated', (e) => this.handleSSETaskUpdated(e));
    this.sse.addEventListener('task_deleted', (e) => this.handleSSETaskDeleted(e));
    this.sse.addEventListener('agent_status', (e) => this.handleSSEAgentStatus(e));
    this.sse.addEventListener('heartbeat', (e) => this.handleSSEHeartbeat(e));
    this.sse.addEventListener('message_created', (e) => this.handleSSEMessageCreated(e));
    
    this.sse.onerror = (err) => this.handleSSEError(err);
  }
  
  handleSSEInit(e) {
    const data = JSON.parse(e.data);
    this.agents = data.agents || [];
    this.tasks = data.tasks || [];
    this.renderAll();
  }
  
  handleSSETaskCreated(e) {
    const data = JSON.parse(e.data);
    if (data.task) {
      // SSE sends full task object
      const existingIndex = this.tasks.findIndex(t => t.id === data.task.id);
      if (existingIndex >= 0) {
        this.tasks[existingIndex] = data.task;
      } else {
        this.tasks.push(data.task);
      }
    } else if (data.task_id) {
      // Fallback: fetch the new task
      this.fetchTasks().then(() => this.renderAll());
    }
    this.renderKanban();
    this.renderAgentSidebar();
    this.updateChatTabs();
  }
  
  handleSSETaskUpdated(e) {
    const data = JSON.parse(e.data);
    const index = this.tasks.findIndex(t => t.id === data.task_id || t.id === data.id);
    if (index >= 0 && data.task) {
      this.tasks[index] = { ...this.tasks[index], ...data.task };
    } else if (index >= 0 && data.status) {
      this.tasks[index].status = data.status;
    } else {
      this.fetchTasks().then(() => this.renderAll());
    }
    this.renderKanban();
    this.renderAgentSidebar();
    if (this.elements.taskDetailModal.classList.contains('show')) {
      this.openTaskDetailModal(this.currentDetailTaskId);
    }
  }
  
  handleSSETaskDeleted(e) {
    const data = JSON.parse(e.data);
    this.tasks = this.tasks.filter(t => t.id !== data.task_id);
    this.renderKanban();
    this.renderAgentSidebar();
    this.updateChatTabs();
    // Close detail modal if it was for this task
    if (this.currentDetailTaskId === data.task_id) {
      this.taskDetailModal.hide();
    }
  }
  
  handleSSEAgentStatus(e) {
    const data = JSON.parse(e.data);
    const agent = this.agents.find(a => a.id === data.agent_id);
    if (agent) {
      agent.status = data.status;
      this.renderAgentSidebar();
    }
  }
  
  handleSSEHeartbeat(e) {
    // Heartbeat received - connection alive
    console.debug('SSE heartbeat');
  }
  
  handleSSEMessageCreated(e) {
    const data = JSON.parse(e.data);
    const channel = data.task_ref || 'general';
    if (!this.messages[channel]) this.messages[channel] = [];
    this.messages[channel].push(data);
    if (this.currentChannel === channel) {
      this.renderChatMessages();
    }
    // Update tab badge if not current channel
    this.updateChatTabBadge(channel);
  }
  
  handleSSEError(err) {
    console.error('SSE error:', err);
    this.showToast('Real-time connection lost. Reconnecting...', 'warning');
    this.attemptReconnect();
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.showToast('Failed to reconnect. Please refresh the page.', 'error');
      return;
    }
    
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1);
    
    setTimeout(() => {
      console.log(`SSE reconnect attempt ${this.reconnectAttempts}`);
      this.setupSSE();
    }, delay);
  }

  // ========== RENDERING ==========
  
  renderAll() {
    this.renderAgentSidebar();
    this.renderKanban();
    this.renderChatTabs();
    this.renderChatMessages();
    this.populateAssigneeDropdown();
  }
  
  renderAgentSidebar() {
    const html = this.agents.map(agent => {
      const statusClass = agent.status || 'unknown';
      const activeTasks = agent.active_tasks || 0;
      const isActive = this.selectedAgentFilter === agent.id;
      
      return `
        <div class="agent-item ${isActive ? 'active' : ''}" 
             data-agent-id="${agent.id}" 
             role="listitem"
             tabindex="0"
             aria-pressed="${isActive}">
          <div class="agent-status-dot ${statusClass}" aria-hidden="true"></div>
          <div class="agent-info">
            <div class="agent-name">${this.escapeHtml(agent.name)}</div>
            <div class="agent-role">${this.escapeHtml(agent.role)}</div>
          </div>
          <span class="agent-task-count">${activeTasks}</span>
        </div>
      `;
    }).join('');
    
    this.elements.agentList.innerHTML = html || '<div class="empty-state"><span>No agents</span></div>';
  }
  
  renderKanban() {
    // Filter tasks if agent filter is active
    let tasksToRender = this.tasks;
    if (this.selectedAgentFilter) {
      tasksToRender = this.tasks.filter(t => t.assignee === this.selectedAgentFilter);
    }
    
    this.columns.forEach(col => {
      const columnTasks = tasksToRender.filter(t => t.status === col);
      this.countElements[col].textContent = columnTasks.length;
      
      if (columnTasks.length === 0) {
        this.columnElements[col].innerHTML = `
          <div class="empty-state" style="padding: 1rem;">
            <i class="bi bi-inbox empty-state-icon"></i>
            <span class="small">No tasks</span>
          </div>
        `;
        return;
      }
      
      this.columnElements[col].innerHTML = columnTasks.map(task => this.renderTaskCard(task)).join('');
    });
  }
  
  renderTaskCard(task) {
    const assignee = this.agents.find(a => a.id === task.assignee);
    const priorityLabels = ['Low', 'Medium', 'High', 'Critical'];
    const priorityColors = ['secondary', 'warning', 'info', 'danger'];
    const priority = task.priority ?? 1;
    
    return `
      <div class="task-card" 
           data-task-id="${task.id}" 
           draggable="true"
           role="listitem"
           tabindex="0"
           aria-label="${this.escapeHtml(task.title)}">
        <div class="task-card-header">
          <h4 class="task-title">${this.escapeHtml(task.title)}</h4>
          <span class="badge bg-${priorityColors[priority]} task-priority">
            ${priorityLabels[priority]}
          </span>
        </div>
        ${task.description ? `
          <div class="task-description">${this.escapeHtml(task.description)}</div>
        ` : ''}
        <div class="task-footer">
          <div class="task-assignee">
            ${assignee ? `
              <span class="task-assignee-dot" style="background: ${assignee.color}"></span>
              <span class="task-assignee-name">${this.escapeHtml(assignee.name)}</span>
            ` : '<span class="text-muted small">Unassigned</span>'}
          </div>
          <button class="btn btn-sm btn-outline-danger p-0" 
                  style="width: 24px; height: 24px; line-height: 1;"
                  onclick="event.stopPropagation(); dashboard.deleteTaskFromCard('${task.id}')"
                  aria-label="Delete task">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    `;
  }
  
  renderChatTabs() {
    const generalTab = this.elements.chatTabs.querySelector('[data-channel="general"]');
    this.elements.chatTabs.innerHTML = `
      <button class="chat-tab ${this.currentChannel === 'general' ? 'active' : ''}" 
              data-channel="general" role="tab" 
              aria-selected="${this.currentChannel === 'general'}" 
              aria-controls="panel-general">
        <i class="bi bi-hash me-1"></i> General
      </button>
    `;
    
    // Add task channels
    const tasksWithMessages = [...new Set(Object.keys(this.messages).filter(k => k !== 'general' && this.messages[k].length > 0))];
    tasksWithMessages.forEach(taskRef => {
      const task = this.tasks.find(t => t.id === taskRef);
      const tab = document.createElement('button');
      tab.className = `chat-tab ${this.currentChannel === taskRef ? 'active' : ''}`;
      tab.dataset.channel = taskRef;
      tab.role = 'tab';
      tab.ariaSelected = this.currentChannel === taskRef;
      tab.ariaControls = `panel-${taskRef}`;
      tab.innerHTML = `
        <i class="bi bi-chat-square-text me-1"></i> 
        ${task ? this.escapeHtml(task.title.substring(0, 20)) : taskRef.substring(0, 20)}
        ${taskRef !== this.currentChannel && this.messages[taskRef]?.some(m => !m.read) ? '<span class="badge bg-danger ms-1" style="font-size: 0.6rem;">•</span>' : ''}
      `;
      this.elements.chatTabs.appendChild(tab);
    });
  }
  
  updateChatTabs() {
    const activeChannel = this.currentChannel;
    this.renderChatTabs();
    this.switchChannel(activeChannel, false);
  }
  
  updateChatTabBadge(channel) {
    const tab = this.elements.chatTabs.querySelector(`[data-channel="${channel}"]`);
    if (tab && channel !== this.currentChannel) {
      const hasUnread = this.messages[channel]?.some(m => !m.read);
      let badge = tab.querySelector('.badge');
      if (hasUnread && !badge) {
        badge = document.createElement('span');
        badge.className = 'badge bg-danger ms-1';
        badge.style.fontSize = '0.6rem';
        badge.textContent = '•';
        tab.appendChild(badge);
      } else if (!hasUnread && badge) {
        badge.remove();
      }
    }
  }
  
  async switchChannel(channel, fetchIfEmpty = true) {
    this.currentChannel = channel;
    
    // Update tab active state
    this.elements.chatTabs.querySelectorAll('.chat-tab').forEach(tab => {
      const isActive = tab.dataset.channel === channel;
      tab.classList.toggle('active', isActive);
      tab.setAttribute('aria-selected', isActive);
    });
    
    // Fetch messages if needed
    if (fetchIfEmpty && (!this.messages[channel] || this.messages[channel].length === 0)) {
      try {
        this.messages[channel] = await this.fetchMessages(channel === 'general' ? null : channel);
      } catch (err) {
        console.error('Failed to fetch messages:', err);
        this.messages[channel] = [];
      }
    }
    
    this.renderChatMessages();
    this.elements.chatInputArea.style.display = channel === 'general' ? 'none' : 'block';
  }
  
  renderChatMessages() {
    const messages = this.messages[this.currentChannel] || [];
    
    if (messages.length === 0) {
      this.elements.chatMessages.innerHTML = `
        <div class="empty-state" style="flex: 1;">
          <i class="bi bi-chat-dots empty-state-icon"></i>
          <span>${this.currentChannel === 'general' ? 'No messages yet. Start the conversation!' : 'No messages for this task.'}</span>
        </div>
      `;
      return;
    }
    
    // Sort by created_at ascending
    const sorted = [...messages].sort((a, b) => (a.created_at || 0) - (b.created_at || 0));
    
    this.elements.chatMessages.innerHTML = sorted.map(msg => this.renderChatMessage(msg)).join('');
    
    // Auto-scroll to bottom
    this.elements.chatMessages.scrollTop = this.elements.chatMessages.scrollHeight;
  }
  
  renderChatMessage(msg) {
    const time = new Date((msg.created_at || Date.now()) * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const color = msg.agent_color || '#64748b';
    const name = msg.agent_name || msg.agent_id || 'Unknown';
    const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
    
    return `
      <div class="chat-message" data-message-id="${msg.id}">
        <div class="chat-message-avatar" style="background: ${color}">${this.escapeHtml(initials)}</div>
        <div class="chat-message-content">
          <div class="chat-message-header">
            <span class="chat-message-author" style="color: ${color}">${this.escapeHtml(name)}</span>
            <span class="chat-message-time">${time}</span>
          </div>
          <div class="chat-message-text">${this.escapeHtml(msg.content)}</div>
        </div>
      </div>
    `;
  }

  // ========== MODALS ==========
  
  openCreateTaskModal() {
    this.populateAssigneeDropdown();
    this.createTaskModal.show();
    // Focus title input after modal shown
    this.elements.createTaskModal.addEventListener('shown.bs.modal', () => {
      this.elements.taskTitle.focus();
    }, { once: true });
  }
  
  populateAssigneeDropdown() {
    const currentValue = this.elements.taskAssignee.value;
    this.elements.taskAssignee.innerHTML = '<option value="">Unassigned</option>' +
      this.agents.map(a => `<option value="${a.id}" style="color: ${a.color}">${this.escapeHtml(a.name)} (${this.escapeHtml(a.role)})</option>`).join('');
    this.elements.taskAssignee.value = currentValue;
  }
  
  async handleCreateTask(e) {
    e.preventDefault();
    
    const title = this.elements.taskTitle.value.trim();
    if (!title) {
      this.showToast('Title is required', 'error');
      return;
    }
    
    const taskData = {
      title,
      description: this.elements.taskDescription.value.trim(),
      assignee: this.elements.taskAssignee.value || null,
      priority: parseInt(this.elements.taskPriority.value, 10),
      skills: null,
      model_override: null
    };
    
    this.elements.createTaskSubmit.disabled = true;
    this.elements.createTaskSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Creating...';
    
    try {
      await this.createTaskAPI(taskData);
      this.createTaskModal.hide();
      this.showToast('Task created successfully', 'success');
      // SSE will push the update
    } catch (err) {
      this.showToast(err.message, 'error');
    } finally {
      this.elements.createTaskSubmit.disabled = false;
      this.elements.createTaskSubmit.innerHTML = '<i class="bi bi-plus-lg me-1"></i> Create Task';
    }
  }
  
  resetCreateTaskForm() {
    this.elements.createTaskForm.reset();
    this.elements.taskPriority.value = '1';
  }
  
  openTaskDetailModal(taskId) {
    const task = this.tasks.find(t => t.id === taskId);
    if (!task) return;
    
    this.currentDetailTaskId = taskId;
    const assignee = this.agents.find(a => a.id === task.assignee);
    const priorityLabels = ['Low', 'Medium', 'High', 'Critical'];
    const statusLabels = { triage: 'Triage', todo: 'To Do', ready: 'Ready', running: 'Running', blocked: 'Blocked', done: 'Done' };
    const statusColors = { triage: 'info', todo: 'secondary', ready: 'success', running: 'success', blocked: 'warning', done: 'success' };
    
    this.elements.taskDetailBody.innerHTML = `
      <div class="task-detail-section">
        <div class="task-detail-label">Title</div>
        <div class="task-detail-value">${this.escapeHtml(task.title)}</div>
      </div>
      <div class="task-detail-section">
        <div class="task-detail-label">Description</div>
        <div class="task-detail-value">${this.escapeHtml(task.description || 'No description')}</div>
      </div>
      <div class="task-detail-section">
        <div class="task-detail-label">Status</div>
        <div class="task-detail-value">
          <span class="status-badge status-${task.status}">${statusLabels[task.status] || task.status}</span>
        </div>
      </div>
      <div class="task-detail-section">
        <div class="task-detail-label">Priority</div>
        <div class="task-detail-value">${priorityLabels[task.priority ?? 1]}</div>
      </div>
      <div class="task-detail-section">
        <div class="task-detail-label">Assignee</div>
        <div class="task-detail-value">
          ${assignee ? `
            <span style="display: inline-flex; align-items: center; gap: 0.5rem;">
              <span style="width: 12px; height: 12px; border-radius: 50%; background: ${assignee.color}"></span>
              ${this.escapeHtml(assignee.name)} (${this.escapeHtml(assignee.role)})
            </span>
          ` : '<span class="text-muted">Unassigned</span>'}
        </div>
      </div>
      <div class="task-detail-section">
        <div class="task-detail-label">Created</div>
        <div class="task-detail-value">${task.created_at ? new Date(task.created_at * 1000).toLocaleString() : 'Unknown'}</div>
      </div>
      <hr>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm flex-fill" id="edit-task-btn">
          <i class="bi bi-pencil me-1"></i> Edit Task
        </button>
        <button class="btn btn-outline-secondary btn-sm" id="view-messages-btn" data-task-ref="${task.id}">
          <i class="bi bi-chat me-1"></i> View Messages
        </button>
      </div>
    `;
    
    // Bind edit button
    const editBtn = this.elements.taskDetailBody.querySelector('#edit-task-btn');
    editBtn.addEventListener('click', () => this.openEditTaskModal(task));
    
    // Bind view messages button
    const msgBtn = this.elements.taskDetailBody.querySelector('#view-messages-btn');
    msgBtn.addEventListener('click', () => {
      this.taskDetailModal.hide();
      this.switchChannel(task.id);
      // Scroll chat panel into view on mobile
      this.elements.chatPanel.scrollIntoView({ behavior: 'smooth' });
    });
    
    this.taskDetailModal.show();
  }
  
  openEditTaskModal(task) {
    this.taskDetailModal.hide();
    
    // Populate create task modal with existing data
    this.elements.taskTitle.value = task.title;
    this.elements.taskDescription.value = task.description || '';
    this.elements.taskAssignee.value = task.assignee || '';
    this.elements.taskPriority.value = task.priority ?? 1;
    
    // Change modal to edit mode
    this.elements.createTaskModalLabel.textContent = 'Edit Task';
    this.elements.createTaskSubmit.innerHTML = '<i class="bi bi-check-lg me-1"></i> Save Changes';
    this.elements.createTaskSubmit.dataset.editTaskId = task.id;
    
    this.createTaskModal.show();
  }
  
  async handleDeleteTask() {
    if (!this.currentDetailTaskId) return;
    
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await this.deleteTaskAPI(this.currentDetailTaskId);
      this.taskDetailModal.hide();
      this.showToast('Task deleted', 'success');
      // SSE will push the update
    } catch (err) {
      this.showToast(err.message, 'error');
    }
  }
  
  resetTaskDetailModal() {
    this.currentDetailTaskId = null;
    this.elements.taskDetailBody.innerHTML = '';
    // Reset create modal if it was in edit mode
    this.elements.createTaskModalLabel.textContent = 'Create New Task';
    this.elements.createTaskSubmit.innerHTML = '<i class="bi bi-plus-lg me-1"></i> Create Task';
    delete this.elements.createTaskSubmit.dataset.editTaskId;
  }

  // ========== CHAT ==========
  
  async sendMessage() {
    const content = this.elements.chatInput.value.trim();
    if (!content) return;
    
    // For demo, use first agent as sender (in real app, this would be current user)
    const currentAgent = this.agents[0] || { id: 'user', name: 'User', color: '#00d4aa' };
    
    const messageData = {
      agent_id: currentAgent.id,
      content,
      task_ref: this.currentChannel === 'general' ? null : this.currentChannel,
      agent_name: currentAgent.name,
      agent_color: currentAgent.color
    };
    
    this.elements.chatInput.value = '';
    this.elements.chatInput.style.height = 'auto';
    
    try {
      await this.sendMessageAPI(messageData);
      // SSE will push the message back
    } catch (err) {
      this.showToast(err.message, 'error');
      // Restore input on error
      this.elements.chatInput.value = content;
    }
  }

  // ========== DRAG AND DROP ==========
  
  handleDragStart(e) {
    const card = e.target.closest('.task-card');
    if (!card) return;
    
    this.draggedTaskId = card.dataset.taskId;
    card.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', this.draggedTaskId);
  }
  
  handleDragOver(e, targetStatus) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    const columnEl = this.columnElements[targetStatus];
    if (columnEl && !columnEl.classList.contains('drag-over')) {
      columnEl.classList.add('drag-over');
    }
  }
  
  handleDragLeave(e, targetStatus) {
    const columnEl = this.columnElements[targetStatus];
    if (columnEl) {
      // Only remove if leaving the column entirely
      const rect = columnEl.getBoundingClientRect();
      if (e.clientX < rect.left || e.clientX > rect.right || 
          e.clientY < rect.top || e.clientY > rect.bottom) {
        columnEl.classList.remove('drag-over');
      }
    }
  }
  
  async handleDrop(e, targetStatus) {
    e.preventDefault();
    
    const columnEl = this.columnElements[targetStatus];
    columnEl.classList.remove('drag-over');
    
    const taskId = this.draggedTaskId || e.dataTransfer.getData('text/plain');
    this.draggedTaskId = null;
    
    // Remove dragging class from all cards
    document.querySelectorAll('.task-card.dragging').forEach(c => c.classList.remove('dragging'));
    
    if (!taskId) return;
    
    const task = this.tasks.find(t => t.id === taskId);
    if (!task || task.status === targetStatus) return;
    
    // Optimistic update
    const oldStatus = task.status;
    task.status = targetStatus;
    this.renderKanban();
    
    try {
      await this.updateTaskStatusAPI(taskId, targetStatus);
      this.showToast(`Task moved to ${targetStatus}`, 'success');
    } catch (err) {
      // Revert on failure
      task.status = oldStatus;
      this.renderKanban();
      this.showToast(err.message, 'error');
    }
  }
  
  // Make deleteTaskFromCard globally accessible for inline onclick
  deleteTaskFromCard(taskId) {
    if (!confirm('Delete this task?')) return;
    this.deleteTaskAPI(taskId)
      .then(() => this.showToast('Task deleted', 'success'))
      .catch(err => this.showToast(err.message, 'error'));
  }

  // ========== AGENT FILTER ==========
  
  filterByAgent(agentId) {
    if (this.selectedAgentFilter === agentId) {
      this.selectedAgentFilter = null;
    } else {
      this.selectedAgentFilter = agentId;
    }
    this.renderAgentSidebar();
    this.renderKanban();
  }

  // ========== UI HELPERS ==========
  
  toggleSidebar() {
    this.elements.agentSidebar.classList.toggle('collapsed');
    const icon = this.elements.sidebarCollapse.querySelector('i');
    icon.classList.toggle('bi-chevron-left');
    icon.classList.toggle('bi-chevron-right');
  }
  
  toggleChat() {
    this.elements.chatPanel.classList.toggle('collapsed');
    const icon = this.elements.chatCollapse.querySelector('i');
    icon.classList.toggle('bi-chevron-right');
    icon.classList.toggle('bi-chevron-left');
  }
  
  showLoading(show) {
    if (show) {
      this.columns.forEach(col => {
        this.columnElements[col].innerHTML = `
          <div class="skeleton skeleton-task"></div>
          <div class="skeleton skeleton-task"></div>
          <div class="skeleton skeleton-task"></div>
        `;
      });
      this.elements.agentList.innerHTML = `
        <div class="skeleton skeleton-agent"></div>
        <div class="skeleton skeleton-agent"></div>
        <div class="skeleton skeleton-agent"></div>
        <div class="skeleton skeleton-agent"></div>
        <div class="skeleton skeleton-agent"></div>
      `;
    }
  }
  
  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.role = 'alert';
    toast.ariaLive = 'polite';
    
    const icons = {
      success: 'bi-check-circle-fill',
      error: 'bi-x-circle-fill',
      warning: 'bi-exclamation-triangle-fill',
      info: 'bi-info-circle-fill'
    };
    
    toast.innerHTML = `
      <div class="toast-header">
        <strong class="toast-title"><i class="bi ${icons[type]} me-1"></i>${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
        <button type="button" class="btn-close btn-close-white" onclick="this.parentElement.parentElement.remove()"></button>
      </div>
      <div class="toast-body">${this.escapeHtml(message)}</div>
    `;
    
    this.elements.toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      toast.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }
  
  handleKeyboardShortcuts(e) {
    // Ignore if typing in input/textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) return;
    
    // N - New task
    if (e.key === 'n' || e.key === 'N') {
      e.preventDefault();
      this.openCreateTaskModal();
    }
    
    // / - Focus search (placeholder for future search)
    if (e.key === '/') {
      e.preventDefault();
      // Could focus a search input if we add one
      this.showToast('Search not yet implemented', 'info');
    }
    
    // Escape - Close modals
    if (e.key === 'Escape') {
      if (this.elements.createTaskModal.classList.contains('show')) {
        this.createTaskModal.hide();
      }
      if (this.elements.taskDetailModal.classList.contains('show')) {
        this.taskDetailModal.hide();
      }
    }
    
    // Ctrl+B - Toggle sidebar
    if (e.ctrlKey && e.key === 'b') {
      e.preventDefault();
      this.toggleSidebar();
    }
    
    // Ctrl+Shift+B - Toggle chat
    if (e.ctrlKey && e.shiftKey && e.key === 'B') {
      e.preventDefault();
      this.toggleChat();
    }
  }
  
  escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize dashboard when DOM is ready
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
  dashboard = new MissionControlDashboard();
  // Make globally accessible for inline handlers
  window.dashboard = dashboard;
});
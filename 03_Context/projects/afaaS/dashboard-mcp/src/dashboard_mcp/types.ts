"""Shared types for Dashboard MCP Server."""

export interface AgentRegistration {
  agent_id: string;
  name: string;
  role: string;
  capabilities: string[];
  model: string;
  config?: AgentConfig;
}

export interface AgentConfig {
  model: string;
  temperature: number;
  max_tokens: number;
  system_prompt?: string;
  tools?: string[];
  metadata?: Record<string, any>;
}

export interface AgentInfo extends AgentRegistration {
  status: AgentStatus;
  current_task?: string;
  token_usage: number;
  last_heartbeat?: string;
  registered_at: string;
  updated_at: string;
}

export type AgentStatus = 'healthy' | 'degraded' | 'unhealthy' | 'offline';

export interface TaskCreate {
  title: string;
  body?: string;
  tags?: string[];
  priority?: TaskPriority;
  assignee_role?: string;
  scheduled_at?: string;
}

export interface TaskInfo {
  task_id: string;
  agent_id: string;
  goal: string;
  context: Record<string, any>;
  priority: TaskPriority;
  status: TaskStatus;
  result?: Record<string, any>;
  error?: string;
  logs?: any[];
  created_at: string;
  started_at?: string;
  completed_at?: string;
  updated_at: string;
}

export interface MessageCreate {
  channel_id: string;
  from_agent: string;
  content: string;
  mentions?: string[];
  reply_to?: string;
}

export interface MessageInfo {
  message_id: string;
  channel_id: string;
  from_agent: string;
  content: string;
  mentions?: string[];
  reply_to?: string;
  created_at: string;
  updated_at: string;
}

export interface ChannelInfo {
  channel_id: string;
  name: string;
  description: string;
  members: string[];
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChannelCreate {
  name: string;
  description?: string;
  members?: string[];
}

export interface WSMessage {
  type: EventType;
  payload: Record<string, any>;
  timestamp: string;
  correlation_id?: string;
}

export type EventType =
  | 'agent_status'
  | 'task_update'
  | 'new_message'
  | 'channel_message'
  | 'agent_registered'
  | 'agent_unregistered'
  | 'channel_created'
  | 'kanban_event';

export interface KanbanTask {
  task_id: string;
  title: string;
  body: string;
  status: string;
  assignee?: string;
  priority: string;
  tags: string[];
  scheduled_at?: string;
  created_at: string;
  updated_at: string;
}

export interface KanbanRun {
  run_id: string;
  task_id: string;
  outcome: string;
  summary?: string;
  meta_data?: Record<string, any>;
  started_at: string;
  completed_at?: string;
  elapsed?: number;
}

export interface KanbanEvent {
  event_id: string;
  type: string;
  task_id: string;
  data: Record<string, any>;
  timestamp: string;
}

export interface FleetConfig {
  agents: AgentRegistration[];
  default_channels: string[];
  task_routing?: Record<string, any>;
  kanban_board?: Record<string, any>;
  dispatcher?: Record<string, any>;
}

export interface Config {
  port: number;
  ws_enabled: boolean;
  agentcomms_path: string;
  fleet_config: string;
  channels_dir: string;
  enable_group_chat: boolean;
  default_channels: string[];
  cors_origins: string[];
  auth_token?: string;
  kanban_board: string;
  fleet_config_path: string;
  kanban_dispatcher_enabled: boolean;
}

export interface FleetStatusResponse {
  agents: AgentInfo[];
  total_agents: number;
  healthy_agents: number;
  running_tasks: number;
  total_token_usage: number;
  column_counts: Record<string, number>;
  throughput_today: number;
  assignee_breakdown: Record<string, number>;
}

export interface TaskListResponse {
  tasks: KanbanTask[];
  total: number;
  page: number;
  page_size: number;
}

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type TaskPriority = 'low' | 'normal' | 'high' | 'critical';
// src/types.ts
export interface AgentInfo {
  agent_id: string;
  name: string;
  role: string;
  status: AgentStatus;
  capabilities: string[];
  model: string;
  token_usage: number;
  last_heartbeat?: string;
  current_task?: string;
  config?: Record<string, any>;
  registered_at?: string;
  updated_at?: string;
}

export type AgentStatus = 'healthy' | 'degraded' | 'unhealthy' | 'offline';

export interface DeploymentInfo {
  deployment_id: string;
  agent_id: string;
  goal: string;
  status: DeploymentStatus;
  started_at?: string;
  completed_at?: string;
  logs?: string[];
}

export type DeploymentStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface MetricData {
  timestamp: string;
  cpu: number;
  memory: number;
  token_cost: number;
  latency: number;
}

export interface Alert {
  alert_id: string;
  agent_id: string;
  message: string;
  severity: 'critical' | 'warning' | 'info';
  timestamp: string;
  acknowledged: boolean;
}

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

export interface FleetStatusResponse {
  agents: AgentInfo[];
  total_agents: number;
  healthy_agents: number;
  running_tasks: number;
  total_token_usage: number;
  column_counts?: Record<string, number>;
  throughput_today?: number;
  assignee_breakdown?: Record<string, number>;
}

export interface KanbanColumn {
  id: string;
  name: string;
  wip_limit?: number;
}
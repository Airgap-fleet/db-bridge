// src/mcp-client.ts
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import type { FleetStatusResponse, AgentInfo, KanbanTask, DeploymentInfo, Alert, MetricData } from './types';

export class DashboardMCPClient {
  private client: Client;
  private transport: StreamableHTTPClientTransport;
  private url: string;

  constructor(url: string) {
    this.url = url;
    this.client = new Client({
      name: 'afaaS-dashboard-client',
      version: '0.1.0',
      capabilities: {
        tools: { subscribe: true },
        resources: { subscribe: true },
        prompts: { list: true },
      },
      metadata: {
        protocolVersion: '2026-07-28',
      },
    });

    this.transport = new StreamableHTTPClientTransport(new URL(url), {
      requestInit: {
        headers: {
          'Mcp-Method': 'tools/call',
          'Mcp-Name': 'fleet_status',
          'MCP-Protocol-Version': '2026-07-28',
        },
      },
    });

    this.client.connect(this.transport);
  }

  async callTool(
    name: string,
    arguments_: Record<string, any> = {}
  ): Promise<any> {
    try {
      const result = await this.client.callTool({ name, arguments: arguments_ });
      return result.content;
    } catch (error) {
      console.error(`MCP tool call failed: ${name}`, error);
      throw error;
    }
  }

  async subscribeToResource(uri: string, onUpdate: (data: any) => void): Promise<void> {
    try {
      await this.client.subscribeResource({ uri, onUpdate });
    } catch (error) {
      console.error(`MCP resource subscription failed: ${uri}`, error);
      throw error;
    }
  }

  async getAgentHealth(agentId: string): Promise<any> {
    return this.callTool('agent_health', { agent_id: agentId });
  }

  async startDeployment(deploymentId: string, agentId: string, goal: string): Promise<any> {
    return this.callTool('deployment_start', {
      deployment_id: deploymentId,
      agent_id: agentId,
      goal,
    });
  }

  async getDeploymentStatus(deploymentId: string): Promise<any> {
    return this.callTool('deployment_status', { deployment_id: deploymentId });
  }

  async queryMetrics(metricType: string): Promise<any> {
    return this.callTool('metrics_query', { metric_type: metricType });
  }

  async acknowledgeAlert(alertId: string): Promise<any> {
    return this.callTool('alert_acknowledge', { alert_id: alertId });
  }

  async getFleetStatus(): Promise<FleetStatusResponse> {
    const result = await this.callTool('fleet_status', {});
    return result as unknown as FleetStatusResponse;
  }

  async getFleetAgents(): Promise<AgentInfo[]> {
    const result = await this.callTool('get_fleet_agents', {});
    return result as unknown as AgentInfo[];
  }

  async getTasks(filters?: Record<string, any>): Promise<KanbanTask[]> {
    const result = await this.callTool('list_tasks', filters || {});
    return result as unknown as KanbanTask[];
  }

  async createTask(taskData: Partial<KanbanTask>): Promise<KanbanTask> {
    const result = await this.callTool('create_task', taskData);
    return result as unknown as KanbanTask;
  }

  async close(): Promise<void> {
    await this.client.close();
  }
}
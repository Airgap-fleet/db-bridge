// src/components/AgentDetail.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Drawer } from './ui/drawer';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { DashboardMCPClient } from '../mcp-client';
import { AgentInfo, DeploymentInfo } from '../types';

const client = new DashboardMCPClient('http://localhost:8001/mcp');

export function AgentDetail() {
  const { agentId } = useParams<{ agentId: string }>();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(true);

  const { data: agent, isLoading, error } = useQuery<AgentInfo, Error>({
    queryKey: ['agent', agentId],
    queryFn: async () => {
      if (!agentId) throw new Error('Agent ID required');
      return client.getAgentHealth(agentId);
    },
    enabled: !!agentId,
    refetchInterval: 10000, // Refetch every 10 seconds
  });

  const { data: deployments } = useQuery({
    queryKey: ['agentDeployments', agentId],
    queryFn: async () => {
      if (!agentId) return [];
      // TODO: Fetch deployments for this agent from MCP
      return [];
    },
    enabled: !!agentId,
    refetchInterval: 30000,
  });

  if (!isOpen) {
    navigate('/');
    return null;
  }

  return (
    <Drawer open={isOpen} onOpenChange={setIsOpen}>
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">{agent?.name || agentId}</h2>
          <Badge variant={agent?.status === 'healthy' ? 'default' : 'secondary'}>
            {agent?.status}
          </Badge>
        </div>

        {isLoading ? (
          <div>Loading agent details...</div>
        ) : error ? (
          <div className="text-destructive">Error: {error.message}</div>
        ) : agent ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Agent Info</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Agent ID:</span>
                  <span className="font-mono">{agent.agent_id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Role:</span>
                  <span>{agent.role}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Model:</span>
                  <span>{agent.model}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Token Usage:</span>
                  <span>{agent.token_usage.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Last Heartbeat:</span>
                  <span>{agent.last_heartbeat ? new Date(agent.last_heartbeat).toLocaleString() : 'Never'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Task:</span>
                  <span>{agent.current_task || 'None'}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Capabilities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities?.map((capability, index) => (
                    <Badge key={index} variant="outline">{capability}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle>Recent Deployments</CardTitle>
              </CardHeader>
              <CardContent>
                {deployments?.length ? (
                  <div className="space-y-2">
                    {deployments.map((deployment: DeploymentInfo) => (
                      <div key={deployment.deployment_id} className="flex items-center justify-between p-2 border rounded">
                        <span className="font-mono text-sm">{deployment.deployment_id}</span>
                        <Badge variant={deployment.status === 'completed' ? 'default' : 'secondary'}>
                          {deployment.status}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {deployment.started_at ? new Date(deployment.started_at).toLocaleString() : 'Not started'}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No deployments found</p>
                )}
              </CardContent>
            </Card>
          </div>
        ) : (
          <div>Agent not found</div>
        )}
      </div>
    </Drawer>
  );
}
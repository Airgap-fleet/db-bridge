// src/components/FleetOverview.tsx
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { DashboardMCPClient } from '../mcp-client';
import { AgentInfo, FleetStatusResponse } from '../types';

const client = new DashboardMCPClient('http://localhost:8001/mcp');

export function FleetOverview() {
  const { data: fleetStatus, isLoading, error } = useQuery<FleetStatusResponse, Error>({
    queryKey: ['fleetStatus'],
    queryFn: async () => {
      const result = await client.getFleetStatus();
      return result;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <CardTitle>Loading...</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-muted animate-pulse rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive rounded-lg p-4">
        <p className="text-destructive">Error loading fleet status: {error.message}</p>
      </div>
    );
  }

  const stats = [
    { label: 'Total Agents', value: fleetStatus?.total_agents, icon: '🤖' },
    { label: 'Healthy', value: fleetStatus?.healthy_agents, icon: '✅' },
    { label: 'Running Tasks', value: fleetStatus?.running_tasks, icon: '⚡' },
    { label: 'Token Usage', value: fleetStatus?.total_token_usage, icon: '💰' },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
              <span className="text-2xl">{stat.icon}</span>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stat.value?.toLocaleString() || 'N/A'}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Agent Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {fleetStatus?.agents?.slice(0, 5).map((agent: AgentInfo) => (
              <div key={agent.agent_id} className="flex items-center justify-between p-2 border rounded">
                <div className="flex items-center space-x-3">
                  <span className="font-mono text-sm">{agent.agent_id}</span>
                  <span className="text-sm">{agent.name}</span>
                  <Badge variant={agent.status === 'healthy' ? 'default' : 'secondary'}>
                    {agent.status}
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  {agent.last_heartbeat ? new Date(agent.last_heartbeat).toLocaleString() : 'No heartbeat'}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
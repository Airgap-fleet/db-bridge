// src/components/DeploymentProgress.tsx
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { DashboardMCPClient } from '../mcp-client';
import { DeploymentInfo } from '../types';

const client = new DashboardMCPClient('http://localhost:8001/mcp');

export function DeploymentProgress() {
  const { deploymentId } = useParams<{ deploymentId: string }>();
  const queryClient = useQueryClient();
  const [logs, setLogs] = useState<string[]>([]);

  const { data: deployment, isLoading, error } = useQuery<DeploymentInfo, Error>({
    queryKey: ['deployment', deploymentId],
    queryFn: async () => {
      if (!deploymentId) throw new Error('Deployment ID required');
      return client.getDeploymentStatus(deploymentId);
    },
    enabled: !!deploymentId,
    refetchInterval: 5000, // Poll every 5 seconds
  });

  // Simulate real-time logs
  useEffect(() => {
    if (deploymentId) {
      const interval = setInterval(() => {
        // This would ideally subscribe to real-time logs via SSE/WebSocket
        setLogs(prev => [
          ...prev,
          `${new Date().toLocaleTimeString()} - Monitoring deployment progress...`
        ].slice(-10)); // Keep last 10 logs
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [deploymentId]);

  const handleCancel = async () => {
    if (!deploymentId) return;
    try {
      await client.callTool('deployment_cancel', { deployment_id: deploymentId });
      queryClient.invalidateQueries({ queryKey: ['deployment', deploymentId] });
    } catch (error) {
      console.error('Failed to cancel deployment:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading deployment details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive rounded-lg p-4">
        <p className="text-destructive">Error: {error.message}</p>
      </div>
    );
  }

  if (!deployment) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Deployment not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Deployment: {deployment.deployment_id}</CardTitle>
          <Badge 
            variant={
              deployment.status === 'completed' ? 'default' :
              deployment.status === 'running' ? 'default' :
              deployment.status === 'failed' ? 'destructive' :
              'secondary'
            }
          >
            {deployment.status}
          </Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-sm text-muted-foreground">Agent ID</h4>
              <p className="font-mono">{deployment.agent_id}</p>
            </div>
            <div>
              <h4 className="font-medium text-sm text-muted-foreground">Goal</h4>
              <p className="text-sm">{deployment.goal}</p>
            </div>
            <div>
              <h4 className="font-medium text-sm text-muted-foreground">Started At</h4>
              <p>{deployment.started_at ? new Date(deployment.started_at).toLocaleString() : 'Not started'}</p>
            </div>
            <div>
              <h4 className="font-medium text-sm text-muted-foreground">Completed At</h4>
              <p>{deployment.completed_at ? new Date(deployment.completed_at).toLocaleString() : 'Not completed'}</p>
            </div>
          </div>
          
          {deployment.status === 'running' && (
            <div className="pt-4">
              <Button variant="destructive" onClick={handleCancel}>
                Cancel Deployment
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Logs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-black text-green-400 p-4 rounded font-mono text-sm overflow-auto max-h-96">
            {logs.length ? (
              logs.map((log, index) => (
                <div key={index} className="py-1 border-b border-green-900 last:border-b-0">
                  {log}
                </div>
              ))
            ) : (
              <div className="text-gray-500">No logs available</div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
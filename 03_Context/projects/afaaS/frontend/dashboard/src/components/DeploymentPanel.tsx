// src/components/DeploymentPanel.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { DashboardMCPClient } from '../mcp-client';
import { AgentInfo } from '../types';

const client = new DashboardMCPClient('http://localhost:8001/mcp');

const deploymentSchema = z.object({
  agent_id: z.string().min(1, 'Agent is required'),
  goal: z.string().min(1, 'Goal is required').max(4096, 'Goal too long'),
});

type DeploymentFormData = z.infer<typeof deploymentSchema>;

interface DeploymentPanelProps {
  agents: AgentInfo[];
  onOpenChange: (open: boolean) => void;
  open: boolean;
}

export function DeploymentPanel({ agents, onOpenChange, open }: DeploymentPanelProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [selectedAgent, setSelectedAgent] = useState<AgentInfo | null>(null);

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm<DeploymentFormData>({
    resolver: zodResolver(deploymentSchema),
  });

  const handleAgentChange = (agentId: string) => {
    const agent = agents.find(a => a.agent_id === agentId);
    setSelectedAgent(agent || null);
    setValue('agent_id', agentId);
  };

  const deploymentMutation = useMutation({
    mutationFn: async (data: DeploymentFormData) => {
      // Generate a deployment ID
      const deploymentId = `deploy-${Date.now()}`;
      return client.startDeployment(deploymentId, data.agent_id, data.goal);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['fleetStatus'] });
      onOpenChange(false);
      navigate(`/deployments/${data.deployment_id}`);
    },
  });

  const onSubmit = (data: DeploymentFormData) => {
    deploymentMutation.mutate(data);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Start New Deployment</DialogTitle>
        </DialogHeader>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="agent_id">Agent</Label>
            <Select onValueChange={handleAgentChange} disabled={deploymentMutation.isPending}>
              <SelectTrigger>
                <SelectValue placeholder="Select an agent" />
              </SelectTrigger>
              <SelectContent>
                {agents.map((agent) => (
                  <SelectItem key={agent.agent_id} value={agent.agent_id}>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm">{agent.agent_id}</span>
                      <span className="text-sm">{agent.name}</span>
                      <span className="text-xs text-muted-foreground">({agent.role})</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.agent_id && (
              <p className="text-sm text-destructive">{errors.agent_id.message}</p>
            )}
          </div>

          {selectedAgent && (
            <div className="p-3 bg-muted rounded-lg">
              <div className="text-sm font-medium">{selectedAgent.name}</div>
              <div className="text-xs text-muted-foreground">{selectedAgent.role}</div>
              <div className="text-xs text-muted-foreground">{selectedAgent.model}</div>
              <div className="text-xs text-muted-foreground">Status: {selectedAgent.status}</div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="goal">Goal</Label>
            <Textarea
              id="goal"
              {...register('goal')}
              placeholder="Describe the deployment goal...
              Example: Analyze quarterly sales data and generate quarterly report"
              rows={4}
              disabled={deploymentMutation.isPending}
            />
            {errors.goal && (
              <p className="text-sm text-destructive">{errors.goal.message}</p>
            )}
          </div>

          <div className="flex justify-end space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={deploymentMutation.isPending}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={deploymentMutation.isPending || !selectedAgent}>
              {deploymentMutation.isPending ? 'Starting...' : 'Start Deployment'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
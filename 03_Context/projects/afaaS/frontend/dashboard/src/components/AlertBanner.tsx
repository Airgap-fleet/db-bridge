// src/components/AlertBanner.tsx
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { DashboardMCPClient } from '../mcp-client';

const client = new DashboardMCPClient('http://localhost:8001/mcp');

interface Alert {
  alert_id: string;
  agent_id: string;
  message: string;
  severity: 'critical' | 'warning' | 'info';
  timestamp: string;
  acknowledged: boolean;
}

export function AlertBanner() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  // Fetch alerts every 30 seconds
  const { data: alertsData } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      // TODO: Implement alert fetching from MCP
      return [];
    },
    refetchInterval: 30000,
  });

  const handleAcknowledge = async (alertId: string) => {
    try {
      await client.acknowledgeAlert(alertId);
      setAlerts(current =>
        current.map(alert =>
          alert.alert_id === alertId
            ? { ...alert, acknowledged: true }
            : alert
        )
      );
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged);

  if (unacknowledgedAlerts.length === 0) {
    return null;
  }

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {unacknowledgedAlerts.map((alert) => (
        <div
          key={alert.alert_id}
          className={cn(
            'p-4 rounded-lg shadow-lg border',
            alert.severity === 'critical' && 'bg-red-50 border-red-200',
            alert.severity === 'warning' && 'bg-yellow-50 border-yellow-200',
            alert.severity === 'info' && 'bg-blue-50 border-blue-200'
          )}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <Badge variant={alert.severity === 'critical' ? 'destructive' : 'secondary'}>
                  {alert.severity}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {alert.agent_id}
                </span>
              </div>
              <p className="text-sm font-medium mt-1">{alert.message}</p>
              <p className="text-xs text-muted-foreground mt-1">
                {new Date(alert.timestamp).toLocaleString()}
              </p>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleAcknowledge(alert.alert_id)}
            >
              Acknowledge
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
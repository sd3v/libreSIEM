'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'High' | 'Medium' | 'Low';
  timestamp: string;
  status: 'Active' | 'Acknowledged' | 'Resolved';
  source: string;
}

export function useAlerts() {
  const queryClient = useQueryClient();

  const { data: alerts, isLoading } = useQuery<Alert[]>({
    queryKey: ['alerts'],
    queryFn: async () => {
      const response = await fetch('/api/alerts');
      return response.json();
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { mutate: acknowledgeAlert } = useMutation({
    mutationFn: async (alertId: string) => {
      const response = await fetch('/api/alerts', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: alertId, status: 'Acknowledged' }),
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  const { mutate: resolveAlert } = useMutation({
    mutationFn: async (alertId: string) => {
      const response = await fetch('/api/alerts', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id: alertId, status: 'Resolved' }),
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  const getAlertStats = () => {
    if (!alerts) return { active: 0, acknowledged: 0, resolved: 0 };

    return alerts.reduce(
      (acc, alert) => {
        switch (alert.status) {
          case 'Active':
            acc.active++;
            break;
          case 'Acknowledged':
            acc.acknowledged++;
            break;
          case 'Resolved':
            acc.resolved++;
            break;
        }
        return acc;
      },
      { active: 0, acknowledged: 0, resolved: 0 }
    );
  };

  return {
    alerts,
    isLoading,
    acknowledgeAlert,
    resolveAlert,
    getAlertStats,
  };
}

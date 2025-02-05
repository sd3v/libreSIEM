'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface SecurityEvent {
  id: string;
  timestamp: string;
  event: string;
  severity: 'High' | 'Medium' | 'Low';
  source: string;
  status: 'Open' | 'Investigating' | 'Resolved';
  details: Record<string, any>;
}

interface ThreatData {
  date: string;
  'Malware Detected': number;
  'Suspicious Activities': number;
  'Policy Violations': number;
}

export function useSecurity() {
  const queryClient = useQueryClient();

  const { data: securityData, isLoading } = useQuery({
    queryKey: ['security'],
    queryFn: async () => {
      const response = await fetch('/api/security');
      return response.json();
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: events } = useQuery<SecurityEvent[]>({
    queryKey: ['security', 'events'],
    queryFn: async () => {
      const response = await fetch('/api/security?type=events');
      return response.json();
    },
    refetchInterval: 30000,
  });

  const { data: threats } = useQuery<ThreatData[]>({
    queryKey: ['security', 'threats'],
    queryFn: async () => {
      const response = await fetch('/api/security?type=threats');
      return response.json();
    },
    refetchInterval: 60000, // Refetch every minute
  });

  const { mutate: updateEventStatus } = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: SecurityEvent['status'] }) => {
      const response = await fetch('/api/security', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ id, status }),
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['security'] });
    },
  });

  const getEventStats = () => {
    if (!events) return { open: 0, investigating: 0, resolved: 0 };

    return events.reduce(
      (acc, event) => {
        switch (event.status) {
          case 'Open':
            acc.open++;
            break;
          case 'Investigating':
            acc.investigating++;
            break;
          case 'Resolved':
            acc.resolved++;
            break;
        }
        return acc;
      },
      { open: 0, investigating: 0, resolved: 0 }
    );
  };

  const getThreatTrends = () => {
    if (!threats) return [];
    return threats.map(threat => ({
      date: threat.date,
      malware: threat['Malware Detected'],
      suspicious: threat['Suspicious Activities'],
      violations: threat['Policy Violations'],
    }));
  };

  return {
    events,
    threats,
    isLoading,
    updateEventStatus,
    getEventStats,
    getThreatTrends,
  };
}

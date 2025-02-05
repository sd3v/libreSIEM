'use client';

import { useQuery } from '@tanstack/react-query';

interface LogVolume {
  date: string;
  'Log Volume': number;
  'Error Rate': number;
  'Warning Rate': number;
}

interface SourceDistribution {
  name: string;
  value: number;
}

interface LogLevel {
  name: string;
  value: number;
}

interface QuickStats {
  totalLogsToday: number;
  successRate: number;
  avgResponseTime: number;
  activeSources: number;
}

export function useAnalytics() {
  const { data: logVolume, isLoading: isLoadingVolume } = useQuery<LogVolume[]>({
    queryKey: ['analytics', 'volume'],
    queryFn: async () => {
      const response = await fetch('/api/analytics?type=volume');
      return response.json();
    },
    refetchInterval: 60000, // Refetch every minute
  });

  const { data: sourceDistribution, isLoading: isLoadingSources } = useQuery<SourceDistribution[]>({
    queryKey: ['analytics', 'sources'],
    queryFn: async () => {
      const response = await fetch('/api/analytics?type=sources');
      return response.json();
    },
    refetchInterval: 60000,
  });

  const { data: logLevels, isLoading: isLoadingLevels } = useQuery<LogLevel[]>({
    queryKey: ['analytics', 'levels'],
    queryFn: async () => {
      const response = await fetch('/api/analytics?type=levels');
      return response.json();
    },
    refetchInterval: 60000,
  });

  const { data: quickStats, isLoading: isLoadingStats } = useQuery<QuickStats>({
    queryKey: ['analytics', 'stats'],
    queryFn: async () => {
      const response = await fetch('/api/analytics?type=stats');
      return response.json();
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const getVolumeData = () => {
    if (!logVolume) return [];
    return logVolume.map(item => ({
      date: item.date,
      volume: item['Log Volume'],
      errorRate: item['Error Rate'],
      warningRate: item['Warning Rate'],
    }));
  };

  const getSourceData = () => {
    if (!sourceDistribution) return [];
    return sourceDistribution.map(item => ({
      name: item.name,
      value: item.value,
    }));
  };

  const getLevelData = () => {
    if (!logLevels) return [];
    return logLevels.map(item => ({
      name: item.name,
      value: item.value,
    }));
  };

  return {
    logVolume: getVolumeData(),
    sourceDistribution: getSourceData(),
    logLevels: getLevelData(),
    quickStats,
    isLoading: isLoadingVolume || isLoadingSources || isLoadingLevels || isLoadingStats,
  };
}

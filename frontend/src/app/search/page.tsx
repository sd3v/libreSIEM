'use client';

import { useState } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const sampleLogs = [
  {
    id: 'log1',
    timestamp: '2025-02-05T15:45:00Z',
    source: 'firewall',
    level: 'warning',
    message: 'Blocked suspicious outbound connection to 192.168.1.100:4444',
  },
  {
    id: 'log2',
    timestamp: '2025-02-05T15:44:30Z',
    source: 'auth',
    level: 'error',
    message: 'Failed login attempt for user admin from 10.0.0.5',
  },
  // Add more sample logs
];

const filterOptions = [
  { value: 'all', label: 'All Sources' },
  { value: 'firewall', label: 'Firewall' },
  { value: 'auth', label: 'Authentication' },
  { value: 'ids', label: 'IDS/IPS' },
];

const levelOptions = [
  { value: 'all', label: 'All Levels' },
  { value: 'info', label: 'Info' },
  { value: 'warning', label: 'Warning' },
  { value: 'error', label: 'Error' },
  { value: 'critical', label: 'Critical' },
];

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [timeRange, setTimeRange] = useState('1h');

  const getLevelBadgeColor = (level: string) => {
    const colors = {
      info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
      warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
      error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
      critical: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    };
    return colors[level as keyof typeof colors] || colors.info;
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Log Search</h1>
        <p className="text-muted-foreground">Search and analyze system logs</p>
      </div>

      <div className="bg-card p-6 rounded-lg border border-border">
        <div className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search logs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-muted rounded-md border border-input text-foreground"
              />
              <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
            </div>
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              className="bg-muted px-3 py-2 rounded-md border border-input text-foreground"
            >
              {filterOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              className="bg-muted px-3 py-2 rounded-md border border-input text-foreground"
            >
              {levelOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="bg-muted px-3 py-2 rounded-md border border-input text-foreground"
            >
              <option value="1h">Last Hour</option>
              <option value="24h">Last 24 Hours</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border">
        <div className="p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Search Results</h2>
        </div>
        <div className="divide-y divide-border">
          {sampleLogs.map((log) => (
            <div key={log.id} className="p-4 hover:bg-muted/50">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                    <span className={`px-2 py-1 rounded-md text-xs font-medium ${getLevelBadgeColor(log.level)}`}>
                      {log.level.toUpperCase()}
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      {log.source.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-foreground">{log.message}</p>
                </div>
                <button className="px-3 py-1.5 text-sm bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90">
                  Details
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
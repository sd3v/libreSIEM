'use client';

import { useState } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

// Beispiel-Log-Daten
const mockLogs = [
  {
    id: 'log1',
    timestamp: '2025-02-05 16:34:22',
    source: 'Firewall',
    severity: 'HIGH',
    message: 'Multiple failed login attempts detected from IP 192.168.1.100',
    raw: '{"src_ip":"192.168.1.100","attempts":5,"protocol":"SSH","dst_port":22}',
  },
  {
    id: 'log2',
    timestamp: '2025-02-05 16:33:15',
    source: 'IDS',
    severity: 'MEDIUM',
    message: 'Suspicious outbound connection to known malicious host',
    raw: '{"dst_ip":"10.0.0.55","connection_type":"TCP","flags":"SYN"}',
  },
  // ... weitere Logs
];

// Beispiel-Statistiken
const stats = [
  { name: 'Events/sec', value: '1,234', trend: '+5%' },
  { name: 'Alerts (24h)', value: '47', trend: '-12%' },
  { name: 'Failed Logins', value: '23', trend: '+2' },
  { name: 'System Load', value: '78%', trend: '+5%' },
];

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [timeRange, setTimeRange] = useState('15m');
  
  return (
    <div className="min-h-screen bg-background">
      {/* Suchleiste */}
      <div className="border-b border-border sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center space-x-4 p-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder='source="firewall" severity="HIGH" | stats count by src_ip'
              className="w-full bg-muted px-4 py-2 pl-10 rounded-md border border-input ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <MagnifyingGlassIcon className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
          </div>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-muted px-4 py-2 rounded-md border border-input ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            <option value="15m">Last 15 minutes</option>
            <option value="1h">Last 1 hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
          </select>
        </div>
      </div>

      {/* Statistik-Panel */}
      <div className="grid grid-cols-4 gap-4 p-4">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-card p-4 rounded-lg border border-border">
            <div className="text-sm text-muted-foreground">{stat.name}</div>
            <div className="mt-1 flex items-baseline justify-between">
              <div className="text-2xl font-semibold text-card-foreground">{stat.value}</div>
              <div className={`text-sm ${stat.trend.startsWith('+') ? 'text-green-500 dark:text-green-400' : 'text-red-500 dark:text-red-400'}`}>
                {stat.trend}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Log-Tabelle */}
      <div className="p-4">
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-border">
              <thead className="bg-muted">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Source
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Severity
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Message
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border bg-card">
                {mockLogs.map((log) => (
                  <tr 
                    key={log.id} 
                    className="hover:bg-muted/50 cursor-pointer group"
                    onClick={() => console.log('Show raw log:', log.raw)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-card-foreground">
                      {log.timestamp}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-card-foreground">
                      {log.source}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        log.severity === 'HIGH' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                        log.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                        'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      }`}>
                        {log.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-card-foreground">
                      {log.message}
                      <div className="hidden group-hover:block mt-2 text-xs text-muted-foreground font-mono">
                        {log.raw}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

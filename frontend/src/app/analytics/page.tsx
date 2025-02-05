'use client';

import { useState } from 'react';

const timeRanges = [
  { value: '24h', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
  { value: '90d', label: 'Last 90 Days' },
];

const logData = [
  {
    date: '2024-02-01',
    'Total Logs': 12453,
    'Error Logs': 234,
    'Warning Logs': 543,
    'Info Logs': 11676,
  },
  {
    date: '2024-02-02',
    'Total Logs': 13567,
    'Error Logs': 345,
    'Warning Logs': 654,
    'Info Logs': 12568,
  },
  // Add more sample data
];

const sourceDistribution = [
  { source: 'Apache', value: 4563 },
  { source: 'MySQL', value: 3421 },
  { source: 'System', value: 2345 },
  { source: 'Application', value: 5678 },
  { source: 'Security', value: 3456 },
];

const severityDistribution = [
  { name: 'Error', value: 234 },
  { name: 'Warning', value: 543 },
  { name: 'Info', value: 11676 },
];

export default function AnalyticsPage() {
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Log Analytics</h1>
          <p className="text-muted-foreground">Analyze and visualize log data across your infrastructure</p>
        </div>
        <div className="w-48">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="w-full bg-muted px-4 py-2 rounded-md border border-input ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {timeRanges.map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="col-span-1 lg:col-span-2">
          <div className="bg-card p-6 rounded-lg border border-border">
            <h2 className="text-lg font-semibold text-card-foreground">Log Volume Trends</h2>
            <div className="h-[300px] mt-4">
              {/* LineChart component would go here */}
            </div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Log Severity Distribution</h2>
          <div className="h-[300px] mt-4">
            {/* DonutChart component would go here */}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Log Sources</h2>
          <div className="h-[300px] mt-4">
            {/* BarChart component would go here */}
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Top Log Patterns</h2>
          <div className="mt-6 space-y-4">
            {sourceDistribution.map((source) => (
              <div key={source.source} className="flex justify-between items-center py-2 border-b border-border last:border-0">
                <span className="text-card-foreground">{source.source}</span>
                <span className="text-muted-foreground">{source.value.toLocaleString()} logs</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import { Card, Title, Text, Grid, Col, LineChart, BarChart, DonutChart, Select, SelectItem } from '@tremor/react';
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <Title>Log Analytics</Title>
          <Text>Analyze and visualize log data across your infrastructure</Text>
        </div>
        <div className="w-48">
          <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
            {timeRanges.map((range) => (
              <SelectItem key={range.value} value={range.value}>
                {range.label}
              </SelectItem>
            ))}
          </Select>
        </div>
      </div>

      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-6">
        <Col numColSpan={1} numColSpanLg={2}>
          <Card>
            <Title>Log Volume Trends</Title>
            <LineChart
              className="mt-6"
              data={logData}
              index="date"
              categories={['Total Logs', 'Error Logs', 'Warning Logs', 'Info Logs']}
              colors={['blue', 'red', 'yellow', 'green']}
              yAxisWidth={48}
            />
          </Card>
        </Col>

        <Card>
          <Title>Log Severity Distribution</Title>
          <DonutChart
            className="mt-6"
            data={severityDistribution}
            category="value"
            index="name"
            colors={['red', 'yellow', 'green']}
          />
        </Card>
      </Grid>

      <Grid numItems={1} numItemsSm={2} className="gap-6">
        <Card>
          <Title>Log Sources</Title>
          <BarChart
            className="mt-6"
            data={sourceDistribution}
            index="source"
            categories={['value']}
            colors={['blue']}
            yAxisWidth={48}
          />
        </Card>

        <Card>
          <Title>Top Log Patterns</Title>
          <div className="mt-6 space-y-4">
            {sourceDistribution.map((source) => (
              <div key={source.source} className="flex justify-between items-center">
                <Text>{source.source}</Text>
                <Text>{source.value.toLocaleString()} logs</Text>
              </div>
            ))}
          </div>
        </Card>
      </Grid>
    </div>
  );
}

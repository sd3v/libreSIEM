'use client';

import { Card, Title, Text, Grid, Col, LineChart, BarChart, Flex, Badge } from '@tremor/react';
import { useState } from 'react';

const alertData = [
  {
    date: '2024-02-01',
    'Critical Alerts': 2,
    'High Alerts': 5,
    'Medium Alerts': 8,
    'Low Alerts': 12,
  },
  {
    date: '2024-02-02',
    'Critical Alerts': 1,
    'High Alerts': 4,
    'Medium Alerts': 7,
    'Low Alerts': 10,
  },
  // Add more sample data here
];

const recentAlerts = [
  {
    id: 'alert-1',
    severity: 'critical',
    title: 'Potential Data Breach Detected',
    description: 'Multiple failed login attempts from unknown IP',
    timestamp: '2024-02-05T12:30:00Z',
  },
  {
    id: 'alert-2',
    severity: 'high',
    title: 'Unusual Network Activity',
    description: 'High outbound traffic detected on port 445',
    timestamp: '2024-02-05T12:25:00Z',
  },
  // Add more alerts
];

const getSeverityColor = (severity: string) => {
  const colors = {
    critical: 'red',
    high: 'orange',
    medium: 'yellow',
    low: 'green',
  };
  return colors[severity as keyof typeof colors] || 'gray';
};

export default function AlertsPage() {
  const [selectedAlert, setSelectedAlert] = useState<typeof recentAlerts[0] | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <Title>Security Alerts</Title>
        <Text>Monitor and manage security alerts across your infrastructure</Text>
      </div>

      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-6">
        <Col numColSpan={1} numColSpanLg={2}>
          <Card>
            <Title>Alert Trends</Title>
            <LineChart
              className="mt-6"
              data={alertData}
              index="date"
              categories={['Critical Alerts', 'High Alerts', 'Medium Alerts', 'Low Alerts']}
              colors={['red', 'orange', 'yellow', 'green']}
              yAxisWidth={40}
            />
          </Card>
        </Col>

        <Card>
          <Title>Alert Distribution</Title>
          <BarChart
            className="mt-6"
            data={alertData}
            index="date"
            categories={['Critical Alerts', 'High Alerts', 'Medium Alerts', 'Low Alerts']}
            colors={['red', 'orange', 'yellow', 'green']}
            yAxisWidth={40}
          />
        </Card>
      </Grid>

      <Card>
        <Title>Recent Alerts</Title>
        <div className="mt-6 space-y-4">
          {recentAlerts.map((alert) => (
            <div
              key={alert.id}
              className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
              onClick={() => setSelectedAlert(alert)}
            >
              <Flex>
                <div>
                  <Badge color={getSeverityColor(alert.severity)} size="xs">
                    {alert.severity.toUpperCase()}
                  </Badge>
                  <Text className="font-medium mt-1">{alert.title}</Text>
                  <Text className="text-sm text-gray-500">{alert.description}</Text>
                </div>
                <Text className="text-sm text-gray-500">
                  {new Date(alert.timestamp).toLocaleString()}
                </Text>
              </Flex>
            </div>
          ))}
        </div>
      </Card>

      {selectedAlert && (
        <Card>
          <Title>Alert Details</Title>
          <div className="mt-4">
            <Badge color={getSeverityColor(selectedAlert.severity)} size="xs">
              {selectedAlert.severity.toUpperCase()}
            </Badge>
            <Text className="font-medium mt-2">{selectedAlert.title}</Text>
            <Text className="text-gray-500 mt-1">{selectedAlert.description}</Text>
            <Text className="text-sm text-gray-500 mt-4">
              Detected at: {new Date(selectedAlert.timestamp).toLocaleString()}
            </Text>
          </div>
        </Card>
      )}
    </div>
  );
}

'use client';

import { Card, Title, Text, Grid, Col, LineChart, BarChart, Metric, Flex, Badge, Button } from '@tremor/react';
import { ShieldCheckIcon, ShieldExclamationIcon, BellAlertIcon } from '@heroicons/react/24/solid';

const securityScore = 85;
const activeThreats = 3;
const activeAlerts = 12;

const threatData = [
  {
    date: '2024-02-01',
    'Malware Detected': 2,
    'Suspicious Activity': 5,
    'Policy Violations': 8,
  },
  {
    date: '2024-02-02',
    'Malware Detected': 1,
    'Suspicious Activity': 4,
    'Policy Violations': 6,
  },
  // Add more sample data
];

const recentThreats = [
  {
    id: 'threat-1',
    type: 'malware',
    title: 'Ransomware Attempt Blocked',
    description: 'Attempted encryption of system files detected and blocked',
    timestamp: '2024-02-05T12:30:00Z',
    status: 'blocked',
  },
  {
    id: 'threat-2',
    type: 'suspicious',
    title: 'Unusual Admin Activity',
    description: 'Multiple privilege escalation attempts detected',
    timestamp: '2024-02-05T12:25:00Z',
    status: 'investigating',
  },
  // Add more threats
];

const getThreatColor = (type: string) => {
  const colors = {
    malware: 'red',
    suspicious: 'orange',
    policy: 'yellow',
  };
  return colors[type as keyof typeof colors] || 'gray';
};

const getStatusColor = (status: string) => {
  const colors = {
    blocked: 'green',
    investigating: 'orange',
    resolved: 'blue',
  };
  return colors[status as keyof typeof colors] || 'gray';
};

export default function SecurityPage() {
  return (
    <div className="space-y-6">
      <div>
        <Title>Security Overview</Title>
        <Text>Monitor and respond to security threats across your infrastructure</Text>
      </div>

      <Grid numItems={1} numItemsSm={2} numItemsLg={3} className="gap-6">
        <Card decoration="top" decorationColor={securityScore >= 80 ? 'green' : 'red'}>
          <Flex>
            <div>
              <Text>Security Score</Text>
              <Metric>{securityScore}%</Metric>
            </div>
            <ShieldCheckIcon className="w-8 h-8 text-green-500" />
          </Flex>
        </Card>

        <Card decoration="top" decorationColor="red">
          <Flex>
            <div>
              <Text>Active Threats</Text>
              <Metric>{activeThreats}</Metric>
            </div>
            <ShieldExclamationIcon className="w-8 h-8 text-red-500" />
          </Flex>
        </Card>

        <Card decoration="top" decorationColor="orange">
          <Flex>
            <div>
              <Text>Active Alerts</Text>
              <Metric>{activeAlerts}</Metric>
            </div>
            <BellAlertIcon className="w-8 h-8 text-orange-500" />
          </Flex>
        </Card>
      </Grid>

      <Grid numItems={1} numItemsSm={2} className="gap-6">
        <Col numColSpan={1} numColSpanLg={2}>
          <Card>
            <Title>Threat Activity</Title>
            <LineChart
              className="mt-6"
              data={threatData}
              index="date"
              categories={['Malware Detected', 'Suspicious Activity', 'Policy Violations']}
              colors={['red', 'orange', 'yellow']}
              yAxisWidth={40}
            />
          </Card>
        </Col>
      </Grid>

      <Card>
        <Title>Recent Threats</Title>
        <div className="mt-6 space-y-4">
          {recentThreats.map((threat) => (
            <div key={threat.id} className="p-4 border rounded-lg">
              <Flex>
                <div>
                  <div className="flex space-x-2">
                    <Badge color={getThreatColor(threat.type)} size="xs">
                      {threat.type.toUpperCase()}
                    </Badge>
                    <Badge color={getStatusColor(threat.status)} size="xs">
                      {threat.status.toUpperCase()}
                    </Badge>
                  </div>
                  <Text className="font-medium mt-1">{threat.title}</Text>
                  <Text className="text-sm text-gray-500">{threat.description}</Text>
                </div>
                <Button size="xs" variant="secondary">
                  Investigate
                </Button>
              </Flex>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

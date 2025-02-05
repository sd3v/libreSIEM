"use client";

import { Card, Title, Text, TabGroup, TabList, Tab, TabPanels, TabPanel, AreaChart, BarChart, Color } from "@tremor/react";
import { ShieldCheckIcon, ShieldExclamationIcon, ClockIcon } from "@heroicons/react/24/outline";

const securityEvents = [
  {
    timestamp: "2024-02-05 12:30",
    event: "Failed login attempt",
    severity: "High",
    source: "192.168.1.100",
    status: "Open",
  },
  {
    timestamp: "2024-02-05 12:25",
    event: "Firewall rule violation",
    severity: "Medium",
    source: "192.168.1.150",
    status: "Investigating",
  },
  {
    timestamp: "2024-02-05 12:20",
    event: "New user account created",
    severity: "Low",
    source: "Internal",
    status: "Resolved",
  },
];

const threatData = [
  {
    date: "2024-02-01",
    "Malware Detected": 23,
    "Suspicious Activities": 45,
    "Policy Violations": 20,
  },
  {
    date: "2024-02-02",
    "Malware Detected": 12,
    "Suspicious Activities": 54,
    "Policy Violations": 32,
  },
  // Add more data points
];

export default function SecurityPage() {
  return (
    <div className="space-y-6 p-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <Title>Security Operations</Title>
          <Text>Monitor and respond to security incidents</Text>
        </div>
      </div>

      {/* Security Overview Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
              <ShieldCheckIcon className="h-6 w-6 text-green-700 dark:text-green-300" />
            </div>
            <div>
              <Text>System Status</Text>
              <Title className="text-green-700 dark:text-green-300">Secure</Title>
            </div>
          </div>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
              <ShieldExclamationIcon className="h-6 w-6 text-yellow-700 dark:text-yellow-300" />
            </div>
            <div>
              <Text>Active Threats</Text>
              <Title className="text-yellow-700 dark:text-yellow-300">3</Title>
            </div>
          </div>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
              <ClockIcon className="h-6 w-6 text-blue-700 dark:text-blue-300" />
            </div>
            <div>
              <Text>Last Scan</Text>
              <Title className="text-blue-700 dark:text-blue-300">5m ago</Title>
            </div>
          </div>
        </Card>
      </div>

      <TabGroup>
        <TabList>
          <Tab>Incidents</Tab>
          <Tab>Threat Analytics</Tab>
          <Tab>Compliance</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Security Incidents</Title>
                <div className="mt-4">
                  {securityEvents.map((event, index) => (
                    <div
                      key={index}
                      className="mb-4 flex items-center justify-between rounded-lg border p-4 transition-all duration-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <div className="space-y-1">
                        <Text className="font-medium">{event.event}</Text>
                        <Text className="text-sm text-gray-500">
                          {event.timestamp} • Source: {event.source}
                        </Text>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span
                          className={`rounded-full px-3 py-1 text-sm ${
                            event.severity === "High"
                              ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                              : event.severity === "Medium"
                              ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                              : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                          }`}
                        >
                          {event.severity}
                        </span>
                        <span
                          className={`rounded-full px-3 py-1 text-sm ${
                            event.status === "Open"
                              ? "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
                              : event.status === "Investigating"
                              ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                              : "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
                          }`}
                        >
                          {event.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Threat Trends</Title>
                <AreaChart
                  className="mt-4 h-72"
                  data={threatData}
                  index="date"
                  categories={["Malware Detected", "Suspicious Activities", "Policy Violations"]}
                  colors={["red", "amber", "blue"]}
                  valueFormatter={(number) => Intl.NumberFormat("en-US").format(number)}
                />
              </Card>

              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Attack Sources</Title>
                <BarChart
                  className="mt-4 h-72"
                  data={[
                    { source: "External IPs", attacks: 234 },
                    { source: "Internal Network", attacks: 123 },
                    { source: "Web Applications", attacks: 321 },
                    { source: "Email", attacks: 89 },
                  ]}
                  index="source"
                  categories={["attacks"]}
                  colors={["red"]}
                  valueFormatter={(number) => Intl.NumberFormat("en-US").format(number)}
                />
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Compliance Status</Title>
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <div className="rounded-lg bg-green-50 p-4 dark:bg-green-900">
                    <Text>GDPR Compliance</Text>
                    <Title className="mt-2">98%</Title>
                  </div>
                  <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900">
                    <Text>ISO 27001</Text>
                    <Title className="mt-2">100%</Title>
                  </div>
                  <div className="rounded-lg bg-purple-50 p-4 dark:bg-purple-900">
                    <Text>SOC 2</Text>
                    <Title className="mt-2">95%</Title>
                  </div>
                  <div className="rounded-lg bg-yellow-50 p-4 dark:bg-yellow-900">
                    <Text>PCI DSS</Text>
                    <Title className="mt-2">92%</Title>
                  </div>
                </div>
              </Card>
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
}

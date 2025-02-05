"use client";

import { Card, Title, Text, Tab, TabList, TabGroup, TabPanel, TabPanels } from "@tremor/react";
import { BarChart, LineChart } from "@tremor/react";

const logData = [
  {
    date: "2024-02-01",
    "Total Logs": 234,
    "Error Logs": 13,
    "Warning Logs": 45,
  },
  {
    date: "2024-02-02",
    "Total Logs": 245,
    "Error Logs": 15,
    "Warning Logs": 52,
  },
  // Add more sample data here
];

const sourceData = [
  {
    source: "Apache",
    logs: 1234,
  },
  {
    source: "Syslog",
    logs: 856,
  },
  {
    source: "Application",
    logs: 543,
  },
];

export default function Home() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Title>Dashboard</Title>
          <Text>Monitor your system&apos;s health and security</Text>
        </div>
      </div>

      <TabGroup>
        <TabList className="mt-8">
          <Tab>Overview</Tab>
          <Tab>Log Analysis</Tab>
          <Tab>Security</Tab>
        </TabList>
        <TabPanels>
          <TabPanel>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              {/* Log Volume Trends */}
              <Card>
                <Title>Log Volume Trends</Title>
                <LineChart
                  className="mt-4 h-72"
                  data={logData}
                  index="date"
                  categories={["Total Logs", "Error Logs", "Warning Logs"]}
                  colors={["blue", "red", "yellow"]}
                  yAxisWidth={40}
                />
              </Card>

              {/* Log Sources Distribution */}
              <Card>
                <Title>Log Sources Distribution</Title>
                <BarChart
                  className="mt-4 h-72"
                  data={sourceData}
                  index="source"
                  categories={["logs"]}
                  colors={["blue"]}
                  yAxisWidth={40}
                />
              </Card>

              {/* Recent Security Events */}
              <Card>
                <Title>Recent Security Events</Title>
                <div className="mt-4">
                  <div className="space-y-2">
                    {[
                      "Failed login attempt from IP 192.168.1.100",
                      "Firewall rule violation detected",
                      "New user account created",
                    ].map((event, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between rounded-lg border p-3"
                      >
                        <Text>{event}</Text>
                        <Text className="text-gray-500">2m ago</Text>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>

              {/* System Health */}
              <Card>
                <Title>System Health</Title>
                <div className="mt-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <Text>CPU Usage</Text>
                    <Text>45%</Text>
                  </div>
                  <div className="h-2 rounded-full bg-gray-200">
                    <div
                      className="h-2 rounded-full bg-green-500"
                      style={{ width: "45%" }}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Text>Memory Usage</Text>
                    <Text>68%</Text>
                  </div>
                  <div className="h-2 rounded-full bg-gray-200">
                    <div
                      className="h-2 rounded-full bg-yellow-500"
                      style={{ width: "68%" }}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Text>Disk Usage</Text>
                    <Text>23%</Text>
                  </div>
                  <div className="h-2 rounded-full bg-gray-200">
                    <div
                      className="h-2 rounded-full bg-green-500"
                      style={{ width: "23%" }}
                    />
                  </div>
                </div>
              </Card>
            </div>
          </TabPanel>
          <TabPanel>
            <div className="mt-6">
              <Card>
                <Title>Log Analysis</Title>
                <Text>Coming soon...</Text>
              </Card>
            </div>
          </TabPanel>
          <TabPanel>
            <div className="mt-6">
              <Card>
                <Title>Security Overview</Title>
                <Text>Coming soon...</Text>
              </Card>
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
}

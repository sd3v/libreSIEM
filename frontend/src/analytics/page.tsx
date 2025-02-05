"use client";

import { Card, Title, Text, TabGroup, TabList, Tab, TabPanels, TabPanel, AreaChart, DonutChart, BarList } from "@tremor/react";
import { useState } from "react";

// Sample data - replace with real API data later
const chartdata = [
  {
    date: "Jan 22",
    "Log Volume": 2890,
    "Error Rate": 12,
    "Warning Rate": 43,
  },
  {
    date: "Feb 22",
    "Log Volume": 3200,
    "Error Rate": 15,
    "Warning Rate": 38,
  },
  // Add more data points
];

const sourceData = [
  { name: "Apache", value: 456 },
  { name: "Nginx", value: 351 },
  { name: "MySQL", value: 271 },
  { name: "PostgreSQL", value: 191 },
  { name: "MongoDB", value: 91 },
];

const logLevels = [
  { name: "ERROR", value: 89 },
  { name: "WARNING", value: 156 },
  { name: "INFO", value: 345 },
  { name: "DEBUG", value: 190 },
];

export default function AnalyticsPage() {
  const [selectedView, setSelectedView] = useState("1");

  return (
    <div className="space-y-6 p-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <Title>Analytics Dashboard</Title>
          <Text>Comprehensive log analysis and insights</Text>
        </div>
      </div>

      <TabGroup className="mt-6">
        <TabList>
          <Tab>Overview</Tab>
          <Tab>Log Analysis</Tab>
          <Tab>Performance</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <div className="mt-6 grid gap-6 md:grid-cols-2">
              {/* Log Volume Trends */}
              <Card className="transition-transform hover:scale-[1.02]">
                <Title>Log Volume Trends</Title>
                <AreaChart
                  className="mt-4 h-72"
                  data={chartdata}
                  index="date"
                  categories={["Log Volume", "Error Rate", "Warning Rate"]}
                  colors={["blue", "red", "yellow"]}
                  valueFormatter={(number) => Intl.NumberFormat("en-US").format(number)}
                />
              </Card>

              {/* Log Source Distribution */}
              <Card className="transition-transform hover:scale-[1.02]">
                <Title>Log Source Distribution</Title>
                <DonutChart
                  className="mt-4 h-72"
                  data={sourceData}
                  category="value"
                  index="name"
                  valueFormatter={(number) => Intl.NumberFormat("en-US").format(number)}
                  colors={["blue", "cyan", "indigo", "violet", "fuchsia"]}
                />
              </Card>

              {/* Log Levels */}
              <Card className="transition-transform hover:scale-[1.02]">
                <Title>Log Levels</Title>
                <BarList
                  data={logLevels}
                  className="mt-4"
                  valueFormatter={(number) => Intl.NumberFormat("en-US").format(number)}
                />
              </Card>

              {/* Quick Stats */}
              <Card className="transition-transform hover:scale-[1.02]">
                <Title>Quick Stats</Title>
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900">
                    <Text>Total Logs Today</Text>
                    <Title className="mt-2">23,456</Title>
                  </div>
                  <div className="rounded-lg bg-green-50 p-4 dark:bg-green-900">
                    <Text>Success Rate</Text>
                    <Title className="mt-2">98.2%</Title>
                  </div>
                  <div className="rounded-lg bg-yellow-50 p-4 dark:bg-yellow-900">
                    <Text>Avg. Response Time</Text>
                    <Title className="mt-2">235ms</Title>
                  </div>
                  <div className="rounded-lg bg-purple-50 p-4 dark:bg-purple-900">
                    <Text>Active Sources</Text>
                    <Title className="mt-2">12</Title>
                  </div>
                </div>
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Advanced Log Analysis</Title>
                <Text>Coming soon with powerful search and filtering capabilities</Text>
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>System Performance</Title>
                <Text>Coming soon with detailed performance metrics</Text>
              </Card>
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
}

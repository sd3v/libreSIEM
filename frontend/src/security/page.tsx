"use client";

import { Card, Title, Text, TabGroup, TabList, Tab, TabPanels, TabPanel, Badge, Button, AreaChart, BarChart } from "@tremor/react";
import { ShieldCheckIcon, ShieldExclamationIcon, ClockIcon } from "@heroicons/react/24/outline";
import { useSecurity } from "../hooks/useSecurity";

export default function SecurityPage() {
  const { events, threats, isLoading, updateEventStatus, getEventStats, getThreatTrends } = useSecurity();
  const stats = getEventStats();
  const threatTrends = getThreatTrends();

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <Title>Loading security data...</Title>
          <Text>Please wait while we fetch the latest security information</Text>
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-6 p-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <Title>Security Overview</Title>
          <Text>Monitor and manage security events</Text>
        </div>
        <Button
          icon={ShieldCheckIcon}
          className="bg-blue-500 text-white hover:bg-blue-600"
        >
          Run Security Scan
        </Button>
      </div>

      {/* Security Overview Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-red-100 p-3 dark:bg-red-900">
              <ShieldExclamationIcon className="h-6 w-6 text-red-700 dark:text-red-300" />
            </div>
            <div>
              <Text>Open Events</Text>
              <Title className="text-red-700 dark:text-red-300">{stats.open}</Title>
            </div>
          </div>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
              <ClockIcon className="h-6 w-6 text-yellow-700 dark:text-yellow-300" />
            </div>
            <div>
              <Text>Investigating</Text>
              <Title className="text-yellow-700 dark:text-yellow-300">{stats.investigating}</Title>
            </div>
          </div>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
              <ShieldCheckIcon className="h-6 w-6 text-green-700 dark:text-green-300" />
            </div>
            <div>
              <Text>Resolved Today</Text>
              <Title className="text-green-700 dark:text-green-300">{stats.resolved}</Title>
            </div>
          </div>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-gray-100 p-3 dark:bg-gray-900">
              <ShieldCheckIcon className="h-6 w-6 text-gray-700 dark:text-gray-300" />
            </div>
            <div>
              <Text>Total Events</Text>
              <Title className="text-gray-700 dark:text-gray-300">
                {stats.open + stats.investigating + stats.resolved}
              </Title>
            </div>
          </div>
        </Card>
      </div>

      <TabGroup>
        <TabList>
          <Tab>Security Events</Tab>
          <Tab>Threat Analytics</Tab>
          <Tab>Compliance</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <div className="space-y-4">
                  {events?.map((event) => (
                    <div
                      key={event.id}
                      className="flex items-center justify-between rounded-lg border p-4 transition-all duration-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Text className="font-medium">{event.event}</Text>
                          <Badge
                            color={
                              event.severity === "High"
                                ? "red"
                                : event.severity === "Medium"
                                ? "yellow"
                                : "green"
                            }
                          >
                            {event.severity}
                          </Badge>
                          <Badge
                            color={
                              event.status === "Open"
                                ? "red"
                                : event.status === "Investigating"
                                ? "yellow"
                                : "green"
                            }
                          >
                            {event.status}
                          </Badge>
                        </div>
                        <Text className="text-sm text-gray-500">
                          Source: {event.source}
                        </Text>
                        <Text className="text-xs text-gray-400">
                          {event.timestamp}
                        </Text>
                      </div>
                      <div className="flex space-x-2">
                        {event.status === "Open" && (
                          <Button
                            size="xs"
                            variant="secondary"
                            className="text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                            onClick={() => updateEventStatus({ id: event.id, status: "Investigating" })}
                          >
                            Investigate
                          </Button>
                        )}
                        {event.status === "Investigating" && (
                          <Button
                            size="xs"
                            variant="secondary"
                            className="text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                            onClick={() => updateEventStatus({ id: event.id, status: "Resolved" })}
                          >
                            Resolve
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Threat Trends</Title>
                <Text>30-day overview of security threats</Text>
                <AreaChart
                  className="mt-4 h-72"
                  data={threatTrends}
                  index="date"
                  categories={["malware", "suspicious", "violations"]}
                  colors={["red", "amber", "blue"]}
                />
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Compliance Status</Title>
                <Text>Coming soon with detailed compliance reporting</Text>
              </Card>
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
}

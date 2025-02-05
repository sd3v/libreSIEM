"use client";

import { Card, Title, Text, TabGroup, TabList, Tab, TabPanels, TabPanel, Badge, Button } from "@tremor/react";
import { BellIcon, BellSlashIcon, CheckCircleIcon } from "@heroicons/react/24/outline";
import { useAlerts } from "../hooks/useAlerts";





export default function AlertsPage() {
  const { alerts, isLoading, acknowledgeAlert, resolveAlert, getAlertStats } = useAlerts();
  const stats = getAlertStats();

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <Title>Loading alerts...</Title>
          <Text>Please wait while we fetch the latest alerts</Text>
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-6 p-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <Title>Alert Management</Title>
          <Text>Monitor and manage system alerts</Text>
        </div>
        <Button
          icon={BellIcon}
          className="bg-blue-500 text-white hover:bg-blue-600"
        >
          Configure Notifications
        </Button>
      </div>

      {/* Alert Overview Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-red-100 p-3 dark:bg-red-900">
              <BellIcon className="h-6 w-6 text-red-700 dark:text-red-300" />
            </div>
            <div>
              <Text>Active Alerts</Text>
              <Title className="text-red-700 dark:text-red-300">{stats.active}</Title>
            </div>
          </div>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
              <BellIcon className="h-6 w-6 text-yellow-700 dark:text-yellow-300" />
            </div>
            <div>
              <Text>Acknowledged</Text>
              <Title className="text-yellow-700 dark:text-yellow-300">{stats.acknowledged}</Title>
            </div>
          </div>
        </Card>

        <Card className="transition-all duration-300 hover:shadow-lg">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-green-100 p-3 dark:bg-green-900">
              <CheckCircleIcon className="h-6 w-6 text-green-700 dark:text-green-300" />
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
              <BellSlashIcon className="h-6 w-6 text-gray-700 dark:text-gray-300" />
            </div>
            <div>
              <Text>Snoozed</Text>
              <Title className="text-gray-700 dark:text-gray-300">2</Title>
            </div>
          </div>
        </Card>
      </div>

      <TabGroup>
        <TabList>
          <Tab>Active Alerts</Tab>
          <Tab>Alert Rules</Tab>
          <Tab>History</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <div className="space-y-4">
                  {alerts?.map((alert) => (
                    <div
                      key={alert.id}
                      className="flex items-center justify-between rounded-lg border p-4 transition-all duration-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Text className="font-medium">{alert.title}</Text>
                          <Badge
                            color={
                              alert.severity === "High"
                                ? "red"
                                : alert.severity === "Medium"
                                ? "yellow"
                                : "green"
                            }
                          >
                            {alert.severity}
                          </Badge>
                          <Badge
                            color={
                              alert.status === "Active"
                                ? "red"
                                : alert.status === "Acknowledged"
                                ? "yellow"
                                : "green"
                            }
                          >
                            {alert.status}
                          </Badge>
                        </div>
                        <Text className="text-sm text-gray-500">
                          {alert.description}
                        </Text>
                        <Text className="text-xs text-gray-400">
                          {alert.timestamp} • {alert.source}
                        </Text>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="xs"
                          variant="secondary"
                          className="text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                          onClick={() => acknowledgeAlert(alert.id)}
                        >
                          Acknowledge
                        </Button>

                        <Button
                          size="xs"
                          variant="secondary"
                          className="text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                          onClick={() => resolveAlert(alert.id)}
                        >
                          Resolve
                        </Button>

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
                <div className="flex justify-between">
                  <Title>Alert Rules</Title>
                  <Button
                    size="xs"
                    className="bg-blue-500 text-white hover:bg-blue-600"
                  >
                    Add Rule
                  </Button>
                </div>
                <div className="mt-4 space-y-4">
                  {[
                    {
                      name: "High CPU Usage",
                      condition: "CPU > 90% for 5min",
                      severity: "High",
                      enabled: true,
                    },
                    {
                      name: "Failed Logins",
                      condition: "> 5 failed attempts in 10min",
                      severity: "Medium",
                      enabled: true,
                    },
                    {
                      name: "Disk Space",
                      condition: "Free space < 10%",
                      severity: "High",
                      enabled: false,
                    },
                  ].map((rule, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between rounded-lg border p-4 transition-all duration-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                    >
                      <div className="space-y-1">
                        <Text className="font-medium">{rule.name}</Text>
                        <Text className="text-sm text-gray-500">
                          Condition: {rule.condition}
                        </Text>
                      </div>
                      <div className="flex items-center space-x-4">
                        <Badge
                          color={
                            rule.severity === "High"
                              ? "red"
                              : rule.severity === "Medium"
                              ? "yellow"
                              : "green"
                          }
                        >
                          {rule.severity}
                        </Badge>
                        <Badge color={rule.enabled ? "green" : "gray"}>
                          {rule.enabled ? "Enabled" : "Disabled"}
                        </Badge>
                        <Button
                          size="xs"
                          variant="secondary"
                          className="text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                        >
                          Edit
                        </Button>
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
                <Title>Alert History</Title>
                <Text>Coming soon with detailed alert history and analytics</Text>
              </Card>
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
}

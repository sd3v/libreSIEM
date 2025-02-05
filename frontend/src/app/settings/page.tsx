"use client";

import { Card, Title, Text, TabGroup, TabList, Tab, TabPanels, TabPanel, TextInput, Select, SelectItem, Button, Switch } from "@tremor/react";
import { useState } from "react";

export default function SettingsPage() {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [emailAlerts, setEmailAlerts] = useState(true);

  return (
    <div className="space-y-6 p-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <Title>Settings</Title>
          <Text>Manage your system preferences</Text>
        </div>
        <Button className="bg-blue-500 text-white hover:bg-blue-600">
          Save Changes
        </Button>
      </div>

      <TabGroup>
        <TabList>
          <Tab>General</Tab>
          <Tab>Notifications</Tab>
          <Tab>Security</Tab>
          <Tab>API</Tab>
        </TabList>

        <TabPanels>
          <TabPanel>
            <div className="mt-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>General Settings</Title>
                <div className="mt-4 space-y-6">
                  {/* Theme Settings */}
                  <div className="space-y-2">
                    <Text>Theme Preferences</Text>
                    <div className="flex items-center justify-between rounded-lg border p-4">
                      <div>
                        <Text className="font-medium">Dark Mode</Text>
                        <Text className="text-sm text-gray-500">
                          Enable dark mode for the dashboard
                        </Text>
                      </div>
                      <Switch
                        checked={darkMode}
                        onChange={setDarkMode}
                        className="ml-4"
                      />
                    </div>
                  </div>

                  {/* Language Settings */}
                  <div className="space-y-2">
                    <Text>Language</Text>
                    <Select defaultValue="en">
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="de">Deutsch</SelectItem>
                      <SelectItem value="es">Español</SelectItem>
                    </Select>
                  </div>

                  {/* Timezone Settings */}
                  <div className="space-y-2">
                    <Text>Timezone</Text>
                    <Select defaultValue="utc">
                      <SelectItem value="utc">UTC</SelectItem>
                      <SelectItem value="est">Eastern Time</SelectItem>
                      <SelectItem value="pst">Pacific Time</SelectItem>
                    </Select>
                  </div>
                </div>
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6 space-y-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Notification Preferences</Title>
                <div className="mt-4 space-y-4">
                  {/* General Notifications */}
                  <div className="flex items-center justify-between rounded-lg border p-4">
                    <div>
                      <Text className="font-medium">Enable Notifications</Text>
                      <Text className="text-sm text-gray-500">
                        Receive notifications for important events
                      </Text>
                    </div>
                    <Switch
                      checked={notifications}
                      onChange={setNotifications}
                      className="ml-4"
                    />
                  </div>

                  {/* Email Alerts */}
                  <div className="flex items-center justify-between rounded-lg border p-4">
                    <div>
                      <Text className="font-medium">Email Alerts</Text>
                      <Text className="text-sm text-gray-500">
                        Receive critical alerts via email
                      </Text>
                    </div>
                    <Switch
                      checked={emailAlerts}
                      onChange={setEmailAlerts}
                      className="ml-4"
                    />
                  </div>

                  {/* Alert Settings */}
                  <div className="space-y-2">
                    <Text>Alert Priority</Text>
                    <Select defaultValue="all">
                      <SelectItem value="all">All Alerts</SelectItem>
                      <SelectItem value="high">High Priority Only</SelectItem>
                      <SelectItem value="critical">Critical Only</SelectItem>
                    </Select>
                  </div>
                </div>
              </Card>

              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Integration Settings</Title>
                <div className="mt-4 space-y-4">
                  {/* Slack Integration */}
                  <div className="space-y-2">
                    <Text>Slack Webhook URL</Text>
                    <TextInput placeholder="https://hooks.slack.com/..." />
                  </div>

                  {/* Teams Integration */}
                  <div className="space-y-2">
                    <Text>Microsoft Teams Webhook</Text>
                    <TextInput placeholder="https://outlook.office.com/..." />
                  </div>
                </div>
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6 space-y-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Security Settings</Title>
                <div className="mt-4 space-y-4">
                  {/* 2FA Settings */}
                  <div className="flex items-center justify-between rounded-lg border p-4">
                    <div>
                      <Text className="font-medium">Two-Factor Authentication</Text>
                      <Text className="text-sm text-gray-500">
                        Enable 2FA for additional security
                      </Text>
                    </div>
                    <Switch defaultChecked className="ml-4" />
                  </div>

                  {/* Session Settings */}
                  <div className="space-y-2">
                    <Text>Session Timeout</Text>
                    <Select defaultValue="30">
                      <SelectItem value="15">15 minutes</SelectItem>
                      <SelectItem value="30">30 minutes</SelectItem>
                      <SelectItem value="60">1 hour</SelectItem>
                    </Select>
                  </div>

                  {/* IP Whitelist */}
                  <div className="space-y-2">
                    <Text>IP Whitelist</Text>
                    <TextInput placeholder="Enter IP addresses (comma-separated)" />
                  </div>
                </div>
              </Card>

              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>Audit Log</Title>
                <div className="mt-4">
                  <Text>Coming soon with detailed audit logging capabilities</Text>
                </div>
              </Card>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="mt-6 space-y-6">
              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>API Configuration</Title>
                <div className="mt-4 space-y-4">
                  {/* API Key */}
                  <div className="space-y-2">
                    <Text>API Key</Text>
                    <div className="flex space-x-2">
                      <TextInput
                        className="flex-grow"
                        value="••••••••••••••••"
                        disabled
                      />
                      <Button variant="secondary">Regenerate</Button>
                    </div>
                  </div>

                  {/* Rate Limiting */}
                  <div className="space-y-2">
                    <Text>Rate Limit (requests/minute)</Text>
                    <Select defaultValue="1000">
                      <SelectItem value="100">100</SelectItem>
                      <SelectItem value="500">500</SelectItem>
                      <SelectItem value="1000">1,000</SelectItem>
                      <SelectItem value="unlimited">Unlimited</SelectItem>
                    </Select>
                  </div>

                  {/* Allowed Origins */}
                  <div className="space-y-2">
                    <Text>Allowed Origins</Text>
                    <TextInput placeholder="Enter domains (comma-separated)" />
                  </div>
                </div>
              </Card>

              <Card className="transition-all duration-300 hover:shadow-lg">
                <Title>API Documentation</Title>
                <div className="mt-4">
                  <Text>
                    Access our API documentation to integrate with your systems
                  </Text>
                  <Button
                    variant="secondary"
                    className="mt-4"
                  >
                    View Documentation
                  </Button>
                </div>
              </Card>
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>
    </div>
  );
}

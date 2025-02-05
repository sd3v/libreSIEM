'use client';

import { Card, Title, Text, TextInput, Button, Select, SelectItem, Grid, Switch } from '@tremor/react';
import { useState } from 'react';

const notificationChannels = [
  { value: 'email', label: 'Email' },
  { value: 'slack', label: 'Slack' },
  { value: 'webhook', label: 'Webhook' },
];

const retentionPeriods = [
  { value: '30', label: '30 Days' },
  { value: '60', label: '60 Days' },
  { value: '90', label: '90 Days' },
  { value: '180', label: '180 Days' },
  { value: '365', label: '1 Year' },
];

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState('sk_test_123456789');
  const [notificationChannel, setNotificationChannel] = useState('email');
  const [retentionPeriod, setRetentionPeriod] = useState('30');
  const [emailSettings, setEmailSettings] = useState({
    enabled: true,
    address: 'admin@example.com',
  });
  const [slackSettings, setSlackSettings] = useState({
    enabled: false,
    webhook: 'https://hooks.slack.com/services/xxx/yyy/zzz',
  });
  const [webhookSettings, setWebhookSettings] = useState({
    enabled: false,
    url: 'https://api.example.com/webhook',
  });

  const regenerateApiKey = () => {
    // In a real application, this would make an API call
    const newKey = 'sk_test_' + Math.random().toString(36).substring(2);
    setApiKey(newKey);
  };

  return (
    <div className="space-y-6">
      <div>
        <Title>Settings</Title>
        <Text>Configure your LibreSIEM instance</Text>
      </div>

      <Grid numItems={1} className="gap-6">
        <Card>
          <Title>API Configuration</Title>
          <div className="mt-4 space-y-4">
            <div>
              <Text>API Key</Text>
              <div className="flex space-x-2 mt-1">
                <TextInput value={apiKey} readOnly className="flex-1" />
                <Button onClick={regenerateApiKey}>Regenerate</Button>
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <Title>Notification Settings</Title>
          <div className="mt-4 space-y-6">
            <div>
              <Text>Default Notification Channel</Text>
              <Select
                className="mt-1"
                value={notificationChannel}
                onValueChange={setNotificationChannel}
              >
                {notificationChannels.map((channel) => (
                  <SelectItem key={channel.value} value={channel.value}>
                    {channel.label}
                  </SelectItem>
                ))}
              </Select>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <Text>Email Notifications</Text>
                  <Switch
                    checked={emailSettings.enabled}
                    onChange={(checked) =>
                      setEmailSettings({ ...emailSettings, enabled: checked })
                    }
                  />
                </div>
                {emailSettings.enabled && (
                  <TextInput
                    className="mt-2"
                    placeholder="Email address"
                    value={emailSettings.address}
                    onChange={(e) =>
                      setEmailSettings({ ...emailSettings, address: e.target.value })
                    }
                  />
                )}
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <Text>Slack Notifications</Text>
                  <Switch
                    checked={slackSettings.enabled}
                    onChange={(checked) =>
                      setSlackSettings({ ...slackSettings, enabled: checked })
                    }
                  />
                </div>
                {slackSettings.enabled && (
                  <TextInput
                    className="mt-2"
                    placeholder="Slack webhook URL"
                    value={slackSettings.webhook}
                    onChange={(e) =>
                      setSlackSettings({ ...slackSettings, webhook: e.target.value })
                    }
                  />
                )}
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <Text>Webhook Notifications</Text>
                  <Switch
                    checked={webhookSettings.enabled}
                    onChange={(checked) =>
                      setWebhookSettings({ ...webhookSettings, enabled: checked })
                    }
                  />
                </div>
                {webhookSettings.enabled && (
                  <TextInput
                    className="mt-2"
                    placeholder="Webhook URL"
                    value={webhookSettings.url}
                    onChange={(e) =>
                      setWebhookSettings({ ...webhookSettings, url: e.target.value })
                    }
                  />
                )}
              </div>
            </div>
          </div>
        </Card>

        <Card>
          <Title>Data Retention</Title>
          <div className="mt-4">
            <Text>Log Retention Period</Text>
            <Select
              className="mt-1"
              value={retentionPeriod}
              onValueChange={setRetentionPeriod}
            >
              {retentionPeriods.map((period) => (
                <SelectItem key={period.value} value={period.value}>
                  {period.label}
                </SelectItem>
              ))}
            </Select>
          </div>
        </Card>

        <div className="flex justify-end space-x-2">
          <Button variant="secondary">Cancel</Button>
          <Button>Save Changes</Button>
        </div>
      </Grid>
    </div>
  );
}

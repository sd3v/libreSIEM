'use client';

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
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Settings</h1>
        <p className="text-muted-foreground">Configure your LibreSIEM instance</p>
      </div>

      <div className="space-y-6">
        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">API Configuration</h2>
          <div className="mt-4 space-y-4">
            <div>
              <label className="text-sm font-medium text-card-foreground">API Key</label>
              <div className="flex space-x-2 mt-1">
                <input
                  type="text"
                  value={apiKey}
                  readOnly
                  className="flex-1 bg-muted px-3 py-2 rounded-md border border-input text-card-foreground"
                />
                <button
                  onClick={regenerateApiKey}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                >
                  Regenerate
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Notification Settings</h2>
          <div className="mt-4 space-y-6">
            <div>
              <label className="text-sm font-medium text-card-foreground">Default Notification Channel</label>
              <select
                className="mt-1 w-full bg-muted px-3 py-2 rounded-md border border-input text-card-foreground"
                value={notificationChannel}
                onChange={(e) => setNotificationChannel(e.target.value)}
              >
                {notificationChannels.map((channel) => (
                  <option key={channel.value} value={channel.value}>
                    {channel.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-card-foreground">Email Notifications</label>
                  <button
                    onClick={() => setEmailSettings({ ...emailSettings, enabled: !emailSettings.enabled })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background ${emailSettings.enabled ? 'bg-primary' : 'bg-input'}`}
                  >
                    <span
                      className={`${emailSettings.enabled ? 'translate-x-6' : 'translate-x-1'} inline-block h-4 w-4 transform rounded-full bg-background transition-transform`}
                    />
                  </button>
                </div>
                {emailSettings.enabled && (
                  <input
                    type="email"
                    className="mt-2 w-full bg-muted px-3 py-2 rounded-md border border-input text-card-foreground"
                    placeholder="Email address"
                    value={emailSettings.address}
                    onChange={(e) => setEmailSettings({ ...emailSettings, address: e.target.value })}
                  />
                )}
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-card-foreground">Slack Notifications</label>
                  <button
                    onClick={() => setSlackSettings({ ...slackSettings, enabled: !slackSettings.enabled })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background ${slackSettings.enabled ? 'bg-primary' : 'bg-input'}`}
                  >
                    <span
                      className={`${slackSettings.enabled ? 'translate-x-6' : 'translate-x-1'} inline-block h-4 w-4 transform rounded-full bg-background transition-transform`}
                    />
                  </button>
                </div>
                {slackSettings.enabled && (
                  <input
                    type="url"
                    className="mt-2 w-full bg-muted px-3 py-2 rounded-md border border-input text-card-foreground"
                    placeholder="Slack webhook URL"
                    value={slackSettings.webhook}
                    onChange={(e) => setSlackSettings({ ...slackSettings, webhook: e.target.value })}
                  />
                )}
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-card-foreground">Webhook Notifications</label>
                  <button
                    onClick={() => setWebhookSettings({ ...webhookSettings, enabled: !webhookSettings.enabled })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background ${webhookSettings.enabled ? 'bg-primary' : 'bg-input'}`}
                  >
                    <span
                      className={`${webhookSettings.enabled ? 'translate-x-6' : 'translate-x-1'} inline-block h-4 w-4 transform rounded-full bg-background transition-transform`}
                    />
                  </button>
                </div>
                {webhookSettings.enabled && (
                  <input
                    type="url"
                    className="mt-2 w-full bg-muted px-3 py-2 rounded-md border border-input text-card-foreground"
                    placeholder="Webhook URL"
                    value={webhookSettings.url}
                    onChange={(e) => setWebhookSettings({ ...webhookSettings, url: e.target.value })}
                  />
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Data Retention</h2>
          <div className="mt-4">
            <label className="text-sm font-medium text-card-foreground">Log Retention Period</label>
            <select
              className="mt-1 w-full bg-muted px-3 py-2 rounded-md border border-input text-card-foreground"
              value={retentionPeriod}
              onChange={(e) => setRetentionPeriod(e.target.value)}
            >
              {retentionPeriods.map((period) => (
                <option key={period.value} value={period.value}>
                  {period.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex justify-end space-x-2">
          <button
            className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90"
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}

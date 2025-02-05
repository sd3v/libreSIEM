'use client';

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
    critical: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    high: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
    medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  };
  return colors[severity as keyof typeof colors] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
};

export default function AlertsPage() {
  const [selectedAlert, setSelectedAlert] = useState<typeof recentAlerts[0] | null>(null);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Security Alerts</h1>
        <p className="text-muted-foreground">Monitor and manage security alerts across your infrastructure</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="col-span-1 lg:col-span-2">
          <div className="bg-card p-6 rounded-lg border border-border">
            <h2 className="text-lg font-semibold text-card-foreground">Alert Trends</h2>
            <div className="h-[300px] mt-4">
              {/* LineChart component would go here */}
            </div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Alert Distribution</h2>
          <div className="h-[300px] mt-4">
            {/* BarChart component would go here */}
          </div>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border">
        <div className="p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Recent Alerts</h2>
          <div className="mt-6 space-y-4">
            {recentAlerts.map((alert) => (
              <div
                key={alert.id}
                className="p-4 border border-border rounded-lg hover:bg-muted/50 cursor-pointer"
                onClick={() => setSelectedAlert(alert)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <h3 className="font-medium mt-1 text-card-foreground">{alert.title}</h3>
                    <p className="text-sm text-muted-foreground">{alert.description}</p>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {new Date(alert.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {selectedAlert && (
        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-semibold text-card-foreground">Alert Details</h2>
          <div className="mt-4">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(selectedAlert.severity)}`}>
              {selectedAlert.severity.toUpperCase()}
            </span>
            <h3 className="font-medium mt-2 text-card-foreground">{selectedAlert.title}</h3>
            <p className="text-muted-foreground mt-1">{selectedAlert.description}</p>
            <p className="text-sm text-muted-foreground mt-4">
              Detected at: {new Date(selectedAlert.timestamp).toLocaleString()}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

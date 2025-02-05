'use client';

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
    malware: 'bg-destructive text-destructive-foreground',
    suspicious: 'bg-warning text-warning-foreground',
    policy: 'bg-yellow-500 text-yellow-50',
  };
  return colors[type as keyof typeof colors] || 'bg-muted text-muted-foreground';
};

const getStatusColor = (status: string) => {
  const colors = {
    blocked: 'bg-success text-success-foreground',
    investigating: 'bg-warning text-warning-foreground',
    resolved: 'bg-primary text-primary-foreground',
  };
  return colors[status as keyof typeof colors] || 'bg-muted text-muted-foreground';
};

export default function SecurityPage() {
  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Security Overview</h1>
        <p className="text-muted-foreground">Monitor and respond to security threats across your infrastructure</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className={`bg-card p-6 rounded-lg border border-border ${securityScore >= 80 ? 'border-t-4 border-t-success' : 'border-t-4 border-t-destructive'}`}>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-card-foreground">Security Score</p>
              <p className="text-3xl font-semibold text-card-foreground mt-2">{securityScore}%</p>
            </div>
            <ShieldCheckIcon className={`w-8 h-8 ${securityScore >= 80 ? 'text-success' : 'text-destructive'}`} />
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border border-t-4 border-t-destructive">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-card-foreground">Active Threats</p>
              <p className="text-3xl font-semibold text-card-foreground mt-2">{activeThreats}</p>
            </div>
            <ShieldExclamationIcon className="w-8 h-8 text-destructive" />
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border border-t-4 border-t-warning">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-card-foreground">Active Alerts</p>
              <p className="text-3xl font-semibold text-card-foreground mt-2">{activeAlerts}</p>
            </div>
            <BellAlertIcon className="w-8 h-8 text-warning" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        <div className="col-span-1 lg:col-span-2">
          <div className="bg-card p-6 rounded-lg border border-border">
            <h2 className="text-lg font-semibold text-card-foreground">Threat Activity</h2>
            {/* Replace with a more customizable chart component */}
            <div className="h-[300px] mt-6 bg-muted rounded-md flex items-center justify-center">
              <p className="text-muted-foreground">Chart placeholder - implement with a custom chart library</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-card p-6 rounded-lg border border-border">
        <h2 className="text-lg font-semibold text-card-foreground">Recent Threats</h2>
        <div className="mt-6 space-y-4">
          {recentThreats.map((threat) => (
            <div key={threat.id} className="p-4 bg-muted rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex space-x-2">
                    <span className={`px-2 py-1 rounded-md text-xs font-medium ${getThreatColor(threat.type)}`}>
                      {threat.type.toUpperCase()}
                    </span>
                    <span className={`px-2 py-1 rounded-md text-xs font-medium ${getStatusColor(threat.status)}`}>
                      {threat.status.toUpperCase()}
                    </span>
                  </div>
                  <h3 className="font-medium text-card-foreground mt-2">{threat.title}</h3>
                  <p className="text-sm text-muted-foreground">{threat.description}</p>
                </div>
                <button
                  className="px-3 py-1.5 bg-secondary text-secondary-foreground text-sm rounded-md hover:bg-secondary/90"
                >
                  Investigate
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

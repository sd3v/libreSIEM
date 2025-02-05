'use client';

import { useState } from 'react';
import { DocumentTextIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

const sampleReports = [
  {
    id: 'report1',
    title: 'Monthly Security Summary',
    description: 'Overview of security events and incidents from the past month',
    type: 'security',
    lastGenerated: '2025-02-01T00:00:00Z',
    schedule: 'Monthly',
  },
  {
    id: 'report2',
    title: 'System Performance Analysis',
    description: 'Detailed analysis of system performance metrics',
    type: 'performance',
    lastGenerated: '2025-02-04T00:00:00Z',
    schedule: 'Weekly',
  },
  // Add more sample reports
];

const reportTypes = [
  { value: 'all', label: 'All Reports' },
  { value: 'security', label: 'Security Reports' },
  { value: 'performance', label: 'Performance Reports' },
  { value: 'compliance', label: 'Compliance Reports' },
];

export default function ReportsPage() {
  const [selectedType, setSelectedType] = useState('all');

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Reports</h1>
          <p className="text-muted-foreground">Generate and manage security reports</p>
        </div>
        <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 flex items-center space-x-2">
          <DocumentTextIcon className="h-5 w-5" />
          <span>New Report</span>
        </button>
      </div>

      <div className="bg-card p-6 rounded-lg border border-border">
        <div className="flex gap-4 items-center">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="bg-muted px-3 py-2 rounded-md border border-input text-foreground"
          >
            {reportTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sampleReports.map((report) => (
          <div key={report.id} className="bg-card rounded-lg border border-border p-6">
            <div className="flex justify-between items-start">
              <div className="space-y-2">
                <h3 className="text-lg font-semibold text-card-foreground">{report.title}</h3>
                <p className="text-sm text-muted-foreground">{report.description}</p>
                <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                  <span>Type: {report.type}</span>
                  <span>Schedule: {report.schedule}</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Last generated: {new Date(report.lastGenerated).toLocaleDateString()}
                </p>
              </div>
              <button className="p-2 text-muted-foreground hover:text-foreground">
                <ArrowDownTrayIcon className="h-5 w-5" />
              </button>
            </div>
            <div className="mt-4 flex space-x-3">
              <button className="px-3 py-1.5 bg-primary text-primary-foreground text-sm rounded-md hover:bg-primary/90">
                Generate Now
              </button>
              <button className="px-3 py-1.5 bg-secondary text-secondary-foreground text-sm rounded-md hover:bg-secondary/90">
                Edit Schedule
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
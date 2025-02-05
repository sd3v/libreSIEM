import { NextResponse } from 'next/server';

// This would typically come from your database
let alerts = [
  {
    id: '1',
    title: 'High CPU Usage Detected',
    description: 'Server CPU usage exceeded 90% for more than 5 minutes',
    severity: 'High',
    timestamp: '2024-02-05 13:15',
    status: 'Active',
    source: 'System Monitor',
  },
  {
    id: '2',
    title: 'Failed Login Attempts',
    description: 'Multiple failed login attempts from IP 192.168.1.100',
    severity: 'Medium',
    timestamp: '2024-02-05 13:10',
    status: 'Acknowledged',
    source: 'Auth Service',
  },
];

export async function GET() {
  return NextResponse.json(alerts);
}

export async function POST(req: Request) {
  const newAlert = await req.json();
  alerts.unshift({
    id: String(alerts.length + 1),
    ...newAlert,
    timestamp: new Date().toISOString(),
  });
  return NextResponse.json(alerts[0]);
}

export async function PUT(req: Request) {
  const { id, status } = await req.json();
  const alert = alerts.find(a => a.id === id);
  if (alert) {
    alert.status = status;
    return NextResponse.json(alert);
  }
  return NextResponse.json({ error: 'Alert not found' }, { status: 404 });
}

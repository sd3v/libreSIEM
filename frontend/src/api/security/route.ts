import { NextResponse } from 'next/server';

// This would typically come from your database
const securityEvents = [
  {
    id: '1',
    timestamp: '2024-02-05 12:30',
    event: 'Failed login attempt',
    severity: 'High',
    source: '192.168.1.100',
    status: 'Open',
    details: {
      username: 'admin',
      attempts: 5,
      location: 'US',
    },
  },
  {
    id: '2',
    timestamp: '2024-02-05 12:25',
    event: 'Firewall rule violation',
    severity: 'Medium',
    source: '192.168.1.150',
    status: 'Investigating',
    details: {
      rule: 'Block outbound SSH',
      destination: '203.0.113.1',
      port: 22,
    },
  },
  {
    id: '3',
    timestamp: '2024-02-05 12:20',
    event: 'Malware detected',
    severity: 'High',
    source: '192.168.1.200',
    status: 'Open',
    details: {
      malwareType: 'Ransomware',
      file: '/tmp/suspicious.exe',
      hash: 'a1b2c3d4e5f6',
    },
  },
  {
    id: '4',
    timestamp: '2024-02-05 12:15',
    event: 'Suspicious process',
    severity: 'Medium',
    source: '192.168.1.175',
    status: 'Investigating',
    details: {
      processName: 'unknown.exe',
      pid: 1234,
      user: 'system',
    },
  },
  {
    id: '5',
    timestamp: '2024-02-05 12:10',
    event: 'Data exfiltration attempt',
    severity: 'High',
    source: '192.168.1.125',
    status: 'Open',
    details: {
      destination: '198.51.100.1',
      dataSize: '2.5GB',
      protocol: 'HTTPS',
    },
  },
];

const threatData = [
  {
    date: '2024-02-01',
    'Malware Detected': 23,
    'Suspicious Activities': 45,
    'Policy Violations': 20,
  },
  {
    date: '2024-02-02',
    'Malware Detected': 12,
    'Suspicious Activities': 54,
    'Policy Violations': 32,
  },
  {
    date: '2024-02-03',
    'Malware Detected': 34,
    'Suspicious Activities': 38,
    'Policy Violations': 25,
  },
  {
    date: '2024-02-04',
    'Malware Detected': 18,
    'Suspicious Activities': 42,
    'Policy Violations': 28,
  },
  {
    date: '2024-02-05',
    'Malware Detected': 28,
    'Suspicious Activities': 48,
    'Policy Violations': 22,
  },
];

export async function GET(req: Request) {
  const url = new URL(req.url);
  const type = url.searchParams.get('type');

  if (type === 'events') {
    return NextResponse.json(securityEvents);
  } else if (type === 'threats') {
    return NextResponse.json(threatData);
  }

  return NextResponse.json({
    events: securityEvents,
    threats: threatData,
  });
}

export async function POST(req: Request) {
  const newEvent = await req.json();
  securityEvents.unshift({
    id: String(securityEvents.length + 1),
    ...newEvent,
    timestamp: new Date().toISOString(),
  });
  return NextResponse.json(securityEvents[0]);
}

export async function PUT(req: Request) {
  const { id, status } = await req.json();
  const event = securityEvents.find(e => e.id === id);
  if (event) {
    event.status = status;
    return NextResponse.json(event);
  }
  return NextResponse.json({ error: 'Event not found' }, { status: 404 });
}

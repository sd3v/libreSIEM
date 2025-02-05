import { NextResponse } from 'next/server';

const logVolume = [
  {
    date: '2024-02-01',
    'Log Volume': 2890,
    'Error Rate': 12,
    'Warning Rate': 43,
  },
  {
    date: '2024-02-02',
    'Log Volume': 3200,
    'Error Rate': 15,
    'Warning Rate': 38,
  },
  {
    date: '2024-02-03',
    'Log Volume': 2950,
    'Error Rate': 8,
    'Warning Rate': 35,
  },
  {
    date: '2024-02-04',
    'Log Volume': 3100,
    'Error Rate': 10,
    'Warning Rate': 40,
  },
  {
    date: '2024-02-05',
    'Log Volume': 3400,
    'Error Rate': 14,
    'Warning Rate': 45,
  },
];

const sourceDistribution = [
  { name: 'Apache', value: 456 },
  { name: 'Nginx', value: 351 },
  { name: 'MySQL', value: 271 },
  { name: 'PostgreSQL', value: 191 },
  { name: 'MongoDB', value: 91 },
];

const logLevels = [
  { name: 'ERROR', value: 89 },
  { name: 'WARNING', value: 156 },
  { name: 'INFO', value: 345 },
  { name: 'DEBUG', value: 190 },
];

const quickStats = {
  totalLogsToday: 23456,
  successRate: 98.2,
  avgResponseTime: 235,
  activeSources: 12,
};

export async function GET(req: Request) {
  const url = new URL(req.url);
  const type = url.searchParams.get('type');

  switch (type) {
    case 'volume':
      return NextResponse.json(logVolume);
    case 'sources':
      return NextResponse.json(sourceDistribution);
    case 'levels':
      return NextResponse.json(logLevels);
    case 'stats':
      return NextResponse.json(quickStats);
    default:
      return NextResponse.json({
        logVolume,
        sourceDistribution,
        logLevels,
        quickStats,
      });
  }
}

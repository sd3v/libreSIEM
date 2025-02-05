import { NextResponse } from 'next/server';

// This would typically come from your database
let settings = {
  theme: 'light',
  language: 'en',
  timezone: 'UTC',
  notifications: {
    enabled: true,
    email: true,
    slack: false,
    teams: false,
  },
  security: {
    twoFactorAuth: true,
    sessionTimeout: 30,
    ipWhitelist: [],
  },
  api: {
    rateLimit: 1000,
    allowedOrigins: [],
  },
};

export async function GET() {
  return NextResponse.json(settings);
}

export async function POST(req: Request) {
  const updates = await req.json();
  settings = { ...settings, ...updates };
  return NextResponse.json(settings);
}

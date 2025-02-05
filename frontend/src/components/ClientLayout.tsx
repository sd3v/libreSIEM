'use client';

import dynamic from 'next/dynamic';
import { ReactNode } from 'react';

const AnimatedLayout = dynamic(() => import('./AnimatedLayout'), { ssr: false });

interface ClientLayoutProps {
  children: ReactNode;
  sidebar: ReactNode;
}

export default function ClientLayout({ children, sidebar }: ClientLayoutProps) {
  return <AnimatedLayout sidebar={sidebar}>{children}</AnimatedLayout>;
}

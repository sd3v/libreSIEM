import type { Metadata } from 'next';
import { Geist } from 'next/font/google';
import Sidebar from '../components/Sidebar';
import ClientLayout from '../components/ClientLayout';
import Providers from './providers';
import './globals.css';
import './animations.css';

const geist = Geist({
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'LibreSIEM Command Center',
  description: 'Next-Generation Security Information and Event Management System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${geist.className} bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 min-h-screen`}>
        <Providers>
          <ClientLayout sidebar={<Sidebar />}>
            {children}
          </ClientLayout>
        </Providers>
      </body>
    </html>
  );
}

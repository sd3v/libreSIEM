import type { Metadata } from 'next';
import { Geist } from 'next/font/google';
import { ThemeProvider } from '../components/ThemeProvider';
import Sidebar from '../components/Sidebar';
import { ThemeToggle } from '../components/ThemeToggle';
import './globals.css';

const geist = Geist({
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'LibreSIEM',
  description: 'Security Information and Event Management System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geist.className} bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100`}>
        <ThemeProvider>
          <div className="flex h-screen">
            <Sidebar />
            <main className="flex-1 overflow-auto">
              <ThemeToggle />
              {children}
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}

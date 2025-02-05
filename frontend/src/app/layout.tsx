import type { Metadata } from "next";
import { Geist } from "next/font/google";
import Sidebar from "@/components/Sidebar";
import Providers from './providers';
import "./globals.css";
import "./animations.css";

const geist = Geist({
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "LibreSIEM Dashboard",
  description: "Open Source Security Information and Event Management System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={geist.className}>
        <Providers>
          <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
            <Sidebar />
            <main className="flex-1 overflow-auto p-8">
              {children}
            </main>
          </div>
        </Providers>
      </body>
    </html>
  );
}

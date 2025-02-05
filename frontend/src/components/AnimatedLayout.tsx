'use client';

import { motion } from 'framer-motion';
import { ReactNode } from 'react';

interface AnimatedLayoutProps {
  children: ReactNode;
  sidebar: ReactNode;
}

export default function AnimatedLayout({ children, sidebar }: AnimatedLayoutProps) {
  return (
    <>
      {/* Hintergrund-Effekte */}
      <div className="fixed inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))] opacity-20" />
      <div className="fixed inset-0 bg-gradient-to-br from-gray-900/50 via-gray-800/50 to-gray-900/50 backdrop-blur-3xl" />
      
      <div className="relative flex h-screen overflow-hidden">
        {/* Ambient Glow Effekt */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-purple-500/5 to-pink-500/5" />
        
        {/* Animierte Sidebar */}
        <motion.div
          initial={{ x: -300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        >
          {sidebar}
        </motion.div>
        
        {/* Hauptinhalt mit Glasmorphismus */}
        <main className="relative flex-1 overflow-auto p-8">
          <div className="pointer-events-none fixed inset-0 z-30 [mask-image:radial-gradient(circle_at_center,transparent_20%,black)]" />
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {children}
          </motion.div>
        </main>
      </div>

      {/* Ambient Light Effect am unteren Rand */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 pointer-events-none">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="h-[200px] w-[600px] bg-gradient-to-t from-blue-500/20 via-purple-500/20 to-transparent blur-3xl"
        />
      </div>
    </>
  );
}

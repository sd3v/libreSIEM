'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface Settings {
  theme: string;
  language: string;
  timezone: string;
  notifications: {
    enabled: boolean;
    email: boolean;
    slack: boolean;
    teams: boolean;
  };
  security: {
    twoFactorAuth: boolean;
    sessionTimeout: number;
    ipWhitelist: string[];
  };
  api: {
    rateLimit: number;
    allowedOrigins: string[];
  };
}

export function useSettings() {
  const queryClient = useQueryClient();

  const { data: settings, isLoading } = useQuery<Settings>({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await fetch('/api/settings');
      return response.json();
    },
  });

  const { mutate: updateSettings } = useMutation({
    mutationFn: async (newSettings: Partial<Settings>) => {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSettings),
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });

  const setTheme = (theme: string) => {
    updateSettings({ theme });
    document.documentElement.setAttribute('data-theme', theme);
  };

  const setLanguage = (language: string) => {
    updateSettings({ language });
  };

  const setTimezone = (timezone: string) => {
    updateSettings({ timezone });
  };

  const updateNotifications = (notifications: Partial<Settings['notifications']>) => {
    updateSettings({
      notifications: {
        ...settings?.notifications,
        ...notifications,
      },
    });
  };

  const updateSecurity = (security: Partial<Settings['security']>) => {
    updateSettings({
      security: {
        ...settings?.security,
        ...security,
      },
    });
  };

  const updateApi = (api: Partial<Settings['api']>) => {
    updateSettings({
      api: {
        ...settings?.api,
        ...api,
      },
    });
  };

  return {
    settings,
    isLoading,
    setTheme,
    setLanguage,
    setTimezone,
    updateNotifications,
    updateSecurity,
    updateApi,
  };
}

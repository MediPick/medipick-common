'use client';

import React from 'react';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';

interface NotificationBannerProps {
  type?: 'info' | 'success' | 'warning' | 'error';
  message: string;
  onDismiss?: () => void;
  className?: string;
}

export const NotificationBanner: React.FC<NotificationBannerProps> = ({
  type = 'info',
  message,
  onDismiss,
  className = ''
}) => {
  const styles = {
    info: { bg: 'bg-blue-500/10 border-blue-500/20 text-blue-300', icon: <Info className="w-4 h-4 text-blue-400" /> },
    success: { bg: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300', icon: <CheckCircle className="w-4 h-4 text-emerald-400" /> },
    warning: { bg: 'bg-amber-500/10 border-amber-500/20 text-amber-300', icon: <AlertCircle className="w-4 h-4 text-amber-400" /> },
    error: { bg: 'bg-rose-500/10 border-rose-500/20 text-rose-300', icon: <AlertCircle className="w-4 h-4 text-rose-400" /> }
  }[type];

  return (
    <div className={`flex items-center justify-between gap-3 px-4 py-2.5 rounded-xl border text-xs font-medium ${styles.bg} ${className}`}>
      <div className="flex items-center gap-2.5">
        {styles.icon}
        <span>{message}</span>
      </div>
      {onDismiss && (
        <button onClick={onDismiss} className="hover:opacity-75 transition-opacity">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};

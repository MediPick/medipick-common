'use client';

import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  trend?: string;
  trendDirection?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  icon?: React.ReactNode;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  trend,
  trendDirection = 'up',
  subtitle,
  icon,
  className = ''
}) => {
  return (
    <div className={`p-5 rounded-2xl bg-[#111D1E] border border-[#1F3335] shadow-lg flex flex-col justify-between ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {icon && (
          <div className="w-9 h-9 rounded-xl bg-[#1D6F72]/15 border border-[#1D6F72]/30 flex items-center justify-center text-[#C7E36B]">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold tracking-tight text-white font-['Plus_Jakarta_Sans']">
          {value}
        </div>

        {(trend || subtitle) && (
          <div className="mt-1.5 flex items-center gap-2 text-xs">
            {trend && (
              <span className={`font-semibold ${
                trendDirection === 'up' ? 'text-emerald-400' :
                trendDirection === 'down' ? 'text-rose-400' : 'text-slate-400'
              }`}>
                {trend}
              </span>
            )}
            {subtitle && <span className="text-slate-500">{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
};

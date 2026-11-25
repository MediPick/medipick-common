'use client';

import React from 'react';

interface UserProfileBadgeProps {
  name: string;
  role: string;
  avatarUrl?: string;
  className?: string;
}

export const UserProfileBadge: React.FC<UserProfileBadgeProps> = ({
  name,
  role,
  avatarUrl,
  className = ''
}) => {
  return (
    <div className={`inline-flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-[#182728] border border-[#1F3335] text-slate-200 ${className}`}>
      {avatarUrl ? (
        <img src={avatarUrl} alt={name} className="w-6 h-6 rounded-full object-cover" />
      ) : (
        <div className="w-6 h-6 rounded-full bg-[#1D6F72] text-[#C7E36B] flex items-center justify-center font-bold text-xs">
          {name.charAt(0).toUpperCase()}
        </div>
      )}
      <span className="text-xs font-semibold text-white">{name}</span>
      <span className="text-[10px] px-1.5 py-0.5 rounded bg-teal-500/10 text-teal-400 border border-teal-500/20 font-medium uppercase tracking-wider">
        {role}
      </span>
    </div>
  );
};

'use client';

import React from 'react';

export type StatusType =
  // Order statuses
  | 'PENDING'
  | 'QUOTED'
  | 'CONFIRMED'
  | 'PREPARING'
  | 'DISPENSED'
  | 'COMPLETED'
  | 'CANCELLED'
  | 'REJECTED'
  // Verification & Compliance
  | 'VERIFIED'
  | 'UNVERIFIED'
  | 'FLAGGED'
  | 'SUSPENDED'
  | 'COMPLIANT'
  // Stock / Inventory
  | 'IN_STOCK'
  | 'LOW_STOCK'
  | 'OUT_OF_STOCK'
  // Generic
  | 'ACTIVE'
  | 'INACTIVE';

interface StatusBadgeProps {
  status: StatusType | string;
  className?: string;
  size?: 'sm' | 'md';
}

const STATUS_STYLES: Record<string, { bg: string; text: string; dot: string; label: string }> = {
  // Positive / Completed
  COMPLETED: { bg: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'Completed' },
  DISPENSED: { bg: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'Dispensed' },
  VERIFIED: { bg: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'Verified' },
  COMPLIANT: { bg: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'Compliant' },
  IN_STOCK: { bg: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'In Stock' },
  ACTIVE: { bg: 'bg-emerald-500/10 border-emerald-500/20', text: 'text-emerald-400', dot: 'bg-emerald-400', label: 'Active' },

  // In Progress / Action Required
  QUOTED: { bg: 'bg-amber-500/10 border-amber-500/20', text: 'text-amber-400', dot: 'bg-amber-400', label: 'Quoted' },
  CONFIRMED: { bg: 'bg-teal-500/10 border-teal-500/20', text: 'text-teal-400', dot: 'bg-teal-400', label: 'Confirmed' },
  PREPARING: { bg: 'bg-teal-500/10 border-teal-500/20', text: 'text-teal-400', dot: 'bg-teal-400', label: 'Preparing' },
  PENDING: { bg: 'bg-amber-500/10 border-amber-500/20', text: 'text-amber-400', dot: 'bg-amber-400 animate-pulse', label: 'Pending' },
  LOW_STOCK: { bg: 'bg-amber-500/10 border-amber-500/20', text: 'text-amber-400', dot: 'bg-amber-400', label: 'Low Stock' },

  // Negative / Warning / Regulatory
  REJECTED: { bg: 'bg-rose-500/10 border-rose-500/20', text: 'text-rose-400', dot: 'bg-rose-400', label: 'Rejected' },
  CANCELLED: { bg: 'bg-slate-500/10 border-slate-500/20', text: 'text-slate-400', dot: 'bg-slate-400', label: 'Cancelled' },
  FLAGGED: { bg: 'bg-rose-500/10 border-rose-500/20', text: 'text-rose-400', dot: 'bg-rose-400', label: 'Flagged' },
  SUSPENDED: { bg: 'bg-rose-500/10 border-rose-500/20', text: 'text-rose-400', dot: 'bg-rose-400', label: 'Suspended' },
  OUT_OF_STOCK: { bg: 'bg-rose-500/10 border-rose-500/20', text: 'text-rose-400', dot: 'bg-rose-400', label: 'Out of Stock' },
  INACTIVE: { bg: 'bg-slate-500/10 border-slate-500/20', text: 'text-slate-400', dot: 'bg-slate-400', label: 'Inactive' },
  UNVERIFIED: { bg: 'bg-slate-500/10 border-slate-500/20', text: 'text-slate-400', dot: 'bg-slate-400', label: 'Unverified' },
};

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '', size = 'sm' }) => {
  const normStatus = (status || '').toUpperCase();
  const config = STATUS_STYLES[normStatus] || {
    bg: 'bg-slate-500/10 border-slate-500/20',
    text: 'text-slate-400',
    dot: 'bg-slate-400',
    label: status || 'Unknown'
  };

  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border ${config.bg} ${config.text} ${sizeClasses} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
};

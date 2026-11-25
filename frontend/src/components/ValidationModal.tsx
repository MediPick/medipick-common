'use client';

import React, { useEffect } from 'react';
import { AlertCircle, AlertTriangle, X } from 'lucide-react';

export interface ValidationModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  message: string;
  fields?: Record<string, string> | string[];
  severity?: 'warning' | 'error' | 'info';
  confirmText?: string;
}

export const ValidationModal: React.FC<ValidationModalProps> = ({
  isOpen,
  onClose,
  title = 'Validation Required',
  message,
  fields,
  severity = 'warning',
  confirmText = 'Review & Fix',
}) => {
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const fieldList = Array.isArray(fields)
    ? fields
    : fields
    ? Object.entries(fields).map(([k, v]) => `${k.charAt(0).toUpperCase() + k.slice(1)}: ${v}`)
    : [];

  const isError = severity === 'error';
  const iconBg = isError ? 'rgba(239, 68, 68, 0.12)' : 'rgba(245, 158, 11, 0.12)';
  const iconBorder = isError ? 'rgba(239, 68, 68, 0.3)' : 'rgba(245, 158, 11, 0.3)';
  const iconColor = isError ? '#EF4444' : '#F59E0B';

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-in fade-in duration-200"
      role="dialog"
      aria-modal="true"
      aria-labelledby="validation-modal-title"
    >
      <div
        className="w-full max-w-md rounded-3xl shadow-2xl overflow-hidden transition-all animate-in zoom-in-95 duration-200"
        style={{
          background: 'var(--bg-surface, #0C1D1F)',
          border: 'none',
          outline: 'none',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6), 0 0 30px rgba(45, 212, 191, 0.08)',
        }}
      >
        {/* Header */}
        <div
          className="p-5 border-b flex items-center justify-between"
          style={{ borderColor: 'var(--border-subtle, rgba(45, 212, 191, 0.08))' }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 border"
              style={{ background: iconBg, borderColor: iconBorder, color: iconColor }}
            >
              {isError ? <AlertCircle size={20} /> : <AlertTriangle size={20} />}
            </div>
            <div>
              <h3 id="validation-modal-title" className="font-heading font-black text-sm text-[var(--text-primary)]">
                {title}
              </h3>
              <p className="text-[11px] text-[var(--text-muted)] font-medium">Input Validation Notice</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-xl border transition-all cursor-pointer hover:bg-white/5 active:scale-95"
            style={{ borderColor: 'var(--border-default, rgba(45, 212, 191, 0.15))', color: 'var(--text-muted)' }}
            aria-label="Close modal"
          >
            <X size={16} />
          </button>
        </div>

        {/* Body Content */}
        <div className="p-5 space-y-4">
          <p className="text-xs leading-relaxed text-[var(--text-primary)] font-medium">{message}</p>

          {fieldList.length > 0 && (
            <div
              className="p-3.5 rounded-2xl border space-y-2 text-xs"
              style={{
                background: isError ? 'rgba(239, 68, 68, 0.06)' : 'rgba(245, 158, 11, 0.06)',
                borderColor: isError ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
              }}
            >
              <span className="text-[11px] font-bold block" style={{ color: iconColor }}>
                Required Corrections:
              </span>
              <ul className="space-y-1.5 list-disc list-inside text-[11px] text-[var(--text-primary)]">
                {fieldList.map((item, idx) => (
                  <li key={idx} className="font-semibold leading-snug">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          className="p-4 border-t flex items-center justify-end"
          style={{ borderColor: 'var(--border-subtle, rgba(45, 212, 191, 0.08))' }}
        >
          <button
            type="button"
            onClick={onClose}
            className="btn-brand px-6 py-2.5 rounded-xl text-xs font-bold active:scale-95 cursor-pointer shadow-lg"
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

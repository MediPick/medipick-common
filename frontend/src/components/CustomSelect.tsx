'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { ChevronDown, Check } from 'lucide-react';

export interface CustomSelectOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
  description?: string;
}

export interface CustomSelectProps {
  value: string;
  onChange: (value: string) => void;
  options: CustomSelectOption[];
  label?: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  buttonClassName?: string;
  dropUp?: boolean;
  size?: 'sm' | 'md';
}

export const CustomSelect: React.FC<CustomSelectProps> = ({
  value,
  onChange,
  options,
  label,
  placeholder = 'Select option...',
  disabled = false,
  className = '',
  buttonClassName = '',
  dropUp = false,
  size = 'md',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [popoverCoords, setPopoverCoords] = useState<{ top: number; left: number; width: number } | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);

  const selectedOption = options.find((o) => o.value === value);

  useEffect(() => {
    setMounted(true);
  }, []);

  const calculatePosition = useCallback(() => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const approxMenuHeight = Math.min(260, Math.max(120, options.length * 42 + 16));
    const spaceBelow = window.innerHeight - rect.bottom;
    const showAbove = dropUp || (spaceBelow < approxMenuHeight && rect.top > approxMenuHeight);

    const top = showAbove
      ? Math.max(8, rect.top - approxMenuHeight - 6)
      : Math.min(window.innerHeight - approxMenuHeight - 8, rect.bottom + 6);

    const minWidth = Math.max(rect.width, 220);
    const left = Math.max(8, Math.min(rect.left, window.innerWidth - minWidth - 8));

    setPopoverCoords({
      top,
      left,
      width: rect.width,
    });
  }, [dropUp, options.length]);

  const toggleDropdown = () => {
    if (disabled) return;
    if (!isOpen) {
      calculatePosition();
    }
    setIsOpen((prev) => !prev);
  };

  useEffect(() => {
    if (!isOpen) return;
    calculatePosition();

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (containerRef.current && containerRef.current.contains(target)) return;
      if (popoverRef.current && popoverRef.current.contains(target)) return;
      setIsOpen(false);
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };

    const handleScrollOrResize = () => {
      calculatePosition();
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    window.addEventListener('resize', handleScrollOrResize);
    window.addEventListener('scroll', handleScrollOrResize, true);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('resize', handleScrollOrResize);
      window.removeEventListener('scroll', handleScrollOrResize, true);
    };
  }, [isOpen, calculatePosition]);

  const handleSelect = (val: string) => {
    onChange(val);
    setIsOpen(false);
  };

  const isCompact = size === 'sm';

  return (
    <div ref={containerRef} className={`relative text-xs w-full ${className}`}>
      {label && (
        <label className="block mb-1.5 font-bold text-slate-800 dark:text-slate-200">
          {label}
        </label>
      )}

      {/* Button Trigger */}
      <button
        type="button"
        disabled={disabled}
        onClick={toggleDropdown}
        className={`w-full flex items-center justify-between ${
          isCompact ? 'px-3 py-1.5 rounded-lg' : 'px-3.5 py-2.5 rounded-xl'
        } border bg-white dark:bg-slate-900 cursor-pointer text-left transition-all select-none shadow-2xs ${
          isOpen
            ? 'ring-2 ring-teal-500/30 border-teal-500 bg-teal-50/10'
            : 'hover:border-teal-500/50 hover:bg-slate-50/50 dark:hover:bg-slate-800/50'
        } ${disabled ? 'opacity-50 cursor-not-allowed bg-slate-100 dark:bg-slate-800' : ''} ${buttonClassName}`}
        style={{ borderColor: isOpen ? '#0D9488' : 'var(--border-subtle)' }}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          {selectedOption?.icon && (
            <span className="shrink-0 text-teal-600 dark:text-teal-400">
              {selectedOption.icon}
            </span>
          )}
          <span
            className={`truncate font-semibold ${
              selectedOption ? 'text-slate-900 dark:text-slate-100' : 'text-slate-400 dark:text-slate-500 font-normal'
            }`}
          >
            {selectedOption ? selectedOption.label : placeholder}
          </span>
        </div>

        <ChevronDown
          size={isCompact ? 13 : 15}
          className={`shrink-0 ml-2 text-slate-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180 text-teal-600 dark:text-teal-400' : ''
          }`}
        />
      </button>

      {/* Portal Popover Menu */}
      {isOpen && mounted && popoverCoords && createPortal(
        <div
          ref={popoverRef}
          role="listbox"
          style={{
            position: 'fixed',
            top: popoverCoords.top,
            left: popoverCoords.left,
            width: popoverCoords.width,
            minWidth: 220,
            zIndex: 99999,
            borderColor: 'var(--border-subtle)',
            backdropFilter: 'blur(16px)',
          }}
          className="p-1.5 rounded-2xl shadow-2xl border bg-white dark:bg-slate-900 animate-fade-in max-h-72 overflow-y-auto select-none"
        >
          {options.length === 0 ? (
            <div className="p-3 text-center text-slate-400 text-xs">No options available</div>
          ) : (
            options.map((opt) => {
              const isSelected = opt.value === value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => handleSelect(opt.value)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left text-xs transition-all cursor-pointer my-0.5 ${
                    isSelected
                      ? 'bg-teal-50 dark:bg-teal-950/60 text-teal-800 dark:text-teal-200 font-bold'
                      : 'hover:bg-slate-100/80 dark:hover:bg-slate-800/80 text-slate-700 dark:text-slate-300 font-medium'
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    {opt.icon && <span className="shrink-0">{opt.icon}</span>}
                    <div className="truncate">
                      <span className="block truncate">{opt.label}</span>
                      {opt.description && (
                        <span className="text-[10px] text-slate-400 dark:text-slate-500 block truncate font-normal mt-0.5">
                          {opt.description}
                        </span>
                      )}
                    </div>
                  </div>

                  {isSelected && (
                    <Check size={14} className="shrink-0 ml-2 text-teal-600 dark:text-teal-400" />
                  )}
                </button>
              );
            })
          )}
        </div>,
        document.body
      )}
    </div>
  );
};

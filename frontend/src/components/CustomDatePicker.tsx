'use client';

import React, { useState, useMemo, useRef, useEffect, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, X } from 'lucide-react';

interface CustomDatePickerProps {
  value: string; // YYYY-MM-DD or empty string
  onChange: (dateStr: string) => void;
  minDate?: string; // YYYY-MM-DD
  label?: string;
  placeholder?: string;
  dropUp?: boolean;
  position?: 'top' | 'bottom' | 'auto';
}

export const CustomDatePicker: React.FC<CustomDatePickerProps> = ({
  value,
  onChange,
  minDate = new Date().toISOString().split('T')[0],
  label,
  placeholder = 'Select expiry date',
  dropUp = false,
  position = 'auto',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);
  const [popoverCoords, setPopoverCoords] = useState<{ top: number; left: number; width: number } | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const calculatePosition = useCallback(() => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const calendarHeight = 370;
    const spaceBelow = window.innerHeight - rect.bottom;
    const spaceAbove = rect.top;

    let showAbove = false;
    if (position === 'top') {
      showAbove = true;
    } else if (position === 'bottom') {
      showAbove = false;
    } else if (dropUp) {
      showAbove = spaceAbove >= calendarHeight || spaceAbove > spaceBelow;
    } else {
      showAbove = spaceBelow < calendarHeight && spaceAbove > spaceBelow;
    }

    let top: number;
    if (showAbove) {
      top = Math.max(12, rect.top - calendarHeight - 8);
    } else {
      top = Math.min(window.innerHeight - calendarHeight - 12, rect.bottom + 8);
      top = Math.max(12, top);
    }

    const left = Math.max(12, Math.min(rect.left, window.innerWidth - 330));
    setPopoverCoords({
      top,
      left,
      width: Math.max(290, Math.min(rect.width, 320)),
    });
  }, [dropUp, position]);

  const toggleDropdown = () => {
    if (!isOpen) {
      calculatePosition();
    }
    setIsOpen((prev) => !prev);
  };

  // Close when clicking outside & handle scroll reposition
  useEffect(() => {
    if (!isOpen) return;
    calculatePosition();

    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (containerRef.current && containerRef.current.contains(target)) return;
      if (popoverRef.current && popoverRef.current.contains(target)) return;
      setIsOpen(false);
    };

    const handleScrollOrResize = () => {
      calculatePosition();
    };

    document.addEventListener('mousedown', handleClickOutside);
    window.addEventListener('resize', handleScrollOrResize);
    window.addEventListener('scroll', handleScrollOrResize, true);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      window.removeEventListener('resize', handleScrollOrResize);
      window.removeEventListener('scroll', handleScrollOrResize, true);
    };
  }, [isOpen, calculatePosition]);

  // Parse current view month/year from value or current date
  const initialDate = useMemo(() => {
    if (value) {
      const parts = value.split('-').map(Number);
      return new Date(parts[0], parts[1] - 1, parts[2]);
    }
    return new Date();
  }, [value]);

  const [viewYear, setViewYear] = useState(initialDate.getFullYear());
  const [viewMonth, setViewMonth] = useState(initialDate.getMonth()); // 0-11

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const handlePrevMonth = () => {
    if (viewMonth === 0) {
      setViewMonth(11);
      setViewYear((y) => y - 1);
    } else {
      setViewMonth((m) => m - 1);
    }
  };

  const handleNextMonth = () => {
    if (viewMonth === 11) {
      setViewMonth(0);
      setViewYear((y) => y + 1);
    } else {
      setViewMonth((m) => m + 1);
    }
  };

  // Preset quick picks
  const applyPreset = (daysFromNow: number | null) => {
    if (daysFromNow === null) {
      onChange('');
      setIsOpen(false);
      return;
    }
    const d = new Date();
    d.setDate(d.getDate() + daysFromNow);
    const yr = d.getFullYear();
    const mo = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    onChange(`${yr}-${mo}-${day}`);
    setViewYear(d.getFullYear());
    setViewMonth(d.getMonth());
    setIsOpen(false);
  };

  // Generate days in month
  const calendarGrid = useMemo(() => {
    const firstDayIndex = new Date(viewYear, viewMonth, 1).getDay(); // 0 is Sunday
    const daysInCurrentMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
    const days = [];

    // Leading blanks
    for (let i = 0; i < firstDayIndex; i++) {
      days.push(null);
    }

    // Days
    for (let d = 1; d <= daysInCurrentMonth; d++) {
      const mStr = String(viewMonth + 1).padStart(2, '0');
      const dStr = String(d).padStart(2, '0');
      const isoString = `${viewYear}-${mStr}-${dStr}`;
      const isPast = minDate ? isoString < minDate : false;
      const isSelected = value === isoString;
      const isToday = new Date().toISOString().split('T')[0] === isoString;

      days.push({
        dayNumber: d,
        isoString,
        isPast,
        isSelected,
        isToday,
      });
    }

    return days;
  }, [viewYear, viewMonth, value, minDate]);

  const displayFormatted = useMemo(() => {
    if (!value) return null;
    try {
      const [yr, mo, da] = value.split('-').map(Number);
      const d = new Date(yr, mo - 1, da);
      return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
    } catch {
      return value;
    }
  }, [value]);

  return (
    <div ref={containerRef} className="relative text-xs">
      {label && <label className="block mb-1.5 font-bold text-slate-700 dark:text-slate-300">{label}</label>}

      {/* Input button trigger */}
      <div className="flex items-center gap-1.5">
        <button
          type="button"
          onClick={toggleDropdown}
          className="flex-1 flex items-center justify-between p-2.5 rounded-xl border input-base bg-white dark:bg-slate-900 cursor-pointer text-left focus:ring-2 focus:ring-teal-500"
          style={{ borderColor: 'var(--border-subtle)' }}
        >
          <span className={value ? 'font-bold text-slate-900 dark:text-slate-100' : 'text-slate-400 font-normal'}>
            {displayFormatted || placeholder}
          </span>
          <CalendarIcon size={14} className="text-teal-600 dark:text-teal-400 ml-2" />
        </button>

        {value && (
          <button
            type="button"
            onClick={() => onChange('')}
            className="p-2.5 rounded-xl border hover:bg-black/5 text-slate-400 hover:text-rose-500 cursor-pointer"
            title="Clear date"
            style={{ borderColor: 'var(--border-subtle)' }}
          >
            <X size={14} />
          </button>
        )}
      </div>

      {/* Clean Calendar Dropdown rendered via Portal to avoid parent clipping */}
      {isOpen && mounted && popoverCoords && createPortal(
        <div
          ref={popoverRef}
          style={{
            position: 'fixed',
            top: popoverCoords.top,
            left: popoverCoords.left,
            width: popoverCoords.width,
            maxWidth: 320,
            maxHeight: 'calc(100vh - 24px)',
            zIndex: 99999,
            borderColor: 'var(--border-subtle)',
          }}
          className="p-4 pb-5 rounded-2xl shadow-2xl border bg-white dark:bg-slate-900 animate-fade-in text-xs overflow-y-auto select-none"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Quick Presets */}
          <div className="grid grid-cols-4 gap-1 pb-2.5 mb-2 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
            <button
              type="button"
              onClick={() => applyPreset(7)}
              className="px-1.5 py-1.5 rounded-lg text-[10px] font-bold border hover:bg-teal-50 dark:hover:bg-teal-950/30 text-teal-700 dark:text-teal-300 text-center transition-colors cursor-pointer"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              +7 Days
            </button>
            <button
              type="button"
              onClick={() => applyPreset(14)}
              className="px-1.5 py-1.5 rounded-lg text-[10px] font-bold border hover:bg-teal-50 dark:hover:bg-teal-950/30 text-teal-700 dark:text-teal-300 text-center transition-colors cursor-pointer"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              +14 Days
            </button>
            <button
              type="button"
              onClick={() => applyPreset(30)}
              className="px-1.5 py-1.5 rounded-lg text-[10px] font-bold border hover:bg-teal-50 dark:hover:bg-teal-950/30 text-teal-700 dark:text-teal-300 text-center transition-colors cursor-pointer"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              +30 Days
            </button>
            <button
              type="button"
              onClick={() => applyPreset(null)}
              className="px-1.5 py-1.5 rounded-lg text-[10px] font-bold border hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 text-center transition-colors cursor-pointer"
              style={{ borderColor: 'var(--border-subtle)' }}
            >
              Ongoing
            </button>
          </div>

          {/* Month / Year Navigator */}
          <div className="flex items-center justify-between mb-2 px-1">
            <span className="font-bold text-slate-800 dark:text-slate-100 text-xs">
              {monthNames[viewMonth]} {viewYear}
            </span>
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={handlePrevMonth}
                className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 cursor-pointer"
              >
                <ChevronLeft size={14} />
              </button>
              <button
                type="button"
                onClick={handleNextMonth}
                className="p-1 rounded-lg hover:bg-black/5 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300 cursor-pointer"
              >
                <ChevronRight size={14} />
              </button>
            </div>
          </div>

          {/* Day of Week Headers */}
          <div className="grid grid-cols-7 gap-1 text-center font-bold text-[10px] text-slate-400 mb-1.5">
            <div>Su</div>
            <div>Mo</div>
            <div>Tu</div>
            <div>We</div>
            <div>Th</div>
            <div>Fr</div>
            <div>Sa</div>
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1 justify-items-center">
            {calendarGrid.map((item, idx) => {
              if (!item) {
                return <div key={`empty-${idx}`} className="h-7 w-7" />;
              }

              const { dayNumber, isoString, isPast, isSelected, isToday } = item;

              return (
                <button
                  key={isoString}
                  type="button"
                  disabled={isPast}
                  onClick={() => {
                    onChange(isoString);
                    setIsOpen(false);
                  }}
                  className={`h-7 w-7 rounded-lg flex items-center justify-center text-xs font-semibold transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-teal-600 text-white font-bold shadow-sm'
                      : isPast
                      ? 'opacity-25 cursor-not-allowed text-slate-400'
                      : isToday
                      ? 'border border-teal-500 font-bold text-teal-600 dark:text-teal-400 hover:bg-teal-50 dark:hover:bg-teal-950/20'
                      : 'hover:bg-black/5 dark:hover:bg-white/10 text-slate-700 dark:text-slate-200'
                  }`}
                >
                  {dayNumber}
                </button>
              );
            })}
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

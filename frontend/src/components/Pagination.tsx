"use client";

import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export interface PaginationProps {
  currentPage: number;
  totalItems: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (pageSize: number) => void;
  pageSizeOptions?: number[];
  itemName?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 25, 50],
  itemName = 'items',
}) => {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  
  if (totalItems === 0) return null;

  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  // Generate page numbers with smart window
  const getPageNumbers = (): (number | 'ellipsis')[] => {
    if (totalPages <= 7) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }
    const pages: (number | 'ellipsis')[] = [];
    if (currentPage <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i);
      pages.push('ellipsis');
      pages.push(totalPages);
    } else if (currentPage >= totalPages - 3) {
      pages.push(1);
      pages.push('ellipsis');
      for (let i = totalPages - 4; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      pages.push('ellipsis');
      pages.push(currentPage - 1);
      pages.push(currentPage);
      pages.push(currentPage + 1);
      pages.push('ellipsis');
      pages.push(totalPages);
    }
    return pages;
  };

  return (
    <div className="card-premium p-3 sm:p-4 rounded-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs mt-4">
      {/* Left: Summary Count & Page Size Selector */}
      <div className="flex items-center gap-3 flex-wrap">
        <span className="font-semibold" style={{ color: 'var(--text-muted)' }}>
          Showing <span className="font-bold font-mono" style={{ color: 'var(--text-primary)' }}>{startItem}–{endItem}</span> of{' '}
          <span className="font-bold font-mono" style={{ color: 'var(--text-primary)' }}>{totalItems}</span> {itemName}
        </span>

        {onPageSizeChange && (
          <div className="flex items-center gap-1.5 pl-2 border-l" style={{ borderColor: 'var(--border-subtle)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Per page:</span>
            <div className="flex items-center gap-1">
              {pageSizeOptions.map((sz) => (
                <button
                  key={sz}
                  type="button"
                  onClick={() => {
                    onPageSizeChange(sz);
                    onPageChange(1);
                  }}
                  className={`px-2 py-0.5 rounded-lg font-bold font-mono transition-all cursor-pointer ${
                    pageSize === sz
                      ? 'bg-[var(--brand)] text-[var(--text-on-brand)] shadow-xs'
                      : 'hover:bg-black/5 dark:hover:bg-white/5 text-[var(--text-muted)]'
                  }`}
                >
                  {sz}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Right: Navigation Buttons and Number Pills */}
      <div className="flex items-center gap-1 self-center sm:self-auto">
        <button
          type="button"
          disabled={currentPage <= 1}
          onClick={() => onPageChange(currentPage - 1)}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl border font-bold transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer hover:bg-black/5 dark:hover:bg-white/5 shadow-xs"
          style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
          title="Previous Page"
        >
          <ChevronLeft size={14} />
          <span className="hidden sm:inline">Prev</span>
        </button>

        <div className="flex items-center gap-1 px-1">
          {getPageNumbers().map((p, idx) =>
            p === 'ellipsis' ? (
              <span key={`ell-${idx}`} className="px-1.5 py-1 font-bold text-[var(--text-muted)]">
                …
              </span>
            ) : (
              <button
                key={p}
                type="button"
                onClick={() => onPageChange(p)}
                className={`min-w-[30px] h-[30px] flex items-center justify-center rounded-xl font-bold font-mono transition-all cursor-pointer text-xs ${
                  currentPage === p
                    ? 'bg-[var(--brand)] text-[var(--text-on-brand)] shadow-xs font-black'
                    : 'border hover:bg-black/5 dark:hover:bg-white/5 text-[var(--text-secondary)]'
                }`}
                style={currentPage !== p ? { borderColor: 'var(--border-default)' } : {}}
              >
                {p}
              </button>
            )
          )}
        </div>

        <button
          type="button"
          disabled={currentPage >= totalPages}
          onClick={() => onPageChange(currentPage + 1)}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl border font-bold transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer hover:bg-black/5 dark:hover:bg-white/5 shadow-xs"
          style={{ borderColor: 'var(--border-default)', color: 'var(--text-primary)' }}
          title="Next Page"
        >
          <span className="hidden sm:inline">Next</span>
          <ChevronRight size={14} />
        </button>
      </div>
    </div>
  );
};


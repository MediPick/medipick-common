'use client';

import React, { useState } from 'react';
import { Menu, X, ChevronRight, LogOut, Shield } from 'lucide-react';

export interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: string | number;
  badgeVariant?: 'default' | 'alert' | 'success';
}

interface SidebarLayoutProps {
  portalTitle: string;
  portalSubtitle?: string;
  navItems: NavItem[];
  activeId: string;
  onSelectNav: (id: string) => void;
  userProfile?: {
    name: string;
    role: string;
    email?: string;
  };
  onLogout?: () => void;
  children: React.ReactNode;
}

export const SidebarLayout: React.FC<SidebarLayoutProps> = ({
  portalTitle,
  portalSubtitle,
  navItems,
  activeId,
  onSelectNav,
  userProfile,
  onLogout,
  children
}) => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-[#0B1313] text-slate-100 font-['Plus_Jakarta_Sans']">
      {/* Mobile Drawer Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex flex-col border-r border-[#1F3335] bg-[#111D1E] transition-all duration-300 lg:static ${
          collapsed ? 'lg:w-20' : 'lg:w-64'
        } ${mobileOpen ? 'w-64 translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Header / Brand */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-[#1F3335]">
          {!collapsed && (
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#1D6F72] flex items-center justify-center text-[#C7E36B] font-bold text-sm shadow-md">
                MP
              </div>
              <div className="overflow-hidden">
                <h1 className="text-sm font-bold text-white truncate">{portalTitle}</h1>
                {portalSubtitle && <p className="text-[10px] text-slate-400 truncate">{portalSubtitle}</p>}
              </div>
            </div>
          )}

          <button
            onClick={() => {
              if (window.innerWidth < 1024) setMobileOpen(false);
              else setCollapsed(!collapsed);
            }}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#182728] transition-colors"
          >
            {collapsed ? <ChevronRight className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {navItems.map((item) => {
            const isActive = activeId === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectNav(item.id);
                  setMobileOpen(false);
                }}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[#1D6F72] text-white shadow-md shadow-[#1D6F72]/20 font-semibold'
                    : 'text-slate-400 hover:text-white hover:bg-[#182728]'
                } ${collapsed ? 'justify-center px-0' : ''}`}
                title={collapsed ? item.label : undefined}
              >
                <span className="flex-shrink-0 text-lg">{item.icon}</span>
                {!collapsed && <span className="truncate">{item.label}</span>}
                {!collapsed && item.badge !== undefined && (
                  <span
                    className={`ml-auto px-2 py-0.5 text-xs font-semibold rounded-full ${
                      item.badgeVariant === 'alert'
                        ? 'bg-rose-500/20 text-rose-300'
                        : item.badgeVariant === 'success'
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* User Profile & Logout Footer */}
        {userProfile && (
          <div className="p-3 border-t border-[#1F3335]">
            <div className={`flex items-center gap-3 p-2 rounded-xl bg-[#182728] ${collapsed ? 'justify-center' : ''}`}>
              <div className="w-9 h-9 rounded-full bg-[#1D6F72]/30 border border-[#1D6F72] flex items-center justify-center font-bold text-xs text-[#C7E36B] flex-shrink-0">
                {userProfile.name.charAt(0).toUpperCase()}
              </div>

              {!collapsed && (
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-white truncate">{userProfile.name}</p>
                  <span className="inline-block px-1.5 py-0.2 text-[10px] font-medium rounded bg-[#1D6F72]/30 text-teal-300 border border-[#1D6F72]/50">
                    {userProfile.role}
                  </span>
                </div>
              )}

              {onLogout && !collapsed && (
                <button
                  onClick={onLogout}
                  title="Sign out"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Top Navbar */}
        <header className="lg:hidden flex h-16 items-center justify-between px-4 border-b border-[#1F3335] bg-[#111D1E]">
          <button
            onClick={() => setMobileOpen(true)}
            className="p-2 rounded-lg text-slate-400 hover:text-white"
          >
            <Menu className="w-6 h-6" />
          </button>
          <span className="font-bold text-white text-sm">{portalTitle}</span>
          <div className="w-6" />
        </header>

        {/* Page Content */}
        <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

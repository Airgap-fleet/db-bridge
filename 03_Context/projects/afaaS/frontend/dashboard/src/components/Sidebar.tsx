// src/components/Sidebar.tsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '../lib/utils';

const navigation = [
  { name: 'Fleet', href: '/', icon: '🤖' },
  { name: 'Agents', href: '/agents', icon: '👥' },
  { name: 'Deployments', href: '/deployments', icon: '🚀' },
  { name: 'Metrics', href: '/metrics', icon: '📊' },
];

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  return (
    <div
      className={cn(
        'fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}
    >
      <div className="flex h-full flex-col bg-card border-r">
        <div className="p-6">
          <h2 className="text-xl font-bold">AFaaS Dashboard</h2>
          <p className="text-sm text-muted-foreground">Agent Fleet Management</p>
        </div>
        
        <nav className="flex-1 space-y-1 px-3">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  'flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )
              }
              onClick={() => window.innerWidth < 1024 && onClose()}
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
        
        <div className="p-6 border-t">
          <div className="text-xs text-muted-foreground">
            MCP Protocol v2026-07-28
          </div>
        </div>
      </div>
    </div>
  );
}
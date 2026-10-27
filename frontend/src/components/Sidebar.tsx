'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Users, MapPin, Server, Ticket, Wrench,
  Calendar, FileText, BookOpen, Bot, BarChart3, Settings,
  Shield, LogOut, ChevronRight,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import clsx from 'clsx';

const navItems = [
  { href: '/dashboard',     label: 'Overview',        icon: LayoutDashboard },
  { href: '/customers',     label: 'Customers',       icon: Users },
  { href: '/sites',         label: 'Sites',           icon: MapPin },
  { href: '/assets',        label: 'Assets',          icon: Server },
  { href: '/tickets',       label: 'Service Desk',    icon: Ticket },
  { href: '/technicians',   label: 'Technicians',     icon: Wrench },
  { href: '/maintenance',   label: 'Maintenance',     icon: Calendar },
  { href: '/contracts',     label: 'AMC Contracts',   icon: FileText },
  { href: '/knowledge',     label: 'Knowledge Base',  icon: BookOpen },
  { href: '/assistant',     label: 'AI Troubleshooting', icon: Bot },
  { href: '/reports',       label: 'Reports',         icon: BarChart3 },
  { href: '/settings',      label: 'Settings',        icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 left-0 w-60 bg-white border-r border-slate-100 flex flex-col z-30">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-slate-100">
        <div className="w-8 h-8 rounded-lg bg-teal-900 flex items-center justify-center flex-shrink-0">
          <Shield size={16} className="text-emerald-300" />
        </div>
        <div>
          <p className="text-teal-950 font-semibold text-sm leading-tight">FieldOps Assist</p>
          <p className="text-slate-400 text-xs leading-tight">IT & Security Platform</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link key={href} href={href}>
              <span className={clsx('nav-item', active && 'nav-item-active')}>
                <Icon size={16} className="flex-shrink-0" />
                <span className="flex-1">{label}</span>
                {active && <ChevronRight size={14} className="opacity-60" />}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* User */}
      {user && (
        <div className="px-3 py-4 border-t border-slate-100">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-semibold">
                {user.full_name.charAt(0)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-teal-950 text-xs font-medium truncate">{user.full_name}</p>
              <p className="text-slate-400 text-xs capitalize">{user.role}</p>
            </div>
            <button onClick={logout} className="text-slate-400 hover:text-teal-900 transition-colors" title="Sign out">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      )}
    </aside>
  );
}

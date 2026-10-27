'use client';

import { Bell, Search } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

interface HeaderProps {
  title: string;
  breadcrumbs?: Array<{ label: string; href?: string }>;
}

export function Header({ title, breadcrumbs }: HeaderProps) {
  const { user } = useAuth();

  return (
    <header className="h-16 bg-white border-b border-slate-100 flex items-center justify-between px-6 flex-shrink-0">
      <div>
        <h1 className="text-lg font-semibold text-teal-950">{title}</h1>
        {breadcrumbs && (
          <nav className="flex items-center gap-1 text-xs text-gray-500 mt-0.5">
            {breadcrumbs.map((b, i) => (
              <span key={i} className="flex items-center gap-1">
                {i > 0 && <span>/</span>}
                <span className={i === breadcrumbs.length - 1 ? 'text-gray-700 font-medium' : ''}>
                  {b.label}
                </span>
              </span>
            ))}
          </nav>
        )}
      </div>

      <div className="flex items-center gap-3">
        <div className="relative hidden sm:block">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            placeholder="Quick search..."
            className="pl-9 pr-4 py-1.5 text-sm border border-gray-200 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-52"
          />
        </div>
        <button className="relative w-9 h-9 rounded-lg border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition-colors">
          <Bell size={16} className="text-gray-600" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 bg-red-500 rounded-full" />
        </button>
        {user && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center">
              <span className="text-white text-xs font-semibold">{user.full_name.charAt(0)}</span>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

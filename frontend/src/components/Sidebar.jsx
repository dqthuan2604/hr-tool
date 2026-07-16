import { NavLink, useLocation } from 'react-router-dom';
import {
  FilePdf,
  Users,
  MagicWand,
  Lightning,
} from '@phosphor-icons/react';

const navItems = [
  { to: '/templates', label: 'Templates', icon: FilePdf, description: 'Mẫu CV' },
  { to: '/candidates', label: 'Candidates', icon: Users, description: 'Ứng viên' },
  { to: '/generator', label: 'Generator', icon: MagicWand, description: 'Tạo CV' },
];

export default function Sidebar() {
  return (
    <aside
      className="w-[240px] flex-shrink-0 h-screen flex flex-col"
      style={{
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border)',
      }}
    >
      {/* Brand */}
      <div className="px-5 pt-6 pb-5" style={{ borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="flex items-center gap-2.5">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{
              background: 'var(--accent-muted)',
              border: '1px solid var(--border-accent)',
            }}
          >
            <Lightning size={16} weight="fill" style={{ color: 'var(--accent-hover)' }} />
          </div>
          <div>
            <p className="text-sm font-bold" style={{ color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
              HR Tool
            </p>
            <p className="text-[10px]" style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              v1.0 beta
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, label, icon: Icon, description }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative ${
                isActive ? 'active-nav-item' : 'inactive-nav-item'
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? 'var(--accent-muted)' : 'transparent',
              borderLeft: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              color: isActive ? 'var(--accent-hover)' : 'var(--text-secondary)',
            })}
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={18}
                  weight={isActive ? 'fill' : 'regular'}
                  style={{ flexShrink: 0 }}
                />
                <div className="min-w-0">
                  <p
                    className="text-sm font-medium leading-none"
                    style={{ color: isActive ? 'var(--accent-hover)' : 'var(--text-primary)' }}
                  >
                    {label}
                  </p>
                  <p
                    className="text-[10px] mt-0.5"
                    style={{ color: isActive ? 'var(--accent-muted)' : 'var(--text-muted)' }}
                  >
                    {description}
                  </p>
                </div>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div
        className="px-5 py-4"
        style={{ borderTop: '1px solid var(--border-subtle)' }}
      >
        <div
          className="flex items-center gap-2 text-[11px] px-2 py-1.5 rounded-lg"
          style={{ background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.15)' }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full flex-shrink-0"
            style={{ background: '#4ade80', boxShadow: '0 0 4px #4ade80' }}
          />
          <span style={{ color: '#4ade80', fontFamily: 'var(--font-mono)' }}>System online</span>
        </div>
      </div>
    </aside>
  );
}

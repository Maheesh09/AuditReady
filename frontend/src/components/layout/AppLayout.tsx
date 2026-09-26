import {
  ClipboardList,
  FileText,
  LayoutDashboard,
  ListChecks,
  ScrollText,
  TriangleAlert,
  type LucideIcon,
} from 'lucide-react'
import { NavLink, Outlet } from 'react-router-dom'

import { cn } from '@/lib/utils'

type NavItem = { to: string; label: string; icon: LucideIcon }

// The demo questionnaire id is wired in once questionnaires load from the API (FE-09).
const NAV: NavItem[] = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/documents', label: 'Documents', icon: FileText },
  { to: '/review', label: 'Review queue', icon: ListChecks },
  { to: '/questionnaires/demo', label: 'Questionnaire', icon: ClipboardList },
  { to: '/gaps', label: 'Gaps', icon: TriangleAlert },
  { to: '/access-log', label: 'Access log', icon: ScrollText },
]

export function AppLayout() {
  return (
    <div className="flex min-h-full">
      <aside className="border-line bg-surface w-60 shrink-0 border-r">
        <div className="text-brand px-6 py-5 text-lg font-semibold">AuditReady</div>
        <nav aria-label="Main" className="flex flex-col gap-1 px-3">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                cn(
                  'text-muted hover:bg-canvas flex items-center gap-3 rounded-md px-3 py-2 text-sm',
                  isActive && 'bg-canvas text-ink font-medium',
                )
              }
            >
              <Icon aria-hidden className="size-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 px-8 py-6">
        <Outlet />
      </main>
    </div>
  )
}

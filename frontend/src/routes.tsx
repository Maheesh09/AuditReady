import type { RouteObject } from 'react-router-dom'

import { AppLayout } from '@/components/layout/AppLayout'
import { AccessLogPage } from '@/pages/AccessLogPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { DocumentDetailPage } from '@/pages/DocumentDetailPage'
import { DocumentsPage } from '@/pages/DocumentsPage'
import { GapsPage } from '@/pages/GapsPage'
import { LoginPage } from '@/pages/LoginPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { QuestionnairePage } from '@/pages/QuestionnairePage'
import { ReviewPage } from '@/pages/ReviewPage'

/**
 * Routes from Section 13.1. The citation panel (screen 7) is a panel inside the
 * questionnaire screen, not a route. Auth guard is added in FE-02.
 */
export const routes: RouteObject[] = [
  { path: '/login', element: <LoginPage /> },
  {
    element: <AppLayout />,
    children: [
      { path: '/', element: <DashboardPage /> },
      { path: '/documents', element: <DocumentsPage /> },
      { path: '/documents/:id', element: <DocumentDetailPage /> },
      { path: '/review', element: <ReviewPage /> },
      { path: '/questionnaires/:id', element: <QuestionnairePage /> },
      { path: '/gaps', element: <GapsPage /> },
      { path: '/access-log', element: <AccessLogPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
]

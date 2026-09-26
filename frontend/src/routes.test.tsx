import { render, screen } from '@testing-library/react'
import { RouterProvider, createMemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import { routes } from '@/routes'

const renderAt = (path: string) =>
  render(<RouterProvider router={createMemoryRouter(routes, { initialEntries: [path] })} />)

describe('routes (Section 13.1)', () => {
  it.each([
    ['/login', 'Sign in to AuditReady'],
    ['/', 'Dashboard'],
    ['/documents', 'Documents'],
    ['/documents/abc', 'Document detail'],
    ['/review', 'Review queue'],
    ['/questionnaires/demo', 'Questionnaire'],
    ['/gaps', 'Gaps'],
    ['/access-log', 'Access log'],
    ['/nope', 'Page not found'],
  ])('%s renders "%s"', (path, heading) => {
    renderAt(path)
    expect(screen.getByRole('heading', { level: 1, name: heading })).toBeInTheDocument()
  })

  it('shows the sidebar on app pages', () => {
    renderAt('/documents')
    expect(screen.getByRole('navigation', { name: 'Main' })).toBeInTheDocument()
  })

  it('hides the sidebar on the login page', () => {
    renderAt('/login')
    expect(screen.queryByRole('navigation', { name: 'Main' })).not.toBeInTheDocument()
  })
})

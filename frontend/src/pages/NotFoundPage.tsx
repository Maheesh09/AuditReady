import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <section>
      <h1 className="text-2xl font-semibold">Page not found</h1>
      <p className="text-muted mt-2">
        This page does not exist.{' '}
        <Link className="text-brand underline" to="/">
          Go to the dashboard
        </Link>
      </p>
    </section>
  )
}

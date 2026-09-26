type Props = {
  title: string
  purpose: string
  /** Backlog task IDs that will build this screen (Section 18). */
  tasks: string[]
}

/** Temporary screen used until the real feature lands. Delete once every route is built. */
export function PagePlaceholder({ title, purpose, tasks }: Props) {
  return (
    <section>
      <h1 className="text-2xl font-semibold">{title}</h1>
      <p className="text-muted mt-2 max-w-prose">{purpose}</p>
      <p className="text-muted mt-4 text-sm">Built in: {tasks.join(', ')}</p>
    </section>
  )
}

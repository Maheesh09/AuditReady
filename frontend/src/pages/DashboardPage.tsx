import { PagePlaceholder } from '@/components/PagePlaceholder'

export function DashboardPage() {
  return (
    <PagePlaceholder
      title="Dashboard"
      purpose="Document status, fields by confidence tier, pending reviews and open gaps at a glance."
      tasks={['FE-15']}
    />
  )
}

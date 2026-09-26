import { PagePlaceholder } from '@/components/PagePlaceholder'

export function GapsPage() {
  return (
    <PagePlaceholder
      title="Gaps"
      purpose="Expired and expiring certificates, missing months, pending reviews and unanswered questions."
      tasks={['FE-15']}
    />
  )
}

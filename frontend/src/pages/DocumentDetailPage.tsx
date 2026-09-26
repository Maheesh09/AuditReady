import { PagePlaceholder } from '@/components/PagePlaceholder'

export function DocumentDetailPage() {
  return (
    <PagePlaceholder
      title="Document detail"
      purpose="The original page with extracted fields highlighted, or the facts and hash if the original was deleted."
      tasks={['FE-05', 'FE-07', 'FE-12']}
    />
  )
}

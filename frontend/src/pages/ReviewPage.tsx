import { PagePlaceholder } from '@/components/PagePlaceholder'

export function ReviewPage() {
  return (
    <PagePlaceholder
      title="Review queue"
      purpose="Confirm, correct or reject values the system was not sure about."
      tasks={['FE-08']}
    />
  )
}

import { PagePlaceholder } from '@/components/PagePlaceholder'

export function QuestionnairePage() {
  return (
    <PagePlaceholder
      title="Questionnaire"
      purpose="Generate answers to the buyer questionnaire, each linked to its source document and page."
      tasks={['FE-09', 'FE-10', 'FE-11', 'FE-17']}
    />
  )
}

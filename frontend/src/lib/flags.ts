/**
 * Environment-based feature flags (Section 4.6).
 * Unfinished features merge to main switched off.
 */
const on = (value: string | undefined) => value === 'true'

export const flags = {
  exportXlsx: on(import.meta.env.VITE_FEATURE_EXPORT_XLSX),
} as const

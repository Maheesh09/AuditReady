import js from '@eslint/js'
import { defineConfig, globalIgnores } from 'eslint/config'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import globals from 'globals'
import tseslint from 'typescript-eslint'

export default defineConfig([
  globalIgnores(['dist', 'src/api/schema.d.ts']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: { ecmaVersion: 2022, globals: globals.browser },
    rules: {
      // Section 4.4: no `any` unless commented with a reason (use eslint-disable-next-line + reason)
      '@typescript-eslint/no-explicit-any': 'error',
      // Definition of Done: no console.log left in code
      'no-console': ['error', { allow: ['warn', 'error'] }],
    },
  },
])

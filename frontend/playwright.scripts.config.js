import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  testMatch: 'project-scripts.spec.js',
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
})

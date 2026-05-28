import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    include: ['test_*.ts'],
    environment: 'node',
    reporters: ['verbose'],
    globals: false,
  },
})

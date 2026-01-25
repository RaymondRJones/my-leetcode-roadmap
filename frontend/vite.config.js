import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  root: 'src',
  build: {
    outDir: '../../static/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        styles: resolve(__dirname, 'src/styles/main.css'),
        'theme-toggle': resolve(__dirname, 'src/js/theme-toggle.js')
      },
      output: {
        entryFileNames: 'js/[name].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name.endsWith('.css')) {
            return 'css/[name][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        }
      }
    }
  },
  css: {
    postcss: resolve(__dirname, 'postcss.config.js')
  }
})

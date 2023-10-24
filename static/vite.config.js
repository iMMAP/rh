import { defineConfig } from 'vite';
import inject from '@rollup/plugin-inject';
import {djangoVitePlugin } from "django-vite-plugin";


export default defineConfig({
  plugins: [
    inject({
      // that should be first under plugins array
      $: 'jquery',
      jQuery: 'jquery',
    }),

    djangoVitePlugin({
      input: ["./src/js/app.js", "./src/styles/style.scss"],
      root:"..",
    }),
    
  ],
});

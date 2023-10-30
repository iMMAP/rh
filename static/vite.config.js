import { defineConfig } from "vite";
import { djangoVitePlugin } from "django-vite-plugin";

export default defineConfig({
  plugins: [
    djangoVitePlugin({
      input: [
        "src/styles/style.scss", 
        "src/js/app.js", 

        // relative to the folder that vite.config is located
        "../stock/static/stock/stock.js",
      ],
      root: "..",
    }),
  ],
});

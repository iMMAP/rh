import { defineConfig } from "vite";
import { djangoVitePlugin } from "django-vite-plugin";

export default defineConfig({
  plugins: [
    djangoVitePlugin({
      input: [
        "src/styles/style.scss", 
        "src/js/app.js", 
        "src/js/utils/initSentry.js", 
        "../rh/static/rh/project_planning.js",

        // relative to the folder that vite.config is located
        // "../users/static/users/users.js",
      ],
      root: "..",
    }),
  ],
});

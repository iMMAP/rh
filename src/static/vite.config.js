import { defineConfig } from "vite";
import { djangoVitePlugin } from "django-vite-plugin";

export default defineConfig({
  plugins: [
    djangoVitePlugin({
      input: [
        "src/styles/style.scss", 
        "src/js/app.js", 
        "rh/js/project_planning.js",

        // relative to the folder that vite.config is located
        "../users/static/users/users.js",
      ],
      root: "..",
    }),
  ],
});

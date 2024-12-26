import { defineConfig } from "vite"
import { resolve } from "node:path"

export default defineConfig({
	build: {
		manifest: false,
		// outDir: resolve(__dirname, "dist"),
		emptyOutDir: true,
		assetsDir: "",
		rollupOptions: {
			input: [
				resolve(__dirname, "js/app.js"),
				resolve(__dirname, "styles/style.scss"),
				resolve(__dirname, "js/utils/initSentry.js"),
      ],
      output: {
        entryFileNames: "[name].js",
        chunkFileNames: "[name].js",
        assetFileNames: "[name].[ext]",
      },
		},
	},
});
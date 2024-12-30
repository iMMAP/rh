import { defineConfig } from "vite"
import { resolve } from "path"

export default defineConfig({
	build: {
		manifest: false,
		outDir: resolve(__dirname, "src/static/dist"),
		emptyOutDir: true,
		assetsDir: "",
		rollupOptions: {
			input: [
				resolve(__dirname, "src/static/js/app.js"),
				resolve(__dirname, "src/static/styles/style.scss"),
			],
			output: {
				entryFileNames: "[name].js",
				chunkFileNames: "[name].js",
				assetFileNames: "[name].[ext]",
			},
		},
	},
});
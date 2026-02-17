import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import frappeui from 'frappe-ui/vite'
import path from 'path'
import { defineConfig } from 'vite'
import Icons from 'unplugin-icons/vite'

export default defineConfig({
	plugins: [
		frappeui({
			frappeProxy: true,
			lucideIcons: false,
			jinjaBootData: true,
			buildConfig: false,
		}),
		Icons({
			compiler: 'vue3',
		}),
		vue(),
		vueJsx(),
	],
	server: {
		allowedHosts: true,
	},
	esbuild: { loader: 'tsx' },
	resolve: {
		alias: {
			// https://github.com/vitejs/vite/discussions/16730#discussioncomment-13048825
			vue: 'vue/dist/vue.esm-bundler.js',
			'@': path.resolve(__dirname, 'src2'),
			'tailwind.config.js': path.resolve(__dirname, 'tailwind.config.js'),
		},
	},
	build: {
		outDir: `../insights/public/frontend`,
		emptyOutDir: true,
		sourcemap: false, // Disabled in production — saves ~30% bundle size
		rollupOptions: {
			input: {
				main: path.resolve(__dirname, 'index.html'),
			},
			output: {
				manualChunks: {
					'frappe-ui': ['frappe-ui'],
					'echarts': ['echarts'],
					'codemirror': ['codemirror', '@codemirror/lang-sql', '@codemirror/lang-python'],
					'vue-flow': ['@vue-flow/core'],
				},
			},
		},
	},
	optimizeDeps: {
		include: ['feather-icons', 'showdown', 'tailwind.config.js', 'highlight.js/lib/core'],
	},
	define: {
		// enable hydration mismatch details in production build
		__VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'true',
	},
})

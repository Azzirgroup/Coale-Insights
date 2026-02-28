<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { call } from 'frappe-ui'
import SettingItem from './SettingItem.vue'
import useSettings from './settings'
import { createToast } from '../helpers/toasts'

const settings = useSettings()
settings.load()

const isTesting = ref(false)
const ollamaModels = ref<string[]>([])

const aiStatus = ref({
	enabled: false,
	configured: false,
	provider: 'openrouter',
	quota_used: 0,
	daily_quota: 100,
	last_refresh: null as string | null
})

async function fetchAIStatus() {
	try {
		const response = await call('insights.ai.openrouter_client.get_ai_status')
		if (response) aiStatus.value = response
	} catch (error) {
		console.error('Failed to fetch AI status:', error)
	}
}

const selectedProvider = computed(() => settings.doc.ai_provider || 'openrouter')

const providerOptions = [
	{ value: 'openrouter', label: 'OpenRouter', icon: 'cloud', desc: 'Cloud AI with free & paid models' },
	{ value: 'ollama', label: 'Ollama', icon: 'server', desc: 'Local AI, no API key needed' },
]

const modelOptions = [
	{ group: 'Free Models', options: [
		{ value: 'mistralai/mistral-small-3.1-24b-instruct:free', label: 'Mistral Small 3.1 24B' },
		{ value: 'google/gemma-3-27b-it:free', label: 'Gemma 3 27B' },
		{ value: 'meta-llama/llama-3.3-70b-instruct:free', label: 'Llama 3.3 70B' },
		{ value: 'qwen/qwen3-coder:free', label: 'Qwen3 Coder' },
		{ value: 'openai/gpt-oss-120b:free', label: 'GPT-OSS 120B' },
		{ value: 'nousresearch/hermes-3-llama-3.1-405b:free', label: 'Hermes 3 405B' },
		{ value: 'google/gemma-3-12b-it:free', label: 'Gemma 3 12B' },
		{ value: 'nvidia/nemotron-3-nano-30b-a3b:free', label: 'Nemotron 3 Nano 30B' },
		{ value: 'qwen/qwen3-next-80b-a3b-instruct:free', label: 'Qwen3 Next 80B' },
		{ value: 'openai/gpt-oss-20b:free', label: 'GPT-OSS 20B' },
		{ value: 'deepseek/deepseek-r1-0528:free', label: 'DeepSeek R1' },
		{ value: 'google/gemini-2.0-flash-exp:free', label: 'Gemini 2.0 Flash' },
		{ value: 'qwen/qwen3-235b-a22b:free', label: 'Qwen3 235B' },
	]},
	{ group: 'Paid Models', options: [
		{ value: 'openai/gpt-4o-mini', label: 'GPT-4o Mini' },
		{ value: 'openai/gpt-4o', label: 'GPT-4o' },
		{ value: 'anthropic/claude-3.5-sonnet', label: 'Claude 3.5 Sonnet' },
	]}
]

const scheduleOptions = [
	{ value: 'Disabled', label: 'Disabled' },
	{ value: 'Daily', label: 'Daily' },
	{ value: 'Weekly', label: 'Weekly' },
	{ value: 'Monthly', label: 'Monthly' },
]

const quotaPercent = computed(() => {
	const used = aiStatus.value.quota_used || 0
	const total = settings.doc.daily_ai_quota || 100
	return Math.min(100, (used / total) * 100)
})

const quotaColor = computed(() => {
	if (quotaPercent.value >= 90) return 'bg-red-500'
	if (quotaPercent.value >= 70) return 'bg-amber-500'
	return 'bg-blue-500'
})

function formatDate(dateStr: string | null) {
	if (!dateStr) return 'Never'
	const date = new Date(dateStr)
	return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

async function testConnection() {
	const provider = settings.doc.ai_provider || 'openrouter'

	if (provider === 'openrouter' && !settings.doc.openrouter_api_key) {
		createToast({ title: 'API Key Required', message: 'Enter your OpenRouter API key first', variant: 'warning' })
		return
	}

	isTesting.value = true
	try {
		const response = await call('insights.ai.openrouter_client.test_connection', { provider })

		if (response?.success) {
			const msg = provider === 'ollama'
				? `Connected. ${response.data?.model_count || 0} models available.`
				: 'Connection successful'

			// If Ollama, populate discovered models
			if (provider === 'ollama' && response.data?.models) {
				ollamaModels.value = response.data.models
			}

			createToast({ title: 'Connected', message: msg, variant: 'success' })
		} else {
			createToast({ title: 'Connection Failed', message: response?.error || 'Unable to connect', variant: 'error' })
		}
	} catch (error: any) {
		createToast({ title: 'Error', message: error.message || 'Connection test failed', variant: 'error' })
	} finally {
		isTesting.value = false
	}
}

async function fetchOllamaModels() {
	try {
		const response = await call('insights.ai.openrouter_client.test_connection', { provider: 'ollama' })
		if (response?.success && response.data?.models) {
			ollamaModels.value = response.data.models
		}
	} catch { /* silent */ }
}

watch(selectedProvider, (val) => {
	if (val === 'ollama' && ollamaModels.value.length === 0) {
		fetchOllamaModels()
	}
})

onMounted(() => {
	fetchAIStatus()
	if (selectedProvider.value === 'ollama') {
		fetchOllamaModels()
	}
})
</script>

<template>
	<div class="flex w-full flex-col gap-6 overflow-y-scroll p-8 px-10">
		<!-- Header -->
		<div class="flex items-center justify-between">
			<div>
				<h1 class="text-xl font-semibold text-gray-900">AI Analytics</h1>
				<p class="text-sm text-gray-500 mt-1">Configure AI-powered insights for your dashboards</p>
			</div>
			<Badge
				v-if="settings.doc.enable_ai_analytics"
				variant="subtle"
				theme="green"
				size="md"
			>Active</Badge>
			<Badge v-else variant="subtle" theme="gray" size="md">Inactive</Badge>
		</div>

		<!-- Enable Toggle -->
		<SettingItem
			label="Enable AI Analytics"
			description="Use AI to generate insights, narratives, and recommendations across dashboards."
		>
			<FormControl
				type="checkbox"
				v-model="settings.doc.enable_ai_analytics"
				:label="settings.doc.enable_ai_analytics ? 'On' : 'Off'"
			/>
		</SettingItem>

		<template v-if="settings.doc.enable_ai_analytics">
			<!-- Provider Selection -->
			<div class="border-t pt-6">
				<h2 class="text-base font-medium text-gray-800 mb-3">Provider</h2>
				<div class="grid grid-cols-2 gap-3">
					<label
						v-for="p in providerOptions"
						:key="p.value"
						class="relative flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition-all"
						:class="selectedProvider === p.value
							? 'border-blue-500 bg-blue-50/50 ring-1 ring-blue-200'
							: 'border-gray-200 hover:border-gray-300 hover:bg-gray-50/50'"
					>
						<input
							type="radio"
							:value="p.value"
							v-model="settings.doc.ai_provider"
							class="mt-0.5 text-blue-600"
						/>
						<div class="flex-1 min-w-0">
							<div class="font-medium text-sm text-gray-900">{{ p.label }}</div>
							<div class="text-xs text-gray-500 mt-0.5">{{ p.desc }}</div>
						</div>
					</label>
				</div>
			</div>

			<!-- OpenRouter Config -->
			<div v-if="selectedProvider === 'openrouter'" class="border-t pt-6 space-y-5">
				<h2 class="text-base font-medium text-gray-800">OpenRouter Settings</h2>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1.5">API Key</label>
					<div class="flex gap-2">
						<FormControl
							type="password"
							v-model="settings.doc.openrouter_api_key"
							placeholder="sk-or-v1-..."
							class="flex-1"
						/>
						<Button
							variant="outline"
							:loading="isTesting"
							@click="testConnection"
						>Test</Button>
					</div>
					<p class="text-xs text-gray-400 mt-1">Get your key at openrouter.ai/keys</p>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1.5">Primary Model</label>
						<select
							v-model="settings.doc.ai_model"
							class="w-full rounded-md border border-gray-300 px-3 py-[7px] text-sm bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
						>
							<optgroup v-for="group in modelOptions" :key="group.group" :label="group.group">
								<option v-for="opt in group.options" :key="opt.value" :value="opt.value">
									{{ opt.label }}
								</option>
							</optgroup>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1.5">Fallback Model</label>
						<select
							v-model="settings.doc.ai_model_fallback"
							class="w-full rounded-md border border-gray-300 px-3 py-[7px] text-sm bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
						>
							<optgroup v-for="group in modelOptions" :key="group.group" :label="group.group">
								<option v-for="opt in group.options" :key="opt.value" :value="opt.value">
									{{ opt.label }}
								</option>
							</optgroup>
						</select>
					</div>
				</div>
			</div>

			<!-- Ollama Config -->
			<div v-if="selectedProvider === 'ollama'" class="border-t pt-6 space-y-5">
				<div>
					<h2 class="text-base font-medium text-gray-800">Ollama Settings</h2>
					<p class="text-xs text-gray-500 mt-1">Runs locally on your machine. Make sure Ollama is running before testing.</p>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1.5">Base URL</label>
						<div class="flex gap-2">
							<FormControl
								type="text"
								v-model="settings.doc.ollama_base_url"
								placeholder="http://localhost:11434"
								class="flex-1"
							/>
							<Button
								variant="outline"
								:loading="isTesting"
								@click="testConnection"
							>Test</Button>
						</div>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1.5">Model</label>
						<FormControl
							v-if="ollamaModels.length === 0"
							type="text"
							v-model="settings.doc.ollama_model"
							placeholder="llama3.1"
						/>
						<select
							v-else
							v-model="settings.doc.ollama_model"
							class="w-full rounded-md border border-gray-300 px-3 py-[7px] text-sm bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
						>
							<option v-for="m in ollamaModels" :key="m" :value="m">{{ m }}</option>
						</select>
						<p class="text-xs text-gray-400 mt-1">
							{{ ollamaModels.length > 0 ? `${ollamaModels.length} models detected` : 'Test connection to discover models' }}
						</p>
					</div>
				</div>
			</div>

			<!-- Schedule & Quota -->
			<div class="border-t pt-6 space-y-5">
				<h2 class="text-base font-medium text-gray-800">Schedule & Limits</h2>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1.5">Auto Refresh</label>
						<select
							v-model="settings.doc.refresh_schedule"
							class="w-full rounded-md border border-gray-300 px-3 py-[7px] text-sm bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none"
						>
							<option v-for="opt in scheduleOptions" :key="opt.value" :value="opt.value">
								{{ opt.label }}
							</option>
						</select>
					</div>
					<div>
						<label class="block text-sm font-medium text-gray-700 mb-1.5">Daily Quota</label>
						<div class="flex items-center gap-2">
							<FormControl
								type="number"
								v-model="settings.doc.daily_ai_quota"
								:min="1"
								class="w-24"
							/>
							<span class="text-sm text-gray-500">requests/day</span>
						</div>
					</div>
				</div>
			</div>

			<!-- Usage Status -->
			<div class="border-t pt-6">
				<h2 class="text-base font-medium text-gray-800 mb-3">Usage</h2>
				<div class="grid grid-cols-3 gap-3">
					<div class="rounded-lg border border-gray-100 bg-gray-50/70 p-3.5">
						<p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Quota Today</p>
						<p class="text-lg font-semibold text-gray-900 mt-1">
							{{ aiStatus.quota_used || 0 }}<span class="text-sm font-normal text-gray-400"> / {{ settings.doc.daily_ai_quota || 100 }}</span>
						</p>
						<div class="mt-2 w-full bg-gray-200 rounded-full h-1.5">
							<div
								:class="[quotaColor, 'h-1.5 rounded-full transition-all']"
								:style="`width: ${quotaPercent}%`"
							></div>
						</div>
					</div>
					<div class="rounded-lg border border-gray-100 bg-gray-50/70 p-3.5">
						<p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Last Refresh</p>
						<p class="text-sm font-medium text-gray-900 mt-1">
							{{ formatDate(aiStatus.last_refresh) }}
						</p>
					</div>
					<div class="rounded-lg border border-gray-100 bg-gray-50/70 p-3.5">
						<p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Provider</p>
						<p class="text-sm font-medium text-gray-900 mt-1 capitalize">
							{{ selectedProvider === 'openrouter' ? 'OpenRouter' : 'Ollama' }}
						</p>
					</div>
				</div>
			</div>
		</template>

		<!-- Save Button -->
		<div class="flex justify-end border-t pt-4">
			<Button
				label="Save"
				variant="solid"
				:disabled="!settings.isdirty"
				:loading="settings.saving"
				@click="() => settings.save()"
			/>
		</div>
	</div>
</template>

<template>
	<header class="sticky top-0 z-10 flex items-center justify-between bg-white px-5 py-2.5">
		<PageBreadcrumbs class="h-7" :items="[{ label: 'Settings' }]" />
		<div class="space-x-2.5">
			<Button
				label="Update"
				:disabled="updateDisabled"
				variant="solid"
				@click="store.update(configurables)"
			>
				<template #prefix>
					<CheckIcon class="w-4" />
				</template>
			</Button>
		</div>
	</header>
	<div class="flex flex-1 space-y-4 overflow-hidden bg-white px-6 py-2">
		<div class="-m-1 flex flex-1 flex-col space-y-6 overflow-y-auto p-1">
			<div class="rounded bg-white p-6 shadow">
				<div class="flex items-baseline">
					<div class="text-xl font-medium text-gray-700">General</div>
				</div>
				<div class="mt-4 flex flex-col space-y-8">
					<Setting
						label="Max Query Result Limit"
						description="Maximum number of rows to be returned by a query. This is to prevent long running queries and memory issues."
					>
						<Input type="number" min="0" v-model="configurables.query_result_limit" />
						<div class="ml-2 text-gray-600">Rows</div>
					</Setting>

					<Setting
						label="Cache Query Results For"
						description="Number of minutes to cache query results. This is to prevent accidental running of the same query multiple times."
					>
						<Input type="number" min="0" v-model="configurables.query_result_expiry" />
						<div class="ml-2 text-gray-600">Minutes</div>
					</Setting>

					<Setting
						label="Fiscal Year Start"
						description="Start of the fiscal year. This is used to calculate fiscal year for date columns."
					>
						<DatePicker
							placeholder="Select Date"
							:value="configurables.fiscal_year_start"
							@change="configurables.fiscal_year_start = $event"
						/>
					</Setting>

					<Setting
						label="Auto Execute Query"
						description="Automatically execute when tables, columns, or filters are changed."
					>
						<Input
							type="checkbox"
							v-model="configurables.auto_execute_query"
							:label="configurables.auto_execute_query ? 'Enabled' : 'Disabled'"
						/>
					</Setting>

					<Setting
						label="Enable Query Reusability"
						description="Allow selecting query as a table in another query. Any query selected as a table will be appended as a sub query using CTE (Common Table Expression)."
					>
						<Input
							type="checkbox"
							v-model="configurables.allow_subquery"
							:label="configurables.allow_subquery ? 'Enabled' : 'Disabled'"
						/>
					</Setting>
				</div>
			</div>

			<!-- AI Analytics Section -->
			<div class="rounded bg-white p-6 shadow">
				<div class="flex items-baseline justify-between">
					<div class="text-xl font-medium text-gray-700">
						<BrainIcon class="inline-block w-5 h-5 mr-2 text-purple-500" />
						AI Analytics
					</div>
					<Badge v-if="aiStatus.configured" variant="subtle" theme="green">Configured</Badge>
					<Badge v-else variant="subtle" theme="orange">Not Configured</Badge>
				</div>
				<div class="mt-4 flex flex-col space-y-8">
					<Setting
						label="Enable AI Analytics"
						description="Enable ML-powered analytics with AI-generated insights for dashboards."
					>
						<Input
							type="checkbox"
							v-model="configurables.enable_ai_analytics"
							:label="configurables.enable_ai_analytics ? 'Enabled' : 'Disabled'"
						/>
					</Setting>

					<div v-if="configurables.enable_ai_analytics" class="flex flex-col space-y-8">
						<Setting
							label="OpenRouter API Key"
							description="Get your API key from https://openrouter.ai/keys. Required for AI-powered analytics."
						>
							<Input
								type="password"
								v-model="configurables.openrouter_api_key"
								placeholder="sk-or-v1-..."
								class="w-full"
							/>
						</Setting>

						<div class="grid grid-cols-2 gap-6">
							<Setting
								label="Primary AI Model"
								description="Main model for generating insights. Free models recommended for cost efficiency."
							>
								<select
									v-model="configurables.ai_model"
									class="form-select rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
								>
									<optgroup label="Free Models (Recommended)">
										<option value="meta-llama/llama-3.3-70b-instruct:free">Llama 3.3 70B (Free) ⭐</option>
										<option value="openai/gpt-oss-120b:free">OpenAI GPT-OSS 120B (Free)</option>
										<option value="google/gemini-2.0-flash-exp:free">Gemini 2.0 Flash (Free)</option>
										<option value="qwen/qwen3-235b-a22b:free">Qwen3 235B (Free)</option>
										<option value="mistralai/mistral-small-3.1-24b-instruct:free">Mistral Small 3.1 24B (Free)</option>
										<option value="nousresearch/hermes-3-llama-3.1-405b:free">Hermes 3 Llama 405B (Free)</option>
									</optgroup>
									<optgroup label="Paid Models">
										<option value="openai/gpt-4o-mini">GPT-4o Mini</option>
										<option value="openai/gpt-4o">GPT-4o</option>
										<option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
									</optgroup>
								</select>
							</Setting>

							<Setting
								label="Fallback AI Model"
								description="Used when primary model fails or is rate-limited."
							>
								<select
									v-model="configurables.ai_model_fallback"
									class="form-select rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
								>
									<optgroup label="Free Models (Recommended)">
										<option value="meta-llama/llama-3.3-70b-instruct:free">Llama 3.3 70B (Free) ⭐</option>
										<option value="openai/gpt-oss-120b:free">OpenAI GPT-OSS 120B (Free)</option>
										<option value="google/gemini-2.0-flash-exp:free">Gemini 2.0 Flash (Free)</option>
										<option value="qwen/qwen3-235b-a22b:free">Qwen3 235B (Free)</option>
										<option value="mistralai/mistral-small-3.1-24b-instruct:free">Mistral Small 3.1 24B (Free)</option>
										<option value="nousresearch/hermes-3-llama-3.1-405b:free">Hermes 3 Llama 405B (Free)</option>
									</optgroup>
									<optgroup label="Paid Models">
										<option value="openai/gpt-4o-mini">GPT-4o Mini</option>
										<option value="openai/gpt-4o">GPT-4o</option>
										<option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</option>
									</optgroup>
								</select>
							</Setting>
						</div>

						<div class="border-t pt-6">
							<div class="text-lg font-medium text-gray-600 mb-4">Scheduling & Quotas</div>
							<div class="grid grid-cols-2 gap-6">
								<Setting
									label="Auto Refresh Schedule"
									description="Automatically refresh AI insights on a schedule."
								>
									<select
										v-model="configurables.refresh_schedule"
										class="form-select rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
									>
										<option value="Disabled">Disabled</option>
										<option value="Daily">Daily</option>
										<option value="Weekly">Weekly</option>
										<option value="Monthly">Monthly</option>
									</select>
								</Setting>

								<Setting
									label="Daily AI Request Quota"
									description="Maximum AI requests per day to control costs."
								>
									<Input type="number" min="1" v-model="configurables.daily_ai_quota" />
									<div class="ml-2 text-gray-600">requests/day</div>
								</Setting>
							</div>
						</div>

						<!-- AI Status Display -->
						<div class="border-t pt-6">
							<div class="text-lg font-medium text-gray-600 mb-4">Status</div>
							<div class="grid grid-cols-3 gap-4">
								<div class="bg-gray-50 rounded p-4">
									<div class="text-sm text-gray-500">Quota Used Today</div>
									<div class="text-2xl font-semibold text-gray-800">
										{{ aiStatus.quota_used || 0 }} / {{ aiStatus.daily_quota || 100 }}
									</div>
								</div>
								<div class="bg-gray-50 rounded p-4">
									<div class="text-sm text-gray-500">Last Refresh</div>
									<div class="text-lg font-medium text-gray-800">
										{{ aiStatus.last_refresh ? formatDate(aiStatus.last_refresh) : 'Never' }}
									</div>
								</div>
								<div class="bg-gray-50 rounded p-4">
									<div class="text-sm text-gray-500">Primary Model</div>
									<div class="text-lg font-medium text-gray-800 truncate">
										{{ getModelDisplayName(configurables.ai_model) }}
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="rounded bg-white p-6 shadow">
				<div class="flex items-baseline">
					<div class="text-xl font-medium text-gray-700">Notifications</div>
				</div>
				<div class="mt-4 flex flex-col space-y-8">
					<Setting
						label="Telegram Bot Token"
						description="Telegram bot token to send notifications to Telegram."
					>
						<Input
							type="password"
							v-model="configurables.telegram_api_token"
							placeholder="Telegram Bot Token"
						/>
					</Setting>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import DatePicker from '@/components/Controls/DatePicker.vue'
import PageBreadcrumbs from '@/components/PageBreadcrumbs.vue'
import Setting from '@/components/Setting.vue'
import settingsStore from '@/stores/settingsStore'
import { CheckIcon, BrainIcon } from 'lucide-vue-next'
import { Badge } from 'frappe-ui'
import { computed, ref, watchEffect, onMounted } from 'vue'
import { call } from 'frappe-ui'

const initialValues = {
	query_result_limit: 1000,
	query_result_expiry: 60,
	auto_execute_query: true,
	allow_subquery: true,
	fiscal_year_start: null,
	telegram_api_token: '',
	enable_ai_analytics: false,
	openrouter_api_key: '',
	ai_model: 'meta-llama/llama-3.1-8b-instruct:free',
	ai_model_fallback: 'mistralai/mistral-7b-instruct:free',
	refresh_schedule: 'Daily',
	daily_ai_quota: 100,
}

const configurables = ref(initialValues)
const aiStatus = ref({
	enabled: false,
	configured: false,
	quota_used: 0,
	daily_quota: 100,
	last_refresh: null
})

const store = settingsStore()

watchEffect(() => {
	if (store.settings) {
		Object.keys(configurables.value).forEach((key) => {
			configurables.value[key] = store.settings[key]
		})
	} else {
		configurables.value = initialValues
	}
})

const updateDisabled = computed(() => {
	const local = configurables.value
	const remote = store.settings
	if (!local || !remote) return true
	return (
		Object.keys(local).find((key) => local[key] !== remote[key]) === undefined ||
		store.settings.loading
	)
})

// Fetch AI status
async function fetchAIStatus() {
	try {
		const response = await call('insights.ai.openrouter_client.get_ai_status')
		if (response) {
			aiStatus.value = response
		}
	} catch (error) {
		console.error('Failed to fetch AI status:', error)
	}
}

// Model display names
function getModelDisplayName(model) {
	const names = {
		'meta-llama/llama-3.1-8b-instruct:free': 'Llama 3.1 8B',
		'mistralai/mistral-7b-instruct:free': 'Mistral 7B',
		'google/gemma-2-9b-it:free': 'Gemma 2 9B',
		'openai/gpt-4o-mini': 'GPT-4o Mini',
		'openai/gpt-4o': 'GPT-4o',
		'anthropic/claude-3.5-sonnet': 'Claude 3.5'
	}
	return names[model] || model
}

// Format date
function formatDate(dateStr) {
	if (!dateStr) return 'Never'
	const date = new Date(dateStr)
	return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
	fetchAIStatus()
})

document.title = 'Settings - Insights'
</script>

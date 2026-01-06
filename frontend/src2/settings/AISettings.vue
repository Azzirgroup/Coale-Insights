<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { call } from 'frappe-ui'
import SettingItem from './SettingItem.vue'
import useSettings from './settings'
import { createToast } from '../helpers/toasts'

const settings = useSettings()
settings.load()

const aiStatus = ref({
	enabled: false,
	configured: false,
	quota_used: 0,
	daily_quota: 100,
	last_refresh: null as string | null
})

const isSaving = ref(false)

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
const modelOptions = [
	{ group: 'Free Models (Recommended)', options: [
		{ value: 'meta-llama/llama-3.3-70b-instruct:free', label: 'Llama 3.3 70B (Free) ⭐' },
		{ value: 'openai/gpt-oss-120b:free', label: 'OpenAI GPT-OSS 120B (Free)' },
		{ value: 'google/gemini-2.0-flash-exp:free', label: 'Gemini 2.0 Flash (Free)' },
		{ value: 'qwen/qwen3-235b-a22b:free', label: 'Qwen3 235B (Free)' },
		{ value: 'mistralai/mistral-small-3.1-24b-instruct:free', label: 'Mistral Small 3.1 24B (Free)' },
		{ value: 'nousresearch/hermes-3-llama-3.1-405b:free', label: 'Hermes 3 Llama 405B (Free)' },
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

function getModelDisplayName(model: string) {
	for (const group of modelOptions) {
		const found = group.options.find(o => o.value === model)
		if (found) return found.label
	}
	return model
}

function formatDate(dateStr: string | null) {
	if (!dateStr) return 'Never'
	const date = new Date(dateStr)
	return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

async function testConnection() {
	if (!settings.doc.openrouter_api_key) {
		createToast({
			title: 'API Key Required',
			message: 'Please enter your OpenRouter API key first',
			variant: 'warning'
		})
		return
	}
	
	try {
		const response = await call('insights.ai.openrouter_client.test_connection', {
			api_key: settings.doc.openrouter_api_key
		})
		
		if (response?.success) {
			createToast({
				title: 'Connection Successful',
				message: 'OpenRouter API is working correctly',
				variant: 'success'
			})
		} else {
			createToast({
				title: 'Connection Failed',
				message: response?.error || 'Failed to connect to OpenRouter',
				variant: 'error'
			})
		}
	} catch (error: any) {
		createToast({
			title: 'Connection Error',
			message: error.message || 'Failed to test connection',
			variant: 'error'
		})
	}
}

onMounted(() => {
	fetchAIStatus()
})
</script>

<template>
	<div class="flex w-full flex-col gap-6 overflow-y-scroll p-8 px-10">
		<div class="flex items-center justify-between">
			<h1 class="text-xl font-semibold flex items-center gap-2">
				<span class="text-2xl">🧠</span>
				AI Analytics
			</h1>
			<div class="flex items-center gap-2">
				<Badge v-if="settings.doc.enable_ai_analytics && settings.doc.openrouter_api_key" variant="subtle" theme="green">
					Configured
				</Badge>
				<Badge v-else variant="subtle" theme="orange">
					Not Configured
				</Badge>
			</div>
		</div>

		<SettingItem
			label="Enable AI Analytics"
			description="Enable ML-powered analytics with AI-generated insights for dashboards."
		>
			<FormControl
				type="checkbox"
				v-model="settings.doc.enable_ai_analytics"
				:label="settings.doc.enable_ai_analytics ? 'Enabled' : 'Disabled'"
			/>
		</SettingItem>

		<div v-if="settings.doc.enable_ai_analytics" class="flex flex-col gap-6">
			<div class="border-t pt-6">
				<h2 class="text-lg font-medium text-gray-700 mb-4">API Configuration</h2>
				
				<SettingItem
					label="OpenRouter API Key"
					description="Get your API key from https://openrouter.ai/keys. Required for AI-powered analytics."
				>
					<div class="flex gap-2">
						<FormControl
							type="password"
							v-model="settings.doc.openrouter_api_key"
							placeholder="sk-or-v1-..."
							class="flex-1"
						/>
						<Button variant="outline" @click="testConnection">
							Test
						</Button>
					</div>
				</SettingItem>
			</div>

			<div class="border-t pt-6">
				<h2 class="text-lg font-medium text-gray-700 mb-4">Model Selection</h2>
				<div class="grid grid-cols-2 gap-6">
					<SettingItem
						label="Primary AI Model"
						description="Main model for generating insights. Free models recommended."
					>
						<select
							v-model="settings.doc.ai_model"
							class="form-select w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
						>
							<optgroup v-for="group in modelOptions" :key="group.group" :label="group.group">
								<option v-for="opt in group.options" :key="opt.value" :value="opt.value">
									{{ opt.label }}
								</option>
							</optgroup>
						</select>
					</SettingItem>

					<SettingItem
						label="Fallback AI Model"
						description="Used when primary model fails or is rate-limited."
					>
						<select
							v-model="settings.doc.ai_model_fallback"
							class="form-select w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
						>
							<optgroup v-for="group in modelOptions" :key="group.group" :label="group.group">
								<option v-for="opt in group.options" :key="opt.value" :value="opt.value">
									{{ opt.label }}
								</option>
							</optgroup>
						</select>
					</SettingItem>
				</div>
			</div>

			<div class="border-t pt-6">
				<h2 class="text-lg font-medium text-gray-700 mb-4">Scheduling & Quotas</h2>
				<div class="grid grid-cols-2 gap-6">
					<SettingItem
						label="Auto Refresh Schedule"
						description="Automatically refresh AI insights on a schedule."
					>
						<select
							v-model="settings.doc.refresh_schedule"
							class="form-select w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
						>
							<option v-for="opt in scheduleOptions" :key="opt.value" :value="opt.value">
								{{ opt.label }}
							</option>
						</select>
					</SettingItem>

					<SettingItem
						label="Daily AI Request Quota"
						description="Maximum AI requests per day to control costs."
					>
						<div class="flex items-center gap-2">
							<FormControl
								type="number"
								v-model="settings.doc.daily_ai_quota"
								:min="1"
								class="w-24"
							/>
							<span class="text-gray-600 text-sm">requests/day</span>
						</div>
					</SettingItem>
				</div>
			</div>

			<div class="border-t pt-6">
				<h2 class="text-lg font-medium text-gray-700 mb-4">Status</h2>
				<div class="grid grid-cols-3 gap-4">
					<div class="bg-gray-50 rounded-lg p-4">
						<div class="text-sm text-gray-500">Quota Used Today</div>
						<div class="text-2xl font-semibold text-gray-800">
							{{ aiStatus.quota_used || 0 }} / {{ settings.doc.daily_ai_quota || 100 }}
						</div>
						<div class="mt-2 w-full bg-gray-200 rounded-full h-2">
							<div 
								class="bg-blue-500 h-2 rounded-full transition-all"
								:style="`width: ${Math.min(100, ((aiStatus.quota_used || 0) / (settings.doc.daily_ai_quota || 100)) * 100)}%`"
							></div>
						</div>
					</div>
					<div class="bg-gray-50 rounded-lg p-4">
						<div class="text-sm text-gray-500">Last Refresh</div>
						<div class="text-lg font-medium text-gray-800">
							{{ formatDate(aiStatus.last_refresh) }}
						</div>
					</div>
					<div class="bg-gray-50 rounded-lg p-4">
						<div class="text-sm text-gray-500">Primary Model</div>
						<div class="text-lg font-medium text-gray-800 truncate">
							{{ getModelDisplayName(settings.doc.ai_model || '') }}
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="flex justify-end border-t pt-4">
			<Button
				label="Update"
				variant="solid"
				:disabled="!settings.isdirty"
				:loading="settings.saving"
				@click="() => settings.save()"
			/>
		</div>
	</div>
</template>

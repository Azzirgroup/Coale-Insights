<template>
	<div class="flex items-center space-x-2">
		<Button
			:variant="variant"
			:loading="isRefreshing"
			:disabled="!isEnabled"
			@click="refreshDashboard"
		>
			<template #prefix>
				<RefreshCwIcon v-if="!isRefreshing" class="w-4 h-4" />
				<LoaderIcon v-else class="w-4 h-4 animate-spin" />
			</template>
			{{ buttonLabel }}
		</Button>
		
		<div v-if="showStatus" class="flex items-center text-sm text-gray-500">
			<span v-if="lastUpdated" class="flex items-center">
				<ClockIcon class="w-3 h-3 mr-1" />
				{{ formatRelativeTime(lastUpdated) }}
			</span>
			<Badge v-if="cached" variant="subtle" theme="blue" class="ml-2">Cached</Badge>
			<Badge v-if="modelUsed" variant="subtle" theme="purple" class="ml-2">{{ modelUsed }}</Badge>
		</div>
	</div>
	
	<!-- Error Toast -->
	<div
		v-if="error"
		class="fixed bottom-4 right-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg shadow-lg flex items-center"
	>
		<AlertCircleIcon class="w-5 h-5 mr-2" />
		{{ error }}
		<button @click="error = null" class="ml-3 text-red-500 hover:text-red-700">
			<XIcon class="w-4 h-4" />
		</button>
	</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import { Badge } from 'frappe-ui'
import { RefreshCwIcon, LoaderIcon, ClockIcon, AlertCircleIcon, XIcon } from 'lucide-vue-next'

const props = defineProps({
	dashboardType: {
		type: String,
		required: true
	},
	variant: {
		type: String,
		default: 'outline'
	},
	label: {
		type: String,
		default: 'Refresh with AI'
	},
	showStatus: {
		type: Boolean,
		default: true
	},
	filters: {
		type: Object,
		default: () => ({})
	}
})

const emit = defineEmits(['refresh', 'data', 'error'])

const isRefreshing = ref(false)
const isEnabled = ref(false)
const lastUpdated = ref(null)
const cached = ref(false)
const modelUsed = ref(null)
const error = ref(null)

const buttonLabel = computed(() => {
	if (isRefreshing.value) return 'Refreshing...'
	return props.label
})

// Check if AI is enabled
async function checkAIStatus() {
	try {
		const response = await call('insights.ai.openrouter_client.get_ai_status')
		isEnabled.value = response?.enabled && response?.configured
	} catch (err) {
		console.error('Failed to check AI status:', err)
		isEnabled.value = false
	}
}

// Refresh dashboard with AI
async function refreshDashboard() {
	if (isRefreshing.value || !isEnabled.value) return
	
	isRefreshing.value = true
	error.value = null
	
	try {
		const response = await call('insights.analytics.ml_engine.refresh_dashboard', {
			dashboard_type: props.dashboardType,
			filters: JSON.stringify(props.filters)
		})
		
		if (response) {
			lastUpdated.value = response.last_updated || new Date().toISOString()
			cached.value = response.ai_insights?.cached || false
			modelUsed.value = getShortModelName(response.ai_insights?.model_used)
			
			emit('data', response)
			emit('refresh', response)
		}
	} catch (err) {
		console.error('Failed to refresh dashboard:', err)
		error.value = err.message || 'Failed to refresh AI insights'
		emit('error', err)
	} finally {
		isRefreshing.value = false
	}
}

// Format relative time
function formatRelativeTime(dateStr) {
	if (!dateStr) return ''
	
	const date = new Date(dateStr)
	const now = new Date()
	const diffMs = now - date
	const diffMins = Math.floor(diffMs / 60000)
	const diffHours = Math.floor(diffMs / 3600000)
	const diffDays = Math.floor(diffMs / 86400000)
	
	if (diffMins < 1) return 'Just now'
	if (diffMins < 60) return `${diffMins}m ago`
	if (diffHours < 24) return `${diffHours}h ago`
	return `${diffDays}d ago`
}

// Get short model name
function getShortModelName(model) {
	if (!model) return null
	
	const names = {
		'meta-llama/llama-3.1-8b-instruct:free': 'Llama 8B',
		'mistralai/mistral-7b-instruct:free': 'Mistral 7B',
		'google/gemma-2-9b-it:free': 'Gemma 9B',
		'openai/gpt-4o-mini': 'GPT-4o Mini',
		'openai/gpt-4o': 'GPT-4o',
		'anthropic/claude-3.5-sonnet': 'Claude 3.5'
	}
	
	return names[model] || model.split('/').pop()
}

onMounted(() => {
	checkAIStatus()
})
</script>

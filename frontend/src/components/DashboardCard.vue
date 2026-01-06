<template>
	<div class="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
		<!-- Header -->
		<div class="p-4 border-b" :style="{ borderBottomColor: color + '40' }">
			<div class="flex items-center justify-between">
				<div class="flex items-center">
					<div
						class="w-10 h-10 rounded-lg flex items-center justify-center"
						:style="{ backgroundColor: color + '20' }"
					>
						<component :is="iconComponent" class="w-5 h-5" :style="{ color: color }" />
					</div>
					<div class="ml-3">
						<h3 class="font-semibold text-gray-800">{{ title }}</h3>
						<p class="text-xs text-gray-500">{{ description }}</p>
					</div>
				</div>
				<Button size="sm" variant="ghost" @click="$emit('refresh')" :loading="loading">
					<RefreshCwIcon class="w-4 h-4" />
				</Button>
			</div>
		</div>

		<!-- KPIs -->
		<div class="p-4">
			<div v-if="loading" class="space-y-3">
				<div v-for="i in 4" :key="i" class="h-6 bg-gray-100 rounded animate-pulse"></div>
			</div>
			<div v-else-if="data?.kpis" class="grid grid-cols-2 gap-3">
				<div v-for="kpi in data.kpis.slice(0, 4)" :key="kpi.label" class="p-2 bg-gray-50 rounded">
					<div class="text-xs text-gray-500 truncate">{{ kpi.label }}</div>
					<div class="font-semibold text-gray-800">
						{{ formatValue(kpi.value, kpi.format) }}
					</div>
					<div v-if="kpi.change !== undefined" class="text-xs" :class="kpi.change >= 0 ? 'text-green-600' : 'text-red-600'">
						{{ kpi.change >= 0 ? '↑' : '↓' }} {{ Math.abs(kpi.change) }}%
					</div>
				</div>
			</div>
			<div v-else class="text-center py-4 text-gray-400">
				<PackageIcon class="w-8 h-8 mx-auto mb-2" />
				<p class="text-sm">Click refresh to load data</p>
			</div>
		</div>

		<!-- AI Insights Preview -->
		<div v-if="data?.ai_insights?.insights" class="px-4 pb-4">
			<div class="p-3 bg-purple-50 rounded-lg border border-purple-100">
				<div class="flex items-center text-purple-700 text-xs mb-1">
					<BrainIcon class="w-3 h-3 mr-1" />
					AI Insight
				</div>
				<p class="text-sm text-purple-900 line-clamp-2">
					{{ truncateInsight(data.ai_insights.insights) }}
				</p>
			</div>
		</div>

		<!-- Footer -->
		<div class="px-4 pb-4">
			<Button class="w-full" variant="outline" @click="$emit('view')">
				View Details
				<ArrowRightIcon class="w-4 h-4 ml-2" />
			</Button>
		</div>
	</div>
</template>

<script setup>
import { computed } from 'vue'
import {
	RefreshCwIcon,
	ArrowRightIcon,
	BrainIcon,
	PackageIcon,
	DollarSignIcon,
	TrendingUpIcon,
	ShoppingCartIcon,
	SettingsIcon,
	UsersIcon
} from 'lucide-vue-next'

const props = defineProps({
	title: { type: String, required: true },
	description: { type: String, required: true },
	icon: { type: String, required: true },
	color: { type: String, default: '#3B82F6' },
	type: { type: String, required: true },
	data: { type: Object, default: null },
	loading: { type: Boolean, default: false }
})

defineEmits(['refresh', 'view'])

const iconComponents = {
	'dollar-sign': DollarSignIcon,
	'trending-up': TrendingUpIcon,
	'shopping-cart': ShoppingCartIcon,
	'package': PackageIcon,
	'settings': SettingsIcon,
	'users': UsersIcon
}

const iconComponent = computed(() => iconComponents[props.icon] || PackageIcon)

function formatValue(value, format) {
	if (value === null || value === undefined) return '-'
	
	switch (format) {
		case 'currency':
			return new Intl.NumberFormat('en-US', {
				style: 'currency',
				currency: 'KES',
				minimumFractionDigits: 0,
				maximumFractionDigits: 0
			}).format(value)
		case 'percent':
			return `${value.toFixed(1)}%`
		case 'number':
			return new Intl.NumberFormat('en-US').format(value)
		case 'decimal':
			return value.toFixed(2)
		default:
			return String(value)
	}
}

function truncateInsight(text) {
	if (!text) return ''
	// Get first sentence or first 150 chars
	const firstSentence = text.split(/[.!?]/)[0]
	if (firstSentence.length > 150) {
		return firstSentence.substring(0, 150) + '...'
	}
	return firstSentence + '.'
}
</script>

<style scoped>
.line-clamp-2 {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}
</style>

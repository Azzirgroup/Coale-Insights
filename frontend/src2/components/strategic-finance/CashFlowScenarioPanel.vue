<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
          <FlaskConical class="h-5 w-5 text-indigo-600" />
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 dark:text-white">What-If Scenarios</h4>
          <p class="text-xs text-gray-500">Explore different cash flow outcomes</p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <!-- Filter by type -->
        <select 
          v-model="filterType"
          class="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300"
        >
          <option value="all">All Types</option>
          <option value="risk">Risks</option>
          <option value="opportunity">Opportunities</option>
          <option value="decision">Decisions</option>
        </select>
        <button 
          @click="expanded = !expanded"
          class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          <ChevronDown :class="['h-5 w-5 text-gray-500 transition-transform', expanded ? 'rotate-180' : '']" />
        </button>
      </div>
    </div>

    <div v-if="expanded" class="space-y-4">
      <!-- Baseline Summary -->
      <div class="grid grid-cols-3 gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <div class="text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">Base Ending Balance</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">{{ formatCompact(scenarios?.base_ending_balance || 0) }}</p>
        </div>
        <div class="text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">Base Min Balance</p>
          <p class="text-lg font-bold" :class="(scenarios?.base_min_balance || 0) < (scenarios?.threshold || 0) ? 'text-red-600' : 'text-gray-900 dark:text-white'">
            {{ formatCompact(scenarios?.base_min_balance || 0) }}
          </p>
        </div>
        <div class="text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">Min Threshold</p>
          <p class="text-lg font-bold text-amber-600">{{ formatCompact(scenarios?.threshold || 0) }}</p>
        </div>
      </div>

      <!-- Scenarios ListView Table -->
      <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-3 py-2.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scenario</th>
              <th class="px-3 py-2.5 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">Type</th>
              <th class="px-3 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Impact</th>
              <th class="px-3 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-24">End Bal.</th>
              <th class="px-3 py-2.5 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-24">Min Bal.</th>
              <th class="px-3 py-2.5 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-20">Risk</th>
              <th class="px-3 py-2.5 text-center text-xs font-medium text-gray-500 uppercase tracking-wider w-16">Alert</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr 
              v-for="row in filteredScenarios" 
              :key="row.id"
              :class="[
                'cursor-pointer transition-colors',
                selectedScenario?.id === row.id ? 'bg-indigo-50 dark:bg-indigo-900/30' : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
              ]"
              @click="selectRow(row)"
            >
              <!-- Scenario Name -->
              <td class="px-3 py-3">
                <div class="flex items-center gap-2">
                  <div :class="['p-1.5 rounded-lg flex-shrink-0', getScenarioIconBg(row)]">
                    <component :is="getScenarioIcon(row)" class="h-4 w-4" :class="getScenarioIconColor(row)" />
                  </div>
                  <div class="min-w-0">
                    <p class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ row.name }}</p>
                    <p class="text-xs text-gray-500 truncate">{{ row.description }}</p>
                  </div>
                </div>
              </td>

              <!-- Type Badge -->
              <td class="px-3 py-3 text-center">
                <span :class="['text-xs px-2 py-1 rounded-full font-medium', getTypeBadgeClass(row.type)]">
                  {{ row.type }}
                </span>
              </td>

              <!-- Impact -->
              <td class="px-3 py-3 text-right">
                <span :class="['font-bold text-sm', row.impact >= 0 ? 'text-green-600' : 'text-red-600']">
                  {{ row.impact >= 0 ? '+' : '' }}{{ formatCompact(row.impact) }}
                </span>
              </td>

              <!-- Ending Balance -->
              <td class="px-3 py-3 text-right">
                <span class="font-medium text-gray-900 dark:text-white text-sm">{{ formatCompact(row.ending_balance) }}</span>
              </td>

              <!-- Min Balance -->
              <td class="px-3 py-3 text-right">
                <span :class="['font-medium text-sm', row.min_balance < (scenarios?.threshold || 0) ? 'text-red-600' : 'text-gray-900 dark:text-white']">
                  {{ formatCompact(row.min_balance) }}
                </span>
              </td>

              <!-- Risk Level -->
              <td class="px-3 py-3 text-center">
                <span :class="['text-xs px-2 py-1 rounded-full font-medium', getRiskBadgeClass(row.risk_level)]">
                  {{ row.risk_level }}
                </span>
              </td>

              <!-- Weeks Below Threshold -->
              <td class="px-3 py-3 text-center">
                <span v-if="row.weeks_below_threshold > 0" class="flex items-center justify-center gap-1 text-red-600 text-sm">
                  <AlertTriangle class="h-3.5 w-3.5" />
                  {{ row.weeks_below_threshold }}
                </span>
                <CheckCircle v-else class="h-4 w-4 text-green-500 mx-auto" />
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Empty State -->
        <div v-if="!filteredScenarios.length" class="p-8 text-center">
          <FlaskConical class="h-10 w-10 mx-auto text-gray-400 mb-2" />
          <p class="text-sm text-gray-600 dark:text-gray-400">No scenarios available</p>
        </div>
      </div>

      <!-- Selected Scenario Detail -->
      <div v-if="selectedScenario" class="p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-200 dark:border-indigo-700">
        <div class="flex items-center justify-between mb-3">
          <h5 class="font-medium text-sm text-indigo-700 dark:text-indigo-300 flex items-center gap-2">
            <BarChart3 class="h-4 w-4" />
            {{ selectedScenario.name }}
          </h5>
          <button @click="selectedScenario = null" class="p-1 text-gray-500 hover:text-gray-700 hover:bg-indigo-100 dark:hover:bg-indigo-800 rounded">
            <X class="h-4 w-4" />
          </button>
        </div>
        
        <!-- Comparison Bars -->
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <span class="w-16 text-xs text-gray-600 dark:text-gray-400">Base</span>
            <div class="flex-1 h-6 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden relative">
              <div 
                class="h-full bg-blue-500 rounded-lg transition-all"
                :style="{ width: getBarWidth(scenarios?.base_ending_balance || 0) + '%' }"
              ></div>
              <span class="absolute right-2 top-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                {{ formatCompact(scenarios?.base_ending_balance || 0) }}
              </span>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <span class="w-16 text-xs text-gray-600 dark:text-gray-400">Scenario</span>
            <div class="flex-1 h-6 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden relative">
              <div 
                :class="['h-full rounded-lg transition-all', selectedScenario.impact >= 0 ? 'bg-green-500' : 'bg-red-500']"
                :style="{ width: getBarWidth(selectedScenario.ending_balance) + '%' }"
              ></div>
              <span class="absolute right-2 top-1 text-xs font-medium text-gray-700 dark:text-gray-300">
                {{ formatCompact(selectedScenario.ending_balance) }}
              </span>
            </div>
          </div>
        </div>
        
        <div class="mt-3 pt-3 border-t border-indigo-200 dark:border-indigo-700 grid grid-cols-3 gap-4 text-center">
          <div>
            <p class="text-xs text-gray-500">Impact</p>
            <p :class="['font-bold', selectedScenario.impact >= 0 ? 'text-green-600' : 'text-red-600']">
              {{ selectedScenario.impact >= 0 ? '+' : '' }}{{ formatCompact(selectedScenario.impact) }}
            </p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Min Balance</p>
            <p :class="['font-bold', selectedScenario.min_balance < (scenarios?.threshold || 0) ? 'text-red-600' : 'text-gray-900 dark:text-white']">
              {{ formatCompact(selectedScenario.min_balance) }}
            </p>
          </div>
          <div>
            <p class="text-xs text-gray-500">Weeks at Risk</p>
            <p :class="['font-bold', selectedScenario.weeks_below_threshold > 0 ? 'text-red-600' : 'text-green-600']">
              {{ selectedScenario.weeks_below_threshold || 0 }}
            </p>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div v-if="scenarios?.quick_actions?.length" class="space-y-2">
        <h5 class="font-medium text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
          <Lightbulb class="h-4 w-4 text-amber-500" />
          Recommended Actions
        </h5>
        <div class="space-y-2">
          <div 
            v-for="(action, idx) in scenarios.quick_actions" 
            :key="idx"
            :class="[
              'p-3 rounded-lg border-l-4 bg-white dark:bg-gray-800',
              action.priority === 'high' ? 'border-red-500' : 'border-amber-500'
            ]"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="font-medium text-sm text-gray-900 dark:text-white">{{ action.action }}</span>
              <span :class="['text-xs px-2 py-0.5 rounded-full', action.priority === 'high' ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300' : 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300']">
                {{ action.priority }} priority
              </span>
            </div>
            <p class="text-xs text-gray-600 dark:text-gray-400">{{ action.description }}</p>
            <p class="text-xs text-green-600 mt-1">Potential impact: {{ formatCompact(action.potential_impact) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  FlaskConical, 
  ChevronDown, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  Clock,
  FastForward,
  Pause,
  Sun,
  CloudRain,
  Lightbulb,
  Zap,
  CheckCircle,
  BarChart3,
  X
} from 'lucide-vue-next'

interface Props {
  scenarios: any
}

const props = defineProps<Props>()

const expanded = ref(true)
const selectedScenario = ref<any>(null)
const filterType = ref('all')

const filteredScenarios = computed(() => {
  const scenarios = props.scenarios?.scenarios || []
  if (filterType.value === 'all') return scenarios
  return scenarios.filter((s: any) => s.type === filterType.value)
})

const selectRow = (row: any) => {
  selectedScenario.value = selectedScenario.value?.id === row.id ? null : row
}

const getBarWidth = (value: number) => {
  const max = Math.max(
    props.scenarios?.base_ending_balance || 0,
    ...((props.scenarios?.scenarios || []).map((s: any) => s.ending_balance))
  )
  if (max <= 0) return 10
  return Math.max(10, Math.min(100, (value / max) * 100))
}

const getScenarioIconBg = (scenario: any) => {
  if (scenario.type === 'risk') return 'bg-red-100 dark:bg-red-900/30'
  if (scenario.type === 'opportunity') return 'bg-green-100 dark:bg-green-900/30'
  return 'bg-blue-100 dark:bg-blue-900/30'
}

const getScenarioIconColor = (scenario: any) => {
  if (scenario.type === 'risk') return 'text-red-600'
  if (scenario.type === 'opportunity') return 'text-green-600'
  return 'text-blue-600'
}

const getScenarioIcon = (scenario: any) => {
  const iconMap: Record<string, any> = {
    'clock': Clock,
    'trending-up': TrendingUp,
    'trending-down': TrendingDown,
    'fast-forward': FastForward,
    'pause': Pause,
    'alert-triangle': AlertTriangle,
    'sun': Sun,
    'cloud-rain': CloudRain
  }
  return iconMap[scenario.icon] || Zap
}

const getTypeBadgeClass = (type: string) => {
  switch (type) {
    case 'risk': return 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300'
    case 'opportunity': return 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300'
    case 'decision': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
    default: return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  }
}

const getRiskBadgeClass = (level: string) => {
  switch (level) {
    case 'critical': return 'bg-red-500 text-white'
    case 'high': return 'bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-300'
    case 'medium': return 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300'
    case 'low': return 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300'
    default: return 'bg-gray-100 text-gray-700'
  }
}

const formatCompact = (value: number) => {
  if (value === null || value === undefined) return '0'
  const absValue = Math.abs(value)
  const sign = value < 0 ? '-' : ''
  if (absValue >= 1000000) return `${sign}${(absValue / 1000000).toFixed(1)}M`
  if (absValue >= 1000) return `${sign}${(absValue / 1000).toFixed(0)}K`
  return `${sign}${absValue.toFixed(0)}`
}
</script>

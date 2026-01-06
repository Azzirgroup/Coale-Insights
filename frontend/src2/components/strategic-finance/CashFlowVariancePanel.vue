<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
          <GitCompare class="h-5 w-5 text-purple-600" />
        </div>
        <div>
          <h4 class="font-semibold text-gray-900 dark:text-white">Variance Review</h4>
          <p class="text-xs text-gray-500">Actual vs Forecast Analysis</p>
        </div>
      </div>
      <button 
        @click="expanded = !expanded"
        class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
      >
        <ChevronDown :class="['h-5 w-5 text-gray-500 transition-transform', expanded ? 'rotate-180' : '']" />
      </button>
    </div>

    <div v-if="expanded">
      <!-- No Data State -->
      <div v-if="!variance?.has_variance_data" class="p-6 text-center bg-gray-50 dark:bg-gray-800 rounded-xl">
        <FileQuestion class="h-10 w-10 mx-auto text-gray-400 mb-2" />
        <p class="text-sm text-gray-600 dark:text-gray-400">No variance data available yet</p>
        <p class="text-xs text-gray-500">Variance data will appear after weeks with actual vs forecast comparisons</p>
      </div>

      <template v-else>
        <!-- Accuracy Summary -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-1">
              <Target class="h-4 w-4 text-blue-500" />
              <span class="text-xs text-gray-500">Inflow Accuracy</span>
            </div>
            <p :class="['text-xl font-bold', getAccuracyColor(variance.summary?.inflow_forecast_accuracy)]">
              {{ variance.summary?.inflow_forecast_accuracy || 0 }}%
            </p>
          </div>
          
          <div class="p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-1">
              <Target class="h-4 w-4 text-red-500" />
              <span class="text-xs text-gray-500">Outflow Accuracy</span>
            </div>
            <p :class="['text-xl font-bold', getAccuracyColor(variance.summary?.outflow_forecast_accuracy)]">
              {{ variance.summary?.outflow_forecast_accuracy || 0 }}%
            </p>
          </div>
          
          <div class="p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-1">
              <TrendingUp class="h-4 w-4 text-green-500" />
              <span class="text-xs text-gray-500">Net Variance</span>
            </div>
            <p :class="['text-xl font-bold', (variance.summary?.total_net_variance || 0) >= 0 ? 'text-green-600' : 'text-red-600']">
              {{ (variance.summary?.total_net_variance || 0) >= 0 ? '+' : '' }}{{ formatCompact(variance.summary?.total_net_variance || 0) }}
            </p>
          </div>
          
          <div class="p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-2 mb-1">
              <Calendar class="h-4 w-4 text-purple-500" />
              <span class="text-xs text-gray-500">Weeks Analyzed</span>
            </div>
            <p class="text-xl font-bold text-gray-900 dark:text-white">
              {{ variance.weeks_analyzed || 0 }}
            </p>
          </div>
        </div>

        <!-- Insights -->
        <div v-if="variance.insights?.length" class="space-y-2">
          <h5 class="font-medium text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <Sparkles class="h-4 w-4 text-amber-500" />
            Key Insights
          </h5>
          <div class="space-y-2">
            <div 
              v-for="(insight, idx) in variance.insights" 
              :key="idx"
              :class="[
                'p-3 rounded-lg border-l-4',
                insight.type === 'positive' ? 'bg-green-50 dark:bg-green-900/20 border-green-500' : 'bg-red-50 dark:bg-red-900/20 border-red-500'
              ]"
            >
              <div class="flex items-center gap-2 mb-1">
                <component 
                  :is="insight.type === 'positive' ? TrendingUp : TrendingDown" 
                  :class="['h-4 w-4', insight.type === 'positive' ? 'text-green-600' : 'text-red-600']"
                />
                <span class="font-medium text-sm text-gray-900 dark:text-white">{{ insight.title }}</span>
                <span :class="['text-xs px-1.5 py-0.5 rounded', getCategoryBadge(insight.category)]">
                  {{ insight.category }}
                </span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ insight.description }}</p>
              <p class="text-xs text-blue-600 dark:text-blue-400 mt-1 flex items-center gap-1">
                <Lightbulb class="h-3 w-3" />
                {{ insight.recommendation }}
              </p>
            </div>
          </div>
        </div>

        <!-- Weekly Variance Table -->
        <div v-if="variance.weekly_details?.length" class="overflow-x-auto">
          <h5 class="font-medium text-sm text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
            <Table2 class="h-4 w-4" />
            Weekly Variance Details
          </h5>
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-gray-200 dark:border-gray-700">
                <th class="px-3 py-2 text-left text-gray-500 font-medium">Week</th>
                <th class="px-3 py-2 text-right text-gray-500 font-medium">Inflow Var</th>
                <th class="px-3 py-2 text-right text-gray-500 font-medium">%</th>
                <th class="px-3 py-2 text-right text-gray-500 font-medium">Outflow Var</th>
                <th class="px-3 py-2 text-right text-gray-500 font-medium">%</th>
                <th class="px-3 py-2 text-right text-gray-500 font-medium">Net Var</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="week in variance.weekly_details" 
                :key="week.week_number"
                class="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50"
              >
                <td class="px-3 py-2 font-medium text-gray-900 dark:text-white">
                  {{ week.week_label }}
                </td>
                <td :class="['px-3 py-2 text-right', getVarianceColor(week.inflow_variance)]">
                  {{ week.inflow_variance >= 0 ? '+' : '' }}{{ formatCompact(week.inflow_variance) }}
                </td>
                <td :class="['px-3 py-2 text-right text-xs', getVarianceColor(week.inflow_variance_pct)]">
                  {{ week.inflow_variance_pct >= 0 ? '+' : '' }}{{ week.inflow_variance_pct }}%
                </td>
                <td :class="['px-3 py-2 text-right', getVarianceColor(-week.outflow_variance)]">
                  {{ week.outflow_variance >= 0 ? '+' : '' }}{{ formatCompact(week.outflow_variance) }}
                </td>
                <td :class="['px-3 py-2 text-right text-xs', getVarianceColor(-week.outflow_variance_pct)]">
                  {{ week.outflow_variance_pct >= 0 ? '+' : '' }}{{ week.outflow_variance_pct }}%
                </td>
                <td :class="['px-3 py-2 text-right font-medium', getVarianceColor(week.net_variance)]">
                  {{ week.net_variance >= 0 ? '+' : '' }}{{ formatCompact(week.net_variance) }}
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="bg-gray-50 dark:bg-gray-800 font-medium">
                <td class="px-3 py-2 text-gray-700 dark:text-gray-300">Total</td>
                <td :class="['px-3 py-2 text-right', getVarianceColor(variance.summary?.total_inflow_variance)]">
                  {{ (variance.summary?.total_inflow_variance || 0) >= 0 ? '+' : '' }}{{ formatCompact(variance.summary?.total_inflow_variance || 0) }}
                </td>
                <td class="px-3 py-2"></td>
                <td :class="['px-3 py-2 text-right', getVarianceColor(-(variance.summary?.total_outflow_variance || 0))]">
                  {{ (variance.summary?.total_outflow_variance || 0) >= 0 ? '+' : '' }}{{ formatCompact(variance.summary?.total_outflow_variance || 0) }}
                </td>
                <td class="px-3 py-2"></td>
                <td :class="['px-3 py-2 text-right', getVarianceColor(variance.summary?.total_net_variance)]">
                  {{ (variance.summary?.total_net_variance || 0) >= 0 ? '+' : '' }}{{ formatCompact(variance.summary?.total_net_variance || 0) }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Visual Variance Chart -->
        <div class="p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
          <h5 class="font-medium text-sm text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
            <BarChart3 class="h-4 w-4" />
            Variance Trend
          </h5>
          <div class="flex items-end justify-around h-32 gap-1">
            <div 
              v-for="week in variance.weekly_details" 
              :key="week.week_number"
              class="flex flex-col items-center flex-1"
            >
              <!-- Positive variance (up) -->
              <div class="w-full flex justify-center" style="height: 50px;">
                <div 
                  v-if="week.net_variance > 0"
                  class="w-4/5 bg-green-500 rounded-t transition-all"
                  :style="{ height: getBarHeight(week.net_variance, true) + '%' }"
                  :title="`+${formatCompact(week.net_variance)}`"
                ></div>
              </div>
              <!-- Zero line -->
              <div class="w-full h-px bg-gray-300 dark:bg-gray-600"></div>
              <!-- Negative variance (down) -->
              <div class="w-full flex justify-center" style="height: 50px;">
                <div 
                  v-if="week.net_variance < 0"
                  class="w-4/5 bg-red-500 rounded-b transition-all"
                  :style="{ height: getBarHeight(week.net_variance, false) + '%' }"
                  :title="`${formatCompact(week.net_variance)}`"
                ></div>
              </div>
              <!-- Label -->
              <span class="text-xs text-gray-500 mt-1 truncate w-full text-center">
                {{ week.week_label?.split(' ')[0] }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { 
  GitCompare,
  ChevronDown,
  Target,
  TrendingUp,
  TrendingDown,
  Calendar,
  Sparkles,
  Lightbulb,
  Table2,
  BarChart3,
  FileQuestion
} from 'lucide-vue-next'

interface Props {
  variance: any
}

const props = defineProps<Props>()

const expanded = ref(true)

const getAccuracyColor = (accuracy: number) => {
  if (accuracy >= 90) return 'text-green-600'
  if (accuracy >= 75) return 'text-amber-600'
  return 'text-red-600'
}

const getVarianceColor = (value: number) => {
  if (value > 0) return 'text-green-600'
  if (value < 0) return 'text-red-600'
  return 'text-gray-500'
}

const getCategoryBadge = (category: string) => {
  switch (category) {
    case 'inflows': return 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300'
    case 'outflows': return 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300'
    case 'net': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300'
    default: return 'bg-gray-100 text-gray-700'
  }
}

const getBarHeight = (value: number, isPositive: boolean) => {
  const maxVariance = Math.max(
    ...((props.variance?.weekly_details || []).map((w: any) => Math.abs(w.net_variance)))
  )
  if (maxVariance === 0) return 0
  
  const absValue = Math.abs(value)
  const height = (absValue / maxVariance) * 100
  
  if (isPositive && value > 0) return height
  if (!isPositive && value < 0) return height
  return 0
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

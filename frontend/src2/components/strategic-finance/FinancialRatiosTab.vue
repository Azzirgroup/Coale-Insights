<template>
  <div class="space-y-6">
    <!-- Key Ratios Summary - Use ratio_cards array from API -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div 
        v-for="card in ratioCards" 
        :key="card.name"
        class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700"
      >
        <div class="flex items-center justify-between mb-2">
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ card.name }}</p>
          <div :class="['px-2 py-0.5 rounded text-xs font-medium', card.statusClass]">
            {{ card.status === 'good' ? 'Good' : card.status === 'warning' ? 'Warning' : 'Low' }}
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900 dark:text-white">
          {{ card.value }}
        </p>
        <p class="text-xs text-gray-500 mt-2">Benchmark: {{ card.benchmark }}</p>
      </div>
    </div>

    <!-- Ratio Categories -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Liquidity Ratios -->
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Droplets class="h-5 w-5 text-blue-500" />
          Liquidity Ratios
        </h3>
        <div class="space-y-4">
          <div v-for="ratio in liquidityRatios" :key="ratio.name" class="flex justify-between items-center">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ ratio.name }}</p>
              <p class="text-xs text-gray-500">{{ ratio.description }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-900 dark:text-white">{{ ratio.value }}</p>
              <p :class="['text-xs', ratio.trend >= 0 ? 'text-green-600' : 'text-red-600']">
                {{ ratio.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(ratio.trend).toFixed(1) }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Profitability Ratios -->
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <TrendingUp class="h-5 w-5 text-green-500" />
          Profitability Ratios
        </h3>
        <div class="space-y-4">
          <div v-for="ratio in profitabilityRatios" :key="ratio.name" class="flex justify-between items-center">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ ratio.name }}</p>
              <p class="text-xs text-gray-500">{{ ratio.description }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-900 dark:text-white">{{ ratio.value }}</p>
              <p :class="['text-xs', ratio.trend >= 0 ? 'text-green-600' : 'text-red-600']">
                {{ ratio.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(ratio.trend).toFixed(1) }}%
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Efficiency Ratios -->
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Gauge class="h-5 w-5 text-purple-500" />
          Efficiency Ratios
        </h3>
        <div class="space-y-4">
          <div v-for="ratio in efficiencyRatios" :key="ratio.name" class="flex justify-between items-center">
            <div>
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ ratio.name }}</p>
              <p class="text-xs text-gray-500">{{ ratio.description }}</p>
            </div>
            <div class="text-right">
              <p class="font-semibold text-gray-900 dark:text-white">{{ ratio.value }}</p>
              <p :class="['text-xs', ratio.trend >= 0 ? 'text-green-600' : 'text-red-600']">
                {{ ratio.trend >= 0 ? '↑' : '↓' }} {{ Math.abs(ratio.trend).toFixed(1) }}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ratio Trends Chart (Transposed: Quarters as Columns) -->
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <LineChartIcon class="h-5 w-5 text-gray-500" />
        Quarterly Ratio Trends
      </h3>
      <div v-if="quarterlyTrends.length" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase sticky left-0 bg-gray-50 dark:bg-gray-800">Metric</th>
              <th v-for="quarter in quarterlyTrends" :key="quarter.period"
                  class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase whitespace-nowrap">
                {{ quarter.period }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <!-- Gross Margin Row -->
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white sticky left-0 bg-white dark:bg-gray-800">Gross Margin</td>
              <td v-for="quarter in quarterlyTrends" :key="'gm-'+quarter.period" 
                  class="px-4 py-3 text-sm text-right whitespace-nowrap"
                  :class="getRatioTrendClass(quarter.gross_margin, 35)">
                {{ quarter.gross_margin?.toFixed(1) }}%
              </td>
            </tr>
            <!-- Net Margin Row -->
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white sticky left-0 bg-white dark:bg-gray-800">Net Margin</td>
              <td v-for="quarter in quarterlyTrends" :key="'nm-'+quarter.period" 
                  class="px-4 py-3 text-sm text-right whitespace-nowrap"
                  :class="getRatioTrendClass(quarter.net_margin, 10)">
                {{ quarter.net_margin?.toFixed(1) }}%
              </td>
            </tr>
            <!-- ROA Row -->
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white sticky left-0 bg-white dark:bg-gray-800">ROA</td>
              <td v-for="quarter in quarterlyTrends" :key="'roa-'+quarter.period" 
                  class="px-4 py-3 text-sm text-right whitespace-nowrap"
                  :class="getRatioTrendClass(quarter.roa, 8)">
                {{ quarter.roa?.toFixed(1) }}%
              </td>
            </tr>
            <!-- Asset Turnover Row -->
            <tr class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white sticky left-0 bg-white dark:bg-gray-800">Asset Turnover</td>
              <td v-for="quarter in quarterlyTrends" :key="'at-'+quarter.period" 
                  class="px-4 py-3 text-sm text-right whitespace-nowrap"
                  :class="getRatioTrendClass(quarter.asset_turnover, 1.2)">
                {{ quarter.asset_turnover?.toFixed(2) }}x
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        No quarterly trend data available
      </div>
    </div>

    <!-- Industry Benchmarks -->
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <BarChart3 class="h-5 w-5 text-gray-500" />
        Performance vs Benchmarks
      </h3>
      <div class="space-y-4">
        <div v-for="benchmark in benchmarkComparison" :key="benchmark.name">
          <div class="flex justify-between mb-1">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ benchmark.name }}</span>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              {{ benchmark.actual }} / {{ benchmark.benchmark }} (benchmark)
            </span>
          </div>
          <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden relative">
            <!-- Benchmark line -->
            <div 
              class="absolute top-0 bottom-0 w-0.5 bg-gray-500 z-10"
              :style="{ left: `${Math.min(benchmark.benchmarkPosition, 100)}%` }"
            ></div>
            <!-- Actual value bar -->
            <div 
              :class="['h-full rounded-full transition-all', benchmark.isGood ? 'bg-green-500' : 'bg-amber-500']"
              :style="{ width: `${Math.min(benchmark.actualPosition, 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Droplets, 
  TrendingUp, 
  Gauge, 
  LineChart as LineChartIcon,
  BarChart3
} from 'lucide-vue-next'

interface Props {
  data: any
}

const props = defineProps<Props>()

const formatRatio = (value: number | null | undefined) => {
  if (value === null || value === undefined) return '0.00'
  return value.toFixed(2)
}

const formatPercent = (value: number | null | undefined) => {
  if (value === null || value === undefined) return '0%'
  return `${value.toFixed(1)}%`
}

// Liquidity Ratios - from ratio_cards or current_ratios
const liquidityRatios = computed(() => {
  if (!props.data) return []
  const current = props.data.current_ratios || {}
  return [
    { 
      name: 'Asset Turnover', 
      value: formatRatio(current.asset_turnover),
      description: 'Revenue / Total Assets',
      trend: 0
    },
    { 
      name: 'Debt to Equity', 
      value: formatRatio(current.debt_to_equity),
      description: 'Total Debt / Shareholders Equity',
      trend: 0
    },
    { 
      name: 'Cash Ratio', 
      value: formatRatio(props.data.cash_ratio),
      description: 'Cash / Current Liabilities',
      trend: props.data.cash_ratio_trend || 0
    }
  ]
})

// Profitability Ratios - from current_ratios
const profitabilityRatios = computed(() => {
  if (!props.data) return []
  const current = props.data.current_ratios || {}
  return [
    { 
      name: 'Gross Margin', 
      value: formatPercent(current.gross_margin),
      description: 'Gross Profit / Revenue',
      trend: 0
    },
    { 
      name: 'Net Profit Margin', 
      value: formatPercent(current.net_margin),
      description: 'Net Income / Revenue',
      trend: 0
    },
    { 
      name: 'ROE', 
      value: current.roe > 0 ? formatPercent(current.roe) : 'N/A',
      description: 'Net Income / Shareholders Equity',
      trend: 0
    },
    { 
      name: 'ROA', 
      value: formatPercent(current.roa),
      description: 'Net Income / Total Assets',
      trend: 0
    }
  ]
})

// Efficiency Ratios - from current_ratios
const efficiencyRatios = computed(() => {
  if (!props.data) return []
  const current = props.data.current_ratios || {}
  return [
    { 
      name: 'Asset Turnover', 
      value: formatRatio(current.asset_turnover) + 'x',
      description: 'Revenue / Total Assets',
      trend: 0
    },
    { 
      name: 'Debt/Equity', 
      value: current.debt_to_equity > 0 ? formatRatio(current.debt_to_equity) : 'N/A',
      description: 'Total Debt / Equity',
      trend: 0
    }
  ]
})

// Ratio Cards - use the pre-built ratio cards from API
const ratioCards = computed(() => {
  if (!props.data?.ratio_cards) return []
  return props.data.ratio_cards.map((card: any) => ({
    name: card.name,
    value: card.name.includes('Margin') || card.name.includes('RO') 
      ? (card.value > 0 ? formatPercent(card.value) : 'N/A')
      : formatRatio(card.value),
    benchmark: card.name.includes('Margin') || card.name.includes('RO')
      ? formatPercent(card.benchmark)
      : formatRatio(card.benchmark),
    status: card.status,
    statusClass: card.status === 'good' 
      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
      : card.status === 'warning'
      ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
      : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }))
})

// Quarterly Trends - last 4 quarters for transposed table
const quarterlyTrends = computed(() => {
  return props.data?.trends?.slice(-4) || []
})

// Benchmark Comparison - use ratio_cards from API
const benchmarkComparison = computed(() => {
  if (!props.data?.ratio_cards) return []
  
  return props.data.ratio_cards.map((card: any) => {
    const actual = card.value || 0
    const benchmark = card.benchmark || 1
    const maxValue = Math.max(Math.abs(actual), benchmark) * 1.2 || 1
    const isPercent = card.name.includes('Margin') || card.name.includes('RO')
    
    return {
      name: card.name,
      actual: isPercent ? `${actual.toFixed(1)}%` : actual.toFixed(2),
      benchmark: isPercent ? `${benchmark}%` : benchmark.toFixed(2),
      actualPosition: Math.min((Math.abs(actual) / maxValue) * 100, 100),
      benchmarkPosition: Math.min((benchmark / maxValue) * 100, 100),
      isGood: card.status === 'good'
    }
  })
})

// Health badge functions
const getRatioHealth = (value: number | null | undefined, type: string) => {
  if (!value) return 'N/A'
  
  switch (type) {
    case 'current':
      if (value >= 1.5 && value <= 3.0) return 'Good'
      if (value < 1.0) return 'Low'
      if (value > 3.0) return 'High'
      return 'Fair'
    case 'quick':
      if (value >= 1.0 && value <= 2.0) return 'Good'
      if (value < 1.0) return 'Low'
      return 'High'
    case 'margin':
      if (value >= 30) return 'Good'
      if (value >= 20) return 'Fair'
      return 'Low'
    case 'net_margin':
      if (value >= 10) return 'Good'
      if (value >= 5) return 'Fair'
      return 'Low'
    default:
      return 'N/A'
  }
}

const getRatioHealthBadge = (value: number | null | undefined, type: string) => {
  const health = getRatioHealth(value, type)
  const base = 'px-2 py-0.5 rounded text-xs font-medium'
  
  switch (health) {
    case 'Good':
      return `${base} bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400`
    case 'Fair':
      return `${base} bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400`
    case 'Low':
    case 'High':
      return `${base} bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400`
    default:
      return `${base} bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400`
  }
}

const getRatioTrendClass = (value: number | null | undefined, benchmark: number) => {
  if (!value) return 'text-gray-600 dark:text-gray-400'
  return value >= benchmark ? 'text-green-600 font-medium' : 'text-amber-600'
}
</script>

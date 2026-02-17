<template>
  <div class="presentation-slide" :class="slideClasses" :style="slideStyles">
    <!-- Title Slide Layout -->
    <div v-if="slide.type === 'title'" class="title-slide text-center py-16">
      <div class="max-w-4xl mx-auto">
        <div v-if="slide.content.logo_placeholder" class="mb-8">
          <div class="w-24 h-24 bg-gray-200 rounded-lg mx-auto flex items-center justify-center">
            <Building class="w-12 h-12 text-gray-500" />
          </div>
        </div>
        
        <h1 class="text-5xl font-bold mb-4" :style="{ color: colors.primary }">
          {{ slide.content.title }}
        </h1>
        
        <h2 class="text-2xl text-gray-600 mb-6">
          {{ slide.content.subtitle }}
        </h2>
        
        <div class="text-lg text-gray-500">
          {{ slide.content.company }}
        </div>
      </div>
    </div>

    <!-- Overview Slide Layout -->
    <div v-else-if="slide.type === 'overview'" class="overview-slide p-8">
      <h2 class="text-3xl font-bold mb-8" :style="{ color: colors.primary }">
        {{ slide.content.title }}
      </h2>
      
      <!-- Metrics Grid Layout -->
      <div v-if="slide.content.layout === 'metrics_grid'" class="grid grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="metric in slide.content.metrics" :key="metric.label" 
             class="bg-white rounded-lg shadow-md p-6 border-l-4"
             :style="{ borderLeftColor: colors.secondary }">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 uppercase tracking-wide">{{ metric.label }}</p>
              <p class="text-2xl font-bold mt-2" :style="{ color: colors.primary }">
                {{ metric.formatted_value }}
              </p>
            </div>
            <div class="p-3 rounded-lg" :style="{ backgroundColor: colors.secondary + '20' }">
              <TrendingUp v-if="metric.trend === 'up'" class="w-6 h-6" :style="{ color: colors.secondary }" />
              <TrendingDown v-else-if="metric.trend === 'down'" class="w-6 h-6" :style="{ color: colors.secondary }" />
              <Minus v-else class="w-6 h-6" :style="{ color: colors.secondary }" />
            </div>
          </div>
        </div>
      </div>

      <!-- Insights List Layout -->
      <div v-else-if="slide.content.layout === 'insights_list'" class="space-y-4">
        <div v-for="insight in slide.content.insights" :key="insight.title" 
             class="bg-white rounded-lg shadow-md p-6">
          <div class="flex items-start space-x-4">
            <div class="p-2 rounded-lg" :style="{ backgroundColor: getInsightColor(insight.impact) + '20' }">
              <AlertCircle class="w-6 h-6" :style="{ color: getInsightColor(insight.impact) }" />
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ insight.title }}</h3>
              <p class="text-gray-700 mb-2">{{ insight.insight }}</p>
              <div class="text-2xl font-bold" :style="{ color: colors.primary }">{{ insight.value }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations Grid Layout -->
      <div v-else-if="slide.content.layout === 'recommendations_grid'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div v-for="rec in slide.content.recommendations" :key="rec.title" 
             class="bg-white rounded-lg shadow-md p-6 border-l-4"
             :style="{ borderLeftColor: getPriorityColor(rec.priority) }">
          <div class="flex items-start justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">{{ rec.title }}</h3>
            <Badge :variant="getPriorityVariant(rec.priority)" class="ml-2">{{ rec.priority }}</Badge>
          </div>
          <p class="text-gray-700 mb-4">{{ rec.description }}</p>
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="text-gray-500">Impact:</span>
              <span class="ml-2 font-medium">{{ rec.impact }}</span>
            </div>
            <div>
              <span class="text-gray-500">Effort:</span>
              <span class="ml-2 font-medium">{{ rec.effort }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart Slide Layout -->
    <div v-else-if="slide.type === 'chart'" class="chart-slide p-8">
      <h2 class="text-3xl font-bold mb-8" :style="{ color: colors.primary }">
        {{ slide.content.title }}
      </h2>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Chart Container -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-md p-6 h-80">
            <!-- Chart Placeholder -->
            <div class="h-full flex items-center justify-center text-gray-500">
              <div class="text-center">
                <BarChart class="w-16 h-16 mx-auto mb-4" />
                <p class="text-lg font-medium">Chart Visualization</p>
                <p class="text-sm">{{ slide.content.chart_type || 'Line' }} Chart</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Chart Insights -->
        <div class="space-y-4">
          <h3 class="text-xl font-semibold text-gray-900">Key Insights</h3>
          <div v-for="insight in slide.content.insights" :key="insight" 
               class="bg-white rounded-lg shadow-sm p-4">
            <div class="flex items-center space-x-3">
              <div class="w-2 h-2 rounded-full" :style="{ backgroundColor: colors.secondary }"></div>
              <span class="text-gray-700">{{ insight }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Slide Layout -->
    <div v-else-if="slide.type === 'table'" class="table-slide p-8">
      <h2 class="text-3xl font-bold mb-8" :style="{ color: colors.primary }">
        {{ slide.content.title }}
      </h2>
      
      <div v-if="slide.content.table_data" class="bg-white rounded-lg shadow-md overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead :style="{ backgroundColor: colors.primary + '10' }">
            <tr>
              <th v-for="header in slide.content.table_data.headers" :key="header"
                  class="px-6 py-4 text-left text-sm font-semibold text-gray-900 uppercase tracking-wider">
                {{ header }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(row, index) in slide.content.table_data.rows" :key="index" 
                class="hover:bg-gray-50">
              <td v-for="(cell, cellIndex) in row" :key="cellIndex" 
                  class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <span v-if="cellIndex === row.length - 1" class="font-medium">{{ cell }}</span>
                <span v-else>{{ cell }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Default/Unknown Layout -->
    <div v-else class="default-slide p-8">
      <div class="text-center py-16">
        <h2 class="text-3xl font-bold text-gray-900 mb-4">{{ slide.content.title || 'Slide Content' }}</h2>
        <p class="text-gray-600">Slide type: {{ slide.type }}</p>
      </div>
    </div>

    <!-- Slide Footer -->
    <div v-if="fullscreen" class="slide-footer absolute bottom-4 left-8 right-8">
      <div class="flex items-center justify-between text-white text-sm">
        <div>{{ slide.content.company || 'Company Name' }}</div>
        <div>{{ new Date().toLocaleDateString() }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Badge } from 'frappe-ui'
import { 
  Building, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertCircle, 
  BarChart 
} from 'lucide-vue-next'

// Props
const props = defineProps({
  slide: {
    type: Object,
    required: true
  },
  fullscreen: {
    type: Boolean,
    default: false
  },
  colors: {
    type: Object,
    default: () => ({
      primary: '#1f2937',
      secondary: '#3b82f6',
      accent: '#10b981'
    })
  }
})

// Computed properties
const slideClasses = computed(() => {
  return [
    'presentation-slide',
    `slide-${props.slide.type}`,
    {
      'fullscreen-slide': props.fullscreen,
      'embedded-slide': !props.fullscreen
    }
  ]
})

const slideStyles = computed(() => {
  if (props.fullscreen) {
    return {
      background: `linear-gradient(135deg, ${props.colors.primary} 0%, ${props.colors.secondary} 100%)`,
      color: 'white',
      minHeight: '100vh',
      position: 'relative'
    }
  }
  
  return {
    backgroundColor: '#f9fafb',
    minHeight: '400px',
    position: 'relative'
  }
})

// Helper methods
const getInsightColor = (impact) => {
  const colors = {
    'high': '#ef4444',
    'medium': '#f59e0b', 
    'low': '#3b82f6'
  }
  return colors[impact?.toLowerCase()] || '#6b7280'
}

const getPriorityColor = (priority) => {
  const colors = {
    'high': '#ef4444',
    'medium': '#f59e0b',
    'low': '#3b82f6'
  }
  return colors[priority?.toLowerCase()] || '#6b7280'
}

const getPriorityVariant = (priority) => {
  const variants = {
    'high': 'red',
    'medium': 'yellow',
    'low': 'blue'
  }
  return variants[priority?.toLowerCase()] || 'gray'
}
</script>

<style scoped>
.presentation-slide {
  transition: all 0.3s ease;
}

.fullscreen-slide {
  padding: 2rem;
}

.embedded-slide {
  padding: 1.5rem;
  border-radius: 0.5rem;
}

.title-slide h1 {
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.title-slide h2 {
  line-height: 1.3;
}

/* Animation for metrics */
.metrics-grid > div {
  animation: slideInUp 0.6s ease-out;
}

.metrics-grid > div:nth-child(2) {
  animation-delay: 0.1s;
}

.metrics-grid > div:nth-child(3) {
  animation-delay: 0.2s;
}

.metrics-grid > div:nth-child(4) {
  animation-delay: 0.3s;
}

.metrics-grid > div:nth-child(5) {
  animation-delay: 0.4s;
}

.metrics-grid > div:nth-child(6) {
  animation-delay: 0.5s;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive text scaling */
@media (max-width: 768px) {
  .title-slide h1 {
    font-size: 2.5rem;
  }
  
  .title-slide h2 {
    font-size: 1.5rem;
  }
  
  .overview-slide h2,
  .chart-slide h2,
  .table-slide h2 {
    font-size: 2rem;
  }
}

/* Print optimizations */
@media print {
  .presentation-slide {
    background: white !important;
    color: black !important;
    page-break-inside: avoid;
    margin-bottom: 2rem;
  }
  
  .fullscreen-slide {
    min-height: auto;
  }
  
  .slide-footer {
    position: static;
    border-top: 1px solid #e5e7eb;
    padding-top: 1rem;
    margin-top: 2rem;
    color: black !important;
  }
}
</style>
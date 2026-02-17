<template>
  <div class="manufacturing-dashboard min-h-screen bg-gray-50">
    <!-- Header Section -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between py-6">
          <div class="flex items-center space-x-4">
            <div class="p-3 bg-blue-500 rounded-lg">
              <Settings class="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900">Manufacturing Intelligence</h1>
              <p class="text-gray-600">Production & Operations Analytics</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <select 
              v-model="selectedPeriod" 
              @change="refreshData"
              class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="MTD">Month to Date</option>
              <option value="QTD">Quarter to Date</option>
              <option value="YTD">Year to Date</option>
              <option value="TTM">Trailing 12 Months</option>
            </select>
            <Button 
              @click="refreshData" 
              size="sm" 
              :disabled="loading"
              class="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <RefreshCw class="h-4 w-4 mr-2" :class="{ 'animate-spin': loading }" />
              Refresh
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-gray-600 mt-4">Loading manufacturing data...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-6">
        <div class="flex items-center">
          <AlertCircle class="h-6 w-6 text-red-600 mr-3" />
          <div>
            <h3 class="text-lg font-semibold text-red-800">Error Loading Data</h3>
            <p class="text-red-700 mt-1">{{ error }}</p>
            <Button @click="refreshData" size="sm" class="mt-3 bg-red-600 hover:bg-red-700 text-white">
              Try Again
            </Button>
          </div>
        </div>
      </div>

      <!-- Dashboard Content -->
      <div v-else-if="manufacturingData" class="space-y-8">
        <!-- OEE Overview Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold text-gray-900 flex items-center">
              <Activity class="h-6 w-6 mr-2 text-blue-600" />
              Overall Equipment Effectiveness (OEE)
            </h2>
            <div class="flex items-center space-x-2">
              <div 
                :class="oeeStatusColor" 
                class="px-3 py-1 rounded-full text-sm font-medium"
              >
                {{ oeeRating }}
              </div>
            </div>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <!-- OEE Score -->
            <div class="text-center">
              <div class="relative w-24 h-24 mx-auto mb-3">
                <svg viewBox="0 0 42 42" class="w-full h-full">
                  <circle cx="21" cy="21" r="15.91549430918954" fill="transparent" stroke="#e5e7eb" stroke-width="3"></circle>
                  <circle 
                    cx="21" 
                    cy="21" 
                    r="15.91549430918954" 
                    fill="transparent" 
                    :stroke="oeeScoreColor"
                    stroke-width="3"
                    :stroke-dasharray="`${oeeScore} ${100 - oeeScore}`"
                    stroke-dashoffset="25"
                    transform="rotate(-90 21 21)"
                  ></circle>
                </svg>
                <div class="absolute inset-0 flex items-center justify-center">
                  <span class="text-lg font-bold text-gray-900">{{ oeeScore }}%</span>
                </div>
              </div>
              <h3 class="font-semibold text-gray-900">OEE Score</h3>
              <p class="text-sm text-gray-600">Overall effectiveness</p>
            </div>

            <!-- Availability -->
            <div class="text-center">
              <div class="text-3xl font-bold mb-2" :class="availabilityColor">{{ availability }}%</div>
              <h3 class="font-semibold text-gray-900">Availability</h3>
              <p class="text-sm text-gray-600">Equipment uptime</p>
              <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  class="h-2 rounded-full"
                  :class="availabilityColor"
                  :style="{ width: `${availability}%` }"
                ></div>
              </div>
            </div>

            <!-- Performance -->
            <div class="text-center">
              <div class="text-3xl font-bold mb-2" :class="performanceColor">{{ performance }}%</div>
              <h3 class="font-semibold text-gray-900">Performance</h3>
              <p class="text-sm text-gray-600">Speed efficiency</p>
              <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  class="h-2 rounded-full"
                  :class="performanceColor"
                  :style="{ width: `${performance}%` }"
                ></div>
              </div>
            </div>

            <!-- Quality -->
            <div class="text-center">
              <div class="text-3xl font-bold mb-2" :class="qualityColor">{{ quality }}%</div>
              <h3 class="font-semibold text-gray-900">Quality</h3>
              <p class="text-sm text-gray-600">First pass yield</p>
              <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div 
                  class="h-2 rounded-full"
                  :class="qualityColor"
                  :style="{ width: `${quality}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Production Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <!-- Production Overview -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Production Overview</h3>
              <CheckCircle class="h-6 w-6 text-green-600" />
            </div>
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Work Orders</span>
                <span class="font-semibold">{{ totalWorkOrders }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Completed</span>
                <span class="font-semibold text-green-600">{{ completedOrders }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Completion Rate</span>
                <span 
                  class="font-semibold"
                  :class="completionRate >= 90 ? 'text-green-600' : completionRate >= 80 ? 'text-yellow-600' : 'text-red-600'"
                >
                  {{ completionRate }}%
                </span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Production Qty</span>
                <span class="font-semibold">{{ totalProductionQty.toLocaleString() }}</span>
              </div>
            </div>
          </div>

          <!-- Capacity Utilization -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Capacity</h3>
              <Factory class="h-6 w-6 text-blue-600" />
            </div>
            <div class="space-y-4">
              <div class="text-center">
                <div class="text-2xl font-bold mb-1" :class="capacityUtilizationColor">
                  {{ capacityUtilization }}%
                </div>
                <p class="text-sm text-gray-600 mb-3">Overall Utilization</p>
                <div class="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    class="h-3 rounded-full transition-all duration-300"
                    :class="capacityUtilizationColor.replace('text-', 'bg-')"
                    :style="{ width: `${capacityUtilization}%` }"
                  ></div>
                </div>
              </div>
              <div class="pt-2">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600">Available Capacity</span>
                  <span class="font-semibold text-green-600">{{ availableCapacity }}%</span>
                </div>
                <div class="flex justify-between items-center mt-2">
                  <span class="text-sm text-gray-600">Bottlenecks</span>
                  <span 
                    class="font-semibold"
                    :class="bottleneckCount > 0 ? 'text-red-600' : 'text-green-600'"
                  >
                    {{ bottleneckCount }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Efficiency Metrics -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg font-semibold text-gray-900">Efficiency</h3>
              <TrendingUp class="h-6 w-6 text-green-600" />
            </div>
            <div class="space-y-4">
              <div class="text-center">
                <div class="text-2xl font-bold mb-1" :class="efficiencyColor">
                  {{ averageEfficiency }}%
                </div>
                <p class="text-sm text-gray-600 mb-3">Average Efficiency</p>
              </div>
              <div class="space-y-2">
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600">Consistency</span>
                  <span 
                    class="px-2 py-1 rounded text-xs font-medium"
                    :class="consistencyClass"
                  >
                    {{ consistencyRating }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <span class="text-sm text-gray-600">Monthly Growth</span>
                  <span 
                    class="font-semibold"
                    :class="monthlyGrowth >= 0 ? 'text-green-600' : 'text-red-600'"
                  >
                    {{ monthlyGrowth >= 0 ? '+' : '' }}{{ monthlyGrowth }}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Workstation Performance -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-semibold text-gray-900 flex items-center">
              <Cog class="h-6 w-6 mr-2 text-gray-600" />
              Workstation Performance
            </h3>
            <Button size="sm" variant="ghost" @click="showWorkstationDetails = !showWorkstationDetails">
              {{ showWorkstationDetails ? 'Hide Details' : 'Show Details' }}
            </Button>
          </div>
          
          <div v-if="workstationPerformance.length > 0" class="space-y-4">
            <!-- Summary Row -->
            <div class="grid grid-cols-4 gap-4 text-sm font-medium text-gray-600 border-b border-gray-200 pb-2">
              <span>Workstation</span>
              <span>Utilization</span>
              <span>Capacity (hrs)</span>
              <span>Status</span>
            </div>
            
            <!-- Workstation Rows -->
            <div 
              v-for="(ws, index) in displayedWorkstations" 
              :key="index"
              class="grid grid-cols-4 gap-4 items-center py-2 hover:bg-gray-50 transition-colors"
            >
              <span class="font-medium text-gray-900">{{ ws.workstation }}</span>
              <div class="flex items-center space-x-2">
                <span class="font-semibold">{{ ws.utilization_pct }}%</span>
                <div class="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full"
                    :class="getUtilizationColor(ws.utilization_pct)"
                    :style="{ width: `${Math.min(ws.utilization_pct, 100)}%` }"
                  ></div>
                </div>
              </div>
              <span class="text-gray-700">{{ ws.capacity_hours }}h</span>
              <span 
                class="px-2 py-1 rounded text-xs font-medium"
                :class="getStatusClass(ws.status)"
              >
                {{ ws.status }}
              </span>
            </div>
          </div>
          
          <div v-else class="text-center py-8 text-gray-500">
            <Cog class="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No workstation performance data available</p>
          </div>
        </div>

        <!-- Recommendations Section -->
        <div v-if="recommendations.length > 0" class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div class="flex items-center mb-6">
            <Lightbulb class="h-6 w-6 mr-3 text-yellow-500" />
            <h3 class="text-lg font-semibold text-gray-900">AI Recommendations</h3>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div 
              v-for="(rec, index) in recommendations" 
              :key="index"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div class="flex items-center justify-between mb-2">
                <span 
                  class="px-2 py-1 rounded text-xs font-medium"
                  :class="getPriorityClass(rec.priority)"
                >
                  {{ rec.priority }} Priority
                </span>
              </div>
              <h4 class="font-semibold text-gray-900 mb-2">{{ rec.title }}</h4>
              <p class="text-sm text-gray-600 mb-3">{{ rec.description }}</p>
              <div v-if="rec.actions" class="space-y-1">
                <p class="text-xs font-medium text-gray-700">Suggested Actions:</p>
                <ul class="text-xs text-gray-600 space-y-1">
                  <li v-for="action in rec.actions" :key="action" class="flex items-start">
                    <span class="w-1.5 h-1.5 bg-blue-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                    {{ action }}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  Settings, RefreshCw, AlertCircle, Activity, CheckCircle, 
  Factory, TrendingUp, Cog, Lightbulb 
} from 'lucide-vue-next'
import { Button } from 'frappe-ui'
import { apiCall } from '../helpers/api'

const loading = ref(false)
const error = ref(null)
const selectedPeriod = ref('YTD')
const showWorkstationDetails = ref(false)

// Manufacturing overview data
const manufacturingData = ref(null)

// OEE data
const oeeScore = ref(0)
const availability = ref(0)
const performance = ref(0)
const quality = ref(0)
const oeeRating = ref('unknown')

// Production metrics
const totalWorkOrders = ref(0)
const completedOrders = ref(0)
const completionRate = ref(0)
const totalProductionQty = ref(0)
const monthlyGrowth = ref(0)

// Capacity metrics
const capacityUtilization = ref(0)
const availableCapacity = ref(0)
const bottleneckCount = ref(0)

// Efficiency metrics
const averageEfficiency = ref(0)
const consistencyRating = ref('unknown')

// Workstation data
const workstationPerformance = ref([])

// Recommendations
const recommendations = ref([])

// Computed
const oeeStatusColor = computed(() => {
  if (oeeScore.value >= 85) return 'bg-green-100 text-green-800'
  if (oeeScore.value >= 60) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
})

const oeeScoreColor = computed(() => {
  if (oeeScore.value >= 85) return '#10b981'
  if (oeeScore.value >= 60) return '#f59e0b'
  return '#ef4444'
})

const availabilityColor = computed(() => {
  if (availability.value >= 90) return 'text-green-600 bg-green-100'
  if (availability.value >= 80) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
})

const performanceColor = computed(() => {
  if (performance.value >= 95) return 'text-green-600 bg-green-100'
  if (performance.value >= 85) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
})

const qualityColor = computed(() => {
  if (quality.value >= 99) return 'text-green-600 bg-green-100'
  if (quality.value >= 95) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
})

const capacityUtilizationColor = computed(() => {
  if (capacityUtilization.value <= 85 && capacityUtilization.value >= 70) return 'text-green-600'
  if (capacityUtilization.value > 85) return 'text-red-600'
  return 'text-yellow-600'
})

const efficiencyColor = computed(() => {
  if (averageEfficiency.value >= 80) return 'text-green-600'
  if (averageEfficiency.value >= 60) return 'text-yellow-600'
  return 'text-red-600'
})

const consistencyClass = computed(() => {
  const rating = consistencyRating.value.toLowerCase()
  if (rating === 'high') return 'bg-green-100 text-green-800'
  if (rating === 'medium') return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
})

const displayedWorkstations = computed(() => {
  if (showWorkstationDetails.value) return workstationPerformance.value
  return workstationPerformance.value.slice(0, 5)
})

onMounted(() => {
  loadManufacturingData()
})

async function loadManufacturingData() {
  loading.value = true
  error.value = null
  
  try {
    const result = await apiCall('insights.api.ml.get_manufacturing_overview', {
      period: selectedPeriod.value
    })

    manufacturingData.value = result
    processManufacturingData(result)
    
  } catch (err) {
    console.error('Error loading manufacturing data:', err)
    error.value = err.message || 'Failed to load manufacturing data'
  } finally {
    loading.value = false
  }
}

function processManufacturingData(data) {
  // Process OEE data
  const oeeData = data.oee_analysis || {}
  oeeScore.value = oeeData.oee_score_pct || 0
  availability.value = oeeData.availability_pct || 0
  performance.value = oeeData.performance_pct || 0
  quality.value = oeeData.quality_pct || 0
  oeeRating.value = oeeData.oee_rating || 'unknown'
  
  // Process production metrics
  const productionData = data.production_metrics || {}
  totalWorkOrders.value = productionData.total_work_orders || 0
  completedOrders.value = productionData.completed_orders || 0
  completionRate.value = productionData.completion_rate_pct || 0
  totalProductionQty.value = productionData.total_production_qty || 0
  monthlyGrowth.value = productionData.monthly_growth_rate || 0
  
  // Process capacity data
  const capacityData = data.capacity_utilization || {}
  capacityUtilization.value = capacityData.overall_utilization_pct || 0
  availableCapacity.value = capacityData.available_capacity_pct || 0
  
  const bottleneckData = data.bottleneck_analysis || {}
  bottleneckCount.value = bottleneckData.bottleneck_count || 0
  
  // Process efficiency data
  const efficiencyData = data.efficiency_metrics || {}
  averageEfficiency.value = efficiencyData.average_efficiency_pct || 0
  consistencyRating.value = efficiencyData.consistency_rating || 'unknown'
  
  // Process workstation data
  const workstationData = data.workstation_performance || {}
  workstationPerformance.value = workstationData.workstation_performance || []
  
  // Process recommendations
  recommendations.value = data.recommendations || []
}

async function refreshData() {
  await loadManufacturingData()
}

function getUtilizationColor(utilization) {
  if (utilization > 90) return 'bg-red-400'
  if (utilization > 80) return 'bg-yellow-400'
  if (utilization > 60) return 'bg-green-400'
  return 'bg-gray-400'
}

function getStatusClass(status) {
  const statusLower = status.toLowerCase()
  if (statusLower === 'optimal') return 'bg-green-100 text-green-800'
  if (statusLower === 'overloaded') return 'bg-red-100 text-red-800'
  return 'bg-yellow-100 text-yellow-800'
}

function getPriorityClass(priority) {
  const priorityLower = priority.toLowerCase()
  if (priorityLower === 'high') return 'bg-red-100 text-red-800'
  if (priorityLower === 'medium') return 'bg-yellow-100 text-yellow-800'
  return 'bg-blue-100 text-blue-800'
}
</script>

<style scoped>
.manufacturing-dashboard {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.transition-all {
  transition: all 0.3s ease;
}

.hover\:shadow-md:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

/* Custom scrollbar for workstation list */
.workstation-list {
  max-height: 400px;
  overflow-y: auto;
}

.workstation-list::-webkit-scrollbar {
  width: 6px;
}

.workstation-list::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.workstation-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.workstation-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
<template>
  <div class="esg-intelligence p-4">
    <!-- Header Section -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">ESG Intelligence</h1>
        <p class="text-gray-600 mt-1">Environmental, Social & Governance analytics for sustainable business practices</p>
      </div>
      <div class="flex gap-3">
        <Button variant="outline" @click="refreshData" :loading="loading">
          <RefreshCw class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        <Button variant="solid" @click="generateESGReport">
          <FileOutput class="w-4 h-4 mr-2" />
          ESG Report
        </Button>
      </div>
    </div>

    <!-- ESG Score Overview -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
      <!-- Overall ESG Score -->
      <Card class="p-4 lg:col-span-1">
        <div class="text-center">
          <h3 class="text-sm font-medium text-gray-700 mb-2">Overall ESG Score</h3>
          <div class="relative inline-flex items-center justify-center">
            <div class="w-24 h-24 rounded-full border-8 flex items-center justify-center"
                 :class="getScoreColorClass(esgScore.overall_score)">
              <span class="text-2xl font-bold" :class="getScoreTextClass(esgScore.overall_score)">
                {{ esgScore.overall_score || 0 }}
              </span>
            </div>
          </div>
          <p class="text-sm mt-2" :class="getRatingColorClass(esgScore.rating)">
            Rating: {{ esgScore.rating || 'Not Rated' }}
          </p>
          <p class="text-xs text-gray-500 mt-1">{{ esgScore.rating_description || 'ESG performance evaluation' }}</p>
        </div>
      </Card>

      <!-- Environmental Score -->
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-700">Environmental</h3>
            <p class="text-3xl font-bold text-green-600 mt-1">{{ esgScore.environmental_score || 0 }}</p>
            <p class="text-sm text-gray-500">Carbon & Resource Impact</p>
          </div>
          <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
            <Leaf class="w-6 h-6 text-green-600" />
          </div>
        </div>
      </Card>

      <!-- Social Score -->
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-700">Social</h3>
            <p class="text-3xl font-bold text-blue-600 mt-1">{{ esgScore.social_score || 0 }}</p>
            <p class="text-sm text-gray-500">People & Community</p>
          </div>
          <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <Users class="w-6 h-6 text-blue-600" />
          </div>
        </div>
      </Card>

      <!-- Governance Score -->
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div class="flex-1">
            <h3 class="text-sm font-medium text-gray-700">Governance</h3>
            <p class="text-3xl font-bold text-purple-600 mt-1">{{ esgScore.governance_score || 0 }}</p>
            <p class="text-sm text-gray-500">Ethics & Compliance</p>
          </div>
          <div class="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
            <Shield class="w-6 h-6 text-purple-600" />
          </div>
        </div>
      </Card>
    </div>

    <!-- Environmental Metrics -->
    <Card class="mb-6">
      <div class="p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900 flex items-center">
          <Leaf class="w-5 h-5 mr-2 text-green-600" />
          Environmental Impact
        </h3>
      </div>
      <div class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="bg-green-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <Zap class="w-5 h-5 text-green-600" />
              <span class="text-sm font-medium text-green-900">Energy</span>
            </div>
            <p class="text-2xl font-bold text-green-800">{{ environmentalMetrics.renewable_energy_pct || 0 }}%</p>
            <p class="text-sm text-green-700">Renewable Energy</p>
          </div>
          
          <div class="bg-blue-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <Droplets class="w-5 h-5 text-blue-600" />
              <span class="text-sm font-medium text-blue-900">Water</span>
            </div>
            <p class="text-2xl font-bold text-blue-800">{{ environmentalMetrics.water_recycled_pct || 0 }}%</p>
            <p class="text-sm text-blue-700">Water Recycled</p>
          </div>
          
          <div class="bg-yellow-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <Recycle class="w-5 h-5 text-yellow-600" />
              <span class="text-sm font-medium text-yellow-900">Waste</span>
            </div>
            <p class="text-2xl font-bold text-yellow-800">{{ environmentalMetrics.recycled_waste_pct || 0 }}%</p>
            <p class="text-sm text-yellow-700">Waste Recycled</p>
          </div>
          
          <div class="bg-gray-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-2">
              <Cloud class="w-5 h-5 text-gray-600" />
              <span class="text-sm font-medium text-gray-900">Emissions</span>
            </div>
            <p class="text-2xl font-bold text-gray-800">{{ carbonFootprint.total_emissions_tco2 || 0 }}</p>
            <p class="text-sm text-gray-700">tCO2 Footprint</p>
          </div>
        </div>
        
        <!-- Green Initiatives -->
        <div class="mt-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Green Initiatives</h4>
          <div v-if="greenInitiatives.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="initiative in greenInitiatives" :key="initiative.name" 
                 class="border border-gray-200 rounded-lg p-3">
              <div class="flex items-center justify-between mb-2">
                <h5 class="font-medium text-gray-900">{{ initiative.name }}</h5>
                <span class="px-2 py-1 text-xs rounded-full" 
                      :class="getInitiativeStatusClass(initiative.status)">
                  {{ initiative.status }}
                </span>
              </div>
              <div class="mb-2">
                <div class="flex justify-between text-sm text-gray-600 mb-1">
                  <span>Progress</span>
                  <span>{{ initiative.progress_pct }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div class="bg-green-600 h-2 rounded-full" :style="{width: initiative.progress_pct + '%'}"></div>
                </div>
              </div>
              <p class="text-sm text-gray-600">{{ initiative.expected_impact }}</p>
              <p class="text-xs text-gray-500 mt-1">Target: {{ formatDate(initiative.target_completion) }}</p>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            <TreePine class="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p>No green initiatives tracked</p>
          </div>
        </div>
      </div>
    </Card>

    <!-- Social Responsibility Metrics -->
    <Card class="mb-6">
      <div class="p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900 flex items-center">
          <Users class="w-5 h-5 mr-2 text-blue-600" />
          Social Responsibility
        </h3>
      </div>
      <div class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Employee Wellbeing -->
          <div class="bg-blue-50 p-4 rounded-lg">
            <h4 class="font-medium text-blue-900 mb-3">Employee Wellbeing</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-sm text-blue-700">Satisfaction Score</span>
                <span class="font-medium text-blue-900">{{ employeeWellbeing.employee_satisfaction_score || 0 }}/5</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-blue-700">Work-Life Balance</span>
                <span class="font-medium text-blue-900">{{ employeeWellbeing.work_life_balance_score || 0 }}/5</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-blue-700">Wellness Participation</span>
                <span class="font-medium text-blue-900">{{ employeeWellbeing.wellness_program_enrollment || 0 }}%</span>
              </div>
            </div>
          </div>
          
          <!-- Diversity & Inclusion -->
          <div class="bg-purple-50 p-4 rounded-lg">
            <h4 class="font-medium text-purple-900 mb-3">Diversity & Inclusion</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-sm text-purple-700">Inclusion Index</span>
                <span class="font-medium text-purple-900">{{ diversityMetrics.inclusion_index || 0 }}/10</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-purple-700">Diverse Hiring</span>
                <span class="font-medium text-purple-900">{{ diversityMetrics.diverse_hiring_pct || 0 }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-purple-700">Training Completion</span>
                <span class="font-medium text-purple-900">{{ diversityMetrics.diversity_training_completion || 0 }}%</span>
              </div>
            </div>
          </div>
          
          <!-- Community Impact -->
          <div class="bg-green-50 p-4 rounded-lg">
            <h4 class="font-medium text-green-900 mb-3">Community Impact</h4>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-sm text-green-700">Volunteer Participation</span>
                <span class="font-medium text-green-900">{{ communityMetrics.volunteer_participation_pct || 0 }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-green-700">Local Suppliers</span>
                <span class="font-medium text-green-900">{{ communityMetrics.local_supplier_spend_pct || 0 }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-sm text-green-700">Partnerships</span>
                <span class="font-medium text-green-900">{{ communityMetrics.community_partnerships || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Health & Safety -->
        <div class="mt-6 bg-red-50 p-4 rounded-lg">
          <h4 class="font-medium text-red-900 mb-3 flex items-center">
            <Shield class="w-4 h-4 mr-2" />
            Health & Safety
          </h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
              <p class="text-2xl font-bold text-red-800">{{ safetyMetrics.safety_culture_index || 0 }}</p>
              <p class="text-sm text-red-700">Safety Culture /10</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-red-800">{{ safetyMetrics.safety_training_completion_pct || 0 }}%</p>
              <p class="text-sm text-red-700">Training Complete</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-red-800">{{ safetyMetrics.workplace_inspection_score || 0 }}</p>
              <p class="text-sm text-red-700">Inspection Score /10</p>
            </div>
            <div class="text-center">
              <p class="text-2xl font-bold text-red-800">{{ safetyMetrics.lost_time_injury_rate || 0 }}</p>
              <p class="text-sm text-red-700">Lost Time Injuries</p>
            </div>
          </div>
        </div>
      </div>
    </Card>

    <!-- Governance & Compliance -->
    <Card class="mb-6">
      <div class="p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900 flex items-center">
          <Shield class="w-5 h-5 mr-2 text-purple-600" />
          Governance & Compliance
        </h3>
      </div>
      <div class="p-4">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="bg-purple-50 p-4 rounded-lg">
            <h4 class="font-medium text-purple-900 mb-3">Ethics & Compliance</h4>
            <div class="text-center">
              <p class="text-3xl font-bold text-purple-800">{{ governanceScore.ethics_score || 0 }}</p>
              <p class="text-sm text-purple-700">Compliance Score</p>
            </div>
          </div>
          
          <div class="bg-indigo-50 p-4 rounded-lg">
            <h4 class="font-medium text-indigo-900 mb-3">Risk Management</h4>
            <div class="text-center">
              <p class="text-3xl font-bold text-indigo-800">{{ governanceScore.risk_score || 0 }}</p>
              <p class="text-sm text-indigo-700">Risk Score</p>
            </div>
          </div>
          
          <div class="bg-gray-50 p-4 rounded-lg">
            <h4 class="font-medium text-gray-900 mb-3">Transparency</h4>
            <div class="text-center">
              <p class="text-3xl font-bold text-gray-800">{{ governanceScore.transparency_score || 0 }}</p>
              <p class="text-sm text-gray-700">Transparency Score</p>
            </div>
          </div>
        </div>
      </div>
    </Card>

    <!-- ESG Recommendations -->
    <Card class="mb-6" v-if="recommendations.length > 0">
      <div class="p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900 flex items-center">
          <Target class="w-5 h-5 mr-2 text-orange-600" />
          ESG Improvement Recommendations
        </h3>
      </div>
      <div class="p-4">
        <div class="space-y-4">
          <div v-for="rec in recommendations" :key="rec.recommendation" 
               class="border border-gray-200 rounded-lg p-4">
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <span class="px-2 py-1 text-xs font-medium rounded-full"
                        :class="getPriorityColorClass(rec.priority)">
                    {{ rec.priority?.toUpperCase() || 'MEDIUM' }}
                  </span>
                  <span class="text-sm text-gray-600">{{ rec.category }}</span>
                </div>
                <h4 class="font-medium text-gray-900 mb-2">{{ rec.recommendation }}</h4>
                <p class="text-sm text-gray-600 mb-1">{{ rec.impact }}</p>
                <p class="text-xs text-gray-500">Timeline: {{ rec.timeframe }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Card>

    <!-- ESG Trends Chart -->
    <Card v-if="chartData">
      <div class="p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900 flex items-center">
          <TrendingUp class="w-5 h-5 mr-2 text-blue-600" />
          ESG Performance Trends
        </h3>
      </div>
      <div class="p-4">
        <div class="h-64" ref="chartContainer">
          <!-- Chart will be rendered here -->
        </div>
      </div>
    </Card>

    <!-- Loading State -->
    <div v-if="loading" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-sm w-full mx-4">
        <div class="flex items-center space-x-3">
          <Loader class="w-6 h-6 animate-spin text-blue-600" />
          <p class="text-gray-900">Loading ESG intelligence...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { 
  Leaf, Users, Shield, Zap, Droplets, Recycle, Cloud, TreePine, Target,
  RefreshCw, FileOutput, TrendingUp, Loader 
} from 'lucide-vue-next'
import { Button, Card } from 'frappe-ui'
import { apiCall } from '../helpers/api'

// Reactive data
const loading = ref(false)
const esgData = ref({})
const chartContainer = ref(null)

// Computed properties for data access
const esgScore = computed(() => esgData.value.esg_score || {})
const environmentalMetrics = computed(() => {
  const env = esgData.value.environmental_metrics || {}
  return {
    renewable_energy_pct: env.energy_consumption?.renewable_energy_pct || 0,
    water_recycled_pct: env.water_usage?.water_recycled_pct || 0,
    recycled_waste_pct: env.waste_management?.recycled_waste_pct || 0,
  }
})
const carbonFootprint = computed(() => esgData.value.carbon_footprint || {})
const greenInitiatives = computed(() => esgData.value.environmental_metrics?.green_initiatives || [])
const employeeWellbeing = computed(() => esgData.value.social_metrics?.employee_wellbeing || {})
const diversityMetrics = computed(() => esgData.value.social_metrics?.diversity_inclusion || {})
const communityMetrics = computed(() => esgData.value.social_metrics?.community_involvement || {})
const safetyMetrics = computed(() => esgData.value.social_metrics?.health_safety || {})
const governanceScore = computed(() => esgData.value.governance_metrics?.governance_score || {})
const recommendations = computed(() => esgData.value.recommendations || [])
const chartData = computed(() => esgData.value.chart_data || null)

// Methods
const refreshData = async () => {
  loading.value = true
  try {
    esgData.value = await apiCall('insights.api.ml.get_esg_overview', { period: 'YTD' })
    await nextTick()
    renderChart()
  } catch (error) {
    console.error('Error fetching ESG data:', error)
  } finally {
    loading.value = false
  }
}

const generateESGReport = async () => {
  try {
    await apiCall('insights.api.ml.generate_executive_report', { report_type: 'esg' })
    console.log('ESG report generated successfully!')
  } catch (error) {
    console.error('Error generating ESG report:', error)
  }
}

const renderChart = () => {
  if (!chartContainer.value || !chartData.value) return
  
  // Chart rendering would be implemented here using a charting library like Chart.js
  // For now, showing placeholder
  chartContainer.value.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500">ESG trends chart will be displayed here</div>'
}

// Utility functions
const getScoreColorClass = (score) => {
  if (score >= 85) return 'border-green-500'
  if (score >= 70) return 'border-yellow-500' 
  if (score >= 55) return 'border-orange-500'
  return 'border-red-500'
}

const getScoreTextClass = (score) => {
  if (score >= 85) return 'text-green-600'
  if (score >= 70) return 'text-yellow-600'
  if (score >= 55) return 'text-orange-600'
  return 'text-red-600'
}

const getRatingColorClass = (rating) => {
  if (['AAA', 'AA', 'A'].includes(rating)) return 'text-green-600'
  if (['BBB', 'BB'].includes(rating)) return 'text-yellow-600'
  if (['B', 'CCC'].includes(rating)) return 'text-orange-600'
  return 'text-red-600'
}

const getInitiativeStatusClass = (status) => {
  switch (status) {
    case 'Completed': return 'bg-green-100 text-green-800'
    case 'In Progress': return 'bg-blue-100 text-blue-800' 
    case 'Planning': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getPriorityColorClass = (priority) => {
  switch (priority) {
    case 'critical': return 'bg-red-100 text-red-800'
    case 'high': return 'bg-orange-100 text-orange-800'
    case 'medium': return 'bg-yellow-100 text-yellow-800'
    case 'low': return 'bg-blue-100 text-blue-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'TBD'
  return new Date(dateStr).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.esg-intelligence {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
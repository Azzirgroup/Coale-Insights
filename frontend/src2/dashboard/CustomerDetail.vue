<script setup lang="ts">
import { Breadcrumbs, call } from 'frappe-ui'
import { 
  RefreshCcw, Loader2, User, ShoppingCart, TrendingUp, 
  Gift, AlertTriangle, ArrowLeft, Mail, Phone, MapPin,
  Calendar, DollarSign, Heart, Target, ChevronRight,
  Package, Clock, CreditCard, BarChart3, Zap
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createToast } from '../../src/utils/toasts'
import DashboardChatButton from '../components/DashboardChatButton.vue'

const route = useRoute()
const router = useRouter()

// Props
const customerId = computed(() => route.params.customerId as string)

// State
const isLoading = ref(true)
const isRefreshing = ref(false)
const error = ref<string | null>(null)
const customer = ref<any>(null)
const purchaseHistory = ref<any[]>([])
const crossSellRecommendations = ref<any[]>([])
const purchasePatterns = ref<any>(null)

// Sidebar navigation
const activeSection = ref('profile')
const sections = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'purchases', label: 'Purchases', icon: ShoppingCart },
  { id: 'clv', label: 'CLV Analysis', icon: TrendingUp },
  { id: 'recommendations', label: 'Recommendations', icon: Gift },
  { id: 'risk', label: 'Risk Assessment', icon: AlertTriangle },
]

// Filter type for navigation context
const filterType = ref<'clv' | 'territory' | 'rfm'>('clv')
const filterOptions = [
  { value: 'clv', label: 'By CLV Tier' },
  { value: 'territory', label: 'By Territory' },
  { value: 'rfm', label: 'By RFM Segment' },
]

// Load customer data
async function loadCustomerData(refresh = false) {
  if (refresh) {
    isRefreshing.value = true
  } else {
    isLoading.value = true
  }
  error.value = null
  
  try {
    // Load main customer 360 data
    const response = await call('insights.api.ml.customer_360_detail', {
      customer_id: customerId.value,
      include_purchases: true,
      include_recommendations: true
    })
    
    if (response?.status === 'success') {
      customer.value = response.customer
      purchaseHistory.value = response.purchase_history || []
      crossSellRecommendations.value = response.cross_sell || []
      purchasePatterns.value = response.purchase_patterns || null
      
      createToast({
        title: 'Customer Loaded',
        message: `Loaded data for ${response.customer?.customer_name || customerId.value}`,
        variant: 'success'
      })
    } else {
      error.value = response?.message || 'Failed to load customer data'
    }
  } catch (e: any) {
    error.value = e.message || 'Failed to load customer details'
  } finally {
    isLoading.value = false
    isRefreshing.value = false
  }
}

// Navigate back to customer list
function goBack() {
  router.push('/customer-intelligence')
}

// Navigate to related customer by filter
function navigateToRelated(relatedCustomerId: string) {
  router.push(`/customer/${relatedCustomerId}`)
}

// Computed values
const clvTier = computed(() => customer.value?.clv_tier || 'Unknown')
const healthScore = computed(() => customer.value?.health_score || 0)
const healthStatus = computed(() => customer.value?.health_status || 'Unknown')
const churnRisk = computed(() => customer.value?.churn_risk || 'Unknown')
const churnScore = computed(() => customer.value?.churn_score || 0)
const rfmSegment = computed(() => customer.value?.rfm_segment || 'Unknown')

const totalOrders = computed(() => customer.value?.order_count || 0)
const totalRevenue = computed(() => customer.value?.historical_clv || 0)
const avgOrderValue = computed(() => customer.value?.avg_order_value || 0)
const daysSincePurchase = computed(() => customer.value?.days_since_last_purchase || 0)
const predictedClv = computed(() => customer.value?.predicted_12m_clv || 0)

const nextBestActions = computed(() => customer.value?.recommendations || [])

// Helper functions
function formatCurrency(value: number): string {
  if (!value && value !== 0) return 'KES 0'
  if (value >= 1000000) return `KES ${(value / 1000000).toFixed(1)}M`
  if (value >= 1000) return `KES ${(value / 1000).toFixed(1)}K`
  return `KES ${value.toFixed(0)}`
}

function formatNumber(value: number): string {
  return value?.toLocaleString() || '0'
}

function formatDate(dateStr: string): string {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { 
    year: 'numeric', month: 'short', day: 'numeric' 
  })
}

function formatPercent(value: number): string {
  return `${value?.toFixed(1) || 0}%`
}

function getTierColor(tier: string): string {
  const colors: Record<string, string> = {
    'Diamond': 'bg-purple-600',
    'Platinum': 'bg-blue-600',
    'Gold': 'bg-yellow-500',
    'Silver': 'bg-gray-400',
    'Bronze': 'bg-orange-600'
  }
  return colors[tier] || 'bg-gray-500'
}

function getTierBgColor(tier: string): string {
  const colors: Record<string, string> = {
    'Diamond': 'bg-purple-50 border-purple-200',
    'Platinum': 'bg-blue-50 border-blue-200',
    'Gold': 'bg-yellow-50 border-yellow-200',
    'Silver': 'bg-gray-50 border-gray-200',
    'Bronze': 'bg-orange-50 border-orange-200'
  }
  return colors[tier] || 'bg-gray-50 border-gray-200'
}

function getHealthColor(status: string): string {
  const colors: Record<string, string> = {
    'Excellent': 'text-green-600',
    'Healthy': 'text-blue-600',
    'At Risk': 'text-yellow-600',
    'Critical': 'text-red-600'
  }
  return colors[status] || 'text-gray-600'
}

function getHealthBgColor(status: string): string {
  const colors: Record<string, string> = {
    'Excellent': 'bg-green-100 text-green-700',
    'Healthy': 'bg-blue-100 text-blue-700',
    'At Risk': 'bg-yellow-100 text-yellow-700',
    'Critical': 'bg-red-100 text-red-700'
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}

function getRiskColor(risk: string): string {
  const colors: Record<string, string> = {
    'Low': 'bg-green-100 text-green-700',
    'Medium': 'bg-yellow-100 text-yellow-700',
    'High': 'bg-orange-100 text-orange-700',
    'Critical': 'bg-red-100 text-red-700'
  }
  return colors[risk] || 'bg-gray-100 text-gray-700'
}

function getRfmColor(segment: string): string {
  const colors: Record<string, string> = {
    'Champions': 'bg-purple-100 text-purple-700',
    'Loyal Customers': 'bg-blue-100 text-blue-700',
    'Potential Loyalists': 'bg-green-100 text-green-700',
    'New Customers': 'bg-cyan-100 text-cyan-700',
    'Promising': 'bg-teal-100 text-teal-700',
    'Need Attention': 'bg-yellow-100 text-yellow-700',
    'About to Sleep': 'bg-orange-100 text-orange-700',
    'At Risk': 'bg-red-100 text-red-700',
    "Can't Lose": 'bg-pink-100 text-pink-700',
    'Hibernating': 'bg-gray-100 text-gray-700',
    'Lost': 'bg-gray-200 text-gray-600'
  }
  return colors[segment] || 'bg-gray-100 text-gray-700'
}

// Chat context for AI assistant
const chatContext = computed(() => ({
  customer_id: customerId.value,
  customer_name: customer.value?.customer_name,
  clv_tier: clvTier.value,
  health_status: healthStatus.value,
  churn_risk: churnRisk.value,
  total_revenue: totalRevenue.value,
  total_orders: totalOrders.value,
  rfm_segment: rfmSegment.value
}))

// Lifecycle
onMounted(() => {
  loadCustomerData()
})

watch(customerId, () => {
  loadCustomerData()
})
</script>

<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Header -->
    <header class="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-white border-b">
      <div class="flex items-center gap-4">
        <button 
          @click="goBack"
          class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft class="w-5 h-5" />
        </button>
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-xl font-semibold text-gray-900">
              {{ customer?.customer_name || customerId }}
            </h1>
            <span 
              v-if="clvTier !== 'Unknown'"
              :class="['px-3 py-1 text-sm font-medium text-white rounded-full', getTierColor(clvTier)]"
            >
              {{ clvTier }}
            </span>
          </div>
          <p class="text-sm text-gray-500">Customer ID: {{ customerId }}</p>
        </div>
      </div>
      
      <div class="flex items-center gap-3">
        <!-- Filter Type Selector -->
        <select 
          v-model="filterType"
          class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option v-for="opt in filterOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
        
        <button
          @click="loadCustomerData(true)"
          :disabled="isRefreshing"
          class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCcw :class="['w-4 h-4', isRefreshing && 'animate-spin']" />
          Refresh
        </button>
      </div>
    </header>
    
    <!-- Main Content -->
    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar Navigation -->
      <aside class="w-64 bg-white border-r overflow-y-auto">
        <nav class="p-4 space-y-1">
          <button
            v-for="section in sections"
            :key="section.id"
            @click="activeSection = section.id"
            :class="[
              'w-full flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors',
              activeSection === section.id
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            ]"
          >
            <component :is="section.icon" class="w-5 h-5" />
            {{ section.label }}
          </button>
        </nav>
        
        <!-- Quick Stats in Sidebar -->
        <div class="p-4 border-t">
          <h4 class="text-xs font-semibold text-gray-500 uppercase mb-3">Quick Stats</h4>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Health</span>
              <span :class="['px-2 py-1 text-xs font-medium rounded', getHealthBgColor(healthStatus)]">
                {{ healthScore.toFixed(0) }}%
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">Churn Risk</span>
              <span :class="['px-2 py-1 text-xs font-medium rounded', getRiskColor(churnRisk)]">
                {{ churnRisk }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-600">RFM Segment</span>
              <span :class="['px-2 py-1 text-xs font-medium rounded truncate max-w-[100px]', getRfmColor(rfmSegment)]" :title="rfmSegment">
                {{ rfmSegment }}
              </span>
            </div>
          </div>
        </div>
      </aside>
      
      <!-- Content Area -->
      <main class="flex-1 overflow-y-auto p-6">
        <!-- Loading State -->
        <div v-if="isLoading" class="flex items-center justify-center h-64">
          <div class="text-center">
            <Loader2 class="w-10 h-10 mx-auto text-blue-500 animate-spin" />
            <p class="mt-4 text-gray-500">Loading customer data...</p>
          </div>
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="flex items-center justify-center h-64">
          <div class="text-center">
            <AlertTriangle class="w-12 h-12 mx-auto text-red-400" />
            <p class="mt-4 text-red-600">{{ error }}</p>
            <button
              @click="loadCustomerData(true)"
              class="mt-4 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              Try Again
            </button>
          </div>
        </div>
        
        <!-- Content Sections -->
        <div v-else>
          <!-- Profile Section -->
          <div v-if="activeSection === 'profile'" class="space-y-6">
            <!-- Key Metrics Cards -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div :class="['p-5 rounded-xl border', getTierBgColor(clvTier)]">
                <div class="flex items-center gap-2 text-gray-600 mb-2">
                  <DollarSign class="w-4 h-4" />
                  <span class="text-sm">Total Revenue</span>
                </div>
                <p class="text-2xl font-bold text-gray-900">{{ formatCurrency(totalRevenue) }}</p>
                <p class="text-xs text-gray-500 mt-1">Lifetime Value</p>
              </div>
              
              <div class="p-5 bg-white rounded-xl border border-gray-200">
                <div class="flex items-center gap-2 text-gray-600 mb-2">
                  <ShoppingCart class="w-4 h-4" />
                  <span class="text-sm">Total Orders</span>
                </div>
                <p class="text-2xl font-bold text-gray-900">{{ formatNumber(totalOrders) }}</p>
                <p class="text-xs text-gray-500 mt-1">AOV: {{ formatCurrency(avgOrderValue) }}</p>
              </div>
              
              <div class="p-5 bg-white rounded-xl border border-gray-200">
                <div class="flex items-center gap-2 text-gray-600 mb-2">
                  <TrendingUp class="w-4 h-4" />
                  <span class="text-sm">Predicted CLV (12m)</span>
                </div>
                <p class="text-2xl font-bold text-green-600">{{ formatCurrency(predictedClv) }}</p>
                <p class="text-xs text-gray-500 mt-1">Next 12 months</p>
              </div>
              
              <div class="p-5 bg-white rounded-xl border border-gray-200">
                <div class="flex items-center gap-2 text-gray-600 mb-2">
                  <Clock class="w-4 h-4" />
                  <span class="text-sm">Last Purchase</span>
                </div>
                <p class="text-2xl font-bold text-gray-900">{{ daysSincePurchase }}</p>
                <p class="text-xs text-gray-500 mt-1">days ago</p>
              </div>
            </div>
            
            <!-- Customer Details -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div class="p-6 bg-white rounded-xl border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <User class="w-5 h-5" />
                  Customer Information
                </h3>
                <div class="space-y-4">
                  <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-sm text-gray-600">Customer Group</span>
                    <span class="text-sm font-medium text-gray-900">{{ customer?.customer_group || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-sm text-gray-600">Territory</span>
                    <span class="text-sm font-medium text-gray-900">{{ customer?.territory || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-sm text-gray-600">Account Manager</span>
                    <span class="text-sm font-medium text-gray-900">{{ customer?.account_manager || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-sm text-gray-600">Customer Since</span>
                    <span class="text-sm font-medium text-gray-900">{{ formatDate(customer?.customer_since) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-2">
                    <span class="text-sm text-gray-600">Tenure</span>
                    <span class="text-sm font-medium text-gray-900">{{ customer?.tenure_days || 0 }} days</span>
                  </div>
                </div>
              </div>
              
              <div class="p-6 bg-white rounded-xl border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <BarChart3 class="w-5 h-5" />
                  Segmentation
                </h3>
                <div class="space-y-4">
                  <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-sm text-gray-600">CLV Tier</span>
                    <span :class="['px-3 py-1 text-sm font-medium text-white rounded-full', getTierColor(clvTier)]">
                      {{ clvTier }}
                    </span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-sm text-gray-600">RFM Segment</span>
                    <span :class="['px-3 py-1 text-sm font-medium rounded-full', getRfmColor(rfmSegment)]">
                      {{ rfmSegment }}
                    </span>
                  </div>
                  <div class="flex justify-between items-center py-2 border-b border-gray-100">
                    <span class="text-sm text-gray-600">Health Status</span>
                    <span :class="['px-3 py-1 text-sm font-medium rounded-full', getHealthBgColor(healthStatus)]">
                      {{ healthStatus }}
                    </span>
                  </div>
                  <div class="flex justify-between items-center py-2">
                    <span class="text-sm text-gray-600">Churn Risk</span>
                    <span :class="['px-3 py-1 text-sm font-medium rounded-full', getRiskColor(churnRisk)]">
                      {{ churnRisk }} ({{ churnScore.toFixed(0) }}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Purchases Section -->
          <div v-if="activeSection === 'purchases'" class="space-y-6">
            <div class="p-6 bg-white rounded-xl border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <ShoppingCart class="w-5 h-5" />
                Purchase History
              </h3>
              
              <div v-if="purchaseHistory.length > 0" class="overflow-x-auto">
                <table class="w-full text-sm">
                  <thead>
                    <tr class="border-b border-gray-200">
                      <th class="px-4 py-3 text-left text-gray-600">Invoice</th>
                      <th class="px-4 py-3 text-left text-gray-600">Date</th>
                      <th class="px-4 py-3 text-right text-gray-600">Amount</th>
                      <th class="px-4 py-3 text-right text-gray-600">Outstanding</th>
                      <th class="px-4 py-3 text-center text-gray-600">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="purchase in purchaseHistory.slice(0, 20)" 
                      :key="purchase.invoice_id"
                      class="border-b border-gray-100 hover:bg-gray-50"
                    >
                      <td class="px-4 py-3 font-medium text-blue-600">{{ purchase.invoice_id }}</td>
                      <td class="px-4 py-3 text-gray-600">{{ formatDate(purchase.posting_date) }}</td>
                      <td class="px-4 py-3 text-right font-medium">{{ formatCurrency(purchase.grand_total) }}</td>
                      <td class="px-4 py-3 text-right" :class="purchase.outstanding_amount > 0 ? 'text-red-600' : 'text-green-600'">
                        {{ formatCurrency(purchase.outstanding_amount) }}
                      </td>
                      <td class="px-4 py-3 text-center">
                        <span :class="[
                          'px-2 py-1 text-xs font-medium rounded-full',
                          purchase.payment_status === 'Paid' ? 'bg-green-100 text-green-700' :
                          purchase.payment_status === 'Overdue' ? 'bg-red-100 text-red-700' :
                          'bg-yellow-100 text-yellow-700'
                        ]">
                          {{ purchase.payment_status }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div v-else class="text-center py-12 text-gray-500">
                <ShoppingCart class="w-12 h-12 mx-auto text-gray-300" />
                <p class="mt-4">No purchase history available</p>
              </div>
            </div>
            
            <!-- Purchase Patterns -->
            <div v-if="purchasePatterns" class="p-6 bg-white rounded-xl border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <BarChart3 class="w-5 h-5" />
                Purchase Patterns
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-600">Avg Order Frequency</p>
                  <p class="text-xl font-bold text-gray-900">{{ purchasePatterns.avg_frequency || 'N/A' }}</p>
                  <p class="text-xs text-gray-500">days between orders</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-600">Preferred Day</p>
                  <p class="text-xl font-bold text-gray-900">{{ purchasePatterns.preferred_day || 'N/A' }}</p>
                  <p class="text-xs text-gray-500">most common purchase day</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-600">Peak Month</p>
                  <p class="text-xl font-bold text-gray-900">{{ purchasePatterns.peak_month || 'N/A' }}</p>
                  <p class="text-xs text-gray-500">highest spending month</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- CLV Analysis Section -->
          <div v-if="activeSection === 'clv'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="p-6 bg-white rounded-xl border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <TrendingUp class="w-5 h-5" />
                  CLV Breakdown
                </h3>
                <div class="space-y-4">
                  <div class="flex justify-between items-center py-3 border-b border-gray-100">
                    <span class="text-sm text-gray-600">Historical CLV</span>
                    <span class="text-lg font-bold text-gray-900">{{ formatCurrency(totalRevenue) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-3 border-b border-gray-100">
                    <span class="text-sm text-gray-600">Predicted 12m CLV</span>
                    <span class="text-lg font-bold text-green-600">{{ formatCurrency(predictedClv) }}</span>
                  </div>
                  <div class="flex justify-between items-center py-3 border-b border-gray-100">
                    <span class="text-sm text-gray-600">CLV Score</span>
                    <span class="text-lg font-bold text-blue-600">{{ customer?.clv_score?.toFixed(0) || 0 }}</span>
                  </div>
                  <div class="flex justify-between items-center py-3">
                    <span class="text-sm text-gray-600">CLV Tier</span>
                    <span :class="['px-3 py-1 text-sm font-medium text-white rounded-full', getTierColor(clvTier)]">
                      {{ clvTier }}
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="p-6 bg-white rounded-xl border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Target class="w-5 h-5" />
                  CLV Components
                </h3>
                <div class="space-y-4">
                  <div>
                    <div class="flex justify-between text-sm mb-1">
                      <span class="text-gray-600">Revenue Score</span>
                      <span class="font-medium">{{ customer?.revenue_score?.toFixed(0) || 0 }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-blue-600 rounded-full h-2" :style="{ width: `${customer?.revenue_score || 0}%` }"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between text-sm mb-1">
                      <span class="text-gray-600">Engagement Score</span>
                      <span class="font-medium">{{ customer?.engagement_score?.toFixed(0) || 0 }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-green-600 rounded-full h-2" :style="{ width: `${customer?.engagement_score || 0}%` }"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between text-sm mb-1">
                      <span class="text-gray-600">Longevity Score</span>
                      <span class="font-medium">{{ customer?.longevity_score?.toFixed(0) || 0 }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-purple-600 rounded-full h-2" :style="{ width: `${customer?.longevity_score || 0}%` }"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between text-sm mb-1">
                      <span class="text-gray-600">Growth Score</span>
                      <span class="font-medium">{{ customer?.growth_score?.toFixed(0) || 0 }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-orange-600 rounded-full h-2" :style="{ width: `${customer?.growth_score || 0}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Recommendations Section -->
          <div v-if="activeSection === 'recommendations'" class="space-y-6">
            <!-- Next Best Actions -->
            <div class="p-6 bg-white rounded-xl border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Zap class="w-5 h-5" />
                Next Best Actions
              </h3>
              <div v-if="nextBestActions.length > 0" class="space-y-3">
                <div 
                  v-for="action in nextBestActions" 
                  :key="action.action"
                  :class="[
                    'p-4 rounded-lg border-l-4',
                    action.priority === 'High' ? 'bg-red-50 border-red-500' :
                    action.priority === 'Medium' ? 'bg-yellow-50 border-yellow-500' :
                    'bg-blue-50 border-blue-500'
                  ]"
                >
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-sm font-bold uppercase text-gray-700">
                      {{ action.action?.replace(/_/g, ' ') }}
                    </span>
                    <span :class="[
                      'px-2 py-1 text-xs font-medium rounded',
                      action.priority === 'High' ? 'bg-red-100 text-red-700' :
                      action.priority === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-blue-100 text-blue-700'
                    ]">
                      {{ action.priority }} Priority
                    </span>
                  </div>
                  <p class="text-sm text-gray-700">{{ action.description }}</p>
                  <p class="mt-2 text-xs text-gray-500">💡 {{ action.suggestion }}</p>
                </div>
              </div>
              <div v-else class="text-center py-12 text-gray-500">
                <Zap class="w-12 h-12 mx-auto text-gray-300" />
                <p class="mt-4">No actions recommended at this time</p>
              </div>
            </div>
            
            <!-- Cross-sell Recommendations -->
            <div class="p-6 bg-white rounded-xl border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Gift class="w-5 h-5" />
                Cross-sell Recommendations
              </h3>
              <div v-if="crossSellRecommendations.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div 
                  v-for="rec in crossSellRecommendations.slice(0, 6)" 
                  :key="rec.item_code"
                  class="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
                >
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <p class="font-medium text-gray-900 truncate" :title="rec.item_name">{{ rec.item_code }}</p>
                      <p class="text-sm text-gray-500 truncate" :title="rec.item_name">{{ rec.item_name }}</p>
                    </div>
                    <span class="px-2 py-1 text-xs font-medium bg-green-100 text-green-700 rounded">
                      {{ (rec.confidence * 100).toFixed(0) }}%
                    </span>
                  </div>
                  <div class="mt-2 text-xs text-gray-500">
                    <span>Based on: {{ rec.reason || 'Purchase history' }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-12 text-gray-500">
                <Gift class="w-12 h-12 mx-auto text-gray-300" />
                <p class="mt-4">No cross-sell recommendations available</p>
              </div>
            </div>
          </div>
          
          <!-- Risk Assessment Section -->
          <div v-if="activeSection === 'risk'" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Churn Risk -->
              <div class="p-6 bg-white rounded-xl border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <AlertTriangle class="w-5 h-5" />
                  Churn Risk Assessment
                </h3>
                <div class="text-center py-6">
                  <div :class="[
                    'inline-flex items-center justify-center w-24 h-24 rounded-full text-3xl font-bold',
                    churnRisk === 'Low' ? 'bg-green-100 text-green-700' :
                    churnRisk === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                    churnRisk === 'High' ? 'bg-orange-100 text-orange-700' :
                    'bg-red-100 text-red-700'
                  ]">
                    {{ churnScore.toFixed(0) }}%
                  </div>
                  <p class="mt-4 text-lg font-semibold" :class="getHealthColor(churnRisk === 'Low' ? 'Excellent' : churnRisk === 'Medium' ? 'Healthy' : churnRisk === 'High' ? 'At Risk' : 'Critical')">
                    {{ churnRisk }} Risk
                  </p>
                </div>
                <div class="mt-4 space-y-3">
                  <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">Frequency Trend</span>
                    <span :class="[
                      'font-medium',
                      (customer?.frequency_trend || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                    ]">
                      {{ (customer?.frequency_trend || 0) >= 0 ? '↑' : '↓' }} {{ Math.abs(customer?.frequency_trend || 0).toFixed(1) }}
                    </span>
                  </div>
                  <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-600">Value Trend</span>
                    <span :class="[
                      'font-medium',
                      (customer?.value_trend || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                    ]">
                      {{ (customer?.value_trend || 0) >= 0 ? '↑' : '↓' }} {{ Math.abs(customer?.value_trend || 0).toFixed(1) }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- Health Score -->
              <div class="p-6 bg-white rounded-xl border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Heart class="w-5 h-5" />
                  Health Score
                </h3>
                <div class="text-center py-6">
                  <div :class="[
                    'inline-flex items-center justify-center w-24 h-24 rounded-full text-3xl font-bold',
                    healthStatus === 'Excellent' ? 'bg-green-100 text-green-700' :
                    healthStatus === 'Healthy' ? 'bg-blue-100 text-blue-700' :
                    healthStatus === 'At Risk' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-red-100 text-red-700'
                  ]">
                    {{ healthScore.toFixed(0) }}
                  </div>
                  <p class="mt-4 text-lg font-semibold" :class="getHealthColor(healthStatus)">
                    {{ healthStatus }}
                  </p>
                </div>
                <div class="mt-4">
                  <div class="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Health Components</span>
                    <span>Score</span>
                  </div>
                  <div class="space-y-2">
                    <div class="flex justify-between items-center">
                      <span class="text-sm">Revenue</span>
                      <div class="flex items-center gap-2">
                        <div class="w-20 bg-gray-200 rounded-full h-1.5">
                          <div class="bg-blue-600 rounded-full h-1.5" :style="{ width: `${customer?.revenue_score || 0}%` }"></div>
                        </div>
                        <span class="text-xs font-medium w-8 text-right">{{ (customer?.revenue_score || 0).toFixed(0) }}</span>
                      </div>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="text-sm">Engagement</span>
                      <div class="flex items-center gap-2">
                        <div class="w-20 bg-gray-200 rounded-full h-1.5">
                          <div class="bg-green-600 rounded-full h-1.5" :style="{ width: `${customer?.engagement_score || 0}%` }"></div>
                        </div>
                        <span class="text-xs font-medium w-8 text-right">{{ (customer?.engagement_score || 0).toFixed(0) }}</span>
                      </div>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="text-sm">Payment</span>
                      <div class="flex items-center gap-2">
                        <div class="w-20 bg-gray-200 rounded-full h-1.5">
                          <div class="bg-purple-600 rounded-full h-1.5" :style="{ width: `${customer?.payment_score || 0}%` }"></div>
                        </div>
                        <span class="text-xs font-medium w-8 text-right">{{ (customer?.payment_score || 0).toFixed(0) }}</span>
                      </div>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="text-sm">Longevity</span>
                      <div class="flex items-center gap-2">
                        <div class="w-20 bg-gray-200 rounded-full h-1.5">
                          <div class="bg-orange-600 rounded-full h-1.5" :style="{ width: `${customer?.longevity_score || 0}%` }"></div>
                        </div>
                        <span class="text-xs font-medium w-8 text-right">{{ (customer?.longevity_score || 0).toFixed(0) }}</span>
                      </div>
                    </div>
                    <div class="flex justify-between items-center">
                      <span class="text-sm">Growth</span>
                      <div class="flex items-center gap-2">
                        <div class="w-20 bg-gray-200 rounded-full h-1.5">
                          <div class="bg-cyan-600 rounded-full h-1.5" :style="{ width: `${customer?.growth_score || 0}%` }"></div>
                        </div>
                        <span class="text-xs font-medium w-8 text-right">{{ (customer?.growth_score || 0).toFixed(0) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Payment Behavior -->
            <div class="p-6 bg-white rounded-xl border border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <CreditCard class="w-5 h-5" />
                Payment Behavior
              </h3>
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-600">Avg Days to Pay</p>
                  <p class="text-2xl font-bold text-gray-900">{{ customer?.avg_days_to_pay?.toFixed(0) || 'N/A' }}</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-600">Outstanding Amount</p>
                  <p class="text-2xl font-bold" :class="(customer?.outstanding_amount || 0) > 0 ? 'text-red-600' : 'text-green-600'">
                    {{ formatCurrency(customer?.outstanding_amount || 0) }}
                  </p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-600">Payment Score</p>
                  <p class="text-2xl font-bold text-gray-900">{{ customer?.payment_score?.toFixed(0) || 0 }}%</p>
                </div>
                <div class="p-4 bg-gray-50 rounded-lg">
                  <p class="text-sm text-gray-600">Overdue Invoices</p>
                  <p class="text-2xl font-bold" :class="(customer?.overdue_count || 0) > 0 ? 'text-red-600' : 'text-green-600'">
                    {{ customer?.overdue_count || 0 }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
    
    <!-- AI Chat Button -->
    <DashboardChatButton
      dashboard-type="Customer 360"
      :dashboard-context="chatContext"
    />
  </div>
</template>

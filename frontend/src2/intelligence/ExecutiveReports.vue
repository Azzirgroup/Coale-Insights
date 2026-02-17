<template>
  <div class="executive-reports p-4">
    <!-- Header Section -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Executive Reports</h1>
        <p class="text-gray-600 mt-1">Automated business intelligence reports for C-suite management</p>
      </div>
      <div class="flex gap-3">
        <Button 
          variant="outline" 
          @click="fetchReportsStatus"
          :loading="loadingStatus"
        >
          <RefreshCw class="w-4 h-4 mr-2" />
          Refresh
        </Button>
        <Button 
          variant="solid" 
          @click="generateReportModal = true"
        >
          <Plus class="w-4 h-4 mr-2" />
          Generate Report
        </Button>
      </div>
    </div>

    <!-- Status Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-medium text-gray-700">Daily Reports</h3>
            <p class="text-2xl font-bold text-blue-600">{{ reportsStatus.daily_count || 0 }}</p>
            <p class="text-sm text-gray-500">Last: {{ reportsStatus.last_daily || 'N/A' }}</p>
          </div>
          <Calendar class="w-8 h-8 text-blue-500" />
        </div>
      </Card>
      
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-medium text-gray-700">Weekly Reports</h3>
            <p class="text-2xl font-bold text-green-600">{{ reportsStatus.weekly_count || 0 }}</p>
            <p class="text-sm text-gray-500">Last: {{ reportsStatus.last_weekly || 'N/A' }}</p>
          </div>
          <TrendingUp class="w-8 h-8 text-green-500" />
        </div>
      </Card>
      
      <Card class="p-4">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-medium text-gray-700">Monthly Reports</h3>
            <p class="text-2xl font-bold text-purple-600">{{ reportsStatus.monthly_count || 0 }}</p>
            <p class="text-sm text-gray-500">Last: {{ reportsStatus.last_monthly || 'N/A' }}</p>
          </div>
          <BarChart3 class="w-8 h-8 text-purple-500" />
        </div>
      </Card>
    </div>

    <!-- Scheduling Status -->
    <Card class="mb-6">
      <div class="p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900 flex items-center">
          <Clock class="w-5 h-5 mr-2" />
          Automated Scheduling Status
        </h3>
      </div>
      <div class="p-4">
        <div v-if="schedulingStatus" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <div>
              <p class="font-medium text-blue-900">Daily Reports</p>
              <p class="text-sm text-blue-700">{{ schedulingStatus.daily_reports || 'Not scheduled' }}</p>
            </div>
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div>
              <p class="font-medium text-green-900">Weekly Reports</p>
              <p class="text-sm text-green-700">{{ schedulingStatus.weekly_reports || 'Not scheduled' }}</p>
            </div>
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <div class="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
            <div>
              <p class="font-medium text-purple-900">Monthly Reports</p>
              <p class="text-sm text-purple-700">{{ schedulingStatus.monthly_reports || 'Not scheduled' }}</p>
            </div>
            <div class="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
        </div>
        <div v-else class="text-center text-gray-500">
          <Loader class="w-5 h-5 animate-spin mx-auto mb-2" />
          Loading scheduling status...
        </div>
      </div>
    </Card>

    <!-- Recent Reports Table -->
    <Card>
      <div class="p-4 border-b">
        <h3 class="text-lg font-medium text-gray-900 flex items-center">
          <FileText class="w-5 h-5 mr-2" />
          Recent Reports
        </h3>
      </div>
      <div class="p-0">
        <div v-if="loadingReports" class="text-center py-8">
          <Loader class="w-6 h-6 animate-spin mx-auto mb-2" />
          <p class="text-gray-500">Loading reports...</p>
        </div>
        <div v-else-if="recentReports.length === 0" class="text-center py-8">
          <FileX class="w-12 h-12 mx-auto text-gray-300 mb-4" />
          <p class="text-gray-500">No reports generated yet</p>
          <p class="text-sm text-gray-400">Generate your first executive report to get started</p>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report Type</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Generated</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="report in recentReports" :key="report.id" class="hover:bg-gray-50">
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <div :class="getReportTypeIconClass(report.report_type)">
                      <component :is="getReportTypeIcon(report.report_type)" class="w-4 h-4" />
                    </div>
                    <span class="ml-2 font-medium text-gray-900 capitalize">{{ report.report_type }}</span>
                  </div>
                </td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ formatReportDate(report.report_date) }}</td>
                <td class="px-4 py-3 text-sm text-gray-600">{{ formatDateTime(report.created) }}</td>
                <td class="px-4 py-3">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    <div class="w-1.5 h-1.5 bg-green-500 rounded-full mr-1"></div>
                    Generated
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="flex items-center space-x-2">
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      @click="previewReport(report)"
                      :loading="loadingPreview === report.id"
                    >
                      <Eye class="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      @click="downloadReport(report)"
                      :loading="loadingDownload === report.id"
                    >
                      <Download class="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      @click="sendReportEmail(report)"
                      :loading="loadingSend === report.id"
                    >
                      <Mail class="w-4 h-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Card>

    <!-- Generate Report Modal -->
    <Dialog
      v-model="generateReportModal"
      :options="{
        title: 'Generate Executive Report',
        actions: [
          { label: 'Cancel', variant: 'outline', onClick: () => generateReportModal = false },
          { label: generatingReport ? 'Generating...' : 'Generate Report', variant: 'solid', loading: generatingReport, disabled: generatingReport, onClick: generateReport }
        ]
      }"
    >
      <template #body-content>
        <p class="text-sm text-gray-500 mb-4">Select the type of executive report to generate</p>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
            <select 
              v-model="selectedReportType" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="daily">Daily Executive Summary</option>
              <option value="weekly">Weekly Business Review</option>
              <option value="monthly">Monthly Board Report</option>
            </select>
          </div>
          
          <div class="flex items-center space-x-2">
            <input 
              id="send-email" 
              v-model="sendEmailAfterGeneration" 
              type="checkbox"
              class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            >
            <label for="send-email" class="text-sm text-gray-700">Send email after generation</label>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Preview Modal -->
    <Dialog
      v-model="previewModal"
      :options="{
        title: 'Report Preview',
        size: 'xl',
        actions: [
          { label: 'Close', variant: 'outline', onClick: () => previewModal = false }
        ]
      }"
    >
      <template #body-content>
        <p class="text-sm text-gray-500 mb-4">Preview of {{ selectedReport?.report_type }} report data</p>
        <div v-if="previewData" class="space-y-4 max-h-96 overflow-y-auto">
          <div class="bg-blue-50 p-4 rounded-lg">
            <h4 class="font-medium text-blue-900 mb-2">Executive Summary</h4>
            <p class="text-blue-800">{{ previewData.executive_summary }}</p>
          </div>
          
          <div v-if="previewData.key_metrics" class="bg-gray-50 p-4 rounded-lg">
            <h4 class="font-medium text-gray-900 mb-3">Key Metrics</h4>
            <div class="grid grid-cols-2 gap-3">
              <div v-for="(value, key) in previewData.key_metrics" :key="key" class="bg-white p-2 rounded border">
                <p class="text-sm text-gray-600">{{ formatMetricKey(key) }}</p>
                <p class="font-semibold">{{ formatMetricValue(value) }}</p>
              </div>
            </div>
          </div>
          
          <div v-if="previewData.alerts && previewData.alerts.length > 0" class="bg-red-50 p-4 rounded-lg">
            <h4 class="font-medium text-red-900 mb-3">Alerts & Exceptions</h4>
            <div v-for="alert in previewData.alerts" :key="alert.type" class="bg-red-100 p-2 rounded mb-2">
              <p class="font-medium text-red-800">{{ alert.type }} ({{ alert.priority }})</p>
              <p class="text-red-700 text-sm">{{ alert.message }}</p>
            </div>
          </div>
          
          <div class="bg-green-50 p-4 rounded-lg">
            <h4 class="font-medium text-green-900 mb-2">Data Availability</h4>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="module in previewData.modules_with_data" 
                :key="module"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
              >
                {{ module }}
              </span>
            </div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  Calendar, TrendingUp, BarChart3, Clock, RefreshCw, Plus, FileText, 
  Eye, Download, Mail, FileX, Loader 
} from 'lucide-vue-next'
import { Button, Card, Dialog } from 'frappe-ui'
import { apiCall } from '../helpers/api'

// Reactive data
const recentReports = ref([])
const reportsStatus = ref({})
const schedulingStatus = ref(null)
const loadingReports = ref(false)
const loadingStatus = ref(false)
const loadingPreview = ref(null)
const loadingDownload = ref(null)
const loadingSend = ref(null)

// Modal states
const generateReportModal = ref(false)
const previewModal = ref(false)
const selectedReportType = ref('daily')
const sendEmailAfterGeneration = ref(true)
const generatingReport = ref(false)

// Preview data
const selectedReport = ref(null)
const previewData = ref(null)

// Methods
const fetchRecentReports = async () => {
  loadingReports.value = true
  try {
    const result = await apiCall('insights.api.ml.get_recent_executive_reports', { limit: 20 })
    recentReports.value = result?.reports || []
    updateReportsStatus()
  } catch (error) {
    console.error('Error fetching recent reports:', error)
  } finally {
    loadingReports.value = false
  }
}

const fetchReportsStatus = async () => {
  loadingStatus.value = true
  try {
    schedulingStatus.value = await apiCall('insights.api.ml.get_executive_reports_status')
  } catch (error) {
    console.error('Error fetching reports status:', error)
  } finally {
    loadingStatus.value = false
  }
}

const updateReportsStatus = () => {
  // Calculate status from recent reports
  const dailyReports = recentReports.value.filter(r => r.report_type === 'daily')
  const weeklyReports = recentReports.value.filter(r => r.report_type === 'weekly')
  const monthlyReports = recentReports.value.filter(r => r.report_type === 'monthly')
  
  reportsStatus.value = {
    daily_count: dailyReports.length,
    weekly_count: weeklyReports.length,
    monthly_count: monthlyReports.length,
    last_daily: dailyReports.length > 0 ? dailyReports[0].report_date : null,
    last_weekly: weeklyReports.length > 0 ? weeklyReports[0].report_date : null,
    last_monthly: monthlyReports.length > 0 ? monthlyReports[0].report_date : null
  }
}

const generateReport = async () => {
  generatingReport.value = true
  try {
    await apiCall('insights.api.ml.generate_executive_report', {
      report_type: selectedReportType.value
    })

    // Optionally send email
    if (sendEmailAfterGeneration.value) {
      await apiCall('insights.api.ml.send_executive_report', {
        report_type: selectedReportType.value
      })
    }

    // Refresh reports list
    await fetchRecentReports()
    generateReportModal.value = false

    // Show success notification
    window.frappe.show_alert({
      message: `${selectedReportType.value.charAt(0).toUpperCase() + selectedReportType.value.slice(1)} executive report generated successfully!`,
      indicator: 'green'
    })
  } catch (error) {
    console.error('Error generating report:', error)
    window.frappe.show_alert({
      message: 'Error generating report. Please try again.',
      indicator: 'red'
    })
  } finally {
    generatingReport.value = false
  }
}

const previewReport = async (report) => {
  loadingPreview.value = report.id
  try {
    const result = await apiCall('insights.api.ml.preview_executive_report_data', {
      report_type: report.report_type
    })

    selectedReport.value = report
    previewData.value = result
    previewModal.value = true
  } catch (error) {
    console.error('Error previewing report:', error)
  } finally {
    loadingPreview.value = null
  }
}

const downloadReport = async (report) => {
  loadingDownload.value = report.id
  try {
    const result = await apiCall('insights.api.ml.download_executive_report', {
      report_id: report.id
    })

    // Open download URL
    window.open(result.download_url, '_blank')
  } catch (error) {
    console.error('Error downloading report:', error)
  } finally {
    loadingDownload.value = null
  }
}

const sendReportEmail = async (report) => {
  loadingSend.value = report.id
  try {
    await apiCall('insights.api.ml.send_executive_report', {
      report_type: report.report_type
    })

    window.frappe.show_alert({
      message: 'Report sent successfully!',
      indicator: 'green'
    })
  } catch (error) {
    console.error('Error sending report:', error)
  } finally {
    loadingSend.value = null
  }
}

// Utility functions
const getReportTypeIcon = (type) => {
  switch (type) {
    case 'daily': return Calendar
    case 'weekly': return TrendingUp  
    case 'monthly': return BarChart3
    default: return FileText
  }
}

const getReportTypeIconClass = (type) => {
  switch (type) {
    case 'daily': return 'flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-600 rounded-full'
    case 'weekly': return 'flex items-center justify-center w-8 h-8 bg-green-100 text-green-600 rounded-full'
    case 'monthly': return 'flex items-center justify-center w-8 h-8 bg-purple-100 text-purple-600 rounded-full'
    default: return 'flex items-center justify-center w-8 h-8 bg-gray-100 text-gray-600 rounded-full'
  }
}

const formatReportDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString()
}

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return 'N/A'
  return new Date(dateTimeStr).toLocaleString()
}

const formatMetricKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatMetricValue = (value) => {
  if (typeof value === 'number') {
    if (value > 1000000) {
      return '$' + (value / 1000000).toFixed(1) + 'M'
    } else if (value > 1000) {
      return '$' + (value / 1000).toFixed(1) + 'K'
    } else if (value % 1 === 0) {
      return value.toString()
    } else {
      return value.toFixed(2)
    }
  }
  return value
}

// Lifecycle
onMounted(() => {
  fetchRecentReports()
  fetchReportsStatus()
})
</script>

<style scoped>
.executive-reports {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
<template>
  <div class="flex flex-1 flex-col overflow-hidden bg-white">
    <!-- Header -->
    <div class="border-b border-gray-200 px-6 py-4">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-semibold text-gray-900">AI-Powered Insights</h1>
          <p class="text-sm text-gray-600 mt-1">
            Ask natural language questions about your business data
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <div class="flex items-center space-x-1 text-sm text-gray-500">
            <div class="w-2 h-2 rounded-full bg-green-500"></div>
            <span>AI Online</span>
          </div>
          <button
            @click="showModelStatus = true"
            class="text-gray-400 hover:text-gray-600"
            v-if="isAdmin"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Chat Interface -->
      <div class="flex-1 flex flex-col">
        <!-- Chat Messages -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4" ref="chatContainer">
          <div v-if="messages.length === 0" class="text-center py-12">
            <div class="text-gray-400 mb-4">
              <svg class="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Welcome to AI Insights</h3>
            <p class="text-gray-600 mb-4">Ask questions about your business data in natural language</p>
            <div class="flex flex-wrap justify-center gap-2">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion"
                @click="askQuestion(suggestion)"
                class="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>

          <div
            v-for="(message, index) in messages"
            :key="index"
            class="flex"
            :class="message.type === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-3xl px-4 py-2 rounded-lg"
              :class="message.type === 'user' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 text-gray-900'"
            >
              <div v-if="message.type === 'ai'" class="prose max-w-none">
                <div v-html="formatResponse(message.content)"></div>
                <div v-if="message.metadata" class="text-xs text-gray-500 mt-2 border-t pt-2">
                  Model: {{ message.metadata.model_used }} | 
                  Time: {{ message.metadata.processing_time }}s |
                  {{ message.metadata.cached ? 'Cached' : 'Fresh' }}
                </div>
              </div>
              <div v-else>{{ message.content }}</div>
            </div>
          </div>

          <div v-if="isLoading" class="flex justify-start">
            <div class="max-w-3xl px-4 py-2 bg-gray-100 rounded-lg">
              <div class="flex items-center space-x-2">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                <span class="text-gray-600">AI is thinking...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="border-t border-gray-200 p-4">
          <div class="flex space-x-4">
            <div class="flex-1">
              <textarea
                v-model="currentQuestion"
                @keydown.enter.prevent="handleEnter"
                placeholder="Ask a question about your business data..."
                class="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows="2"
              ></textarea>
            </div>
            <div class="flex flex-col space-y-2">
              <button
                @click="askQuestion(currentQuestion)"
                :disabled="!currentQuestion.trim() || isLoading"
                class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
              <select
                v-model="selectedComplexity"
                class="px-3 py-2 border border-gray-300 rounded-md text-sm"
              >
                <option value="simple">Simple</option>
                <option value="medium">Medium</option>
                <option value="complex">Complex</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- Business Intelligence Sidebar -->
      <div class="w-80 border-l border-gray-200 bg-gray-50 p-4 overflow-y-auto">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Quick Insights</h3>
        
        <div class="space-y-4">
          <div
            v-for="module in erpNextModules"
            :key="module.name"
            class="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-md transition-shadow cursor-pointer"
            @click="getBIInsights(module.name)"
          >
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-medium text-gray-900">{{ module.title }}</h4>
                <p class="text-sm text-gray-600">{{ module.description }}</p>
              </div>
              <div class="text-2xl">{{ module.icon }}</div>
            </div>
          </div>
        </div>

        <!-- Recent Insights -->
        <div class="mt-6">
          <h4 class="text-md font-medium text-gray-900 mb-3">Recent Insights</h4>
          <div class="space-y-2">
            <div
              v-for="insight in recentInsights"
              :key="insight.id"
              class="p-3 bg-white rounded border text-sm"
            >
              <p class="text-gray-900 font-medium">{{ insight.title }}</p>
              <p class="text-gray-600 text-xs">{{ insight.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Model Status Modal -->
    <div v-if="showModelStatus" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium">AI Model Status</h3>
          <button @click="showModelStatus = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" />
            </svg>
          </button>
        </div>
        <div v-if="modelStatus" class="space-y-4">
          <div v-for="model in modelStatus.models" :key="model.name" class="border rounded p-4">
            <div class="flex justify-between items-center mb-2">
              <span class="font-medium">{{ model.name }}</span>
              <span class="text-sm text-gray-600">{{ model.quota_used }}% used</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div 
                class="bg-blue-500 h-2 rounded-full transition-all"
                :style="`width: ${model.quota_used}%`"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { call } from 'frappe-ui'

export default {
  name: 'AIInsights',
  data() {
    return {
      messages: [],
      currentQuestion: '',
      selectedComplexity: 'simple',
      isLoading: false,
      showModelStatus: false,
      modelStatus: null,
      isAdmin: false,
      suggestions: [
        'What were our top selling items last month?',
        'Show me customer payment trends',
        'Which suppliers have the best performance?',
        'What is our inventory turnover rate?',
        'How is our cash flow looking?'
      ],
      erpNextModules: [
        {
          name: 'accounts',
          title: 'Financial Analytics',
          description: 'Revenue, expenses, cash flow',
          icon: '💰'
        },
        {
          name: 'selling',
          title: 'Sales Intelligence',
          description: 'Customer trends, sales performance',
          icon: '📈'
        },
        {
          name: 'buying',
          title: 'Procurement Analytics',
          description: 'Supplier performance, costs',
          icon: '🛒'
        },
        {
          name: 'stock',
          title: 'Inventory Insights',
          description: 'Stock levels, turnover rates',
          icon: '📦'
        },
        {
          name: 'manufacturing',
          title: 'Production Analytics',
          description: 'Efficiency, resource planning',
          icon: '🏭'
        },
        {
          name: 'crm',
          title: 'Customer Intelligence',
          description: 'Lead conversion, customer journey',
          icon: '👥'
        }
      ],
      recentInsights: []
    }
  },
  mounted() {
    this.checkUserPermissions()
    this.loadRecentInsights()
  },
  methods: {
    async checkUserPermissions() {
      // Check if user is admin
      this.isAdmin = window.frappe && window.frappe.user_roles && window.frappe.user_roles.includes('System Manager')
    },
    
    async askQuestion(question) {
      if (!question || !question.trim()) return
      
      // Add user message
      this.messages.push({
        type: 'user',
        content: question,
        timestamp: new Date()
      })
      
      this.currentQuestion = ''
      this.isLoading = true
      
      try {
        const response = await call('insights.api.ai_insights.get_ai_insights', {
          query: question,
          complexity: this.selectedComplexity
        })
        
        if (response.success) {
          this.messages.push({
            type: 'ai',
            content: response.response.content || 'I received your question but couldn\'t generate a response.',
            metadata: {
              model_used: response.model_used,
              processing_time: response.processing_time,
              cached: response.cached,
              tokens_used: response.tokens_used
            },
            timestamp: new Date()
          })
        } else {
          this.messages.push({
            type: 'ai',
            content: `Sorry, I encountered an error: ${response.error}`,
            timestamp: new Date()
          })
        }
      } catch (error) {
        this.messages.push({
          type: 'ai',
          content: 'Sorry, I\'m having trouble connecting to the AI service. Please try again.',
          timestamp: new Date()
        })
      }
      
      this.isLoading = false
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    
    async getBIInsights(module) {
      this.isLoading = true
      
      try {
        const response = await call('insights.api.ai_insights.get_business_intelligence_insights', {
          module: module
        })
        
        if (response.success) {
          const insightText = this.formatBIInsights(response.insights, module)
          this.messages.push({
            type: 'ai',
            content: insightText,
            metadata: {
              module: module,
              data_points: response.data_points
            },
            timestamp: new Date()
          })
        }
      } catch (error) {
        console.error('BI Insights Error:', error)
      }
      
      this.isLoading = false
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    
    formatBIInsights(insights, module) {
      return `Here are the latest insights for ${module}:\n\n${JSON.stringify(insights, null, 2)}`
    },
    
    formatResponse(content) {
      // Basic markdown-like formatting
      return content.replace(/\n/g, '<br>')
    },
    
    handleEnter(event) {
      if (!event.shiftKey) {
        this.askQuestion(this.currentQuestion)
      }
    },
    
    scrollToBottom() {
      const container = this.$refs.chatContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    async loadRecentInsights() {
      // Load recent insights from storage or API
      this.recentInsights = []
    },
    
    async loadModelStatus() {
      if (!this.isAdmin) return
      
      try {
        const response = await call('insights.api.ai_insights.get_ai_model_status')
        if (response.success) {
          this.modelStatus = response.status
        }
      } catch (error) {
        console.error('Model Status Error:', error)
      }
    }
  },
  
  watch: {
    showModelStatus(newVal) {
      if (newVal) {
        this.loadModelStatus()
      }
    }
  }
}
</script>

<style scoped>
.ai-insights-page {
  background: #f8fafc;
}

.prose {
  max-width: none;
}

.prose p {
  margin-bottom: 0.5rem;
}
</style>
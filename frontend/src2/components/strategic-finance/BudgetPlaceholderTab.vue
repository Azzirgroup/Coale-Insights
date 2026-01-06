<template>
  <div class="flex flex-col items-center justify-center py-20">
    <div class="text-center max-w-lg">
      <!-- Placeholder Icon -->
      <div class="mx-auto mb-6 w-24 h-24 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
        <PiggyBank class="h-12 w-12 text-gray-400" />
      </div>

      <!-- Title -->
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
        Budget vs Actual Analysis
      </h3>

      <!-- Description -->
      <p class="text-gray-500 dark:text-gray-400 mb-6">
        This feature will allow you to compare actual financial performance against budgeted targets, 
        track variances, and identify areas that need attention.
      </p>

      <!-- Coming Soon Badge -->
      <div class="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 dark:bg-blue-900/20 rounded-full">
        <Clock class="h-4 w-4 text-blue-600" />
        <span class="text-sm font-medium text-blue-700 dark:text-blue-400">Coming Soon</span>
      </div>

      <!-- Features Preview -->
      <div class="mt-8 text-left bg-gray-50 dark:bg-gray-800 rounded-xl p-6">
        <h4 class="font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Sparkles class="h-5 w-5 text-amber-500" />
          Planned Features
        </h4>
        <ul class="space-y-3">
          <li class="flex items-start gap-3">
            <CheckCircle class="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Budget creation and management by department/account
            </span>
          </li>
          <li class="flex items-start gap-3">
            <CheckCircle class="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Real-time variance tracking with threshold alerts
            </span>
          </li>
          <li class="flex items-start gap-3">
            <CheckCircle class="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Rolling forecast updates and re-budgeting tools
            </span>
          </li>
          <li class="flex items-start gap-3">
            <CheckCircle class="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Cost center and project-level budget tracking
            </span>
          </li>
          <li class="flex items-start gap-3">
            <CheckCircle class="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Year-to-date and full-year projection views
            </span>
          </li>
        </ul>
      </div>

      <!-- Setup Hint -->
      <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
        <div class="flex items-start gap-3">
          <AlertTriangle class="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div class="text-left">
            <p class="text-sm font-medium text-amber-700 dark:text-amber-400">
              No Budget Data Available
            </p>
            <p class="text-sm text-amber-600 dark:text-amber-500 mt-1">
              To use this feature, you'll need to set up budgets in ERPNext under 
              Accounting → Budget. Once budget data is available, this tab will 
              automatically display budget vs actual comparisons.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  PiggyBank, 
  Clock, 
  Sparkles, 
  CheckCircle, 
  AlertTriangle 
} from 'lucide-vue-next'
</script>

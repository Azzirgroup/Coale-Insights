<template>
  <div class="flex flex-col h-full bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b px-6 py-4 flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">Tax Intelligence</h1>
        <p class="text-sm text-gray-500 mt-1">
          Kenya Corporate Tax analytics, compliance monitoring, and optimization insights
        </p>
      </div>
      <div class="flex items-center gap-3">
        <span v-if="lastUpdated" class="text-sm text-gray-500">
          Updated: {{ formatDate(lastUpdated) }}
        </span>
        <Button
          variant="solid"
          @click="refreshData"
          :loading="loading"
          icon-left="refresh-cw"
        >
          Refresh Analysis
        </Button>
      </div>
    </header>

    <!-- Summary Cards -->
    <div class="p-6 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 border">
        <div class="text-sm font-medium text-gray-500">Taxable Income</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">
          {{ formatCurrency(taxOverview.taxable_income) }}
        </div>
        <div class="text-sm text-gray-500 mt-1">KES</div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-4 border">
        <div class="text-sm font-medium text-gray-500">Tax Liability</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">
          {{ formatCurrency(taxOverview.tax_liability) }}
        </div>
        <div class="text-sm text-gray-500 mt-1">30% corporate rate</div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-4 border">
        <div class="text-sm font-medium text-gray-500">Effective Rate</div>
        <div class="text-2xl font-bold mt-1" :class="getEffectiveRateColor(taxOverview.effective_tax_rate)">
          {{ taxOverview.effective_tax_rate }}%
        </div>
        <div class="text-sm mt-1" :class="getEffectiveRateColor(taxOverview.effective_tax_rate)">
          {{ getEffectiveRateLabel(taxOverview.effective_tax_rate) }}
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-4 border">
        <div class="text-sm font-medium text-gray-500">Instalments Paid</div>
        <div class="text-2xl font-bold text-gray-900 mt-1">
          {{ formatCurrency(taxOverview.instalments_paid) }}
        </div>
        <div class="text-sm text-gray-500 mt-1">KRA quarterly</div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-4 border">
        <div class="text-sm font-medium text-gray-500">Net Tax Position</div>
        <div class="text-2xl font-bold mt-1" :class="getPositionColor(taxOverview.net_tax_position)">
          {{ formatCurrency(taxOverview.net_tax_position) }}
        </div>
        <div class="text-sm mt-1" :class="getPositionColor(taxOverview.net_tax_position)">
          {{ getPositionLabel(taxOverview.net_tax_position) }}
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-4 border">
        <div class="text-sm font-medium text-gray-500">Capital Allowances</div>
        <div class="text-2xl font-bold text-green-600 mt-1">
          {{ formatCurrency(capitalAllowances.total_allowances) }}
        </div>
        <div class="text-sm text-gray-500 mt-1">Tax relief</div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="bg-white border-b mx-6 rounded-t-lg">
      <div class="flex overflow-x-auto">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            'px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 -mb-px',
            activeTab === tab.value
              ? 'text-blue-600 border-blue-600'
              : 'text-gray-500 border-transparent hover:text-gray-700'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="flex-1 p-6 overflow-auto">
      <!-- Tab 1: Overview -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Tax Computation Summary -->
          <div class="bg-white rounded-lg shadow-sm p-6 border">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Tax Computation Summary</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Total Revenue</span>
                <span class="text-sm font-medium text-gray-900">{{ formatCurrency(taxOverview.total_revenue) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Total Expenses</span>
                <span class="text-sm font-medium text-gray-900">{{ formatCurrency(taxOverview.total_expenses) }}</span>
              </div>
              <div class="flex justify-between items-center border-t pt-2">
                <span class="text-sm font-medium text-gray-900">Gross Profit</span>
                <span class="text-sm font-medium text-gray-900">{{ formatCurrency(taxOverview.gross_profit) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Add Back (Non-Allowable)</span>
                <span class="text-sm font-medium text-red-600">+{{ formatCurrency(taxOverview.add_backs) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Less: Capital Allowances</span>
                <span class="text-sm font-medium text-green-600">-{{ formatCurrency(taxOverview.capital_allowances) }}</span>
              </div>
              <div class="flex justify-between items-center border-t pt-2">
                <span class="text-sm font-medium text-gray-900">Taxable Income</span>
                <span class="text-sm font-bold text-gray-900">{{ formatCurrency(taxOverview.taxable_income) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600">Corporate Tax (30%)</span>
                <span class="text-sm font-medium text-red-600">{{ formatCurrency(taxOverview.tax_liability) }}</span>
              </div>
            </div>
          </div>

          <!-- Expense Classification -->
          <div class="bg-white rounded-lg shadow-sm p-6 border">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Expense Classification</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span class="text-sm text-gray-600">Allowable Expenses</span>
                </div>
                <span class="text-sm font-medium text-gray-900">{{ formatCurrency(expenseAnalysis.total_allowable) }}</span>
              </div>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span class="text-sm text-gray-600">Non-Allowable Expenses</span>
                </div>
                <span class="text-sm font-medium text-gray-900">{{ formatCurrency(expenseAnalysis.total_non_allowable) }}</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-green-500 h-2 rounded-full"
                  :style="{ width: `${getExpenseRatio()}%` }"
                ></div>
              </div>
              <div class="text-xs text-gray-500 text-center">
                {{ getExpenseRatio().toFixed(1) }}% allowable
              </div>
            </div>

            <!-- Non-Allowable Details -->
            <div v-if="expenseAnalysis.non_allowable_expenses?.length" class="mt-4 pt-4 border-t">
              <h4 class="text-sm font-medium text-gray-900 mb-2">Non-Allowable Expenses</h4>
              <div class="space-y-2">
                <div v-for="exp in expenseAnalysis.non_allowable_expenses.slice(0, 3)" :key="exp.account_name"
                     class="flex justify-between items-center text-xs">
                  <span class="text-gray-600 truncate w-32">{{ exp.account_name }}</span>
                  <span class="text-red-600 font-medium">{{ formatCurrency(exp.amount) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- KRA Compliance Status -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">KRA Instalment Status</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div v-for="inst in kraSchedule.instalments" :key="inst.quarter"
                 class="p-4 rounded-lg border" :class="getInstalmentBgColor(inst.status)">
              <div class="text-sm font-medium text-gray-900">{{ inst.label }}</div>
              <div class="text-lg font-bold mt-1" :class="getInstalmentTextColor(inst.status)">
                {{ formatCurrency(inst.amount_paid) }} / {{ formatCurrency(inst.amount_due) }}
              </div>
              <div class="text-xs mt-1" :class="getInstalmentTextColor(inst.status)">
                {{ inst.status }} • Due {{ inst.due_date_formatted }}
              </div>
              <div v-if="inst.balance > 0" class="text-xs mt-1 text-red-600">
                Balance: {{ formatCurrency(inst.balance) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: Income & Expenses -->
      <div v-if="activeTab === 'income'" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Income by Account -->
          <div class="bg-white rounded-lg shadow-sm p-6 border">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Income by Account</h3>
            <div class="space-y-3">
              <div v-for="inc in (incomeAnalysis.by_account || []).slice(0, 10)" :key="inc.account_name"
                   class="flex items-center justify-between">
                <div class="flex items-center gap-3 flex-1">
                  <span class="text-sm font-medium text-gray-700 truncate w-32">{{ inc.account_name }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                    <div
                      class="bg-blue-500 h-full rounded-full"
                      :style="{ width: `${getIncomePct(inc.amount)}%` }"
                    ></div>
                  </div>
                </div>
                <span class="text-sm text-gray-600 w-24 text-right">{{ formatCurrency(inc.amount) }}</span>
              </div>
            </div>
          </div>

          <!-- Monthly Income Trend -->
          <div class="bg-white rounded-lg shadow-sm p-6 border">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Monthly Income Trend</h3>
            <div v-if="incomeAnalysis.monthly_trend?.length" class="h-64">
              <div class="space-y-2">
                <div v-for="month in incomeAnalysis.monthly_trend.slice(-12)" :key="month.period"
                     class="flex items-center gap-3">
                  <span class="text-sm text-gray-600 w-20">{{ formatPeriod(month.period) }}</span>
                  <div class="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
                    <div
                      class="bg-blue-500 h-full rounded-full flex items-center justify-end pr-2"
                      :style="{ width: `${getIncomeBarWidth(month.amount)}%` }"
                    >
                      <span class="text-xs text-white font-medium">{{ formatCurrency(month.amount) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="h-64 flex items-center justify-center text-gray-500">
              No income data available
            </div>
          </div>
        </div>

        <!-- Expenses by Account -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Expenses by Account</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Account</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Classification</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="exp in (expenseAnalysis.allowable_expenses || []).slice(0, 20)" :key="exp.account_name">
                  <td class="px-4 py-3">
                    <div class="font-medium text-gray-900">{{ exp.account_name }}</div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ exp.account_type }}</td>
                  <td class="px-4 py-3 text-right text-sm font-medium text-gray-900">
                    {{ formatCurrency(exp.amount) }}
                  </td>
                  <td class="px-4 py-3">
                    <span class="px-2 py-1 rounded text-xs bg-green-100 text-green-700">Allowable</span>
                  </td>
                </tr>
                <tr v-for="exp in (expenseAnalysis.non_allowable_expenses || []).slice(0, 10)" :key="exp.account_name">
                  <td class="px-4 py-3">
                    <div class="font-medium text-gray-900">{{ exp.account_name }}</div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ exp.account_type }}</td>
                  <td class="px-4 py-3 text-right text-sm font-medium text-gray-900">
                    {{ formatCurrency(exp.amount) }}
                  </td>
                  <td class="px-4 py-3">
                    <span class="px-2 py-1 rounded text-xs bg-red-100 text-red-700">Non-Allowable</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab 3: Capital Allowances -->
      <div v-if="activeTab === 'capital'" class="space-y-6">
        <!-- Summary -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Total Allowances</div>
            <div class="text-xl font-bold text-green-600">{{ formatCurrency(capitalAllowances.total_allowances) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Wear & Tear</div>
            <div class="text-xl font-bold text-blue-600">{{ formatCurrency(capitalAllowances.total_wear_tear) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Investment Deduction</div>
            <div class="text-xl font-bold text-purple-600">{{ formatCurrency(capitalAllowances.total_investment_deduction) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Assets Count</div>
            <div class="text-xl font-bold text-gray-900">{{ capitalAllowances.asset_count }}</div>
          </div>
        </div>

        <!-- Allowances by Category -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Capital Allowances by Category</h3>
          <div class="space-y-4">
            <div v-for="cat in capitalAllowances.by_category" :key="cat.category"
                 class="p-4 bg-gray-50 rounded-lg">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <div class="font-medium text-gray-900">{{ cat.category }}</div>
                  <div class="text-sm text-gray-500">{{ cat.asset_count }} assets</div>
                </div>
                <div class="text-right">
                  <div class="text-lg font-bold text-green-600">{{ formatCurrency(cat.total_allowance) }}</div>
                  <div class="text-sm text-gray-500">Total allowance</div>
                </div>
              </div>
              <div class="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-gray-500">Gross Value:</span>
                  <span class="font-medium ml-1">{{ formatCurrency(cat.gross_value) }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Wear & Tear:</span>
                  <span class="font-medium ml-1">{{ formatCurrency(cat.wear_tear) }}</span>
                </div>
                <div>
                  <span class="text-gray-500">Investment:</span>
                  <span class="font-medium ml-1">{{ formatCurrency(cat.investment_deduction) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Asset Details -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Asset Details</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Gross Amount</th>
                  <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Class</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Wear & Tear</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Investment</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total Allowance</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="asset in (capitalAllowances.asset_details || []).slice(0, 20)" :key="asset.name">
                  <td class="px-4 py-3">
                    <div class="font-medium text-gray-900">{{ asset.asset_name }}</div>
                    <div class="text-sm text-gray-500">{{ asset.name }}</div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ asset.category }}</td>
                  <td class="px-4 py-3 text-right text-sm text-gray-900">{{ formatCurrency(asset.gross_amount) }}</td>
                  <td class="px-4 py-3 text-center text-sm text-gray-600">{{ asset.wear_tear_class }}</td>
                  <td class="px-4 py-3 text-right text-sm text-green-600">{{ formatCurrency(asset.wear_tear_allowance) }}</td>
                  <td class="px-4 py-3 text-right text-sm text-purple-600">{{ formatCurrency(asset.investment_deduction) }}</td>
                  <td class="px-4 py-3 text-right text-sm font-bold text-green-600">{{ formatCurrency(asset.total_allowance) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab 4: KRA Instalments -->
      <div v-if="activeTab === 'kra'" class="space-y-6">
        <!-- Instalment Schedule -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">KRA Quarterly Instalment Schedule</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Quarter</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount Due</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Amount Paid</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Balance</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="inst in kraSchedule.instalments" :key="inst.quarter">
                  <td class="px-4 py-3">
                    <div class="font-medium text-gray-900">{{ inst.label }}</div>
                  </td>
                  <td class="px-4 py-3 text-sm text-gray-600">{{ inst.due_date_formatted }}</td>
                  <td class="px-4 py-3 text-right text-sm font-medium text-gray-900">
                    {{ formatCurrency(inst.amount_due) }}
                  </td>
                  <td class="px-4 py-3 text-right text-sm text-gray-900">
                    {{ formatCurrency(inst.amount_paid) }}
                  </td>
                  <td class="px-4 py-3 text-right">
                    <span :class="inst.balance > 0 ? 'text-red-600' : 'text-green-600'" class="font-medium">
                      {{ formatCurrency(inst.balance) }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="px-2 py-1 rounded text-xs font-medium" :class="getStatusBadge(inst.status)">
                      {{ inst.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Compliance Summary -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Total Annual Tax</div>
            <div class="text-xl font-bold text-gray-900">{{ formatCurrency(kraSchedule.total_annual_tax) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Total Paid</div>
            <div class="text-xl font-bold text-green-600">{{ formatCurrency(kraSchedule.total_paid) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Outstanding Balance</div>
            <div class="text-xl font-bold" :class="kraSchedule.total_balance > 0 ? 'text-red-600' : 'text-green-600'">
              {{ formatCurrency(kraSchedule.total_balance) }}
            </div>
          </div>
        </div>

        <!-- Compliance Status -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Compliance Status</h3>
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2">
              <div :class="getComplianceIcon(kraSchedule.compliance_status)" class="w-6 h-6"></div>
              <span class="text-lg font-medium" :class="getComplianceColor(kraSchedule.compliance_status)">
                {{ kraSchedule.compliance_status }}
              </span>
            </div>
            <div class="text-sm text-gray-500">
              {{ kraSchedule.overdue_count }} instalments overdue
            </div>
          </div>
          <div class="mt-4 p-4 bg-blue-50 rounded-lg">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> {{ kraSchedule.note }}
            </p>
          </div>
        </div>
      </div>

      <!-- Tab 5: WHT Analysis -->
      <div v-if="activeTab === 'wht'" class="space-y-6">
        <!-- WHT Summary -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">WHT Deducted</div>
            <div class="text-xl font-bold text-blue-600">{{ formatCurrency(whtAnalysis.total_wht_deducted) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">WHT Suffered</div>
            <div class="text-xl font-bold text-purple-600">{{ formatCurrency(whtAnalysis.total_wht_suffered) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Net WHT Position</div>
            <div class="text-xl font-bold" :class="whtAnalysis.net_wht_position >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ formatCurrency(whtAnalysis.net_wht_position) }}
            </div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Liability Balance</div>
            <div class="text-xl font-bold text-red-600">{{ formatCurrency(whtAnalysis.wht_liability_balance) }}</div>
          </div>
        </div>

        <!-- WHT by Supplier -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">WHT Deducted by Supplier</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Supplier</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Invoices</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">WHT Amount</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="sup in whtAnalysis.wht_deducted_by_supplier" :key="sup.supplier">
                  <td class="px-4 py-3">
                    <div class="font-medium text-gray-900">{{ sup.supplier_name || sup.supplier }}</div>
                  </td>
                  <td class="px-4 py-3 text-right text-sm text-gray-600">{{ sup.invoice_count }}</td>
                  <td class="px-4 py-3 text-right text-sm font-medium text-gray-900">
                    {{ formatCurrency(sup.wht_amount) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- WHT Rates Reference -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Kenya WHT Rates Reference</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(details, rateName) in (whtAnalysis.wht_rates || {})" :key="rateName"
                 class="p-4 bg-gray-50 rounded-lg">
              <div class="font-medium text-gray-900">{{ rateName }}</div>
              <div class="text-sm text-blue-600 font-medium">{{ (details as any)?.rate || '-' }}</div>
              <div class="text-xs text-gray-500">{{ (details as any)?.section || '' }}</div>
            </div>
          </div>
          <div class="mt-4 p-4 bg-yellow-50 rounded-lg">
            <p class="text-sm text-yellow-800">
              <strong>Remittance:</strong> {{ whtAnalysis.remittance_note }}
            </p>
          </div>
        </div>
      </div>

      <!-- Tab 6: Forecasts -->
      <div v-if="activeTab === 'forecasts'" class="space-y-6">
        <!-- Forecast Summary -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">YTD Progress</div>
            <div class="text-xl font-bold text-blue-600">{{ taxForecast.ytd_progress_pct }}%</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Projected Annual Tax</div>
            <div class="text-xl font-bold text-gray-900">{{ formatCurrency(taxForecast.projected_annual_tax) }}</div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Variance from YTD</div>
            <div class="text-xl font-bold" :class="taxForecast.variance_from_ytd >= 0 ? 'text-red-600' : 'text-green-600'">
              {{ formatCurrency(taxForecast.variance_from_ytd) }}
            </div>
          </div>
          <div class="bg-white rounded-lg shadow-sm p-4 border">
            <div class="text-sm text-gray-500">Potential Savings</div>
            <div class="text-xl font-bold text-green-600">
              {{ formatCurrency(taxForecast.tax_savings_potential?.total_potential_saving || 0) }}
            </div>
          </div>
        </div>

        <!-- Monthly Projections -->
        <div class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Monthly Tax Projections</h3>
          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead>
                <tr class="bg-gray-50">
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Month</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Revenue</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Expense</th>
                  <th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Projected Tax</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="proj in taxForecast.monthly_projections" :key="proj.month">
                  <td class="px-4 py-3 font-medium text-gray-900">{{ proj.month }}</td>
                  <td class="px-4 py-3 text-right text-sm text-gray-900">{{ formatCurrency(proj.projected_revenue) }}</td>
                  <td class="px-4 py-3 text-right text-sm text-gray-900">{{ formatCurrency(proj.projected_expense) }}</td>
                  <td class="px-4 py-3 text-right text-sm font-medium text-gray-900">{{ formatCurrency(proj.projected_tax) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Savings Opportunities -->
        <div v-if="taxForecast.tax_savings_potential?.opportunities?.length" class="bg-white rounded-lg shadow-sm p-6 border">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">Tax Savings Opportunities</h3>
          <div class="space-y-4">
            <div v-for="opp in taxForecast.tax_savings_potential.opportunities" :key="opp.opportunity"
                 class="p-4 bg-green-50 rounded-lg">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <div class="font-medium text-gray-900">{{ opp.opportunity }}</div>
                  <div class="text-sm text-gray-600 mt-1">{{ opp.description }}</div>
                </div>
                <div class="text-right">
                  <div class="text-lg font-bold text-green-600">{{ formatCurrency(opp.potential_saving) }}</div>
                  <div class="text-sm text-gray-500">Potential saving</div>
                </div>
              </div>
              <div class="text-sm text-gray-600">{{ opp.action }}</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- AI Chat Button -->
    <DashboardChatButton
      dashboard-type="Tax"
      :dashboard-context="chatContext"
      @navigate-dashboard="handleDashboardRedirect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Button } from 'frappe-ui'
import { useRouter } from 'vue-router'
import DashboardChatButton from '../components/DashboardChatButton.vue'

const router = useRouter()

// Reactive data
const loading = ref(false)
const lastUpdated = ref('')
const activeTab = ref('overview')

// Data stores with proper typing
const taxOverview = ref<Record<string, any>>({})
const incomeAnalysis = ref<Record<string, any>>({})
const expenseAnalysis = ref<Record<string, any>>({})
const capitalAllowances = ref<Record<string, any>>({})
const kraSchedule = ref<Record<string, any>>({})
const whtAnalysis = ref<Record<string, any>>({})
const taxForecast = ref<Record<string, any>>({})
const optimizationInsights = ref<any[]>([])

// Tabs configuration
const tabs = [
  { label: 'Overview', value: 'overview' },
  { label: 'Income & Expenses', value: 'income' },
  { label: 'Capital Allowances', value: 'capital' },
  { label: 'KRA Instalments', value: 'kra' },
  { label: 'WHT Analysis', value: 'wht' },
  { label: 'Forecasts', value: 'forecasts' }
]

// Load data on mount
onMounted(() => {
  refreshData()
})

// Refresh data function
async function refreshData() {
  loading.value = true
  try {
    const response = await fetch('/api/method/insights.api.ml.tax_intelligence?refresh=1', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': (window as any).csrf_token || ''
      }
    })

    const result = await response.json()

    if (result.message?.status === 'success') {
      const data = result.message

      taxOverview.value = data.tax_overview || {}
      incomeAnalysis.value = data.income_analysis || {}
      expenseAnalysis.value = data.expense_analysis || {}
      capitalAllowances.value = data.capital_allowances || {}
      kraSchedule.value = data.kra_schedule || {}
      whtAnalysis.value = data.wht_analysis || {}
      taxForecast.value = data.tax_forecast || {}
      optimizationInsights.value = data.optimization_insights || []

      lastUpdated.value = new Date().toISOString()
    } else {
      console.error('Tax Intelligence Error:', result.message?.message || result.exc || 'Unknown error')
    }
  } catch (error) {
    console.error('Error loading tax intelligence data:', error)
  } finally {
    loading.value = false
  }
}

// Helper functions
const formatCurrency = (amount: number) => {
  if (amount === null || amount === undefined) return 'KES 0'
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: 'KES',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

const formatDate = (date: string | undefined) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-KE', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPeriod = (period: string) => {
  if (!period) return ''
  const [year, month] = period.split('-')
  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${monthNames[parseInt(month) - 1]} ${year.slice(2)}`
}

// Calculation helpers
const getExpenseRatio = () => {
  const total = (expenseAnalysis.value.total_allowable || 0) + (expenseAnalysis.value.total_non_allowable || 0)
  if (total === 0) return 0
  return ((expenseAnalysis.value.total_allowable || 0) / total) * 100
}

const getIncomePct = (amount: number) => {
  const total = incomeAnalysis.value.total_income || 1
  return Math.min((amount / total) * 100, 100)
}

const getIncomeBarWidth = (amount: number) => {
  const maxAmount = Math.max(...(incomeAnalysis.value.monthly_trend?.map((m: any) => m.amount) || [1]))
  return Math.max(10, (amount / maxAmount) * 100)
}

// Color helpers
const getEffectiveRateColor = (rate: number) => {
  if (rate > 30) return 'text-red-600'
  if (rate > 25) return 'text-amber-600'
  return 'text-green-600'
}

const getEffectiveRateLabel = (rate: number) => {
  if (rate > 30) return 'High'
  if (rate > 25) return 'Moderate'
  return 'Optimal'
}

const getPositionColor = (amount: number) => {
  return amount > 0 ? 'text-red-600' : 'text-green-600'
}

const getPositionLabel = (amount: number) => {
  return amount > 0 ? 'Outstanding' : 'Paid'
}

const getInstalmentBgColor = (status: string) => {
  if (status === 'Paid') return 'bg-green-50 border-green-200'
  if (status === 'Overdue') return 'bg-red-50 border-red-200'
  if (status === 'Due Soon') return 'bg-amber-50 border-amber-200'
  return 'bg-gray-50 border-gray-200'
}

const getInstalmentTextColor = (status: string) => {
  if (status === 'Paid') return 'text-green-700'
  if (status === 'Overdue') return 'text-red-700'
  if (status === 'Due Soon') return 'text-amber-700'
  return 'text-gray-700'
}

const getStatusBadge = (status: string) => {
  if (status === 'Paid') return 'bg-green-100 text-green-700'
  if (status === 'Overdue') return 'bg-red-100 text-red-700'
  if (status === 'Due Soon') return 'bg-amber-100 text-amber-700'
  return 'bg-gray-100 text-gray-700'
}

const getComplianceIcon = (status: string) => {
  if (status === 'Fully Compliant') return 'text-green-500'
  if (status === 'On Track') return 'text-blue-500'
  return 'text-red-500'
}

const getComplianceColor = (status: string) => {
  if (status === 'Fully Compliant') return 'text-green-700'
  if (status === 'On Track') return 'text-blue-700'
  return 'text-red-700'
}

// Chat context for AI insights
const chatContext = computed(() => ({
  summary: taxOverview.value,
  taxOverview: taxOverview.value,
  expenseClassification: expenseAnalysis.value,
  capitalAllowances: capitalAllowances.value,
  kraSchedule: kraSchedule.value,
  whtAnalysis: whtAnalysis.value,
  optimizationInsights: optimizationInsights.value,
  activeTab: activeTab.value,
  lastUpdated: lastUpdated.value
}))

// Handle navigation to other dashboards from chat suggestions
function handleDashboardRedirect(target: string) {
  const routes: Record<string, string> = {
    'Sales': '/sales-intelligence',
    'Risk': '/risk-intelligence',
    'Inventory': '/inventory-intelligence',
    'Financial': '/financial-intelligence',
    'Customer': '/customer-intelligence',
    'Procurement': '/procurement-intelligence',
    'Tax': '/tax-intelligence'
  }
  if (routes[target]) {
    router.push(routes[target])
  }
}
</script>
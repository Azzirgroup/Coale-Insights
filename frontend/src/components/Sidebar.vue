<template>
	<div
		class="md:w-60 flex w-14 flex-shrink-0 flex-col border-r border-gray-300 bg-white"
	>
		<div class="flex flex-grow flex-col overflow-y-auto p-2.5">
			<div class="md:flex hidden flex-shrink-0 items-end text-sm text-gray-600">
				<img src="../assets/insights-logo-new.svg" class="h-7" />
			</div>
			<router-link to="/" class="md:hidden flex cursor-pointer">
				<img src="../assets/insights-logo-new.svg" class="rounded" />
			</router-link>

			<div class="mt-4 flex flex-col">
				<nav class="flex-1 space-y-1 pb-4 text-base">
					<Tooltip
						v-for="sidebarItem in sidebarItems"
						:key="sidebarItem.path"
						placement="right"
						:hoverDelay="0.1"
						class="w-full"
					>
						<template #body>
							<div
								class="w-fit rounded border border-gray-100 bg-gray-800 px-2 py-1 text-xs text-white shadow-xl"
							>
								{{ sidebarItem.label }}
							</div>
						</template>

						<router-link
							:to="sidebarItem.path"
							:class="[
								sidebarItem.current
									? 'bg-gray-200/70'
									: 'text-gray-700 hover:bg-gray-50 hover:text-gray-800',
								'md:justify-start group flex w-full items-center justify-center rounded p-2 font-medium',
							]"
							aria-current="page"
						>
							<component
								:is="sidebarItem.icon"
								:stroke-width="1.5"
								:class="[
									sidebarItem.current
										? 'text-gray-800'
										: 'text-gray-700 group-hover:text-gray-700',
									'md:mr-3 md:h-4 md:w-4 mr-0 h-5 w-5 flex-shrink-0',
								]"
							/>

							<span class="md:inline-block hidden">{{ sidebarItem.label }}</span>
						</router-link>
					</Tooltip>
				</nav>
			</div>

			<div class="mt-auto flex flex-col items-center gap-2 text-base text-gray-600">
				<Button variant="ghost" @click="open('https://docs.frappeinsights.com')">
					<BookOpen class="h-4 text-gray-600" />
				</Button>
				<Dropdown
					placement="left"
					:options="[
						{
							label: 'Documentation',
							icon: 'help-circle',
							onClick: () => open('https://docs.frappeinsights.com'),
						},
						{
							label: 'Join Telegram Group',
							icon: 'message-circle',
							onClick: () => open('https://t.me/frappeinsights'),
						},
						{
							label: 'Help',
							icon: 'life-buoy',
							onClick: () => (showHelpDialog = true),
						},
						session.user.is_admin
							? {
									label: 'Switch to Desk',
									icon: 'grid',
									onClick: () => open('/app'),
							  }
							: null,
						{
							label: 'Logout',
							icon: 'log-out',
							onClick: () => session.logout(),
						},
					]"
				>
					<template v-slot="{ open }">
						<button
							class="flex w-full items-center space-x-2 rounded p-1 text-left text-base font-medium"
							:class="open ? 'bg-gray-300' : 'hover:bg-gray-200'"
						>
							<Avatar
								size="xl"
								:label="session.user.full_name"
								:image="session.user.user_image"
							/>
							<span
								class="md:inline ml-2 hidden overflow-hidden text-ellipsis whitespace-nowrap"
							>
								{{ session.user.full_name }}
							</span>
							<FeatherIcon name="chevron-down" class="md:inline hidden h-4 w-4" />
						</button>
					</template>
				</Dropdown>
			</div>
		</div>
	</div>

	<HelpDialog v-model="showHelpDialog" />

</template>

<script setup>
import { Avatar } from 'frappe-ui'

import HelpDialog from '@/components/HelpDialog.vue'
import sessionStore from '@/stores/sessionStore'
import settingsStore from '@/stores/settingsStore'
import {
	Book,
	BookOpen,
	Brain,
	Database,
	GanttChartSquare,
	HomeIcon,
	LayoutPanelTop,
	Settings,
	User,
	Users,
	ShieldAlert,
	TrendingUp,
	Package,
	Wallet,
	ShoppingCart,
	UserCheck,
} from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const session = sessionStore()
const settings = settingsStore().settings

const showHelpDialog = ref(false)

const sidebarItems = ref([
	{
		path: '/',
		label: 'Home',
		icon: HomeIcon,
		name: 'Home',
		current: false,
	},
	{
		path: '/ai-insights',
		label: 'AI Insights',
		icon: Brain,
		name: 'AIInsights',
		current: false,
	},
	{
		path: '/dashboard',
		label: 'Dashboards',
		icon: LayoutPanelTop,
		name: 'Dashboard',
		current: false,
	},
	{
		path: '/risk-intelligence',
		label: 'Risk Intelligence',
		icon: ShieldAlert,
		name: 'RiskIntelligence',
		current: false,
	},
	{
		path: '/sales-intelligence',
		label: 'Sales Intelligence',
		icon: TrendingUp,
		name: 'SalesIntelligence',
		current: false,
	},
	{
		path: '/inventory-intelligence',
		label: 'Inventory Intelligence',
		icon: Package,
		name: 'InventoryIntelligence',
		current: false,
	},
	{
		path: '/financial-intelligence',
		label: 'Financial Intelligence',
		icon: Wallet,
		name: 'FinancialIntelligence',
		current: false,
	},
	{
		path: '/procurement-intelligence',
		label: 'Procurement Intelligence',
		icon: ShoppingCart,
		name: 'ProcurementIntelligence',
		current: false,
	},
	{
		path: '/customer-intelligence',
		label: 'Customer Intelligence',
		icon: UserCheck,
		name: 'CustomerIntelligence',
		current: false,
	},
	{
		path: '/query',
		label: 'Query',
		icon: GanttChartSquare,
		name: 'QueryList',
		current: false,
	},
	{
		path: '/data-source',
		label: 'Data Sources',
		icon: Database,
		name: 'Data Source',
	},
	{
		path: '/notebook',
		label: 'Notebook',
		icon: Book,
		name: 'Notebook',
		current: false,
	},
	{
		path: '/settings',
		label: 'Settings',
		icon: Settings,
		name: 'Settings',
		current: false,
	},
])

console.log('Sidebar items:', sidebarItems.value)

const route = useRoute()
const currentRoute = computed(() => {
	sidebarItems.value.forEach((item) => {
		// check if /<route> or /<route>/<id> is in sidebar item path
		item.current = route.path.match(new RegExp(`^${item.path}(/|$)`))
	})
	return route.path
})

const open = (url) => window.open(url, '_blank')
</script>

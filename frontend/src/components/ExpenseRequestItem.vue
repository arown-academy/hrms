<template>
	<ListItem
		:isTeamRequest="props.isTeamRequest"
		:employee="props.doc.employee"
		:employeeName="props.doc.employee_name"
	>
		<template #left>
			<ExpenseIcon class="h-5 w-5 text-gray-500" />
			<div class="flex flex-col items-start gap-1.5">
				<div class="text-base font-normal text-gray-800">
					{{ __("{0} Request", [__(props.doc.expense_category || "Expense")]) }}
				</div>
				<div class="text-xs font-normal text-gray-500">
					<span>{{ requestDate }}</span>
					<span class="whitespace-pre"> &middot; </span>
					<span class="whitespace-nowrap">
						{{ formatCurrency(props.doc.estimated_amount, props.doc.currency) }}
					</span>
				</div>
			</div>
		</template>
		<template #right>
			<Badge
				variant="outline"
				:theme="statusMap[status] || 'gray'"
				:label="__(status, null, 'Expense Request')"
				size="md"
			/>
			<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
		</template>
	</ListItem>
</template>

<script setup>
// Expense Request (arown) = step 1 of an expense; the Expense Claim is made from it once approved
import { FeatherIcon, Badge } from "frappe-ui"
import { computed, inject } from "vue"

import ListItem from "@/components/ListItem.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"

import { formatCurrency } from "@/utils/formatters"

const dayjs = inject("$dayjs")
const __ = inject("$translate")
const props = defineProps({
	doc: {
		type: Object,
	},
	isTeamRequest: {
		type: Boolean,
		default: false,
	},
	workflowStateField: {
		type: String,
		required: false,
	},
})

const statusMap = {
	Draft: "gray",
	"Request Pending Department Head": "orange",
	"Request Pending HR Head": "orange",
	"Request Pending Accounts": "orange",
	"Pending HR Booking": "blue",
	"Request Approved": "green",
	"Request Rejected": "red",
	Approved: "green",
	Claimed: "blue",
	Rejected: "red",
	Cancelled: "red",
}

// approved requests show whether the claim is made yet
const status = computed(() => {
	if (props.doc.docstatus === 2 || props.doc.status === "Cancelled") return "Cancelled"
	if (props.doc.status === "Claimed") return "Claimed"
	return props.doc.workflow_state || props.doc.status || "Draft"
})

const requestDate = computed(() => dayjs(props.doc.request_date).format("D MMM"))
</script>

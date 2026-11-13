<template>
	<BaseLayout :pageTitle="__('Expense Claims')">
		<template #body>
			<div class="flex flex-col mt-7 mb-7 p-4 gap-7">
				<ExpenseClaimSummary />

				<!-- step 1: the request (purpose, estimate, booking) is approved first; step 2: the claim made from it -->
				<div class="w-full flex flex-col gap-3">
					<router-link
						:to="{ name: 'ExpenseRequestFormView' }"
						v-slot="{ navigate }"
					>
						<Button
							@click="navigate"
							variant="solid"
							class="w-full py-5 text-base"
						>
							{{ __("Request an Expense") }}
						</Button>
					</router-link>
					<router-link
						:to="{ name: 'ExpenseClaimFormView' }"
						v-slot="{ navigate }"
					>
						<Button
							@click="navigate"
							variant="subtle"
							class="w-full py-5 text-base"
						>
							{{ __("Claim an Expense") }}
						</Button>
					</router-link>
					<p class="text-sm text-gray-600">
						{{ __("Claims are made from an approved expense request.") }}
					</p>
				</div>

				<div>
					<div class="text-lg text-gray-800 font-bold">{{ __("Expense Requests") }}</div>
					<RequestList
						:component="markRaw(ExpenseRequestItem)"
						:items="myExpenseRequests.data"
						:addListButton="true"
						listButtonRoute="ExpenseRequestListView"
						:emptyStateMessage="__('You have no expense requests')"
					/>
				</div>

				<div>
					<div class="text-lg text-gray-800 font-bold">{{ __("Recent Expenses") }}</div>
					<RequestList
						:component="markRaw(ExpenseClaimItem)"
						:items="myClaims.data"
						:addListButton="true"
						listButtonRoute="ExpenseClaimListView"
					/>
				</div>

				<div>
					<div class="flex flex-row justify-between items-center">
						<div class="text-lg text-gray-800 font-bold">
							{{ __("Employee Advance Balance") }}
						</div>
						<router-link
							:to="{ name: 'EmployeeAdvanceListView' }"
							class="text-sm text-gray-800 font-semibold cursor-pointer underline underline-offset-2"
						>
							{{ __("View List") }}
						</router-link>
					</div>

					<EmployeeAdvanceBalance :items="advanceBalance.data" />
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { markRaw, onMounted } from "vue"

import BaseLayout from "@/components/BaseLayout.vue"
import ExpenseClaimSummary from "@/components/ExpenseClaimSummary.vue"
import RequestList from "@/components/RequestList.vue"
import ExpenseClaimItem from "@/components/ExpenseClaimItem.vue"
import ExpenseRequestItem from "@/components/ExpenseRequestItem.vue"
import EmployeeAdvanceBalance from "@/components/EmployeeAdvanceBalance.vue"

import { myClaims } from "@/data/claims"
import { myExpenseRequests } from "@/data/expenseRequests"
import { advanceBalance } from "@/data/advances"

onMounted(() => myExpenseRequests.reload())
</script>

<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView
				v-if="formFields.data"
				doctype="Expense Request"
				v-model="expenseRequest"
				:isSubmittable="true"
				:fields="formFields.data"
				:id="props.id"
				:showAttachmentView="true"
				:showFormButton="!claimStep"
				@validateForm="validateForm"
			>
				<!-- approved request: step 2 = the Expense Claim -->
				<template #formButton>
					<div class="flex flex-col gap-2">
						<p v-if="!expenseRequest.expense_claim" class="text-sm text-gray-600">
							{{ __("Approved. After spending, create the Expense Claim with the actual expenses and bills.") }}
						</p>
						<Button
							v-if="expenseRequest.expense_claim"
							class="w-full rounded py-5 text-base"
							variant="subtle"
							@click="router.push({ name: 'ExpenseClaimDetailView', params: { id: expenseRequest.expense_claim } })"
						>
							{{ __("View Expense Claim") }}
						</Button>
						<Button
							v-else
							class="w-full rounded py-5 text-base"
							variant="solid"
							@click="router.push({ name: 'ExpenseClaimFormView', query: { expense_request: props.id } })"
						>
							{{ __("Create Expense Claim") }}
						</Button>
					</div>
				</template>
			</FormView>
		</ion-content>
	</ion-page>
</template>

<script setup>
// Expense Request (arown) = step 1 of an expense: purpose, estimate, booking by HR. Approved by Department Head ->
// HR Head -> Accounts (-> HR attaches the booking). Then the employee creates the Expense Claim from it (step 2).
import { IonPage, IonContent } from "@ionic/vue"
import { createResource } from "frappe-ui"
import { computed, ref, watch, inject } from "vue"
import { useRouter } from "vue-router"

import FormView from "@/components/FormView.vue"

const router = useRouter()
const __ = inject("$translate")
const dayjs = inject("$dayjs")
const employee = inject("$employee")

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

const expenseRequest = ref({
	employee: employee.data.name,
	employee_name: employee.data.employee_name,
	company: employee.data.company,
	department: employee.data.department,
	request_date: dayjs().format("YYYY-MM-DD"),
})

// the mobile form does not evaluate depends_on
const TRAVEL_FIELDS = [
	"travel_section",
	"from_place",
	"to_place",
	"mode_of_travel",
	"travel_start_date",
	"travel_end_date",
]
const BOOKING_FIELDS = ["booking_details", "booking_remarks"]
// set by the server / approvers: not shown on a new request
const SERVER_FIELDS = ["status", "remarks", "expense_claim", "workflow_state"]
// user ids for the workflow; the form shows the approvers' names (*_name)
const APPROVER_IDS = ["expense_approver", "hr_approver", "accounts_approver"]
const APPROVER_NAMES = ["expense_approver_name", "hr_approver_name", "accounts_approver_name"]
const NOT_SET = "Not set - ask HR"

const formFields = createResource({
	url: "hrms.api.get_doctype_fields",
	params: { doctype: "Expense Request" },
	transform(data) {
		const exclude = ["currency", ...APPROVER_IDS]
		if (!props.id) exclude.push("employee", "employee_name", "department", "company", ...SERVER_FIELDS)
		return data
			.filter((field) => !exclude.includes(field.fieldname))
			.map((field) => {
				if (field.fieldname === "request_date") field.default = dayjs().format("YYYY-MM-DD")
				if (field.fieldname === "booking_details") field.reqd = 0
				return field
			})
	},
	onSuccess() {
		setFieldVisibility()
		if (!props.id) approvers.fetch({ employee: employee.data.name })
	},
})
formFields.reload()

// the Department Head / HR Head / Accounts approvers of the employee (Employee > Approvers), before saving.
// A missing one shows "Not set - ask HR" (the server refills the names on save and refuses Submit without them).
const approvers = createResource({
	url: "arown.arown.doctype.expense_request.expense_request.get_employee_approvers",
	onSuccess(data) {
		APPROVER_IDS.forEach((field) => {
			expenseRequest.value[field] = data?.[field] || ""
			expenseRequest.value[`${field}_name`] = data?.[`${field}_name`] || __(NOT_SET)
		})
	},
})

// the employee's own approved request: show Create / View Expense Claim instead of the workflow actions
const claimStep = computed(
	() =>
		Boolean(props.id) &&
		expenseRequest.value.docstatus === 1 &&
		expenseRequest.value.employee === employee.data.name
)

function setFieldVisibility() {
	formFields.data?.forEach((field) => {
		if (TRAVEL_FIELDS.includes(field.fieldname)) {
			field.hidden = expenseRequest.value.expense_category !== "Travel"
		} else if (BOOKING_FIELDS.includes(field.fieldname)) {
			field.hidden = !expenseRequest.value.booking_required
			if (field.fieldname === "booking_details") field.reqd = expenseRequest.value.booking_required ? 1 : 0
		} else if (field.fieldname === "expense_claim") {
			field.hidden = !expenseRequest.value.expense_claim
		}
	})
}

watch(
	() => [
		expenseRequest.value.expense_category,
		expenseRequest.value.booking_required,
		expenseRequest.value.expense_claim,
	],
	() => setFieldVisibility()
)

function validateForm() {
	if (!props.id) expenseRequest.value.employee = employee.data.name
	APPROVER_NAMES.forEach((field) => {
		if (expenseRequest.value[field] === __(NOT_SET)) expenseRequest.value[field] = ""
	})
}
</script>

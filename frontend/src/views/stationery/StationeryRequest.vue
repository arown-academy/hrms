<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col gap-4 p-4">
				<!-- ========================= -->
				<!-- HEADER -->
				<!-- ========================= -->

				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<!-- Back Button -->
						<button
							v-if="showForm"
							type="button"
							class="flex h-9 w-9 items-center justify-center rounded-full"
							@click="closeForm"
						>
							<span class="text-2xl leading-none">
								‹
							</span>
						</button>

						<h1 class="text-xl font-semibold">
							{{
								showForm
									? __("New Stationery Request")
									: __("Stationery Requests")
							}}
						</h1>
					</div>

					<!-- Add Request -->
					<button
						v-if="!showForm"
						type="button"
						class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white"
						@click="openForm"
					>
						{{ __("Request Stationery") }}
					</button>
				</div>

				<!-- ========================= -->
				<!-- ERROR -->
				<!-- ========================= -->

				<div
					v-if="errorMessage"
					class="rounded-lg bg-white p-4 shadow-sm"
				>
					<p class="text-sm text-red-500">
						{{ errorMessage }}
					</p>
				</div>

				<!-- ========================= -->
				<!-- STATIONERY REQUEST FORM -->
				<!-- ========================= -->

				<div
					v-if="showForm"
					class="rounded-lg bg-white p-4 shadow-sm"
				>
					<div class="flex flex-col gap-4">
						<!-- Form Header -->
						<div class="flex items-center justify-between">
							<h2 class="text-base font-semibold">
								{{ __("Request Stationery") }}
							</h2>

							<button
								type="button"
								class="text-sm text-gray-500"
								@click="closeForm"
							>
								{{ __("Cancel") }}
							</button>
						</div>

						<!-- ========================= -->
						<!-- EMPLOYEE -->
						<!-- ========================= -->

						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Employee") }}
							</label>

							<input
								v-model="form.employee"
								type="text"
								readonly
								class="w-full rounded-lg border border-gray-300 bg-gray-100 px-3 py-3 text-sm text-gray-600"
								:placeholder="
									loadingEmployee
										? __('Loading...')
										: __('Employee')
								"
							/>
						</div>

						<!-- ========================= -->
						<!-- EMPLOYEE NAME -->
						<!-- ========================= -->

						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Employee Name") }}
							</label>

							<input
								v-model="form.employee_name"
								type="text"
								readonly
								class="w-full rounded-lg border border-gray-300 bg-gray-100 px-3 py-3 text-sm text-gray-600"
							/>
						</div>

						<!-- ========================= -->
						<!-- REQUEST DATE -->
						<!-- ========================= -->

						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Request Date") }}

								<span class="text-red-500">
									*
								</span>
							</label>

							<input
								v-model="form.request_date"
								type="date"
								class="w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-sm"
							/>
						</div>

						<!-- ========================= -->
						<!-- STATIONERY -->
						<!-- ========================= -->

						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Stationery") }}

								<span class="text-red-500">
									*
								</span>
							</label>

							<select
								v-model="form.stationery"
								class="w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-sm"
							>
								<option value="">
									{{ __("Select Stationery") }}
								</option>

								<option
									v-for="item in stationeryList"
									:key="item.name"
									:value="item.name"
								>
									{{
										item.stationery_name ||
										item.name
									}}
								</option>
							</select>
						</div>

						<!-- ========================= -->
						<!-- QUANTITY -->
						<!-- ========================= -->

						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Quantity") }}

								<span class="text-red-500">
									*
								</span>
							</label>

							<input
								v-model.number="form.quantity"
								type="number"
								min="1"
								class="w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-sm"
								:placeholder="
									__('Enter quantity')
								"
							/>
						</div>

						<!-- ========================= -->
						<!-- APPROVER -->
						<!-- ========================= -->

						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Approver") }}
							</label>

							<input
								v-model="form.approver"
								type="text"
								readonly
								class="w-full rounded-lg border border-gray-300 bg-gray-100 px-3 py-3 text-sm text-gray-600"
								:placeholder="
									loadingEmployee
										? __('Loading...')
										: __('Not configured')
								"
							/>
						</div>

						<!-- ========================= -->
						<!-- REASON -->
						<!-- ========================= -->

						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Reason") }}
							</label>

							<textarea
								v-model="form.reason"
								rows="4"
								class="w-full rounded-lg border border-gray-300 px-3 py-3 text-sm"
								:placeholder="
									__(
										'Enter reason for requesting stationery'
									)
								"
							></textarea>
						</div>

						<!-- ========================= -->
						<!-- SUBMIT -->
						<!-- ========================= -->

						<button
							type="button"
							class="w-full rounded-lg bg-gray-900 px-4 py-3 text-sm font-medium text-white disabled:opacity-50"
							:disabled="
								submitting ||
								loadingEmployee ||
								!form.employee ||
								!form.stationery ||
								!form.quantity ||
								!form.approver
							"
							@click="submitRequest"
						>
							{{
								submitting
									? __("Submitting...")
									: __("Submit Request")
							}}
						</button>
					</div>
				</div>

				<!-- ========================= -->
				<!-- LOADING -->
				<!-- ========================= -->

				<div
					v-if="loading && !showForm"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<p class="text-gray-500">
						{{
							__(
								"Loading stationery requests..."
							)
						}}
					</p>
				</div>

				<!-- ========================= -->
				<!-- NO REQUESTS -->
				<!-- ========================= -->

				<div
					v-else-if="
						!showForm &&
						requestList.length === 0
					"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<p class="text-gray-500">
						{{
							__(
								"You have not submitted any stationery requests yet."
							)
						}}
					</p>
				</div>

				<!-- ========================= -->
				<!-- REQUEST LIST -->
				<!-- ========================= -->

				<div
					v-else-if="
						!showForm &&
						requestList.length > 0
					"
					class="flex flex-col gap-3"
				>
					<h2 class="text-base font-semibold">
						{{ __("My Stationery Requests") }}
					</h2>

					<div
						v-for="item in requestList"
						:key="item.name"
						class="rounded-lg bg-white p-4 shadow-sm"
					>
						<div class="flex flex-col gap-3">
							<!-- Stationery + Status -->
							<div
								class="flex items-start justify-between gap-3"
							>
								<div>
									<h3 class="text-base font-semibold">
										{{ item.stationery }}
									</h3>

									<p
										class="mt-1 text-xs text-gray-500"
									>
										{{ __("Request") }}:
										{{ item.name }}
									</p>
								</div>

								<span
									v-if="
										item.workflow_state ||
										item.status
									"
									class="rounded-full bg-gray-100 px-3 py-1 text-xs"
								>
									{{
										item.workflow_state ||
										item.status
									}}
								</span>
							</div>

							<!-- Quantity -->
							<div v-if="item.quantity">
								<p class="text-sm text-gray-600">
									{{ __("Quantity") }}:
									{{ item.quantity }}
								</p>
							</div>

							<!-- Employee -->
							<div v-if="item.employee_name">
								<p class="text-xs text-gray-500">
									{{ __("Employee") }}:
									{{ item.employee_name }}
								</p>
							</div>

							<!-- Request Date -->
							<div v-if="item.request_date">
								<p class="text-xs text-gray-400">
									{{ __("Request Date") }}:
									{{
										formatDate(
											item.request_date
										)
									}}
								</p>
							</div>

							<!-- Approver -->
							<div v-if="item.approver">
								<p class="text-xs text-gray-500">
									{{ __("Approver") }}:
									{{ item.approver }}
								</p>
							</div>

							<!-- Reason -->
							<div v-if="item.reason">
								<p class="text-xs text-gray-500">
									{{ __("Reason") }}
								</p>

								<p
									class="mt-1 whitespace-pre-line text-sm text-gray-600"
								>
									{{ item.reason }}
								</p>
							</div>

							<!-- Stock Updated -->
							<div v-if="item.stock_updated">
								<p class="text-xs text-gray-500">
									{{ __("Stock Updated") }}
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { inject, onMounted, ref } from "vue"

import BaseLayout from "@/components/BaseLayout.vue"

const __ = inject("$translate")

/*
 * =========================
 * STATE
 * =========================
 */

const requestList = ref([])
const stationeryList = ref([])

const loading = ref(true)
const loadingEmployee = ref(false)
const submitting = ref(false)
const showForm = ref(false)
const errorMessage = ref("")

/*
 * Form
 */

const form = ref({
	employee: "",
	employee_name: "",
	request_date: "",
	stationery: "",
	quantity: "",
	approver: "",
	reason: "",
})

/*
 * =========================
 * FORMAT DATE
 * =========================
 */

const formatDate = (value) => {
	if (!value) {
		return ""
	}

	const date = new Date(
		value.includes(" ")
			? value.replace(" ", "T")
			: value
	)

	return date.toLocaleDateString()
}

/*
 * =========================
 * GET LOGGED-IN USER
 * =========================
 */

const getLoggedInUser = async () => {
	const response = await fetch(
		"/api/method/frappe.auth.get_logged_user"
	)

	const result = await response.json()

	if (!response.ok) {
		console.error(
			"Logged User API Error:",
			result
		)

		throw new Error(
			result?.exception ||
				result?.message ||
				__(
					"Unable to identify the logged-in user."
				)
		)
	}

	if (!result.message) {
		throw new Error(
			__(
				"Unable to identify the logged-in user."
			)
		)
	}

	return result.message
}

/*
 * =========================
 * GET EMPLOYEE DETAILS
 * =========================
 *
 * Employee
 *    ↓
 * custom_stationary_item_approver
 *    ↓
 * Approver
 *
 */

const getEmployeeDetails = async () => {
	const user = await getLoggedInUser()

	const fields = JSON.stringify([
		"name",
		"user_id",
		"employee_name",
		"custom_stationary_item_approver",
	])

	const filters = JSON.stringify([
		["user_id", "=", user],
	])

	const url =
		"/api/resource/Employee" +
		"?fields=" +
		encodeURIComponent(fields) +
		"&filters=" +
		encodeURIComponent(filters) +
		"&limit_page_length=1"

	const response = await fetch(url)

	const result = await response.json()

	if (!response.ok) {
		console.error(
			"Employee API Error:",
			result
		)

		throw new Error(
			result?.exception ||
				result?.message ||
				__(
					"Unable to find your Employee record."
				)
		)
	}

	if (
		!result.data ||
		result.data.length === 0
	) {
		throw new Error(
			__(
				"No Employee record is linked to your login user."
			)
		)
	}

	return result.data[0]
}

/*
 * =========================
 * LOAD EMPLOYEE
 * =========================
 */

const loadEmployeeDetails = async () => {
	loadingEmployee.value = true
	errorMessage.value = ""

	try {
		const employee =
			await getEmployeeDetails()

		form.value.employee =
			employee.name

		form.value.employee_name =
			employee.employee_name ||
			employee.name

		form.value.approver =
			employee.custom_stationary_item_approver ||
			""

		if (!form.value.approver) {
			throw new Error(
				__(
					"Stationery approver is not configured for your Employee record."
				)
			)
		}
	} catch (error) {
		console.error(
			"Error loading employee details:",
			error
		)

		errorMessage.value =
			error.message ||
			__(
				"Unable to load employee details."
			)
	} finally {
		loadingEmployee.value = false
	}
}

/*
 * =========================
 * LOAD STATIONERY MASTER
 * =========================
 */

const loadStationeryList = async () => {
	try {
		const fields = JSON.stringify([
			"name",
			"stationery_name",
		])

		const url =
			"/api/resource/Stationery" +
			"?fields=" +
			encodeURIComponent(fields) +
			"&limit_page_length=100"

		const response = await fetch(url)

		const result = await response.json()

		if (!response.ok) {
			console.error(
				"Stationery API Error:",
				result
			)

			throw new Error(
				result?.exception ||
					result?.message ||
					__(
						"Unable to load stationery items."
					)
			)
		}

		stationeryList.value =
			result.data || []
	} catch (error) {
		console.error(
			"Error loading stationery:",
			error
		)

		errorMessage.value =
			error.message ||
			__(
				"Unable to load stationery items."
			)
	}
}

/*
 * =========================
 * LOAD USER REQUESTS
 * =========================
 */

const loadRequests = async () => {
	loading.value = true
	errorMessage.value = ""

	try {
		const employee =
			await getEmployeeDetails()

		const fields = JSON.stringify([
			"name",
			"employee",
			"employee_name",
			"request_date",
			"stationery",
			"quantity",
			"status",
			"workflow_state",
			"stock_updated",
			"approver",
			"reason",
		])

		const filters = JSON.stringify([
			[
				"employee",
				"=",
				employee.name,
			],
		])

		const url =
			"/api/resource/Stationery Request" +
			"?fields=" +
			encodeURIComponent(fields) +
			"&filters=" +
			encodeURIComponent(filters) +
			"&order_by=" +
			encodeURIComponent(
				"request_date desc"
			) +
			"&limit_page_length=100"

		const response = await fetch(url)

		const result = await response.json()

		if (!response.ok) {
			console.error(
				"Stationery Request API Error:",
				result
			)

			throw new Error(
				result?.exception ||
					result?.message ||
					__(
						"Unable to load stationery requests."
					)
			)
		}

		requestList.value =
			result.data || []
	} catch (error) {
		console.error(
			"Error loading stationery requests:",
			error
		)

		errorMessage.value =
			error.message ||
			__(
				"Unable to load stationery requests."
			)
	} finally {
		loading.value = false
	}
}

/*
 * =========================
 * OPEN FORM
 * =========================
 */

const openForm = async () => {
	errorMessage.value = ""

	form.value = {
		employee: "",
		employee_name: "",
		request_date: getToday(),
		stationery: "",
		quantity: "",
		approver: "",
		reason: "",
	}

	showForm.value = true

	await Promise.all([
		loadEmployeeDetails(),
		loadStationeryList(),
	])
}

/*
 * =========================
 * SUBMIT REQUEST
 * =========================
 *
 * IMPORTANT:
 *
 * First:
 *
 * Draft
 *
 * Then workflow action:
 *
 * Submit
 *
 * Result:
 *
 * Pending Approval
 *
 */

const submitRequest = async () => {
	errorMessage.value = ""

	/*
	 * =========================
	 * VALIDATION
	 * =========================
	 */

	if (!form.value.employee) {
		errorMessage.value = __(
			"Unable to identify your Employee record."
		)

		return
	}

	if (!form.value.request_date) {
		errorMessage.value = __(
			"Please select the request date."
		)

		return
	}

	if (!form.value.stationery) {
		errorMessage.value = __(
			"Please select a stationery item."
		)

		return
	}

	if (
		!form.value.quantity ||
		Number(form.value.quantity) <= 0
	) {
		errorMessage.value = __(
			"Please enter a valid quantity."
		)

		return
	}

	if (!form.value.approver) {
		errorMessage.value = __(
			"Stationery approver is not configured."
		)

		return
	}

	submitting.value = true

	try {
		/*
		 * =========================
		 * CREATE DOCUMENT
		 * =========================
		 *
		 * VERY IMPORTANT:
		 *
		 * workflow_state = Draft
		 *
		 * Do NOT send:
		 *
		 * status: ""
		 *
		 */

		const doc = {
			doctype: "Stationery Request",

			employee:
				form.value.employee,

			employee_name:
				form.value.employee_name,

			request_date:
				form.value.request_date,

			stationery:
				form.value.stationery,

			quantity:
				Number(form.value.quantity),

			approver:
				form.value.approver,

			reason:
				form.value.reason
					? form.value.reason.trim()
					: "",

			/*
			 * Start workflow in Draft.
			 */
			workflow_state: "Draft",
		}

		console.log(
			"Creating Stationery Request:",
			doc
		)

		const response = await fetch(
			"/api/resource/Stationery Request",
			{
				method: "POST",

				headers: {
					"Content-Type":
						"application/json",

					"X-Frappe-CSRF-Token":
						window.frappe?.csrf_token ||
						window.csrf_token ||
						"fetch",
				},

				body: JSON.stringify(doc),
			}
		)

		const result =
			await response.json()

		if (!response.ok) {
			console.error(
				"Create Stationery Request Error:",
				result
			)

			throw new Error(
				result?.exception ||
					result?.message ||
					__(
						"Unable to create stationery request."
					)
			)
		}

		const request =
			result.data

		if (!request?.name) {
			throw new Error(
				__(
					"Stationery Request was created but no document name was returned."
				)
			)
		}

		console.log(
			"Stationery Request created:",
			request
		)

		/*
		 * =========================
		 * APPLY WORKFLOW
		 * =========================
		 *
		 * Draft
		 *   ↓
		 * Submit
		 *   ↓
		 * Pending Approval
		 */

		await submitWorkflow(
			request.name
		)

		/*
		 * =========================
		 * RESET FORM
		 * =========================
		 */

		resetForm()

		showForm.value = false

		/*
		 * Reload requests
		 */

		await loadRequests()
	} catch (error) {
		console.error(
			"Error submitting stationery request:",
			error
		)

		errorMessage.value =
			error.message ||
			__(
				"Unable to submit stationery request."
			)
	} finally {
		submitting.value = false
	}
}

/*
 * =========================
 * WORKFLOW SUBMIT
 * =========================
 */

const submitWorkflow = async (
	requestName
) => {
	console.log(
		"Applying workflow Submit to:",
		requestName
	)

	const response = await fetch(
		"/api/method/frappe.model.workflow.apply_workflow",
		{
			method: "POST",

			headers: {
				"Content-Type":
					"application/json",

				"X-Frappe-CSRF-Token":
					window.frappe?.csrf_token ||
					window.csrf_token ||
					"fetch",
			},

			body: JSON.stringify({
				doc: {
					doctype:
						"Stationery Request",

					name:
						requestName,
				},

				action: "Submit",
			}),
		}
	)

	const result =
		await response.json()

	if (!response.ok) {
		console.error(
			"Workflow Submit Error:",
			result
		)

		throw new Error(
			result?.exception ||
				result?.message ||
				__(
					"Request was created, but could not be submitted for approval."
				)
		)
	}

	console.log(
		"Stationery Request workflow submitted:",
		result
	)

	return result
}

/*
 * =========================
 * TODAY
 * =========================
 */

const getToday = () => {
	const now = new Date()

	const pad = (number) =>
		String(number).padStart(2, "0")

	return (
		`${now.getFullYear()}-${pad(
			now.getMonth() + 1
		)}-${pad(now.getDate())}`
	)
}

/*
 * =========================
 * RESET FORM
 * =========================
 */

const resetForm = () => {
	form.value = {
		employee: "",
		employee_name: "",
		request_date: "",
		stationery: "",
		quantity: "",
		approver: "",
		reason: "",
	}
}

/*
 * =========================
 * CLOSE FORM
 * =========================
 */

const closeForm = () => {
	showForm.value = false

	errorMessage.value = ""

	resetForm()
}

/*
 * =========================
 * INITIAL LOAD
 * =========================
 */

onMounted(() => {
	loadRequests()
})
</script>

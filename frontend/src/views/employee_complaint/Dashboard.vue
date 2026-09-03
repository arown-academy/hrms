<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col gap-4 p-4">
				<!-- Header -->
				<div class="flex items-center justify-between">
					<div class="flex items-center gap-3">
						<!-- Back Button -->
						<button
							type="button"
							class="flex h-9 w-9 items-center justify-center rounded-full"
							@click="goHome"
						>
							<span class="text-3xl leading-none">‹</span>
						</button>

						<h1 class="text-xl font-semibold">
							{{ showForm ? __("New Complaint") : __("Complaints") }}
						</h1>
					</div>

					<!-- Add Complaint -->
					<button
						v-if="!showForm"
						type="button"
						class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white"
						@click="openForm"
					>
						{{ __("Add Complaint") }}
					</button>
				</div>

				<!-- Error -->
				<div
					v-if="errorMessage"
					class="rounded-lg bg-white p-4 shadow-sm"
				>
					<p class="text-sm text-red-500">
						{{ errorMessage }}
					</p>
				</div>

				<!-- ========================= -->
				<!-- COMPLAINT FORM -->
				<!-- ========================= -->

				<div
					v-if="showForm"
					class="rounded-lg bg-white p-4 shadow-sm"
				>
					<div class="flex flex-col gap-4">
						<!-- Form Header -->
						<div class="flex items-center justify-between">
							<h2 class="text-base font-semibold">
								{{ __("Give Complaint") }}
							</h2>

							<button
								type="button"
								class="text-sm text-gray-500"
								@click="closeForm"
							>
								{{ __("Cancel") }}
							</button>
						</div>

						<!-- Employee -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Employee") }}
							</label>

							<input
								v-model="form.employee_name"
								type="text"
								readonly
								class="w-full rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-sm text-gray-600"
								:placeholder="
									loadingEmployee
										? __('Loading...')
										: __('Employee')
								"
							/>
						</div>

						<!-- Reports To / L1 -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Reports To")
								}}
							</label>

							<input
								v-model="form.reports_to"
								type="text"
								readonly
								class="w-full rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-sm text-gray-600"
								:placeholder="
									loadingEmployee
										? __('Loading...')
										: __('Not configured')
								"
							/>
						</div>

						<!-- Complaint Approver / L2 (optional) -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Complaint Approver") }}
								<span class="text-xs font-normal text-gray-400">
									{{ __("(optional)") }}
								</span>
							</label>

							<input
								v-model="form.complaint_approver"
								type="text"
								readonly
								class="w-full rounded-lg border border-gray-300 bg-gray-100 px-3 py-2 text-sm text-gray-600"
								:placeholder="
									loadingEmployee
										? __('Loading...')
										: __('Not configured')
								"
							/>
						</div>

						<!-- Complaint Type -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Complaint Type") }}
								<span class="text-red-500">*</span>
							</label>

							<select
								v-model="form.complaint_type"
								class="w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-sm"
							>
								<option value="">
									{{ __("Select Complaint Type") }}
								</option>

								<option value="Workplace">
									{{ __("Workplace") }}
								</option>

								<option value="Salary / Payroll">
									{{ __("Salary / Payroll") }}
								</option>

								<option value="Leave">
									{{ __("Leave") }}
								</option>

								<option value="Attendance">
									{{ __("Attendance") }}
								</option>

								<option value="Manager / Supervisor">
									{{ __("Manager / Supervisor") }}
								</option>

								<option value="Colleague">
									{{ __("Colleague") }}
								</option>

								<option value="Facilities">
									{{ __("Facilities") }}
								</option>

								<option value="Other">
									{{ __("Other") }}
								</option>
							</select>
						</div>

						<!-- Subject -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Subject") }}
								<span class="text-red-500">*</span>
							</label>

							<input
								v-model="form.subject"
								type="text"
								class="w-full rounded-lg border border-gray-300 px-3 py-3 text-sm"
								:placeholder="__('Enter subject')"
							/>
						</div>

						<!-- Description -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Description") }}
								<span class="text-red-500">*</span>
							</label>

							<textarea
								v-model="form.description"
								rows="5"
								class="w-full rounded-lg border border-gray-300 px-3 py-3 text-sm"
								:placeholder="__('Describe your complaint...')"
							></textarea>
						</div>

						<!-- Supporting Document -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Supporting Document") }}
							</label>

							<input
								type="file"
								@change="handleFileChange"
								class="w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-sm"
							/>

							<p
								v-if="selectedFile"
								class="text-xs text-gray-500"
							>
								{{ selectedFile.name }}
							</p>
						</div>

						<!-- Date -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Date") }}
							</label>

							<input
								v-model="form.date"
								type="date"
								class="w-full rounded-lg border border-gray-300 bg-white px-3 py-3 text-sm"
							/>
						</div>

						<!-- Remarks -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Remarks") }}
							</label>

							<textarea
								v-model="form.remarks"
								rows="3"
								class="w-full rounded-lg border border-gray-300 px-3 py-3 text-sm"
								:placeholder="__('Enter remarks if required')"
							></textarea>
						</div>

						<!-- Submit -->
						<button
							type="button"
							class="w-full rounded-lg bg-gray-900 px-4 py-3 text-sm font-medium text-white disabled:opacity-50"
							:disabled="
								submitting ||
								loadingEmployee ||
								!form.employee ||
								!form.reports_to
							"
							@click="submitComplaint"
						>
							{{
								submitting
									? __("Submitting...")
									: __("Submit Complaint")
							}}
						</button>
					</div>
				</div>

				<!-- LOADING -->
				<div
					v-if="loading && !showForm"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<p class="text-gray-500">
						{{ __("Loading complaints...") }}
					</p>
				</div>

				<!-- NO COMPLAINT -->
				<div
					v-else-if="
						!showForm &&
						feedbackList.length === 0
					"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<p class="text-gray-500">
						{{ __("You have not submitted any complaints yet.") }}
					</p>
				</div>

				<!-- COMPLAINT LIST -->
				<div
					v-else-if="
						!showForm &&
						feedbackList.length > 0
					"
					class="flex flex-col gap-3"
				>
					<h2 class="text-base font-semibold">
						{{ __("My Complaints") }}
					</h2>

					<div
						v-for="item in feedbackList"
						:key="item.name"
						class="rounded-lg bg-white p-4 shadow-sm"
					>
						<div class="flex flex-col gap-3">
							<!-- Subject + Status -->
							<div
								class="flex items-start justify-between gap-3"
							>
								<div>
									<h3 class="text-base font-semibold">
										{{ item.subject }}
									</h3>

									<p
										v-if="item.complaint_type"
										class="mt-1 text-xs text-gray-500"
									>
										{{ item.complaint_type }}
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

							<!-- Employee -->
							<div v-if="item.employee">
								<p class="text-xs text-gray-500">
									{{ __("Employee") }}:
									{{ item.employee }}
								</p>
							</div>

							<!-- Approvers -->
							<div
								v-if="
									item.reports_to ||
									item.complaint_approver
								"
								class="flex flex-col gap-1"
							>
								<p
									v-if="item.reports_to"
									class="text-xs text-gray-500"
								>
									{{ __("Reports To") }}:
									{{ item.reports_to }}
								</p>

								<p
									v-if="item.complaint_approver"
									class="text-xs text-gray-500"
								>
									{{ __("Complaint Approver") }}:
									{{ item.complaint_approver }}
								</p>
							</div>

							<!-- Description -->
							<div v-if="item.description">
								<p
									class="whitespace-pre-line text-sm text-gray-600"
								>
									{{ stripHtml(item.description) }}
								</p>
							</div>

							<!-- Date -->
							<div v-if="item.date">
								<p class="text-xs text-gray-400">
									{{ __("Date") }}:
									{{ formatDate(item.date) }}
								</p>
							</div>

							<!-- Resolved On -->
							<div v-if="item.resolved_on">
								<p class="text-xs text-gray-400">
									{{ __("Resolved On") }}:
									{{ formatDate(item.resolved_on) }}
								</p>
							</div>

							<!-- Remarks -->
							<div v-if="item.remarks">
								<p class="text-xs text-gray-500">
									{{ __("Remarks") }}
								</p>

								<p
									class="mt-1 whitespace-pre-line text-sm"
								>
									{{ item.remarks }}
								</p>
							</div>

							<!-- Supporting Document -->
							<div
								v-if="item.supporting_document"
								class="pt-1"
							>
								<a
									:href="item.supporting_document"
									target="_blank"
									rel="noopener noreferrer"
									class="text-sm text-blue-600"
								>
									{{ __("View Supporting Document") }}
								</a>
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
import { useRouter } from "vue-router"

import BaseLayout from "@/components/BaseLayout.vue"

const __ = inject("$translate")
const router = useRouter()

const feedbackList = ref([])

const loading = ref(true)
const loadingEmployee = ref(false)
const submitting = ref(false)
const showForm = ref(false)
const errorMessage = ref("")

const selectedFile = ref(null)

const form = ref({
	employee: "",
	employee_name: "",
	reports_to: "",
	complaint_approver: "",
	complaint_type: "",
	subject: "",
	description: "",
	supporting_document: "",
	status: "",
	date: "",
	resolved_on: "",
	remarks: "",
})

const getToday = () => {
	const now = new Date()

	const pad = (number) =>
		String(number).padStart(2, "0")

	return `${now.getFullYear()}-${pad(
		now.getMonth() + 1
	)}-${pad(now.getDate())}`
}

const formatDate = (value) => {
	if (!value) return ""

	const date = new Date(
		value.includes(" ")
			? value.replace(" ", "T")
			: value
	)

	return date.toLocaleDateString()
}

const stripHtml = (value) => {
	if (!value) return ""

	const temp = document.createElement("div")

	temp.innerHTML = value

	return (
		temp.textContent ||
		temp.innerText ||
		""
	)
}

const getLoggedInUser = async () => {
	const response = await fetch(
		"/api/method/frappe.auth.get_logged_user"
	)

	if (!response.ok) {
		throw new Error(
			__(
				"Unable to identify the logged-in user."
			)
		)
	}

	const result = await response.json()

	if (!result.message) {
		throw new Error(
			__(
				"Unable to identify the logged-in user."
			)
		)
	}

	return result.message
}

const getEmployeeDetails = async () => {
	const user = await getLoggedInUser()

	const fields = JSON.stringify([
		"name",
		"user_id",
		"employee_name",
		"custom_complaint_approver",
		"custom_complaint_approver_l2",
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

const loadEmployeeDetails = async () => {
	loadingEmployee.value = true
	errorMessage.value = ""

	try {
		const employee =
			await getEmployeeDetails()

		form.value.employee = employee.name

		form.value.employee_name =
			employee.employee_name ||
			employee.name

		form.value.reports_to =
			employee.custom_complaint_approver ||
			""

		form.value.complaint_approver =
			employee.custom_complaint_approver_l2 ||
			""

		if (!form.value.reports_to) {
			throw new Error(
				__(
					"Complaint L1 approver is not configured for your Employee record."
				)
			)
		}

		// L2 (complaint_approver) is optional — some
		// employees only have an L1 approver configured.
		// No error thrown when it is blank.
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

const loadComplaints = async () => {
	loading.value = true
	errorMessage.value = ""

	try {
		const employee =
			await getEmployeeDetails()

		const fields = JSON.stringify([
			"name",
			"employee",
			"complaint_type",
			"subject",
			"description",
			"supporting_document",
			"status",
			"workflow_state",
			"date",
			"reports_to",
			"complaint_approver",
			"resolved_on",
			"remarks",
		])

		const filters = JSON.stringify([
			["employee", "=", employee.name],
		])

		const url =
			"/api/resource/Employee Complaint" +
			"?fields=" +
			encodeURIComponent(fields) +
			"&filters=" +
			encodeURIComponent(filters) +
			"&order_by=" +
			encodeURIComponent("date desc") +
			"&limit_page_length=100"

		const response = await fetch(url)

		const result = await response.json()

		if (!response.ok) {
			throw new Error(
				result?.exception ||
					result?.message ||
					__(
						"Unable to load complaints."
					)
			)
		}

		feedbackList.value =
			result.data || []
	} catch (error) {
		console.error(
			"Error loading complaints:",
			error
		)

		errorMessage.value =
			error.message ||
			__(
				"Unable to load complaints."
			)
	} finally {
		loading.value = false
	}
}

const openForm = async () => {
	errorMessage.value = ""

	selectedFile.value = null

	form.value = {
		employee: "",
		employee_name: "",
		reports_to: "",
		complaint_approver: "",
		complaint_type: "",
		subject: "",
		description: "",
		supporting_document: "",
		status: "",
		date: getToday(),
		resolved_on: "",
		remarks: "",
	}

	showForm.value = true

	await loadEmployeeDetails()
}

const handleFileChange = (event) => {
	const files = event.target.files

	if (!files || files.length === 0) {
		selectedFile.value = null
		return
	}

	selectedFile.value = files[0]
}

/*
 * Create Complaint
 * Then apply the workflow action:
 *
 * Open
 *   ↓ Submit
 * Pending L1 Approval
 */
const submitComplaint = async () => {
	errorMessage.value = ""

	if (!form.value.employee) {
		errorMessage.value = __(
			"Unable to identify your Employee record."
		)
		return
	}

	if (!form.value.reports_to) {
		errorMessage.value = __(
			"Complaint L1 approver is not configured."
		)
		return
	}

	// L2 (complaint_approver) is optional — no check here.

	if (!form.value.complaint_type) {
		errorMessage.value = __(
			"Please select a complaint type."
		)
		return
	}

	if (!form.value.subject.trim()) {
		errorMessage.value = __(
			"Please enter a subject."
		)
		return
	}

	if (!form.value.description.trim()) {
		errorMessage.value = __(
			"Please enter the complaint description."
		)
		return
	}

	submitting.value = true

	try {
		/*
		 * Step 1:
		 * Create the document in the workflow's
		 * initial state.
		 *
		 * IMPORTANT: "status" is a Select field that
		 * only allows "", "Open", "In Review",
		 * "Resolved", "Closed". Do NOT set it to
		 * "Submitted" here — that value is not a valid
		 * option and will raise a ValidationError at
		 * insert time. The workflow itself takes care
		 * of moving status forward once the "Submit"
		 * action is applied below.
		 */
		const doc = {
			doctype: "Employee Complaint",

			employee:
				form.value.employee,

			complaint_type:
				form.value.complaint_type,

			subject:
				form.value.subject.trim(),

			description:
				form.value.description.trim(),

			date:
				form.value.date ||
				getToday(),

			status: "Open",

			workflow_state: "Open",

			reports_to:
				form.value.reports_to,

			complaint_approver:
				form.value.complaint_approver ||
				"",

			remarks:
				form.value.remarks
					? form.value.remarks.trim()
					: "",
		}

		console.log(
			"Creating Employee Complaint:",
			doc
		)

		const response = await fetch(
			"/api/resource/Employee Complaint",
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
				"Create Complaint Error:",
				result
			)

			throw new Error(
				result?.exception ||
					result?.message ||
					__(
						"Unable to create complaint."
					)
			)
		}

		/*
		 * IMPORTANT:
		 * Use the complete document returned
		 * by Frappe.
		 */
		const complaint =
			result.data

		console.log(
			"Complaint created:",
			complaint
		)

		/*
		 * Step 2:
		 * Upload supporting document.
		 */
		if (selectedFile.value) {
			await uploadSupportingDocument(
				complaint.name,
				selectedFile.value
			)
		}

		/*
		 * Step 3:
		 * Apply workflow action using the
		 * complete complaint document.
		 */
		const workflowResponse =
			await fetch(
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
						doc: complaint,
						action: "Submit",
					}),
				}
			)

		const workflowResult =
			await workflowResponse.json()

		if (!workflowResponse.ok) {
			console.error(
				"Workflow Submit Error:",
				workflowResult
			)

			throw new Error(
				workflowResult?.exception ||
					workflowResult?.message ||
					__(
						"Complaint was created, but could not be submitted for approval."
					)
			)
		}

		console.log(
			"Complaint submitted to workflow:",
			workflowResult
		)

		/*
		 * Reset form
		 */
		form.value = {
			employee: "",
			employee_name: "",
			reports_to: "",
			complaint_approver: "",
			complaint_type: "",
			subject: "",
			description: "",
			supporting_document: "",
			status: "",
			date: "",
			resolved_on: "",
			remarks: "",
		}

		selectedFile.value = null

		showForm.value = false

		await loadComplaints()
	} catch (error) {
		console.error(
			"Error submitting complaint:",
			error
		)

		errorMessage.value =
			error.message ||
			__(
				"Unable to submit complaint."
			)
	} finally {
		submitting.value = false
	}
}

const uploadSupportingDocument = async (
	docname,
	file
) => {
	const formData = new FormData()

	formData.append(
		"file",
		file
	)

	formData.append(
		"doctype",
		"Employee Complaint"
	)

	formData.append(
		"docname",
		docname
	)

	formData.append(
		"is_private",
		"1"
	)

	const response = await fetch(
		"/api/method/upload_file",
		{
			method: "POST",

			headers: {
				"X-Frappe-CSRF-Token":
					window.frappe?.csrf_token ||
					window.csrf_token ||
					"fetch",
			},

			body: formData,
		}
	)

	const result =
		await response.json()

	if (!response.ok) {
		console.error(
			"File Upload Error:",
			result
		)

		throw new Error(
			result?.exception ||
				result?.message ||
				__(
					"Unable to upload supporting document."
				)
		)
	}

	return result
}

const closeForm = () => {
	showForm.value = false

	errorMessage.value = ""

	selectedFile.value = null

	form.value = {
		employee: "",
		employee_name: "",
		reports_to: "",
		complaint_approver: "",
		complaint_type: "",
		subject: "",
		description: "",
		supporting_document: "",
		status: "",
		date: "",
		resolved_on: "",
		remarks: "",
	}
}

const goHome = () => {
	router.push("/home")
}

onMounted(() => {
	loadComplaints()
})
</script>

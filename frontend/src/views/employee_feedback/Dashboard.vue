<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col gap-4 p-4">
				<!-- Header -->
				<div class="flex items-center justify-between">
					<h1 class="text-xl font-semibold">
						{{ __("Feedback") }}
					</h1>

					<button
						type="button"
						class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white"
						@click="showForm = true"
					>
						{{ __("Add Feedback") }}
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

				<!-- Feedback Form -->
				<div
					v-if="showForm"
					class="rounded-lg bg-white p-4 shadow-sm"
				>
					<div class="flex flex-col gap-4">
						<div class="flex items-center justify-between">
							<h2 class="text-base font-semibold">
								{{ __("Give Feedback") }}
							</h2>

							<button
								type="button"
								class="text-sm text-gray-500"
								@click="closeForm"
							>
								{{ __("Cancel") }}
							</button>
						</div>

						<!-- Feedback Type -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Feedback Type") }}
							</label>

							<select
								v-model="form.feedback_type"
								class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
							>
								<option value="">
									{{ __("Select Feedback Type") }}
								</option>

								<option value="General">
									{{ __("General") }}
								</option>

								<option value="Suggestion">
									{{ __("Suggestion") }}
								</option>

								<option value="Work Environment">
									{{ __("Work Environment") }}
								</option>

								<option value="Management">
									{{ __("Management") }}
								</option>

								<option value="Salary">
									{{ __("Salary") }}
								</option>

								<option value="Leave">
									{{ __("Leave") }}
								</option>

								<option value="Attendance">
									{{ __("Attendance") }}
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
							</label>

							<input
								v-model="form.subject"
								type="text"
								class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
								:placeholder="__('Enter subject')"
							/>
						</div>

						<!-- Feedback -->
						<div class="flex flex-col gap-1">
							<label class="text-sm font-medium">
								{{ __("Feedback") }}
							</label>

							<textarea
								v-model="form.feedback"
								rows="5"
								class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
								:placeholder="__('Write your feedback here...')"
							></textarea>
						</div>

						<!-- Submit -->
						<button
							type="button"
							class="w-full rounded-lg bg-gray-900 px-4 py-3 text-sm font-medium text-white disabled:opacity-50"
							:disabled="submitting"
							@click="submitFeedback"
						>
							{{
								submitting
									? __("Submitting...")
									: __("Submit Feedback")
							}}
						</button>
					</div>
				</div>

				<!-- Loading -->
				<div
					v-if="loading"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<p class="text-gray-500">
						{{ __("Loading feedback...") }}
					</p>
				</div>

				<!-- No Feedback -->
				<div
					v-else-if="feedbackList.length === 0 && !showForm"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<p class="text-gray-500">
						{{ __("You have not submitted any feedback yet.") }}
					</p>
				</div>

				<!-- Feedback List -->
				<div
					v-else-if="feedbackList.length > 0"
					class="flex flex-col gap-3"
				>
					<h2 class="text-base font-semibold">
						{{ __("My Feedback") }}
					</h2>

					<div
						v-for="item in feedbackList"
						:key="item.name"
						class="rounded-lg bg-white p-4 shadow-sm"
					>
						<div class="flex flex-col gap-3">
							<!-- Subject and Status -->
							<div
								class="flex items-start justify-between gap-3"
							>
								<div>
									<h3 class="text-base font-semibold">
										{{ item.subject }}
									</h3>

									<p
										v-if="item.feedback_type"
										class="mt-1 text-xs text-gray-500"
									>
										{{ item.feedback_type }}
									</p>
								</div>

								<span
									v-if="item.status"
									class="rounded-full bg-gray-100 px-3 py-1 text-xs"
								>
									{{ item.status }}
								</span>
							</div>

							<!-- Feedback Text -->
							<div v-if="item.feedback">
								<p
									class="whitespace-pre-line text-sm text-gray-600"
								>
									{{ stripHtml(item.feedback) }}
								</p>
							</div>

							<!-- Submitted Date -->
							<div v-if="item.submitted_on">
								<p class="text-xs text-gray-400">
									{{ __("Submitted On") }}:
									{{ formatDateTime(item.submitted_on) }}
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

const feedbackList = ref([])

const loading = ref(true)
const submitting = ref(false)
const showForm = ref(false)
const errorMessage = ref("")

const form = ref({
	feedback_type: "",
	subject: "",
	feedback: "",
})

const formatDateTime = (value) => {
	if (!value) return ""

	return new Date(value.replace(" ", "T")).toLocaleString()
}

const stripHtml = (value) => {
	if (!value) return ""

	const temp = document.createElement("div")
	temp.innerHTML = value

	return temp.textContent || temp.innerText || ""
}

const getLoggedInUser = async () => {
	const response = await fetch(
		"/api/method/frappe.auth.get_logged_user"
	)

	if (!response.ok) {
		throw new Error(__("Unable to identify the logged-in user."))
	}

	const result = await response.json()

	if (!result.message) {
		throw new Error(__("Unable to identify the logged-in user."))
	}

	return result.message
}

const getEmployee = async () => {
	const user = await getLoggedInUser()

	const fields = JSON.stringify([
		"name",
		"user_id",
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

	if (!response.ok) {
		throw new Error(__("Unable to find your Employee record."))
	}

	const result = await response.json()

	if (!result.data || result.data.length === 0) {
		throw new Error(
			__("No Employee record is linked to your login user.")
		)
	}

	return result.data[0].name
}

const loadFeedback = async () => {
	loading.value = true
	errorMessage.value = ""

	try {
		const employee = await getEmployee()

		const fields = JSON.stringify([
			"name",
			"employee",
			"feedback_type",
			"subject",
			"feedback",
			"submitted_on",
			"status",
			"remarks",
		])

		const filters = JSON.stringify([
			["employee", "=", employee],
		])

		const url =
			"/api/resource/Employee Feedback" +
			"?fields=" +
			encodeURIComponent(fields) +
			"&filters=" +
			encodeURIComponent(filters) +
			"&order_by=" +
			encodeURIComponent("submitted_on desc") +
			"&limit_page_length=100"

		const response = await fetch(url)

		const result = await response.json()

		if (!response.ok) {
			console.error("Feedback API Error:", result)

			throw new Error(
				result?.exception ||
					result?.message ||
					__("Unable to load feedback.")
			)
		}

		feedbackList.value = result.data || []
	} catch (error) {
		console.error("Error loading feedback:", error)

		errorMessage.value =
			error.message || __("Unable to load feedback.")
	} finally {
		loading.value = false
	}
}

const submitFeedback = async () => {
	errorMessage.value = ""

	if (!form.value.feedback_type) {
		errorMessage.value = __("Please select a feedback type.")
		return
	}

	if (!form.value.subject.trim()) {
		errorMessage.value = __("Please enter a subject.")
		return
	}

	if (!form.value.feedback.trim()) {
		errorMessage.value = __("Please enter your feedback.")
		return
	}

	submitting.value = true

	try {
		const employee = await getEmployee()

		const doc = {
			doctype: "Employee Feedback",
			employee: employee,
			feedback_type: form.value.feedback_type,
			subject: form.value.subject.trim(),
			feedback: form.value.feedback.trim(),
			submitted_on: getCurrentDateTime(),
			status: "Submitted",
		}

		const response = await fetch(
			"/api/resource/Employee Feedback",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token":
						window.frappe?.csrf_token ||
						window.csrf_token ||
						"fetch",
				},
				body: JSON.stringify(doc),
			}
		)

		const result = await response.json()

		if (!response.ok) {
			console.error("Create Feedback Error:", result)

			throw new Error(
				result?.exception ||
					result?.message ||
					__("Unable to submit feedback.")
			)
		}

		console.log("Feedback created:", result.data)

		form.value = {
			feedback_type: "",
			subject: "",
			feedback: "",
		}

		showForm.value = false

		await loadFeedback()
	} catch (error) {
		console.error("Error submitting feedback:", error)

		errorMessage.value =
			error.message || __("Unable to submit feedback.")
	} finally {
		submitting.value = false
	}
}

const getCurrentDateTime = () => {
	const now = new Date()

	const pad = (number) => String(number).padStart(2, "0")

	return (
		`${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(
			now.getDate()
		)}` +
		` ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(
			now.getSeconds()
		)}`
	)
}

const closeForm = () => {
	showForm.value = false

	form.value = {
		feedback_type: "",
		subject: "",
		feedback: "",
	}
}

onMounted(() => {
	loadFeedback()
})
</script>

<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col gap-4 p-4">
				<!-- Page Header -->
				<div>
					<h1 class="text-xl font-semibold">
						{{ __("My Tasks") }}
					</h1>
				</div>

				<!-- Loading -->
				<div
					v-if="loading"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<p class="text-gray-500">
						{{ __("Loading tasks...") }}
					</p>
				</div>

				<!-- Error -->
				<div
					v-else-if="errorMessage"
					class="rounded-lg bg-white p-4 shadow-sm"
				>
					<p class="text-sm text-red-500">
						{{ errorMessage }}
					</p>
				</div>

				<!-- No Tasks -->
				<div
					v-else-if="tasks.length === 0"
					class="rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<div class="flex flex-col items-center gap-2">
						<p class="text-gray-500">
							{{ __("No tasks assigned to you.") }}
						</p>

						<p class="text-xs text-gray-400">
							{{ __("New tasks assigned to you will appear here.") }}
						</p>
					</div>
				</div>

				<!-- Task List -->
				<div v-else class="flex flex-col gap-3">
					<div
						v-for="task in tasks"
						:key="task.name"
						class="rounded-lg bg-white p-4 shadow-sm"
					>
						<div class="flex flex-col gap-3">
							<!-- Title -->
							<div
								class="flex items-start justify-between gap-3"
							>
								<h2 class="text-base font-semibold">
									{{ task.task_title }}
								</h2>

								<span
									v-if="task.priority"
									class="rounded-full bg-gray-100 px-2 py-1 text-xs"
								>
									{{ task.priority }}
								</span>
							</div>

							<!-- Description -->
							<div v-if="task.description">
								<p
									class="whitespace-pre-line text-sm text-gray-600"
								>
									{{ task.description }}
								</p>
							</div>

							<!-- Task Details -->
							<div class="flex flex-col gap-1 text-sm">
								<div v-if="task.assigned_date">
									<span class="text-gray-500">
										{{ __("Assigned Date") }}:
									</span>

									<span class="ml-1">
										{{ formatDate(task.assigned_date) }}
									</span>
								</div>

								<div v-if="task.due_date">
									<span class="text-gray-500">
										{{ __("Due Date") }}:
									</span>

									<span class="ml-1">
										{{ formatDate(task.due_date) }}
									</span>
								</div>

								<div v-if="task.assigned_by">
									<span class="text-gray-500">
										{{ __("Assigned By") }}:
									</span>

									<span class="ml-1">
										{{ task.assigned_by }}
									</span>
								</div>
							</div>

							<!-- Current Status -->
							<div
								class="flex items-center justify-between border-t pt-3"
							>
								<span class="text-sm text-gray-500">
									{{ __("Status") }}
								</span>

								<span
									class="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium"
								>
									{{ task.status || __("Assigned") }}
								</span>
							</div>

							<!-- Employee Remarks -->
							<div v-if="task.employee_remarks">
								<p class="text-xs text-gray-500">
									{{ __("Remarks") }}
								</p>

								<p
									class="mt-1 whitespace-pre-line text-sm"
								>
									{{ task.employee_remarks }}
								</p>
							</div>

							<!-- Completion Date -->
							<div v-if="task.completion_date">
								<span class="text-sm text-gray-500">
									{{ __("Completed On") }}:
								</span>

								<span class="ml-1 text-sm">
									{{ formatDate(task.completion_date) }}
								</span>
							</div>

							<!-- Update Button -->
							<button
								type="button"
								class="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium"
								@click="openEdit(task)"
							>
								{{ __("Update Task") }}
							</button>

							<!-- Edit Section -->
							<div
								v-if="editingTask === task.name"
								class="mt-2 flex flex-col gap-4 rounded-lg bg-gray-50 p-4"
							>
								<!-- Edit Header -->
								<div
									class="flex items-center justify-between"
								>
									<h3 class="text-sm font-semibold">
										{{ __("Update Task") }}
									</h3>

									<button
										type="button"
										class="text-sm text-gray-500"
										@click="cancelEdit"
									>
										{{ __("Cancel") }}
									</button>
								</div>

								<!-- Status -->
								<div class="flex flex-col gap-1">
									<label class="text-sm font-medium">
										{{ __("Status") }}
									</label>

									<select
										v-model="editForm.status"
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm"
									>
										<option value="Assigned">
											{{ __("Assigned") }}
										</option>

										<option value="In Progress">
											{{ __("In Progress") }}
										</option>

										<option value="Completed">
											{{ __("Completed") }}
										</option>
									</select>
								</div>

								<!-- Employee Remarks -->
								<div class="flex flex-col gap-1">
									<label class="text-sm font-medium">
										{{ __("Remarks") }}
									</label>

									<textarea
										v-model="editForm.employee_remarks"
										rows="4"
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm"
										:placeholder="
											__('Enter your remarks...')
										"
									></textarea>
								</div>

								<!-- Save Button -->
								<button
									type="button"
									class="w-full rounded-lg bg-gray-900 px-4 py-3 text-sm font-medium text-white disabled:opacity-50"
									:disabled="saving"
									@click="saveTask(task)"
								>
									{{
										saving
											? __("Saving...")
											: __("Save Changes")
									}}
								</button>
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

const tasks = ref([])

const loading = ref(true)
const saving = ref(false)

const errorMessage = ref("")

const editingTask = ref(null)

const editForm = ref({
	status: "",
	employee_remarks: "",
})

const formatDate = (date) => {
	if (!date) return ""

	const value = String(date)

	return new Date(
		value.includes("T") ? value : `${value}T00:00:00`
	).toLocaleDateString()
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

	const filters = JSON.stringify([
		["user_id", "=", user],
	])

	const fields = JSON.stringify([
		"name",
		"user_id",
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
		throw new Error(__("Unable to find the employee record."))
	}

	const result = await response.json()

	if (!result.data || result.data.length === 0) {
		throw new Error(
			__("No Employee record is linked to your login user.")
		)
	}

	return result.data[0].name
}

const loadTasks = async () => {
	loading.value = true
	errorMessage.value = ""

	try {
		const employee = await getEmployee()

		console.log("Logged-in Employee:", employee)

		const fields = JSON.stringify([
			"name",
			"task_title",
			"employee",
			"description",
			"assigned_by",
			"assigned_date",
			"due_date",
			"priority",
			"status",
			"employee_remarks",
			"completion_date",
		])

		const filters = JSON.stringify([
			["employee", "=", employee],
		])

		const url =
			"/api/resource/Employee Task" +
			"?fields=" +
			encodeURIComponent(fields) +
			"&filters=" +
			encodeURIComponent(filters) +
			"&order_by=" +
			encodeURIComponent("due_date asc") +
			"&limit_page_length=100"

		const response = await fetch(url)

		const result = await response.json()

		if (!response.ok) {
			console.error("Employee Task API Error:", result)

			throw new Error(
				result?.exception ||
					result?.message ||
					__("Unable to load tasks.")
			)
		}

		console.log("Employee Tasks:", result.data)

		tasks.value = result.data || []
	} catch (error) {
		console.error("Error loading Employee Tasks:", error)

		errorMessage.value =
			error.message || __("Unable to load tasks.")
	} finally {
		loading.value = false
	}
}

const openEdit = (task) => {
	editingTask.value = task.name

	editForm.value = {
		status: task.status || "Assigned",
		employee_remarks: task.employee_remarks || "",
	}

	errorMessage.value = ""
}

const cancelEdit = () => {
	editingTask.value = null

	editForm.value = {
		status: "",
		employee_remarks: "",
	}

	errorMessage.value = ""
}

const getTodayDate = () => {
	const now = new Date()

	const year = now.getFullYear()
	const month = String(now.getMonth() + 1).padStart(2, "0")
	const day = String(now.getDate()).padStart(2, "0")

	return `${year}-${month}-${day}`
}

const getCSRFToken = () => {
	return (
		window.frappe?.csrf_token ||
		window.csrf_token ||
		"fetch"
	)
}

const saveTask = async (task) => {
	saving.value = true
	errorMessage.value = ""

	try {
		const updateData = {
			status: editForm.value.status,
			employee_remarks: editForm.value.employee_remarks,
		}

		// Automatically set completion date
		// when employee marks the task as Completed.
		if (editForm.value.status === "Completed") {
			updateData.completion_date =
				task.completion_date || getTodayDate()
		} else {
			updateData.completion_date = null
		}

		const response = await fetch(
			`/api/resource/Employee Task/${encodeURIComponent(
				task.name
			)}`,
			{
				method: "PUT",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": getCSRFToken(),
				},
				body: JSON.stringify(updateData),
			}
		)

		const result = await response.json()

		if (!response.ok) {
			console.error("Update Employee Task Error:", result)

			throw new Error(
				result?.exception ||
					result?.message ||
					__("Unable to update task.")
			)
		}

		console.log("Task updated successfully:", result.data)

		// Close edit section
		editingTask.value = null

		editForm.value = {
			status: "",
			employee_remarks: "",
		}

		// Reload task list
		await loadTasks()
	} catch (error) {
		console.error("Error updating Employee Task:", error)

		errorMessage.value =
			error.message || __("Unable to update task.")
	} finally {
		saving.value = false
	}
}

onMounted(() => {
	loadTasks()
})
</script>

<template>
	<BaseLayout :pageTitle="__('My Tasks')">
		<template #body>
			<!--
				Employee Task = one task sheet per week (arown app, arown/employee_task.py).
				Each sheet holds many task rows; the employee updates each row (status, remarks, attachment).
				A task can only be Completed with an attachment (proof of work).
			-->
			<div class="flex flex-col gap-4 p-4 pb-24">
				<!-- Filter -->
				<div class="flex rounded-lg bg-gray-100 p-1 text-sm">
					<button
						v-for="option in filterOptions"
						:key="option.value"
						type="button"
						class="flex-1 rounded-md px-3 py-1.5 font-medium"
						:class="
							filter === option.value
								? 'bg-white text-gray-900 shadow-sm'
								: 'text-gray-500'
						"
						@click="setFilter(option.value)"
					>
						{{ option.label }}
					</button>
				</div>

				<!-- Error -->
				<div
					v-if="errorMessage"
					class="rounded-lg bg-red-50 p-3 text-sm text-red-600"
				>
					{{ errorMessage }}
				</div>

				<!-- Loading -->
				<div
					v-if="loading"
					class="rounded-lg bg-white p-6 text-center text-gray-500 shadow-sm"
				>
					{{ __("Loading tasks...") }}
				</div>

				<!-- No Tasks -->
				<div
					v-else-if="sheets.length === 0"
					class="flex flex-col items-center gap-2 rounded-lg bg-white p-6 text-center shadow-sm"
				>
					<FeatherIcon name="check-square" class="h-8 w-8 text-gray-300" />
					<p class="text-gray-500">{{ emptyText }}</p>
					<p class="text-xs text-gray-400">
						{{ __("Tasks assigned to you each week will appear here.") }}
					</p>
				</div>

				<!-- Weekly Sheets -->
				<template v-else>
				<div
					v-for="sheet in sheets"
					:key="sheet.name"
					class="rounded-lg bg-white shadow-sm"
				>
					<!-- Sheet Header -->
					<button
						type="button"
						class="flex w-full flex-col gap-2 p-4 text-left"
						@click="toggleSheet(sheet.name)"
					>
						<div class="flex w-full items-start justify-between gap-3">
							<div class="flex flex-col">
								<span class="text-base font-semibold text-gray-900">
									{{ sheet.week }} · {{ sheet.quarter }}
								</span>
								<span class="text-xs text-gray-500">
									{{ formatDate(sheet.from_date) }} –
									{{ formatDate(sheet.to_date) }}
								</span>
							</div>
							<div class="flex items-center gap-2">
								<span
									class="rounded-full px-2 py-1 text-xs font-medium"
									:class="statusClass(sheet.status)"
								>
									{{ __(sheet.status) }}
								</span>
								<FeatherIcon
									:name="isOpen(sheet.name) ? 'chevron-up' : 'chevron-down'"
									class="h-4 w-4 text-gray-500"
								/>
							</div>
						</div>

						<!-- Progress -->
						<div class="flex w-full items-center gap-2">
							<div class="h-1.5 flex-1 rounded-full bg-gray-100">
								<div
									class="h-1.5 rounded-full bg-green-500"
									:style="{ width: percent(sheet.progress) + '%' }"
								></div>
							</div>
							<span class="text-xs text-gray-500">
								{{ percent(sheet.progress) }}% ·
								{{ sheet.completed_tasks }}/{{ sheet.total_tasks }}
								{{ __("done") }}
							</span>
						</div>
					</button>

					<div v-if="isOpen(sheet.name)" class="flex flex-col gap-3 border-t px-4 pb-4 pt-3">
						<!-- Sheet Details -->
						<div class="flex flex-col gap-1 text-sm">
							<div v-if="sheet.assigned_by_name">
								<span class="text-gray-500">{{ __("Assigned By") }}:</span>
								<span class="ml-1">{{ sheet.assigned_by_name }}</span>
							</div>
							<div v-if="sheet.description">
								<p class="text-gray-500">{{ __("Instructions") }}</p>
								<p class="whitespace-pre-line text-gray-700">
									{{ sheet.description }}
								</p>
							</div>
							<a
								v-if="sheet.attachment"
								:href="sheet.attachment"
								target="_blank"
								class="mt-1 flex items-center gap-2 rounded-lg border px-3 py-2 text-gray-700"
							>
								<FeatherIcon name="file-text" class="h-4 w-4" />
								<span class="truncate">
									{{ __("Task Document") }}: {{ fileName(sheet.attachment) }}
								</span>
							</a>
						</div>

						<!-- Task Rows -->
						<div
							v-for="task in sheet.tasks"
							:key="task.name"
							class="flex flex-col gap-2 rounded-lg border p-3"
							:class="task.status === 'Cancelled' ? 'opacity-60' : ''"
						>
							<div class="flex items-start justify-between gap-2">
								<h3 class="text-sm font-semibold text-gray-900">
									<span class="text-gray-400">#{{ task.task_no || task.idx }}</span>
									{{ task.task_title }}
								</h3>
								<span
									class="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium"
									:class="statusClass(task.status)"
								>
									{{ __(task.status) }}
								</span>
							</div>

							<p
								v-if="task.description"
								class="whitespace-pre-line text-sm text-gray-600"
							>
								{{ task.description }}
							</p>

							<div class="flex flex-wrap gap-x-4 gap-y-1 text-xs">
								<span v-if="task.due_date" :class="isOverdue(task) ? 'text-red-600' : 'text-gray-500'">
									{{ __("Due") }}: {{ formatDate(task.due_date) }}
								</span>
								<span v-if="task.priority" class="text-gray-500">
									{{ __("Priority") }}: {{ __(task.priority) }}
								</span>
								<span v-if="task.completion_date" class="text-gray-500">
									{{ __("Completed On") }}: {{ formatDate(task.completion_date) }}
								</span>
							</div>

							<div
								v-if="task.status !== 'Cancelled'"
								class="flex items-center gap-2"
							>
								<div class="h-1 flex-1 rounded-full bg-gray-100">
									<div
										class="h-1 rounded-full"
										:class="task.status === 'Completed' ? 'bg-green-500' : 'bg-blue-500'"
										:style="{ width: percent(task.progress) + '%' }"
									></div>
								</div>
								<span class="w-9 text-right text-xs text-gray-500">
									{{ percent(task.progress) }}%
								</span>
							</div>

							<a
								v-if="task.attachment"
								:href="task.attachment"
								target="_blank"
								class="flex items-center gap-1 text-xs text-blue-600"
							>
								<FeatherIcon name="paperclip" class="h-3 w-3" />
								<span class="truncate">{{ fileName(task.attachment) }}</span>
							</a>

							<div v-if="task.employee_remarks" class="text-xs">
								<span class="text-gray-500">{{ __("Remarks") }}:</span>
								<span class="ml-1 whitespace-pre-line text-gray-700">{{ task.employee_remarks }}</span>
							</div>

							<!-- Update -->
							<button
								v-if="task.status !== 'Cancelled' && editingRow !== task.name"
								type="button"
								class="mt-1 w-full rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium"
								@click="openEdit(task)"
							>
								{{ __("Update Task") }}
							</button>

							<div
								v-if="editingRow === task.name"
								class="mt-1 flex flex-col gap-3 rounded-lg bg-gray-50 p-3"
							>
								<div class="flex flex-col gap-1">
									<label class="text-sm font-medium">{{ __("Status") }}</label>
									<select
										v-model="editForm.status"
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm"
										@change="onStatusChange"
									>
										<option v-for="s in employeeStatuses" :key="s" :value="s">
											{{ __(s) }}
										</option>
									</select>
								</div>

								<div class="flex flex-col gap-1">
									<label class="flex justify-between text-sm font-medium">
										<span>{{ __("Progress") }}</span>
										<span class="text-gray-600">{{ editForm.progress }}%</span>
									</label>
									<input
										v-model.number="editForm.progress"
										type="range"
										min="0"
										max="100"
										step="10"
										class="w-full accent-gray-900"
										:disabled="editForm.status === 'Completed'"
										@input="onProgressChange"
									/>
								</div>

								<div class="flex flex-col gap-1">
									<label class="text-sm font-medium">
										{{ __("Attachment") }}
										<span v-if="editForm.status === 'Completed'" class="text-red-500">*</span>
									</label>
									<p
										v-if="task.attachment && !editForm.file"
										class="flex items-center gap-1 text-xs text-gray-600"
									>
										<FeatherIcon name="paperclip" class="h-3 w-3" />
										{{ fileName(task.attachment) }}
										<span class="text-gray-400">({{ __("choose a file to replace") }})</span>
									</p>
									<input
										:key="fileInputKey"
										type="file"
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm"
										@change="onFileSelect"
									/>
									<p class="text-xs text-gray-400">
										{{ __("Required to mark the task Completed.") }}
									</p>
								</div>

								<div class="flex flex-col gap-1">
									<label class="text-sm font-medium">{{ __("Remarks") }}</label>
									<textarea
										v-model="editForm.employee_remarks"
										rows="3"
										class="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm"
										:placeholder="__('Enter your remarks...')"
									></textarea>
								</div>

								<p v-if="editError" class="text-sm text-red-600">{{ editError }}</p>

								<div class="flex gap-2">
									<button
										type="button"
										class="flex-1 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium"
										:disabled="saving"
										@click="cancelEdit"
									>
										{{ __("Cancel") }}
									</button>
									<button
										type="button"
										class="flex-1 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-medium text-white disabled:opacity-50"
										:disabled="saving"
										@click="saveTask(sheet, task)"
									>
										{{ saving ? __("Saving...") : __("Save") }}
									</button>
								</div>
							</div>
						</div>
					</div>
				</div>
				</template>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { computed, inject, onMounted, ref } from "vue"
import { FeatherIcon } from "frappe-ui"

import BaseLayout from "@/components/BaseLayout.vue"

const __ = inject("$translate")

const API = "/api/method/arown.employee_task"
const employeeStatuses = ["Assigned", "In Progress", "Completed"]
const filterOptions = [
	{ value: "Open", label: __("Open") },
	{ value: "Completed", label: __("Completed") },
	{ value: "", label: __("All") },
]

const sheets = ref([])
const filter = ref("Open")
const loading = ref(true)
const errorMessage = ref("")
const openSheets = ref(new Set())

const editingRow = ref(null)
const editForm = ref({ status: "", employee_remarks: "", file: null, progress: 0 })
const editError = ref("")
const saving = ref(false)
const fileInputKey = ref(0)

const emptyText = computed(() =>
	filter.value === "Completed"
		? __("No completed tasks yet.")
		: filter.value === "Open"
			? __("No open tasks. Well done!")
			: __("No tasks assigned to you.")
)

const csrfToken = () => window.frappe?.csrf_token || window.csrf_token || "fetch"

// Frappe error response -> readable message
const getErrorMessage = (result, fallback) => {
	try {
		if (result?._server_messages) {
			const messages = JSON.parse(result._server_messages).map((m) => {
				const parsed = typeof m === "string" ? JSON.parse(m) : m
				return parsed.message || parsed
			})
			const text = messages.join(" ").replace(/<[^>]+>/g, "")
			if (text) return text
		}
	} catch (e) {
		// fall through
	}
	if (result?.exception) return String(result.exception).split(":").slice(1).join(":").trim() || fallback
	return fallback
}

const formatDate = (date) => {
	if (!date) return ""
	const value = String(date)
	return new Date(value.includes("T") ? value : `${value}T00:00:00`).toLocaleDateString()
}

const todayString = () => {
	const now = new Date()
	return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`
}

const isOverdue = (task) =>
	task.due_date && !["Completed", "Cancelled"].includes(task.status) && String(task.due_date) < todayString()

const fileName = (url) => decodeURIComponent(String(url || "").split("/").pop())

const percent = (value) => Math.round(Number(value) || 0)

const statusClass = (status) =>
	({
		Completed: "bg-green-100 text-green-700",
		"In Progress": "bg-blue-100 text-blue-700",
		Cancelled: "bg-gray-100 text-gray-500",
	})[status] || "bg-orange-100 text-orange-700"

const isOpen = (name) => openSheets.value.has(name)

const toggleSheet = (name) => {
	const next = new Set(openSheets.value)
	next.has(name) ? next.delete(name) : next.add(name)
	openSheets.value = next
}

const loadTasks = async () => {
	loading.value = true
	errorMessage.value = ""
	try {
		const query = filter.value ? `?status=${encodeURIComponent(filter.value)}` : ""
		const response = await fetch(`${API}.get_my_tasks${query}`)
		const result = await response.json()
		if (!response.ok) throw new Error(getErrorMessage(result, __("Unable to load tasks.")))

		sheets.value = result.message || []
		// the newest sheet starts expanded
		if (sheets.value.length && !sheets.value.some((s) => openSheets.value.has(s.name))) {
			openSheets.value = new Set([sheets.value[0].name])
		}
	} catch (error) {
		errorMessage.value = error.message || __("Unable to load tasks.")
	} finally {
		loading.value = false
	}
}

const setFilter = (value) => {
	if (filter.value === value) return
	filter.value = value
	cancelEdit()
	loadTasks()
}

const openEdit = (task) => {
	editingRow.value = task.name
	editForm.value = {
		status: employeeStatuses.includes(task.status) ? task.status : "Assigned",
		employee_remarks: task.employee_remarks || "",
		file: null,
		progress: percent(task.progress),
	}
	editError.value = ""
	fileInputKey.value++
}

const cancelEdit = () => {
	editingRow.value = null
	editForm.value = { status: "", employee_remarks: "", file: null, progress: 0 }
	editError.value = ""
}

// same rules as the server: Completed = 100%, progress above 0 = In Progress
const onStatusChange = () => {
	if (editForm.value.status === "Completed") editForm.value.progress = 100
}

const onProgressChange = () => {
	if (editForm.value.progress > 0 && editForm.value.status === "Assigned") editForm.value.status = "In Progress"
}

const onFileSelect = (event) => {
	editForm.value.file = event.target.files?.[0] || null
}

const saveTask = async (sheet, task) => {
	editError.value = ""
	if (editForm.value.status === "Completed" && !editForm.value.file && !task.attachment) {
		editError.value = __("Attach a file before marking the task Completed.")
		return
	}

	saving.value = true
	try {
		const formData = new FormData()
		formData.append("task", sheet.name)
		formData.append("row", task.name)
		formData.append("status", editForm.value.status)
		formData.append("employee_remarks", editForm.value.employee_remarks || "")
		formData.append("progress", String(editForm.value.progress ?? 0))
		if (editForm.value.file) formData.append("file", editForm.value.file, editForm.value.file.name)

		const response = await fetch(`${API}.update_task`, {
			method: "POST",
			headers: { "X-Frappe-CSRF-Token": csrfToken() },
			body: formData,
		})
		const result = await response.json()
		if (!response.ok) throw new Error(getErrorMessage(result, __("Unable to update task.")))

		cancelEdit()
		await loadTasks()
	} catch (error) {
		editError.value = error.message || __("Unable to update task.")
	} finally {
		saving.value = false
	}
}

onMounted(loadTasks)
</script>

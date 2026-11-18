<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col gap-4 p-4 pb-24">
				<!-- Header -->
				<div class="flex items-center justify-between gap-2">
					<div class="flex items-center gap-2">
						<button type="button" class="flex h-9 w-9 items-center justify-center rounded-full" @click="back">
							<span class="text-3xl leading-none">‹</span>
						</button>
						<h1 class="text-xl font-semibold">{{ showForm ? text.newTitle : text.title }}</h1>
					</div>
					<button
						v-if="!showForm"
						type="button"
						class="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white"
						@click="openForm"
					>
						{{ text.add }}
					</button>
				</div>

				<div v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-600">{{ error }}</div>

				<!-- ===================== NEW TICKET FORM ===================== -->
				<div v-if="showForm" class="flex flex-col gap-4 rounded-lg bg-white p-4 shadow-sm">
					<!-- feedback type -->
					<div v-if="isFeedback" class="flex flex-col gap-1">
						<label class="text-sm font-medium">{{ __("Type") }} *</label>
						<div class="grid grid-cols-2 gap-2">
							<button
								v-for="t in FEEDBACK_TYPES"
								:key="t"
								type="button"
								class="rounded-lg border px-3 py-2 text-sm"
								:class="form.ticket_type === t ? 'border-gray-900 bg-gray-900 text-white' : 'border-gray-300'"
								@click="form.ticket_type = t"
							>
								{{ __(t) }}
							</button>
						</div>
					</div>

					<div class="flex flex-col gap-1">
						<div class="flex items-center justify-between">
							<label class="text-sm font-medium">{{ __("Category") }} *</label>
							<button
								v-if="options.can_add_category && !newCategory"
								type="button"
								class="text-sm font-medium text-blue-600"
								@click="startNewCategory"
							>
								+ {{ __("New category") }}
							</button>
						</div>
						<select v-model="form.category" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
							<option value="">{{ loadingOptions ? __("Loading...") : __("Select a category") }}</option>
							<option v-for="c in options.categories" :key="c.name" :value="c.name">{{ c.name }}</option>
						</select>
						<p v-if="categoryHint" class="text-xs text-gray-500">{{ categoryHint }}</p>

						<!-- managers: add a Ticket Category without leaving the form -->
						<div v-if="newCategory" class="mt-2 flex flex-col gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
							<p class="text-sm font-medium">{{ __("New category") }}</p>
							<input
								v-model="newCategory.category_name"
								type="text"
								class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
								:placeholder="__('Category name, e.g. Salary')"
							/>
							<select v-model="newCategory.department" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
								<option value="">{{ __("Team that handles it") }}</option>
								<option v-for="d in options.departments" :key="d" :value="d">{{ d }}</option>
							</select>
							<input
								v-model="newCategory.description"
								type="text"
								class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
								:placeholder="__('Short hint for people (optional)')"
							/>
							<div class="flex gap-2">
								<button type="button" class="flex-1 rounded-lg border border-gray-300 bg-white py-2 text-sm" @click="newCategory = null">
									{{ __("Cancel") }}
								</button>
								<button
									type="button"
									class="flex-1 rounded-lg bg-blue-600 py-2 text-sm font-medium text-white disabled:opacity-50"
									:disabled="savingCategory || !newCategory.category_name.trim() || !newCategory.department"
									@click="saveCategory"
								>
									{{ savingCategory ? __("Saving...") : __("Add") }}
								</button>
							</div>
						</div>
					</div>

					<!-- asset categories: which of my company assets -->
					<div v-if="isAssetCategory" class="flex flex-col gap-1">
						<label class="text-sm font-medium">{{ __("Which asset?") }} *</label>
						<select v-model="form.asset" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
							<option value="">{{ __("Select your asset") }}</option>
							<option v-for="a in options.my_assets" :key="a.name" :value="a.name">
								{{ a.asset_name }} · {{ a.name }}{{ a.serial_number ? " · " + a.serial_number : "" }}
							</option>
						</select>
						<p v-if="!options.my_assets?.length" class="text-xs text-red-600">
							{{ __("No company asset is issued to you.") }}
						</p>
					</div>

					<!-- not for asset problems: the complaint is about the asset -->
					<div v-if="!isFeedback && !isAssetCategory" class="flex flex-col gap-2">
						<label class="text-sm font-medium">{{ __("Complaint Against") }} *</label>
						<div class="grid grid-cols-2 gap-2">
							<button
								v-for="a in againstKinds"
								:key="a.key"
								type="button"
								class="rounded-lg border px-2 py-2 text-sm"
								:class="form.against_kind === a.key ? 'border-gray-900 bg-gray-900 text-white' : 'border-gray-300'"
								@click="form.against_kind = a.key"
							>
								{{ a.label }}
							</button>
						</div>
						<PersonPicker
							v-if="form.against_kind === 'person'"
							v-model="form.against"
							kind="against"
							:exclude="form.report_to.map((p) => p.user)"
							:placeholder="__('Search the person')"
						/>
						<select
							v-if="form.against_kind === 'department'"
							v-model="form.against_department"
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
						>
							<option value="">{{ __("Select the department") }}</option>
							<option v-for="d in options.departments" :key="d" :value="d">{{ d }}</option>
						</select>
						<p v-if="form.against_kind === 'person'" class="text-xs text-gray-500">
							{{ __("The person this complaint is about. They will never see it.") }}
						</p>
						<p v-if="form.against_kind === 'department'" class="text-xs text-gray-500">
							{{ __("It goes to the grievance team, never to the department it is about.") }}
						</p>
					</div>

					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium">{{ isFeedback ? __("For / Report To") : __("Report To") }}</label>
						<PersonPicker
							v-model="form.report_to"
							kind="report_to"
							multiple
							:exclude="form.against.map((p) => p.user)"
							:placeholder="__('Search people (you can pick more than one)')"
						/>
						<p class="text-xs text-gray-500">
							{{
								__(
									"Everyone you pick gets it and can solve it. Leave empty to send it to the team of the category."
								)
							}}
						</p>
					</div>

					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium">{{ __("Subject") }} *</label>
						<input
							v-model="form.subject"
							type="text"
							maxlength="140"
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
							:placeholder="__('In a few words')"
						/>
					</div>

					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium">{{ isFeedback ? __("Message") : __("Details") }} *</label>
						<textarea
							v-model="form.description"
							rows="5"
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
							:placeholder="isFeedback ? __('Your feedback') : __('What happened? When? Who was involved?')"
						></textarea>
					</div>

					<div class="flex flex-col gap-1">
						<label class="text-sm font-medium">{{ __("Attachment") }}</label>
						<input type="file" class="text-sm" @change="file = $event.target.files[0] || null" />
					</div>

					<label v-if="isFeedback && options.allow_anonymous" class="flex items-center gap-2 text-sm">
						<input v-model="form.is_anonymous" type="checkbox" />
						{{ __("Send without my name") }}
					</label>

					<div class="flex gap-2">
						<button type="button" class="flex-1 rounded-lg border border-gray-300 py-2 text-sm" @click="closeForm">
							{{ __("Cancel") }}
						</button>
						<button
							type="button"
							class="flex-1 rounded-lg bg-gray-900 py-2 text-sm font-medium text-white disabled:opacity-50"
							:disabled="submitting"
							@click="submit"
						>
							{{ submitting ? __("Sending...") : __("Submit") }}
						</button>
					</div>
				</div>

				<!-- ===================== LISTS ===================== -->
				<template v-else>
					<div v-if="!isFeedback" class="grid grid-cols-2 gap-1 rounded-lg bg-gray-100 p-1">
						<button
							v-for="t in tabs"
							:key="t.key"
							type="button"
							class="rounded-md py-2 text-sm font-medium"
							:class="tab === t.key ? 'bg-white shadow-sm' : 'text-gray-500'"
							@click="switchTab(t.key)"
						>
							{{ t.label }}
							<span v-if="t.count" class="ml-1 rounded-full bg-gray-900 px-2 text-xs text-white">{{ t.count }}</span>
						</button>
					</div>

					<div class="flex gap-2 overflow-x-auto">
						<button
							v-for="g in groups"
							:key="g.key"
							type="button"
							class="whitespace-nowrap rounded-full border px-3 py-1 text-xs"
							:class="group === g.key ? 'border-gray-900 bg-gray-900 text-white' : 'border-gray-300 text-gray-600'"
							@click="group = g.key; load()"
						>
							{{ g.label }}
						</button>
					</div>

					<div v-if="loading" class="rounded-lg bg-white p-6 text-center text-sm text-gray-500 shadow-sm">
						{{ __("Loading...") }}
					</div>
					<div v-else-if="!tickets.length" class="rounded-lg bg-white p-6 text-center text-sm text-gray-500 shadow-sm">
						{{ tab === "assigned" ? __("Nothing assigned to you.") : text.empty }}
					</div>

					<button
						v-for="t in tickets"
						v-else
						:key="t.ticket"
						type="button"
						class="flex flex-col gap-2 rounded-lg bg-white p-4 text-left shadow-sm"
						@click="openTicket(t.ticket)"
					>
						<div class="flex items-start justify-between gap-3">
							<div class="min-w-0">
								<p class="truncate text-base font-semibold">{{ t.subject }}</p>
								<p class="mt-0.5 text-xs text-gray-500">
									{{ t.ticket }} · {{ t.category }}<template v-if="isFeedback || tab === 'assigned'"> · {{ t.ticket_type }}</template>
								</p>
							</div>
							<span class="shrink-0 rounded-full px-2 py-1 text-xs" :class="STATUS_CLASS[t.status] || 'bg-gray-100'">
								{{ __(t.status) }}
							</span>
						</div>
						<div class="flex flex-wrap gap-2 text-xs">
							<span v-if="t.escalation_level" class="rounded bg-red-50 px-2 py-0.5 text-red-700">
								{{ __("Escalated L{0}", [t.escalation_level]) }}
							</span>
							<span v-if="t.needs_reply && tab === 'mine'" class="rounded bg-orange-50 px-2 py-0.5 text-orange-700">
								{{ __("Needs your reply") }}
							</span>
							<span v-if="t.sla_status === 'Breached' && !['Resolved', 'Closed', 'Rejected'].includes(t.status)" class="rounded bg-red-50 px-2 py-0.5 text-red-700">
								{{ __("Overdue") }}
							</span>
							<span v-if="t.asset_name" class="rounded bg-blue-50 px-2 py-0.5 text-blue-700">🖥 {{ t.asset_name }}</span>
							<span v-if="(t.against_user_name || t.against_department) && tab === 'mine'" class="text-gray-500">
								{{ __("Against") }}: {{ t.against_user_name || t.against_department }}
							</span>
							<span v-if="tab === 'assigned' && t.requester_name" class="text-gray-500">
								{{ __("From") }}: {{ t.requester_name }}
							</span>
						</div>
						<p class="text-xs text-gray-400">{{ t.created }}</p>
					</button>
				</template>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"
import { onIonViewWillEnter } from "@ionic/vue"

import BaseLayout from "@/components/BaseLayout.vue"
import PersonPicker from "./PersonPicker.vue"
import { FEEDBACK_TYPES, STATUS_CLASS, get, post, uploadFile } from "./api"

const __ = inject("$translate")
const router = useRouter()

const props = defineProps({
	kind: { type: String, default: "complaint" }, // complaint | feedback
})

const isFeedback = computed(() => props.kind === "feedback")
const text = computed(() =>
	isFeedback.value
		? {
				title: __("Feedback"),
				newTitle: __("Give Feedback"),
				add: __("Give Feedback"),
				empty: __("You have not given any feedback yet."),
		  }
		: {
				title: __("Complaints"),
				newTitle: __("New Complaint"),
				add: __("Add Complaint"),
				empty: __("You have not raised any complaints yet."),
		  }
)

const tab = ref("mine")
const group = ref("")
const tickets = ref([])
const counts = ref({})
const assignedCount = ref(0)
const loading = ref(true)
const error = ref("")

const tabs = computed(() => [
	{ key: "mine", label: __("My Complaints") },
	{ key: "assigned", label: __("Assigned to me"), count: assignedCount.value },
])
const groups = computed(() =>
	tab.value === "assigned"
		? [
				{ key: "open", label: __("Open") },
				{ key: "resolved", label: __("Resolved") },
				{ key: "all", label: __("All") },
		  ]
		: [
				{ key: "", label: __("All") },
				{ key: "open", label: __("Open") },
				{ key: "waiting", label: __("Needs reply") },
				{ key: "resolved", label: __("Resolved") },
		  ]
)

async function load() {
	loading.value = true
	error.value = ""
	try {
		if (tab.value === "assigned") {
			const result = await get("get_assigned_tickets", { group: group.value || "open", page_length: 50 })
			tickets.value = result.tickets
			assignedCount.value = result.counts.open
		} else {
			const result = await get("get_my_tickets", {
				group: group.value,
				ticket_type: isFeedback.value ? FEEDBACK_TYPES.join(",") : "Complaint",
				page_length: 50,
			})
			tickets.value = result.tickets
			counts.value = result.counts
			if (!isFeedback.value) {
				get("get_assigned_tickets", { group: "open", page_length: 1 })
					.then((r) => (assignedCount.value = r.counts.open))
					.catch(() => {})
			}
		}
	} catch (e) {
		error.value = e.message
		tickets.value = []
	} finally {
		loading.value = false
	}
}

function switchTab(key) {
	tab.value = key
	group.value = key === "assigned" ? "open" : ""
	load()
}

// ---------------------------------------------------------------- form
const showForm = ref(false)
const submitting = ref(false)
const loadingOptions = ref(false)
const options = ref({ categories: [], departments: [], allow_anonymous: 0, can_add_category: 0 })
const againstKinds = computed(() => [
	{ key: "person", label: __("A person") },
	{ key: "department", label: __("A department") },
])

// managers: add a category from here (arown_lms.api.support.add_category)
const newCategory = ref(null)
const savingCategory = ref(false)
function startNewCategory() {
	newCategory.value = { category_name: "", department: "", description: "" }
}
async function saveCategory() {
	savingCategory.value = true
	error.value = ""
	try {
		const row = await post("add_category", {
			category_name: newCategory.value.category_name.trim(),
			department: newCategory.value.department,
			description: newCategory.value.description.trim(),
		})
		options.value.categories = [...options.value.categories, row].sort((a, b) => a.name.localeCompare(b.name))
		form.value.category = row.name
		newCategory.value = null
	} catch (e) {
		error.value = e.message
	} finally {
		savingCategory.value = false
	}
}
const file = ref(null)
const emptyForm = () => ({
	ticket_type: isFeedback.value ? "Suggestion" : "Complaint",
	category: "",
	against_kind: "person", // person | department (a complaint is always against someone)
	against: [],
	against_department: "",
	asset: "",
	report_to: [],
	subject: "",
	description: "",
	is_anonymous: false,
})
const form = ref(emptyForm())

const isAssetCategory = computed(
	() => !isFeedback.value && !!options.value.categories.find((c) => c.name === form.value.category)?.is_asset_issue
)
const categoryHint = computed(() => options.value.categories.find((c) => c.name === form.value.category)?.hint)

async function openForm() {
	form.value = emptyForm()
	file.value = null
	newCategory.value = null
	error.value = ""
	showForm.value = true
	if (options.value.categories.length) return
	loadingOptions.value = true
	try {
		options.value = await get("get_support_options")
	} catch (e) {
		error.value = e.message
	} finally {
		loadingOptions.value = false
	}
}

function closeForm() {
	showForm.value = false
	error.value = ""
}

async function submit() {
	const f = form.value
	if (!f.category) return (error.value = __("Select a category"))
	if (!f.subject.trim() || !f.description.trim()) return (error.value = __("Subject and details are required"))
	if (isAssetCategory.value && !f.asset) return (error.value = __("Choose the asset this problem is about"))
	const needsAgainst = !isFeedback.value && !isAssetCategory.value
	if (needsAgainst && f.against_kind === "person" && !f.against.length)
		return (error.value = __("Choose the person this complaint is against"))
	if (needsAgainst && f.against_kind === "department" && !f.against_department)
		return (error.value = __("Choose the department this complaint is against"))
	submitting.value = true
	error.value = ""
	try {
		const ticket = await post("create_ticket", {
			ticket_type: f.ticket_type,
			category: f.category,
			subject: f.subject.trim(),
			description: f.description.trim(),
			against_user: needsAgainst && f.against_kind === "person" ? f.against[0]?.user || null : null,
			against_department: needsAgainst && f.against_kind === "department" ? f.against_department || null : null,
			report_to: JSON.stringify(f.report_to.map((p) => p.user)),
			is_anonymous: isFeedback.value && f.is_anonymous ? 1 : 0,
			asset: isAssetCategory.value ? f.asset : null,
		})
		if (file.value) {
			try {
				await uploadFile(ticket.ticket, file.value)
			} catch (e) {
				alert(__("Sent, but the file could not be attached: {0}", [e.message]))
			}
		}
		showForm.value = false
		openTicket(ticket.ticket)
	} catch (e) {
		error.value = e.message
	} finally {
		submitting.value = false
	}
}

function openTicket(id) {
	router.push({ name: "SupportTicketDetailView", params: { id } })
}

function back() {
	if (showForm.value) return closeForm()
	router.push("/home")
}

watch(
	() => props.kind,
	() => {
		tab.value = "mine"
		group.value = ""
		showForm.value = false
		load()
	}
)
// Ionic keeps the page alive: reload when coming back from a ticket (the first entry loads in onMounted)
let entered = false
onMounted(load)
onIonViewWillEnter(() => {
	if (entered && !showForm.value) load()
	entered = true
})
</script>

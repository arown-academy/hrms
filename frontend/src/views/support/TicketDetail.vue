<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col gap-4 p-4 pb-24">
				<div class="flex items-center gap-2">
					<button type="button" class="flex h-9 w-9 items-center justify-center rounded-full" @click="back">
						<span class="text-3xl leading-none">‹</span>
					</button>
					<h1 class="truncate text-xl font-semibold">{{ t?.ticket || __("Ticket") }}</h1>
				</div>

				<div v-if="error" class="rounded-lg bg-red-50 p-3 text-sm text-red-600">{{ error }}</div>
				<div v-if="loading && !t" class="rounded-lg bg-white p-6 text-center text-sm text-gray-500 shadow-sm">
					{{ __("Loading...") }}
				</div>

				<template v-if="t">
					<!-- summary -->
					<div class="flex flex-col gap-3 rounded-lg bg-white p-4 shadow-sm">
						<div class="flex items-start justify-between gap-3">
							<div class="min-w-0">
								<p class="text-base font-semibold">{{ t.subject }}</p>
								<p class="mt-0.5 text-xs text-gray-500">{{ t.ticket_type }} · {{ t.category }} · {{ t.created }}</p>
							</div>
							<span class="shrink-0 rounded-full px-2 py-1 text-xs" :class="STATUS_CLASS[t.status] || 'bg-gray-100'">
								{{ __(t.status) }}
							</span>
						</div>
						<div class="flex flex-wrap gap-2 text-xs">
							<span v-if="t.escalation_level" class="rounded bg-red-50 px-2 py-0.5 text-red-700">
								{{ __("Escalated L{0}", [t.escalation_level]) }}
							</span>
							<span v-if="t.sla_text" class="rounded bg-gray-100 px-2 py-0.5 text-gray-700">{{ t.sla_text }}</span>
						</div>
						<dl class="grid grid-cols-3 gap-x-2 gap-y-1 text-sm">
							<template v-if="!t.is_requester">
								<dt class="text-gray-500">{{ __("From") }}</dt>
								<dd class="col-span-2">{{ t.requester_name }} <span class="text-gray-400">({{ t.requester_type }})</span></dd>
							</template>
							<template v-if="t.against_user_name || t.against_department">
								<dt class="text-gray-500">{{ __("Against") }}</dt>
								<dd class="col-span-2">
									{{ [t.against_user_name, t.against_department && __("{0} (department)", [t.against_department])].filter(Boolean).join(", ") }}
								</dd>
							</template>
							<template v-if="t.report_to?.length">
								<dt class="text-gray-500">{{ __("Report To") }}</dt>
								<dd class="col-span-2">{{ t.report_to.map((p) => p.name).join(", ") }}</dd>
							</template>
							<dt class="text-gray-500">{{ __("Handled by") }}</dt>
							<dd class="col-span-2">{{ t.assignee_name || t.department || "-" }}</dd>
						</dl>
						<p class="whitespace-pre-line text-sm text-gray-700">{{ t.description }}</p>
						<div v-if="t.attachments?.length" class="flex flex-col gap-1">
							<a
								v-for="f in t.attachments"
								:key="f.file"
								:href="f.file_url"
								target="_blank"
								rel="noopener noreferrer"
								class="text-sm text-blue-600"
							>
								📎 {{ f.file_name }}
							</a>
						</div>
					</div>

					<!-- asset complaint -->
					<div v-if="t.asset" class="flex flex-col gap-2 rounded-lg bg-blue-50 p-4">
						<div class="flex items-start justify-between gap-2">
							<div>
								<p class="text-xs font-medium text-blue-800">{{ __("Asset") }}</p>
								<p class="text-sm font-semibold text-blue-950">{{ t.asset.asset_name }} · {{ t.asset.name }}</p>
								<p class="text-xs text-blue-900">
									{{ [t.asset.asset_category, t.asset.model, t.asset.serial_number && __("S/N {0}", [t.asset.serial_number])].filter(Boolean).join(" · ") }}
								</p>
								<p v-if="t.asset.issue_date" class="text-xs text-blue-900">{{ __("Issued on {0}", [t.asset.issue_date]) }}</p>
							</div>
							<span class="shrink-0 rounded-full bg-white px-2 py-1 text-xs">{{ __(t.asset.status) }}</span>
						</div>
						<p v-if="t.asset.repair" class="text-xs text-blue-900">
							{{ __("Repair {0}: {1}", [t.asset.repair.name, __(t.asset.repair.repair_status)]) }}
							<template v-if="t.asset.repair.failure_date"> · {{ __("sent {0}", [t.asset.repair.failure_date]) }}</template>
							<template v-if="t.asset.repair.completion_date"> · {{ __("done {0}", [t.asset.repair.completion_date]) }}</template>
						</p>
						<div v-if="t.can_send_for_repair || t.can_finish_repair" class="flex gap-2">
							<button
								v-if="t.can_send_for_repair"
								type="button"
								class="flex-1 rounded-lg bg-blue-600 py-2 text-sm font-medium text-white disabled:opacity-50"
								:disabled="busy"
								@click="ask('send_for_repair', 'note', __('What is wrong / where is it sent? The employee will see this.'))"
							>
								{{ __("Send for Repair") }}
							</button>
							<button
								v-if="t.can_finish_repair"
								type="button"
								class="flex-1 rounded-lg bg-green-600 py-2 text-sm font-medium text-white disabled:opacity-50"
								:disabled="busy"
								@click="ask('finish_repair', 'note', __('What was repaired? The asset goes back to the employee and the complaint is resolved.'))"
							>
								{{ __("Repair Done") }}
							</button>
						</div>
					</div>

					<!-- outcome -->
					<div v-if="t.resolution_note && ['Resolved', 'Closed'].includes(t.status)" class="rounded-lg bg-green-50 p-4">
						<p class="text-xs font-medium text-green-800">{{ __("Solution") }}</p>
						<p class="mt-1 whitespace-pre-line text-sm text-green-900">{{ t.resolution_note }}</p>
					</div>
					<div v-if="t.reject_reason && t.status === 'Rejected'" class="rounded-lg bg-red-50 p-4">
						<p class="text-xs font-medium text-red-800">{{ __("Not accepted") }}</p>
						<p class="mt-1 whitespace-pre-line text-sm text-red-900">{{ t.reject_reason }}</p>
					</div>

					<!-- requester: solved / not solved -->
					<div v-if="t.can_close || t.can_reopen" class="flex flex-col gap-2 rounded-lg bg-white p-4 shadow-sm">
						<p class="text-sm font-medium">
							{{ t.status === "Resolved" ? __("Did this solve your problem?") : __("Still not solved?") }}
						</p>
						<div class="flex gap-2">
							<button
								v-if="t.can_close"
								type="button"
								class="flex-1 rounded-lg bg-green-600 py-2 text-sm font-medium text-white disabled:opacity-50"
								:disabled="busy"
								@click="act('close_ticket')"
							>
								✔ {{ __("Solved") }}
							</button>
							<button
								v-if="t.can_reopen"
								type="button"
								class="flex-1 rounded-lg bg-red-600 py-2 text-sm font-medium text-white disabled:opacity-50"
								:disabled="busy"
								@click="ask('reopen_ticket', 'reason', __('Why is it not solved? It will be escalated to a senior person.'))"
							>
								✘ {{ __("Not solved") }}
							</button>
						</div>
					</div>

					<!-- requester: rating -->
					<div v-if="t.can_rate && !t.rating" class="flex flex-col gap-2 rounded-lg bg-white p-4 shadow-sm">
						<p class="text-sm font-medium">{{ __("Rate the support") }}</p>
						<div class="flex gap-2 text-3xl">
							<button v-for="n in 5" :key="n" type="button" :disabled="busy" @click="act('rate_ticket', { rating: n })">
								<span :class="n <= hoverRating ? 'text-yellow-500' : 'text-gray-300'" @mouseenter="hoverRating = n" @mouseleave="hoverRating = 0">★</span>
							</button>
						</div>
					</div>
					<p v-else-if="t.rating" class="text-sm text-gray-500">{{ __("Your rating") }}: {{ "★".repeat(t.rating) }}</p>

					<!-- handler actions -->
					<div v-if="t.can_start || t.can_resolve || (t.can_reject && !['Rejected', 'Closed'].includes(t.status))" class="flex flex-wrap gap-2">
						<button
							v-if="t.can_start"
							type="button"
							class="flex-1 rounded-lg border border-gray-900 py-2 text-sm font-medium disabled:opacity-50"
							:disabled="busy"
							@click="act('start_ticket')"
						>
							{{ __("Start") }}
						</button>
						<button
							v-if="t.can_resolve && t.status !== 'Resolved'"
							type="button"
							class="flex-1 rounded-lg bg-green-600 py-2 text-sm font-medium text-white disabled:opacity-50"
							:disabled="busy"
							@click="ask('resolve_ticket', 'note', __('What was done to solve it? The requester will see this.'))"
						>
							{{ __("Resolve") }}
						</button>
						<button
							v-if="t.can_reject && t.is_requester === false && !['Rejected', 'Closed', 'Resolved'].includes(t.status)"
							type="button"
							class="flex-1 rounded-lg border border-red-600 py-2 text-sm font-medium text-red-600 disabled:opacity-50"
							:disabled="busy"
							@click="ask('reject_ticket', 'reason', __('Why is this not accepted?'))"
						>
							{{ __("Reject") }}
						</button>
					</div>

					<!-- prompt (reason / solution) -->
					<div v-if="prompt" class="flex flex-col gap-2 rounded-lg bg-white p-4 shadow-sm">
						<p class="text-sm font-medium">{{ prompt.label }}</p>
						<textarea v-model="prompt.value" rows="3" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"></textarea>
						<div class="flex gap-2">
							<button type="button" class="flex-1 rounded-lg border border-gray-300 py-2 text-sm" @click="prompt = null">
								{{ __("Cancel") }}
							</button>
							<button
								type="button"
								class="flex-1 rounded-lg bg-gray-900 py-2 text-sm font-medium text-white disabled:opacity-50"
								:disabled="busy || !prompt.value.trim()"
								@click="act(prompt.method, { [prompt.field]: prompt.value.trim() })"
							>
								{{ __("Send") }}
							</button>
						</div>
					</div>

					<!-- conversation -->
					<div class="flex flex-col gap-2">
						<h2 class="text-base font-semibold">{{ __("Conversation") }}</h2>
						<p v-if="!t.conversation.length" class="text-sm text-gray-500">{{ __("No messages yet.") }}</p>
						<div
							v-for="(m, i) in t.conversation"
							:key="i"
							class="max-w-[85%] rounded-lg p-3 text-sm"
							:class="[
								m.mine ? 'self-end bg-gray-900 text-white' : 'self-start bg-white shadow-sm',
								m.is_internal ? 'border border-dashed border-yellow-500' : '',
							]"
						>
							<p class="text-xs" :class="m.mine ? 'text-gray-300' : 'text-gray-500'">
								{{ m.by }}<template v-if="m.is_internal"> · {{ __("internal note") }}</template> · {{ m.posted_on }}
							</p>
							<p class="mt-1 whitespace-pre-line">{{ m.message }}</p>
							<a v-if="m.attachment_url" :href="m.attachment_url" target="_blank" rel="noopener noreferrer" class="mt-1 block underline">
								📎 {{ __("Attachment") }}
							</a>
						</div>
						<div v-if="canReply" class="flex gap-2">
							<textarea
								v-model="message"
								rows="2"
								class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm"
								:placeholder="__('Write a message')"
							></textarea>
							<button
								type="button"
								class="rounded-lg bg-gray-900 px-4 text-sm font-medium text-white disabled:opacity-50"
								:disabled="busy || !message.trim()"
								@click="sendMessage"
							>
								{{ __("Send") }}
							</button>
						</div>
					</div>

					<!-- timeline -->
					<details class="rounded-lg bg-white p-4 shadow-sm">
						<summary class="text-sm font-semibold">{{ __("History") }}</summary>
						<ol class="mt-3 flex flex-col gap-2 border-l border-gray-200 pl-3">
							<li v-for="(e, i) in t.timeline" :key="i" class="text-sm">
								<p class="font-medium">{{ e.event }}</p>
								<p v-if="e.detail" class="text-gray-600">{{ e.detail }}</p>
								<p class="text-xs text-gray-400">{{ e.by }} · {{ e.on }}</p>
							</li>
						</ol>
					</details>
				</template>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { computed, inject, onMounted, ref, watch } from "vue"
import { useRouter } from "vue-router"

import BaseLayout from "@/components/BaseLayout.vue"
import { STATUS_CLASS, get, post } from "./api"

const __ = inject("$translate")
const router = useRouter()

const props = defineProps({ id: { type: String, required: true } })

const t = ref(null)
const loading = ref(false)
const busy = ref(false)
const error = ref("")
const message = ref("")
const prompt = ref(null)
const hoverRating = ref(0)

const canReply = computed(() => t.value && (t.value.can_reply || t.value.can_staff_reply))

async function load() {
	loading.value = true
	error.value = ""
	try {
		t.value = await get("get_ticket", { ticket: props.id })
	} catch (e) {
		error.value = e.message
	} finally {
		loading.value = false
	}
}

function ask(method, field, label) {
	prompt.value = { method, field, label, value: "" }
}

async function act(method, params = {}) {
	busy.value = true
	error.value = ""
	try {
		t.value = await post(method, { ticket: props.id, ...params })
		prompt.value = null
	} catch (e) {
		error.value = e.message
	} finally {
		busy.value = false
	}
}

async function sendMessage() {
	await act("reply_ticket", { message: message.value.trim() })
	if (!error.value) message.value = ""
}

function back() {
	if (window.history.length > 1) router.back()
	else router.push({ name: "EmployeeComplaintDashboard" })
}

watch(() => props.id, load)
onMounted(load)
</script>

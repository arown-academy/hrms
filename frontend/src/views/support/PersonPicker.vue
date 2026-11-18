<template>
	<div class="flex flex-col gap-2">
		<!-- chosen people -->
		<div v-if="chosen.length" class="flex flex-wrap gap-2">
			<span
				v-for="person in chosen"
				:key="person.user"
				class="flex items-center gap-1 rounded-full bg-gray-100 py-1 pl-3 pr-2 text-sm"
			>
				{{ person.name }}
				<button type="button" class="px-1 text-gray-500" :aria-label="__('Remove')" @click="remove(person)">✕</button>
			</span>
		</div>

		<div v-if="multiple || !chosen.length" class="relative">
			<input
				v-model="search"
				type="text"
				class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
				:placeholder="placeholder"
				@focus="open = true; load()"
				@input="onInput"
				@blur="close"
			/>
			<div
				v-if="open"
				class="absolute z-20 mt-1 max-h-64 w-full overflow-y-auto rounded-lg border border-gray-200 bg-white shadow-lg"
			>
				<p v-if="loading" class="p-3 text-sm text-gray-500">{{ __("Searching...") }}</p>
				<p v-else-if="!options.length" class="p-3 text-sm text-gray-500">{{ __("Nobody found") }}</p>
				<button
					v-for="person in options"
					:key="person.user"
					type="button"
					class="flex w-full flex-col items-start border-b border-gray-100 px-3 py-2 text-left last:border-0 active:bg-gray-50"
					@mousedown.prevent="pick(person)"
				>
					<span class="text-sm font-medium">{{ person.name }}</span>
					<span class="text-xs text-gray-500">{{ [person.type, person.detail].filter(Boolean).join(" · ") }}</span>
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed, inject, ref } from "vue"
import { get } from "./api"

const __ = inject("$translate")

const props = defineProps({
	modelValue: { type: Array, default: () => [] }, // [{ user, name }]
	kind: { type: String, default: "report_to" }, // report_to | against
	multiple: { type: Boolean, default: false },
	exclude: { type: Array, default: () => [] }, // user ids not offered
	placeholder: { type: String, default: "" },
})
const emit = defineEmits(["update:modelValue"])

const search = ref("")
const options = ref([])
const loading = ref(false)
const open = ref(false)
let timer = null

const chosen = computed(() => props.modelValue || [])

async function load() {
	loading.value = true
	try {
		const taken = new Set([...chosen.value.map((p) => p.user), ...props.exclude])
		const rows = await get("search_people", { txt: search.value, kind: props.kind })
		options.value = (rows || []).filter((p) => !taken.has(p.user))
	} catch (e) {
		options.value = []
	} finally {
		loading.value = false
	}
}

function onInput() {
	open.value = true
	clearTimeout(timer)
	timer = setTimeout(load, 300)
}

function pick(person) {
	const value = props.multiple ? [...chosen.value, { user: person.user, name: person.name }] : [{ user: person.user, name: person.name }]
	emit("update:modelValue", value)
	search.value = ""
	open.value = props.multiple
	if (props.multiple) load()
}

function remove(person) {
	emit("update:modelValue", chosen.value.filter((p) => p.user !== person.user))
}

function close() {
	setTimeout(() => (open.value = false), 150)
}
</script>

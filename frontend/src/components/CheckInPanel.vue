<template>
	<div class="flex flex-col bg-white rounded w-full py-6 px-4 border-none">
		<h2 class="text-lg font-bold text-gray-900">
			{{ __("Hey, {0} 👋", [employee?.data?.first_name]) }}
		</h2>

		<template v-if="settings.data?.allow_employee_checkin_from_mobile_app">
			<!-- status could not be loaded: never guess "Check In" -->
			<template v-if="statusLoadFailed">
				<div class="mt-3 rounded bg-red-50 p-3 text-sm font-medium text-red-700">
					{{ __("Could not load your check-in status. Check your connection and try again.") }}
				</div>
				<Button
					class="mt-4 mb-1 drop-shadow-sm py-5 text-base"
					:loading="checkins.list.loading"
					@click="loadStatus"
				>
					{{ __("Retry") }}
				</Button>
			</template>

			<template v-else>
				<div class="font-medium text-sm text-gray-500 mt-1.5" v-if="lastLog">
					<span>{{ __("Last {0} was at {1}", [__(lastLogType), formatTimestamp(lastLog.time)]) }}</span>
					<span class="whitespace-pre"> &middot; </span>
					<router-link :to="{ name: 'EmployeeCheckinListView' }" v-slot="{ navigate }">
						<span @click="navigate" class="underline">View List</span>
					</router-link>
				</div>
				<Button
					class="mt-4 mb-1 drop-shadow-sm py-5 text-base"
					:loading="!checkins.data"
					@click="openSheet"
				>
					<template #prefix>
						<FeatherIcon
							:name="nextAction.action === 'IN' ? 'arrow-right-circle' : 'arrow-left-circle'"
							class="w-4"
						/>
					</template>
					{{ nextAction.label }}
				</Button>
			</template>
		</template>

		<div v-else class="font-medium text-sm text-gray-500 mt-1.5">
			{{ dayjs().format("ddd, D MMMM, YYYY") }}
		</div>
	</div>

	<!--
		The sheet closes only through closeSheet() (Done / Cancel / after a successful save):
		swipe, backdrop and back button are blocked by can-dismiss.
	-->
	<ion-modal
		v-if="settings.data?.allow_employee_checkin_from_mobile_app"
		:is-open="sheetOpen"
		:initial-breakpoint="1"
		:breakpoints="[0, 1]"
		:backdrop-dismiss="false"
		:can-dismiss="canDismiss"
		@didDismiss="onSheetDismissed"
	>
		<div class="w-full flex flex-col items-center justify-center gap-5 px-4 pt-8 pb-10">
			<!-- saved on the server -->
			<template v-if="sheetState === 'success'">
				<FeatherIcon name="check-circle" class="h-16 w-16 text-green-600" />
				<div class="flex flex-col gap-1.5 items-center text-center">
					<div class="font-bold text-xl text-gray-900">
						<!-- already_saved: a retry after a lost response found the log saved the first time -->
						{{
							savedLog?.already_saved
								? __("{0} was already saved", [pendingAction.title])
								: __("{0} saved", [pendingAction.title])
						}}
					</div>
					<div class="font-medium text-gray-600 text-base">
						{{ __("Recorded at {0}", [dayjs(savedLog?.time).format("hh:mm a, D MMM YYYY")]) }}
					</div>
				</div>
				<Button variant="solid" class="w-full py-5 text-sm" @click="closeSheet">
					{{ __("Done") }}
				</Button>
			</template>

			<template v-else>
				<div class="flex flex-col gap-1.5 items-center justify-center">
					<div class="font-bold text-xl">
						{{ now.format("hh:mm:ss a") }}
					</div>
					<div class="font-medium text-gray-500 text-sm">
						{{ now.format("D MMM, YYYY") }}
					</div>
				</div>

				<template v-if="geolocationRequired">
					<span
						class="font-medium text-sm text-center"
						:class="locationState === 'error' ? 'text-red-600' : 'text-gray-500'"
					>
						{{ locationStatus }}
					</span>

					<div
						v-if="locationState === 'ok'"
						class="rounded border-4 translate-z-0 block overflow-hidden w-full"
					>
						<iframe
							width="100%"
							height="170"
							frameborder="0"
							scrolling="no"
							marginheight="0"
							marginwidth="0"
							style="border: 0"
							:src="`https://maps.google.com/maps?q=${latitude},${longitude}&hl=en&z=15&amp;output=embed`"
						>
						</iframe>
					</div>

					<Button
						v-if="locationState === 'error' && sheetState !== 'saving'"
						class="w-full py-5 text-sm"
						@click="fetchLocation"
					>
						{{ __("Retry location") }}
					</Button>
				</template>

				<!-- not saved: the message stays inside the sheet until the employee acts -->
				<div
					v-if="sheetState === 'error'"
					class="w-full rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700"
				>
					<div class="font-bold mb-1">
						{{ __("{0} NOT saved", [pendingAction.title]) }}
					</div>
					<div v-for="(message, index) in errorMessages" :key="index">{{ message }}</div>
				</div>

				<Button
					variant="solid"
					class="w-full py-5 text-sm disabled:bg-gray-700"
					:loading="sheetState === 'saving'"
					:disabled="!canConfirm"
					@click="submitLog"
				>
					{{ confirmLabel }}
				</Button>

				<Button
					v-if="sheetState !== 'saving'"
					variant="subtle"
					class="w-full py-5 text-sm"
					@click="closeSheet"
				>
					{{ __("Cancel") }}
				</Button>
			</template>
		</div>
	</ion-modal>
</template>

<script setup>
import { createListResource, createResource, FeatherIcon } from "frappe-ui"
import { computed, inject, ref, onMounted, onBeforeUnmount } from "vue"
import { IonModal } from "@ionic/vue"

import { formatTimestamp } from "@/utils/formatters"
import { settings } from "@/data/settings"

const DOCTYPE = "Employee Checkin"

const socket = inject("$socket")
const employee = inject("$employee")
const dayjs = inject("$dayjs")
const __ = inject("$translate")

const latitude = ref(0)
const longitude = ref(0)
const locationStatus = ref("")
const locationState = ref("idle") // idle | locating | ok | error

const sheetOpen = ref(false)
const sheetState = ref("idle") // idle | saving | success | error
const pendingAction = ref({})
const savedLog = ref(null)
const errorMessages = ref([])
const now = ref(dayjs())

let allowClose = false
let clockTimer = null
let autoCloseTimer = null

const checkins = createListResource({
	doctype: DOCTYPE,
	fields: ["name", "employee", "employee_name", "log_type", "time", "device_id"],
	filters: {
		employee: employee.data.name,
		log_type: ["is", "set"],
	},
	orderBy: "time desc",
})

// errors are shown in the panel (statusLoadFailed), not thrown
const loadStatus = () => checkins.reload().catch(() => {})
loadStatus()

// keep showing the loaded data while the list reloads (no flip to "Check In" during a reload)
const lastLog = computed(() => checkins.data?.[0] || null)

const statusLoadFailed = computed(() => !checkins.data && !!checkins.list.error && !checkins.list.loading)

const lastLogType = computed(() => {
	return lastLog.value?.log_type === "IN" ? "check-in" : "check-out"
})

// same rule as EmployeeCheckin.validate_log_sequence: an IN from an earlier day does not count
const isCheckedIn = computed(
	() => lastLog.value?.log_type === "IN" && dayjs(lastLog.value.time).isToday()
)

const nextAction = computed(() => {
	return isCheckedIn.value
		? { action: "OUT", label: __("Check Out"), title: __("Check-out") }
		: { action: "IN", label: __("Check In"), title: __("Check-in") }
})

const geolocationRequired = computed(() => !!settings.data?.allow_geolocation_tracking)

const canConfirm = computed(() => {
	if (sheetState.value === "saving") return false
	if (geolocationRequired.value && locationState.value !== "ok") return false
	return true
})

const confirmLabel = computed(() => {
	if (sheetState.value === "saving") return __("Saving {0}...", [pendingAction.value.title])
	if (sheetState.value === "error") return __("Try again")
	if (geolocationRequired.value && locationState.value === "locating") return __("Getting your location...")
	return __("Confirm {0}", [pendingAction.value.label])
})

function handleLocationSuccess(position) {
	latitude.value = position.coords.latitude
	longitude.value = position.coords.longitude
	locationState.value = "ok"

	locationStatus.value = [
		__("Latitude: {0}°", [Number(latitude.value).toFixed(5)]),
		__("Longitude: {0}°", [Number(longitude.value).toFixed(5)]),
	].join(", ")
}

function handleLocationError(error) {
	locationState.value = "error"
	if (error?.code === 1) {
		locationStatus.value = __(
			"Location permission is blocked. Allow location for this app in your phone settings, then tap Retry location."
		)
		return
	}
	locationStatus.value = __("Unable to retrieve your location")
	if (error) locationStatus.value += `: ERROR(${error.code}): ${error.message}`
}

const fetchLocation = () => {
	latitude.value = 0
	longitude.value = 0
	if (!navigator.geolocation) {
		locationState.value = "error"
		locationStatus.value = __("Geolocation is not supported by your current browser")
	} else {
		locationState.value = "locating"
		locationStatus.value = __("Locating...")
		navigator.geolocation.getCurrentPosition(handleLocationSuccess, handleLocationError, {
			enableHighAccuracy: true,
			timeout: 20000,
			maximumAge: 60000,
		})
	}
}

const openSheet = () => {
	// the action is fixed for this sheet: a list reload can no longer change what is sent
	pendingAction.value = { ...nextAction.value }
	sheetState.value = "idle"
	savedLog.value = null
	errorMessages.value = []
	locationState.value = "idle"
	locationStatus.value = ""
	latitude.value = 0
	longitude.value = 0

	now.value = dayjs()
	clearInterval(clockTimer)
	clockTimer = setInterval(() => (now.value = dayjs()), 1000)

	if (geolocationRequired.value) fetchLocation()

	allowClose = false
	sheetOpen.value = true
}

// ion-modal asks this before every dismiss (swipe, backdrop, back button, is-open=false)
const canDismiss = async () => allowClose

const closeSheet = () => {
	if (sheetState.value === "saving") return
	clearTimeout(autoCloseTimer)
	allowClose = true
	sheetOpen.value = false
}

const onSheetDismissed = () => {
	sheetOpen.value = false
	allowClose = false
	clearInterval(clockTimer)
	clearTimeout(autoCloseTimer)
	loadStatus()
}

const stripHtml = (text) => {
	const div = document.createElement("div")
	div.innerHTML = text
	return (div.textContent || div.innerText || "").trim()
}

const saveLog = createResource({ url: "hrms.api.create_employee_checkin" })

const submitLog = () => {
	if (!canConfirm.value) return

	sheetState.value = "saving"
	errorMessages.value = []

	saveLog
		.submit(
			{
				log_type: pendingAction.value.action,
				latitude: latitude.value,
				longitude: longitude.value,
			},
			{
				onSuccess(data) {
					savedLog.value = data
					sheetState.value = "success"
					loadStatus()
					autoCloseTimer = setTimeout(closeSheet, 2500)
				},
				onError(error) {
					const messages = (error?.messages || []).map(stripHtml).filter(Boolean)
					errorMessages.value = messages.length
						? messages
						: [
								__(
									"No connection to the server. Your {0} is NOT saved. Check your internet and tap Try again.",
									[pendingAction.value.title]
								),
						  ]
					sheetState.value = "error"
					// e.g. "already checked out" after a lost response: show the real state outside the sheet
					if (error?.exc_type === "CheckinSequenceError") loadStatus()
				},
			}
		)
		.catch(() => {})
}

onMounted(() => {
	socket.emit("doctype_subscribe", DOCTYPE)
	socket.on("list_update", (data) => {
		if (data.doctype == DOCTYPE) {
			loadStatus()
		}
	})
})

onBeforeUnmount(() => {
	clearInterval(clockTimer)
	clearTimeout(autoCloseTimer)
	socket.emit("doctype_unsubscribe", DOCTYPE)
	socket.off("list_update")
})
</script>

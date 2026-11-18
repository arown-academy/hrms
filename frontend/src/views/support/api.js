// Complaints & Feedback = Support Tickets of the Arown LMS support desk (arown_lms.api.support), the same
// tickets students raise from the LMS app and staff work on in the LMS portal / desk.

const BASE = "/api/method/arown_lms.api.support."

function csrf() {
	return window.frappe?.csrf_token || window.csrf_token || "fetch"
}

function errorText(result, fallback) {
	if (result?._server_messages) {
		try {
			const messages = JSON.parse(result._server_messages).map((m) => JSON.parse(m).message)
			const text = messages.join("\n").replace(/<[^>]+>/g, "")
			if (text) return text
		} catch (e) {
			/* fall through */
		}
	}
	return (result?.exception || result?.message || fallback || "Something went wrong").toString().replace(/<[^>]+>/g, "")
}

async function parse(response) {
	const result = await response.json().catch(() => ({}))
	if (!response.ok) throw new Error(errorText(result, response.statusText))
	return result.message
}

export async function get(method, params = {}) {
	const query = new URLSearchParams()
	for (const [key, value] of Object.entries(params)) {
		if (value !== undefined && value !== null && value !== "") query.append(key, value)
	}
	return parse(await fetch(`${BASE}${method}?${query}`, { headers: { Accept: "application/json" } }))
}

export async function post(method, params = {}) {
	return parse(
		await fetch(`${BASE}${method}`, {
			method: "POST",
			headers: { "Content-Type": "application/json", Accept: "application/json", "X-Frappe-CSRF-Token": csrf() },
			body: JSON.stringify(params),
		})
	)
}

export async function uploadFile(ticket, file) {
	const form = new FormData()
	form.append("ticket", ticket)
	form.append("file", file, file.name)
	return parse(
		await fetch(`${BASE}upload_ticket_file`, {
			method: "POST",
			headers: { Accept: "application/json", "X-Frappe-CSRF-Token": csrf() },
			body: form,
		})
	)
}

export const STATUS_CLASS = {
	Open: "bg-blue-100 text-blue-700",
	Assigned: "bg-blue-100 text-blue-700",
	"In Progress": "bg-yellow-100 text-yellow-800",
	"Waiting on Requester": "bg-orange-100 text-orange-700",
	Resolved: "bg-green-100 text-green-700",
	Closed: "bg-gray-100 text-gray-600",
	Rejected: "bg-red-100 text-red-700",
}

export const FEEDBACK_TYPES = ["Suggestion", "Appreciation"]

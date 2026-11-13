import { createResource } from "frappe-ui"
import { employeeResource } from "./employee"

// Expense Request (arown) = step 1 of an expense; API arown.arown.doctype.expense_request.expense_request
const API = "arown.arown.doctype.expense_request.expense_request"

const transformRequestData = (data) => {
	return data.map((request) => {
		request.doctype = "Expense Request"
		return request
	})
}

export const myExpenseRequests = createResource({
	url: `${API}.get_expense_requests`,
	params: {
		employee: employeeResource.data.name,
		limit: 10,
	},
	auto: true,
	cache: "hrms:my_expense_requests",
	transform(data) {
		return transformRequestData(data)
	},
})

// requests waiting on this user at their own step
export const teamExpenseRequests = createResource({
	url: `${API}.get_expense_requests`,
	params: {
		employee: employeeResource.data.name,
		approver_id: employeeResource.data.user_id,
		for_approval: 1,
		limit: 10,
	},
	auto: true,
	cache: "hrms:team_expense_requests",
	transform(data) {
		return transformRequestData(data)
	},
})

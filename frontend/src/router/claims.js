const routes = [
	// Expense Request (arown) = step 1 of an expense; the claim is made from an approved request
	{
		name: "ExpenseRequestListView",
		path: "/expense-requests",
		component: () => import("@/views/expense_request/List.vue"),
	},
	{
		name: "ExpenseRequestFormView",
		path: "/expense-requests/new",
		component: () => import("@/views/expense_request/Form.vue"),
	},
	{
		name: "ExpenseRequestDetailView",
		path: "/expense-requests/:id",
		props: true,
		component: () => import("@/views/expense_request/Form.vue"),
	},
	{
		name: "ExpenseClaimListView",
		path: "/expense-claims",
		component: () => import("@/views/expense_claim/List.vue"),
	},
	{
		name: "ExpenseClaimFormView",
		path: "/expense-claims/new",
		component: () => import("@/views/expense_claim/Form.vue"),
	},
	{
		name: "ExpenseClaimDetailView",
		path: "/expense-claims/:id",
		props: true,
		component: () => import("@/views/expense_claim/Form.vue"),
	},
]

export default routes

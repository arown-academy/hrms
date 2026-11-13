<template>
	<ion-page>
		<ListView
			doctype="Expense Request"
			:pageTitle="__('Expense Requests')"
			:tabButtons="TAB_BUTTONS"
			:fields="EXPENSE_REQUEST_FIELDS"
			:filterConfig="FILTER_CONFIG"
		/>
	</ion-page>
</template>

<script setup>
import { IonPage } from "@ionic/vue"
import { inject } from "vue"
import ListView from "@/components/ListView.vue"

const __ = inject("$translate")
const TAB_BUTTONS = ["My Requests", "Team Requests"] // __("My Requests"), __("Team Requests")
const EXPENSE_REQUEST_FIELDS = [
	"name",
	"employee",
	"employee_name",
	"expense_category",
	"purpose",
	"estimated_amount",
	"currency",
	"request_date",
	"status",
	"docstatus",
	"expense_claim",
]

const FILTER_CONFIG = [
	{
		fieldname: "status",
		fieldtype: "Select",
		label: __("Status"),
		options: ["Draft", "Pending Approval", "Approved", "Rejected", "Claimed"],
	},
	{
		fieldname: "expense_category",
		fieldtype: "Select",
		label: __("Expense Category"),
		options: ["Travel", "Food", "Local Conveyance", "Accommodation", "Office Supplies", "Client Entertainment", "Other"],
	},
	{
		fieldname: "employee",
		fieldtype: "Link",
		label: __("Employee"),
		options: "Employee",
	},
	{ fieldname: "request_date", fieldtype: "Date", label: __("Request Date") },
]
</script>

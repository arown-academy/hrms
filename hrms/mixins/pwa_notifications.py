# # Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# # For license information, please see license.txt
# import frappe
# from frappe import bold
#
#
# class PWANotificationsMixin:
# 	"""Mixin class for managing PWA updates"""
#
# 	def notify_approval_status(self):
# 		"""Send Leave Application, Expense Claim & Shift Request Approval status notification - to employees"""
# 		status_field = self._get_doc_status_field()
# 		status = self.get(status_field)
#
# 		if self.has_value_changed(status_field) and status in ["Approved", "Rejected"]:
# 			from_user = frappe.session.user
# 			from_user_name = self._get_user_name(from_user)
# 			to_user = self._get_employee_user()
#
# 			if from_user == to_user:
# 				return
#
# 			notification = frappe.new_doc("PWA Notification")
# 			notification.from_user = from_user
# 			notification.to_user = to_user
#
# 			notification.message = f"{bold('Your')} {bold(self.doctype)} {self.name} has been {bold(status)} by {bold(from_user_name)}"
#
# 			notification.reference_document_type = self.doctype
# 			notification.reference_document_name = self.name
# 			notification.insert(ignore_permissions=True)
#
# 	def notify_approver(self):
# 		"""Send new Leave Application, Expense Claim & Shift Request request notification - to approvers"""
# 		from_user = self._get_employee_user()
# 		to_user = self._get_doc_approver()
#
# 		if not to_user or from_user == to_user:
# 			return
#
# 		notification = frappe.new_doc("PWA Notification")
# 		notification.message = (
# 			f"{bold(self.employee_name)} raised a new {bold(self.doctype)} for approval: {self.name}"
# 		)
# 		notification.from_user = from_user
# 		notification.to_user = to_user
#
# 		notification.reference_document_type = self.doctype
# 		notification.reference_document_name = self.name
# 		notification.insert(ignore_permissions=True)
#
# 	def _get_doc_status_field(self) -> str:
# 		APPROVAL_STATUS_FIELD = {
# 			"Leave Application": "status",
# 			"Expense Claim": "approval_status",
# 			"Shift Request": "status",
# 		}
# 		return APPROVAL_STATUS_FIELD[self.doctype]
#
# 	def _get_doc_approver(self) -> str:
# 		APPROVER_FIELD = {
# 			"Leave Application": "leave_approver",
# 			"Expense Claim": "expense_approver",
# 			"Shift Request": "approver",
# 		}
# 		approver_field = APPROVER_FIELD[self.doctype]
# 		return self.get(approver_field)
#
# 	def _get_employee_user(self) -> str:
# 		return frappe.db.get_value("Employee", self.employee, "user_id", cache=True)
#
# 	def _get_user_name(self, user) -> str:
# 		return frappe.db.get_value("User", user, "full_name", cache=True)


# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import bold


class PWANotificationsMixin:
	"""Mixin class for managing PWA updates"""

	def notify_approval_status(self):
		"""Send approval status notification to the employee."""

		status_field = self._get_doc_status_field()
		status = self.get(status_field)

		if self.has_value_changed(status_field) and status in ["Approved", "Rejected"]:
			from_user = frappe.session.user
			from_user_name = self._get_user_name(from_user)
			to_user = self._get_employee_user()

			if not to_user or from_user == to_user:
				return

			notification = frappe.new_doc("PWA Notification")

			notification.from_user = from_user
			notification.to_user = to_user

			notification.message = (
				f"{bold('Your')} {bold(self.doctype)} {self.name} "
				f"has been {bold(status)} by {bold(from_user_name)}"
			)

			notification.reference_document_type = self.doctype
			notification.reference_document_name = self.name

			notification.insert(ignore_permissions=True)

	def notify_approver(self):
		"""
		Send new Leave Application / Expense Claim / Shift Request
		notification to all configured approvers.
		"""

		from_user = self._get_employee_user()
		approvers = self._get_doc_approvers()

		if not approvers:
			return

		for to_user in approvers:

			# Do not notify the employee who created the request
			if not to_user or from_user == to_user:
				continue

			notification = frappe.new_doc("PWA Notification")

			notification.message = (
				f"{bold(self.employee_name)} raised a new "
				f"{bold(self.doctype)} for approval: {self.name}"
			)

			notification.from_user = from_user
			notification.to_user = to_user

			notification.reference_document_type = self.doctype
			notification.reference_document_name = self.name

			notification.insert(ignore_permissions=True)

	def _get_doc_status_field(self) -> str:
		APPROVAL_STATUS_FIELD = {
			"Leave Application": "status",
			"Expense Claim": "approval_status",
			"Shift Request": "status",
		}

		return APPROVAL_STATUS_FIELD[self.doctype]

	def _get_doc_approvers(self) -> list:
		"""
		Get all approvers configured on the Employee.
		"""

		if not self.employee:
			return []

		employee = frappe.get_doc("Employee", self.employee)

		if self.doctype == "Leave Application":
			return self._get_leave_approvers(employee)

		if self.doctype == "Expense Claim":
			return self._get_expense_approvers(employee)

		if self.doctype == "Shift Request":
			approver = self.get("approver")

			if approver:
				return [approver]

			return []

		return []

	def _get_leave_approvers(self, employee) -> list:
		"""
		Get all Leave Approvers from Employee.

		Primary:
			leave_approver

		Level 2:
			custom_leave_approver_l2

		Level 3:
			custom_leave_approver_l3
		"""

		approvers = [
			employee.get("leave_approver"),
			employee.get("custom_leave_approver_l2"),
			employee.get("custom_leave_approver_l3"),
		]

		return self._remove_duplicate_users(approvers)

	def _get_expense_approvers(self, employee) -> list:
		"""
		Get all Expense Approvers from Employee.

		Primary:
			expense_approver

		Level 2:
			custom_expense_approver_l2
		"""

		approvers = [
			employee.get("expense_approver"),
			employee.get("custom_expense_approver_l2"),
		]

		return self._remove_duplicate_users(approvers)

	def _remove_duplicate_users(self, users) -> list:
		"""Remove empty and duplicate users while preserving order."""

		result = []
		seen = set()

		for user in users or []:
			if user and user not in seen:
				result.append(user)
				seen.add(user)

		return result

	def _get_employee_user(self) -> str:
		return frappe.db.get_value(
			"Employee",
			self.employee,
			"user_id",
			cache=True,
		)

	def _get_user_name(self, user) -> str:
		return frappe.db.get_value(
			"User",
			user,
			"full_name",
			cache=True,
		)

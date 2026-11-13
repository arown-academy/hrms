import frappe


def execute():
	"""Remove the "HR" sidebar that Frappe's sidebar migration built by merging the HR areas.

	Before the split, HR Setup, Tenure, Recruitment, Shift & Attendance, Leaves, Expenses and
	Performance were all in module "HR", so the migration merged their sidebars into one "HR"
	sidebar whose first page was Expenses, and every HR desktop icon opened Expenses. Each area now
	has its own module and ships its own sidebar (hrms/<module>/sidebar/), and "HR" is a
	code-only module (hooks.code_only_modules), so the merged row is left over.

	Only that generated row is removed: one that is not standard (no app file backs it) and was
	built by the merge (merged_from is set). A sidebar someone made on the site is left alone.
	"""
	if not frappe.db.exists("DocType", "Sidebar"):
		return

	row = frappe.db.get_value("Sidebar", "HR", ["module", "standard", "merged_from"], as_dict=True)
	if not row or row.module != "HR" or row.standard or not row.merged_from:
		return

	# on_trash also removes any dock row that points at this sidebar
	frappe.delete_doc("Sidebar", "HR", force=True, ignore_permissions=True)

	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")

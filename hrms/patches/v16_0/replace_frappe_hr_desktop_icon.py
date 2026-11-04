import frappe


def execute():
	# "Arown HR" (desktop_icon/arown_hr.json) is the app icon now; the auto-created "Frappe HR" icon
	# was a duplicate whose /desk/people link failed ("Page people not found")
	if not frappe.db.exists("Desktop Icon", "Arown HR"):
		return

	# icons still under "Frappe HR" (e.g. created on the site) would disappear with their parent
	frappe.db.set_value(
		"Desktop Icon", {"parent_icon": "Frappe HR"}, "parent_icon", "Arown HR", update_modified=False
	)
	frappe.delete_doc("Desktop Icon", "Frappe HR", ignore_missing=True, force=True)

	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")

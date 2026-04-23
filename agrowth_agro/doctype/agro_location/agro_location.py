import frappe
from frappe.model.document import Document


class AgroLocation(Document):
    def after_insert(self):
        self._ensure_warehouse()

    def _ensure_warehouse(self):
        try:
            parent_warehouse = frappe.db.get_value("Agro Field", self.field, "warehouse_id")
            existing = frappe.db.get_value(
                "Warehouse",
                {"warehouse_name": self.location_name, "company": self.company},
                "name"
            )
            if existing:
                self.db_set("warehouse_id", existing, update_modified=False)
                return
            doc = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": self.location_name,
                "company": self.company,
                "parent_warehouse": parent_warehouse or "",
                "is_group": 0,
            })
            doc.insert(ignore_permissions=True)
            self.db_set("warehouse_id", doc.name, update_modified=False)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "AgroLocation.after_insert: warehouse creation failed")

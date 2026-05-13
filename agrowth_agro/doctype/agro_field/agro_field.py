import frappe
from frappe.model.document import Document
from frappe import _


class AgroField(Document):
    def after_insert(self):
        self._ensure_warehouse()

    def on_update(self):
        if self.warehouse_id and self.has_value_changed("field_name"):
            self._rename_warehouse()

    def on_trash(self):
        if self.warehouse_id:
            try:
                frappe.db.set_value("Warehouse", self.warehouse_id, "disabled", 1)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "AgroField.on_trash: warehouse disable failed")

    def before_delete(self):
        lots = frappe.db.count("Agro Lot", {"field": self.name, "company": self.company})
        if lots:
            frappe.throw(
                _("No se puede eliminar el campo {0}: tiene {1} lote(s) asociado(s)").format(
                    self.field_name, lots
                )
            )

    def _ensure_warehouse(self):
        try:
            existing = frappe.db.get_value(
                "Warehouse",
                {"warehouse_name": self.field_name, "company": self.company},
                "name"
            )
            if existing:
                self.db_set("warehouse_id", existing, update_modified=False)
                return
            doc = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": self.field_name,
                "company": self.company,
                "is_group": 0,
            })
            doc.insert(ignore_permissions=True)
            self.db_set("warehouse_id", doc.name, update_modified=False)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "AgroField.after_insert: warehouse creation failed")

    def _rename_warehouse(self):
        try:
            old_warehouse = self.warehouse_id
            existing = frappe.db.get_value(
                "Warehouse",
                {"warehouse_name": self.field_name, "company": self.company},
                "name"
            )
            if existing and existing != old_warehouse:
                self.db_set("warehouse_id", existing, update_modified=False)
                return
            wh_doc = frappe.get_doc("Warehouse", old_warehouse)
            wh_doc.warehouse_name = self.field_name
            wh_doc.save(ignore_permissions=True)
            new_name = frappe.db.get_value(
                "Warehouse",
                {"warehouse_name": self.field_name, "company": self.company},
                "name"
            )
            if new_name and new_name != old_warehouse:
                self.db_set("warehouse_id", new_name, update_modified=False)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "AgroField.on_update: warehouse rename failed")

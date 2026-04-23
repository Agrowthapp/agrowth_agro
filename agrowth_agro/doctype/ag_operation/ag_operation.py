import frappe
from frappe.model.document import Document
from frappe import _


class AgOperation(Document):
    def validate(self):
        self._validate_items()

    def _validate_items(self):
        for idx, item in enumerate(self.items or [], start=1):
            if not item.service_name:
                frappe.throw(
                    _("Fila {0}: el campo 'Insumo / Servicio' es obligatorio").format(idx)
                )

import frappe
from frappe.model.document import Document
from frappe import _


class AgCampaignLot(Document):
    def validate(self):
        self._validate_no_duplicate()

    def _validate_no_duplicate(self):
        existing = frappe.db.exists(
            "Ag Campaign Lot",
            {
                "campaign": self.campaign,
                "lot": self.lot,
                "company": self.company,
                "name": ["!=", self.name],
            },
        )
        if existing:
            frappe.throw(
                _("El lote {0} ya está asignado a esta campaña").format(self.lot)
            )

    def before_delete(self):
        operations = frappe.db.count(
            "Ag Operation", {"campaign_lot": self.name, "company": self.company}
        )
        if operations:
            frappe.throw(
                _("No se puede eliminar: el lote de campaña tiene {0} operación(es) registrada(s)").format(
                    operations
                )
            )

import frappe
from frappe.model.document import Document
from frappe import _


class AgroCampaign(Document):
    def validate(self):
        self._validate_dates()

    def _validate_dates(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw(
                _("La fecha de fin ({0}) no puede ser anterior a la fecha de inicio ({1})").format(
                    self.end_date, self.start_date
                )
            )

    def before_delete(self):
        lots = frappe.db.count("Ag Campaign Lot", {"campaign": self.name, "company": self.company})
        if lots:
            frappe.throw(
                _("No se puede eliminar la campaña {0}: tiene {1} lote(s) asignado(s)").format(
                    self.campaign_name, lots
                )
            )

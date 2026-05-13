import frappe
from frappe.model.document import Document
from frappe import _


class AgroLot(Document):
    def before_delete(self):
        operations = frappe.db.sql(
            """
            SELECT COUNT(op.name)
            FROM `tabAg Operation` op
            JOIN `tabAg Campaign Lot` cl ON cl.name = op.campaign_lot
            WHERE cl.lot = %s AND op.company = %s
            """,
            (self.name, self.company),
        )[0][0]

        if operations:
            frappe.throw(
                _("No se puede eliminar el lote {0}: tiene {1} operación(es) registrada(s). "
                  "El historial operativo debe preservarse.").format(self.lot_name, operations)
            )

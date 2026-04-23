import frappe
from frappe.utils import flt
from frappe import _


def _map_item(row):
    return {
        "id": str(row.get("name") or ""),
        "itemId": row.get("item") or None,
        "serviceName": str(row.get("service_name") or ""),
        "dose": flt(row.get("dose")) or None,
        "uom": row.get("uom") or None,
        "quantityTotal": flt(row.get("quantity_total")) or None,
        "costTotal": flt(row.get("cost_total")) or None,
        "costPerHa": flt(row.get("cost_per_ha")) or None,
        "supplier": row.get("supplier") or None,
    }


def _map_operation(doc_or_row, items=None):
    return {
        "id": str(doc_or_row.get("name") or ""),
        "campaignLotId": str(doc_or_row.get("campaign_lot") or ""),
        "operationType": str(doc_or_row.get("operation_type") or ""),
        "date": str(doc_or_row.get("date") or ""),
        "performedBy": doc_or_row.get("performed_by") or None,
        "notes": doc_or_row.get("notes") or None,
        "items": items or [],
    }


def _load_operation(company_id, operation_id):
    rows = frappe.get_all(
        "Ag Operation",
        filters=[["name", "=", operation_id], ["company", "=", company_id]],
        fields=["name", "campaign_lot", "operation_type", "date", "performed_by", "notes"],
        limit_page_length=1,
    )
    return rows[0] if rows else None


def _get_operation_with_items(operation_id):
    doc = frappe.get_doc("Ag Operation", operation_id)
    items = [_map_item(item.as_dict()) for item in (doc.items or [])]
    return _map_operation(doc.as_dict(), items)


@frappe.whitelist()
def list_operations(company_id, campaign_lot_id=None, campaign_id=None, lot_id=None, operation_type=None):
    filters = [["company", "=", company_id]]
    if campaign_lot_id:
        filters.append(["campaign_lot", "=", campaign_lot_id])
    if operation_type:
        filters.append(["operation_type", "=", operation_type])
    if campaign_id and not campaign_lot_id:
        lot_ids = frappe.get_all(
            "Ag Campaign Lot",
            filters=[["campaign", "=", campaign_id], ["company", "=", company_id]],
            pluck="name",
        )
        if not lot_ids:
            return []
        filters.append(["campaign_lot", "in", lot_ids])
    if lot_id and not campaign_lot_id:
        cl_ids = frappe.get_all(
            "Ag Campaign Lot",
            filters=[["lot", "=", lot_id], ["company", "=", company_id]],
            pluck="name",
        )
        if not cl_ids:
            return []
        filters.append(["campaign_lot", "in", cl_ids])

    rows = frappe.get_all(
        "Ag Operation",
        filters=filters,
        fields=["name", "campaign_lot", "operation_type", "date", "performed_by", "notes"],
        order_by="date desc",
    )
    return [_map_operation(r) for r in rows]


@frappe.whitelist()
def get_operation(company_id, operation_id):
    row = _load_operation(company_id, operation_id)
    if not row:
        return None
    return _get_operation_with_items(operation_id)


@frappe.whitelist()
def create_operation(company_id, campaign_lot_id, operation_type, date,
                     performed_by=None, notes=None, items=None):
    doc = frappe.new_doc("Ag Operation")
    doc.company = company_id
    doc.campaign_lot = campaign_lot_id
    doc.operation_type = operation_type
    doc.date = date
    if performed_by:
        doc.performed_by = performed_by
    if notes:
        doc.notes = notes
    for item in (items or []):
        doc.append("items", {
            "item": item.get("item_id"),
            "service_name": item.get("service_name"),
            "dose": item.get("dose"),
            "uom": item.get("uom"),
            "quantity_total": item.get("quantity_total"),
            "cost_total": item.get("cost_total"),
            "cost_per_ha": item.get("cost_per_ha"),
            "supplier": item.get("supplier"),
        })
    doc.insert(ignore_permissions=True)
    return _get_operation_with_items(doc.name)


@frappe.whitelist()
def update_operation(company_id, operation_id, operation_type=None, date=None,
                     performed_by=None, notes=None, items=None):
    row = _load_operation(company_id, operation_id)
    if not row:
        frappe.throw(_("Operación no encontrada: {0}").format(operation_id))
    doc = frappe.get_doc("Ag Operation", operation_id)
    if operation_type is not None:
        doc.operation_type = operation_type
    if date is not None:
        doc.date = date
    if performed_by is not None:
        doc.performed_by = performed_by
    if notes is not None:
        doc.notes = notes
    if items is not None:
        doc.items = []
        for item in items:
            doc.append("items", {
                "item": item.get("item_id"),
                "service_name": item.get("service_name"),
                "dose": item.get("dose"),
                "uom": item.get("uom"),
                "quantity_total": item.get("quantity_total"),
                "cost_total": item.get("cost_total"),
                "cost_per_ha": item.get("cost_per_ha"),
                "supplier": item.get("supplier"),
            })
    doc.save(ignore_permissions=True)
    return _get_operation_with_items(doc.name)


@frappe.whitelist()
def delete_operation(company_id, operation_id):
    row = _load_operation(company_id, operation_id)
    if not row:
        frappe.throw(_("Operación no encontrada: {0}").format(operation_id))
    frappe.delete_doc("Ag Operation", operation_id, ignore_permissions=True)
    return True

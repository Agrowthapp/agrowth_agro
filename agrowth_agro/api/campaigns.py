import frappe
from frappe import _


def _map_campaign(row):
    return {
        "id": str(row.get("name") or ""),
        "code": str(row.get("code") or ""),
        "name": str(row.get("campaign_name") or ""),
        "startDate": str(row.get("start_date") or ""),
        "endDate": str(row.get("end_date") or "") or None,
        "status": str(row.get("status") or "activa"),
    }


def _load_campaign(company_id, campaign_id):
    rows = frappe.get_all(
        "Agro Campaign",
        filters=[["name", "=", campaign_id], ["company", "=", company_id]],
        fields=["name", "code", "campaign_name", "start_date", "end_date", "status"],
        limit_page_length=1,
    )
    return rows[0] if rows else None


@frappe.whitelist()
def list_campaigns(company_id):
    rows = frappe.get_all(
        "Agro Campaign",
        filters=[["company", "=", company_id]],
        fields=["name", "code", "campaign_name", "start_date", "end_date", "status"],
        order_by="start_date desc",
    )
    return [_map_campaign(r) for r in rows]


@frappe.whitelist()
def get_campaign(company_id, campaign_id):
    row = _load_campaign(company_id, campaign_id)
    return _map_campaign(row) if row else None


@frappe.whitelist()
def create_campaign(company_id, code, name, start_date, end_date=None, status="activa"):
    doc = frappe.new_doc("Agro Campaign")
    doc.company = company_id
    doc.code = code
    doc.campaign_name = name
    doc.start_date = start_date
    doc.status = status
    if end_date:
        doc.end_date = end_date
    doc.insert(ignore_permissions=True)
    return _map_campaign(frappe.get_doc("Agro Campaign", doc.name).as_dict())


@frappe.whitelist()
def update_campaign(company_id, campaign_id, code=None, name=None, start_date=None, end_date=None, status=None):
    row = _load_campaign(company_id, campaign_id)
    if not row:
        frappe.throw(_("Campaña no encontrada: {0}").format(campaign_id))
    doc = frappe.get_doc("Agro Campaign", campaign_id)
    if code is not None:
        doc.code = code
    if name is not None:
        doc.campaign_name = name
    if start_date is not None:
        doc.start_date = start_date
    if end_date is not None:
        doc.end_date = end_date
    if status is not None:
        doc.status = status
    doc.save(ignore_permissions=True)
    return _map_campaign(doc.as_dict())


@frappe.whitelist()
def delete_campaign(company_id, campaign_id):
    row = _load_campaign(company_id, campaign_id)
    if not row:
        frappe.throw(_("Campaña no encontrada: {0}").format(campaign_id))
    frappe.delete_doc("Agro Campaign", campaign_id, ignore_permissions=True)
    return True

import frappe
from frappe import _

_AUTO_COLORS = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#EC4899", "#14B8A6", "#F97316",
]


def _map_campaign_lot(row):
    return {
        "id": str(row.get("name") or ""),
        "campaignId": str(row.get("campaign") or ""),
        "lotId": str(row.get("lot") or ""),
        "state": str(row.get("state") or "planificado"),
        "crop": row.get("crop") or None,
        "variety": row.get("variety") or None,
        "colorKey": row.get("color_key") or None,
        "notes": row.get("notes") or None,
    }


def _load_campaign_lot(company_id, campaign_lot_id):
    rows = frappe.get_all(
        "Ag Campaign Lot",
        filters=[["name", "=", campaign_lot_id], ["company", "=", company_id]],
        fields=["name", "campaign", "lot", "state", "crop", "variety", "color_key", "notes"],
        limit_page_length=1,
    )
    return rows[0] if rows else None


def _next_color(company_id, campaign_id):
    """Pick the next auto color based on how many lots the campaign already has."""
    count = frappe.db.count("Ag Campaign Lot", {"campaign": campaign_id, "company": company_id})
    return _AUTO_COLORS[count % len(_AUTO_COLORS)]


@frappe.whitelist()
def list_campaign_lots(company_id, campaign_id=None, lot_id=None):
    filters = [["company", "=", company_id]]
    if campaign_id:
        filters.append(["campaign", "=", campaign_id])
    if lot_id:
        filters.append(["lot", "=", lot_id])
    rows = frappe.get_all(
        "Ag Campaign Lot",
        filters=filters,
        fields=["name", "campaign", "lot", "state", "crop", "variety", "color_key", "notes"],
        order_by="creation asc",
    )
    return [_map_campaign_lot(r) for r in rows]


@frappe.whitelist()
def assign_lot_to_campaign(company_id, campaign_id, lot_id, state="planificado",
                            crop=None, variety=None, color_key=None, notes=None):
    doc = frappe.new_doc("Ag Campaign Lot")
    doc.company = company_id
    doc.campaign = campaign_id
    doc.lot = lot_id
    doc.state = state
    doc.color_key = color_key or _next_color(company_id, campaign_id)
    if crop:
        doc.crop = crop
    if variety:
        doc.variety = variety
    if notes:
        doc.notes = notes
    doc.insert(ignore_permissions=True)
    return _map_campaign_lot(frappe.get_doc("Ag Campaign Lot", doc.name).as_dict())


@frappe.whitelist()
def update_campaign_lot(company_id, campaign_lot_id, state=None, crop=None,
                         variety=None, color_key=None, notes=None):
    row = _load_campaign_lot(company_id, campaign_lot_id)
    if not row:
        frappe.throw(_("Lote de campaña no encontrado: {0}").format(campaign_lot_id))
    doc = frappe.get_doc("Ag Campaign Lot", campaign_lot_id)
    if state is not None:
        doc.state = state
    if crop is not None:
        doc.crop = crop
    if variety is not None:
        doc.variety = variety
    if color_key is not None:
        doc.color_key = color_key
    if notes is not None:
        doc.notes = notes
    doc.save(ignore_permissions=True)
    return _map_campaign_lot(doc.as_dict())


@frappe.whitelist()
def remove_lot_from_campaign(company_id, campaign_lot_id):
    row = _load_campaign_lot(company_id, campaign_lot_id)
    if not row:
        frappe.throw(_("Lote de campaña no encontrado: {0}").format(campaign_lot_id))
    frappe.delete_doc("Ag Campaign Lot", campaign_lot_id, ignore_permissions=True)
    return True

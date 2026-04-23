import frappe
from frappe.utils import flt
from frappe import _


def _map_location(row):
    return {
        "id": str(row.get("name") or ""),
        "fieldId": str(row.get("field") or ""),
        "name": str(row.get("location_name") or ""),
        "locationType": str(row.get("location_type") or ""),
        "parentLocationId": row.get("parent_location") or None,
        "code": row.get("code") or None,
        "capacity": flt(row.get("capacity")) or None,
        "uom": row.get("uom") or None,
        "status": str(row.get("status") or "active"),
        "geometryJson": row.get("geometry_json") or None,
        "warehouseId": row.get("warehouse_id") or None,
    }


def _load_location(company_id, location_id):
    rows = frappe.get_all(
        "Agro Location",
        filters=[["name", "=", location_id], ["company", "=", company_id]],
        fields=["name", "field", "location_name", "location_type", "parent_location",
                "code", "capacity", "uom", "status", "geometry_json", "warehouse_id"],
        limit_page_length=1,
    )
    return rows[0] if rows else None


@frappe.whitelist()
def list_locations(company_id, field_id=None):
    filters = [["company", "=", company_id]]
    if field_id:
        filters.append(["field", "=", field_id])
    rows = frappe.get_all(
        "Agro Location",
        filters=filters,
        fields=["name", "field", "location_name", "location_type", "parent_location",
                "code", "capacity", "uom", "status", "geometry_json", "warehouse_id"],
        order_by="location_name asc",
    )
    return [_map_location(r) for r in rows]


@frappe.whitelist()
def get_location(company_id, location_id):
    row = _load_location(company_id, location_id)
    return _map_location(row) if row else None


@frappe.whitelist()
def create_location(company_id, field_id, name, location_type, status="active",
                    parent_location_id=None, code=None, capacity=None, uom=None, geometry_json=None):
    doc = frappe.new_doc("Agro Location")
    doc.company = company_id
    doc.field = field_id
    doc.location_name = name
    doc.location_type = location_type
    doc.status = status
    if parent_location_id:
        doc.parent_location = parent_location_id
    if code:
        doc.code = code
    if capacity is not None:
        doc.capacity = capacity
    if uom:
        doc.uom = uom
    if geometry_json:
        doc.geometry_json = geometry_json
    doc.insert(ignore_permissions=True)
    return _map_location(frappe.get_doc("Agro Location", doc.name).as_dict())


@frappe.whitelist()
def update_location(company_id, location_id, name=None, location_type=None, status=None,
                    parent_location_id=None, code=None, capacity=None, uom=None, geometry_json=None):
    row = _load_location(company_id, location_id)
    if not row:
        frappe.throw(_("Ubicación no encontrada: {0}").format(location_id))
    doc = frappe.get_doc("Agro Location", location_id)
    if name is not None:
        doc.location_name = name
    if location_type is not None:
        doc.location_type = location_type
    if status is not None:
        doc.status = status
    if parent_location_id is not None:
        doc.parent_location = parent_location_id
    if code is not None:
        doc.code = code
    if capacity is not None:
        doc.capacity = capacity
    if uom is not None:
        doc.uom = uom
    if geometry_json is not None:
        doc.geometry_json = geometry_json
    doc.save(ignore_permissions=True)
    return _map_location(doc.as_dict())


@frappe.whitelist()
def delete_location(company_id, location_id):
    row = _load_location(company_id, location_id)
    if not row:
        frappe.throw(_("Ubicación no encontrada: {0}").format(location_id))
    frappe.delete_doc("Agro Location", location_id, ignore_permissions=True)
    return True

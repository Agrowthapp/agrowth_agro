import frappe
from frappe.utils import flt
from frappe import _


def _map_field(row):
    return {
        "id": str(row.get("name") or ""),
        "name": str(row.get("field_name") or ""),
        "code": row.get("code") or None,
        "city": row.get("city") or None,
        "province": row.get("province") or None,
        "status": str(row.get("status") or "active"),
        "geometryJson": row.get("geometry_json") or None,
        "centerLat": flt(row.get("center_lat")) or None,
        "centerLng": flt(row.get("center_lng")) or None,
        "ownershipType": row.get("ownership_type") or None,
        "totalHa": flt(row.get("total_ha")) or None,
        "warehouseId": row.get("warehouse_id") or None,
    }


def _load_field(company_id, field_id):
    rows = frappe.get_all(
        "Agro Field",
        filters=[["name", "=", field_id], ["company", "=", company_id]],
        fields=["name", "field_name", "code", "city", "province", "status", "geometry_json", "center_lat", "center_lng",
                "ownership_type", "total_ha", "warehouse_id"],
        limit_page_length=1,
    )
    return rows[0] if rows else None


@frappe.whitelist()
def list_fields(company_id):
    rows = frappe.get_all(
        "Agro Field",
        filters=[["company", "=", company_id]],
        fields=["name", "field_name", "code", "city", "province", "status", "geometry_json", "center_lat", "center_lng",
                "ownership_type", "total_ha", "warehouse_id"],
        order_by="field_name asc",
    )
    return [_map_field(r) for r in rows]


@frappe.whitelist()
def get_field(company_id, field_id):
    row = _load_field(company_id, field_id)
    return _map_field(row) if row else None


@frappe.whitelist()
def create_field(company_id, name, status="active", code=None, city=None, province=None, geometry_json=None, ownership_type=None, total_ha=None):
    doc = frappe.new_doc("Agro Field")
    doc.company = company_id
    doc.field_name = name
    doc.status = status
    if code:
        doc.code = code
    if city:
        doc.city = city
    if province:
        doc.province = province
    if geometry_json:
        doc.geometry_json = geometry_json
        _set_centroid(doc, geometry_json)
    if ownership_type:
        doc.ownership_type = ownership_type
    if total_ha is not None:
        doc.total_ha = total_ha
    doc.insert(ignore_permissions=True)
    return _map_field(frappe.get_doc("Agro Field", doc.name).as_dict())


@frappe.whitelist()
def update_field(company_id, field_id, name=None, status=None, code=None, city=None, province=None, geometry_json=None, ownership_type=None):
    row = _load_field(company_id, field_id)
    if not row:
        frappe.throw(_("Campo no encontrado: {0}").format(field_id))
    doc = frappe.get_doc("Agro Field", field_id)
    if name is not None:
        doc.field_name = name
    if status is not None:
        doc.status = status
    if code is not None:
        doc.code = code
    if city is not None:
        doc.city = city
    if province is not None:
        doc.province = province
    if geometry_json is not None:
        doc.geometry_json = geometry_json
        _set_centroid(doc, geometry_json)
    if ownership_type is not None:
        doc.ownership_type = ownership_type
    doc.save(ignore_permissions=True)
    return _map_field(doc.as_dict())


@frappe.whitelist()
def delete_field(company_id, field_id):
    row = _load_field(company_id, field_id)
    if not row:
        frappe.throw(_("Campo no encontrado: {0}").format(field_id))
    frappe.delete_doc("Agro Field", field_id, ignore_permissions=True)
    return True


def _set_centroid(doc, geometry_json):
    """Best-effort centroid from GeoJSON bbox midpoint."""
    try:
        import json
        geo = json.loads(geometry_json)
        coords_type = geo.get("type")
        if coords_type == "Polygon":
            rings = geo.get("coordinates", [[]])
        elif coords_type == "MultiPolygon":
            rings = [r for poly in geo.get("coordinates", []) for r in poly]
        else:
            return
        lons = [p[0] for ring in rings for p in ring]
        lats = [p[1] for ring in rings for p in ring]
        if lons and lats:
            doc.center_lat = (min(lats) + max(lats)) / 2
            doc.center_lng = (min(lons) + max(lons)) / 2
    except Exception:
        pass

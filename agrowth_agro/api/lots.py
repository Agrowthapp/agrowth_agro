import json
import frappe
from frappe.utils import flt
from frappe import _


def _map_lot(row):
    return {
        "id": str(row.get("name") or ""),
        "name": str(row.get("lot_name") or ""),
        "fieldId": str(row.get("field") or ""),
        "geojson": row.get("geojson") or None,
        "areaHa": flt(row.get("area_ha")) or None,
        "centroidLat": flt(row.get("centroid_lat")) or None,
        "centroidLng": flt(row.get("centroid_lng")) or None,
        "bboxJson": row.get("bbox_json") or None,
        "status": str(row.get("status") or "activo"),
    }


def _load_lot(company_id, lot_id):
    rows = frappe.get_all(
        "Agro Lot",
        filters=[["name", "=", lot_id], ["company", "=", company_id]],
        fields=["name", "lot_name", "field", "geojson", "area_ha", "centroid_lat", "centroid_lng", "bbox_json", "status"],
        limit_page_length=1,
    )
    return rows[0] if rows else None


def _compute_geometry(doc, geojson_str):
    """Calculate area_ha, centroid and bbox from GeoJSON string."""
    try:
        geo = json.loads(geojson_str)
        coords_type = geo.get("type")
        if coords_type == "Polygon":
            rings = geo.get("coordinates", [[]])
        elif coords_type == "MultiPolygon":
            rings = [r for poly in geo.get("coordinates", []) for r in poly]
        else:
            return

        lons = [p[0] for ring in rings for p in ring]
        lats = [p[1] for ring in rings for p in ring]
        if not lons:
            return

        doc.centroid_lat = (min(lats) + max(lats)) / 2
        doc.centroid_lng = (min(lons) + max(lons)) / 2
        doc.bbox_json = json.dumps([min(lons), min(lats), max(lons), max(lats)])
        doc.area_ha = _spherical_area_ha(geo)
    except Exception:
        pass


def _spherical_area_ha(geo):
    import math
    R = 6378137.0

    def ring_area(ring):
        total = 0.0
        for i in range(len(ring) - 1):
            lon1, lat1 = ring[i][0], ring[i][1]
            lon2, lat2 = ring[i + 1][0], ring[i + 1][1]
            total += (math.radians(lon2) - math.radians(lon1)) * (
                2 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2))
            )
        return abs(total * R * R / 2)

    coords_type = geo.get("type")
    if coords_type == "Polygon":
        polygons = [geo.get("coordinates", [])]
    elif coords_type == "MultiPolygon":
        polygons = geo.get("coordinates", [])
    else:
        return 0.0

    total_sq_m = 0.0
    for poly in polygons:
        if not poly:
            continue
        outer = ring_area(poly[0])
        holes = sum(ring_area(h) for h in poly[1:])
        total_sq_m += max(0, outer - holes)

    return total_sq_m / 10000


@frappe.whitelist()
def list_lots(company_id, field_id=None, status=None):
    filters = [["company", "=", company_id]]
    if field_id:
        filters.append(["field", "=", field_id])
    if status:
        filters.append(["status", "=", status])
    rows = frappe.get_all(
        "Agro Lot",
        filters=filters,
        fields=["name", "lot_name", "field", "geojson", "area_ha", "centroid_lat", "centroid_lng", "bbox_json", "status"],
        order_by="lot_name asc",
    )
    return [_map_lot(r) for r in rows]


@frappe.whitelist()
def get_lot(company_id, lot_id):
    row = _load_lot(company_id, lot_id)
    return _map_lot(row) if row else None


@frappe.whitelist()
def create_lot(company_id, name, field_id, geojson=None, area_ha=None, status="activo"):
    doc = frappe.new_doc("Agro Lot")
    doc.company = company_id
    doc.lot_name = name
    doc.field = field_id
    doc.status = status
    if geojson:
        doc.geojson = geojson
        _compute_geometry(doc, geojson)
    elif area_ha is not None:
        doc.area_ha = flt(area_ha)
    doc.insert(ignore_permissions=True)
    return _map_lot(frappe.get_doc("Agro Lot", doc.name).as_dict())


@frappe.whitelist()
def update_lot(company_id, lot_id, name=None, field_id=None, geojson=None, area_ha=None, status=None):
    row = _load_lot(company_id, lot_id)
    if not row:
        frappe.throw(_("Lote no encontrado: {0}").format(lot_id))
    doc = frappe.get_doc("Agro Lot", lot_id)
    if name is not None:
        doc.lot_name = name
    if field_id is not None:
        doc.field = field_id
    if status is not None:
        doc.status = status
    if geojson is not None:
        doc.geojson = geojson
        _compute_geometry(doc, geojson)
    elif area_ha is not None:
        doc.area_ha = flt(area_ha)
    doc.save(ignore_permissions=True)
    return _map_lot(doc.as_dict())


@frappe.whitelist()
def delete_lot(company_id, lot_id):
    row = _load_lot(company_id, lot_id)
    if not row:
        frappe.throw(_("Lote no encontrado: {0}").format(lot_id))
    frappe.delete_doc("Agro Lot", lot_id, ignore_permissions=True)
    return True

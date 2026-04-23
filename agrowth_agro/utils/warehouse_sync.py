"""
Warehouse Sync — Agrowth Agro

Auto-creates / renames / disables ERPNext Warehouses in response to
Agro Field and Agro Location lifecycle events.

Rules:
- Non-fatal: all functions wrap in try/except and log via frappe.log_error.
- Idempotent: ensure_warehouse checks existence before inserting.
- Naming convention: "{entity_name} - {company_abbr}"
"""

import frappe


# ── Helpers ───────────────────────────────────────────────────────────────────


def _resolve_abbr(company: str) -> str:
    return frappe.db.get_value("Company", company, "abbr") or ""


def _expected_warehouse_name(entity_name: str, company: str) -> str:
    """Return the full ERPNext warehouse name: '{entity_name} - {abbr}'"""
    abbr = _resolve_abbr(company)
    return f"{entity_name} - {abbr}" if abbr else entity_name


def _root_warehouse(company: str):
    """Return the root (group) warehouse for the company, or None."""
    rows = frappe.get_all(
        "Warehouse",
        filters=[
            ["company", "=", company],
            ["is_group", "=", 1],
            ["parent_warehouse", "in", ["", None]],
        ],
        fields=["name"],
        limit_page_length=1,
    )
    return rows[0].name if rows else None


def _ensure_warehouse(entity_name: str, company: str, parent_warehouse=None) -> str:
    """Idempotent: create warehouse if it doesn't exist, return its full name."""
    expected_name = _expected_warehouse_name(entity_name, company)
    if frappe.db.exists("Warehouse", expected_name):
        return expected_name

    doc = frappe.new_doc("Warehouse")
    doc.warehouse_name = entity_name
    doc.company = company
    doc.is_group = 0
    if parent_warehouse:
        doc.parent_warehouse = parent_warehouse
    doc.insert(ignore_permissions=True)
    # ERPNext sets doc.name = "{entity_name} - {abbr}"
    return doc.name


# ── Agro Field hooks ──────────────────────────────────────────────────────────


def on_field_after_insert(doc, method):
    try:
        parent = _root_warehouse(doc.company)
        warehouse_name = _ensure_warehouse(doc.field_name, doc.company, parent)
        frappe.db.set_value(
            "Agro Field", doc.name, "warehouse_id", warehouse_name, update_modified=False
        )
    except Exception:
        frappe.log_error(
            f"Failed to create warehouse for Agro Field {doc.name}",
            "AgroWarehouseSync",
        )


def on_field_after_rename(doc, method, old=None, new=None, merge=False):
    try:
        old_warehouse_id = frappe.db.get_value("Agro Field", doc.name, "warehouse_id")
        if not old_warehouse_id:
            # No warehouse yet — create one with the new name
            on_field_after_insert(doc, method)
            return

        expected_new = _expected_warehouse_name(doc.field_name, doc.company)
        if old_warehouse_id != expected_new and not merge:
            frappe.rename_doc(
                "Warehouse", old_warehouse_id, expected_new, ignore_permissions=True
            )
            frappe.db.set_value(
                "Agro Field", doc.name, "warehouse_id", expected_new, update_modified=False
            )
    except Exception:
        frappe.log_error(
            f"Failed to rename warehouse for Agro Field {doc.name}",
            "AgroWarehouseSync",
        )


def on_field_on_trash(doc, method):
    try:
        warehouse_id = getattr(doc, "warehouse_id", None) or frappe.db.get_value(
            "Agro Field", doc.name, "warehouse_id"
        )
        if warehouse_id and frappe.db.exists("Warehouse", warehouse_id):
            frappe.db.set_value(
                "Warehouse", warehouse_id, "disabled", 1, update_modified=False
            )
    except Exception:
        frappe.log_error(
            f"Failed to disable warehouse for Agro Field {doc.name}",
            "AgroWarehouseSync",
        )


# ── Agro Location hooks ───────────────────────────────────────────────────────


def on_location_after_insert(doc, method):
    try:
        # Resolve parent: prefer campo warehouse, fall back to company root
        parent_warehouse = None
        if doc.field:
            parent_warehouse = frappe.db.get_value("Agro Field", doc.field, "warehouse_id")
        if not parent_warehouse:
            parent_warehouse = _root_warehouse(doc.company)

        warehouse_name = _ensure_warehouse(doc.location_name, doc.company, parent_warehouse)
        frappe.db.set_value(
            "Agro Location", doc.name, "warehouse_id", warehouse_name, update_modified=False
        )
    except Exception:
        frappe.log_error(
            f"Failed to create warehouse for Agro Location {doc.name}",
            "AgroWarehouseSync",
        )

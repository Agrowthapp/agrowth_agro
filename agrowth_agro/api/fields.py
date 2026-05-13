from __future__ import annotations

import frappe
from frappe import _


def _normalize_company(company_id: str | None) -> str:
    company = (company_id or "").strip()
    if not company:
        frappe.throw(_("company_id es obligatorio"))
    return company


@frappe.whitelist()
def list_fields(company_id: str | None = None):
    company = _normalize_company(company_id)
    return frappe.get_all(
        "Agro Field",
        filters={"company": company},
        fields=[
            "name",
            "field_name",
            "company",
            "ownership_type",
            "zone",
            "default_warehouse",
            "is_active",
            "modified",
        ],
        order_by="field_name asc",
    )


@frappe.whitelist()
def get_field(field_id: str, company_id: str | None = None):
    if not field_id:
        frappe.throw(_("field_id es obligatorio"))

    filters = {"name": field_id}
    if company_id:
        filters["company"] = _normalize_company(company_id)

    rows = frappe.get_all(
        "Agro Field",
        filters=filters,
        fields=[
            "name",
            "field_name",
            "company",
            "ownership_type",
            "zone",
            "default_warehouse",
            "is_active",
            "modified",
        ],
        limit_page_length=1,
    )
    return rows[0] if rows else None

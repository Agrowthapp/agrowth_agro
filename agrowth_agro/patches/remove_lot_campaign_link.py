"""
Patch: remove_lot_campaign_link
Migra la relación directa Agro Lot.campaign → Ag Campaign Lot (pivot).

Contexto:
  El campo `campaign` en `Agro Lot` era un link directo legado que
  predataba el diseño del pivot `Ag Campaign Lot`. Este patch:
  1. Por cada Agro Lot con campaign seteado, crea un Ag Campaign Lot
     si no existe ya un registro para ese par (campaign, lot).
  2. Limpia el campo `campaign` del Agro Lot.

Seguro de re-ejecutar: usa `or_ignore=True` al insertar el pivot.
"""

import frappe


def execute():
    lots_with_campaign = frappe.get_all(
        "Agro Lot",
        filters=[["campaign", "!=", ""]],
        fields=["name", "campaign", "company"],
    )

    migrated = 0
    skipped = 0

    for lot in lots_with_campaign:
        if not lot.get("campaign"):
            continue

        already_exists = frappe.db.exists(
            "Ag Campaign Lot",
            {"campaign": lot["campaign"], "lot": lot["name"], "company": lot["company"]},
        )

        if not already_exists:
            pivot = frappe.new_doc("Ag Campaign Lot")
            pivot.campaign = lot["campaign"]
            pivot.lot = lot["name"]
            pivot.company = lot["company"]
            pivot.state = "planificado"
            pivot.insert(ignore_permissions=True, ignore_if_duplicate=True)
            migrated += 1
        else:
            skipped += 1

        # Limpiar el campo legacy (requiere que el campo aún exista en el schema)
        try:
            frappe.db.set_value("Agro Lot", lot["name"], "campaign", None)
        except Exception:
            pass  # El campo puede ya no existir si se quitó del JSON antes

    frappe.db.commit()
    print(f"[remove_lot_campaign_link] Migrados: {migrated}, Ya existían: {skipped}")

import frappe


def _workspace_payload():
    return {
        "doctype": "Workspace",
        "label": "Agro",
        "title": "Agro",
        "module": "Agrowth Agro",
        "app": "agrowth_agro",
        "public": 1,
        "is_hidden": 0,
        "icon": "fa fa-leaf",
        "content": "[]",
    }


def ensure_workspaces():
    workspace_name = "Agro"
    if frappe.db.exists("Workspace", workspace_name):
        return

    workspace = frappe.get_doc(_workspace_payload())
    workspace.insert(ignore_permissions=True)

from frappe.boot import get_bootinfo


def get_data():
    return [
        {
            "module_name": "Livestock",
            "color": "green",
            "icon": "fa fa-leanpub",
            "type": "module",
            "label": "Ganaderia"
        },
        {
            "module_name": "Agro",
            "color": "green",
            "icon": "fa fa-leaf",
            "type": "module",
            "label": "Agrowth Agro"
        }
    ]

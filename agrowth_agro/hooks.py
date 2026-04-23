from . import __version__ as app_version

app_name = "agrowth_agro"
app_title = "Agrowth Agro"
app_publisher = "Agrowth"
app_description = "Módulo de agricultura para ERPNext - Campos, lotes, campañas y operaciones agrícolas"
app_icon = "fa fa-leanpub"
app_color = "green"
app_email = "info@agrowth.app"
app_license = "MIT"

fixtures = []

docevents = {
    "*": {
        "on_update": "agrowth_agro.utils.tracking.track_modification",
    }
}

doc_events = {
    "Agro Field": {
        "after_insert": "agrowth_agro.utils.warehouse_sync.on_field_after_insert",
        "after_rename": "agrowth_agro.utils.warehouse_sync.on_field_after_rename",
        "on_trash": "agrowth_agro.utils.warehouse_sync.on_field_on_trash",
    },
    "Agro Location": {
        "after_insert": "agrowth_agro.utils.warehouse_sync.on_location_after_insert",
    },
}

# Includes in <head>
# ------------------

# app_include_css = "/assets/agrowth_agro/css/agrowth_agro.css"
# app_include_js = "/assets/agrowth_agro/js/agrowth_agro.js"

# website_route_rules = [
#     {"from_route": "/orders/<path:app_path>", "to_route": "orders"},
# ]

# Permissions
# -----------
# Permissions on DocTypes will be automatically applied based on configured permissions

# Document Events
# ---------------
# Hook on document methods and doctype events for processing
#
# doc_events = {
#     "*": {
#         "on_update": "agrowth_agro.utils.tracking.track_modification",
#         "on_cancel": "agrowth_agro.utils.tracking.track_cancellation",
#         "on_submit": "agrowth_agro.utils.tracking.track_submission",
#     }
# }

# Scheduled Tasks
# ---------------
# scheduler_events = {
#     "all": [
#         "agrowth_agro.utils.tasks.all",
#     ],
#     "daily": [
#         "agrowth_agro.utils.tasks.daily",
#     ],
#     "hourly": [
#         "agrowth_agro.utils.tasks.hourly",
#     ],
#     "weekly": [
#         "agrowth_agro.utils.tasks.weekly",
#     ],
#     "monthly": [
#         "agrowth_agro.utils.tasks.monthly",
#     ],
# }

# Testing
# -------

# override_whitelisted_methods = {
#     "erpnext.stock.doctype.material_request.material_request.make_purchase_order": "agrowth_agro.utils.material_request.make_purchase_order"
# }

# Overriding DocTypes
# -------------------
# Override DocType methods using the patch method

# override_doctype_dashboards = {
#     "Task": "agrowth_agro.task.get_dashboard_data"
# }

# User Data Protection
# ----------------------

# (Do not change this variable name)
# user_data_fields = [
#     {
#         "doctype": "{doctype_1}",
#         "filters": [
#             {"field": "owner", "value": "user_id"}
#         ]
#     },
#     {
#         "doctype": "{doctype_2}",
#         "filters": [
#             {"field": "owner", "value": "user_id"}
#         ]
#     },
#     {
#         "doctype": "{doctype_3}",
#         "filters": [
#             {"field": "owner", "value": "user_id"}
#         ]
#     },
#     {
#         "doctype": "{doctype_4}",
#         "filters": [
#             {"field": "owner", "value": "user_id"}
#         ]
#     },
# ]

# Migration
# ----------
# migration_patches = {
#     "0.0.1": ["agrowth_agro.migrations.set_first_value"]
# }

after_install = "agrowth_agro.workspace_setup.ensure_workspaces"

after_migrate = ["agrowth_agro.workspace_setup.ensure_workspaces"]

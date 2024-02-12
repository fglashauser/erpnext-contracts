from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def after_install():
    create_custom_field(
        "Sales Invoice",
        dict(
            fieldname="extended_contract",
            label="Extended Contract",
            fieldtype="Link",
            insert_after="to_date",
            options="Extended Contract",
        ),
    )
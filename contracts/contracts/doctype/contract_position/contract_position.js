// Copyright (c) 2024, PC-Giga and contributors
// For license information, please see license.txt

frappe.ui.form.on('Contract Position', {
    form_render(frm, cdt, cdn) {
        update_next_billing_date(frm, cdt, cdn);
    },
    item(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.item) {
            // update the item details on item change
            frappe.call({
                method: 'contracts.contracts.doctype.contract_position.contract_position.get_item_details',
                args: {
                    item_code: row.item
                },
                callback: function(response) {
                    let item = response.message;
                    frappe.model.set_value(cdt, cdn, 'item_name', item.item_name);
                    frappe.model.set_value(cdt, cdn, 'uom', item.uom);
                    frappe.model.set_value(cdt, cdn, 'rate', item.rate);
                    frappe.model.set_value(cdt, cdn, 'description', item.description);
                } 
            });
        }
    },
    billing_cycle(frm, cdt, cdn) {
        update_next_billing_date(frm, cdt, cdn);
    },
    valid_from(frm, cdt, cdn) {
        update_next_billing_date(frm, cdt, cdn);
    },
    valid_until(frm, cdt, cdn) {
        update_next_billing_date(frm, cdt, cdn);
    },
    last_billing_date(frm, cdt, cdn) {
        update_next_billing_date(frm, cdt, cdn);
    }
});

function update_next_billing_date(frm, cdt, cdn) {
    // let row = frappe.get_doc(cdt, cdn);
    // frm.call('get_position_next_billing_date', { position_dict: row })
    //     .then(r => {
    //         frappe.model.set_value(cdt, cdn, 'next_billing_date', r.message);
    //     });
}
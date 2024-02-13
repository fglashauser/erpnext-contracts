// Copyright (c) 2023, PC-Giga and contributors
// For license information, please see license.txt

frappe.ui.form.on('Extended Contract', {
    refresh(frm) {
        autofill_defaults(frm);
        add_invoices_button(frm);
    },
    end_date(frm) {
        update_termination_effective_date(frm);
    },
    np_amount(frm) {
        update_termination_effective_date(frm);
    },
    np_unit(frm) {
        update_termination_effective_date(frm);
    },
    np_term(frm) {
        update_termination_effective_date(frm);
    }
});

//
// Adds the "Create invoice(s)" button to the form if contract is active
//
function add_invoices_button(frm) {
    if (frm.doc.status == 'Active') {
        frm.add_custom_button(__('Create invoice(s)'), () => {
            frm.call('create_invoices')
        });
    }
}

//
// Autofills the default values from the settings
//
function autofill_defaults(frm) {
    if (!frm.doc.__islocal)
        return;
    
    frm.call('get_default_values')
        .then(r => {
            let defaults = r.message;
            frm.set_value('is_indefinite', defaults.is_indefinite);
            frm.set_value('start_date', defaults.start_date);
            frm.set_value('end_date', defaults.end_date);
            frm.set_value('np_amount', defaults.np_amount);
            frm.set_value('np_unit', defaults.np_unit);
            frm.set_value('np_term', defaults.np_term);
            frm.set_value('automatic_renewal_amount', defaults.automatic_renewal_amount);
            frm.set_value('automatic_renewal_unit', defaults.automatic_renewal_unit);
            frm.set_value('billing_type', defaults.billing_type);
            frm.set_value('income_account', defaults.income_account);
            frm.set_value('taxes_and_charges', defaults.taxes_and_charges);
        });
}

// frappe.ui.form.on('Contract Position', {
//     form_render(frm, cdt, cdn) {
//         update_next_billing_date(frm, cdt, cdn);
//     },
//     item(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];

//         if (row.item) {
//             // update the item details on item change
//             frappe.call({
//                 method: 'contracts.contracts.doctype.contract_position.contract_position.get_item_details',
//                 args: {
//                     item_code: row.item
//                 },
//                 callback: function(response) {
//                     let item = response.message;
//                     frappe.model.set_value(cdt, cdn, 'item_name', item.item_name);
//                     frappe.model.set_value(cdt, cdn, 'uom', item.uom);
//                     frappe.model.set_value(cdt, cdn, 'rate', item.rate);
//                     frappe.model.set_value(cdt, cdn, 'description', item.description);
//                 } 
//             });
//         }
//     },
//     billing_cycle(frm, cdt, cdn) {
//         update_next_billing_date(frm, cdt, cdn);
//     },
//     valid_from(frm, cdt, cdn) {
//         update_next_billing_date(frm, cdt, cdn);
//     },
//     valid_until(frm, cdt, cdn) {
//         update_next_billing_date(frm, cdt, cdn);
//     },
//     last_billing_date(frm, cdt, cdn) {
//         update_next_billing_date(frm, cdt, cdn);
//     }
// });

function update_termination_effective_date(frm) {
    frm.call('update_termination_date')
        .then(r => {
            frm.set_value('termination_effective_date', r.message);
        });
}

function update_next_billing_date(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    frm.call('get_position_next_billing_date', { position_dict: row })
        .then(r => {
            frappe.model.set_value(cdt, cdn, 'next_billing_date', r.message);
        });
}
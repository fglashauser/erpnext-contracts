// Copyright (c) 2023, PC-Giga and contributors
// For license information, please see license.txt

frappe.ui.form.on('Extended Contract', {
    end_date(frm) {
        update_termination_effective_date(frm);
    },
    notice_period_amount(frm) {
        update_termination_effective_date(frm);
    },
    notice_period_unit(frm) {
        update_termination_effective_date(frm);
    },
    notice_period_term(frm) {
        update_termination_effective_date(frm);
    }
});

frappe.ui.form.on('Contract Position', {
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

function update_termination_effective_date(frm) {
    frappe.call({
        method: 'contracts.contracts.doctype.extended_contract.extended_contract.calculate_termination_date',
        args: {
            is_indefinite:  frm.doc.is_indefinite,
            end_date:       frm.doc.end_date,
            np_amount:      frm.doc.notice_period_amount,
            np_unit:        frm.doc.notice_period_unit,
            np_term:        frm.doc.notice_period_term
        },
        callback: function(response) {
            frm.set_value('termination_effective_date', response.message);
            frm.refresh();
        }
    });
}

function update_next_billing_date(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    frappe.call({
        method: 'contracts.contracts.doctype.contract_position.contract_position.calculate_next_billing_date',
        args: {
            contract_start_date:    frm.doc.start_date,
            billing_cycle:          row.billing_cycle,
            valid_from:             row.valid_from,
            valid_until:            row.valid_until,
            last_billing_date:      row.last_billing_date
        },
        callback: function(response) {
            frappe.model.set_value(cdt, cdn, 'next_billing_date', response.message);
        }
    });
}
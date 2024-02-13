// Copyright (c) 2024, PC-Giga and contributors
// For license information, please see license.txt

frappe.ui.form.on('Extended Contract', {
    refresh(frm) {
        // Autofills the default values from the settings.
        autofill_defaults(frm);

        // Adds the "Create invoice(s)" button to the form if contract is active.
        add_invoices_button(frm);
    },
    end_date(frm) {
        // Updates the termination effective date based on the end date and the notice period.
        update_termination_effective_date(frm);
    },
    np_amount(frm) {
        // Updates the termination effective date based on the end date and the notice period.
        update_termination_effective_date(frm);
    },
    np_unit(frm) {
        // Updates the termination effective date based on the end date and the notice period.
        update_termination_effective_date(frm);
    },
    np_term(frm) {
        // Updates the termination effective date based on the end date and the notice period.
        update_termination_effective_date(frm);
    }
});

/**
 * Adds the "Create invoice(s)" button to the form if contract is active.
 */
function add_invoices_button(frm) {
    if (frm.doc.status == 'Active') {
        frm.add_custom_button(__('Create invoice(s)'), () => {
            frm.call('create_invoices')
        });
    }
}

/**
 * Autofills the default values from the settings.
 */
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

/**
 * Updates the termination effective date based on the end date and the notice period.
 */
function update_termination_effective_date(frm) {
    frm.call('update_termination_date')
        .then(r => {
            frm.set_value('termination_effective_date', r.message);
        });
}


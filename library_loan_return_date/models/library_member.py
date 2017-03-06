from openerp import fields, models, api


class LibraryMember(models.Model):
    _inherit = 'library.member'
    loan_duration = fields.Integer('Loan duration', default=15, required=True)

    @api.multi
    def return_all_books(self):
        self.ensure_one
        wizard = self.env['library.returns.wizard']  # Get an empty recordset
        values = {'member_id': self.id}  # For a new wizard record
        #values = {'member_id': self.id, book_ids=False}  # For a new wizard record
        specs = wizard._onchange_spec()  # Onchange specifications for the wizard (which onchange methods will be called)
        updates = wizard.onchange(values, ['member_id'], specs)  # Get the result of the onchange method
        value = updates.get('value', {})
        for name, val in value.iteritems():
            if isinstance(val, tuple):
                value[name] = val[0]
        values.update(value)
        record = wizard.create(values)  # Create a wizard
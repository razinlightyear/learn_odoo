# -*- coding: utf-8 -*-
from openerp import fields, models, api


class LibraryReturnsWizard(models.TransientModel):
    _name = 'library.returns.wizard'
    member_id = fields.Many2one('library.member', string='Member')
    book_ids = fields.Many2many('library.book', string='Books')

    @api.multi
    def record_returns(self):
        loan = self.env['library.book.loan']
        for rec in self:
            loans = loan.search(
                [('state', '=', 'ongoing'),
                 ('book_id', 'in', rec.book_ids.ids),
                 ('member_id', '=', rec.member_id.id)]
            )
            print "**********************************************************************************************"
            print loans
            for loan in loans:
                print loan
                print type(loan)
                print loan.state

            loans.write({'state': 'done'})

    #  automatically populate the list of books to return
    @api.onchange('member_id')
    def onchange_member(self):
        loan = self.env['library.book.loan']
        loans = loan.search(
            [('state', '=', 'ongoing'),
             ('member_id', '=', self.member_id.id)]
        )
        self.book_ids = loans.mapped('book_id')

        #  Add warning message if the user has overdue books
        result = {
            'domain': {'book_ids': [
                ('id', 'in', self.book_ids.ids)]
            }
        }
        late_domain = [
            ('id', 'in', loans.ids),
            ('expected_return_date', '<', fields.Date.today())
        ]
        late_loans = loans.search(late_domain)
        if late_loans:
            message = ('Warn the member that the following '
                       'books are late:\n')
            titles = late_loans.mapped('book_id.name')
            result['warning'] = {
                'title': 'Late books',
                'message': message + '\n'.join(titles)
            }
        return result

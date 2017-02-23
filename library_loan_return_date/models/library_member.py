from openerp import fields, models, api

class LibraryMember(models.Model):
	_inherit = 'library.member'
	loan_duration = fields.Integer('Loan duration', default=15, required=True)

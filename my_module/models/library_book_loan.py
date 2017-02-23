# -*- coding: utf-8 -*-
from openerp import fields, models, api

class LibraryBookLoan(models.Model):
	_name = 'library.book.loan'
	book_id = fields.Many2one('library.book', 'Book', required=True)
	member_id = fields.Many2one('library.member', 'Borrower', required=True)
	state = fields.Selection([('ongoing', 'Ongoing'),
							  ('done', 'Done')],
							  'State',
							  default='ongoing',
							  required=True)

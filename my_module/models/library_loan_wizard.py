# -*- coding: utf-8 -*-
from openerp import fields, models, api

class LibraryLoanWizard(models.TransientModel):
	_name = 'library.loan.wizard'
	member_id = fields.Many2one('library.member', 'Member') # record the member borrowing the books
	book_ids = fields.Many2many('library.book', 'Books') # record the books being borrowed
	# might want to add another field for return_date

	# create a the loans records from the submitted form values. (Still not sure why this neccesary)
	@api.multi
	def record_loans(self):
		for wizard in self:
			member = wizard.member_id # not in revised version, don't need it?
			books = wizard.book_ids
			loan = self.env['library.book.loan']
			for book in wizard.book_ids:
				values = self._prepare_loan(book)
				loan.create(values)
				#loan.create({'member_id': member.id, 'book_id': book.id})

	@api.multi
	def _prepare_loan(self, book):
		return {'member_id': self.member_id.id, 'book_id': book.id}

# -*- coding: utf-8 -*-
{
	'name': "Library Books",
	'summary': "Manage your books",
	'depends': ['base', 'decimal_precision'],
	'data': [  
			# ordering matters. Security files should be on the top
			# security groups
			# model security access
			# ..Other data files
			'security/library_security.xml',
			'security/ir.model.access.csv',
			'views/library_book.xml',
			'views/library_loan_wizard.xml',
	],
	'category': 'Library', # Added with security
	'description': "Library system for SilencerCo internal use.",
}

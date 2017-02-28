# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.fields import Date as fDate
from openerp.addons import decimal_precision as dp
from datetime import timedelta as td


class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']
    _description = 'Library Book'
    _order = 'date_release desc, name'
    _rec_name = 'short_name'
    name = fields.Char('Title', required=True)
    short_name = fields.Char(
        string='Short Title',
        size=100,  # For Char only
        tranlate=False,  # also for text fields
    )
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'UnAvailable'),
         ('available', 'Available'),
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')],
        'State')
    description = fields.Html(
        string='Description',
        # optional:
        sanitize=True,
        strip_style=False,
        tranlate=False,
    )
    cover = fields.Binary('Book Cover')
    out_of_print = fields.Boolean('Out of Print?')
    date_release = fields.Date('Release Date')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer(  # Lots of options!
        string='Number of Pages',
        default=0,
        help='Total book page count',
        groups='base.group_user',
        states={'cancel': [('readonly', True)]},
        copy=True,
        index=False,
        readonly=False,
        required=False,
        company_dependent=False,
    )
    reader_rating = fields.Float(
        'Reader Average Rating',
        (1, 14),  # Optiona; precision (total, decimals)
    )
    # active = fields.Boolean('Active',default=True) # Ability to remove something from the library (I added). Inherited by abstract model
    cost_price = fields.Float('Book Cost', dp.get_precision('Book Price'))
    currency_id = fields.Many2one('res.currency', string='Currency')  # Stores the currency to be used.
    retail_price = fields.Monetary('Retail Price',
                                   currency_field='currency_id')  # optional: currency_field='currency_id'
    author_ids = fields.Many2many('res.partner', string='Authors')
    publisher_id = fields.Many2one(
        'res.partner',
        string='Publisher',
        # optional: ondelete='set null', context={}, domain=[]
    )
    publisher_city = fields.Char('Publisher City', related='publisher_id.city')
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        store=False,
        compute_sudo=False,
    )
    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')
    manager_remarks = fields.Text('Manager Remarks')  # added from pg. 118
    isbn = fields.Char('ISBN')

    # Validations
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Book title must be unique.')
    ]

    # Used with searching books. Updated at the end of chapter 5.
    def name_get(self):
        result = []
        for book in self:
            authors = book.author_ids.mapped('name')
            # name = u'%s (%s)' % (book.title, u', '.join(authors)) # Wrong in book?
            name = u'%s (%s)' % (book.name, u', '.join(authors))
            result.append((book.id, name))
        # result.append(
        #	(record.id, u"%s (%s)" % (record.name, record.date_released))
        #	)
        return result

    # Validation
    @api.constrains('date_release')
    def _check_release_date(self):
        for r in self:
            if r.date_release > fields.Date.today():
                raise models.ValidationError(
                    'Release date must be in the past')

    # used for age_days (computed attribute)
    @api.depends('date_release')
    def _compute_age(self):
        today = fDate.from_string(fDate.today())
        for book in self.filtered('date_release'):
            delta = (fDate.from_string(book.date_release - today))
            book.age_days = delta.days

    # used for age_days (computed attribute)
    def _inverse_age(self):
        today = fDate.from_string(fDate.today())
        for book in self.filtered('date_release'):
            d = td(days=book.age_days) - today
            book.date_release = fDate.to_string(d)

    # used for age_days (computed attribute)
    def _search_age(self, operator, value):
        today = fDate.from_string(fDate.today())
        value_days = td(days=value)
        value_date = fDate.to_string(today - value_days)
        return [('date_release', operator, value_date)]

    @api.model
    def _referencable_models(self):
        models = self.env['res.request.link'].search([])
        return [(x.object, x.name) for x in models]

    # check weather a state transition is allowed
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')
                   ]
        return (old_state, new_state) in allowed

    # change the state of some books
    @api.multi
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                continue

    # How to access another model
    @api.model
    def get_all_library_members(self):
        library_member_model = self.env['library.member']
        return library_member_model.search([])

    # Prevent users without permission from creating,updating manager_remarks
    @api.model
    @api.returns('self', lambda rec: rec.id)
    def create(self, values):
        if not self.user_has_groups('library.group_library_manager'):
            if 'manager_remarks' in values:
                raise exceptions.UserError(
                    'You are not allowed to modify '
                    'manager_remarks'
                )
        return super(LibraryBook, self).create(values)

    @api.multi
    def write(self, values):
        if not self.user_has_groups('library.group_library_manager'):
            if 'manager_remarks' in values:
                raise exceptions.UserError(
                    'You are not allowed to modify '
                    'manager_remarks'

                )
        return super(LibraryBook, self).write(values)

    @api.model
    def fields_get(self, allfields=None, write_access=True, attributes=None):
        fields = super(LibraryBook, self).fields_get(
            allfields=allfields,
            write_access=write_access,
            attributes=attributes
        )
        if not self.user_has_groups(
                'library.group_library_manager'):
            if 'manager_remarks' in fields:
                fields['manager_remarks']['readonly'] = True
        return fields  # Missing in the book

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not (name == '' and operator == 'ilike'):
            args += ['|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)
                     ]
        return super(LibraryBook, self)._name_search(name='', args=args, operator='ilike',
                                                     limit=limit, name_get_uid=name_get_uid)

    class BaseArchive(models.AbstractModel):
        _name = 'base.archive'
        active = fields.Boolean(default=True)

        def do_archive(self):
            for record in self:
                record.active = not record.active


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _order = 'name'
    book_ids = fields.One2many('library.book', 'publisher_id', string='Published Books')
    # book_ids = fields.Many2many('library.book',string='Authored Books')
    authored_book_ids = fields.Many2many('library.book', string='Authored Books')
    count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)


class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    partner_id = fields.Many2one('res.partner', ondelete='cascade',
                                 required=True)  # It gives me a warning if I don't make this required

    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()

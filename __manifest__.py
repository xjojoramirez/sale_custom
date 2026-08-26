{
    'name': 'Sale Custom',
    'version': '18.0.4.0.0',
    'category': 'Custom',
    'summary': 'Custom sales features: catalog stock filter, customer dropdown restriction, salesperson on invoices, urgent note popup on confirmation, confirmation email to sales rep',
    'description': """
Sale Custom
===========

Custom features for the Sales app:

* Product catalog on sales orders only shows products with available
  inventory (services and non-tracked goods always remain visible).
* The customer field on quotations is filtered per security group:
  "Customers: Own Only" members pick only their own customers,
  "Customers: Extended Access" members also see restricted salesmen's
  customers.
* The invoice PDF shows the salesperson's name and phone number so the
  trucker knows who to call in case of an issue at delivery.
* Confirming a quotation that has chatter log notes pops up a dialog with
  the latest log note (e.g. "call for delivery appointment") before the
  confirmation proceeds. Invoices and automated flows are unaffected.
* On confirmation the order's salesperson receives an email with a link
  back to the sales order.
""",
    'depends': ['sale_stock'],
    'data': [
        'data/mail_template_sale_order_confirmed.xml',
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'wizard/urgent_note_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

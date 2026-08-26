from odoo import Command
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestConfirmationEmail(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.salesperson = cls.env['res.users'].create({
            'name': 'Rep One',
            'login': 'rep_one_test',
            'email': 'rep1@example.com',
            'groups_id': [
                Command.set(cls.env.ref('sales_team.group_sale_salesman').ids)
            ],
        })
        cls.customer = cls.env['res.partner'].create({'name': 'Cust Test'})
        cls.product = cls.env['product.product'].create({
            'name': 'Test Product',
            'type': 'service',
            'list_price': 100.0,
        })

    def _make_order(self, salesperson):
        order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'user_id': salesperson.id,
        })
        self.env['sale.order.line'].create({
            'order_id': order.id,
            'product_id': self.product.id,
            'product_uom_qty': 2,
        })
        return order

    def _order_mails(self, order):
        return self.env['mail.mail'].search([
            ('mail_message_id.model', '=', 'sale.order'),
            ('mail_message_id.res_id', '=', order.id),
        ])

    def test_backend_url_helper(self):
        order = self._make_order(self.salesperson)
        url = order.sale_custom_get_backend_url()
        self.assertIn('id=%s' % order.id, url)
        self.assertIn('model=sale.order', url)
        self.assertTrue(url.startswith('http'))

    def test_email_sent_to_salesperson_on_confirm(self):
        order = self._make_order(self.salesperson)
        order.action_confirm()
        mails = self._order_mails(order)
        self.assertEqual(len(mails), 1)
        self.assertEqual(
            mails[0].recipient_ids,
            self.salesperson.partner_id,
        )
        self.assertIn(order.name, mails[0].subject)

    def test_no_email_without_salesperson(self):
        order = self._make_order(self.salesperson)
        order.user_id = False
        order.action_confirm()
        self.assertFalse(self._order_mails(order))

    def test_reconfirm_does_not_duplicate_email(self):
        order = self._make_order(self.salesperson)
        order.action_confirm()
        with self.assertRaises(UserError):
            order.action_confirm()
        self.assertEqual(len(self._order_mails(order)), 1)

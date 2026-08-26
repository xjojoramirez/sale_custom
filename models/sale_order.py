import logging

from werkzeug import urls

from odoo import Command, _, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_action_add_from_catalog_extra_context(self):
        return {
            **super()._get_action_add_from_catalog_extra_context(),
            'search_default_available_stock': 1,
        }

    def _get_latest_log_note(self):
        self.ensure_one()
        return self.env['mail.message'].search([
            ('model', '=', self._name),
            ('res_id', '=', self.id),
            ('message_type', '=', 'comment'),
            ('subtype_id', '=', self.env.ref('mail.mt_note').id),
        ], limit=1, order='id desc')

    def sale_custom_get_backend_url(self):
        """Public helper for mail templates (sandbox forbids underscore
        attributes). Returns an absolute URL to this order's form.
        Built directly instead of via _notify_get_action_link because the
        enterprise mail_mobile module wraps 'view' links in Firebase
        Dynamic Links (redirect-url.email), which breaks plain browser use."""
        self.ensure_one()
        return urls.url_join(
            self.get_base_url(),
            '/web#id=%s&model=%s&view_type=form' % (self.id, self._name),
        )

    def _sale_custom_notify_salesperson(self):
        template = self.env.ref(
            'sale_custom.mail_template_sale_order_confirmed_salesperson',
            raise_if_not_found=False,
        )
        if not template:
            return
        for order in self:
            if not order.user_id:
                continue
            try:
                template.send_mail(order.id, force_send=True, raise_exception=False)
            except Exception:
                _logger.exception(
                    "sale_custom: failed sending confirmation email for %s",
                    order.name,
                )

    def action_confirm(self):
        pre_confirmed = self.filtered(
            lambda o: o.state in ('draft', 'sent'))
        res = super().action_confirm()
        confirmed = pre_confirmed.filtered(lambda o: o.state == 'sale')
        confirmed._sale_custom_notify_salesperson()
        return res

    def action_confirm_with_check(self):
        if not self.filtered(lambda o: o._get_latest_log_note()):
            return super().action_confirm()
        wizard = self.env['sale_custom.confirm.log.note.wizard'].create({
            'order_ids': [Command.set(self.ids)],
        })
        return {
            'name': _("Urgent Note"),
            'type': 'ir.actions.act_window',
            'res_model': wizard._name,
            'res_id': wizard.id,
            'view_mode': 'form',
            'view_id': self.env.ref(
                'sale_custom.confirm_log_note_wizard_view_form').id,
            'target': 'new',
            'context': {'dialog_size': 'medium'},
        }

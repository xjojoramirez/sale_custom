from odoo import api, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _sale_custom_restriction_domain(self):
        user = self.env.user
        own_group = self.env.ref(
            'sale_custom.group_customers_own_only', raise_if_not_found=False)
        extended_group = self.env.ref(
            'sale_custom.group_customers_extended_access', raise_if_not_found=False)
        if own_group and user in own_group.users:
            return expression.OR([
                [('user_id', '=', user.id)],
                [('commercial_partner_id.user_id', '=', user.id)],
            ])
        if extended_group and user in extended_group.users:
            visible_users = list({*own_group.users.ids, user.id}) if own_group else [user.id]
            return expression.OR([
                [('user_id', 'in', visible_users)],
                [('commercial_partner_id.user_id', 'in', visible_users)],
            ])
        return False

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if self.env.context.get('sale_custom_restrict_partners'):
            domain = self._sale_custom_restriction_domain()
            if domain:
                args = expression.AND([list(args or []), domain])
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.model
    def name_create(self, name):
        if self.env.context.get('sale_custom_restrict_partners'):
            if self._sale_custom_restriction_domain():
                self = self.with_context(default_user_id=self.env.uid)
        return super().name_create(name)

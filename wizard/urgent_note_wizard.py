from odoo import api, fields, models


class ConfirmLogNoteWizard(models.TransientModel):
    _name = 'sale_custom.confirm.log.note.wizard'
    _description = 'Show Latest Log Note Before Confirming'

    order_ids = fields.Many2many('sale.order')
    note_body = fields.Html(compute='_compute_note_body')

    @api.depends('order_ids')
    def _compute_note_body(self):
        for wizard in self:
            sections = []
            for order in wizard.order_ids:
                message = order._get_latest_log_note()
                if not message:
                    continue
                if len(wizard.order_ids) > 1:
                    sections.append(
                        '<div class="fw-bold mb-1">%s</div>%s'
                        % (order.name, message.body)
                    )
                else:
                    sections.append(message.body)
            wizard.note_body = ''.join(sections)

    def action_ok(self):
        self.order_ids.action_confirm()
        return {'type': 'ir.actions.act_window_close'}

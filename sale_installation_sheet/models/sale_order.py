import re

from odoo import models

# The product options printed on the sheet, in the order of the client's PDF.
# An option is ticked when the product category of an order line contains the
# option name (spaces, case and a trailing "s" are ignored), e.g. the category
# "All / Clear Burglar Bars" ticks "Clear Burglar Bars".
INSTALLATION_PRODUCT_OPTIONS = [
    'Clear Burglar Bars',
    'TrellisGuard',
    'Security Mesh Guard',
    'Transparent Security Gate',
    'Steel Gate',
    'RollerGuard',
    'MozziGuard',
    'SpikeGuard',
    'Blinds',
    'Secure Shutters',
]

PARAM_SOP_CODE = 'sale_installation_sheet.sop_code'
PARAM_SOP_VERSION = 'sale_installation_sheet.sop_version'


def _normalize(text):
    return re.sub(r'[^a-z0-9]', '', (text or '').lower())


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_installation_sheet_meta(self):
        """Document code and version printed in the sheet header.

        Both can be changed in Settings > Technical > System Parameters.
        """
        params = self.env['ir.config_parameter'].sudo()
        return {
            'sop_code': params.get_param(PARAM_SOP_CODE, 'SOP-OPS-001'),
            'sop_version': params.get_param(PARAM_SOP_VERSION, '1.0'),
        }

    def _get_installation_sheet_job_ref(self):
        """Sales order number, followed by the posted invoice numbers if any."""
        self.ensure_one()
        refs = [self.name]
        invoices = self.invoice_ids.filtered(lambda inv: inv.state == 'posted')
        refs += [inv.name for inv in invoices if inv.name]
        return ' / '.join(refs)

    def _get_installation_sheet_salesperson(self):
        self.ensure_one()
        parts = [self.user_id.name, self.team_id.name]
        return ' / '.join(part for part in parts if part)

    def _get_installation_sheet_products(self):
        """Work out which product boxes to tick from the order line categories.

        Returns a dict with:
          rows: the 11 options in rows of three cells (label, ticked, text)
        """
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda line: not line.display_type and line.product_id)
        option_keys = {
            option: _normalize(option).rstrip('s')
            for option in INSTALLATION_PRODUCT_OPTIONS
        }
        ticked = set()
        other_categories = []
        for line in lines:
            categ = line.product_id.categ_id
            categ_key = _normalize(categ.complete_name)
            matched = False
            for option, key in option_keys.items():
                if key and key in categ_key:
                    ticked.add(option)
                    matched = True
            # Services (e.g. labour, delivery) must not tick "Other".
            if not matched and line.product_id.type != 'service':
                name = categ.name or line.product_id.display_name
                if name and name not in other_categories:
                    other_categories.append(name)

        cells = [
            {'label': option, 'ticked': option in ticked, 'text': ''}
            for option in INSTALLATION_PRODUCT_OPTIONS
        ]
        cells.append({
            'label': 'Other (specify)',
            'ticked': bool(other_categories),
            'text': ', '.join(other_categories),
        })
        # Pad so the last row always has three cells.
        while len(cells) % 3:
            cells.append({'label': '', 'ticked': False, 'text': ''})
        return {'rows': [cells[i:i + 3] for i in range(0, len(cells), 3)]}

{
    'name': 'Sale Installation Sheet',
    'version': '20.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Print the Installation Completion & Sign-off Sheet (SOP-OPS-001) from a Sales Order',
    'description': """
Adds a "Print Installation Sheet" button to the Sales Order. The PDF follows the
client sign-off sheet (SOP-OPS-001): job details are filled from the order, the
installed products are ticked from the product categories of the order lines, and
everything else is left blank for the installation team to complete by hand.
""",
    'author': 'Kevin',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'data/ir_config_parameter_data.xml',
        'report/installation_sheet_report.xml',
        'report/installation_sheet_templates.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
}

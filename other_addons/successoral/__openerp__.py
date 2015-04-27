# -*- coding: utf-8 -*-
{
    'name': "successoral",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website'],

    # always loaded
    'data': [
        'templates/assets.xml',
        # 'security/ir.model.access.csv',
        'templates/biens.xml',
        'templates/common.xml',
        'templates/defunt.xml',
        'templates/dispositions.xml',
        'templates/donation.xml',
        'templates/error.xml',
        'templates/famille.xml',
        'templates/heritiers.xml',
        'templates/home.xml',
        'templates/region.xml',
        'templates/results.xml',
        'templates/vie.xml',
    ],
}

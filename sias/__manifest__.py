# -*- coding: utf-8 -*-
{
    'name': "SIAS",

    'summary': """
        SIAS - Sistema de Informacion de Agua y Saneamiento.""",

    'description': """
        Se trata de una herramienta de información básica, actualizada y contrastada sobre los servicios de 
        abastecimiento de agua y saneamiento de comunidades rurales..
    """,

    'author': "Leantic",
    'website': "http://www.leantic.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_address_city', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
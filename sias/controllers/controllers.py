# -*- coding: utf-8 -*-
from odoo import http

# class Sias(http.Controller):
#     @http.route('/sias/sias/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sias/sias/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sias.listing', {
#             'root': '/sias/sias',
#             'objects': http.request.env['sias.sias'].search([]),
#         })

#     @http.route('/sias/sias/objects/<model("sias.sias"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sias.object', {
#             'object': obj
#         })
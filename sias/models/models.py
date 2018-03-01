# -*- coding: utf-8 -*-

import base64
import threading

from odoo import models, fields, api, tools
from odoo.modules import get_module_resource


class Community(models.Model):
    _name = 'sias.community'

    name = fields.Char('Name', required=True)
    description = fields.Text()
    city_id = fields.Many2one('res.city', string='City', required=True)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px", )
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized image of this contact. It is automatically " \
                                      "resized as a 128x128px image, with aspect ratio preserved. " \
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized image of this contact. It is automatically " \
                                     "resized as a 64x64px image, with aspect ratio preserved. " \
                                     "Use this field anywhere a small image is required.")
    active = fields.Boolean("Active", default=True)

    @api.model
    def _get_default_image(self):
        colorize, img_path, image = False, False, False

        if not image:
            img_path = get_module_resource('base', 'static/src/img', 'community.png')
            colorize = True

        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
        if image and colorize:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(base64.b64encode(image))

    @api.model
    def create(self, vals):
        # compute default image in create, because computing gravatar in the onchange
        # cannot be easily performed if default images are in the way
        if not vals.get('image'):
            vals['image'] = self._get_default_image()
        tools.image_resize_images(vals)
        community = super(Community, self).create(vals)
        return community

    def open_dashboard(self):
        action = self.env.ref('sias.action_gender_pie_chart').read()[0]
        action.update({'params': {
                        'community_id': self.id
                    }})
        return action


class Home(models.Model):
    _name = 'sias.home'
    _inherits = {'res.partner': 'partner_id'}

    home_code = fields.Char(string='Code', compute='_get_home_code')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
                                 string='Related Partner', help='Partner-related data of the home')
    community_id = fields.Many2one('sias.community', required=True, ondelete='restrict', string="Community")
    observation = fields.Text("Observation")
    active = fields.Boolean("Active", default=True)

    def _get_home_code(self):
        for rec in self:
            rec.home_code = str(rec.id).zfill(7)

    @api.model
    def _get_default_image(self, partner_type, is_company, parent_id):
        if getattr(threading.currentThread(), 'testing', False) or self._context.get('install_mode'):
            return False

        colorize, img_path, image = False, False, False

        if partner_type in ['other'] and parent_id:
            parent_image = self.browse(parent_id).image
            image = parent_image and parent_image.decode('base64') or None

        if not image and partner_type == 'invoice':
            img_path = get_module_resource('base', 'static/src/img', 'money.png')
        elif not image and partner_type == 'delivery':
            img_path = get_module_resource('base', 'static/src/img', 'truck.png')
        elif not image and is_company:
            img_path = get_module_resource('base', 'static/src/img', 'company_image.png')
        elif not image:
            img_path = get_module_resource('base', 'static/src/img', 'home.png')
            colorize = True

        if img_path:
            with open(img_path, 'rb') as f:
                image = f.read()
        if image and colorize:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(base64.b64encode(image))

    @api.model
    def create(self, vals):
        if vals.get('website'):
            vals['website'] = self._clean_website(vals['website'])
        if vals.get('parent_id'):
            vals['company_name'] = False
        # compute default image in create, because computing gravatar in the onchange
        # cannot be easily performed if default images are in the way
        if not vals.get('image'):
            vals['image'] = self._get_default_image(vals.get('type'), vals.get('is_company'), vals.get('parent_id'))
        tools.image_resize_images(vals)
        partner = super(Home, self).create(vals)
        return partner


class Survey(models.Model):
    _name = 'sias.survey'

    name = fields.Char('Periodo')
    description = fields.Text()
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('name_unique', 'unique(name)', 'Ya existe una encuesta con el mismo nombre!')
    ]


class SurveyInput(models.Model):
    _name = 'sias.survey.input'

    def _get_last_survey(self):
        last_survey = self.env['sias.survey'].search([])
        if last_survey:
            last_survey = last_survey.sorted(key=lambda r: r.create_date)[-1]

        return last_survey

        # .sorted(key=lambda r: r.create_date)[-1]

    survey_id = fields.Many2one('sias.survey', default=_get_last_survey)
    home_id = fields.Many2one('sias.home')
    population = fields.Integer("Population quantity")
    lt_20 = fields.Integer("Less than 20")
    gtoeq_20 = fields.Integer("Greater or equal to 20", compute='_compute_gtoeq_20', store=True)
    womens = fields.Integer("Womens quantity")
    mens = fields.Integer("Mens quantity", compute='_compute_mens', store=True)
    education_primario = fields.Integer("Primario")
    education_secundario = fields.Integer("Secundario")
    education_sin_instruccion = fields.Integer("Sin instrucción")
    occupation_agricultor = fields.Integer("Agricultor quantity")
    occupation_jornalero = fields.Integer("Jornalero quantity")
    sump = fields.Boolean('Sump')
    water_supply = fields.Selection([
        ('aljibe_propio', 'Aljibe propio'),
        ('aljibe_comunitario', 'Aljibe comunitario')
    ], string="Water Supply", default='aljibe_propio')
    source_distance = fields.Selection([
        ('5', '5 mts'),
        ('60', '60 mts'),
        ('100', '100 mts'),
        ('300', '300 mts'),
        ('350', '350 mts'),
        ('400', '400 mts'),
        ('500', '500 mts'),
    ], string="Source distance", default='5')
    daily_liters = fields.Integer('Daily liters')
    water_treatment = fields.Selection([
        ('ninguno', 'Ninguno'),
        ('filtrado', 'Filtrado')
    ], string="Water treatment", default='ninguno')
    water_qualification  = fields.Selection([
        ('regular', 'Regular'),
        ('buena', 'Buena')
    ], string="Water qualification", default='regular')
    diseases_diarrea = fields.Boolean('Diarrea')
    diseases_respiratoria = fields.Boolean('Respiratorias')
    diseases_dolor_cabeza = fields.Boolean('Dolor de cabeza')
    diseases_fiebre = fields.Boolean('Fiebre')
    observation = fields.Text('Observation')

    community_id = fields.Many2one(related='home_id.community_id', string="Community")

    @api.depends('population', 'lt_20')
    def _compute_gtoeq_20(self):
        self.gtoeq_20 = self.population - self.lt_20

    @api.depends('population', 'womens')
    def _compute_mens(self):
        self.mens = self.population - self.womens

    @api.multi
    def get_gender_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        womens_quant = 0
        mens_quant = 0

        for input in survey_inputs:
            womens_quant += input.womens or 0
            mens_quant += input.mens or 0

        if last_survey:
            crm_lst = [{
                'name': 'Mujeres',
                'y': womens_quant,
                'sliced': True,
                'selected': True
            }, {
                'name': 'Varones',
                'y': mens_quant
            }]
        else:
            crm_lst = [{
                'name': 'Sin datos',
                'y': 100,
                'sliced': True,
                'selected': True
            }]

        return crm_lst

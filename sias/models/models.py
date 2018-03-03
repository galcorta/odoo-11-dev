# -*- coding: utf-8 -*-

import base64
import threading

from odoo import models, fields, api, tools
from odoo.modules import get_module_resource
from odoo.exceptions import ValidationError


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

    # home_code = fields.Char(string='Code', compute='_get_home_code')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
                                 string='Related Partner', help='Partner-related data of the home')
    chief_name = fields.Char("Chief name", required=True)
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

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name')
    def _compute_display_name(self):
        for partner in self:
            partner.display_name = self.chief_name + ' / ' + self.community_id.name


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

    name = fields.Char(compute='_compute_default_name')
    survey_id = fields.Many2one('sias.survey', default=_get_last_survey)
    home_id = fields.Many2one('sias.home')
    population = fields.Integer("Population quantity", required=True)
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
    water_qualification = fields.Selection([
        ('regular', 'Regular'),
        ('buena', 'Buena')
    ], string="Water qualification", default='regular')
    diseases_diarrea = fields.Boolean('Diarrea')
    diseases_respiratoria = fields.Boolean('Respiratorias')
    diseases_dolor_cabeza = fields.Boolean('Dolor de cabeza')
    diseases_fiebre = fields.Boolean('Fiebre')
    observation = fields.Text('Observation')

    community_id = fields.Many2one(related='home_id.community_id', string="Community")

    @api.constrains('population')
    def _check_population(self):
        for record in self:
            if record.population < 1:
                raise ValidationError("Debe indicar la cant. de Habitantes")

    @api.depends('survey_id', 'home_id')
    def _compute_default_name(self):
        self.name = self.survey_id.name + '-' + self.home_id.name

    @api.depends('population', 'lt_20')
    def _compute_gtoeq_20(self):
        self.gtoeq_20 = self.population - self.lt_20

    @api.depends('population', 'womens')
    def _compute_mens(self):
        self.mens = self.population - self.womens

    def _charts_data(self, community_id):
        survey_inputs = None
        last_survey = self._get_last_survey()
        if last_survey:
            if community_id:
                survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
            else:
                survey_inputs = self.search([['survey_id', '=', last_survey.id]])
        return survey_inputs

    def _get_gender_data(self, survey_inputs):
        result = []
        womens_quant = 0
        mens_quant = 0

        for input in survey_inputs:
            if input.population:
                womens_quant += input.womens or 0
                mens_quant += input.mens or 0

        if womens_quant or mens_quant:
            result = [{
                'name': 'Mujeres',
                'y': womens_quant,
                # 'sliced': True,
                # 'selected': True
            }, {
                'name': 'Varones',
                'y': mens_quant
            }]

        return result

    def _get_population_data(self, survey_inputs):
        result = []
        lt_20 = 0
        gtoeq_20 = 0

        for input in survey_inputs:
            lt_20 += input.lt_20 or 0
            gtoeq_20 += input.gtoeq_20 or 0

        if lt_20 or gtoeq_20 :
            result = [{
                'name': 'Menor',
                'y': lt_20
            }, {
                'name': 'Mayor o igual',
                'y': gtoeq_20
            }]

        return result

    @api.multi
    def get_sump_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        with_sump = 0
        without_sump = 0

        for input in survey_inputs:
            if input.sump:
                with_sump += 1
            else:
                without_sump += 1

        if last_survey:
            data_lst = [{
                'name': 'Posee letrina',
                'y': with_sump
            }, {
                'name': 'No posee letrina',
                'y': without_sump
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_source_distance_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        mts5 = 0
        mts60 = 0
        mts100 = 0
        mts300 = 0
        mts350 = 0
        mts400 = 0
        mts500 = 0

        for input in survey_inputs:
            if input.source_distance == '5':
                mts5 += 1
            elif input.source_distance == '60':
                mts60 += 1
            elif input.source_distance == '100':
                mts100 += 1
            elif input.source_distance == '300':
                mts300 += 1
            elif input.source_distance == '350':
                mts350 += 1
            elif input.source_distance == '400':
                mts400 += 1
            else:
                mts500 += 1

        if last_survey:
            data_lst = [{
                'name': '5 mts',
                'y': mts5
            }, {
                'name': '60 mts',
                'y': mts60
            }, {
                'name': '100 mts',
                'y': mts100
            }, {
                'name': '300 mts',
                'y': mts300
            }, {
                'name': '350 mts',
                'y': mts350
            }, {
                'name': '400 mts',
                'y': mts400
            }, {
                'name': '500 mts',
                'y': mts500
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_water_qualification_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        buena = 0
        regular = 0

        for input in survey_inputs:
            if input.water_qualification == 'buena':
                buena += 1
            else:
                regular += 1

        if last_survey:
            data_lst = [{
                'name': 'Buena',
                'y': buena
            }, {
                'name': 'Regular',
                'y': regular
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_water_treatment_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        ninguno = 0
        filtrado = 0

        for input in survey_inputs:
            if input.water_treatment == 'ninguno':
                ninguno += 1
            else:
                filtrado += 1

        if last_survey:
            data_lst = [{
                'name': 'Ninguno',
                'y': ninguno
            }, {
                'name': 'Filtrado',
                'y': filtrado
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_common_diseases_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        diarrea = 0
        respiratoria = 0
        dolor_cabeza = 0
        fiebre = 0

        for input in survey_inputs:
            if input.diseases_diarrea:
                diarrea += 1
            if input.diseases_respiratoria:
                respiratoria += 1
            if input.diseases_dolor_cabeza:
                dolor_cabeza += 1
            if input.diseases_fiebre:
                fiebre += 1

        if last_survey:
            data_lst = [{
                'name': 'Diarrea',
                'y': diarrea
            }, {
                'name': 'Respiratorias',
                'y': respiratoria
            }, {
                'name': 'Dolor de cabeza',
                'y': dolor_cabeza
            }, {
                'name': 'Fiebre',
                'y': fiebre
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_water_supply_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        propio = 0
        comunitario = 0

        for input in survey_inputs:
            if input.water_supply == 'aljibe_propio':
                propio += 1
            else:
                comunitario += 1

        if last_survey:
            data_lst = [{
                'name': 'Aljibe propio',
                'y': propio
            }, {
                'name': 'Aljibe comunitario',
                'y': comunitario
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_occupation_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        agricultor = 0
        jornalero = 0

        for input in survey_inputs:
            agricultor += input.occupation_agricultor or 0
            jornalero += input.occupation_jornalero or 0

        if last_survey:
            data_lst = [{
                'name': 'Agricultor',
                'y': agricultor
            }, {
                'name': 'Jornalero',
                'y': jornalero
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_education_data(self, **kwargs):
        community_id = kwargs['community_id']
        last_survey = self._get_last_survey()
        survey_inputs = self.search([['community_id', '=', community_id], ['survey_id', '=', last_survey.id]])
        primario = 0
        secundario = 0
        sin_instruccion = 0

        for input in survey_inputs:
            primario += input.education_primario or 0
            secundario += input.education_secundario or 0
            sin_instruccion += input.education_sin_instruccion or 0

        if last_survey:
            data_lst = [{
                'name': 'Primario',
                'y': primario
            }, {
                'name': 'Secundario',
                'y': secundario
            }, {
                'name': 'Sin Instrucción',
                'y': sin_instruccion
            }]
        else:
            data_lst = [{
                'name': 'Sin datos',
                'y': 100
            }]

        return data_lst

    @api.multi
    def get_charts_data(self, **kwargs):
        community_id = kwargs['community_id'] if kwargs.get('community_id') else None
        survey_inputs = self._charts_data(community_id)
        if survey_inputs:
            chart = kwargs['chart']
            if chart == 'gender':
                return self._get_gender_data(survey_inputs)
            elif chart == 'population':
                return self._get_population_data(survey_inputs)
            else:
                return []

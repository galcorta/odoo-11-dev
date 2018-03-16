# -*- coding: utf-8 -*-

import base64
import threading

from odoo import models, fields, api, tools
from odoo.modules import get_module_resource
from odoo.exceptions import ValidationError


class MeansSupplyType(models.Model):
    _name = 'sias.means.supply.type'

    name = fields.Char('Name', required=True)
    active = fields.Boolean("Active", default=True)


class Community(models.Model):
    _name = 'sias.community'

    def _get_last_survey(self):
        last_survey = self.env['sias.survey'].search([])
        if last_survey:
            last_survey = last_survey.sorted(key=lambda r: r.create_date)[-1]
        return last_survey

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
    means_supply_ids = fields.One2many('sias.community.means.supply', 'community_id', string="Means supply")
    home_ids = fields.One2many('sias.home', 'community_id', string="Homes")
    active = fields.Boolean("Active", default=True)

    potable_capacity = fields.Integer(compute='_compute_water_capacity', string="Potable capacity")
    no_potable_capacity = fields.Integer(compute='_compute_water_capacity', string="No potable capacity")
    potable_per_cap = fields.Integer(compute='_compute_water_per_cap', string="Potable por persona")
    no_potable_per_cap = fields.Integer(compute='_compute_water_per_cap', string="No potable por persona")

    @api.depends('means_supply_ids')
    def _compute_water_capacity(self):
        for rec in self:
            if rec.means_supply_ids:
                for item in rec.means_supply_ids:
                    if item.is_potable:
                        rec.potable_capacity += (item.capacity or 0)
                    else:
                        rec.no_potable_capacity += (item.capacity or 0)
            else:
                rec.potable_capacity, rec.no_potable_capacity = 0, 0

    @api.depends('means_supply_ids')
    def _compute_water_per_cap(self):
        for rec in self:
            population = sum([(home.population or 0) for home in rec.home_ids])
            if population:
                potable = sum([(supply.capacity or 0) for supply in rec.means_supply_ids if supply.is_potable])
                no_potable = sum([(supply.capacity or 0) for supply in rec.means_supply_ids if not supply.is_potable])
                rec.potable_per_cap = round(potable / population, 0)
                rec.no_potable_per_cap = round(no_potable / population, 0)
            else:
                rec.potable_per_cap = 0
                rec.no_potable_per_cap = 0



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
        action = self.env.ref('sias.action_charts_page').read()[0]
        action.update({'params': {
                        'survey_id': 0,
                        'community_id': [self.id]
                    }})
        return action


class MeansSupply(models.Model):
    _name = 'sias.means.supply'

    community_id = fields.Many2one('sias.community', required=True, ondelete='restrict', string="Community")
    means_supply_type_id = fields.Many2one('sias.means.supply.type', required=True, ondelete='restrict',
                                           string="Means Supply Type")
    capacity = fields.Integer('Capacity')
    is_potable = fields.Boolean('Is potable?')
    pump_type = fields.Selection([
        ('manual', 'Manual'),
        ('electric', 'Eléctrica'),
        ('windmill', 'Molino de viento'),
        ('solar', 'Solar')
    ], string="Pump type", default='manual')
    is_new = fields.Boolean('Is new?')



class Home(models.Model):
    _name = 'sias.home'
    _inherits = {'res.partner': 'partner_id'}
    _rec_name = 'display_name'

    # home_code = fields.Char(string='Code', compute='_get_home_code')
    partner_id = fields.Many2one('res.partner', required=True, ondelete='restrict', auto_join=True,
                                 string='Related Partner', help='Partner-related data of the home')
    home_number = fields.Char("Home number")
    community_id = fields.Many2one('sias.community', required=True, ondelete='restrict', string="Community")
    observation = fields.Text("Observation")
    population = fields.Integer("Population quantity")
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

    @api.depends('name', 'community_id')
    def _compute_display_name(self):
        for partner in self:
            partner.display_name = partner.name + ' / ' + partner.community_id.name


class CommonDisease(models.Model):
    _name = 'sias.common.disease'

    name = fields.Char('Common disease')
    active = fields.Boolean("Active", default=True)


class Survey(models.Model):
    _name = 'sias.survey'

    name = fields.Char('Name')
    start_date = fields.Date("Start date", required=True)
    end_date = fields.Date("End date")
    description = fields.Text('Description')
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
    shower = fields.Boolean('Shower')
    filter = fields.Boolean('Filter')
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
    diseases_otros = fields.Boolean('Otros')
    common_disease_ids = fields.Many2many('sias.common.disease', string="Enfermedades comunes")
    observation = fields.Text('Observation')

    community_id = fields.Many2one(related='home_id.community_id', string="Community")

    @api.model
    def create(self, vals):
        home = self.env['sias.home'].search([('id', '=', vals['home_id'])])
        home.write({'population': vals['population']})
        record = super(SurveyInput, self).create(vals)
        return record

    @api.multi
    def write(self, vals):
        for rec in self:
            if vals.get('population'):
                last_survey_input = rec.search([('home_id', '=', rec.home_id.id)]).sorted(key=lambda r: r.create_date)[-1]
                if last_survey_input.id == rec.id:
                    rec.home_id.write({'population': vals['population']})
        return super(SurveyInput, self).write(vals)


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

    def _charts_data(self, community_id, survey_id):
        survey_inputs = None
        if not survey_id:
            survey = self._get_last_survey()
            survey_id = survey.id if survey else survey_id
        if survey_id:
            if community_id:
                survey_inputs = self.search([['community_id', 'in', community_id], ['survey_id', '=', survey_id]])
            else:
                survey_inputs = self.search([['survey_id', '=', survey_id]])
        return survey_inputs

    def _get_gender_data(self, survey_inputs):
        result = []
        womens_quant = 0
        mens_quant = 0

        for item in survey_inputs:
            if item.population:
                womens_quant += item.womens or 0
                mens_quant += item.mens or 0

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

        for item in survey_inputs:
            lt_20 += item.lt_20 or 0
            gtoeq_20 += item.gtoeq_20 or 0

        if lt_20 or gtoeq_20:
            result = [{
                'name': 'Menor',
                'y': lt_20
            }, {
                'name': 'Mayor o igual',
                'y': gtoeq_20
            }]

        return result

    def _get_sump_data(self, survey_inputs):
        with_sump = 0
        without_sump = 0

        for item in survey_inputs:
            if item.sump:
                with_sump += 1
            else:
                without_sump += 1

        result = [{
                    'name': 'Posee letrina',
                    'y': with_sump
                }, {
                    'name': 'No posee letrina',
                    'y': without_sump
                }]

        return result

    def _get_source_distance_data(self, survey_inputs):
        mts5 = 0
        mts60 = 0
        mts100 = 0
        mts300 = 0
        mts350 = 0
        mts400 = 0
        mts500 = 0

        for item in survey_inputs:
            if item.source_distance == '5':
                mts5 += 1
            elif item.source_distance == '60':
                mts60 += 1
            elif item.source_distance == '100':
                mts100 += 1
            elif item.source_distance == '300':
                mts300 += 1
            elif item.source_distance == '350':
                mts350 += 1
            elif item.source_distance == '400':
                mts400 += 1
            elif item.source_distance == '500':
                mts500 += 1

        if mts5 + mts60 + mts100 + mts300 + mts350 + mts400 + mts500 > 0:
            return [{
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
            return []

    def _get_water_qualification_data(self, survey_inputs):
        buena = 0
        regular = 0

        for item in survey_inputs:
            if item.water_qualification == 'buena':
                buena += 1
            elif item.water_qualification == 'regular':
                regular += 1

        if buena + regular > 0:
            return [
                    {
                        'name': 'Buena',
                        'y': buena
                    },
                    {
                        'name': 'Regular',
                        'y': regular
                    }
            ]
        else:
            return []

    def _get_water_treatment_data(self, survey_inputs):
        ninguno = 0
        filtrado = 0

        for item in survey_inputs:
            if item.water_treatment == 'ninguno':
                ninguno += 1
            elif item.water_treatment == 'filtrado':
                filtrado += 1
        if ninguno + filtrado > 0:
            return [{
                'name': 'Ninguno',
                'y': ninguno
            }, {
                'name': 'Filtrado',
                'y': filtrado
            }]
        else:
            return []

    def _get_common_diseases_data(self, survey_inputs):
        common_diseases = self.env['sias.common.disease'].search([])
        result = [{'name': cd.name, 'y': 0} for cd in common_diseases]

        for survey_input in survey_inputs:
            for disease in survey_input.common_disease_ids:
                cnt = 0
                for i in result:
                    if i['name'] == disease.name:
                        result[cnt]['y'] += 1
                        break
                    cnt += 1

        if sum([item['y'] for item in result]) > 0:
            return result
        else:
            return []

    def get_water_supply_data(self, survey_inputs):
        propio = 0
        comunitario = 0

        for item in survey_inputs:
            if item.water_supply == 'aljibe_propio':
                propio += 1
            elif item.water_supply == 'aljibe_comunitario':
                comunitario += 1
        if propio + comunitario > 0:
            return [{
                    'name': 'Aljibe propio',
                    'y': propio
                    }, {
                        'name': 'Aljibe comunitario',
                        'y': comunitario
                    }]
        else:
            return []

    def get_occupation_data(self, survey_inputs):
        agricultor = 0
        jornalero = 0

        for item in survey_inputs:
            agricultor += item.occupation_agricultor or 0
            jornalero += item.occupation_jornalero or 0

        if agricultor + jornalero > 0:
            return [{
                    'name': 'Agricultor',
                    'y': agricultor
                }, {
                    'name': 'Jornalero',
                    'y': jornalero
                }]
        else:
            return []

    def get_education_data(self, survey_inputs):
        primario = 0
        secundario = 0
        sin_instruccion = 0

        for item in survey_inputs:
            primario += item.education_primario or 0
            secundario += item.education_secundario or 0
            sin_instruccion += item.education_sin_instruccion or 0

        if primario + secundario + sin_instruccion > 0:
            return [{
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
            return []

    @api.multi
    def get_charts_data(self, **kwargs):
        community_id = kwargs['community_id'] if kwargs.get('community_id') else None
        survey_id = kwargs['survey_id'] if kwargs.get('survey_id') else None

        survey_inputs = self._charts_data(community_id, survey_id)
        if survey_inputs:
            chart = kwargs['chart']
            if chart == 'gender':
                return self._get_gender_data(survey_inputs)
            elif chart == 'population':
                return self._get_population_data(survey_inputs)
            elif chart == 'sump':
                return self._get_sump_data(survey_inputs)
            elif chart == 'source_distance':
                return self._get_source_distance_data(survey_inputs)
            elif chart == 'water_qualification':
                return self._get_water_qualification_data(survey_inputs)
            elif chart == 'water_treatment':
                return self._get_water_treatment_data(survey_inputs)
            elif chart == 'common_diseases':
                return self._get_common_diseases_data(survey_inputs)
            elif chart == 'water_supply':
                return self.get_water_supply_data(survey_inputs)
            elif chart == 'occupation':
                return self.get_occupation_data(survey_inputs)
            elif chart == 'education':
                return self.get_education_data(survey_inputs)
            else:
                return []



"""
Wizard for select community before dashboard

"""


class PreChartsPage(models.TransientModel):
    _name = 'sias.pre.charts.page.wizard'

    def _get_last_survey(self):
        last_survey = self.env['sias.survey'].search([])
        if last_survey:
            last_survey = last_survey.sorted(key=lambda r: r.create_date)[-1]
        return last_survey

    survey_id = fields.Many2one('sias.survey', default=_get_last_survey)
    community_ids = fields.Many2many('sias.community', string="Communities")

    def open_charts_page(self):
        action = self.env.ref('sias.action_charts_page').read()[0]

        survey_id = self.survey_id and self.survey_id.id or 0
        community_list = [community.id for community in self.community_ids]

        action.update({'params': {
                        'survey_id': survey_id,
                        'community_id': community_list
                    }})
        return action

# -*- coding: utf-8 -*-

from openerp import models, fields, api


class SuccessoralDonation(models.Model):
    _name = 'successoral.donation'

    calcul_id = fields.Many2one('successoral.calcul')
    heritier_id = fields.Many2one('successoral.heritier')

    amount = fields.Float()
    origine = fields.Selection([
        ('commun', 'Patrimoine commun des époux donateurs'),
        ('propre', 'Patrimoine propre du donateur'),
    ])
    type = fields.Selection([
        ('immeuble', 'Bien immeuble (tarif ordinaire)'),
        ('meuble', 'Bien meuble (tarif ordinaire)'),
        ('dunno', 'Bien dunno (tarif ordinaire)'),
    ])

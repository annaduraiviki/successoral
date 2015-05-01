# -*- coding: utf-8 -*-

from openerp import models, fields, api


class SuccessoralHeritiers(models.Model):
    _name = 'successoral.heritier'

    calcul_id = fields.Many2one('successoral.calcul')

    nom = fields.Char()
    prenom = fields.Char()
    name = fields.Char(compute='_compute_full_name')
    lien = fields.Selection([
        ('epoux', 'Epoux'),
        ('cohabitant', 'Cohabitant'),
        ('frere', 'Frere ou soeur'),
        ('enfant', 'Enfant'),
        ('petit-enfant', 'Petit-Enfant'),
        ('oncle', 'Oncle ou tante'),
        ('neveu', 'Neveu ou niece'),
        ('entreprise', '(Petites et moyennes) entreprise'),
        ('autre', 'Autre'),
    ])
    ligne_directe = fields.Boolean(compute='_compute_ligne_directe', store=True)
    date_naissance = fields.Date()
    is_hand = fields.Boolean()
    is_dead = fields.Boolean()

    donation_ids = fields.One2many('successoral.donation', 'heritier_id', 'Donations')
    disposition_ids = fields.One2many('successoral.disposition', 'heritier_id', 'Dispositions')

    @api.one
    @api.depends('nom', 'prenom')
    def _compute_full_name(self):
        self.name = self.prenom + ' ' + self.nom

    @api.one
    @api.depends('lien', 'calcul_id.heritier_ids')
    def _compute_ligne_directe(self):
        if self.lien == 'epoux' or \
         self.lien == 'cohabitant' or \
         self.lien == 'enfant' or \
         (not self.calcul_id.heritier_ids.filtered(lambda x: x.lien == 'enfant') and self.lien == 'petit-enfant'):
            self.ligne_directe = True
            print('%s ligne directe' % self.prenom)
        else:
            self.ligne_directe = False
            print('%s PAS ligne directe' % self.prenom)

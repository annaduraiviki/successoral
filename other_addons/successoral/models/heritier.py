# -*- coding: utf-8 -*-

from openerp import models, fields, api


class SuccessoralHeritiers(models.Model):
    _name = 'successoral.heritier'

    calcul_id = fields.Many2one('successoral.calcul')

    nom = fields.Char()
    prenom = fields.Char()
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

    def _compute_ligne_directe(self):
        import pudb; pudb.set_trace()
        if self.lien == 'epoux' or self.lien == 'cohabitant' or self.lien == 'enfant' or (not calcul_id.self_ids.filtered(lambda x: x.lien == 'enfant') and self.lien == 'petit-enfant'):
            self.ligne_directe = True
        else:
            self.ligne_directe = False

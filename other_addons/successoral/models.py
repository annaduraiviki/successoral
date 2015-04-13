# -*- coding: utf-8 -*-

from openerp import models, fields, api


class SuccessoralCalcul(models.Model):
    _name = 'successoral.calcul'

    uid = fields.Char('UID')
    step = fields.Integer(default=0)

    # 1. REGION
    region_region = fields.Selection([
        ('nl', 'Région flamande'),
        ('fr', 'Région wallonne'),
        ('bx', 'Région de Bruxelles-Capitale'),
    ], default='fr')

    # 2. DEFUNT
    defunt_nom = fields.Char('Nom')
    defunt_prenom = fields.Char('Prénom')
    defunt_date_naissance = fields.Date('Date de naissance')

    # 2. FAMILLE
    famille_name = fields.Char('Nom', default="Mr. Nobody")

    # 3. CHOIX DE VIE

    # 4. HERITIERS
    heritiers_ids = fields.One2many('successoral.heritier', 'calcul_id')

    # 5. BIENS
    biens_cong_actif_mobilier = fields.Float()
    biens_propre_actif_mobilier = fields.Float()
    biens_propre_passif_mobilier = fields.Float()
    biens_conjug_logement_familial = fields.Float()
    biens_propre_logement_familial = fields.Float()
    biens_propre_logement_passif = fields.Float()
    biens_conjug_autres = fields.Float()
    biens_propre_autres = fields.Float()
    biens_propre_passif = fields.Float()
    biens_conjug_entreprise_actif = fields.Float()
    biens_propre_entreprise_actif = fields.Float()
    biens_conjug_dettes = fields.Float()
    biens_propre_dettes = fields.Float()
    biens_frais_funeraires = fields.Float()
    biens_check1 = fields.Boolean()
    biens_check2 = fields.Boolean()
    biens_check3 = fields.Boolean()
    biens_check4 = fields.Boolean()

    # 6. DONATION
    donation_ids = fields.One2many('successoral.donation', 'calcul_id')

    # 7 DISPOSITIONS


class SuccessoralDonation(models.Model):
    _name = 'successoral.donation'

    calcul_id = fields.Many2one('successoral.calcul')

    nom = fields.Char()
    lien = fields.Selection([
        ('enfant', 'Enfant'),
        ('parent', 'Parent'),

    ])
    montant = fields.Float()
    origine = fields.Selection([
        ('commun', 'Patrimoine commun des époux donateurs'),
        ('propre', 'Patrimoine propre du donateur'),
    ])
    type = fields.Selection([
        ('immeuble', 'Bien immeuble (tarif ordinaire)'),
        ('meuble', 'Bien meuble (tarif ordinaire)'),
        ('dunno', 'Bien dunno (tarif ordinaire)'),
    ])
    moment = fields.Selection([
        ('moins_3_ans', 'Moins de 3 ans avant le décès'),
        ('', ''),
    ])


class SuccessoralHeritiers(models.Model):
    _name = 'successoral.heritier'

    calcul_id = fields.Many2one('successoral.calcul')

    nom = fields.Char()
    prenom = fields.Char()
    lien = fields.Selection([
        ('enfant', 'Enfant'),
        ('epoux', 'Epoux'),
        ('petit-enfant', 'Petit-Enfant'),
    ])
    date_naissance = fields.Date()
    is_hand = fields.Boolean()
    is_dead = fields.Boolean()

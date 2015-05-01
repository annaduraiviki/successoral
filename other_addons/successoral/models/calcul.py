# -*- coding: utf-8 -*-

import logging

from openerp import models, fields, api
from datetime import datetime


_logger = logging.getLogger(__name__)


class SuccessoralCalcul(models.Model):
    _name = 'successoral.calcul'

    uid = fields.Char('UID')
    step = fields.Integer(default=0)

    # 1. REGION
    region_region = fields.Selection([
        ('nl', 'Région flamande'),
        ('fr', 'Région wallonne'),
        ('bx', 'Région de Bruxelles-Capitale'),
    ], default='bx')

    # 2. DEFUNT
    defunt_nom = fields.Char('Nom')
    defunt_prenom = fields.Char('Prénom')
    defunt_date_naissance = fields.Date('Date de naissance')

    # 3. CHOIX DE VIE

    # 4. HERITIERS
    heritier_ids = fields.One2many('successoral.heritier', 'calcul_id')

    # 5. BIENS
    biens_conjug_actif_mobilier = fields.Float(default=0.0)
    biens_conjug_logement_familial = fields.Float(default=0.0)
    biens_conjug_autres = fields.Float(default=0.0)
    biens_conjug_entreprise_actif = fields.Float(default=0.0)
    biens_conjug_dettes = fields.Float(default=0.0)

    biens_conjug_total = fields.Float(compute='_compute_biens_conjug_total')
    biens_conjug_dettes_total = fields.Float(compute='_compute_biens_conjug_dettes_total')

    biens_propre_actif_mobilier = fields.Float(default=0.0)
    biens_propre_passif_mobilier = fields.Float(default=0.0)
    biens_propre_logement_familial = fields.Float(default=0.0)
    biens_propre_logement_passif = fields.Float(default=0.0)
    biens_propre_autres = fields.Float(default=0.0)
    biens_propre_passif = fields.Float(default=0.0)
    biens_propre_entreprise_actif = fields.Float(default=0.0)
    biens_propre_dettes = fields.Float(default=0.0)

    biens_frais_funeraires = fields.Float(default=0.0)
    biens_check1 = fields.Boolean()
    biens_check2 = fields.Boolean()
    biens_check3 = fields.Boolean()
    biens_check4 = fields.Boolean()

    # 6. DONATION
    donation_ids = fields.One2many('successoral.donation', 'calcul_id')

    # 7 DISPOSITIONS
    disposition_ids = fields.One2many('successoral.disposition', 'calcul_id')

    # RESULTS
    immobilier_net = fields.Float(compute='_compute_actif_net', store=True)
    actif_net = fields.Float(compute='_compute_actif_net', store=True)

    @api.one
    @api.depends(
        'biens_conjug_actif_mobilier', 'biens_conjug_logement_familial', 'biens_conjug_autres',
        'biens_conjug_entreprise_actif')
    def _compute_biens_conjug_total(self):
        self.biens_conjug_total = self.biens_conjug_actif_mobilier + self.biens_conjug_logement_familial + self.biens_conjug_entreprise_actif

    @api.one
    @api.depends('biens_conjug_dettes')
    def _compute_biens_conjug_dettes_total(self):
        self.biens_conjug_dettes_total = self.biens_conjug_dettes

    @api.one
    @api.depends(
        'biens_conjug_actif_mobilier', 'biens_propre_actif_mobilier', 'biens_propre_passif_mobilier',
        'biens_conjug_logement_familial', 'biens_propre_logement_familial', 'biens_propre_logement_passif',
        'biens_conjug_autres', 'biens_propre_autres', 'biens_propre_passif', 'biens_conjug_entreprise_actif',
        'biens_propre_entreprise_actif', 'biens_conjug_dettes', 'biens_propre_dettes', 'biens_frais_funeraires')
    def _compute_actif_net(self):
        biens_conjug_net = (self.biens_conjug_actif_mobilier + self.biens_conjug_logement_familial + self.biens_conjug_autres +
                            self.biens_conjug_entreprise_actif - self.biens_conjug_dettes) / 2.
        biens_propre_net = (self.biens_propre_actif_mobilier - self.biens_propre_passif_mobilier + self.biens_propre_logement_familial -
                            self.biens_propre_logement_passif + self.biens_propre_autres - self.biens_propre_passif +
                            self.biens_propre_entreprise_actif - self.biens_propre_dettes)
        self.immobilier_net = self.biens_conjug_logement_familial/2. + self.biens_propre_logement_familial - self.biens_propre_logement_passif
        self.actif_net = biens_conjug_net + biens_propre_net - self.biens_frais_funeraires

    def compute(self):
        results = []

        # Calcul de l'usufruit et la nue-propriété
        epoux = self.heritier_ids.filtered(lambda x: x.lien in ['epoux', 'cohabitant'])
        if len(epoux) > 1:
            _logger.exception('It cannot be more than one epoux')
            raise Exception
        others = self.heritier_ids.filtered(lambda x: x.lien not in ['epoux', 'cohabitant'])

        print('epoux : %s and others : %s' % (epoux.name, others))

        US, NP = 0, 1
        if epoux:
            US, NP = self._us_np(epoux.date_naissance)
        taux = {}

        # Calcul du taux de chaque héritier
        for heritier in self.heritier_ids:
            if others:
                if heritier == epoux:
                    taux[heritier] = US
                else:
                    taux[heritier] = NP/float(len(others))
            else:
                taux[heritier] = 1
            print('taux of %s = %s' % (heritier.name, taux[heritier]))

        # Calcul des droits de succession pour chaque héritier
        for heritier in self.heritier_ids:

            # TODO: définir le membre de gauche
            # ? virer le passif succession ?
            amount_immobilier = self.immobilier_net - self.biens_frais_funeraires
            amount_immobilier *= taux[heritier]
            amount_immobilier_imposable = amount_immobilier

            if heritier.lien in ['epoux', 'cohabitant']:
                # 55 bis
                _logger.warning('55 bis : on ne calcule pas les droits sur le logement conjug (%s €)' % self.biens_conjug_logement_familial)
                amount_immobilier_imposable -= (taux[heritier]*self.biens_conjug_logement_familial/2.)

            # TODO: définir le membre de droite
            amount_reste = self.actif_net - self.immobilier_net
            amount_reste *= taux[heritier]

            # au reste, on ajoute le montant des dispositions
            # TODO: donations ?
            for disposition in heritier.disposition_ids:
                amount_reste += disposition.amount

            amount_reste_imposable = amount_reste

            # Calcul des droits
            droits_immobilier, taux_immobilier = self._droits_succession(heritier, amount_immobilier_imposable, type='immobilier')
            droits_reste, taux_reste = self._droits_succession(heritier, amount_reste_imposable, type='mobilier')

            amount_total = amount_immobilier + amount_reste
            droits_total = droits_immobilier + droits_reste

            _logger.info('Droits pour %s %s : %s (immobilier (%s) = %s, reste (%s) = %s)' % (heritier.prenom, heritier.nom, droits_total, amount_immobilier, droits_immobilier, amount_reste, droits_reste))

            results.append({
                'heritier_id': heritier,
                'amount_immobilier': amount_immobilier,
                'taux_immobilier': taux_immobilier,
                'droits_immobilier': droits_immobilier,
                'amount_reste': amount_reste,
                'taux_reste': taux_reste,
                'droits_reste': droits_reste,
                'amount_total': amount_total,
                'droits_total': droits_total,
            })
        print results
        return results

    def _us_np(self, date_naissance):
        diff = (datetime.now() - datetime.strptime(date_naissance, '%Y-%m-%d'))
        age = int(diff.days/365.2425)
        _logger.info('age epoux : %s' % age)
        if age < 21:
            return 0.72, 0.28
        elif age < 31:
            return 0.68, 0.32
        elif age < 41:
            return 0.64, 0.36
        elif age < 51:
            return 0.56, 0.44
        elif age < 56:
            return 0.52, 0.48
        elif age < 61:
            return 0.44, 0.56
        elif age < 66:
            return 0.38, 0.62
        elif age < 71:
            return 0.32, 0.68
        elif age < 76:
            return 0.24, 0.76
        elif age < 81:
            return 0.16, 0.84
        else:
            return 0.08, 0.92

    def _droits_succession(self, heritier, amount, type='immobilier', specials={}, cat=None):

        # specials : abattement_15000, abattement_25000

        if amount <= 0:
            return 0, 0

        if self.region_region == 'bx':
            if not cat:
                if (heritier.lien == 'epoux' or heritier.ligne_directe) and type == 'residence_principale':
                    cat = '2'
                elif (heritier.lien == 'epoux' or heritier.ligne_directe) and type != 'residence_principale':
                    cat = '1a'
                elif heritier.lien == 'frere':
                    cat = '1b'
                elif heritier.lien == 'oncle' or heritier.lien == 'neveu':
                    cat = '1c'
                elif heritier.lien == 'entreprise':
                    cat = '1e'
                else:
                    _logger.exception('This lien (%s) does not exist' % heritier.lien)
                    raise Exception

            _logger.info('%s (%s): cat = %s' % (heritier.nom, heritier.lien, cat))

            if cat == '1a':
                # ligne directe, epoux et cohabitant legal
                if 'abattement_15000' in specials:
                    if amount <= 15000:
                        return 0, 0
                    elif amount <= 50000:
                        return 0.03*amount, 0.03
                    elif amount <= 100000:
                        return 1050 + 0.08*(amount-50000), 0.08
                    elif amount <= 175000:
                        return 5050 + 0.09*(amount-100000), 0.09
                    elif amount <= 250000:
                        return 11800 + 0.18*(amount-175000), 0.18
                    elif amount <= 500000:
                        return 25300 + 0.24*(amount-250000), 0.24
                    else:
                        return 85300 + 0.30*(amount-500000), 0.30
                else:
                    if amount <= 15000:
                        return 0.03*amount, 0.03
                    elif amount <= 50000:
                        return 0.03*amount, 0.03
                    elif amount <= 100000:
                        return 1500 + 0.08*(amount-50000), 0.08
                    elif amount <= 175000:
                        return 5500 + 0.09*(amount-100000), 0.09
                    elif amount <= 250000:
                        return 12250 + 0.18*(amount-175000), 0.18
                    elif amount <= 500000:
                        return 25750 + 0.24*(amount-250000), 0.24
                    else:
                        return 85750 + 0.30*(amount-500000), 0.30

            elif cat == '1b':
                if amount <= 12500:
                    return 0.2*amount, 0.2
                elif amount <= 25000:
                    return 2500 + 0.25*(amount-12500), 0.25
                elif amount <= 50000:
                    return 5625 + 0.3*(amount-25000), 0.3
                elif amount <= 100000:
                    return 13125 + 0.4*(amount-50000), 0.4
                elif amount <= 175000:
                    return 33125 + 0.55*(amount-100000), 0.55
                elif amount <= 250000:
                    return 74375 + 0.6*(amount-175000), 0.6
                else:
                    return 119375 + 0.65*(amount-250000), 0.65

            elif cat == '1c':
                if amount <= 50000:
                    return 0.35*amount, 0.35
                elif amount <= 100000:
                    return 17500 + 0.5*(amount-50000), 0.5
                elif amount <= 1750000:
                    return 42500 + 0.6*(amount-100000), 0.6
                else:
                    return 87500 + 0.7*(amount-1750000), 0.7

            elif cat == '1d':
                if amount <= 50000:
                    return 0.4*amount, 0.4
                elif amount <= 75000:
                    return 20000 + 0.55*(amount-50000), 0.55
                elif amount <= 175000:
                    return 33750 + 0.65*(amount-75000), 0.65
                else:
                    return 98750 + 0.8*(amount-175000), 0.8

            elif cat == '1e':
                return 0.03 * amount, 0.03

            elif cat == '2':
                if amount <= 50000:
                    return 0.02*amount, 0.02
                elif amount <= 100000:
                    return 1000 + 0.053*(amount-50000), 0.053
                elif amount <= 175000:
                    return 3650 + 0.06*(amount-100000), 0.6
                elif amount <= 250000:
                    return 8150 + 0.12*(amount-175000), 0.12
                elif amount <= 500000:
                    return 17150 + 0.24*(amount-250000), 0.24
                else:
                    return 77150 + 0.3*(amount-500000), 0.3
            else:
                raise Exception

        elif self.region_region == 'fr':
            # TODO
            print 'TODO'
            return 0, 0
        elif self.region_region == 'nl':
            # TODO
            print 'TODO'
            return 0, 0
        else:
            raise Exception

# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request

import openerp

from datetime import timedelta, datetime
import time
import uuid
import werkzeug


def _get_calcul(uid):
    return request.env['successoral.calcul'].sudo().search([('uid', '=', uid)])


class Successoral(openerp.addons.website.controllers.main.Website):

    @http.route('/', auth='public')
    def home(self, **kw):
        return http.request.render('successoral.home', {
        })

    @http.route('/begin', auth='public')
    def begin(self, **kw):
        calcul = request.env['successoral.calcul'].sudo().create({
            'uid': uuid.uuid4(),
        })
        # BEGIN always shows region first
        return werkzeug.utils.redirect('/region/%s' % calcul.uid)

    @http.route('/region/<string:uid>', auth='public')
    def region(self, uid, **kw):
        calcul = _get_calcul(uid)

        return http.request.render('successoral.region', {
            'calcul': calcul,
        })

    @http.route('/save-region/<string:uid>', auth='public')
    def save_region(self, uid, **kw):
        calcul = _get_calcul(uid)

        if calcul.step < 1:
            calcul.step = 1

        # DEAL WITH POST PARAMETERS
        if kw.get('selected_region'):
            calcul.region_region = str(kw.get('selected_region'))

        if kw.get('show'):
            return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
        else:
            return werkzeug.utils.redirect('/defunt/%s' % calcul.uid)

    @http.route('/defunt/<string:uid>', auth='public')
    def defunt(self, uid, **kw):
        calcul = _get_calcul(uid)

        return http.request.render('successoral.defunt', {
            'calcul': calcul,
        })

    @http.route('/save-defunt/<string:uid>', auth='public')
    def save_defunt(self, uid, **kw):
        calcul = _get_calcul(uid)

        if calcul.step < 2:
            calcul.step = 2

        # DEAL WITH POST PARAMETERS
        if kw.get('defunt_prenom'):
            calcul.defunt_prenom = str(kw.get('defunt_prenom'))
        if kw.get('defunt_nom'):
            calcul.defunt_nom = str(kw.get('defunt_nom'))
        if kw.get('defunt_date_naissance'):
            calcul.defunt_date_naissance = datetime.strptime(str(kw.get('defunt_date_naissance')), '%d-%m-%Y')

        if kw.get('show'):
            return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
        else:
            return werkzeug.utils.redirect('/heritiers/%s' % calcul.uid)

    # @http.route('/famille/<string:uid>', auth='public')
    # def famille(self, uid, **kw):
    #     calcul = _get_calcul(uid)

    #     return http.request.render('successoral.famille', {
    #         'calcul': calcul,
    #     })

    # @http.route('/save-famille/<string:uid>', auth='public')
    # def save_famille(self, uid, **kw):
    #     calcul = _get_calcul(uid)

    #     if calcul.step < 3:
    #         calcul.step = 3
    #     # DEAL WITH POST PARAMETERS

    #     if kw.get('show'):
    #         return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
    #     else:
    #         return werkzeug.utils.redirect('/heritiers/%s' % calcul.uid)

    # @http.route('/vie/<string:uid>', auth='public')
    # def vie(self, uid, **kw):
    #     calcul = _get_calcul(uid)

    #     return http.request.render('successoral.vie', {
    #         'calcul': calcul,
    #     })

    # @http.route('/save-vie/<string:uid>', auth='public')
    # def save_vie(self, uid, **kw):
    #     calcul = _get_calcul(uid)

    #     if calcul.step < 3:
    #         calcul.step = 3
    #     # DEAL WITH POST PARAMETERS

    #     if kw.get('show'):
    #         return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
    #     else:
    #         return werkzeug.utils.redirect('/heritiers/%s' % calcul.uid)

    @http.route('/heritiers/<string:uid>', auth='public')
    def heritiers(self, uid, **kw):
        calcul = _get_calcul(uid)

        all_liens = [
            ['epoux', 'Epoux'],
            ['cohabitant', 'Cohabitant'],
            ['frere', 'Frère ou soeur'],
            ['enfant', 'Enfant'],
            ['petit-enfant', 'Petit-enfant'],
            ['oncle', 'Oncle ou tante'],
            ['neveu', 'Neveu ou niece'],
            ['entreprise', '(Petite ou moyenne) entreprise'],
            ['autre', 'Autre']
        ]

        return http.request.render('successoral.heritiers', {
            'calcul': calcul,
            'all_liens': all_liens,
        })

    @http.route('/save-heritiers/<string:uid>', auth='public')
    def save_heritiers(self, uid, **kw):
        calcul = _get_calcul(uid)

        if calcul.step < 3:
            calcul.step = 3
        # DEAL WITH POST PARAMETERS

        if kw.get('show'):
            return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
        else:
            return werkzeug.utils.redirect('/biens/%s' % calcul.uid)

    @http.route('/ajout-heritiers/<string:uid>', auth='public')
    def ajout_heritiers(self, uid, **kw):

        calcul = _get_calcul(uid)

        heritier = None

        values = {
            'nom': kw.get('heritier_nom'),
            'prenom': kw.get('heritier_prenom'),
            'lien': kw.get('heritier_lien'),
            'date_naissance': kw.get('heritier_date_naissance'),
            'is_hand': kw.get('heritier_is_hand'),
            'is_dead': kw.get('heritier_is_dead'),
        }

        if values['lien'] == 'epoux' and calcul.heritier_ids.filtered(lambda x: x.lien == 'epoux'):
            return self._error(uid, 'Il ne peut y avoir que un seul époux', '/heritiers/%s' % calcul.uid)

        if kw.get('heritier_id'):
            heritier = request.env['successoral.heritier'].sudo().browse(int(kw.get('heritier_id')))
        if heritier:
            heritier.sudo().write(values)
        else:
            values['calcul_id'] = calcul.id
            heritier = request.env['successoral.heritier'].sudo().create(values)

        return werkzeug.utils.redirect('/heritiers/%s' % calcul.uid)

    @http.route('/biens/<string:uid>', auth='public')
    def biens(self, uid, **kw):
        calcul = _get_calcul(uid)

        return http.request.render('successoral.biens', {
            'calcul': calcul,
        })

    @http.route('/save-biens/<string:uid>', auth='public')
    def save_biens(self, uid, **kw):
        calcul = _get_calcul(uid)

        if calcul.step < 4:
            calcul.step = 4
        # DEAL WITH POST PARAMETERS

        if kw.get('biens_conjug_actif_mobilier'):
            calcul.biens_conjug_actif_mobilier = kw.get('biens_conjug_actif_mobilier')
        if kw.get('biens_propre_actif_mobilier'):
            calcul.biens_propre_actif_mobilier = kw.get('biens_propre_actif_mobilier')
        if kw.get('biens_propre_passif_mobilier'):
            calcul.biens_propre_passif_mobilier = kw.get('biens_propre_passif_mobilier')
        if kw.get('biens_conjug_logement_familial'):
            calcul.biens_conjug_logement_familial = kw.get('biens_conjug_logement_familial')
        if kw.get('biens_propre_logement_familial'):
            calcul.biens_propre_logement_familial = kw.get('biens_propre_logement_familial')
        if kw.get('biens_propre_logement_passif'):
            calcul.biens_propre_logement_passif = kw.get('biens_propre_logement_passif')
        if kw.get('biens_conjug_autres'):
            calcul.biens_conjug_autres = kw.get('biens_conjug_autres')
        if kw.get('biens_propre_autres'):
            calcul.biens_propre_autres = kw.get('biens_propre_autres')
        if kw.get('biens_propre_passif'):
            calcul.biens_propre_passif = kw.get('biens_propre_passif')
        if kw.get('biens_conjug_entreprise_actif'):
            calcul.biens_conjug_entreprise_actif = kw.get('biens_conjug_entreprise_actif')
        if kw.get('biens_propre_entreprise_actif'):
            calcul.biens_propre_entreprise_actif = kw.get('biens_propre_entreprise_actif')
        if kw.get('biens_conjug_dettes'):
            calcul.biens_conjug_dettes = kw.get('biens_conjug_dettes')
        if kw.get('biens_propre_dettes'):
            calcul.biens_propre_dettes = kw.get('biens_propre_dettes')
        if kw.get('biens_frais_funeraires'):
            calcul.biens_frais_funeraires = kw.get('biens_frais_funeraires')
        if kw.get('biens_check1'):
            calcul.biens_check1 = True
        else:
            calcul.biens_check1 = False
        if kw.get('biens_check2'):
            calcul.biens_check2 = True
        else:
            calcul.biens_check2 = False
        if kw.get('biens_check3'):
            calcul.biens_check3 = True
        else:
            calcul.biens_check3 = False
        if kw.get('biens_check4'):
            calcul.biens_check4 = True
        else:
            calcul.biens_check4 = False

        if kw.get('show'):
            return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
        else:
            return werkzeug.utils.redirect('/donation/%s' % calcul.uid)

    @http.route('/donation/<string:uid>', auth='public')
    def donation(self, uid, **kw):
        calcul = _get_calcul(uid)

        return http.request.render('successoral.donation', {
            'calcul': calcul,
        })

    @http.route('/save-donation/<string:uid>', auth='public')
    def save_donation(self, uid, **kw):
        calcul = _get_calcul(uid)

        if calcul.step < 4:
            calcul.step = 4

        if kw.get('show'):
            return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
        else:
            return werkzeug.utils.redirect('/dispositions/%s' % calcul.uid)

    @http.route('/ajout-donation/<string:uid>', auth='public')
    def ajout_donation(self, uid, **kw):
        calcul = _get_calcul(uid)

        donation = None
        values = {
            'heritier_id': kw.get('donation_heritier'),
            'amount': kw.get('donation_amount'),
            'origine': kw.get('donation_origine'),
            'type': kw.get('donation_type'),
        }
        if kw.get('donation_id'):
            donation = request.env['successoral.donation'].sudo().browse(int(kw.get('donation_id')))
        if donation:
                donation.sudo().write(values)
        else:
            values['calcul_id'] = calcul.id
            request.env['successoral.donation'].sudo().create(values)

        return werkzeug.utils.redirect('/donation/%s' % calcul.uid)

    @http.route('/ajout-disposition/<string:uid>', auth='public')
    def ajout_disposition(self, uid, **kw):
        calcul = _get_calcul(uid)

        values = {
            'heritier_id': kw.get('disposition_heritier'),
            'amount': kw.get('disposition_amount'),
            'origine': kw.get('disposition_origine'),
            'type': kw.get('disposition_type'),
        }
        disposition = None
        if kw.get('donation_id'):
            disposition = request.env['successoral.disposition'].sudo().browse(int(kw.get('disposition_id')))
        if disposition:
            disposition.sudo().write(values)
        else:
            values['calcul_id'] = calcul.id
            disposition = request.env['successoral.disposition'].sudo().create(values)

        return werkzeug.utils.redirect('/dispositions/%s' % calcul.uid)

    @http.route('/dispositions/<string:uid>', auth='public')
    def dispositions(self, uid, **kw):
        calcul = _get_calcul(uid)

        return http.request.render('successoral.dispositions', {
            'calcul': calcul,
        })

    @http.route('/save-dispositions/<string:uid>', auth='public')
    def save_dispositions(self, uid, **kw):
        calcul = _get_calcul(uid)

        if calcul.step < 5:
            calcul.step = 5

        if kw.get('show'):
            return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
        else:
            return werkzeug.utils.redirect('/results/%s' % calcul.uid)

    @http.route('/results/<string:uid>', auth='public')
    def results(self, uid, **kw):
        calcul = _get_calcul(uid)

        droits_succession = calcul.compute()

        return http.request.render('successoral.results', {
            'calcul': calcul,
            'droits_succession': droits_succession,
        })

    @http.route('/save-results/<string:uid>', auth='public')
    def save_results(self, uid, **kw):
        calcul = _get_calcul(uid)

        if kw.get('show'):
            return werkzeug.utils.redirect('/%s/%s' % (kw.get('show'), calcul.uid))
        else:
            return werkzeug.utils.redirect('/results/%s' % calcul.uid)

    def _error(self, uid, message, redirect):

        calcul = _get_calcul(uid)

        return http.request.render('successoral.error', {
            'calcul': calcul,
            'message': message,
            'redirect': redirect,
        })

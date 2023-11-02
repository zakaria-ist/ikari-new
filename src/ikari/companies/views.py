import datetime
import json
from copy import deepcopy
from django.conf import settings as s
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response, render, get_object_or_404
from django.template import RequestContext
from companies.forms import CostCentersForm, SegmentForm
from companies.models import Company, CostCenters
from countries.models import Country
from currencies.models import Currency
from staffs.models import Staff
from utilities.constants import TRN_CODE_TYPE_DICT, REVALUATION_METHODS, RATE_TYPES
from accounts.models import RevaluationCode, AccountType, Account, ReportGroup, DistributionCode, AccountSet
from banks.models import Bank
from currencies.models import ExchangeRate
from taxes.models import Tax, TaxAuthority, TaxGroup
from accounting.models import FiscalCalendar, Schedule, APGLIntegration, APGLIntegrationDetail, ARGLIntegration, ARGLIntegrationDetail, \
                                AROptions, APOptions


@login_required
def load_list(request):
    company = Company.objects.filter(is_hidden=0, is_active=1).order_by('-id')
    return render_to_response('company-list.html', RequestContext(request, {'companies': company}))


@login_required
def company_profile(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        country = Country.objects.get(pk=company.country_id)
        currency = Currency.objects.get(pk=company.currency_id)
        staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company.id)
        return render_to_response('company-view.html',
                                  RequestContext(request, {'company': company,
                                                           'country': country,
                                                           'currency': currency,
                                                           'staff': staff,
                                                           'menu_type': TRN_CODE_TYPE_DICT['Global'],
                                                           'media_url': s.MEDIA_URL}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist. " \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
def control_file(request):
    try:
        company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        company = Company.objects.get(pk=company_id)
        country = Country.objects.get(pk=company.country_id)
        currency = Currency.objects.get(pk=company.currency_id)
        staff = Staff.objects.filter(is_hidden=0, user_id=request.user.id, company_id=company.id)
        return render_to_response('company-view.html',
                                  RequestContext(request, {'company': company,
                                                           'country': country,
                                                           'currency': currency,
                                                           'staff': staff,
                                                           'menu_type': TRN_CODE_TYPE_DICT['Sales Number File'],
                                                           'media_url': s.MEDIA_URL}))
    except ObjectDoesNotExist:
        messages_error = "Company and Staff information of Current User does not exist. " \
                         "\nPlease input Company and Staff of Current User!"
        return render_to_response('404.html', RequestContext(request, {'messages_error': messages_error}))


@login_required
@permission_required('companies.change_company', login_url='/alert/')
def company_add(request):
    company = Company()
    country_list = Country.objects.filter(is_hidden=0)
    currency_list = Currency.objects.filter(is_hidden=0)
    company_list = Company.objects.all()
    if request.method == 'POST':
        try:
            with transaction.atomic():
                if request.POST.get('IsActive'):
                    company.is_active = True
                else:
                    company.is_active = False
                if request.POST.get('useSegment'):
                    company.use_segment = True
                else:
                    company.use_segment = False
                if request.POST.get('IsUseInventnory'):
                    company.is_inventory = True
                    request.session['use_inventory'] = 1
                else:
                    company.is_inventory = False
                    request.session['use_inventory'] = 0
                company.name = request.POST.get('name')
                company.company_number = request.POST.get('company_no')
                company.postal_code = request.POST.get('postal_code')
                company.address = request.POST.get('address')
                company.phone = request.POST.get('phone')
                company.email = request.POST.get('email')
                company.web = request.POST.get('web')
                company.fax = request.POST.get('fax')
                company.country = Country.objects.get(id=request.POST.get('country'))
                company.currency = Currency.objects.get(id=request.POST.get('currency'))
                company.create_date = datetime.datetime.today()
                company.update_date = datetime.datetime.today()
                company.update_by = request.user.id
                company.is_hidden = 0
                company.remit_remark = request.POST.get('remit_remark')
                company.copy_from_id = request.POST.get('copy_from_id')
                if request.POST.get('multicurrency-checkbox'):
                    company.is_multicurrency = True
                else:
                    company.is_multicurrency = False
                company.save()

                # Do Migration

                # AR and AP options
                ar_options = AROptions()
                ar_options.company_id = company.id
                ar_options.is_hidden = False
                ar_options.create_date = datetime.datetime.today()
                ar_options.update_date = datetime.datetime.today()
                ar_options.update_by = request.user.id
                ar_options.save()

                ap_options = APOptions()
                ap_options.company_id = company.id
                ap_options.is_hidden = False
                ap_options.create_date = datetime.datetime.today()
                ap_options.update_date = datetime.datetime.today()
                ap_options.update_by = request.user.id
                ap_options.save()

                # AP GL Integration
                list_gl_integration = APGLIntegration.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                for row in list_gl_integration:
                    new_row = deepcopy(row)
                    new_row.pk = None
                    new_row.company_id = company.id
                    new_row.save()
                    try:
                        detail = APGLIntegrationDetail.objects.get(is_hidden=0, parent_id=row.id)
                        new_detail = deepcopy(detail)
                        new_detail.pk = None
                        new_detail.parent_id = new_row.id
                        new_detail.save()
                    except:
                        pass
                # AR GL Integration
                list_gl_integration = ARGLIntegration.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                for row in list_gl_integration:
                    new_row = deepcopy(row)
                    new_row.pk = None
                    new_row.company_id = company.id
                    new_row.save()
                    try:
                        detail = ARGLIntegrationDetail.objects.get(is_hidden=0, parent_id=row.id)
                        new_detail = deepcopy(detail)
                        new_detail.pk = None
                        new_detail.parent_id = new_row.id
                        new_detail.save()
                    except:
                        pass

                list_revaluationcode = RevaluationCode.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_accountgroup = AccountType.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_accountcode = Account.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_bankscode = Bank.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_exchangerates = ExchangeRate.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_taxcode = Tax.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_reportgroup = ReportGroup.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_fiscalcalendar = FiscalCalendar.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_taxauthority = TaxAuthority.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_taxgroup = TaxGroup.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_schedule = Schedule.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_costcenter = CostCenters.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_distributioncode = DistributionCode.objects.filter(is_hidden=0, company_id=company.copy_from_id)
                list_accountset = AccountSet.objects.filter(is_hidden=0, company_id=company.copy_from_id)

                list_all = []
                list_all.append(list_revaluationcode)
                list_all.append(list_accountgroup)
                list_all.append(list_accountcode)
                list_all.append(list_bankscode)
                list_all.append(list_exchangerates)
                list_all.append(list_taxcode)
                list_all.append(list_reportgroup)
                list_all.append(list_fiscalcalendar)
                list_all.append(list_taxauthority)
                list_all.append(list_taxgroup)
                list_all.append(list_schedule)
                list_all.append(list_costcenter)
                list_all.append(list_distributioncode)
                list_all.append(list_accountset)

                # Migrate All list

                for current_list in list_all:
                    for row in current_list:
                        new_row = deepcopy(row)
                        new_row.pk = None
                        new_row.company_id = company.id
                        new_row.save()

                # Get all distribution codes & account sets
                list_distributioncode = DistributionCode.objects.filter(is_hidden=0, company_id=company.id)
                list_accountset = AccountSet.objects.filter(is_hidden=0, company_id=company.id)
                list_bank = Bank.objects.filter(is_hidden=0, company_id=company.id)
                list_reportgroup = ReportGroup.objects.filter(is_hidden=0, company_id=company.id)
                list_tax = Tax.objects.filter(is_hidden=0, company_id=company.id)
                list_taxauthority = TaxAuthority.objects.filter(is_hidden=0, company_id=company.id)
                list_taxgroup = TaxGroup.objects.filter(is_hidden=0, company_id=company.id)
                list_revaluationcode = RevaluationCode.objects.filter(is_hidden=0, company_id=company.id)
                list_account = Account.objects.filter(is_hidden=0, company_id=company.id)

                # Account code holder
                account_code_list = []
                tax_authority_code_list = []
                tax_group_code_list = []
                account_type_code_list = []
                cost_center_code_list = []

                # Store account code from distributioncode
                for distributioncode in list_distributioncode:
                    if distributioncode.gl_account != None and distributioncode.gl_account.code not in account_code_list:
                        account_code_list.append(distributioncode.gl_account.code)

                # Store account code from accountset
                for accountset in list_accountset:
                    if accountset.control_account != None and accountset.control_account.code not in account_code_list:
                        account_code_list.append(accountset.control_account.code)

                    if accountset.revaluation_realized_gain != None and accountset.revaluation_realized_gain.code not in account_code_list:
                        account_code_list.append(accountset.revaluation_realized_gain.code)

                    if accountset.revaluation_realized_loss != None and accountset.revaluation_realized_loss.code not in account_code_list:
                        account_code_list.append(accountset.revaluation_realized_loss.code)

                    if accountset.revaluation_unrealized_gain != None and accountset.revaluation_unrealized_gain.code not in account_code_list:
                        account_code_list.append(accountset.revaluation_unrealized_gain.code)

                    if accountset.revaluation_unrealized_loss != None and accountset.revaluation_unrealized_loss.code not in account_code_list:
                        account_code_list.append(accountset.revaluation_unrealized_loss.code)

                    if accountset.revaluation_rounding != None and accountset.revaluation_rounding.code not in account_code_list:
                        account_code_list.append(accountset.revaluation_rounding.code)

                    if accountset.discount_account != None and accountset.discount_account.code not in account_code_list:
                        account_code_list.append(accountset.discount_account.code)

                    if accountset.prepayment_account != None and accountset.prepayment_account.code not in account_code_list:
                        account_code_list.append(accountset.prepayment_account.code)

                    if accountset.writeoff_account != None and accountset.writeoff_account.code not in account_code_list:
                        account_code_list.append(accountset.writeoff_account.code)

                # store account code from bank
                for bank in list_bank:
                    if bank.account != None and bank.account.code not in account_code_list:
                        account_code_list.append(bank.account.code)

                # store account code from reportgroup
                for reportgroup in list_reportgroup:
                    if reportgroup.account_from != None and reportgroup.account_from.code not in account_code_list:
                        account_code_list.append(reportgroup.account_from.code)

                    if reportgroup.account_to != None and reportgroup.account_to.code not in account_code_list:
                        account_code_list.append(reportgroup.account_to.code)

                # store account code from tax
                for tax in list_tax:
                    if tax.tax_account_code != None and tax.tax_account_code.code not in account_code_list:
                        account_code_list.append(tax.tax_account_code.code)

                    if tax.tax_authority != None and tax.tax_authority.code not in tax_authority_code_list:
                        tax_authority_code_list.append(tax.tax_authority.code)

                    if tax.tax_group != None and tax.tax_group.code not in tax_group_code_list:
                        tax_group_code_list.append(tax.tax_group.code)

                # store account code from taxauthority
                for taxauthority in list_taxauthority:
                    if taxauthority.liability_account != None and taxauthority.liability_account.code not in account_code_list:
                        account_code_list.append(taxauthority.liability_account.code)

                    if taxauthority.recoverable_account != None and taxauthority.recoverable_account.code not in account_code_list:
                        account_code_list.append(taxauthority.recoverable_account.code)

                # store account from revaluationcode
                for revaluationcode in list_revaluationcode:
                    if revaluationcode.revaluation_unrealized_gain != None and revaluationcode.revaluation_unrealized_gain.code not in account_code_list:
                        account_code_list.append(revaluationcode.revaluation_unrealized_gain.code)

                    if revaluationcode.revaluation_unrealized_loss != None and revaluationcode.revaluation_unrealized_loss.code not in account_code_list:
                        account_code_list.append(revaluationcode.revaluation_unrealized_loss.code)

                # store taxcode from taxgroup
                for taxgroup in list_taxgroup:
                    if taxgroup.tax_authority != None and taxgroup.tax_authority.code not in tax_authority_code_list:
                        tax_authority_code_list.append(taxgroup.tax_authority.code)

                # store account_type from account
                for account in list_account:
                    if account.account_group != None and account.account_group.code not in account_type_code_list:
                        account_type_code_list.append(account.account_group.code)

                    if account.profit_loss_group != None and account.profit_loss_group.code not in account_type_code_list:
                        account_type_code_list.append(account.profit_loss_group.code)

                    if account.segment_code != None and account.segment_code.code not in cost_center_code_list:
                        cost_center_code_list.append(str(account.segment_code.code))

                # Get all account codes according to account_code_list
                account_list = Account.objects.filter(is_hidden=0, company_id=company.id, code__in=account_code_list)
                tax_authority_list = TaxAuthority.objects.filter(is_hidden=0, company_id=company.id, code__in=tax_authority_code_list)
                account_type_list = AccountType.objects.filter(is_hidden=0, company_id=company.id, code__in=account_type_code_list)
                cost_center_list = CostCenters.objects.filter(is_hidden=0, company_id=company.id, code__in=cost_center_code_list)
                tax_group_list = TaxGroup.objects.filter(is_hidden=0, company_id=company.id, code__in=tax_group_code_list)

                buffer = {}

                # Set account.code as key
                for account in account_list:
                    buffer[account.code] = account

                account_list = buffer

                buffer = {}

                # Set tax.code as key
                for tax_authority in tax_authority_list:
                    buffer[tax_authority.code] = tax_authority

                tax_authority_list = buffer

                buffer = {}

                # set taxgroup.code as key
                for tax_group in tax_group_list:
                    buffer[tax_group.code] = tax_group

                tax_group_list = buffer

                buffer = {}

                # set accounttype.code as key
                for account_type in account_type_list:
                    buffer[account_type.code] = account_type

                account_type_list = buffer

                buffer = {}

                # set costcenter.codde as key
                for cost_center in cost_center_list:
                    buffer[cost_center.code] = cost_center

                cost_center_list = buffer

                # Remove buffer variable
                del buffer

                # Set new account.id based on account.code
                for distributioncode in list_distributioncode:
                    if distributioncode.gl_account != None and distributioncode.gl_account.code in account_list:
                        distributioncode.gl_account_id = account_list[distributioncode.gl_account.code].id

                        distributioncode.save()

                for accountset in list_accountset:
                    if accountset.control_account != None and accountset.control_account.code in account_list:
                        accountset.control_account_id = account_list[accountset.control_account.code].id

                    if accountset.revaluation_realized_gain != None and accountset.revaluation_realized_gain.code in account_code_list:
                        accountset.revaluation_realized_gain_id = account_list[accountset.revaluation_realized_gain.code].id

                    if accountset.revaluation_realized_loss != None and accountset.revaluation_realized_loss.code in account_code_list:
                        accountset.revaluation_realized_loss_id = account_list[accountset.control_account.code].id

                    if accountset.revaluation_unrealized_gain != None and accountset.revaluation_unrealized_gain.code in account_code_list:
                        accountset.revaluation_unrealized_gain_id = account_list[accountset.revaluation_unrealized_gain.code].id

                    if accountset.revaluation_unrealized_loss != None and accountset.revaluation_unrealized_loss.code in account_code_list:
                        accountset.revaluation_unrealized_loss_id = account_list[accountset.revaluation_unrealized_loss.code].id

                    if accountset.revaluation_rounding != None and accountset.revaluation_rounding.code in account_code_list:
                        accountset.revaluation_rounding_id = account_list[accountset.revaluation_rounding.code].id

                    if accountset.discount_account != None and accountset.discount_account.code in account_code_list:
                        accountset.discount_account_id = account_list[accountset.discount_account.code].id

                    if accountset.prepayment_account != None and accountset.prepayment_account.code in account_code_list:
                        accountset.prepayment_account_id = account_list[accountset.prepayment_account.code].id

                    if accountset.writeoff_account != None and accountset.writeoff_account.code in account_code_list:
                        accountset.writeoff_account_id = account_list[accountset.writeoff_account.code].id

                    accountset.save()

                # store account code from bank
                for bank in list_bank:
                    if bank.account != None and bank.account.code in account_list:
                        bank.account_id = account_list[bank.account.code].id

                    bank.save()

                # store account code from reportgroup
                for reportgroup in list_reportgroup:
                    if reportgroup.account_from != None and reportgroup.account_from.code in account_list:
                        reportgroup.account_from_id = account_list[reportgroup.account_from.code].id

                    if reportgroup.account_to != None and reportgroup.account_to.code in account_list:
                        reportgroup.account_to_id = account_list[reportgroup.account_to.code].id

                    reportgroup.save()

                # store account code from tax
                for tax in list_tax:
                    if tax.tax_account_code != None and tax.tax_account_code.code in account_list:
                        tax.tax_account_code_id = account_list[tax.tax_account_code.code].id

                    if tax.tax_authority != None and tax.tax_authority.code in tax_authority_list:
                        tax.tax_authority_id = tax_authority_list[tax.tax_authority.code].id

                    if tax.tax_group != None and tax.tax_group.code in tax_group_list:
                        tax.tax_group_id = tax_group_list[tax.tax_group.code].id

                    tax.save()

                # store account code from taxauthority
                for taxauthority in list_taxauthority:
                    if taxauthority.liability_account != None and taxauthority.liability_account.code in account_list:
                        taxauthority.liability_account_id = account_list[taxauthority.liability_account.code].id

                    if taxauthority.recoverable_account != None and taxauthority.recoverable_account.code in account_list:
                        taxauthority.recoverable_account_id = account_list[taxauthority.recoverable_account.code].id

                    taxauthority.save()

                # store tax code from taxgroup
                for taxgroup in list_taxgroup:
                    if taxgroup.tax_authority != None and taxgroup.tax_authority.code in tax_authority_list:
                        taxgroup.tax_authority_id = tax_authority_list[taxgroup.tax_authority.code].id
                        taxgroup.surtax_authority_id = tax_authority_list[taxgroup.tax_authority.code].id

                    taxgroup.save()

                # store revaluation code from revaluationcode
                for revaluationcode in list_revaluationcode:
                    if revaluationcode.revaluation_unrealized_gain != None and revaluationcode.revaluation_unrealized_gain.code in account_list:
                        revaluationcode.revaluation_unrealized_gain_id = account_list[revaluationcode.revaluation_unrealized_gain.code].id

                    if revaluationcode.revaluation_unrealized_loss != None and revaluationcode.revaluation_unrealized_loss.code in account_list:
                        revaluationcode.revaluation_unrealized_loss_id = account_list[revaluationcode.revaluation_unrealized_loss.code].id

                    revaluationcode.save()

                # store account_type code from account
                for account in list_account:
                    if account.account_group != None and account.account_group.code in account_type_list:
                        account.account_group_id = account_type_list[account.account_group.code].id

                    if account.profit_loss_group != None and account.profit_loss_group.code in account_type_list:
                        account.profit_loss_group_id = account_type_list[account.profit_loss_group.code].id

                    if account.segment_code != None and account.segment_code.code in cost_center_list:
                        account.segment_code_id = cost_center_list[account.segment_code.code].id

                    account.save()

                # Save logo
                file_logo = request.FILES.get('company_logo', False)
                if file_logo:
                    company.logo.delete(False)
                    company.logo.save(file_logo.name, file_logo)
                else:
                    company.logo = ""
                    company.save()

                header_logo = request.FILES.get('header_logo', False)
                if header_logo:
                    company.header_logo.delete(False)
                    company.header_logo.save(header_logo.name, header_logo)
                else:
                    company.header_logo = ""
                    company.save()

                footer_logo = request.FILES.get('footer_logo', False)
                if footer_logo:
                    company.footer_logo.delete(False)
                    company.footer_logo.save(footer_logo.name, footer_logo)
                else:
                    company.footer_logo = ""
                    company.save()

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='company_add')

        return HttpResponseRedirect(reverse('company_list'))
    return render_to_response('company-add.html',
                              RequestContext(request, {'company_list': company_list, 
                                                        'country_list': country_list, 
                                                        'currency_list': currency_list,
                                                        'rate_type': RATE_TYPES,
                                                        'gain_loss_type': REVALUATION_METHODS,}))


def handle_uploaded_file(file_name, f):
    destination = default_storage.open(file_name, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return


def company_change_check(user):
    staff = Staff.objects.filter(is_hidden=0, user_id=user.id).first()
    if not user.has_perm('companies.change_company') and not staff.is_admin:
        return False
    return True


@login_required
@user_passes_test(company_change_check, login_url='/alert/')
def company_edit(request, company_id, is_profile, menu_type):
    company = Company.objects.get(pk=company_id)
    country_list = Country.objects.filter(is_hidden=0)
    currency_list = Currency.objects.filter(is_hidden=0)
    session_date = request.session['session_date']
    fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, start_date__lte=session_date, end_date__gte=session_date).first()
    fsc_years = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0).values_list('fiscal_year', flat=True).order_by('fiscal_year').distinct()
    if company.current_period_month and company.current_period_year:
        fsc_date = datetime.date(int(company.current_period_year), int(company.current_period_month), 1)
        fsc_date = fsc_date.strftime("%d-%m-%Y")
    elif fsc_calendar:
        fsc_year = fsc_calendar.fiscal_year
        fsc_month = fsc_calendar.period
        fsc_date = datetime.date(int(fsc_year), fsc_month, 1)
        fsc_date = fsc_date.strftime("%d-%m-%Y")
    else:
        fsc_date = session_date.strftime("%d-%m-%Y")
    if request.method == 'POST':
        try:
            with transaction.atomic():
                company.id = company_id
                company.name = request.POST.get('name')
                company.company_number = request.POST.get('company_no')
                company.postal_code = request.POST.get('postal_code')
                company.address = request.POST.get('address')
                company.phone = request.POST.get('phone')
                company.email = request.POST.get('email')
                company.web = request.POST.get('web')
                company.fax = request.POST.get('fax')
                if request.POST.get('IsActive'):
                    company.is_active = True
                else:
                    company.is_active = False
                if request.POST.get('useSegment'):
                    company.use_segment = True
                else:
                    company.use_segment = False
                for i in request.session['permission_staff']:
                    if i == 'all_sp':
                        if request.POST.get('IsUseInventnory'):
                            company.is_inventory = True
                            request.session['use_inventory'] = 1
                        else:
                            company.is_inventory = False
                            request.session['use_inventory'] = 0
                company.country_id = request.POST.get('country')
                company.currency_id = request.POST.get('currency')
                company.is_hidden = False
                company.update_by = request.user.id
                if request.POST.get('fiscal'):
                    company.fiscal_period = request.POST.get('fiscal')
                if request.POST.get('current_period_month'):
                    company.current_period_month = request.POST.get('current_period_month')
                if request.POST.get('current_period_year'):
                    company.current_period_year = request.POST.get('current_period_year')
                company.update_date = datetime.datetime.today()
                file_logo = request.FILES.get('company_logo', False)
                header_logo = request.FILES.get('header_logo', False)
                footer_logo = request.FILES.get('footer_logo', False)
                if file_logo:
                    company.logo.delete(False)
                    company.logo.save(file_logo.name, file_logo)
                if header_logo:
                    company.header_logo.delete(False)
                    company.header_logo.save(header_logo.name, header_logo)
                if footer_logo:
                    company.footer_logo.delete(False)
                    company.footer_logo.save(footer_logo.name, footer_logo)
                if request.POST.get('rm_logo'):
                    company.logo = ''
                if request.POST.get('rm_header_logo'):
                    company.header_logo = ''
                if request.POST.get('rm_footer_logo'):
                    company.footer_logo = ''
                if request.POST.get('remit_remark'):
                    company.remit_remark = request.POST.get('remit_remark')
                if request.POST.get('rate_type'):
                    company.rate_type = request.POST.get('rate_type')
                if request.POST.get('gain_loss_type'):
                    company.gain_loss_type = request.POST.get('gain_loss_type')
                if request.POST.get('fiscal_period_number'):
                    company.fiscal_period_number = request.POST.get('fiscal_period_number')
                if not company.is_multicurrency:
                    if request.POST.get('multicurrency-checkbox'):
                        company.is_multicurrency = True
                    else:
                        company.is_multicurrency = False
                company.save()

        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='company_edit')
        if is_profile == 'true':
            return HttpResponseRedirect(reverse('control_file'))
        else:
            return HttpResponseRedirect(reverse('company_list'))
    return render_to_response('company-edit.html', RequestContext(request, {'company': company,
                                                                            'fsc_date': fsc_date,
                                                                            'fsc_years': fsc_years,
                                                                            'country_list': country_list,
                                                                            'currency_list': currency_list,
                                                                            'media_url': s.MEDIA_URL,
                                                                            'is_profile': is_profile,
                                                                            'menu_type': menu_type,
                                                                            'rate_type': RATE_TYPES,
                                                                            'gain_loss_type': REVALUATION_METHODS,}))


@login_required
@permission_required('companies.delete_company', login_url='/alert/')
def company_delete(request, company_id):
    if request.method == 'POST':
        try:
            company = Company.objects.get(pk=company_id)
            company.is_active = False
            company.is_hidden = True
            company.save()
            return HttpResponseRedirect(reverse('company_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='company_delete')


@login_required
def cost_centers_list(request):
    return render_to_response('cost-centers-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Global']}))


@login_required
def cost_centers(request):
    return render_to_response('cost-centers-list.html',
                              RequestContext(request, {'menu_type': TRN_CODE_TYPE_DICT['Sales Number File']}))


@login_required
@permission_required('companies.add_costcenters', login_url='/alert/')
def cost_centers_add(request, menu_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if request.method == 'POST':
        form = CostCentersForm(request.POST)
        if form.is_valid():
            try:
                costcenters = form.save(commit=False)
                costcenters.company_id = company.id
                costcenters.is_active = True
                costcenters.create_date = datetime.datetime.today()
                costcenters.update_date = datetime.datetime.today()
                costcenters.update_by = request.user.id
                costcenters.is_hidden = 0
                costcenters.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='cost_centers')
            return HttpResponsePermanentRedirect(reverse('cost_centers'))
        else:
            form = CostCentersForm(request.POST)
    else:
        form = CostCentersForm()
    return render(request, 'cost-centers.html', {'form': form, 'menu_type': menu_type})


@login_required
@permission_required('companies.change_costcenters', login_url='/alert/')
def cost_centers_edit(request, cost_id, menu_type):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    costcenters = CostCenters.objects.get(pk=cost_id)
    post = get_object_or_404(CostCenters, pk=cost_id)
    if request.method == 'POST':
        form = CostCentersForm(request.POST, instance=post)
        if form.is_valid():
            try:
                costcenters = form.save(commit=False)
                costcenters.company_id = company.id
                costcenters.is_active = True
                costcenters.create_date = datetime.datetime.today()
                costcenters.update_date = datetime.datetime.today()
                costcenters.update_by = request.user.id
                costcenters.is_hidden = 0
                costcenters.save()
            except OSError as e:
                messages.add_message(request, messages.ERROR, e, extra_tags='cost_centers_edit')
            return HttpResponsePermanentRedirect(reverse('cost_centers'))
    post.update_date = post.update_date.strftime("%d-%m-%Y")
    form = CostCentersForm(instance=post)
    return render(request, 'cost-centers.html', {'form': form, 'costcenters': costcenters, 'menu_type': menu_type})


@login_required
@permission_required('companies.delete_costcenters', login_url='/alert/')
def cost_centers_delete(request, cost_id):
    if request.method == 'POST':
        try:
            costcenters = CostCenters.objects.get(pk=cost_id)
            costcenters.is_active = False
            costcenters.is_hidden = True
            costcenters.save()
            return HttpResponsePermanentRedirect(reverse('cost_centers'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='cost_centers_delete')


@login_required
def CostCenter__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    list_filter = CostCenters.objects.filter(is_hidden=0, is_active=1, company_id=company_id).order_by('id')
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(update_date__contains=search)
                                         | Q(name__contains=search)
                                         | Q(code__contains=search)
                                         | Q(postal_code__contains=search)
                                         | Q(address__contains=search)
                                         | Q(email__contains=search)
                                         | Q(phone__contains=search)
                                         )

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "2":
        column_name = "name"
    elif order_column == "1":
        column_name = "code"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%d-%m-%Y"),
                "name": field.name,
                "code": field.code, "is_active": str(field.is_active)}
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def CompanyList__asJson(request):
    draw = request.GET['draw']
    start = request.GET['start']
    length = request.GET['length']
    search = request.GET['search[value]']
    list_filter = Company.objects.filter(is_hidden=0, is_active=1).order_by('id')
    records_total = list_filter.count()

    if search:  # Filter data base on search
        list_filter = list_filter.filter(Q(update_date__contains=search)
                                         | Q(name__contains=search)
                                         | Q(company_number__contains=search)
                                         | Q(country__name__contains=search)
                                         | Q(address__contains=search)
                                         | Q(currency__code__contains=search))

    # All data
    records_filtered = list_filter.count()

    # Order by list_limit base on order_dir and order_column
    order_column = request.GET['order[0][column]']
    if order_column == "0":
        column_name = "update_date"
    elif order_column == "1":
        column_name = "name"
    elif order_column == "2":
        column_name = "company_number"
    elif order_column == "3":
        column_name = "country__name"
    elif order_column == "4":
        column_name = "currency__code"
    elif order_column == "5":
        column_name = "address"
    order_dir = request.GET['order[0][dir]']
    if order_dir == "asc":
        list = list_filter.order_by(column_name)[int(start):(int(start) + int(length))]
    if order_dir == "desc":
        list = list_filter.order_by('-' + column_name)[int(start):(int(start) + int(length))]

    # Create data list
    array = []
    for field in list:
        data = {"id": field.id,
                "update_date": field.update_date.strftime("%Y-%m-%d"),
                "name": field.name,
                "number": str(field.company_number),
                "country_name": field.country.name if field.country else '',
                "currency__code": field.currency.code if field.currency else '',
                "address": field.address,
                "is_active": str(field.is_active)}
        array.append(data)

    content = {
        "draw": draw,
        "data": array,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered
    }

    json_content = json.dumps(content, ensure_ascii=False)
    return HttpResponse(json_content, content_type='application/json')


@login_required
def segment_list(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if company.use_segment:
        segment_list = CostCenters.objects.filter(company_id=company.id, is_hidden=False)
    else:
        segment_list = None
        company = None

    return render(request, 'segment-list.html', {'segment_list': segment_list, 'company': company})


@login_required
def segment_add(request):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    company = Company.objects.get(pk=company_id)
    if request.method == 'POST':
        form = SegmentForm(company_id, request.POST)
        if form.is_valid():
            try:
                segment = form.save(commit=False)
                segment.company_id = company_id
                segment.create_date = datetime.datetime.today()
                segment.update_date = datetime.datetime.today()
                segment.update_by = request.user.id
                segment.is_active = True
                segment.is_hidden = False
                segment.save()
            except OSError as e:
                messages.add_message(
                    request, messages.ERROR, e, extra_tags='segment_add')
            return HttpResponsePermanentRedirect(reverse('segment_list'))
        else:
            form = SegmentForm(company_id, request.POST)
    else:
        form = SegmentForm(company_id)
    return render(request, 'segment-form.html', {'form': form})


@login_required
# @user_passes_test(company_change_check, login_url='/alert/')
def segment_edit(request, segment_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    segment = CostCenters.objects.get(pk=segment_id)
    post = get_object_or_404(CostCenters, pk=segment_id)
    if request.method == 'POST':
        form = SegmentForm(company_id, request.POST, instance=post)
        if form.is_valid():
            try:
                t_segment = form.save(commit=False)
                t_segment.company_id = company_id
                t_segment.create_date = datetime.datetime.today()
                t_segment.update_date = datetime.datetime.today()
                t_segment.update_by = request.user.id
                t_segment.is_active = True
                t_segment.is_hidden = False
                t_segment.save()
            except OSError as e:
                messages.add_message(
                    request, messages.ERROR, e, extra_tags='segment_edit')
            return HttpResponsePermanentRedirect(reverse('segment_list'))
    post.update_date = post.update_date.strftime("%d-%m-%Y")
    form = SegmentForm(company_id, instance=post)
    return render(request, 'segment-form.html', {'form': form, 'segment': segment})


@login_required
def segment_delete(request, segment_id):
    company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
    if request.method == 'POST':
        try:
            segment = CostCenters.objects.get(pk=segment_id)
            segment.is_active = False
            segment.is_hidden = True
            segment.save()
            return HttpResponseRedirect(reverse('segment_list'))
        except OSError as e:
            messages.add_message(request, messages.ERROR, e, extra_tags='segment_delete')

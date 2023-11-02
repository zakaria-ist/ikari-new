import math
from copy import deepcopy
from datetime import datetime
from django.db.models import Sum, Q
from decimal import Decimal
from accounting.models import Journal, Batch, RevaluationLogs, RevaluationDetails, FiscalCalendar
from accounts.models import Account, AccountSet
from companies.models import Company
from transactions.models import Transaction
from utilities.common import generate_batch_number, round_number, add_one_month
from utilities.constants import SOURCE_LEDGER_DICT, STATUS_TYPE_DICT, TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, \
    INPUT_TYPE_DICT, BALANCE_TYPE_DICT
from utilities.messages import RV_ERR_NO_CURRENCY, RV_ERR_NO_RV_ACCOUNT2, \
    RV_ERR_NO_RV_ACCOUNT3, RV_ERR_NO_POSTED_JOURNAL, RV_ERR_CREATE_BATCH, RV_ERR_CREATE_LOG, \
    RV_SUCCESS, RV_SUCCESS2, RV_FAILED, RV_FAILED2, RV_CORRUPT_TRX, RV_ERR_NO_ACCOUNT_SET, RV_ERR_NO_CONTROL_ACCOUNT


class C_Revaluation_ver3:
    request = None
    data = None
    batch_type = dict(TRANSACTION_TYPES)['Undefined']
    d_company = None
    company_id = None
    CurrencySets = None

    def __init__(self, request, type_transaction):
        self.data = {'journal': [], 'batch': None}
        self.company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.d_company = Company.objects.get(pk=self.company_id)
        self.request = request
        self.batch_type = (dict(TRANSACTION_TYPES)['AP Invoice'], dict(TRANSACTION_TYPES)['AR Invoice'])[
            type_transaction == 'AR']
        self.CurrencySets = []

        journal_type = (dict(TRANSACTION_TYPES)['AP Invoice'], dict(TRANSACTION_TYPES)['AR Invoice'])[type_transaction == 'AR']
        try:
            last_revaluation = RevaluationLogs.objects.filter(is_hidden=0, company_id=self.company_id, journal_type=journal_type) \
                .exclude(posting_sequence='0') \
                .order_by('-revaluation_date', '-id') \
                .first()
            self.new_posting_sequence = int(last_revaluation.posting_sequence) + 1
        except:
            self.new_posting_sequence = 1

        self.last_revals = []

    def GenerateRevaluation(self, rv_curr_lists, rev_date):
        result = self.createCurrLists(rv_curr_lists)

        if result[0]:
            result = self.getOpenJournals(rev_date)

            if result[0]:
                result = self.createBatch(rev_date)

                if result[0]:
                    result = self.createEntries(rev_date)

        return result

    def createCurrLists(self, rv_curr_lists):
        result = False
        status = RV_FAILED + RV_ERR_NO_CURRENCY
        if len(rv_curr_lists) > 0:
            for rv_curr_list in rv_curr_lists:
                self.CurrencySets.append(rv_curr_list)
            result = True
            status = None
        return [result, status]

    def getOpenJournals(self, rev_date):
        result = False
        status = ''
        j_entries = None
        # date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d") + timedelta(days=1)

        revaluation_date_obj = datetime.strptime(rev_date, "%Y-%m-%d")
        revaluation_date = rev_date.split('-')

        # rev_org = Revaluation_count.objects.filter(company_id=self.company_id,
        #                                            year_rev=revaluation_date[0],
        #                                            period_rev=revaluation_date[1],
        #                                            code=self.batch_type).last()

        # check if any revaluation exixts in same month
        last_reval_docs = []
        rev_curr = []
        for CurrencySet in self.CurrencySets:
            rev_curr.append(int(CurrencySet['curr_id']))
            last_revals = RevaluationLogs.objects.filter(is_hidden=False, company_id=self.company_id,
                                                         journal_type=self.batch_type,
                                                         revaluation_date__month=revaluation_date[1],
                                                         revaluation_date__year=revaluation_date[0],
                                                         currency_id=int(CurrencySet['curr_id'])) \
                .exclude(posting_sequence='0') \
                .order_by('id')

            for last_reval in last_revals:
                self.last_revals.append({
                    'id': last_reval.id,
                    'curr_id': int(CurrencySet['curr_id'])
                })

                last_reval_detailss = RevaluationDetails.objects.filter(posting_id=last_reval.id, is_hidden=False)

                for detail in last_reval_detailss:
                    if detail.document_no in last_reval_docs:
                        if detail.source_amount == 0:
                            last_reval_docs.remove(detail.document_no)
                    else:
                        last_reval_docs.append(detail.document_no)
        if len(self.last_revals):
            # sort last reval entries in reverse order
            self.last_revals.sort(key=lambda r: (r['id']), reverse=True)

        if int(revaluation_date[1]) == 1:
            revaluation_date[1] = 13

        if self.batch_type == dict(TRANSACTION_TYPES)['AP Invoice']:
            if len(last_reval_docs):
                j_entries = Journal.objects.filter(Q(company_id=self.company_id, is_hidden=False,
                                                   batch__is_hidden=False,
                                                   status=int(STATUS_TYPE_DICT['Posted']),
                                                   batch__batch_type=self.batch_type,
                                                   batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                   document_number__in=last_reval_docs)
                                                   |
                                                   Q(company_id=self.company_id, is_hidden=False,
                                                   batch__is_hidden=False,
                                                   currency_id__in=rev_curr,
                                                   status=int(STATUS_TYPE_DICT['Posted']),
                                                   batch__batch_type=self.batch_type,
                                                   batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                   document_date__lte=revaluation_date_obj)) \
                    .exclude(reverse_reconciliation=True)\
                    .exclude(error_entry__gt=0)\
                    .exclude(journal_type=dict(TRANSACTION_TYPES)['AD'])\
                    .order_by('supplier__code', 'document_number')\
                    .select_related('batch')
            else:
                j_entries = Journal.objects.filter(company_id=self.company_id, is_hidden=False,
                                                   batch__is_hidden=False,
                                                   currency_id__in=rev_curr,
                                                   status=int(STATUS_TYPE_DICT['Posted']),
                                                   batch__batch_type=self.batch_type,
                                                   batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                   document_date__lte=revaluation_date_obj) \
                    .exclude(reverse_reconciliation=True)\
                    .exclude(error_entry__gt=0)\
                    .exclude(journal_type=dict(TRANSACTION_TYPES)['AD'])\
                    .order_by('supplier__code', 'document_number')\
                    .select_related('batch')
        else:
            if len(last_reval_docs):
                j_entries = Journal.objects.filter(Q(company_id=self.company_id, is_hidden=False,
                                                   batch__is_hidden=False,
                                                   status=int(STATUS_TYPE_DICT['Posted']),
                                                   batch__batch_type=self.batch_type,
                                                   batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                   document_number__in=last_reval_docs)
                                                   |
                                                   Q(company_id=self.company_id, is_hidden=False,
                                                     batch__is_hidden=False,
                                                     currency_id__in=rev_curr,
                                                     batch__batch_type=self.batch_type,
                                                     batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                     status=int(STATUS_TYPE_DICT['Posted']),
                                                     document_date__lte=revaluation_date_obj)
                                                   |
                                                   Q(company_id=self.company_id, is_hidden=False,
                                                     batch__is_hidden=False,
                                                     original_currency_id__in=rev_curr,
                                                     status=int(STATUS_TYPE_DICT['Posted']),
                                                     batch__batch_type=dict(TRANSACTION_TYPES)['AR Receipt'],
                                                     batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                     # document_date__month=revaluation_date_obj.month,
                                                     # document_date__year=revaluation_date_obj.year,
                                                     document_date__lte=revaluation_date_obj,
                                                     customer_unapplied__gt=0)) \
                    .exclude(reverse_reconciliation=True)\
                    .exclude(error_entry__gt=0)\
                    .exclude(journal_type=dict(TRANSACTION_TYPES)['AD'])\
                    .order_by('customer__code', 'document_number')\
                    .select_related('batch')
            else:
                j_entries = Journal.objects.filter(Q(company_id=self.company_id, is_hidden=False,
                                                     batch__is_hidden=False,
                                                     currency_id__in=rev_curr,
                                                     batch__batch_type=self.batch_type,
                                                     batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                     status=int(STATUS_TYPE_DICT['Posted']),
                                                     document_date__lte=revaluation_date_obj)
                                                   |
                                                   Q(company_id=self.company_id, is_hidden=False,
                                                     batch__is_hidden=False,
                                                     original_currency_id__in=rev_curr,
                                                     status=int(STATUS_TYPE_DICT['Posted']),
                                                     batch__batch_type=dict(TRANSACTION_TYPES)['AR Receipt'],
                                                     batch__status=int(STATUS_TYPE_DICT['Posted']),
                                                     # document_date__month=revaluation_date_obj.month,
                                                     # document_date__year=revaluation_date_obj.year,
                                                     document_date__lte=revaluation_date_obj,
                                                     customer_unapplied__gt=0)) \
                    .exclude(reverse_reconciliation=True)\
                    .exclude(error_entry__gt=0)\
                    .exclude(journal_type=dict(TRANSACTION_TYPES)['AD'])\
                    .order_by('customer__code', 'document_number')\
                    .select_related('batch')

        if int(revaluation_date[1]) == 13:
            revaluation_date[1] = 1

        # j_entries = j_entries.filter(
            # Q(is_fully_paid=False) | Q(is_fully_paid=True, fully_paid_date__month__gte=revaluation_date_obj.month,
            #                             fully_paid_date__year=revaluation_date_obj.year))
        j_entries = j_entries.filter(Q(fully_paid_date__isnull=True) | Q(fully_paid_date__month__gte=revaluation_date_obj.month,
                                            fully_paid_date__year=revaluation_date_obj.year)).exclude(real_outstanding=0)
        
        if j_entries.exists():

            for j_entry in j_entries:
                receipt_amount = self.getReceiptAmount(j_entry, self.batch_type)
                cn_dn_amount = self.getCnDnAmount(j_entry, self.batch_type)
                if float(j_entry.total_amount) != float(math.fabs(receipt_amount)):  # handle apllied amount (- value)
                    if float(j_entry.total_amount) != float(cn_dn_amount):
                        j_entry.is_rev_do = True
                        j_entry.is_fully_paid = False
                        j_entry.rev_perd_month = revaluation_date[1]
                        j_entry.rev_perd_year = revaluation_date[0]
                        j_entry.save()

                        # if j_entry.journal_type != dict(TRANSACTION_TYPES)['AR Receipt']:
                        #     amout_rev = float(j_entry.total_amount) - float(receipt_amount) - float(cn_dn_amount)
                        # else:
                        #     amout_rev = float(receipt_amount) - float(j_entry.customer_unapplied)
                        cut_date = self.request.session['session_date'].strftime(("%Y-%m-%d"))
                        amout_rev = j_entry.has_outstanding(cut_date)[1]
                        # if j_entry.id in [273, 985]:
                        #     print(j_entry.document_number, j_entry.total_amount,
                        #         receipt_amount, cn_dn_amount, amout_rev)
                        ErrorStatus = self.CheckAccountSet(j_entry)
                        # transaction = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                        #                                          journal__batch__related_batch_id=j_entry.batch_id,
                        #                                          tax_id=None).first()
                        # if transaction:
                        self.data['journal'].append(
                            {'entry': j_entry, 'transaction': '', 'status': ErrorStatus,
                                'amout_rev': amout_rev})

                    else:
                        j_entry.is_fully_paid = True
                        j_entry.save()
                        ErrorStatus = self.CheckAccountSet(j_entry)
                        self.data['journal'].append(
                            {'entry': j_entry, 'transaction': '', 'status': ErrorStatus,
                                'amout_rev': 0})

                else:
                    j_entry.is_fully_paid = True
                    j_entry.save()
                    ErrorStatus = self.CheckAccountSet(j_entry)
                    self.data['journal'].append(
                        {'entry': j_entry, 'transaction': '', 'status': ErrorStatus,
                            'amout_rev': 0})

            if len(self.data['journal']) > 0:
                result = True
            else:
                status = RV_FAILED + RV_CORRUPT_TRX
        else:
            status = RV_FAILED + RV_ERR_NO_POSTED_JOURNAL

        return [result, status]

    def getCnDnAmount(self, invoice_source, batch_type):
        receipt_amount = 0

        if invoice_source.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
            related_cn_dn = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                                                       journal_id=invoice_source.id).last()

            if related_cn_dn.related_invoice_id is None:
                id_related_cn_dn = invoice_source.id
            else:
                id_related_cn_dn = related_cn_dn.related_invoice_id
        else:
            id_related_cn_dn = invoice_source.id

        try:
            ARReceipt = Transaction.objects.select_related('journal').filter(company_id=self.company_id, is_hidden=False,
                                                                             journal__is_hidden=False,
                                                                             related_invoice_id=id_related_cn_dn,
                                                                             journal__journal_type=batch_type,
                                                                             journal__status=int(STATUS_TYPE_DICT['Posted'])). \
                aggregate(trx_amount=Sum('total_amount'))

            if ARReceipt.get('trx_amount'):
                receipt_amount = ARReceipt.get('trx_amount')

        except Exception as e:
            pass

        return receipt_amount

    def getReceiptAmount(self, invoice_source, batch_type):
        journal_type = (dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AP Payment'])[
            batch_type == dict(TRANSACTION_TYPES)['AP Invoice']]

        receipt_amount = 0

        try:
            # if invoice_source.journal_type != dict(TRANSACTION_TYPES)['AR Receipt']:
            Receipts = Transaction.objects.select_related('journal').filter(company_id=self.company_id, is_hidden=False,
                                                                            journal__is_hidden=False,
                                                                            related_invoice_id=invoice_source.id,
                                                                            journal__journal_type=journal_type,
                                                                            journal__status=int(STATUS_TYPE_DICT['Posted']))

            if Receipts:
                Receipt = Receipts.aggregate(trx_amount=Sum('total_amount'))
                if Receipt.get('trx_amount'):
                    receipt_amount = Receipt.get('trx_amount')
                if invoice_source.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                    invoice_source.paid_amount = receipt_amount
                    invoice_source.fully_paid_date = Receipts.last().transaction_date
                    invoice_source.save()

        except Exception as e:
            pass

        return receipt_amount

    def CheckAccountSet(self, journal):
        status = RV_ERR_NO_ACCOUNT_SET

        if journal.account_set:
            status = RV_ERR_NO_CONTROL_ACCOUNT

            if journal.account_set.control_account:
                status = RV_ERR_NO_RV_ACCOUNT2

                if journal.account_set.revaluation_unrealized_gain:
                    status = RV_ERR_NO_RV_ACCOUNT3
                    revAccount = Account.objects.filter(company_id=self.company_id, is_hidden=False, is_active=True,
                                                        pk=journal.account_set.revaluation_unrealized_gain_id).first()
                    if revAccount:
                        status = None

                if journal.account_set.revaluation_unrealized_loss:
                    status = RV_ERR_NO_RV_ACCOUNT3
                    revAccount = Account.objects.filter(company_id=self.company_id, is_hidden=False, is_active=True,
                                                        pk=journal.account_set.revaluation_unrealized_loss_id).first()
                    if revAccount:
                        status = None

                if journal.account_set.revaluation_realized_gain:
                    status = RV_ERR_NO_RV_ACCOUNT3
                    revAccount = Account.objects.filter(company_id=self.company_id, is_hidden=False, is_active=True,
                                                        pk=journal.account_set.revaluation_realized_gain_id).first()
                    if revAccount:
                        status = None

                if journal.account_set.revaluation_realized_loss:
                    status = RV_ERR_NO_RV_ACCOUNT3
                    revAccount = Account.objects.filter(company_id=self.company_id, is_hidden=False, is_active=True,
                                                        pk=journal.account_set.revaluation_realized_loss_id).first()
                    if revAccount:
                        status = None

                if journal.account_set.revaluation_rounding:
                    status = RV_ERR_NO_RV_ACCOUNT3
                    revAccount = Account.objects.filter(company_id=self.company_id, is_hidden=False, is_active=True,
                                                        pk=journal.account_set.revaluation_rounding_id).first()
                    if revAccount:
                        status = None
        return status

    def createRevaluationLog(self, CurrencySet):
        status = ''
        try:
            new_log = RevaluationLogs()
            new_log.journal_type = self.batch_type
            new_log.revaluation_date = CurrencySet['rev_date']
            new_log.rate_date = CurrencySet['rate_date']
            new_log.exchange_rate = float(CurrencySet['rate'])
            new_log.currency_id = int(CurrencySet['curr_id'])
            new_log.company_id = self.d_company.id
            new_log.rate_type = 'SR'
            new_log.posting_sequence = self.new_posting_sequence
            new_log.posting_date = CurrencySet['rev_date']
            new_log.revaluation_method = 1
            new_log.is_hidden = False
            new_log.update_by = self.request.user.id
            new_log.save()
        except Exception as e:
            new_log = None
            status = RV_FAILED + RV_ERR_CREATE_LOG

        return new_log, status

    def createBatch(self, rev_date):
        result = False
        status = None

        try:
            rev_date_ = datetime.strptime(rev_date, '%Y-%m-%d')
            rv_batch = Batch()
            rv_batch.description = 'Generated from revaluation ' + \
                                   ('AP', 'AR')[self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']] + ' ' + \
                                   str(rev_date_.day) + '/' + str(rev_date_.month) + '/' + str(rev_date_.year)
            rv_batch.update_by = self.request.user.id
            rv_batch.batch_no = generate_batch_number(self.company_id, dict(TRANSACTION_TYPES)['GL'])
            rv_batch.batch_amount = 0
            rv_batch.no_entries = 0
            rv_batch.currency_id = self.d_company.currency_id
            rv_batch.status = int(STATUS_TYPE_DICT['Open'])
            rv_batch.company_id = self.company_id
            rv_batch.input_type = INPUT_TYPE_DICT['Generated']
            rv_batch.document_type = DOCUMENT_TYPE_DICT['Undefined']  # investigate later
            rv_batch.batch_type = dict(TRANSACTION_TYPES)['GL']  # gl batch type
            rv_batch.source_ledger = (SOURCE_LEDGER_DICT['Account Payable'],
                                      SOURCE_LEDGER_DICT['Account Receivable'])[
                self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']]
            rv_batch.is_hidden = False
            rv_batch.batch_date = rev_date
            rv_batch.save()
            self.data['batch'] = rv_batch
            result = True
        except Exception as e:
            status = RV_FAILED + RV_ERR_CREATE_BATCH
        return [result, status]

    def createEntries(self, rev_date):
        status = ''
        total_amount_batch = 0
        entries = []
        e_counter = 0
        new_reval_log = ''
        for CurrencySet in self.CurrencySets:
            new_reval_log, status = self.createRevaluationLog(CurrencySet)
            for i, d in enumerate(self.data['journal']):
                if (d['entry'].currency_id == int(CurrencySet['curr_id'])) or \
                        (d['entry'].journal_type == dict(TRANSACTION_TYPES)['AR Receipt'] and d['entry'].original_currency_id == int(CurrencySet['curr_id'])):
                    try:
                        f_amount = self.getFunctionalAmount(d['entry'], CurrencySet, d['amout_rev'])
                        # if d['entry'].id in [273, 985]:
                        #     print('f_amount', f_amount)
                        if (f_amount and float(round_number(f_amount[0], 2)) != 0.00):
                            if not self.d_company.currency.is_decimal:
                                f_amount[0] = float(round_number(f_amount[0]), 0)
                            new_entry = deepcopy(d['entry'])
                            new_entry.pk = None
                            new_entry.status = int(STATUS_TYPE_DICT['Open'])
                            new_entry.journal_type = dict(TRANSACTION_TYPES)['GL']
                            new_entry.document_type = 0
                            new_entry.document_number = \
                                ('AP', 'AR')[self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']] + \
                                '-RV-' + \
                                str((e_counter + 1))
                            new_entry.name = 'RV-' + str(self.new_posting_sequence)
                            new_entry.amount = round_number(math.fabs(f_amount[0]))
                            new_entry.total_amount = round_number(math.fabs(f_amount[0]))
                            new_entry.document_amount = round_number(math.fabs(f_amount[0]))
                            new_entry.original_amount = round_number(math.fabs(f_amount[0]))
                            new_entry.payment_amount = 0.000000
                            new_entry.tax_amount = 0.000000
                            new_entry.discount_amount = 0.000000
                            new_entry.adjustment_amount = 0.000000
                            new_entry.exchange_rate = float(CurrencySet['rate'])
                            new_entry.orig_exch_rate = float(CurrencySet['rate'])

                            if CurrencySet['exchrateid'] != '' and int(CurrencySet['exchrateid']) > 0:
                                new_entry.exchange_rate_fk_id = int(CurrencySet['exchrateid'])
                            else:
                                new_entry.exchange_rate_fk_id = None

                            new_entry.batch = self.data['batch']
                            new_entry.source_type = (
                                ('AP-GL', 'AR-GL')[self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']])
                            new_entry.posting_date = rev_date
                            new_entry.reference = d['entry'].document_number
                            new_entry.document_date = rev_date
                            new_entry.code = '0000' + str(e_counter + 1)
                            new_entry.is_manual_doc = False
                            new_entry.is_rev_do = True
                            new_entry.is_auto_reverse = True
                            new_entry.is_reversed_entry = False
                            new_entry.is_auto_reverse_entry = True
                            new_entry.flag = 0
                            new_entry.reverse_to_period = 1

                            rev_split = rev_date.split('-')
                            rev_yy = int(rev_split[0])
                            rev_mm = int(rev_split[1])

                            fsc_calendar = FiscalCalendar.objects.filter(company_id=self.company_id, is_hidden=0,
                                                                            start_date__lte=rev_date,
                                                                            end_date__gte=rev_date).first()
                            if fsc_calendar:
                                rev_yy = int(fsc_calendar.fiscal_year)
                                rev_mm = int(fsc_calendar.period)

                            reverse_to_period = add_one_month(datetime.strptime(rev_date, "%Y-%m-%d"))

                            new_entry.reverse_to_period_val = str(reverse_to_period.year) + '-' + str(reverse_to_period.month) + '-01'
                            new_entry.perd_month = rev_mm
                            new_entry.perd_year = rev_yy
                            new_entry.rev_perd_month = rev_mm
                            new_entry.rev_perd_year = rev_yy
                            new_entry.is_hidden = False
                            new_entry.save()

                            is_realized = False

                            if new_entry.pk:
                                # add revaluation detail
                                # if d['entry'].journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                                #     d['amout_rev'] = d['amout_rev'] * -1
                                rv_detail = RevaluationDetails()
                                rv_detail.posting = new_reval_log
                                rv_detail.document_no = d['entry'].document_number
                                rv_detail.document_date = d['entry'].document_date
                                rv_detail.due_date = d['entry'].due_date
                                rv_detail.source_amount = d['amout_rev']
                                rv_detail.prior_rate = d['entry'].exchange_rate
                                rv_detail.rev_rate = float(CurrencySet['rate'])
                                rv_detail.customer = d['entry'].customer
                                rv_detail.supplier = d['entry'].supplier
                                if self.d_company.currency.is_decimal:
                                    if d['amout_rev'] == 0:
                                        rv_detail.new_functional = round_number(d['amout_rev'])
                                        if f_amount[1] == 0:
                                            rv_detail.prior_functional = round_number(f_amount[0])
                                        else:
                                            rv_detail.prior_functional = round_number(-1 * f_amount[0])
                                    else:
                                        if d['entry'].exchange_rate and float(d['entry'].exchange_rate) == float(CurrencySet['rate']):
                                            rv_detail.new_functional = round_number(Decimal(d['amout_rev']) * Decimal(CurrencySet['rate']))
                                            rv_detail.prior_functional = round_number(Decimal(d['amout_rev']) * Decimal(d['entry'].exchange_rate)) - round_number(f_amount[0])
                                        else:
                                            rv_detail.new_functional = round_number(Decimal(d['amout_rev']) * Decimal(CurrencySet['rate']))
                                            rv_detail.prior_functional = round_number(Decimal(d['amout_rev']) * Decimal(d['entry'].exchange_rate))
                                else:
                                    if d['amout_rev'] == 0:
                                        rv_detail.new_functional = round_number(d['amout_rev'], 0)
                                        if f_amount[1] == 0:
                                            rv_detail.prior_functional = round_number(f_amount[0], 0)
                                        else:
                                            rv_detail.prior_functional = round_number(-1 * f_amount[0], 0)
                                    else:
                                        if d['entry'].exchange_rate and float(d['entry'].exchange_rate) == float(CurrencySet['rate']):
                                            rv_detail.new_functional = round_number(Decimal(d['amout_rev']) * Decimal(CurrencySet['rate']), 0)
                                            rv_detail.prior_functional = round_number(Decimal(d['amout_rev']) * Decimal(d['entry'].exchange_rate) - round_number(f_amount[0]), 0)
                                        else:
                                            rv_detail.new_functional = round_number(Decimal(d['amout_rev']) * Decimal(CurrencySet['rate']), 0)
                                            rv_detail.prior_functional = round_number(Decimal(d['amout_rev']) * Decimal(d['entry'].exchange_rate), 0)

                                if self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                                    gain_loss = round_number(rv_detail.new_functional - rv_detail.prior_functional)
                                    if gain_loss > 0:
                                        is_gain = True
                                    else:
                                        is_gain = False
                                    rv_detail.gain_loss = gain_loss
                                else:
                                    gain_loss = round_number(rv_detail.prior_functional - rv_detail.new_functional)
                                    if gain_loss > 0:
                                        is_gain = True
                                    else:
                                        is_gain = False
                                    rv_detail.gain_loss = gain_loss

                                rv_detail.is_hidden = False
                                rv_detail.update_by = self.request.user.id
                                rv_detail.save()

                                new_entry.amount = math.fabs(gain_loss)
                                new_entry.total_amount = math.fabs(gain_loss)
                                new_entry.document_amount = math.fabs(gain_loss)
                                new_entry.original_amount = math.fabs(gain_loss)
                                new_entry.save()

                                if self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                                    if rv_detail.gain_loss > 0:
                                        is_gain = True
                                    else:
                                        is_gain = False
                                else:
                                    if rv_detail.gain_loss < 0:
                                        is_gain = True
                                    else:
                                        is_gain = False
                                # if d['entry'].journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                                #     is_gain = not is_gain
                                if math.fabs(gain_loss) == 0:
                                    new_entry.is_hidden = True
                                    new_entry.save()
                                    entry_info = {}
                                    entry_info['status'] = False
                                    entry_info['text'] = RV_FAILED2 % (
                                        d['entry'].document_number, CurrencySet['curr_code'])
                                    entries.append(entry_info)
                                else:
                                    total_amount_batch += new_entry.total_amount
                                    e_counter += 1
                                    entry_info = {}
                                    entry_info['status'] = True
                                    entry_info['text'] = RV_SUCCESS2 % (
                                        d['entry'].document_number, CurrencySet['curr_code'])
                                    entries.append(entry_info)
                                    self.createTransactions(new_entry, d['transaction'], gain_loss, rev_date,
                                                            CurrencySet['rate_date'], is_realized, is_gain)
                            else:
                                entry_info = {}
                                entry_info['status'] = False
                                entry_info['text'] = RV_FAILED2 % (d['entry'].document_number, CurrencySet['curr_code'])
                                entries.append(entry_info)

                    except Exception as e:
                        print(e)
                        entry_info = {}
                        entry_info['status'] = False
                        entry_info['text'] = RV_FAILED2 % (d['entry'].document_number, CurrencySet['curr_code'])
                        entries.append(entry_info)
            # checking if any posting jounal created or not
            new_rev_detail = RevaluationDetails.objects.filter(posting_id=new_reval_log.id).first()
            if not new_rev_detail:
                new_reval_log.posting_sequence = '0'
                new_reval_log.save()
                entry_info = {}
                entry_info['status'] = False
                entry_info['text'] = 'There is nothing to update for currency ' + str(CurrencySet['curr_code'])
                entries.append(entry_info)

        self.data['batch'].batch_amount = total_amount_batch
        self.data['batch'].no_entries = e_counter

        if e_counter == 0:
            self.data['batch'].is_hidden = True

        self.data['batch'].save()

        if self.data['batch'].id and e_counter > 0:
            status = RV_SUCCESS % (self.data['batch'].batch_no)

        for entry in entries:
            if entry['status']:
                status += '<br \>' + entry['text']
            else:
                status += '<br \><span style="color:#F20707">' + entry['text'] + '</span>'
        entries = None

        return [True, status]

    def createTransactions(self, newEntry, oldTransaction, gain_loss, rev_date, rate_date, is_realized=False, is_gain=False):
        acc = AccountSet.objects.filter(pk=newEntry.account_set_id).values('control_account_id',
                                                                           'revaluation_unrealized_gain_id',
                                                                           'revaluation_unrealized_loss_id',
                                                                           'revaluation_realized_gain_id',
                                                                           'revaluation_realized_loss_id',
                                                                           'revaluation_rounding_id').first()

        main_transaction = Transaction()
        main_transaction.transaction_date = rev_date
        main_transaction.rate_date = rate_date
        main_transaction.functional_amount = math.fabs(gain_loss)
        main_transaction.amount = 0
        main_transaction.total_amount = 0
        main_transaction.functional_currency_id = self.d_company.currency_id
        main_transaction.exchange_rate = newEntry.exchange_rate
        main_transaction.currency_id = newEntry.currency_id
        main_transaction.source_type = newEntry.source_type
        main_transaction.is_auto_exch = True

        desc = ""

        if newEntry.customer:
            desc = newEntry.customer.code + '-' + newEntry.customer.name + '-' + newEntry.currency.symbol
        elif newEntry.supplier:
            desc = newEntry.supplier.code + '-' + newEntry.supplier.name + '-' + newEntry.currency.symbol

        main_transaction.reference = newEntry.reference
        main_transaction.description = desc

        if self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']:  # AR
            if is_gain:
                main_transaction.is_credit_account = False
            else:
                main_transaction.is_credit_account = True
        else:
            if is_gain:
                main_transaction.is_credit_account = True
            else:
                main_transaction.is_credit_account = False

        main_transaction.is_debit_account = not main_transaction.is_credit_account
        main_transaction.journal = newEntry
        main_transaction.order_id = newEntry.order_id
        main_transaction.company = newEntry.company
        main_transaction.account_id = acc['control_account_id']
        main_transaction.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                    BALANCE_TYPE_DICT['Debit'])[main_transaction.is_debit_account]
        main_transaction.save()

        if is_realized == False:
            if is_gain:
                # Revaluation Unrealized Gain
                unrealized_gain_transaction = deepcopy(main_transaction)
                unrealized_gain_transaction.pk = None
                unrealized_gain_transaction.is_debit_account = (1, 0)[main_transaction.is_debit_account]
                unrealized_gain_transaction.is_credit_account = (1, 0)[main_transaction.is_credit_account]
                unrealized_gain_transaction.account_id = acc['revaluation_unrealized_gain_id']
                unrealized_gain_transaction.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                                       BALANCE_TYPE_DICT['Debit'])[
                    unrealized_gain_transaction.is_debit_account]
                unrealized_gain_transaction.save()

            else:
                # Revaluation Unrealized Loss
                unrealized_loss_transaction = deepcopy(main_transaction)
                unrealized_loss_transaction.pk = None
                unrealized_loss_transaction.is_debit_account = (1, 0)[main_transaction.is_debit_account]
                unrealized_loss_transaction.is_credit_account = (1, 0)[main_transaction.is_credit_account]
                unrealized_loss_transaction.account_id = acc['revaluation_unrealized_loss_id']
                unrealized_loss_transaction.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                                       BALANCE_TYPE_DICT['Debit'])[
                    unrealized_loss_transaction.is_debit_account]
                unrealized_loss_transaction.save()

        else:
            if is_gain:
                # Revaluation Realized Gain
                realized_gain_transaction = deepcopy(main_transaction)
                realized_gain_transaction.pk = None
                realized_gain_transaction.is_debit_account = (1, 0)[main_transaction.is_debit_account]
                realized_gain_transaction.is_credit_account = (1, 0)[main_transaction.is_credit_account]
                realized_gain_transaction.account_id = acc['revaluation_unrealized_gain_id']
                realized_gain_transaction.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                                     BALANCE_TYPE_DICT['Debit'])[
                    realized_gain_transaction.is_debit_account]
                realized_gain_transaction.save()

            else:
                # Revaluation Realized Loss
                realized_loss_transaction = deepcopy(main_transaction)
                realized_loss_transaction.pk = None
                realized_loss_transaction.is_debit_account = (1, 0)[main_transaction.is_debit_account]
                realized_loss_transaction.is_credit_account = (1, 0)[main_transaction.is_credit_account]
                realized_loss_transaction.account_id = acc['revaluation_unrealized_loss_id']
                realized_loss_transaction.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                                     BALANCE_TYPE_DICT['Debit'])[
                    realized_loss_transaction.is_debit_account]
                realized_loss_transaction.save()

        return True

    def getFunctionalAmount(self, j, curr_set, r_amount):
        rate = float(curr_set['rate'])
        journal_found = False
        if len(self.last_revals) > 0:
            for rev in self.last_revals:
                if rev['curr_id'] == int(curr_set['curr_id']):
                    if self.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                        j_revl = RevaluationDetails.objects.filter(posting_id=rev['id'], document_no=j.document_number, customer_id=j.customer_id).exclude(source_amount=0).last()
                    else:
                        j_revl = RevaluationDetails.objects.filter(posting_id=rev['id'], document_no=j.document_number, supplier_id=j.supplier_id).exclude(source_amount=0).last()
                    if j_revl:
                        journal_found = True
                        if j.is_fully_paid == True:
                            r_amount = 0
                            difference = round_number(float(r_amount) - float(j_revl.gain_loss))
                            total_amount = round_number(float(difference) / float(rate))
                            return [difference, r_amount]
                        # No payment or receipt or same exchange rate
                        elif j_revl.source_amount == r_amount and float(j_revl.rev_rate) == float(curr_set['rate']):
                            return [0, 0]
                        else:
                            f_amount = Decimal(rate) * Decimal(r_amount)
                            f_old_amount = r_amount
                            if j.exchange_rate and float(j.exchange_rate) == float(curr_set['rate']):
                                return [round_number(j_revl.gain_loss), round_number(j_revl.gain_loss)]
                            if j.exchange_rate and float(j.exchange_rate) != 0.000000:
                                f_old_amount = round_number(Decimal(r_amount) * Decimal(j.exchange_rate))
                            if j.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                difference = round_number((float(f_amount) - (float(f_old_amount) + float(j_revl.gain_loss))))
                            else:
                                difference = round_number((float(f_amount) - (float(f_old_amount) - float(j_revl.gain_loss))))
                            total_amount = round_number(float(difference) / float(rate))
                            return [difference, total_amount]
            if not journal_found:
                f_amount = Decimal(rate) * Decimal(r_amount)
                f_old_amount = r_amount
                if j.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                    if j.currency_id == int(curr_set['curr_id']):
                        if j.exchange_rate and float(j.exchange_rate) != 0.000000:
                            f_old_amount = round_number(Decimal(r_amount) * Decimal(j.exchange_rate))
                    elif j.original_currency_id == int(curr_set['curr_id']):
                        if j.orig_exch_rate and float(j.orig_exch_rate) != 0.000000:
                            f_old_amount = round_number(Decimal(r_amount) * Decimal(j.orig_exch_rate))
                else:
                    if j.exchange_rate and float(j.exchange_rate) != 0.000000:
                        f_old_amount = round_number(Decimal(r_amount) * Decimal(j.exchange_rate))
                difference = round_number(float(f_amount) - float(f_old_amount))
                total_amount = round_number(float(difference) / float(rate))
                return [difference, total_amount]
        else:
            f_amount = Decimal(rate) * Decimal(r_amount)
            f_old_amount = r_amount
            if j.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                if j.currency_id == int(curr_set['curr_id']):
                    if j.exchange_rate and float(j.exchange_rate) != 0.000000:
                        f_old_amount = round_number(Decimal(r_amount) * Decimal(j.exchange_rate))
                elif j.original_currency_id == int(curr_set['curr_id']):
                    if j.orig_exch_rate and float(j.orig_exch_rate) != 0.000000:
                        f_old_amount = round_number(Decimal(r_amount) * Decimal(j.orig_exch_rate))
            else:
                if j.exchange_rate and float(j.exchange_rate) != 0.000000:
                    f_old_amount = round_number(Decimal(r_amount) * Decimal(j.exchange_rate))
            difference = round_number(float(f_amount) - float(f_old_amount))
            total_amount = round_number(float(difference) / float(rate))
            return [difference, total_amount]

    def setBalanceType(self, amount, doc_type):
        plus = True if amount >= 0 else False
        if doc_type == '3':  # Credit Note
            return True if plus else False
        else:
            return False if plus else True

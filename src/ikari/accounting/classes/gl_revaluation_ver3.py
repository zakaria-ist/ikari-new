import math
import datetime
from decimal import Decimal
from accounting.models import Journal, Batch
from accounts.models import Account, AccountHistory, AccountCurrency, RevaluationCode
from companies.models import Company
from transactions.models import Transaction
from utilities.common import generate_batch_number, round_number, add_one_month
from utilities.constants import SOURCE_LEDGER_DICT, TRANSACTION_TYPES, STATUS_TYPE_DICT, DOCUMENT_TYPE_DICT, \
    INPUT_TYPE_DICT, BALANCE_TYPE_DICT
from utilities.messages import RV_ERR_NO_CURRENCY, RV_ERR_NO_RV_ACCOUNT1, RV_ERR_NO_POSTED_JOURNAL, \
    RV_ERR_CREATE_BATCH, RV_WARN_UNPROCESSED_ENTRIES, RV_SUCCESS, RV_FAILED


class C_GL_Revaluation_ver3:
    request = None
    d_company = None
    company_id = None
    BatchData = None
    CurrencySets = None
    RevaluationSets = None
    EntrySets = None
    FailedEntries = None

    def __init__(self, request):
        self.company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.session_date = request.session['session_date']
        self.d_company = Company.objects.get(pk=self.company_id)
        self.request = request
        self.entries = 0
        self.BatchData = {'batch_data': None, 'batch_name': None, 'amount': 0, 'entries': 0, 'batch_date': self.session_date}
        self.CurrencySets = []
        self.RevaluationSets = []
        self.EntrySets = []
        self.FailedEntries = []

    # main method
    def GenerateGLRevaluation(self, CurrencyLists):
        result = self.createCurrencyLists(CurrencyLists)

        if result[0]:
            result = self.createRevaluationSets()

            if result[0]:
                result = self.calculateRevalueAmount()

                if result[0]:
                    result = self.createBatch()

                    if result[0]:
                        result = self.createEntries()

        return result

    def createCurrencyLists(self, CurrencyLists):
        result = False
        status = RV_ERR_NO_CURRENCY

        if len(CurrencyLists) > 0:
            for CurrencyList in CurrencyLists:
                self.CurrencySets.append(CurrencyList)

            result = True
            status = None

        return [result, status, 'warn']

    def createRevaluationSets(self):
        result = True
        status = None

        self.BatchData['batch_name'] = self.request.POST.get('txt_batch_desc')

        for CurrencySet in self.CurrencySets:
            acc1 = int(CurrencySet['acc_id_1'])
            acc2 = int(CurrencySet['acc_id_2'])
            rev_code_id = int(CurrencySet['rev_code_id'])

            revaluation_account = Account.objects.filter(is_hidden=False, is_active=True,
                                                         company_id=self.company_id,
                                                         account_segment__range=(acc1, acc2),
                                                         is_multicurrency=True)

            if revaluation_account.count():
                for rev_account in revaluation_account:
                    account_currency = AccountCurrency.objects.filter(is_hidden=False, is_active=True,
                                                                      account_id=rev_account.id,
                                                                      revaluation_code_id=rev_code_id,
                                                                      currency_id=CurrencySet['curr_id'])\
                        .select_related('account', 'currency')

                    if account_currency and account_currency.count():
                        for acc_curr in account_currency:
                            if acc_curr.revaluation_code_id:
                                rev_account_list = {'acc_id': rev_account.id,
                                                    'acc_code': rev_account.code,
                                                    'balance_type': rev_account.balance_type,
                                                    'period_from': CurrencySet['period_from'],
                                                    'period_to': CurrencySet['period_to'],
                                                    'fiscal_year': CurrencySet['fiscal_year'],
                                                    'rate': CurrencySet['rate'],
                                                    'rate_date': CurrencySet['rate_date'],
                                                    'exchrateid': CurrencySet['exchrateid'],
                                                    'je_date': CurrencySet['je_date'],
                                                    'revaluation_code_id': None,
                                                    'currency_id': None
                                                    }
                                rev_account_list['revaluation_code_id'] = acc_curr.revaluation_code_id
                                rev_account_list['currency_id'] = acc_curr.currency_id
                                rev_account_list['currency_code'] = acc_curr.currency.code

                                self.RevaluationSets.append(rev_account_list)

        if len(self.RevaluationSets) == 0:
            result = False
            status = RV_ERR_NO_RV_ACCOUNT1

        return [result, status, 'warn']

    def createEntrySets(self, RevaluationSet, amount):
        EntrySet = {}

        EntrySet['entry_num'] = self.BatchData['entries'] + 1
        EntrySet['amount'] = amount
        EntrySet['exchrateid'] = RevaluationSet['exchrateid']
        EntrySet['acc_id'] = RevaluationSet['acc_id']
        EntrySet['acc_code'] = RevaluationSet['acc_code']
        EntrySet['currency_id'] = RevaluationSet['currency_id']
        EntrySet['currency_code'] = RevaluationSet['currency_code']
        EntrySet['balance_type'] = RevaluationSet['balance_type']
        EntrySet['rate'] = RevaluationSet['rate']
        EntrySet['rate_date'] = RevaluationSet['rate_date']
        EntrySet['revaluation_code_id'] = RevaluationSet['revaluation_code_id']
        EntrySet['je_date'] = RevaluationSet['je_date']
        EntrySet['period_to'] = RevaluationSet['period_to']
        EntrySet['fiscal_year'] = RevaluationSet['fiscal_year']

        self.EntrySets.append(EntrySet)
        self.BatchData['entries'] += 1

        return

    # def getBeginingBalance(self, RevaluationSet):
    #     begin_balance = {'src': 0, 'func': 0}
    #     previous_month = (int(RevaluationSet['period_from']) - 1, 12)[int(RevaluationSet['period_from']) == 1]
    #     year = (int(RevaluationSet['fiscal_year']), int(RevaluationSet['fiscal_year']) - 1)[int(RevaluationSet['period_from']) == 1]

    #     accountHistory = AccountHistory.objects.filter(is_hidden=False, company_id=self.company_id,
    #                                                    account_id=RevaluationSet['acc_id'],
    #                                                    period_month=previous_month,
    #                                                    period_year=year,
    #                                                    source_currency_id=RevaluationSet['currency_id']).first()

    #     if accountHistory:
    #         begin_balance['src'] = Decimal(accountHistory.source_end_balance)
    #         begin_balance['func'] = Decimal(accountHistory.functional_end_balance)

    #     return begin_balance

    def getAccountNetChange(self, RevaluationSet):
        net_change = {'src_eb': 0, 'func_eb': 0, 'src_nc': 0, 'func_nc': 0, 'func_bb': 0}
        from_month = int(RevaluationSet['period_from'])
        to_month = int(RevaluationSet['period_to'])
        year = int(RevaluationSet['fiscal_year'])

        accountHistories = AccountHistory.objects.filter(is_hidden=False, company_id=self.company_id,
                                                         account_id=RevaluationSet['acc_id'], period_month__in=(from_month, to_month),
                                                         period_year=year, source_currency_id=RevaluationSet['currency_id']
                                                         ).select_related('account', 'source_currency')

        for accountHistory in accountHistories:
            net_change['src_eb'] = round_number(accountHistory.source_end_balance)
            net_change['func_eb'] = round_number(accountHistory.functional_end_balance)
            net_change['func_bb'] = round_number(accountHistory.functional_begin_balance)
            net_change['src_nc'] = round_number(accountHistory.source_net_change)
            net_change['func_nc'] = round_number(accountHistory.functional_net_change)

        return net_change

    def getNetChange(self, RevaluationSet):
        net_change = {'src': 0, 'func': 0}

        trx_list = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                                              journal__batch__status=int(STATUS_TYPE_DICT['Posted']),
                                              journal__status__in=(int(STATUS_TYPE_DICT['Posted']),
                                                                   int(STATUS_TYPE_DICT['Auto Reverse Entry'])),
                                              journal__is_hidden=False,
                                              journal__batch__batch_type=dict(TRANSACTION_TYPES)['GL'],
                                              journal__perd_month__range=(
                                                  RevaluationSet['period_from'], RevaluationSet['period_to']),
                                              journal__perd_year=RevaluationSet['fiscal_year'],
                                              account_id=RevaluationSet['acc_id'],
                                              currency_id=RevaluationSet['currency_id']) \
            .exclude(journal__source_type__in=('AR-GL', 'AP-GL')) \
            .select_related('journal', 'journal__batch', 'account', 'currency')
        # .exclude(source_type__in=('AR-GL', 'AP-GL')) \

        for trx in trx_list:
            src_amt = (trx.total_amount, math.fabs(trx.total_amount))[trx.total_amount < 0]
            # fn_amt = (trx.functional_amount, math.fabs(trx.functional_amount))[trx.functional_amount < 0]
            source_amount = round_number((src_amt * -1, src_amt)[trx.is_debit_account])
            # functional_amount = (Decimal(fn_amt) * -1, Decimal(fn_amt))[trx.is_debit_account]
            # if self.d_company.currency.is_decimal:
            #     functional_amount = round(float(functional_amount), 2)
            # else:
            #     functional_amount = round(float(functional_amount))
            net_change['src'] += source_amount
            # net_change['func'] += functional_amount

        return net_change

    def getARAPRevAmount(self, RevaluationSet):
        net_change = 0

        trx_list = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                                              journal__batch__status=int(STATUS_TYPE_DICT['Posted']),
                                              journal__status__in=(int(STATUS_TYPE_DICT['Posted']),
                                                                   int(STATUS_TYPE_DICT['Auto Reverse Entry'])),
                                              journal__is_hidden=False,
                                              journal__batch__batch_type=dict(TRANSACTION_TYPES)['GL'],
                                              journal__perd_month__range=(
                                                  RevaluationSet['period_from'], RevaluationSet['period_to']),
                                              journal__perd_year=RevaluationSet['fiscal_year'],
                                              account_id=RevaluationSet['acc_id'],
                                              currency_id=RevaluationSet['currency_id'],
                                              #   source_type__in=('AR-GL', 'AP-GL'),
                                              journal__source_type__in=('AR-GL', 'AP-GL'))\
            .select_related('journal', 'journal__batch', 'account', 'currency')

        for trx in trx_list:
            # fn_amt = (trx.functional_amount, math.fabs(trx.functional_amount))[trx.functional_amount < 0]
            functional_amount = (float(trx.functional_amount) * -1, float(trx.functional_amount))[trx.is_debit_account]
            if self.d_company.currency.is_decimal:
                functional_amount = round_number(functional_amount)
            else:
                functional_amount = round_number(functional_amount)

            net_change += functional_amount

        return net_change

    def calculateRevalueAmount(self):
        result = False
        status = RV_ERR_NO_POSTED_JOURNAL
        processed = 0

        for RevaluationSet in self.RevaluationSets:

            print('acc_code: ', RevaluationSet['acc_code'], ' ', RevaluationSet['currency_code'])
            account_net_changes = self.getAccountNetChange(RevaluationSet)
            print('account_net_changes: ', account_net_changes, RevaluationSet['rate'])
            source_end_balance = account_net_changes['src_eb'] * Decimal(RevaluationSet['rate'])
            print('source_end_balance: ', source_end_balance)
            functional_end_balance = account_net_changes['func_nc'] + round_number(account_net_changes['func_bb'], 2)
            print('functional_end_balance: ', functional_end_balance)
            revaluation = source_end_balance - round_number(functional_end_balance, 2)
            print('revaluation: ', revaluation)

            if not self.d_company.currency.is_decimal:
                revaluation = float(round_number(float(revaluation), 0))
            if float(round_number(revaluation, 2)) != 0.00:
                self.createEntrySets(RevaluationSet, revaluation)
                processed += 1

        if processed > 0:
            result = True

        return [result, status, 'warn']

    def generate_entry_number(self, company_id, batch_id):
        jour = Journal.objects.filter(company_id=company_id, batch_id=batch_id, is_hidden=False)
        cnt = 0
        jour_last = 0

        if jour:
            cnt = jour.count()

            if jour.last().code:
                jour_last = int(jour.last().code)

        jour_number = cnt + 1 if cnt > jour_last else jour_last + 1

        return jour_number

    def createBatch(self):
        result = False
        status = None

        try:
            gl_rv_batch = Batch()

            gl_rv_batch.description = self.BatchData['batch_name']
            gl_rv_batch.update_by = self.request.user.id
            gl_rv_batch.batch_no = generate_batch_number(self.company_id, dict(TRANSACTION_TYPES)['GL'])
            gl_rv_batch.batch_amount = 0
            gl_rv_batch.no_entries = 0
            gl_rv_batch.currency_id = self.d_company.currency_id
            gl_rv_batch.status = int(STATUS_TYPE_DICT['Open'])
            gl_rv_batch.company_id = self.company_id
            gl_rv_batch.input_type = INPUT_TYPE_DICT['Generated']
            gl_rv_batch.document_type = DOCUMENT_TYPE_DICT['Undefined']
            gl_rv_batch.batch_type = dict(TRANSACTION_TYPES)['GL']
            gl_rv_batch.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
            gl_rv_batch.is_hidden = False
            gl_rv_batch.batch_date = self.BatchData['batch_date']
            gl_rv_batch.save()

            self.BatchData['batch_data'] = gl_rv_batch

            result = True

        except Exception:
            status = RV_FAILED + RV_ERR_CREATE_BATCH

        return [result, status, 'error']

    def createEntries(self):
        result = False
        status = None
        success = Fail = 0

        if len(self.EntrySets):
            for EntrySet in self.EntrySets:
                if float(EntrySet['amount']) != 0.000000:
                    try:
                        gl_rv_journal = Journal()

                        gl_rv_journal.code = EntrySet['entry_num']
                        gl_rv_journal.code = self.generate_entry_number(self.company_id,
                                                                        self.BatchData['batch_data'].id)
                        gl_rv_journal.name = 'Revaluation entries for account ' + str(EntrySet['acc_code']) + ' on ' + \
                                             EntrySet['currency_code']
                        gl_rv_journal.source_type = 'GL-RV'
                        gl_rv_journal.document_date = EntrySet['je_date']
                        gl_rv_journal.posting_date = EntrySet['je_date']
                        gl_rv_journal.amount = float(round_number(math.fabs(EntrySet['amount']), 6))
                        gl_rv_journal.tax_amount = 0.000000
                        gl_rv_journal.exchange_rate = Decimal(EntrySet['rate'])

                        gl_rv_journal.total_amount = float(round_number(math.fabs(EntrySet['amount']), 6))
                        gl_rv_journal.status = int(STATUS_TYPE_DICT['Open'])
                        gl_rv_journal.journal_type = dict(TRANSACTION_TYPES)['GL']
                        gl_rv_journal.company_id = self.company_id
                        gl_rv_journal.is_hidden = False
                        gl_rv_journal.currency_id = self.d_company.currency_id
                        gl_rv_journal.update_by = self.request.user.id
                        gl_rv_journal.batch = self.BatchData['batch_data']
                        try:
                            if int(EntrySet['exchrateid']) > 0:
                                gl_rv_journal.exchange_rate_fk_id = int(EntrySet['exchrateid'])
                        except:
                            pass
                        gl_rv_journal.is_auto_reverse = True
                        gl_rv_journal.reverse_to_period = 1

                        rev_yy = int(EntrySet['fiscal_year'])
                        rev_mm = int(EntrySet['period_to'])
                        
                        reverse_to_period = add_one_month(datetime.datetime.strptime(gl_rv_journal.document_date, "%Y-%m-%d"))

                        gl_rv_journal.reverse_to_period_val = str(reverse_to_period.year) + '-' + str(reverse_to_period.month) + '-01'
                        gl_rv_journal.perd_month = rev_mm
                        gl_rv_journal.perd_year = rev_yy
                        gl_rv_journal.save()

                        self.BatchData['batch_data'].batch_amount += Decimal(EntrySet['amount'])
                        self.BatchData['batch_data'].no_entries += 1
                        self.BatchData['batch_data'].batch_date = EntrySet['je_date']
                        self.BatchData['batch_data'].save()

                        if not self.createTransactions(EntrySet, gl_rv_journal.id):
                            self.FailedEntries.append(EntrySet)
                            Fail += 1
                        else:
                            success += 1

                    except Exception as e:
                        print(e)
                        self.FailedEntries.append(EntrySet)
                        Fail += 1

        result = (False, True)[Fail == 0]
        success_msg = RV_SUCCESS % (self.BatchData['batch_data'].batch_no)
        fail_msg = RV_WARN_UNPROCESSED_ENTRIES % (Fail)
        status = (success_msg, fail_msg)[Fail > 0]

        return [result, status, 'error']

    def createTransactions(self, EntrySet, journal_id):
        result = True

        try:
            revaluation_code = RevaluationCode.objects.get(pk=EntrySet['revaluation_code_id'])

            if EntrySet['amount'] >= 0:
                is_gain = True
            else:
                is_gain = False

            MainAccount = Transaction()

            MainAccount.transaction_date = self.BatchData['batch_date']
            MainAccount.journal_id = journal_id
            MainAccount.description = 'Revalued Source'
            MainAccount.account_id = EntrySet['acc_id']
            MainAccount.currency_id = EntrySet['currency_id']
            MainAccount.is_debit_account = (False, True)[EntrySet['amount'] >= 0]
            MainAccount.is_credit_account = (True, False)[EntrySet['amount'] >= 0]
            MainAccount.amount = 0
            MainAccount.functional_currency_id = self.d_company.currency_id
            MainAccount.total_amount = 0
            MainAccount.functional_amount = math.fabs(Decimal(EntrySet['amount']))
            MainAccount.exchange_rate = Decimal(EntrySet['rate'])
            MainAccount.rate_date = EntrySet['rate_date'] if EntrySet['rate_date'] else None
            MainAccount.is_hidden = False
            MainAccount.update_by = self.request.user.id
            MainAccount.company_id = self.company_id
            MainAccount.source_type = 'GL-RV'
            MainAccount.reference = ''
            MainAccount.is_auto_exch = True
            MainAccount.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                   BALANCE_TYPE_DICT['Debit'])[MainAccount.is_debit_account]

            MainAccount.save()

            ReverseAccount = Transaction()
            ReverseAccount.transaction_date = self.BatchData['batch_date']
            ReverseAccount.journal_id = journal_id
            ReverseAccount.description = ('Revalued Gain', 'Revalued Loss')[Decimal(EntrySet['amount']) < 0]
            ReverseAccount.description = ('Revalued Gain', 'Revalued Loss')[Decimal(EntrySet['amount']) < 0]
            ReverseAccount.account_id = revaluation_code.revaluation_unrealized_gain_id if is_gain else revaluation_code.revaluation_unrealized_loss_id
            ReverseAccount.currency_id = EntrySet['currency_id']
            ReverseAccount.is_debit_account = not MainAccount.is_debit_account
            ReverseAccount.is_credit_account = not MainAccount.is_credit_account
            ReverseAccount.amount = 0
            ReverseAccount.functional_currency_id = self.d_company.currency_id
            ReverseAccount.total_amount = 0
            ReverseAccount.functional_amount = math.fabs(Decimal(EntrySet['amount']))
            ReverseAccount.exchange_rate = Decimal(EntrySet['rate'])
            ReverseAccount.rate_date = EntrySet['rate_date'] if EntrySet['rate_date'] else None
            ReverseAccount.is_hidden = False
            ReverseAccount.update_by = self.request.user.id
            ReverseAccount.company_id = self.company_id
            ReverseAccount.source_type = 'GL-RV'
            ReverseAccount.reference = ''
            ReverseAccount.is_auto_exch = True
            ReverseAccount.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                      BALANCE_TYPE_DICT['Debit'])[ReverseAccount.is_debit_account]

            ReverseAccount.save()

        except Exception as e:
            print(e)
            result = False

        return result

import calendar
import math
from copy import deepcopy
from datetime import datetime, date
from decimal import getcontext
from django.db.models.expressions import RawSQL
from django.db.models import Sum
from django.db import transaction as transactionlib
from accounting.forms import JournalGLForm, BatchInfoForm

from accounting.models import Batch, Journal, FiscalCalendar
from accounts.models import Account, AccountHistory
from companies.models import Company
from transactions.models import Transaction
from utilities.common import generate_batch_number, round_number
from utilities.constants import SOURCE_LEDGER_DICT, TRANSACTION_TYPES, STATUS_TYPE_DICT, INPUT_TYPE_DICT, \
    BALANCE_TYPE_DICT, ACCOUNT_TYPE_DICT
from utilities.messages import YEAR_END_CLOSING_SUCCESS, YEAR_END_CLOSING_FAILED, YEAR_END_CLOSING_ERROR, \
    YEAR_END_CLOSING_ERR1, RV_ERR_CREATE_BATCH, YEAR_END_CLOSING_ERR4, YEAR_END_CLOSING_ERR6, YEAR_END_CLOSING_NONE, \
    BATCH_CREATED, ACCOUNT_CLOSE_FAILED, REFRESH_OR_GO_GET_SUPPORT, IC_SP_MUST_LOCKED, \
    YEAR_END_CLOSING_ERR5, YEAR_END_CLOSING_WARN1


class C_Closing:
    request = None
    company_id = 0
    d_company = None
    batch = None
    year = None
    month = None
    last_CLS_id = None
    retained_earning_account = None
    retained_earning_account_history = None
    income_statement_accounts = None
    transactions = None

    def __init__(self, request):
        getcontext().prec = 6
        self.request = request
        self.company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.d_company = Company.objects.get(pk=self.company_id)
        self.last_CLS_id = 0
        self.income_statement_accounts = []
        self.transactions = []
        self.closing_date = request.session['session_date']
        fsc_calendar = FiscalCalendar.objects.filter(company_id=self.company_id, is_hidden=0, start_date__lte=self.closing_date, end_date__gte=self.closing_date).last()
        if fsc_calendar:
            self.year = fsc_calendar.fiscal_year
            self.month = fsc_calendar.period
        else:
            self.year = self.closing_date.year
            self.month = self.closing_date.month

    def generateClosingBatch(self, pyear):
        self.year = pyear
        fsc_calendar = FiscalCalendar.objects.filter(company_id=self.company_id, is_hidden=0, fiscal_year=pyear, period=12).last()
        if fsc_calendar:
            self.year = fsc_calendar.fiscal_year
            self.month = fsc_calendar.period
            self.closing_date = fsc_calendar.end_date

        result = self.isClosingAccountExist()
        if result[0]:
            self.setLastClosingID()
            result = self.getIncomeStatementAccounts()
            if result[0]:
                result = self.generateBatchEntries()
        return result

    def isOtherModulesClosed(self):
        result = True
        status = None
        fiscal_periods = FiscalCalendar.objects.filter(fiscal_year=self.year, company_id=self.company_id,
                                                       is_hidden=False)
        if fiscal_periods:
            open_period_count = 0
            for fiscal_period in fiscal_periods:
                if not fiscal_period.is_sp_locked:
                    open_period_count += 1
            if open_period_count > 0:
                result = False
                status = YEAR_END_CLOSING_FAILED % (self.year) + IC_SP_MUST_LOCKED
        else:
            result = False
            status = YEAR_END_CLOSING_ERROR + YEAR_END_CLOSING_ERR5 % (self.year) + YEAR_END_CLOSING_WARN1 % (self.year)
        return [result, status]

    def isClosingAccountExist(self):
        result = False
        status = YEAR_END_CLOSING_FAILED % (self.year) + YEAR_END_CLOSING_ERR1
        retainedEarningAccount = Account.objects.filter(account_type=ACCOUNT_TYPE_DICT['Retained Earning'],
                                                        is_hidden=0,
                                                        is_active=True,
                                                        company_id=self.company_id)

        if retainedEarningAccount.count() > 1:
            retainedEarningAccount = retainedEarningAccount.filter(name__icontains='RETAINED EARNING').first()
            self.retained_earning_account = retainedEarningAccount
            result = True
            status = None
        elif retainedEarningAccount.count() == 1:
            retainedEarningAccount = retainedEarningAccount.first()
            self.retained_earning_account = retainedEarningAccount
            result = True
            status = None
        return [result, status]

    def setLastClosingID(self):
        lastClosing = AccountHistory.objects.filter(is_hidden=0, company_id=self.company_id,
                                                    period_month__contains='CLS',
                                                    account_id=self.retained_earning_account.id) \
            .exclude(functional_end_balance=0) \
            .order_by('-create_date').first()

        if lastClosing:
            self.last_CLS_id = lastClosing.id

    def getIncomeStatementAccounts(self):
        result = False
        status = YEAR_END_CLOSING_FAILED % (self.year) + YEAR_END_CLOSING_ERR4
        IncomeStatementAccounts = Account.objects.filter(company_id=self.company_id,
                                                         account_type=int(ACCOUNT_TYPE_DICT['Income Statement']),
                                                         is_hidden=False,
                                                         is_active=True)

        if IncomeStatementAccounts:
            currencies = AccountHistory.objects.filter(is_hidden=0, company_id=self.company_id,
                                                       period_year=self.year, period_month=12) \
                .exclude(source_currency_id__isnull=True).values('source_currency_id').distinct()
            for IncomeStatementAccount in IncomeStatementAccounts:
                self.income_statement_accounts.append(IncomeStatementAccount)
                for currency in currencies:
                    GetAccountHistory = self.getAccountHistory(IncomeStatementAccount.id,
                                                               currency['source_currency_id'], self.year, True)

                    trx = {'source': 0, 'functional': 0}
                    if GetAccountHistory['status']:
                        for account_history in GetAccountHistory['data']:
                            trx['source'] += float(account_history.source_end_balance)
                            trx['functional'] += float(account_history.functional_end_balance)
                        trx['account_id'] = IncomeStatementAccount.id
                        trx['currency_id'] = currency['source_currency_id']
                        self.transactions.append(trx)
            result = True

        return [result, status]

    def getAccountHistory(self, acc_id, curr_id, year=None, lastPeriodOnly=False):
        result = {
            'status': False,
            'data': []
        }
        if not year:
            year = self.year

        account_history_list = AccountHistory.objects.filter(is_hidden=0, company_id=self.company_id, account_id=acc_id)
        accountHistory = account_history_list.filter(period_year=year, source_currency_id=curr_id) \
            .annotate(year_number=RawSQL('CAST(period_year AS UNSIGNED)', params=[])) \
            .order_by('year_number', 'source_currency_id')

        if lastPeriodOnly:
            accountHistory = accountHistory.filter(period_month=12)

        if accountHistory:
            result['status'] = True
            for account_history in accountHistory:
                if float(round_number(float(account_history.functional_end_balance), 2)) != 0 \
                        or float(round_number(float(account_history.source_end_balance), 2)) != 0:
                    result['data'].append(account_history)

        return result

    def generateBatchEntries(self):
        result = [False, YEAR_END_CLOSING_FAILED % (self.year) + YEAR_END_CLOSING_ERROR + REFRESH_OR_GO_GET_SUPPORT]
        idx = 0
        result = self.createBatch()
        if result[0]:
            for income_statement_account in self.income_statement_accounts:
                total_amount = 0
                idx += 1
                entries = self.createEntries(self.batch, income_statement_account.code, total_amount, idx)
                if entries:
                    for transaction in self.transactions:
                        if transaction['account_id'] == income_statement_account.id:
                            self.createTransaction(entries, transaction)
                            closingAccount = Account.objects.get(pk=transaction['account_id'])
                            if self.skip_sum == False:
                                if transaction['currency_id'] == self.batch.currency_id and closingAccount.is_multicurrency == True:
                                    total_amount += math.fabs(transaction['source'])
                                else:
                                    total_amount += math.fabs(transaction['functional'])

                entries.amount = math.fabs(total_amount)
                entries.tax_amount = 0.000000
                entries.total_amount = math.fabs(total_amount)
                entries.save()
                if entries.total_amount == 0:
                    entries.delete()
                    idx -= 1

            self.batch.batch_amount = self.getTrxSum()
            self.batch.save()

            if self.batch.no_entries > 0:
                result = [True, YEAR_END_CLOSING_SUCCESS + BATCH_CREATED % (self.batch.batch_no)]
            else:
                result = [False, YEAR_END_CLOSING_SUCCESS + YEAR_END_CLOSING_ERR6]
                self.batch.delete()
        return result

    def getTrxSum(self):
        trx_sum = Transaction.objects.filter(is_hidden=False, company_id=self.company_id,
                                             journal__batch__id=self.batch.id, is_debit_account=True). \
            aggregate(sum_f_amt=Sum('functional_amount')).get('sum_f_amt')
        return trx_sum if trx_sum else 0

    def createBatch(self):
        result = True
        status = None
        with transactionlib.atomic():
            try:
                newBatch = BatchInfoForm().save(commit=False)
                newBatch.batch_no = generate_batch_number(self.company_id, dict(TRANSACTION_TYPES)['GL'])
                newBatch.description = 'CLOSING BATCH ENTRIES ' + str(self.year)
                newBatch.is_hidden = False
                newBatch.company_id = self.company_id
                newBatch.batch_type = dict(TRANSACTION_TYPES)['GL']
                newBatch.input_type = int(INPUT_TYPE_DICT['Generated'])
                newBatch.status = int(STATUS_TYPE_DICT['Open'])
                newBatch.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
                newBatch.currency_id = self.d_company.currency_id
                newBatch.create_date = datetime.today()
                newBatch.batch_date = self.closing_date
                newBatch.save()
                self.batch = newBatch
                status = YEAR_END_CLOSING_SUCCESS + YEAR_END_CLOSING_NONE % (newBatch.batch_no)
            except Exception as e:
                result = False
                status = YEAR_END_CLOSING_FAILED % (self.year) + RV_ERR_CREATE_BATCH
        return [result, status]

    def createEntries(self, batch, account, amount, num):
        with transactionlib.atomic():
            try:
                new_entry = JournalGLForm(company_id=self.company_id).save(commit=False)
                new_entry.status = STATUS_TYPE_DICT['Open']
                new_entry.journal_type = dict(TRANSACTION_TYPES)['GL']
                new_entry.code = num
                new_entry.name = 'CLOSING ENTRY FOR ACCOUNT ' + account
                new_entry.exchange_rate = 1.000000
                new_entry.is_hidden = False
                new_entry.batch_id = batch.id
                new_entry.source_type = 'GL-CL'
                new_entry.document_date = self.closing_date
                new_entry.perd_year = self.year
                new_entry.perd_month = 15
                new_entry.currency = batch.currency
                new_entry.company_id = batch.company_id
                new_entry.create_date = datetime.today()
                new_entry.save()

                batch.no_entries = num - 1
                batch.save()

                return new_entry

            except Exception as e:
                return False

    def createTransaction(self, journal, trx_data):
        with transactionlib.atomic():
            try:      
                date = datetime.today()
                self.skip_sum = False
                closingAccount = Account.objects.get(pk=trx_data['account_id'])
                transClosingAccount = Transaction()
                transClosingAccount.transaction_date = date
                transClosingAccount.account_id = closingAccount.id
                transClosingAccount.is_hidden = False
                transClosingAccount.tax_amount = 0.000000
                transClosingAccount.description = closingAccount.name
                transClosingAccount.journal_id = journal.id
                transClosingAccount.source_type = journal.source_type
                transClosingAccount.functional_currency_id = self.batch.currency_id
                transClosingAccount.currency_id = trx_data['currency_id']
                closingAccountName = (closingAccount.name).lower()
                is_gainloss_account = False
                if 'foreign' in closingAccountName and 'gain' in closingAccountName and 'loss' in closingAccountName:
                    is_gainloss_account = True
                if not is_gainloss_account and transClosingAccount.currency_id != self.batch.currency_id and \
                        trx_data['functional'] != 0 and trx_data['source'] == 0: # not func currency & src amount is zero
                    transClosingAccount.currency_id = self.batch.currency_id
                    transClosingAccount.total_amount = math.fabs(trx_data['functional'])
                    transClosingAccount.amount = math.fabs(trx_data['functional'])
                    transClosingAccount.functional_amount = math.fabs(trx_data['functional'])
                    if closingAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                        transClosingAccount.is_debit_account = (True, False)[trx_data['functional'] >= 0]
                        transClosingAccount.is_credit_account = (False, True)[trx_data['functional'] >= 0]
                    else:
                        transClosingAccount.is_debit_account = (False, True)[trx_data['functional'] < 0]
                        transClosingAccount.is_credit_account = (True, False)[trx_data['functional'] < 0]
                else:
                    if closingAccount.is_multicurrency == True:
                        transClosingAccount.total_amount = math.fabs(trx_data['source'])
                        transClosingAccount.amount = math.fabs(trx_data['source'])
                    elif transClosingAccount.currency_id != self.batch.currency_id and closingAccount.is_multicurrency == False:
                        transClosingAccount.total_amount = math.fabs(trx_data['source'])
                        transClosingAccount.amount = math.fabs(trx_data['source'])
                        transClosingAccount.is_hidden = True
                        self.skip_sum = True
                    else:
                        transClosingAccount.total_amount = math.fabs(trx_data['functional'])
                        transClosingAccount.amount = math.fabs(trx_data['functional'])
                    if transClosingAccount.currency_id == self.batch.currency_id and closingAccount.is_multicurrency == True:
                        transClosingAccount.functional_amount = math.fabs(trx_data['source'])
                        if closingAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                            transClosingAccount.is_debit_account = (True, False)[trx_data['source'] >= 0]
                            transClosingAccount.is_credit_account = (False, True)[trx_data['source'] >= 0]
                        else:
                            transClosingAccount.is_debit_account = (False, True)[trx_data['source'] < 0]
                            transClosingAccount.is_credit_account = (True, False)[trx_data['source'] < 0]
                    else:
                        transClosingAccount.functional_amount = math.fabs(trx_data['functional'])
                        if closingAccount.balance_type == BALANCE_TYPE_DICT['Debit']:
                            transClosingAccount.is_debit_account = (True, False)[trx_data['functional'] >= 0]
                            transClosingAccount.is_credit_account = (False, True)[trx_data['functional'] >= 0]
                        else:
                            transClosingAccount.is_debit_account = (False, True)[trx_data['functional'] < 0]
                            transClosingAccount.is_credit_account = (True, False)[trx_data['functional'] < 0]
    
                if float(round_number(float(transClosingAccount.functional_amount), 2)) == 0.00:
                    transClosingAccount.is_hidden = True
                    self.skip_sum = True
                if transClosingAccount.functional_amount != transClosingAccount.total_amount and transClosingAccount.total_amount != 0:
                    transClosingAccount.exchange_rate = float(transClosingAccount.functional_amount) / float(transClosingAccount.total_amount)
                else:
                    transClosingAccount.exchange_rate = 1.000000
                transClosingAccount.company_id = journal.company_id
                transClosingAccount.create_date = datetime.today()
                transClosingAccount.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                            BALANCE_TYPE_DICT['Debit'])[
                    transClosingAccount.is_debit_account]
                transClosingAccount.save()
                
                transRetainedEarning = deepcopy(transClosingAccount)
                transRetainedEarning.pk = None
                transRetainedEarning.description = self.retained_earning_account.name
                transRetainedEarning.account_id = self.retained_earning_account.id
                transRetainedEarning.is_debit_account = (1, 0)[transClosingAccount.is_debit_account]
                transRetainedEarning.is_credit_account = (1, 0)[transRetainedEarning.is_debit_account]
                transRetainedEarning.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                                BALANCE_TYPE_DICT['Debit'])[
                    transRetainedEarning.is_debit_account]
                transRetainedEarning.save()

                return True
            except Exception as e:
                return False

    def getAccountTransaction(self, acc_id):
        OpenTrxCount = 0
        with transactionlib.atomic():
            try:
                open_trx = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                                                    account_id=acc_id,
                                                    journal__perd_year__lte=self.year,
                                                    is_close=False)
                if open_trx.count():
                    OpenTrxCount = open_trx.count()
                    for trx in open_trx:
                        trx.is_close = True
                        trx.save()
            except:
                pass

        return OpenTrxCount

    def closeAccounts(self, batch_id):
        result = [False, YEAR_END_CLOSING_ERROR + REFRESH_OR_GO_GET_SUPPORT]
        status = ''
        errors = []
        with transactionlib.atomic():
            try:
                batch_data = Batch.objects.get(pk=batch_id, is_hidden=False, company_id=self.company_id)
                if batch_data:
                    self.batch = batch_data
                    result = self.isClosingAccountExist()
                    if result[0]:
                        self.setLastClosingID()
                        ClosingBatchData = self.getClosingBatchData(self.batch)
                        if ClosingBatchData:
                            #reset account history
                            for closingBatchData in ClosingBatchData:
                                self.resetSourceAccountHistoryBalance(closingBatchData)
                            #reset retain history
                            self.resetRetainAccountHistoryBalance()
                            for closingBatchData in ClosingBatchData:
                                ClearSourceAccountBalance = self.clearSourceAccountBalance(closingBatchData)
                                if ClearSourceAccountBalance[0]:
                                    p_year = closingBatchData.journal.document_date.strftime('%Y')
                                    if closingBatchData.journal.perd_year and closingBatchData.journal.perd_year > 0:
                                        p_year = closingBatchData.journal.perd_year
                                    GetAccountHistory = self.getAccountHistory(closingBatchData.account_id,
                                                                            closingBatchData.currency_id, p_year, True)
                                    if GetAccountHistory['status']:
                                        for account_history in GetAccountHistory['data']:
                                            ClearSourceAccountHistoryBalance = self.clearSourceAccountHistoryBalance(
                                                account_history)
                                            if ClearSourceAccountHistoryBalance:
                                                error_info = {'text': ClearSourceAccountHistoryBalance}
                                                errors.append(error_info)
                            
                            #update retained earning account history
                            output = self.updateRetainedEarning()
                            
                            if len(errors) > 0:
                                for err in errors:
                                    status += err['text']
                            result = [True, status]
                        else:
                            result = [False, YEAR_END_CLOSING_ERROR + YEAR_END_CLOSING_ERR6]

            except Exception as e:
                print(e)

        return result

    def getClosingBatchData(self, batch):
        closing_batch_data = None
        transactions = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                                                  journal__batch_id=batch.id). \
            exclude(account_id=self.retained_earning_account.id)
        if transactions:
            closing_batch_data = []
            for transaction in transactions:
                closing_batch_data.append(transaction)

        return closing_batch_data


    def updateRetainedEarning(self):
        company_id = self.company_id
        company = self.d_company
        
        transaction_list = Transaction.objects.filter(company_id=company_id, is_hidden=0, journal__is_hidden=0,
                                                        journal__batch_id=self.batch.id, account_id=self.retained_earning_account.id) \
                                    .select_related('journal', 'journal__batch', 'account')
        if transaction_list:
            year = transaction_list.first().journal.perd_year
        else:
            year = self.year
        account_history_list = AccountHistory.objects.filter(is_hidden=0, company_id=company_id,
                                                            period_year=year,
                                                            period_month__contains='CLS',
                                                            account_id=self.retained_earning_account.id) \
            .exclude(source_currency_id__isnull=True)\
            .select_related('account')

        # check if retain earning history has all currency entries
        currency_list = transaction_list.order_by(
            'currency_id').distinct().values_list('currency_id', flat=True)
        missing = False
        for currency_id in currency_list:
            curr_account_history_list = account_history_list.filter(
                source_currency_id=currency_id)
            if not len(curr_account_history_list):
                missing = True
                period_list = list(map(str, list(range(1, 13))))
                period_list.extend(['ADJ', 'CLS'])
                for i in period_list:
                    try:
                        i_int = int(i)
                    except Exception as e:
                        print(e)
                        i_int = 12
                    _, num_days = calendar.monthrange(year, i_int)
                    last_day = date(year, i_int, num_days)
                    self.create_account_history(year, i, last_day, self.retained_earning_account.id,
                                                currency_id, 0, company.currency_id, 0)
        if missing:
            account_history_list = AccountHistory.objects.filter(is_hidden=0, company_id=company_id,
                                                                 period_year=year,
                                                                 period_month__contains='CLS',
                                                                 account_id=self.retained_earning_account.id) \
                .exclude(source_currency_id__isnull=True)\
                .select_related('account')

        #reset earning
        account_history_list.update(functional_debit_amount=0, functional_credit_amount=0,
                                              source_debit_amount=0, source_credit_amount=0,
                                              source_net_change=0, functional_net_change=0)
        for period_CLS in account_history_list:
            try:
                period_CLS.source_end_balance = period_CLS.source_begin_balance
                period_CLS.functional_end_balance = period_CLS.functional_begin_balance
                period_CLS.update_date = datetime.today()
                period_CLS.update_by = self.request.user.id
                period_CLS.save()
            except Exception as e:
                print(e)

        for transaction in transaction_list:
            for account_history in account_history_list:
                if account_history.source_currency_id == transaction.currency_id or account_history.source_currency_id == company.currency_id:
                    if transaction.is_debit_account:
                        self.retained_earning_account.debit_amount = round_number(self.retained_earning_account.debit_amount) + round_number(transaction.functional_amount)
                        account_history.functional_debit_amount = round_number(account_history.functional_debit_amount) + round_number(transaction.functional_amount)
                        account_history.functional_net_change = round_number(account_history.functional_net_change) + round_number(transaction.functional_amount)
                    else:
                        self.retained_earning_account.credit_amount = round_number(self.retained_earning_account.credit_amount) - round_number(transaction.functional_amount)
                        account_history.functional_credit_amount = round_number(account_history.functional_credit_amount) - round_number(transaction.functional_amount)
                        account_history.functional_net_change = round_number(account_history.functional_net_change) - round_number(transaction.functional_amount)
                    account_history.functional_end_balance = round_number(account_history.functional_begin_balance) + round_number(account_history.functional_net_change)

                    if account_history.source_currency_id == transaction.currency_id:
                        if transaction.is_debit_account:
                            account_history.source_debit_amount = round_number(account_history.source_debit_amount) + round_number(transaction.total_amount)
                            account_history.source_net_change = round_number(account_history.source_net_change) + round_number(transaction.total_amount)
                        else:
                            account_history.source_credit_amount = round_number(account_history.source_credit_amount) - round_number(transaction.total_amount)
                            account_history.source_net_change = round_number(account_history.source_net_change) - round_number(transaction.total_amount)
                        account_history.source_end_balance = round_number(account_history.source_begin_balance) + round_number(account_history.source_net_change)

                    account_history.update_date = datetime.today()
                    account_history.save()

                    self.retained_earning_account.update_date = datetime.today()
                    self.retained_earning_account.save()

        # update next year
        account_history_list = AccountHistory.objects.filter(is_hidden=0, company_id=company_id,
                                                                period_year=year,
                                                                period_month__contains='CLS',
                                                                account_id=self.retained_earning_account.id)\
            .exclude(source_currency_id__isnull=True)\
            .select_related('account')
        for acc_histoty in account_history_list:
            src_eb = acc_histoty.source_end_balance
            func_eb = acc_histoty.functional_end_balance
            period_year = int(year)
            for _year in range(period_year + 1, period_year + 3):
                if _year > period_year:
                    for i in range(12):
                        _, num_days = calendar.monthrange(_year, i + 1)
                        last_day = date(_year, i + 1, num_days)
                        try:
                            next_history = AccountHistory.objects.select_related('account').filter(is_hidden=False,
                                                                        company_id=company_id,
                                                                        account_id=self.retained_earning_account.id,
                                                                        period_month=i + 1,
                                                                        period_year=_year,
                                                                        source_currency_id=acc_histoty.source_currency_id).first()
                            next_history.source_begin_balance = src_eb
                            next_history.source_end_balance = round_number(next_history.source_begin_balance) + round_number(next_history.source_net_change)
                            next_history.functional_begin_balance = func_eb
                            next_history.functional_end_balance = round_number(next_history.functional_begin_balance) + round_number(next_history.functional_net_change)
                            next_history.save()
                            src_eb = next_history.source_end_balance
                            func_eb = next_history.functional_end_balance
                        except Exception as e:
                            _period = i + 1
                            self.create_account_history(_year, _period, last_day, self.retained_earning_account.id,
                                                acc_histoty.source_currency_id,
                                                src_eb, company.currency_id,
                                                func_eb)

                    period_ADJ = AccountHistory.objects.select_related('account').filter(is_hidden=False, company_id=company_id,
                                                                account_id=self.retained_earning_account.id,
                                                                period_month__in=['ADJ'],
                                                                period_year=_year,
                                                                source_currency_id=acc_histoty.source_currency_id)
                    if period_ADJ:
                        for ADJ_CLS in period_ADJ:
                            ADJ_CLS.source_begin_balance = src_eb
                            ADJ_CLS.source_end_balance = round_number(ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                            ADJ_CLS.functional_begin_balance = func_eb
                            ADJ_CLS.functional_end_balance = round_number(ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                            ADJ_CLS.save()
                    else:
                        self.create_account_history(_year, 'ADJ', last_day, self.retained_earning_account.id,
                                            acc_histoty.source_currency_id, src_eb,
                                            company.currency_id, func_eb)

                    period_CLS = AccountHistory.objects.select_related('account').filter(is_hidden=False, company_id=company_id,
                                                                account_id=self.retained_earning_account.id,
                                                                period_month__in=['CLS'],
                                                                period_year=_year,
                                                                source_currency_id=acc_histoty.source_currency_id)
                    if period_CLS:
                        for ADJ_CLS in period_CLS:
                            ADJ_CLS.source_begin_balance = src_eb
                            ADJ_CLS.source_end_balance = round_number(ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                            ADJ_CLS.functional_begin_balance = func_eb
                            ADJ_CLS.functional_end_balance = round_number(ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                            ADJ_CLS.save()
                    else:
                        self.create_account_history(_year, 'CLS', last_day, self.retained_earning_account.id,
                                            acc_histoty.source_currency_id, src_eb,
                                            company.currency_id, func_eb)
        return True



    def resetSourceAccountHistoryBalance(self, trx):
        period_CLSS = AccountHistory.objects.select_related('account').filter(is_hidden=0, company_id=self.company_id,
                                                   account_id=trx.account_id,
                                                   period_year=self.year,
                                                   period_month='CLS') \
            .exclude(source_currency_id__isnull=True)
        for period_CLS in period_CLSS:
            try:
                period_CLS.source_debit_amount = 0
                period_CLS.source_credit_amount = 0
                period_CLS.source_net_change = 0
                period_CLS.source_end_balance = period_CLS.source_begin_balance
                period_CLS.functional_debit_amount = 0
                period_CLS.functional_credit_amount = 0
                period_CLS.functional_net_change = 0
                period_CLS.functional_end_balance = period_CLS.functional_begin_balance
                period_CLS.update_date = datetime.today()
                period_CLS.update_by = self.request.user.id
                period_CLS.save()
            except Exception as e:
                print(e)
        return True


    def resetRetainAccountHistoryBalance(self):
        period_CLSS = AccountHistory.objects.filter(is_hidden=0, company_id=self.company_id,
                                                   account_id=self.retained_earning_account.id,
                                                   period_year=self.year,
                                                   period_month='CLS') \
            .exclude(source_currency_id__isnull=True)\
            .select_related('account')
        for period_CLS in period_CLSS:
            try:
                period_CLS.source_debit_amount = 0
                period_CLS.source_credit_amount = 0
                period_CLS.source_net_change = 0
                period_CLS.source_end_balance = period_CLS.source_begin_balance
                period_CLS.functional_debit_amount = 0
                period_CLS.functional_credit_amount = 0
                period_CLS.functional_net_change = 0
                period_CLS.functional_end_balance = period_CLS.functional_begin_balance
                period_CLS.update_date = datetime.today()
                period_CLS.update_by = self.request.user.id
                period_CLS.save()
            except Exception as e:
                print(e)
        
        return True



    def clearSourceAccountHistoryBalance(self, acc_to_close):
        company = self.d_company
        status = YEAR_END_CLOSING_ERROR + REFRESH_OR_GO_GET_SUPPORT
        source_begin = float(acc_to_close.source_end_balance)
        source_net = float(acc_to_close.source_end_balance) * -1
        functional_begin = float(acc_to_close.functional_end_balance)
        functional_net = float(acc_to_close.functional_end_balance) * -1
        period_CLSS = AccountHistory.objects.filter(is_hidden=0, company_id=self.company_id,
                                                   account_id=acc_to_close.account_id,
                                                   period_year=acc_to_close.period_year,
                                                   period_month='CLS') \
            .exclude(source_currency_id__isnull=True)\
            .select_related('account')
        for period_CLS in period_CLSS:
            try:
                if period_CLS.source_currency_id == acc_to_close.source_currency_id:
                    if source_net > 0:
                        period_CLS.source_debit_amount = round_number(
                            period_CLS.source_debit_amount) + round_number(math.fabs(source_net))
                    else:
                        period_CLS.source_credit_amount = - \
                            (round_number(math.fabs(period_CLS.source_credit_amount)
                                          ) + round_number(math.fabs(source_net)))
                    if functional_net > 0:
                        period_CLS.functional_debit_amount = round_number(period_CLS.functional_debit_amount) + round_number(math.fabs(
                            functional_net))
                    else:
                        period_CLS.functional_credit_amount = -(round_number(math.fabs(period_CLS.functional_credit_amount)) + round_number(math.fabs(
                            functional_net)))
                    period_CLS.source_begin_balance = source_begin
                    period_CLS.source_net_change = source_net
                    period_CLS.source_end_balance = round_number(source_begin) + round_number(source_net)
                    period_CLS.functional_begin_balance = functional_begin
                    period_CLS.functional_net_change = functional_net
                    period_CLS.functional_end_balance = round_number(functional_begin) + round_number(functional_net)
                else:
                    period_CLS.source_begin_balance = 0
                    period_CLS.source_net_change = 0
                    period_CLS.source_end_balance = 0
                    period_CLS.functional_begin_balance = 0
                    period_CLS.functional_net_change = 0
                    period_CLS.functional_end_balance = 0
                period_CLS.update_date = datetime.today()
                period_CLS.update_by = self.request.user.id
                period_CLS.save()
                status = None
                try:
                    #self.transferToRetainedEarnings(acc_to_close):
                    
                    # update next fiscal year
                    if period_CLS:
                        src_eb = period_CLS.source_end_balance
                        func_eb = period_CLS.functional_end_balance
                        period_year = int(acc_to_close.period_year)
                        for _year in range(period_year + 1, period_year + 3):
                            for i in range(12):
                                _, num_days = calendar.monthrange(_year, i + 1)
                                last_day = date(_year, i + 1, num_days)
                                try:
                                    next_history = AccountHistory.objects.select_related('account').filter(is_hidden=False,
                                                                                company_id=self.company_id,
                                                                                account_id=period_CLS.account_id,
                                                                                period_month=i + 1,
                                                                                period_year=_year,
                                                                                source_currency_id=period_CLS.source_currency_id).first()
                                    next_history.source_begin_balance = src_eb
                                    next_history.source_end_balance = round_number(next_history.source_begin_balance) + round_number(next_history.source_net_change)
                                    next_history.functional_begin_balance = func_eb
                                    next_history.functional_end_balance = round_number(next_history.functional_begin_balance) + round_number(next_history.functional_net_change)
                                    next_history.save()
                                    src_eb = next_history.source_end_balance
                                    func_eb = next_history.functional_end_balance
                                except Exception as e:
                                    _period = i + 1
                                    self.create_account_history(_year, _period, last_day, period_CLS.account_id,
                                                        period_CLS.source_currency_id,
                                                        src_eb, company.currency_id,
                                                        func_eb)

                            period_ADJ = AccountHistory.objects.select_related('account').filter(is_hidden=False, company_id=self.company_id,
                                                                        account_id=period_CLS.account_id,
                                                                        period_month__in=['ADJ'],
                                                                        period_year=_year,
                                                                        source_currency_id=period_CLS.source_currency_id)
                            if period_ADJ:
                                for ADJ_CLS in period_ADJ:
                                    ADJ_CLS.source_begin_balance = src_eb
                                    ADJ_CLS.source_end_balance = round_number(ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                                    ADJ_CLS.functional_begin_balance = func_eb
                                    ADJ_CLS.functional_end_balance = round_number(ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                                    ADJ_CLS.save()
                            else:
                                self.create_account_history(_year, 'ADJ', last_day, period_CLS.account_id,
                                                    period_CLS.source_currency_id, src_eb,
                                                    company.currency_id, func_eb)

                            period_CLOS = AccountHistory.objects.select_related('account').filter(is_hidden=False, company_id=self.company_id,
                                                                        account_id=period_CLS.account_id,
                                                                        period_month__in=['CLS'],
                                                                        period_year=_year,
                                                                        source_currency_id=period_CLS.source_currency_id)
                            if period_CLOS:
                                for ADJ_CLS in period_CLOS:
                                    ADJ_CLS.source_begin_balance = src_eb
                                    ADJ_CLS.source_end_balance = round_number(ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                                    ADJ_CLS.functional_begin_balance = func_eb
                                    ADJ_CLS.functional_end_balance = round_number(ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                                    ADJ_CLS.save()
                            else:
                                self.create_account_history(_year, 'CLS', last_day, period_CLS.account_id,
                                                    period_CLS.source_currency_id, src_eb,
                                                    company.currency_id, func_eb)

                except Exception as e:
                    print(e)

            except Exception as e:
                pass

        else:
            account = Account.objects.get(pk=acc_to_close.account_id)
            if account:
                status = YEAR_END_CLOSING_ERROR + ACCOUNT_CLOSE_FAILED % (account.code + '-' + account.name, self.year)

        return status

    def clearSourceAccountBalance(self, trx_data):
        result = True
        status = YEAR_END_CLOSING_ERROR + REFRESH_OR_GO_GET_SUPPORT
        try:
            acc_to_close = Account.objects.get(pk=trx_data.account_id)
            if trx_data.is_debit_account and trx_data.functional_balance_type == BALANCE_TYPE_DICT['Debit']:
                acc_to_close.debit_amount = round_number(
                    acc_to_close.debit_amount) + round_number(trx_data.functional_amount)
                self.retained_earning_account.debit_amount = round_number(self.retained_earning_account.debit_amount) + round_number(
                    trx_data.functional_amount)
            else:
                acc_to_close.credit_amount = round_number(
                    acc_to_close.credit_amount) + round_number(trx_data.functional_amount)
                self.retained_earning_account.credit_amount = round_number(
                    self.retained_earning_account.credit_amount) + round_number(trx_data.functional_amount)
            acc_to_close.save()
            self.retained_earning_account.save()

        except Exception as e:
            result = False
            account = Account.objects.get(pk=trx_data.account_id)
            if account:
                status = YEAR_END_CLOSING_ERROR + ACCOUNT_CLOSE_FAILED % (account.code + '-' + account.name, self.year)

        return [result, status]

    def getRetainedEarningAccHistory(self, year, currency):
        retained_earning_acc_hist = None
        try:
            retained_earning_acc_hist = AccountHistory.objects.filter(company_id=self.company_id, is_hidden=False,
                                                                      account_id=self.retained_earning_account.id,
                                                                      period_year=year,
                                                                      source_currency_id=currency) \
                                                        .select_related('account')

            if retained_earning_acc_hist.count() < 14:
                if retained_earning_acc_hist.count() > 0:
                    retained_earning_acc_hist.delete()

                last_day = ""
                for i in range(1, 13):
                    _, num_days = calendar.monthrange(int(year), i)
                    last_day = datetime.strptime(year + '-' + str(i) + '-' + str(num_days), '%Y-%m-%d')
                    self.create_account_history(year, i, last_day, self.retained_earning_account.id, currency, 0,
                                                self.d_company.currency.id, 0)

                self.create_account_history(year, 'ADJ', last_day, self.retained_earning_account.id, currency, 0,
                                            self.d_company.currency.id, 0)
                self.create_account_history(year, 'CLS', last_day, self.retained_earning_account.id, currency, 0,
                                            self.d_company.currency.id, 0)

                retained_earning_acc_hist = AccountHistory.objects.filter(company_id=self.company_id, is_hidden=False,
                                                                          account_id=self.retained_earning_account.id,
                                                                          period_year=year,
                                                                          source_currency_id=currency)

        except:
            pass

        return retained_earning_acc_hist

    def create_account_history(self, year, period, last_day, account_id, source_currency_id, source_net_change,
                               functional_currency_id, func_net_change):
        try:
            account_history = AccountHistory()
            account_history.period_year = year
            account_history.period_month = period
            account_history.period_date = last_day
            account_history.company_id = self.company_id
            account_history.account_id = account_id
            account_history.source_currency_id = source_currency_id
            account_history.source_begin_balance = source_net_change
            account_history.source_net_change = 0
            account_history.source_end_balance = round_number(
                account_history.source_begin_balance) + round_number(account_history.source_net_change)
            account_history.functional_currency_id = functional_currency_id
            account_history.functional_begin_balance = func_net_change
            account_history.functional_net_change = 0
            account_history.functional_end_balance = round_number(
                account_history.functional_begin_balance) + round_number(account_history.functional_net_change)
            account_history.update_by = self.request.user.id
            account_history.create_date = datetime.today()
            account_history.save()
            return True
        except Exception as e:
            return False

    def transferToRetainedEarnings(self, closed_account_data):
        result = True
        last_CLS = None
        source_begin = 0
        source_net = closed_account_data.source_end_balance
        functional_begin = 0
        functional_net = closed_account_data.functional_end_balance
        try:
            self.retained_earning_account_history = self.getRetainedEarningAccHistory(closed_account_data.period_year,
                                                                                      closed_account_data.source_currency_id)
            CLS = self.retained_earning_account_history.filter(period_month='CLS').first()
            if CLS:
                if source_net > 0:
                    CLS.source_debit_amount = round_number(
                        CLS.source_debit_amount) + round_number(math.fabs(source_net))
                else:
                    CLS.source_credit_amount = round_number(
                        CLS.source_credit_amount) + round_number(math.fabs(source_net))
                if functional_net > 0:
                    CLS.functional_debit_amount = round_number(
                        CLS.functional_debit_amount) + round_number(math.fabs(functional_net))
                else:
                    CLS.functional_credit_amount = round_number(
                        CLS.functional_credit_amount) + round_number(math.fabs(functional_net))
                CLS.source_begin_balance += round_number(source_begin)
                CLS.source_net_change = round_number(
                    CLS.source_net_change) + round_number(source_net)
                CLS.source_end_balance = round_number(
                    CLS.source_end_balance) + round_number(source_begin) + round_number(source_net)
                CLS.functional_begin_balance = round_number(
                    CLS.functional_begin_balance) + round_number(functional_begin)
                CLS.functional_net_change = round_number(
                    CLS.functional_net_change) + round_number(functional_net)
                CLS.functional_end_balance = round_number(
                    CLS.functional_end_balance) + round_number(functional_begin) + round_number(functional_net)
                CLS.update_date = datetime.today()
                CLS.update_by = self.request.user.id
            else:
                result = False
            CLS.save()

        except Exception as e:
            result = False

        return result

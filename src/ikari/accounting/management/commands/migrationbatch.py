import calendar
import datetime

from copy import deepcopy

from decimal import Decimal
from accounting.forms import JournalGLForm, BatchInfoForm, ARInvoiceInfoForm, ARReceiptInfoForm
from accounting.models import Batch, Journal
from accounts.models import AccountHistory, AccountCurrency
from companies.models import Company
from transactions.models import Transaction
from utilities.common import generate_batch_number
from utilities.constants import STATUS_TYPE_DICT, INPUT_TYPE_DICT, DOCUMENT_TYPE_DICT, \
    TRANSACTION_TYPES, SOURCE_LEDGER_DICT, BALANCE_TYPE_DICT


def Migrate_GL(company_id, year, month, closing=False):
    try:
        company = Company.objects.get(pk=company_id)
        today = datetime.datetime.today()

        batch = Batch()
        batch_form = BatchInfoForm()

        form = JournalGLForm(company_id=company.id)

        Batch_Entry = batch_form.save(commit=False)

        # Save batch Info
        Batch_Entry.update_by = 1

        Batch_Entry.batch_no = generate_batch_number(company.id, dict(TRANSACTION_TYPES)['GL'])
        Batch_Entry.status = int(STATUS_TYPE_DICT['Open'])
        Batch_Entry.company_id = company.id
        Batch_Entry.is_hidden = False
        Batch_Entry.input_type = INPUT_TYPE_DICT['Manual Entry']
        if closing == True:  # If Closing
            Batch_Entry.description = 'CLOSING ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)
        else:
            Batch_Entry.description = 'Net Change ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)

        Batch_Entry.document_type = DOCUMENT_TYPE_DICT['Undefined']
        Batch_Entry.batch_type = dict(TRANSACTION_TYPES)['GL']  # gl batch type
        Batch_Entry.no_entries = 1  # count of journal entries in this batch
        Batch_Entry.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
        Batch_Entry.currency_id = company.currency_id
        Batch_Entry.create_date = today
        Batch_Entry.batch_date = today
        Batch_Entry.save()

        # Save Journal Info
        GL_Entry = form.save(commit=False)
        GL_Entry.status = int(STATUS_TYPE_DICT['Open'])
        GL_Entry.journal_type = dict(TRANSACTION_TYPES)['GL']
        GL_Entry.update_by = 1
        if closing == True:  # If closing
            GL_Entry.name = 'CLOSING ' + str(year) + '-' + str(month)
        else:
            GL_Entry.name = 'Transaction ' + str(year) + '-' + str(month)
        GL_Entry.company_id = company.id
        GL_Entry.is_hidden = False
        GL_Entry.currency_id = company.currency_id
        if(month == 'CLS'):  # if the month is CLS
            GL_Entry.document_date = str(year) + '-' + '12' + '-' + '31'
            GL_Entry.create_date = str(year) + '-' + '12' + '-' + '01'
            GL_Entry.update_date = str(year) + '-' + '12' + '-' + '01'
        else:
            GL_Entry.document_date = str(year) + '-' + str(month) + '-' + str(calendar.monthrange(int(year), int(month)))[4:6]
            GL_Entry.create_date = str(year) + '-' + str(month) + '-01'
            GL_Entry.update_date = str(year) + '-' + str(month) + '-01'
        GL_Entry.code = '0001'
        GL_Entry.source_type = 'GL-CV'
        GL_Entry.batch_id = Batch_Entry.id
        GL_Entry.save()
        if closing == True:  # If Closing
            trans_list = Transaction.objects.filter(
                is_hidden=False,
                company_id=company_id,
                transaction_date__contains=year + '-' + month,
                source_type='GL-CL'
            ).order_by('account_id')
        else:
            trans_list = Transaction.objects.filter(
                is_hidden=False,
                company_id=company_id,
                transaction_date__contains=year + '-' + month
            ).exclude(source_type='GL-CL').order_by('account_id')

        # Save All Transactions Info
        trans_num = 0
        total_amount_for_journal_credit = 0
        total_tax_credit = 0

        for transaction in trans_list:  # Loop Transaction
            trans = Transaction()
            trans.journal_id = GL_Entry.id
            trans.number = trans_num
            trans.reference = transaction.reference
            trans.description = transaction.description
            trans.account_id = transaction.account_id
            trans.currency_id = transaction.currency_id
            trans.functional_currency_id = company.currency_id
            trans.is_debit_account = transaction.is_debit_account
            trans.is_credit_account = transaction.is_credit_account
            trans.exchange_rate = transaction.exchange_rate
            trans.rate_date = transaction.rate_date
            trans.amount = transaction.amount
            trans.total_amount = transaction.total_amount
            trans.tax_amount = transaction.tax_amount
            trans.functional_amount = transaction.functional_amount
            if trans.is_credit_account == 1:  # The transaction wont be doubled with debit
                total_amount_for_journal_credit += trans.functional_amount
                total_tax_credit += trans.tax_amount
            trans.remark = transaction.remark
            trans.is_hidden = False
            trans.source_type = transaction.source_type
            trans.transaction_date = today
            trans.create_date = today
            trans.update_date = today
            trans.company_id = company.id
            trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                             BALANCE_TYPE_DICT['Debit'])[trans.is_debit_account]
            trans.save()
            trans_num += 1

        # Saving all amount to Batch & Journal
        GL_Entry.total_amount = total_amount_for_journal_credit
        GL_Entry.amount = total_amount_for_journal_credit
        GL_Entry.document_amount = total_amount_for_journal_credit
        GL_Entry.original_amount = total_amount_for_journal_credit
        Batch_Entry.batch_amount = total_amount_for_journal_credit
        GL_Entry.perd_month = month
        GL_Entry.perd_year = year
        GL_Entry.save()
        Batch_Entry.save()

    except OSError as e:
        print(e)


def Migrate_GL_opening(company_id, year, month):
    try:
        company = Company.objects.get(pk=company_id)
        today = datetime.datetime.today()

        batch = Batch()
        batch_form = BatchInfoForm()

        form = JournalGLForm(company_id=company.id)
        form_rv = JournalGLForm(company_id=company.id)
        form_reverse = JournalGLForm(company_id=company.id)

        Batch_Entry = batch_form.save(commit=False)

        month = int(month) - 1

        if month == 0:
            month = 12
            year = int(year) - 1

        # Save batch Info
        Batch_Entry.update_by = 1

        Batch_Entry.batch_no = generate_batch_number(company.id, dict(TRANSACTION_TYPES)['GL'])
        Batch_Entry.status = int(STATUS_TYPE_DICT['Open'])
        Batch_Entry.company_id = company.id
        Batch_Entry.is_hidden = False
        Batch_Entry.input_type = INPUT_TYPE_DICT['Manual Entry']
        Batch_Entry.description = 'OPENING ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)

        Batch_Entry.document_type = DOCUMENT_TYPE_DICT['Undefined']
        Batch_Entry.batch_type = dict(TRANSACTION_TYPES)['GL']  # gl batch type
        Batch_Entry.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
        Batch_Entry.currency_id = company.currency_id
        Batch_Entry.create_date = today
        Batch_Entry.batch_date = today
        Batch_Entry.save()

        # Save Journal Info
        Entry_Number = 1
        GL_Entry = form.save(commit=False)
        GL_Entry.status = int(STATUS_TYPE_DICT['Open'])
        GL_Entry.journal_type = dict(TRANSACTION_TYPES)['GL']
        GL_Entry.update_by = 1
        GL_Entry.name = 'OPENING ' + str(year) + ' - ' + str(month)
        GL_Entry.company_id = company.id
        GL_Entry.is_hidden = False
        GL_Entry.currency_id = company.currency_id
        if(month == 'CLS'):  # if the month is CLS
            GL_Entry.document_date = str(year) + '-' + '12' + '-' + '31'
            GL_Entry.create_date = str(year) + '-' + '12' + '-' + '01'
            GL_Entry.update_date = str(year) + '-' + '12' + '-' + '01'
        else:
            GL_Entry.document_date = str(year) + '-' + str(month) + '-' + str(calendar.monthrange(int(year), int(month)))[4:6]
            GL_Entry.create_date = str(year) + '-' + str(month) + '-01'
            GL_Entry.update_date = str(year) + '-' + str(month) + '-01'
        GL_Entry.code = '000' + str(Entry_Number)
        GL_Entry.source_type = 'GL-CV'
        GL_Entry.batch_id = Batch_Entry.id
        GL_Entry.save()
        Batch_Entry.no_entries += 1  # count of journal entries in this batch
        Entry_Number = 1

        acc_history = AccountHistory.objects.filter(
            is_hidden=False,
            company_id=company_id,
            period_month=month,
            period_year=year,
        ).exclude(
            functional_debit_amount=Decimal(0),
            source_debit_amount=Decimal(0),
            functional_credit_amount=Decimal(0),
            source_credit_amount=Decimal(0),
        ).order_by('account_id', 'source_currency_id', '-source_credit_amount', '-source_debit_amount')

        # Save All Transactions Info
        trans_num = 0
        total_amount_for_journal_credit = 0
        total_tax_credit = 0
        total_amount_for_journal_credit_reverse = 0
        #total_all_journals = 0

        last_acc = []
        last_acc_his = None
        last_acc_trx = None

        # Reset Account History Next Month Current Year
        list_month = []

        for x in range(month + 1, 13):
            list_month.append(x)

        account_history_list_reset = AccountHistory.objects.filter(is_hidden=False, company_id=company_id,
                                                                   account_id__company_id=company_id, period_year=int(year),
                                                                   period_month__in=list_month)

        account_history_list_reset.update(functional_debit_amount=0, functional_credit_amount=0,
                                          source_debit_amount=0, source_credit_amount=0,
                                          source_net_change=0, functional_net_change=0)

        # Reset Account History Next Year Every Month
        list_next_year_month = []

        for x in range(1, 13):
            list_next_year_month.append(x)

        account_history_list_reset_next_year = AccountHistory.objects.filter(is_hidden=False, company_id=company_id,
                                                                             account_id__company_id=company_id, period_year__gt=int(year),
                                                                             period_month__in=list_next_year_month)
        account_history_list_reset_next_year.update(functional_debit_amount=0, functional_credit_amount=0,
                                                    source_debit_amount=0, source_credit_amount=0,
                                                    source_net_change=0, functional_net_change=0)

        for transaction in acc_history:  # Loop Transaction
            skip_sum = False
            trans = Transaction()
            trans.journal_id = GL_Entry.id
            trans.number = trans_num
            trans.account_id = transaction.account_id
            trans.currency_id = transaction.source_currency_id
            trans.functional_currency_id = transaction.functional_currency_id

            # If the transaction is debit
            if transaction.functional_debit_amount <= Decimal(0):
                trans.is_credit_account = True
                trans.is_debit_account = False
                trans.amount = transaction.source_credit_amount
                trans.total_amount = transaction.source_credit_amount
                trans.functional_amount = transaction.functional_credit_amount
            else:  # If the transaction is credit
                trans.is_debit_account = True
                trans.is_credit_account = False
                trans.amount = transaction.source_debit_amount
                trans.total_amount = transaction.source_debit_amount
                trans.functional_amount = transaction.functional_debit_amount
                trans.exchange_rate = Decimal(1.0)

            # Skip the sum if the data has clone
            if skip_sum == False:
                if trans.is_credit_account == True:  # The transaction wont be doubled with debit
                    total_amount_for_journal_credit += trans.functional_amount

            trans.rate_date = transaction.period_date
            trans.tax_amount = Decimal(0.0)
            trans.is_hidden = False
            trans.source_type = 'GL-CV'
            trans.transaction_date = today
            trans.create_date = today
            trans.update_date = today
            trans.company_id = company.id
            trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                             BALANCE_TYPE_DICT['Debit'])[trans.is_debit_account]
            trans.save()
            trans_num += 1

        GL_Entry.total_amount = total_amount_for_journal_credit
        GL_Entry.amount = total_amount_for_journal_credit
        GL_Entry.document_amount = total_amount_for_journal_credit
        GL_Entry.original_amount = total_amount_for_journal_credit
        Batch_Entry.batch_amount = total_amount_for_journal_credit
        GL_Entry.perd_month = month
        GL_Entry.perd_year = year
        GL_Entry.save()
        Batch_Entry.save()

        # Save batch Info
        GL_Reverse_Batch = BatchInfoForm().save(commit=False)
        GL_Reverse_Batch.update_by = 1

        GL_Reverse_Batch.batch_no = generate_batch_number(company.id, dict(TRANSACTION_TYPES)['GL'])
        GL_Reverse_Batch.status = int(STATUS_TYPE_DICT['Open'])
        GL_Reverse_Batch.company_id = company.id
        GL_Reverse_Batch.is_hidden = False
        GL_Reverse_Batch.input_type = INPUT_TYPE_DICT['Manual Entry']
        GL_Reverse_Batch.description = 'REVERSING ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)

        GL_Reverse_Batch.document_type = DOCUMENT_TYPE_DICT['Undefined']
        GL_Reverse_Batch.batch_type = dict(TRANSACTION_TYPES)['GL']  # gl batch type
        GL_Reverse_Batch.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
        GL_Reverse_Batch.currency_id = company.currency_id
        GL_Reverse_Batch.create_date = today
        GL_Reverse_Batch.batch_date = today
        GL_Reverse_Batch.no_entries += 1  # count of journal entries in this batch
        GL_Reverse_Batch.save()

        if month == 12:
            month = 0

        GL_Reverse_Entry = form_reverse.save(commit=False)
        GL_Reverse_Entry.status = int(STATUS_TYPE_DICT['Open'])
        GL_Reverse_Entry.journal_type = dict(TRANSACTION_TYPES)['GL']
        GL_Reverse_Entry.update_by = 1
        GL_Reverse_Entry.name = 'REVERSING ' + str(year) + '-' + str(month)
        GL_Reverse_Entry.company_id = company.id
        GL_Reverse_Entry.is_hidden = False
        GL_Reverse_Entry.currency_id = company.currency_id
        if(month == 'CLS'):  # if the month is CLS
            GL_Reverse_Entry.document_date = str(year) + '-' + '12' + '-' + '31'
            GL_Reverse_Entry.create_date = str(year) + '-' + '12' + '-' + '01'
            GL_Reverse_Entry.update_date = str(year) + '-' + '12' + '-' + '01'
        else:
            GL_Reverse_Entry.document_date = str(year) + '-' + str(int(month) + 1) + '-' + str(1)
            GL_Reverse_Entry.create_date = str(year) + '-' + str(int(month) + 1) + '-01'
            GL_Reverse_Entry.update_date = str(year) + '-' + str(int(month) + 1) + '-01'
        GL_Reverse_Entry.code = '000' + str(Entry_Number)
        GL_Reverse_Entry.source_type = 'GL-RV'
        GL_Reverse_Entry.batch_id = GL_Reverse_Batch.id
        GL_Reverse_Entry.save()

        if month == 0:
            month = 12
            transaction_list = Transaction.objects.filter(company_id=company_id,
                                                          is_hidden=False,
                                                          transaction_date=str(year) + '-' + str(month) + '-' + str(31),
                                                          source_type='GL-RV')
        else:
            transaction_list = Transaction.objects.filter(company_id=company_id,
                                                          is_hidden=False,
                                                          transaction_date=str(year) + '-' + str(int(month) + 1) + '-' + str(1),
                                                          source_type='GL-RV')

        trans_num = 0

        total_amount_for_journal_credit = 0

        for transaction in transaction_list:
            trans_reverse = Transaction()
            trans_reverse.journal_id = GL_Reverse_Entry.id
            trans_reverse.number = trans_num
            trans_reverse.is_credit_account = transaction.is_credit_account
            trans_reverse.is_debit_account = transaction.is_debit_account
            trans_reverse.amount = transaction.amount
            trans_reverse.transaction_date = today
            trans_reverse.create_date = transaction.create_date
            trans_reverse.update_date = transaction.update_date
            trans_reverse.is_hidden = transaction.is_hidden
            trans_reverse.account_id = transaction.account_id
            trans_reverse.company_id = transaction.company_id
            trans_reverse.currency_id = transaction.currency_id
            trans_reverse.tax_amount = transaction.tax_amount
            trans_reverse.total_amount = transaction.total_amount
            trans_reverse.description = transaction.description
            trans_reverse.exchange_rate = transaction.exchange_rate
            if trans_reverse.is_credit_account == True:
                trans_reverse.functional_amount = -transaction.functional_amount
            else:
                trans_reverse.functional_amount = transaction.functional_amount
            if trans_reverse.is_credit_account == True:  # The transaction wont be doubled with debit
                total_amount_for_journal_credit += trans_reverse.functional_amount
            trans_reverse.functional_currency_id = transaction.functional_currency_id
            trans_reverse.rate_date = transaction.rate_date
            trans_reverse.reference = transaction.reference
            trans_reverse.source_type = 'GL-RV'
            trans_reverse.is_tax_include = transaction.is_tax_include
            trans_reverse.is_tax_transaction = transaction.is_tax_transaction
            trans_reverse.functional_balance_type = transaction.functional_balance_type
            trans_reverse.is_report = transaction.is_report
            trans_reverse.is_clear_tax = transaction.is_clear_tax
            trans_reverse.adjustment_amount = transaction.adjustment_amount
            trans_reverse.discount_amount = transaction.discount_amount

            trans_reverse.save()
            trans_num += 1

        if month == 12:
            month = 0

        GL_Reverse_Entry.total_amount = total_amount_for_journal_credit
        GL_Reverse_Entry.amount = total_amount_for_journal_credit
        GL_Reverse_Entry.document_amount = total_amount_for_journal_credit
        GL_Reverse_Entry.original_amount = total_amount_for_journal_credit
        GL_Reverse_Entry.perd_month = int(month) + 1
        GL_Reverse_Entry.perd_year = year
        GL_Reverse_Entry.save()

        Entry_Number += 1

        GL_Reversing_Entry = JournalGLForm(company_id=company.id).save(commit=False)
        GL_Reversing_Entry.status = int(STATUS_TYPE_DICT['Open'])
        GL_Reversing_Entry.journal_type = dict(TRANSACTION_TYPES)['GL']
        GL_Reversing_Entry.update_by = 1
        GL_Reversing_Entry.name = 'REVERSE ' + str(year) + '-' + str(month)
        GL_Reversing_Entry.company_id = company.id
        GL_Reversing_Entry.is_hidden = False
        GL_Reversing_Entry.currency_id = company.currency_id
        if(month == 'CLS'):  # if the month is CLS
            GL_Reversing_Entry.document_date = str(year) + '-' + '12' + '-' + '31'
            GL_Reversing_Entry.create_date = str(year) + '-' + '12' + '-' + '01'
            GL_Reversing_Entry.update_date = str(year) + '-' + '12' + '-' + '01'
        else:
            GL_Reversing_Entry.document_date = str(year) + '-' + str(int(month) + 1) + '-' + str(1)
            GL_Reversing_Entry.create_date = str(year) + '-' + str(int(month) + 1) + '-01'
            GL_Reversing_Entry.update_date = str(year) + '-' + str(int(month) + 1) + '-01'
        GL_Reversing_Entry.code = '000' + str(Entry_Number)
        GL_Reversing_Entry.source_type = 'GL-RV'
        GL_Reversing_Entry.batch_id = GL_Reverse_Batch.id
        GL_Reversing_Entry.save()

        if month == 0:
            month = 12
            transaction_list_reversing = Transaction.objects.filter(company_id=company_id,
                                                                    is_hidden=False,
                                                                    transaction_date=str(year) + '-' + str(month) + '-' + str(31),
                                                                    source_type__in=['AR-GL', 'AP-GL'])
        else:
            transaction_list_reversing = Transaction.objects.filter(company_id=company_id,
                                                                    is_hidden=False,
                                                                    transaction_date=str(year) + '-' + str(int(month) + 1) + '-' + str(1),
                                                                    source_type__in=['AR-GL', 'AP-GL'])

        trans_num = 0

        total_amount_for_journal_credit = 0

        for transaction_reversing in transaction_list_reversing:
            trans_reversing = Transaction()
            trans_reversing.journal_id = GL_Reversing_Entry.id
            trans_reversing.number = trans_num
            trans_reversing.is_credit_account = transaction_reversing.is_credit_account
            trans_reversing.is_debit_account = transaction_reversing.is_debit_account
            trans_reversing.amount = transaction_reversing.amount
            trans_reversing.transaction_reversing_date = today
            trans_reversing.create_date = transaction_reversing.create_date
            trans_reversing.update_date = transaction_reversing.update_date
            trans_reversing.is_hidden = transaction_reversing.is_hidden
            trans_reversing.account_id = transaction_reversing.account_id
            trans_reversing.company_id = transaction_reversing.company_id
            trans_reversing.currency_id = transaction_reversing.currency_id
            trans_reversing.tax_amount = transaction_reversing.tax_amount
            trans_reversing.total_amount = transaction_reversing.total_amount
            trans_reversing.description = transaction_reversing.description
            trans_reversing.exchange_rate = transaction_reversing.exchange_rate
            if trans_reversing.is_credit_account == True:
                trans_reversing.functional_amount = -transaction_reversing.functional_amount
            else:
                trans_reversing.functional_amount = transaction_reversing.functional_amount
            if trans_reversing.is_credit_account == True:  # The transaction_reversing wont be doubled with debit
                total_amount_for_journal_credit += trans_reversing.functional_amount
            trans_reversing.functional_currency_id = transaction_reversing.functional_currency_id
            trans_reversing.rate_date = transaction_reversing.rate_date
            trans_reversing.reference = transaction_reversing.reference
            trans_reversing.source_type = 'GL-RV'
            trans_reversing.is_tax_include = transaction_reversing.is_tax_include
            trans_reversing.is_tax_transaction = transaction_reversing.is_tax_transaction
            trans_reversing.functional_balance_type = transaction_reversing.functional_balance_type
            trans_reversing.is_report = transaction_reversing.is_report
            trans_reversing.is_clear_tax = transaction_reversing.is_clear_tax
            trans_reversing.adjustment_amount = transaction_reversing.adjustment_amount
            trans_reversing.discount_amount = transaction_reversing.discount_amount

            trans_reversing.save()
            trans_num += 1

        GL_Reversing_Entry.total_amount = total_amount_for_journal_credit
        GL_Reversing_Entry.amount = total_amount_for_journal_credit
        GL_Reversing_Entry.document_amount = total_amount_for_journal_credit
        GL_Reversing_Entry.original_amount = total_amount_for_journal_credit
        GL_Reversing_Entry.perd_month = int(month) + 1
        GL_Reversing_Entry.perd_year = year
        GL_Reversing_Entry.save()

        GL_Reverse_Batch.batch_amount = GL_Reversing_Entry.total_amount + GL_Reverse_Entry.total_amount
        GL_Reverse_Batch.save()

        if month == 12:
            month = 1
            year += 1
        else:
            month = int(month) + 1

        # Save batch Info AR Invoice
        Batch_Entry_AR_Invoice = BatchInfoForm().save(commit=False)
        Batch_Entry_AR_Invoice.update_by = 1

        Batch_Entry_AR_Invoice.batch_no = generate_batch_number(company.id, dict(TRANSACTION_TYPES)['AR Invoice'])
        Batch_Entry_AR_Invoice.status = int(STATUS_TYPE_DICT['Open'])
        Batch_Entry_AR_Invoice.company_id = company.id
        Batch_Entry_AR_Invoice.is_hidden = False
        Batch_Entry_AR_Invoice.input_type = INPUT_TYPE_DICT['Manual Entry']
        Batch_Entry_AR_Invoice.description = 'OPENING AR INVOICE ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)

        Batch_Entry_AR_Invoice.document_type = DOCUMENT_TYPE_DICT['Undefined']
        Batch_Entry_AR_Invoice.batch_type = dict(TRANSACTION_TYPES)['AR Invoice']  # gl batch type
        Batch_Entry_AR_Invoice.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
        Batch_Entry_AR_Invoice.currency_id = company.currency_id
        Batch_Entry_AR_Invoice.create_date = today
        Batch_Entry_AR_Invoice.batch_date = today
        Batch_Entry_AR_Invoice.save()

        # Save batch Info AP Invoice
        Batch_Entry_AP_Invoice = BatchInfoForm().save(commit=False)
        Batch_Entry_AP_Invoice.update_by = 1

        Batch_Entry_AP_Invoice.batch_no = generate_batch_number(company.id, dict(TRANSACTION_TYPES)['AP Invoice'])
        Batch_Entry_AP_Invoice.status = int(STATUS_TYPE_DICT['Open'])
        Batch_Entry_AP_Invoice.company_id = company.id
        Batch_Entry_AP_Invoice.is_hidden = False
        Batch_Entry_AP_Invoice.input_type = INPUT_TYPE_DICT['Manual Entry']
        Batch_Entry_AP_Invoice.description = 'OPENING AP INVOICE ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)

        Batch_Entry_AP_Invoice.document_type = DOCUMENT_TYPE_DICT['Undefined']
        Batch_Entry_AP_Invoice.batch_type = dict(TRANSACTION_TYPES)['AP Invoice']  # gl batch type
        Batch_Entry_AP_Invoice.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
        Batch_Entry_AP_Invoice.currency_id = company.currency_id
        Batch_Entry_AP_Invoice.create_date = today
        Batch_Entry_AP_Invoice.batch_date = today
        Batch_Entry_AP_Invoice.save()

        Transaction_revaluation_list = Transaction.objects.filter(is_hidden=0, company_id=company_id, source_type__in=['AR-GL', 'AP-GL'],
                                                                  transaction_date=str(year) + '-' + str(month) + '-' + str(calendar.monthrange(int(year), int(month)))[4:6])

        list_related = []

        for trans_related in Transaction_revaluation_list:
            if trans_related.related_invoice_id not in list_related:
                list_related.append(trans_related.related_invoice_id)

        Transaction_CN_DN = Transaction.objects.filter(is_hidden=0, company_id=company_id, transaction_date__lt=str(year) + '-' + str(month) + '-' + str(1),
                                                       related_invoice_id__in=list_related, journal__document_type__in=[dict(DOCUMENT_TYPE_DICT)['Debit Note'], dict(DOCUMENT_TYPE_DICT)['Credit Note']])

        for trans_cn_dn in Transaction_CN_DN:
            if trans_cn_dn.journal_id not in list_related:
                list_related.append(trans_cn_dn.journal_id)

        Revaluation_related_journal_list = Journal.objects.filter(is_hidden=0, company_id=company_id,
                                                                  id__in=list_related, document_date__lt=str(year) + '-' + str(month) + '-' + str(1))

        list_journal_id = {}

        AR_Number = 1
        AP_Number = 1

        for journal_invoice in Revaluation_related_journal_list:
            if journal_invoice.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                journal_invoice_copy = deepcopy(journal_invoice)
                journal_invoice_copy.pk = None
                journal_invoice_copy.batch_id = Batch_Entry_AR_Invoice.id
                journal_invoice_copy.code = AR_Number
                journal_invoice_copy.save()
                AR_Number += 1
                list_journal_id[journal_invoice.id] = journal_invoice_copy.id
            if journal_invoice.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                journal_invoice_copy = deepcopy(journal_invoice)
                journal_invoice_copy.pk = None
                journal_invoice_copy.batch_id = Batch_Entry_AP_Invoice.id
                journal_invoice_copy.code = AP_Number
                journal_invoice_copy.save()
                AP_Number += 1
                list_journal_id[journal_invoice.id] = journal_invoice_copy.id

        Batch_Entry_AR_Invoice.no_entries = AR_Number - 1
        Batch_Entry_AP_Invoice.no_entries = AP_Number - 1
        Batch_Entry_AR_Invoice.save()
        Batch_Entry_AP_Invoice.save()

        Journal_transaction_list = Transaction.objects.filter(is_hidden=0, company_id=company_id, journal_id__in=list(list_journal_id))

        for journal_transaction in Journal_transaction_list:
            journal_transaction_copy = deepcopy(journal_transaction)
            journal_transaction_copy.pk = None
            journal_transaction_copy.journal_id = list_journal_id[journal_transaction_copy.journal_id]
            if journal_transaction_copy.related_invoice_id is not None:
                journal_transaction_copy.related_invoice_id = list_journal_id[journal_transaction_copy.related_invoice_id]
            journal_transaction_copy.save()

        # Payment Batch
        Transaction_receipt = Transaction.objects.filter(is_hidden=0, company_id=company_id, related_invoice_id__in=list(list_journal_id),
                                                         journal__journal_type__in=[dict(TRANSACTION_TYPES)['AR Receipt'],
                                                                                    dict(TRANSACTION_TYPES)['AP Payment']],
                                                         transaction_date__lt=str(year) + '-' + str(month) + '-' + str(1))

        list_journal_receipt_id = []

        for transaction_receipt_id in Transaction_receipt:
            if transaction_receipt_id.journal_id not in list_journal_receipt_id:
                list_journal_receipt_id.append(transaction_receipt_id.journal_id)

        if Transaction_receipt.count() > 0:
            # Save batch Info AR Receipt
            Batch_Entry_AR_Receipt = BatchInfoForm().save(commit=False)
            Batch_Entry_AR_Receipt.update_by = 1
            Batch_Entry_AR_Receipt.batch_no = generate_batch_number(company.id, dict(TRANSACTION_TYPES)['AR Receipt'])
            Batch_Entry_AR_Receipt.status = int(STATUS_TYPE_DICT['Open'])
            Batch_Entry_AR_Receipt.company_id = company.id
            Batch_Entry_AR_Receipt.is_hidden = False
            Batch_Entry_AR_Receipt.input_type = INPUT_TYPE_DICT['Manual Entry']
            Batch_Entry_AR_Receipt.description = 'OPENING AR RECEIPT ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)
            Batch_Entry_AR_Receipt.document_type = DOCUMENT_TYPE_DICT['Undefined']
            Batch_Entry_AR_Receipt.batch_type = dict(TRANSACTION_TYPES)['AR Receipt']  # gl batch type
            Batch_Entry_AR_Receipt.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
            Batch_Entry_AR_Receipt.currency_id = company.currency_id
            Batch_Entry_AR_Receipt.create_date = today
            Batch_Entry_AR_Receipt.batch_date = today
            Batch_Entry_AR_Receipt.save()

            # Save batch Info AP Payment
            Batch_Entry_AP_Payment = BatchInfoForm().save(commit=False)
            Batch_Entry_AP_Payment.update_by = 1
            Batch_Entry_AP_Payment.batch_no = generate_batch_number(company.id, dict(TRANSACTION_TYPES)['AP Payment'])
            Batch_Entry_AP_Payment.status = int(STATUS_TYPE_DICT['Open'])
            Batch_Entry_AP_Payment.company_id = company.id
            Batch_Entry_AP_Payment.is_hidden = False
            Batch_Entry_AP_Payment.input_type = INPUT_TYPE_DICT['Manual Entry']
            Batch_Entry_AP_Payment.description = 'OPENING AP PAYMENT ' + str(company.name) + ' ' + str(year) + ' - ' + str(month)
            Batch_Entry_AP_Payment.document_type = DOCUMENT_TYPE_DICT['Undefined']
            Batch_Entry_AP_Payment.batch_type = dict(TRANSACTION_TYPES)['AP Payment']  # gl batch type
            Batch_Entry_AP_Payment.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
            Batch_Entry_AP_Payment.currency_id = company.currency_id
            Batch_Entry_AP_Payment.create_date = today
            Batch_Entry_AP_Payment.batch_date = today
            Batch_Entry_AP_Payment.save()

            Journal_receipt = Journal.objects.filter(is_hidden=0, company_id=company_id, id__in=list_journal_receipt_id)
            AR_Number = 1
            AP_Number = 1

            list_journal_new_id = {}

            for journal_receipt_copy in Journal_receipt:
                if journal_receipt_copy.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                    journal_receipt_new = deepcopy(journal_receipt_copy)
                    journal_receipt_new.id = None
                    journal_receipt_new.batch_id = Batch_Entry_AR_Receipt.id
                    journal_receipt_new.code = AR_Number
                    journal_receipt_new.save()
                    AR_Number += 1
                    list_journal_new_id[journal_receipt_copy.id] = journal_receipt_new.id
                if journal_receipt_copy.journal_type == dict(TRANSACTION_TYPES)['AP Payment']:
                    journal_receipt_new = deepcopy(journal_receipt_copy)
                    journal_receipt_new.id = None
                    journal_receipt_new.batch_id = Batch_Entry_AP_Payment.id
                    journal_receipt_new.code = AP_Number
                    journal_receipt_new.save()
                    AP_Number += 1
                    list_journal_new_id[journal_receipt_copy.id] = journal_receipt_new.id

            Batch_Entry_AR_Receipt.no_entries = AR_Number - 1
            Batch_Entry_AP_Payment.no_entries = AP_Number - 1
            Batch_Entry_AR_Receipt.save()
            Batch_Entry_AP_Payment.save()

            Journal_transaction_receipt_list = Transaction.objects.filter(is_hidden=0, company_id=company_id, journal_id__in=list(list_journal_new_id))

            for journal_transaction_receipt in Journal_transaction_receipt_list:
                journal_transaction_receipt_copy = deepcopy(journal_transaction_receipt)
                journal_transaction_receipt_copy.pk = None
                journal_transaction_receipt_copy.journal_id = list_journal_new_id[journal_transaction_receipt_copy.journal_id]
                if journal_transaction_receipt_copy.related_invoice_id in list(list_journal_id):
                    journal_transaction_receipt_copy.related_invoice_id = list_journal_id[journal_transaction_receipt.related_invoice_id]

                journal_transaction_receipt_copy.save()

        # Update next month related invoice id
        Transaction_receipt_next_month = Transaction.objects.filter(is_hidden=0, company_id=company_id, related_invoice_id__in=list(list_journal_id),
                                                                    journal__journal_type__in=[dict(TRANSACTION_TYPES)['AR Receipt'],
                                                                                               dict(TRANSACTION_TYPES)['AP Payment']],
                                                                    transaction_date__gte=str(year) + '-' + str(month) + '-' + str(1))

        for transaction_next_month in Transaction_receipt_next_month:
            if transaction_next_month.related_invoice_id in list(list_journal_id):
                transaction_next_month.related_invoice_id = list_journal_id[transaction_next_month.related_invoice_id]
                transaction_next_month.save()

    except OSError as e:
        print(e)

import datetime
import calendar
import logging
import math
import traceback
import re
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.db import transaction as transactionlib
from accounting.forms import JournalGLForm, BatchInfoForm, APInvoiceInfoForm, ARInvoiceInfoForm, \
    ARReceiptInfoForm, APPaymentInfoForm
from accounting.models import Batch, RecurringBatch, RecurringEntry, RecurringEntryDetail, Journal, FiscalCalendar
from companies.models import Company
from accounts.models import AccountHistory
from accounts.models import Account
from currencies.models import ExchangeRate
from transactions.models import Transaction
from utilities.common import round_number, generate_batch_number, update_next_doc_number, AR_AP_generate_document_number
from utilities.constants import STATUS_TYPE_DICT, INPUT_TYPE_DICT, DOCUMENT_TYPE_DICT, \
    SOURCE_LEDGER_DICT, BALANCE_TYPE_DICT, RECURRING_PERIOD_DICT, TRANSACTION_TYPES, PAYMENT_TRANSACTION_TYPES_DICT, \
    RECEIPT_TRANSACTION_TYPES_DICT


def runRecurringTask():
    today = datetime.date.today()
    rec_batch_list = RecurringBatch.objects.filter(is_hidden=0)
    for rec_batch in rec_batch_list:
        try:
            rec_entry_list = RecurringEntry.objects.filter(
                is_hidden=0, batch_id=rec_batch.id, 
                is_active=1, is_expire=0).exclude(schedule_id__isnull=True)
            if rec_entry_list.exists():
                # first_rec_entry = rec_entry_list.first()
                # today = first_rec_entry.run_date + datetime.timedelta(1)
                batch = None
                for rec_entry in rec_entry_list:
                    try:
                        if rec_entry.expire_date and (today - rec_entry.expire_date).days >= 0:
                            continue

                        print("Task called!!", "rec_entry", rec_entry.id)
                        company = rec_entry.company
                        schedule = rec_entry.schedule
                        if RECURRING_PERIOD_DICT['Daily'] == schedule.recur_period:
                            frequency = schedule.daily_frequency
                            if (today - rec_entry.run_date).days >= frequency:
                                if not batch:
                                    batch = get_batch(rec_batch, today)
                                create_RE_entry(company, rec_entry, batch)
                        if RECURRING_PERIOD_DICT['Weekly'] == schedule.recur_period:
                            frequency = schedule.weekly_frequency
                            freq_day = schedule.frequency_weekday_index
                            curr_weekday = today.weekday()
                            if freq_day == curr_weekday and (today - rec_entry.run_date).days >= frequency * 7:
                                if not batch:
                                    batch = get_batch(rec_batch, today)
                                create_RE_entry(company, rec_entry, batch)
                        if RECURRING_PERIOD_DICT['Monthly'] == schedule.recur_period:
                            frequency = schedule.monthly_frequency
                            freq_day = schedule.frequency_date + 1
                            if month_day_validate(freq_day, today) and (
                                (rec_entry.run_date.month == rec_entry.start_date.month) and ((
                                    today - rec_entry.run_date).days >= 1) or abs(today.month - rec_entry.run_date.month) >= frequency):
                                if not batch:
                                    batch = get_batch(rec_batch, today)
                                create_RE_entry(company, rec_entry, batch)
                        if RECURRING_PERIOD_DICT['Yearly'] == schedule.recur_period:
                            freq_month = schedule.frequency_month + 1
                            freq_day = schedule.frequency_date + 1
                            if month_day_validate(freq_day, today) and freq_month == today.month and today.year - rec_entry.run_date.year >= 1:
                                if not batch:
                                    batch = get_batch(rec_batch, today)
                                create_RE_entry(company, rec_entry, batch)

                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)


def month_day_validate(freq_day, today):
    if freq_day == today.day:
        return True
    else:
        if int(today.month) == 2:
            if int(today.day) in [28, 29] and freq_day > int(today.day):
                return True
        elif int(today.month) in [4, 6, 9, 11]:
            if int(today.day) in [30] and freq_day > int(today.day):
                return True
    return False


def create_RE_entry(company, rec_entry, batch):
    if rec_entry.journal_type == dict(TRANSACTION_TYPES)['AP Invoice']:
        create_AP_entry(company, rec_entry, batch)
    elif rec_entry.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']:
        create_AR_entry(company, rec_entry, batch)
    elif rec_entry.journal_type == dict(TRANSACTION_TYPES)['AP Payment']:
        create_AP_Payment_entry(company, rec_entry, batch)
    elif rec_entry.journal_type == dict(TRANSACTION_TYPES)['AR Receipt']:
        create_AR_Receipt_entry(company, rec_entry, batch)
    elif rec_entry.journal_type == dict(TRANSACTION_TYPES)['GL']:
        create_GL_entry(company, rec_entry, batch)


def get_batch(rec_batch, today):
    try:
        with transactionlib.atomic():
            company = rec_batch.company
            batch_form = BatchInfoForm()
            Batch_Entry = batch_form.save(commit=False)

            # Save Batch Info
            Batch_Entry.batch_no = generate_batch_number(
                company.id, rec_batch.batch_type)
            Batch_Entry.status = int(STATUS_TYPE_DICT['Open'])
            Batch_Entry.company_id = company.id
            Batch_Entry.is_hidden = False
            Batch_Entry.input_type = INPUT_TYPE_DICT['Generated']
            Batch_Entry.description = rec_batch.description
            Batch_Entry.posting_sequence = 0
            Batch_Entry.batch_type = rec_batch.batch_type
            Batch_Entry.no_entries = 0  # count of journal entries in this batch
            Batch_Entry.batch_amount = rec_batch.batch_amount
            if rec_batch.batch_type == dict(TRANSACTION_TYPES)['GL']:
                Batch_Entry.document_type = DOCUMENT_TYPE_DICT['Undefined']
                Batch_Entry.source_ledger = SOURCE_LEDGER_DICT['General Ledger']
            elif rec_batch.batch_type == dict(TRANSACTION_TYPES)['AP Invoice']:
                Batch_Entry.document_type = DOCUMENT_TYPE_DICT['Invoice']
                Batch_Entry.source_ledger = SOURCE_LEDGER_DICT['Account Payable']
            elif rec_batch.batch_type == dict(TRANSACTION_TYPES)['AP Payment']:
                Batch_Entry.document_type = DOCUMENT_TYPE_DICT['Invoice']
                Batch_Entry.source_ledger = SOURCE_LEDGER_DICT['Account Payable']
            elif rec_batch.batch_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                Batch_Entry.document_type = DOCUMENT_TYPE_DICT['Invoice']
                Batch_Entry.source_ledger = SOURCE_LEDGER_DICT['Account Receivable']
            elif rec_batch.batch_type == dict(TRANSACTION_TYPES)['AR Receipt']:
                Batch_Entry.document_type = DOCUMENT_TYPE_DICT['Invoice']
                Batch_Entry.source_ledger = SOURCE_LEDGER_DICT['Account Receivable']

            Batch_Entry.currency_id = company.currency_id

            Batch_Entry.create_date = today
            Batch_Entry.batch_date = today
            Batch_Entry.save()

            return Batch_Entry

    except Exception as e:
        print(e)


def create_GL_entry(company, rec_entry, batch):
    try:
        with transactionlib.atomic():
            today = datetime.date.today()
            form = JournalGLForm(company_id=company.id)
            GL_Entry = form.save(commit=False)
            # Save Journal Info
            GL_Entry.total_amount = rec_entry.total_amount
            GL_Entry.status = int(STATUS_TYPE_DICT['Open'])
            GL_Entry.journal_type = dict(TRANSACTION_TYPES)['GL']
            GL_Entry.company_id = company.id
            GL_Entry.is_hidden = False
            GL_Entry.currency_id = company.currency_id
            GL_Entry.document_date = today
            GL_Entry.code = rec_entry.code
            GL_Entry.name = rec_entry.name
            GL_Entry.batch_id = batch.id
            GL_Entry.source_type = rec_entry.source_type
            GL_Entry.exchange_rate = 1
            if rec_entry.is_auto_reverse:
                GL_Entry.is_auto_reverse = rec_entry.is_auto_reverse
                GL_Entry.reverse_to_period = rec_entry.reverse_to_period
                GL_Entry.reverse_to_period_val = rec_entry.reverse_to_period_val
            else:
                GL_Entry.is_auto_reverse = rec_entry.is_auto_reverse
                GL_Entry.reverse_to_period = None
                GL_Entry.reverse_to_period_val = None
            
            fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
            if fsc_calendar:
                year = fsc_calendar.fiscal_year
                month = fsc_calendar.period
            else:
                year = today.year
                month = today.month
            GL_Entry.perd_month = month
            GL_Entry.perd_year = year
            GL_Entry.update_by = rec_entry.update_by
            GL_Entry.save()

            # Save Transactions
            trxnum = 1
            transaction_list = RecurringEntryDetail.objects.filter(
                company_id=company.id, rec_entry_id=rec_entry.id, is_hidden=0)
            if transaction_list != None:
                for transaction in transaction_list:
                    trans = Transaction()
                    trans.journal_id = GL_Entry.id
                    trans.number = trxnum
                    trans.reference = transaction.reference
                    trans.description = transaction.description
                    trans.account_id = transaction.account_id
                    trans.currency_id = transaction.currency_id
                    trans.functional_currency_id = company.currency_id
                    trans.is_debit_account = transaction.is_debit_account
                    trans.is_credit_account = transaction.is_credit_account
                    if transaction.is_debit_account:
                        trans.amount = transaction.source_debit
                        trans.total_amount = transaction.source_debit
                        trans.functional_amount = transaction.func_debit
                    else:
                        trans.amount = transaction.source_credit
                        trans.total_amount = transaction.source_credit
                        trans.functional_amount = transaction.func_credit
                    trans.exchange_rate = transaction.exchange_rate
                    trans.remark = transaction.comment
                    trans.is_hidden = False
                    trans.transaction_date = today
                    # trans.create_date = today
                    # trans.update_date = today
                    # trans.update_by = request.user.id
                    trans.company_id = company.id
                    trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                    BALANCE_TYPE_DICT['Debit'])[trans.is_debit_account]
                    trans.save()
                    trxnum += 1
                    refer = transaction.reference

            # create '5041 rounding', if total_debit <> todal_credit
            total_func_debit = total_func_credit = 0
            transaction_list = Transaction.objects.filter(company_id=company.id, is_hidden=0,
                                                        journal_id=GL_Entry.id)
            trx_debits = transaction_list.filter(is_debit_account=1)
            trx_debits = transaction_list.filter(is_debit_account=1)
            for trx_debit in trx_debits:
                total_func_debit += round_number(trx_debit.functional_amount)
            trx_credits = transaction_list.filter(is_credit_account=1)
            for trx_credit in trx_credits:
                total_func_credit += round_number(trx_credit.functional_amount)

            if round_number(total_func_credit) != round_number(total_func_debit):
                foreign_exchange_amount = round_number(total_func_debit) - round_number(total_func_credit)

                try:
                    if rec_entry.account_set and rec_entry.account_set.revaluation_rounding_id:
                        foreign_exchange_account = Account.objects.get(
                            pk=rec_entry.account_set.revaluation_rounding_id)
                    else:
                        foreign_exchange_account = Account.objects.filter(
                            Q(name__icontains='FOREIGN') & Q(name__icontains='EXCHANGE')).first()

                    gl_exchange = Transaction()
                    gl_exchange.reference = refer
                    gl_exchange.description = str(GL_Entry.name)
                    gl_exchange.journal_id = GL_Entry.id
                    gl_exchange.account_id = foreign_exchange_account.id if foreign_exchange_account else None
                    gl_exchange.company_id = company.id
                    gl_exchange.currency_id = GL_Entry.currency_id
                    gl_exchange.source_type = GL_Entry.source_type
                    gl_exchange.exchange_rate = GL_Entry.exchange_rate
                    gl_exchange.functional_currency_id = company.currency_id
                    gl_exchange.is_debit_account = (True, False)[foreign_exchange_amount > 0]
                    gl_exchange.is_credit_account = (False, True)[foreign_exchange_amount > 0]
                    gl_exchange.functional_amount = math.fabs(foreign_exchange_amount)
                    gl_exchange.functional_balance_type = (BALANCE_TYPE_DICT['Debit'],
                                                        BALANCE_TYPE_DICT['Credit'])[foreign_exchange_amount > 0]
                    gl_exchange.save()

                except Exception as e:
                    print(e)
                    print("Revaluation account couldn't be retrieved!!")
                    transactionlib.set_rollback(True)
                    logging.error(traceback.format_exc())

            batch.no_entries = batch.no_entries + 1
            batch.save()

            # update run date
            rec_entry.run_date = today
            rec_entry.save()

    except OSError as e:
        print(e)


def create_AP_entry(company, rec_entry, batch):
    try:
        today = datetime.date.today()
        form = APInvoiceInfoForm(company_id=company.id)
        AP_Entry = form.save(commit=False)
        # Save Journal Info
        AP_Entry.name = rec_entry.name if rec_entry.name else ''
        AP_Entry.amount = rec_entry.amount
        AP_Entry.tax_amount = rec_entry.tax_amount
        AP_Entry.total_amount = rec_entry.total_amount
        AP_Entry.status = int(STATUS_TYPE_DICT['Open'])
        AP_Entry.journal_type = dict(TRANSACTION_TYPES)['AP Invoice']
        AP_Entry.outstanding_amount = rec_entry.total_amount
        AP_Entry.company_id = company.id
        AP_Entry.is_hidden = False
        AP_Entry.currency_id = rec_entry.supplier.currency_id
        AP_Entry.supplier = rec_entry.supplier
        AP_Entry.account_set = rec_entry.account_set
        AP_Entry.document_type = rec_entry.document_type
        AP_Entry.document_date = today
        AP_Entry.posting_date = today
        AP_Entry.code = rec_entry.code
        AP_Entry.document_amount = rec_entry.document_amount
        AP_Entry.is_manual_doc = rec_entry.is_manual_doc
        if rec_entry.is_manual_doc:
            AP_Entry.document_number = rec_entry.document_number
        else:
            AP_Entry.document_number = AR_AP_generate_document_number(
                company.id,
                dict(TRANSACTION_TYPES)['AP Invoice'])
        AP_Entry.batch_id = batch.id
        if rec_entry.supplier_id:
            try:
                AP_Entry.due_date = today + datetime.timedelta(int(re.sub('\D', '', rec_entry.supplier.term_days)))
            except:
                AP_Entry.due_date = today + relativedelta(months=1)

        AP_Entry.orig_exch_rate = rec_entry.orig_exch_rate if rec_entry.orig_exch_rate != '' else None
        if rec_entry.orig_exch_rate_fk:
            AP_Entry.orig_exch_rate_fk_id = rec_entry.orig_exch_rate_fk.id
        
        fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
        if fsc_calendar:
            year = fsc_calendar.fiscal_year
            month = fsc_calendar.period
        else:
            year = today.year
            month = today.month
        AP_Entry.perd_month = month
        AP_Entry.perd_year = year

        from_currency = rec_entry.supplier.currency_id
        to_currency = company.currency_id
        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                    from_currency_id=from_currency,
                                                    to_currency_id=to_currency,
                                                    exchange_date__lte=today,
                                                    flag='ACCOUNTING').order_by('exchange_date').last()
        if not exchange_rate:
            if from_currency == to_currency:
                AP_Entry.exchange_rate = 1
                AP_Entry.exchange_rate_fk_id = None
            else:
                try:
                    transactionlib.rollback()
                except:
                    pass
        else:
            AP_Entry.exchange_rate = exchange_rate.rate
            AP_Entry.exchange_rate_fk_id = exchange_rate.id
            if exchange_rate.exchange_date.month != today.month:
                AP_Entry.has_old_rate == True
        AP_Entry.update_by = rec_entry.update_by
        AP_Entry.save()

        # doc_number = update_next_doc_number(company.id, AP_Entry.document_number, dict(TRANSACTION_TYPES)['AP Invoice'])

        # Save Transactions
        trxnum = 1
        transaction_list = RecurringEntryDetail.objects.filter(
            company_id=company.id, rec_entry_id=rec_entry.id)
        if transaction_list != None:
            for transaction in transaction_list:
                trans = Transaction()
                trans.transaction_date = today
                trans.journal_id = AP_Entry.id
                trans.number = trxnum
                trans.distribution_code_id = transaction.distribution_code_id if transaction.distribution_code_id else None
                trans.reference = transaction.reference
                trans.description = transaction.description
                trans.remark = transaction.remark
                trans.account_id = transaction.account_id
                trans.amount = transaction.amount
                trans.base_tax_amount = transaction.amount
                trans.tax_amount = transaction.tax_amount
                trans.total_amount = transaction.total_amount
                trans.tax_id = transaction.tax_id
                trans.currency_id = rec_entry.currency.id
                # trans.order_id = rec_entry.order_id if rec_entry.order else None
                trans.is_debit_account = (True, False)[rec_entry.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
                trans.is_credit_account = (False, True)[rec_entry.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
                trans.is_tax_include = transaction.is_tax_include
                trans.is_tax_transaction = transaction.is_tax_transaction
                trans.is_manual_tax_input = transaction.is_manual_tax_input
                if transaction.related_invoice:
                    trans.related_invoice = transaction.related_invoice
                
                trans.exchange_rate = AP_Entry.exchange_rate
                trans.functional_currency_id = company.currency_id
                trans.functional_amount = float(
                    trans.total_amount) * float(trans.exchange_rate)

                if exchange_rate:
                    trans.rate_date = exchange_rate.exchange_date
                else:
                    trans.rate_date = AP_Entry.document_date
                # trans.create_date = today
                # trans.update_date = today
                # trans.update_by = request.user.id
                trans.company_id = company.id
                trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                 BALANCE_TYPE_DICT['Debit'])[trans.is_debit_account]
                trans.save()
                trxnum += 1

        # update run date
        rec_entry.run_date = today
        rec_entry.save()

        batch.no_entries = batch.no_entries + 1
        batch.save()

    except OSError as e:
        print(e)


def create_AR_entry(company, rec_entry, batch):
    try:
        with transactionlib.atomic():
            today = datetime.date.today()
            form = ARInvoiceInfoForm(company_id=company.id)
            AR_Entry = form.save(commit=False)
            # Save Journal Info
            AR_Entry.name = rec_entry.name if rec_entry.name else ''
            AR_Entry.amount = rec_entry.amount
            AR_Entry.tax_amount = rec_entry.tax_amount
            AR_Entry.total_amount = rec_entry.total_amount
            AR_Entry.status = int(STATUS_TYPE_DICT['Open'])
            AR_Entry.journal_type = dict(TRANSACTION_TYPES)['AR Invoice']
            AR_Entry.outstanding_amount = rec_entry.total_amount
            AR_Entry.company_id = company.id
            AR_Entry.is_hidden = False
            AR_Entry.currency_id = rec_entry.customer.currency_id
            AR_Entry.customer = rec_entry.customer
            AR_Entry.account_set = rec_entry.account_set
            AR_Entry.document_type = rec_entry.document_type
            AR_Entry.document_date = today
            AR_Entry.posting_date = today
            # AR_Entry.create_date = today
            # AR_Entry.update_date = today
            AR_Entry.code = rec_entry.code
            AR_Entry.document_amount = rec_entry.document_amount
            AR_Entry.is_manual_doc = rec_entry.is_manual_doc
            if rec_entry.is_manual_doc:
                AR_Entry.document_number = rec_entry.document_number
            else:
                AR_Entry.document_number = AR_AP_generate_document_number(
                    company.id, dict(TRANSACTION_TYPES)['AR Invoice'])
            AR_Entry.batch_id = batch.id
            if rec_entry.customer_id:
                AR_Entry.due_date = today + datetime.timedelta(
                    int(rec_entry.customer.payment_term)) if rec_entry.customer.payment_term else None

            AR_Entry.orig_exch_rate = rec_entry.orig_exch_rate if rec_entry.orig_exch_rate != '' else None
            if rec_entry.orig_exch_rate_fk:
                AR_Entry.orig_exch_rate_fk_id = rec_entry.orig_exch_rate_fk.id
            
            fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
            if fsc_calendar:
                year = fsc_calendar.fiscal_year
                month = fsc_calendar.period
            else:
                year = today.year
                month = today.month
            AR_Entry.perd_month = month
            AR_Entry.perd_year = year

            from_currency = rec_entry.customer.currency_id
            to_currency = company.currency_id
            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                        from_currency_id=from_currency,
                                                        to_currency_id=to_currency,
                                                        exchange_date__lte=today,
                                                        flag='ACCOUNTING').order_by('exchange_date').last()
            if not exchange_rate:
                if from_currency == to_currency:
                    AR_Entry.exchange_rate = 1
                    AR_Entry.exchange_rate_fk_id = None
                else:
                    try:
                        transactionlib.rollback()
                    except:
                        pass
            else:
                AR_Entry.exchange_rate = exchange_rate.rate
                AR_Entry.exchange_rate_fk_id = exchange_rate.id
                if exchange_rate.exchange_date.month != today.month:
                    AR_Entry.has_old_rate == True
            AR_Entry.update_by = rec_entry.update_by
            AR_Entry.save()

            # doc_number = update_next_doc_number(company.id, AR_Entry.document_number, dict(TRANSACTION_TYPES)['AR Invoice'])

            # Save Transactions
            trxnum = 1
            transaction_list = RecurringEntryDetail.objects.filter(company_id=company.id, rec_entry_id=rec_entry.id)
            if transaction_list != None:
                for transaction in transaction_list:
                    trans = Transaction()
                    trans.journal_id = AR_Entry.id
                    trans.number = trxnum
                    trans.distribution_code_id = transaction.distribution_code_id if transaction.distribution_code_id else None
                    trans.reference = transaction.reference
                    trans.description = transaction.description
                    trans.remark = transaction.remark
                    trans.account_id = transaction.account_id
                    trans.amount = transaction.amount
                    trans.base_tax_amount = transaction.amount
                    trans.tax_amount = transaction.tax_amount
                    trans.total_amount = transaction.total_amount
                    trans.tax_id = transaction.tax_id
                    trans.currency_id = rec_entry.currency.id
                    trans.is_debit_account = (True, False)[rec_entry.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
                    trans.is_credit_account = (False, True)[rec_entry.document_type == DOCUMENT_TYPE_DICT['Credit Note']]
                    trans.is_tax_include = transaction.is_tax_include
                    trans.is_tax_transaction = transaction.is_tax_transaction
                    trans.is_manual_tax_input = transaction.is_manual_tax_input
                    if transaction.related_invoice:
                        trans.related_invoice = transaction.related_invoice
                    
                    trans.exchange_rate = AR_Entry.exchange_rate
                    trans.functional_currency_id = company.currency_id
                    if exchange_rate:
                        trans.rate_date = exchange_rate.exchange_date
                    else:
                        trans.rate_date = AR_Entry.document_date
                    trans.functional_amount = float(
                        trans.total_amount) * float(trans.exchange_rate)

                    trans.transaction_date = today
                    # trans.create_date = today
                    # trans.update_date = today
                    trans.company_id = company.id
                    trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                    BALANCE_TYPE_DICT['Debit'])[trans.is_debit_account]
                    trans.save()
                    trxnum += 1

            # update run date
            rec_entry.run_date = today
            rec_entry.save()

            batch.no_entries = batch.no_entries + 1
            batch.save()

    except OSError as e:
        print(e)


def create_AP_Payment_entry(company, rec_entry, batch):
    try:
        today = datetime.date.today()
        form = APPaymentInfoForm(company_id=company.id)
        AP_Payment_entry = form.save(commit=False)
        # Save Journal Info
        if rec_entry.transaction_type == PAYMENT_TRANSACTION_TYPES_DICT['Payment']:
            AP_Payment_entry.batch_id = batch.id
            AP_Payment_entry.name = rec_entry.name if rec_entry.name else ''
            AP_Payment_entry.code = rec_entry.code
            AP_Payment_entry.transaction_type = rec_entry.transaction_type
            AP_Payment_entry.status = int(STATUS_TYPE_DICT['Open'])
            AP_Payment_entry.journal_type = dict(TRANSACTION_TYPES)['AP Payment']
            AP_Payment_entry.document_type = DOCUMENT_TYPE_DICT['Payment']
            AP_Payment_entry.company_id = company.id
            AP_Payment_entry.is_hidden = False
            AP_Payment_entry.bank_id = rec_entry.bank_id
            AP_Payment_entry.currency_id = rec_entry.currency_id
            AP_Payment_entry.payment_code_id = rec_entry.payment_code_id
            AP_Payment_entry.payment_check_number = rec_entry.payment_check_number
            AP_Payment_entry.reference = rec_entry.reference
            AP_Payment_entry.transaction_type = rec_entry.transaction_type
            AP_Payment_entry.supplier = rec_entry.supplier
            AP_Payment_entry.account_set = rec_entry.account_set
            AP_Payment_entry.document_date = today
            AP_Payment_entry.posting_date = today
            AP_Payment_entry.is_manual_doc = rec_entry.is_manual_doc
            AP_Payment_entry.original_currency_id = rec_entry.original_currency_id
            AP_Payment_entry.payment_currency_id = rec_entry.payment_currency_id

            fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
            if fsc_calendar:
                year = fsc_calendar.fiscal_year
                month = fsc_calendar.period
            else:
                year = today.year
                month = today.month
            AP_Payment_entry.perd_month = month
            AP_Payment_entry.perd_year = year
            AP_Payment_entry.document_number = AR_AP_generate_document_number(
                    company.id,
                    dict(TRANSACTION_TYPES)['AP Payment'])
            AP_Payment_entry.save()

            from_currency = rec_entry.bank.currency_id
            to_currency = company.currency_id

            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                        from_currency_id=from_currency,
                                                        to_currency_id=to_currency,
                                                        exchange_date__lte=AP_Payment_entry.document_date,
                                                        flag='ACCOUNTING').order_by('exchange_date').last()
            if not exchange_rate:
                if from_currency == to_currency:
                    AP_Payment_entry.exchange_rate = 1
                    AP_Payment_entry.exchange_rate_fk_id = None
                else:
                    try:
                        transactionlib.rollback()
                    except:
                        pass
            else:
                AP_Payment_entry.exchange_rate = exchange_rate.rate
                AP_Payment_entry.exchange_rate_fk_id = exchange_rate.id
                if exchange_rate.exchange_date.month != today.month:
                    AP_Payment_entry.has_old_rate == True
            AP_Payment_entry.save()

            transaction_list = RecurringEntryDetail.objects.filter(company_id=company.id, rec_entry_id=rec_entry.id)
            for transaction in transaction_list:
                trans = Transaction()
                trans.transaction_date = today
                trans.is_debit_account = True
                trans.is_credit_account = False
                trans.amount = transaction.applied_amount
                trans.base_tax_amount = transaction.applied_amount
                trans.discount_amount = transaction.discount_amount
                trans.company_id = company.id
                trans.currency_id = rec_entry.currency
                trans.total_amount = transaction.applied_amount
                trans.journal_id = AP_Payment_entry.id
                trans.account_id = rec_entry.account_set.control_account_id if rec_entry.account_set.control_account else None
                if AP_Payment_entry.original_currency_id:
                    trans.currency_id = AP_Payment_entry.original_currency_id
                else:
                    trans.currency_id = AP_Payment_entry.currency_id
                if trans.currency_id == AP_Payment_entry.currency_id:
                    trans.exchange_rate = AP_Payment_entry.exchange_rate
                elif trans.currency_id == company.currency_id:
                    trans.exchange_rate = 1.0
                if not trans.exchange_rate:
                    if trans.currency_id != AP_Payment_entry.currency_id:
                        from_currency = trans.currency_id
                        to_currency = company.currency_id

                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                                    from_currency_id=from_currency,
                                                                    to_currency_id=to_currency,
                                                                    flag='ACCOUNTING', exchange_date=str(AP_Payment_entry.document_date.year) + '-' + str(AP_Payment_entry.document_date.month) + '-01').first()
                        if not exchange_rate:
                            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                                        from_currency_id=from_currency,
                                                                        to_currency_id=to_currency,
                                                                        exchange_date__lte=AP_Payment_entry.document_date,
                                                                        flag='ACCOUNTING').order_by('exchange_date').last()
                        if exchange_rate:
                            trans.exchange_rate = exchange_rate.rate
                        else:
                            trans.exchange_rate = 1.0
                    else:
                        trans.exchange_rate = AP_Payment_entry.exchange_rate
                trans.related_invoice_id = transaction.invoice_id
                # calculate the paid amount and outstanding amount for related_invoice
                related_invoice = None
                related_invoice = Journal.objects.get(pk=transaction.invoice_id)
                related_invoice.discount_amount = float(related_invoice.discount_amount) + float(trans.discount_amount)
                related_invoice.paid_amount = float(related_invoice.paid_amount) + float(trans.amount)
                related_invoice.outstanding_amount = float(related_invoice.document_amount) - float(
                    related_invoice.paid_amount)

                real_document_amount = float(related_invoice.document_amount) - \
                    float(related_invoice.discount_amount)

                if real_document_amount == float(related_invoice.paid_amount):
                    related_invoice.is_fully_paid = True
                    related_invoice.outstanding_amount = 0

                related_invoice.save()

                trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                 BALANCE_TYPE_DICT['Debit'])[transaction.is_debit_account]
                trans.functional_currency_id = company.currency_id
                trans.functional_amount = float(trans.total_amount) * float(trans.exchange_rate)
                if exchange_rate:
                    trans.rate_date = exchange_rate.exchange_date
                else:
                    trans.rate_date = AP_Payment_entry.document_date
                trans.save()

            AP_Payment_entry.amount = rec_entry.total_amount
            AP_Payment_entry.total_amount = rec_entry.total_amount
            AP_Payment_entry.payment_amount = rec_entry.payment_amount
            AP_Payment_entry.original_amount = rec_entry.original_amount
            AP_Payment_entry.update_by = rec_entry.update_by
            AP_Payment_entry.save()

        elif rec_entry.transaction_type == PAYMENT_TRANSACTION_TYPES_DICT['Misc Payment']:
            AP_Payment_entry.batch_id = batch.id
            AP_Payment_entry.name = rec_entry.name if rec_entry.name else ''
            AP_Payment_entry.code = rec_entry.code
            AP_Payment_entry.transaction_type = rec_entry.transaction_type
            AP_Payment_entry.status = int(STATUS_TYPE_DICT['Open'])
            AP_Payment_entry.journal_type = dict(TRANSACTION_TYPES)['AP Payment']
            AP_Payment_entry.document_type = DOCUMENT_TYPE_DICT['Miscellaneous Payment']
            AP_Payment_entry.company_id = company.id
            AP_Payment_entry.is_hidden = False
            AP_Payment_entry.bank_id = rec_entry.bank_id
            AP_Payment_entry.currency_id = rec_entry.currency_id
            AP_Payment_entry.payment_code_id = rec_entry.payment_code_id
            AP_Payment_entry.payment_check_number = rec_entry.payment_check_number
            AP_Payment_entry.reference = rec_entry.reference
            AP_Payment_entry.transaction_type = rec_entry.transaction_type
            AP_Payment_entry.invoice_number = rec_entry.invoice_number
            AP_Payment_entry.supplier = rec_entry.supplier
            AP_Payment_entry.account_set = rec_entry.account_set
            AP_Payment_entry.document_date = today
            AP_Payment_entry.posting_date = today
            AP_Payment_entry.is_manual_doc = rec_entry.is_manual_doc
            fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
            if fsc_calendar:
                year = fsc_calendar.fiscal_year
                month = fsc_calendar.period
            else:
                year = today.year
                month = today.month
            AP_Payment_entry.perd_month = month
            AP_Payment_entry.perd_year = year
            AP_Payment_entry.document_number = AR_AP_generate_document_number(
                    company.id,
                    dict(TRANSACTION_TYPES)['AP Payment'])
            AP_Payment_entry.amount = rec_entry.amount
            AP_Payment_entry.tax_amount = rec_entry.tax_amount
            AP_Payment_entry.total_amount = rec_entry.total_amount
            AP_Payment_entry.orig_exch_rate = 0
            AP_Payment_entry.save()

            # get latest exchange rate
            from_currency = rec_entry.bank.currency_id
            to_currency = company.currency_id
            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                        from_currency_id=from_currency,
                                                        to_currency_id=to_currency,
                                                        exchange_date__lte=AP_Payment_entry.document_date,
                                                        flag='ACCOUNTING').order_by('exchange_date').last()
            if not exchange_rate:
                if from_currency == to_currency:
                    AP_Payment_entry.exchange_rate = 1
                    AP_Payment_entry.exchange_rate_fk_id = None
                else:
                    try:
                        transactionlib.rollback()
                    except:
                        pass
            else:
                AP_Payment_entry.exchange_rate = exchange_rate.rate
                AP_Payment_entry.exchange_rate_fk_id = exchange_rate.id
                if exchange_rate.exchange_date.month != today.month:
                    AP_Payment_entry.has_old_rate == True
            AP_Payment_entry.update_by = rec_entry.update_by
            AP_Payment_entry.save()

            # add related transaction for Payment/Misc Payment journal
            # Debit for AP, Credit for AR
            transaction_list = RecurringEntryDetail.objects.filter(company_id=company.id, rec_entry_id=rec_entry.id)
            for transaction in transaction_list:
                trans = Transaction()
                trans.distribution_code_id = transaction.distribution_code_id
                trans.remark = transaction.remark
                trans.account_id = transaction.account_id
                trans.amount = transaction.amount
                trans.base_tax_amount = transaction.amount
                trans.tax_amount = transaction.tax_amount
                trans.total_amount = transaction.total_amount
                trans.tax_id = transaction.tax_id
                trans.currency_id = rec_entry.currency_id
                trans.journal_id = AP_Payment_entry.id
                trans.company_id = company.id
                trans.is_debit_account = True
                trans.is_credit_account = False
                trans.is_tax_include = transaction.is_tax_include
                trans.is_tax_transaction = transaction.is_tax_transaction
                trans.is_manual_tax_input = transaction.is_manual_tax_input

                trans.exchange_rate = AP_Payment_entry.exchange_rate
                trans.functional_currency_id = company.currency_id
                trans.functional_amount = float(trans.total_amount) * float(AP_Payment_entry.exchange_rate)
                if exchange_rate:
                    trans.rate_date = exchange_rate.exchange_date
                else:
                    trans.rate_date = AP_Payment_entry.document_date

                trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                    BALANCE_TYPE_DICT['Debit'])[trans.is_debit_account]
                trans.transaction_date = today
                trans.save()

        # update run date
        rec_entry.run_date = today
        rec_entry.save()

        batch.no_entries = batch.no_entries + 1
        batch.save()

        doc_number = update_next_doc_number(company.id, AP_Payment_entry.document_number, dict(TRANSACTION_TYPES)['AP Payment'])

    except OSError as e:
        print(e)


def create_AR_Receipt_entry(company, rec_entry, batch):
    try:
        today = datetime.date.today()
        form = ARReceiptInfoForm(company_id=company.id)
        AR_Receipt_entry = form.save(commit=False)
        # Save Journal Info
        if rec_entry.transaction_type == RECEIPT_TRANSACTION_TYPES_DICT['Receipt']:
            AR_Receipt_entry.batch_id = batch.id
            AR_Receipt_entry.name = rec_entry.name if rec_entry.name else ''
            AR_Receipt_entry.code = rec_entry.code
            AR_Receipt_entry.transaction_type = rec_entry.transaction_type
            AR_Receipt_entry.status = int(STATUS_TYPE_DICT['Open'])
            AR_Receipt_entry.journal_type = dict(TRANSACTION_TYPES)['AR Receipt']
            AR_Receipt_entry.update_by = 1
            AR_Receipt_entry.company_id = company.id
            AR_Receipt_entry.is_hidden = False
            AR_Receipt_entry.bank_id = rec_entry.bank_id
            AR_Receipt_entry.currency_id = rec_entry.currency_id
            AR_Receipt_entry.payment_code_id = rec_entry.payment_code_id
            AR_Receipt_entry.payment_check_number = rec_entry.payment_check_number
            AR_Receipt_entry.reference = rec_entry.reference
            AR_Receipt_entry.transaction_type = rec_entry.transaction_type
            AR_Receipt_entry.customer = rec_entry.customer
            AR_Receipt_entry.account_set = rec_entry.account_set
            AR_Receipt_entry.document_date = today
            AR_Receipt_entry.posting_date = today
            fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
            if fsc_calendar:
                year = fsc_calendar.fiscal_year
                month = fsc_calendar.period
            else:
                year = today.year
                month = today.month
            AR_Receipt_entry.perd_month = month
            AR_Receipt_entry.perd_year = year
            AR_Receipt_entry.is_manual_doc = rec_entry.is_manual_doc
            AR_Receipt_entry.document_number = AR_AP_generate_document_number(
                    company.id,
                    dict(TRANSACTION_TYPES)['AR Receipt'])
            if rec_entry.payment_check_number:
                AR_Receipt_entry.payment_check_number = rec_entry.payment_check_number
            AR_Receipt_entry.save()

            from_currency = rec_entry.bank.currency_id
            to_currency = company.currency_id

            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                        from_currency_id=from_currency,
                                                        to_currency_id=to_currency,
                                                        exchange_date__lte=AR_Receipt_entry.document_date,
                                                        flag='ACCOUNTING').order_by('exchange_date').last()
            if not exchange_rate:
                if from_currency == to_currency:
                    AR_Receipt_entry.exchange_rate = 1
                    AR_Receipt_entry.exchange_rate_fk_id = None
                else:
                    try:
                        transactionlib.rollback()
                    except:
                        pass
            else:
                AR_Receipt_entry.exchange_rate = exchange_rate.rate
                AR_Receipt_entry.exchange_rate_fk_id = exchange_rate.id
                if exchange_rate.exchange_date.month != today.month:
                    AR_Receipt_entry.has_old_rate == True

            AR_Receipt_entry.document_type = DOCUMENT_TYPE_DICT['Receipt']
            AR_Receipt_entry.amount = rec_entry.amount
            AR_Receipt_entry.total_amount = rec_entry.total_amount
            AR_Receipt_entry.original_amount = rec_entry.original_amount
            AR_Receipt_entry.receipt_unapplied = rec_entry.receipt_unapplied
            AR_Receipt_entry.customer_unapplied = rec_entry.customer_unapplied
            AR_Receipt_entry.original_currency_id = rec_entry.original_currency_id
            AR_Receipt_entry.payment_currency_id = rec_entry.payment_currency_id
            AR_Receipt_entry.orig_exch_rate = rec_entry.orig_exch_rate
            AR_Receipt_entry.save()

            transaction_list = RecurringEntryDetail.objects.filter(company_id=company.id, rec_entry_id=rec_entry.id)
            for transaction in transaction_list:
                trans = Transaction()
                trans.transaction_date = today
                trans.is_credit_account = True
                trans.is_debit_account = False
                trans.amount = transaction.applied_amount
                trans.base_tax_amount = transaction.applied_amount
                trans.company_id = company.id
                trans.currency_id = rec_entry.currency
                trans.total_amount = transaction.applied_amount
                trans.journal_id = AR_Receipt_entry.id
                trans.account_id = rec_entry.account_set.control_account_id if rec_entry.account_set.control_account else None
                if AR_Receipt_entry.original_currency_id:
                    trans.currency_id = AR_Receipt_entry.original_currency_id
                else:
                    trans.currency_id = AR_Receipt_entry.currency_id
                if trans.currency_id == AR_Receipt_entry.currency_id:
                    trans.exchange_rate = AR_Receipt_entry.exchange_rate
                elif trans.currency_id == company.currency_id:
                    trans.exchange_rate = 1.0
                if not trans.exchange_rate:
                    if trans.currency_id != AR_Receipt_entry.currency_id:
                        from_currency = trans.currency_id
                        to_currency = company.currency_id

                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                                    from_currency_id=from_currency,
                                                                    to_currency_id=to_currency,
                                                                    flag='ACCOUNTING', exchange_date=str(AR_Receipt_entry.document_date.year) + '-' + str(AR_Receipt_entry.document_date.month) + '-01').first()
                        if not exchange_rate:
                            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                                        from_currency_id=from_currency,
                                                                        to_currency_id=to_currency,
                                                                        exchange_date__lte=AR_Receipt_entry.document_date,
                                                                        flag='ACCOUNTING').order_by('exchange_date').last()
                        if exchange_rate:
                            trans.exchange_rate = exchange_rate.rate
                        else:
                            trans.exchange_rate = 1.0
                    else:
                        trans.exchange_rate = AR_Receipt_entry.exchange_rate

                trans.related_invoice_id = transaction.invoice_id
                # calculate the paid amount and outstanding amount for related_invoice
                related_invoice = None
                related_invoice = Journal.objects.get(pk=transaction.invoice_id)
                if related_invoice.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                    related_invoice.paid_amount = float(related_invoice.paid_amount) + float(trans.amount)
                    related_invoice.discount_amount = float(related_invoice.discount_amount) + float(trans.discount_amount)
                    related_invoice.adjustment_amount = float(related_invoice.adjustment_amount) + float(trans.adjustment_amount)
                    related_invoice.outstanding_amount = float(related_invoice.document_amount) - float(related_invoice.paid_amount)

                    real_document_amount = float(related_invoice.document_amount) + \
                        float(related_invoice.adjustment_amount) - \
                        float(related_invoice.discount_amount)

                    if float(real_document_amount) == float(related_invoice.paid_amount):
                        related_invoice.outstanding_amount = 0  # force outstanding amount to 0
                        related_invoice.is_fully_paid = True
                    else:
                        related_invoice.is_fully_paid = False
                else:
                    related_invoice.paid_amount = float(related_invoice.paid_amount) + float(trans.total_amount)
                    related_invoice.discount_amount = float(related_invoice.discount_amount) + float(trans.discount_amount)
                    related_invoice.adjustment_amount = float(related_invoice.adjustment_amount) + float(trans.adjustment_amount)

                    real_document_amount = float(related_invoice.customer_unapplied) + \
                        float(related_invoice.adjustment_amount) - \
                        float(related_invoice.discount_amount)

                    if float(real_document_amount) - float(related_invoice.paid_amount) <= 0:
                        related_invoice.is_fully_paid = True
                        related_invoice.outstanding_amount = 0
                    else:
                        related_invoice.is_fully_paid = False
                        related_invoice.outstanding_amount = float(real_document_amount) - float(related_invoice.paid_amount)

                related_invoice.save()

                trans.functional_currency_id = company.currency_id
                trans.functional_amount = float(trans.total_amount) * float(trans.exchange_rate)
                if exchange_rate:
                    trans.rate_date = exchange_rate.exchange_date
                else:
                    trans.rate_date = AR_Receipt_entry.document_date

                trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                 BALANCE_TYPE_DICT['Debit'])[transaction.is_debit_account]
                trans.save()

            AR_Receipt_entry.amount = rec_entry.total_amount
            AR_Receipt_entry.total_amount = rec_entry.total_amount
            AR_Receipt_entry.update_by = rec_entry.update_by
            AR_Receipt_entry.save()

        elif rec_entry.transaction_type == RECEIPT_TRANSACTION_TYPES_DICT['Unapplied Cash']:
            AR_Receipt_entry.batch_id = batch.id
            AR_Receipt_entry.name = rec_entry.name if rec_entry.name else ''
            AR_Receipt_entry.code = rec_entry.code
            AR_Receipt_entry.transaction_type = rec_entry.transaction_type
            AR_Receipt_entry.status = int(STATUS_TYPE_DICT['Open'])
            AR_Receipt_entry.journal_type = dict(TRANSACTION_TYPES)['AR Receipt']
            AR_Receipt_entry.update_by = 1
            AR_Receipt_entry.company_id = company.id
            AR_Receipt_entry.is_hidden = False
            AR_Receipt_entry.bank_id = rec_entry.bank_id
            AR_Receipt_entry.currency_id = rec_entry.currency_id
            AR_Receipt_entry.payment_code_id = rec_entry.payment_code_id
            AR_Receipt_entry.payment_check_number = rec_entry.payment_check_number
            AR_Receipt_entry.reference = rec_entry.reference
            AR_Receipt_entry.transaction_type = rec_entry.transaction_type
            AR_Receipt_entry.customer = rec_entry.customer
            AR_Receipt_entry.account_set = rec_entry.account_set
            AR_Receipt_entry.document_date = today
            AR_Receipt_entry.posting_date = today
            fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
            if fsc_calendar:
                year = fsc_calendar.fiscal_year
                month = fsc_calendar.period
            else:
                year = today.year
                month = today.month
            AR_Receipt_entry.perd_month = month
            AR_Receipt_entry.perd_year = year
            AR_Receipt_entry.is_manual_doc = rec_entry.is_manual_doc
            AR_Receipt_entry.document_number = AR_AP_generate_document_number(
                    company.id,
                    dict(TRANSACTION_TYPES)['AR Receipt'])
            if rec_entry.payment_check_number:
                AR_Receipt_entry.payment_check_number = rec_entry.payment_check_number
            AR_Receipt_entry.save()

            from_currency = rec_entry.bank.currency_id
            to_currency = company.currency_id

            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                        from_currency_id=from_currency,
                                                        to_currency_id=to_currency,
                                                        exchange_date__lte=AR_Receipt_entry.document_date,
                                                        flag='ACCOUNTING').order_by('exchange_date').last()
            if not exchange_rate:
                if from_currency == to_currency:
                    AR_Receipt_entry.exchange_rate = 1
                    AR_Receipt_entry.exchange_rate_fk_id = None
                else:
                    try:
                        transactionlib.rollback()
                    except:
                        pass
            else:
                AR_Receipt_entry.exchange_rate = exchange_rate.rate
                AR_Receipt_entry.exchange_rate_fk_id = exchange_rate.id
                if exchange_rate.exchange_date.month != today.month:
                    AR_Receipt_entry.has_old_rate == True

            AR_Receipt_entry.document_type = DOCUMENT_TYPE_DICT['Unapplied Cash']
            AR_Receipt_entry.amount = rec_entry.amount
            AR_Receipt_entry.total_amount = rec_entry.total_amount
            AR_Receipt_entry.payment_amount = rec_entry.payment_amount
            AR_Receipt_entry.original_amount = rec_entry.original_amount
            AR_Receipt_entry.receipt_unapplied = rec_entry.receipt_unapplied
            AR_Receipt_entry.customer_unapplied = rec_entry.customer_unapplied
            AR_Receipt_entry.original_currency_id = rec_entry.original_currency_id
            AR_Receipt_entry.payment_currency_id = rec_entry.payment_currency_id
            AR_Receipt_entry.orig_exch_rate = rec_entry.orig_exch_rate
            AR_Receipt_entry.save()

            transaction_list = RecurringEntryDetail.objects.filter(company_id=company.id, rec_entry_id=rec_entry.id)
            for transaction in transaction_list:
                trans = Transaction()
                trans.transaction_date = today
                trans.is_credit_account = True
                trans.is_debit_account = False
                trans.company_id = company.id
                trans.currency_id = rec_entry.currency
                trans.journal_id = AR_Receipt_entry.id
                trans.account_id = rec_entry.account_set.control_account_id if rec_entry.account_set.control_account else None
                if AR_Receipt_entry.original_currency_id:
                    trans.currency_id = AR_Receipt_entry.original_currency_id
                else:
                    trans.currency_id = AR_Receipt_entry.currency_id
                if trans.currency_id == AR_Receipt_entry.currency_id:
                    trans.exchange_rate = AR_Receipt_entry.exchange_rate
                elif trans.currency_id == company.currency_id:
                    trans.exchange_rate = 1.0
                if not trans.exchange_rate:
                    if trans.currency_id != AR_Receipt_entry.currency_id:
                        from_currency = trans.currency_id
                        to_currency = company.currency_id

                        exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                                    from_currency_id=from_currency,
                                                                    to_currency_id=to_currency,
                                                                    flag='ACCOUNTING', exchange_date=str(AR_Receipt_entry.document_date.year) + '-' + str(AR_Receipt_entry.document_date.month) + '-01').first()
                        if not exchange_rate:
                            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                                        from_currency_id=from_currency,
                                                                        to_currency_id=to_currency,
                                                                        exchange_date__lte=AR_Receipt_entry.document_date,
                                                                        flag='ACCOUNTING').order_by('exchange_date').last()
                        if exchange_rate:
                            trans.exchange_rate = exchange_rate.rate
                        else:
                            trans.exchange_rate = 1.0
                    else:
                        trans.exchange_rate = AR_Receipt_entry.exchange_rate

                trans.amount = transaction.amount
                trans.base_tax_amount = transaction.amount
                trans.tax_amount = 0
                trans.total_amount = transaction.total_amount
                trans.remark = ''
                trans.is_tax_include = False
                trans.is_tax_transaction = False
                trans.is_manual_tax_input = False
                trans.functional_currency_id = company.currency_id
                trans.functional_amount = float(trans.total_amount) * float(trans.exchange_rate)
                trans.functional_balance_type = BALANCE_TYPE_DICT['Credit'] if trans.is_credit_account else BALANCE_TYPE_DICT['Debit']
                if exchange_rate:
                    trans.rate_date = exchange_rate.exchange_date
                else:
                    trans.rate_date = AR_Receipt_entry.document_date
                trans.save()

            AR_Receipt_entry.amount = rec_entry.total_amount
            AR_Receipt_entry.total_amount = rec_entry.total_amount
            AR_Receipt_entry.update_by = rec_entry.update_by
            AR_Receipt_entry.save()

        elif rec_entry.transaction_type == RECEIPT_TRANSACTION_TYPES_DICT['Misc Receipt']:
            AR_Receipt_entry.batch_id = batch.id
            AR_Receipt_entry.name = rec_entry.name if rec_entry.name else ''
            AR_Receipt_entry.code = rec_entry.code
            AR_Receipt_entry.transaction_type = rec_entry.transaction_type
            AR_Receipt_entry.status = int(STATUS_TYPE_DICT['Open'])
            AR_Receipt_entry.journal_type = dict(TRANSACTION_TYPES)['AR Receipt']
            AR_Receipt_entry.document_type = DOCUMENT_TYPE_DICT['Miscellaneous Receipt']
            AR_Receipt_entry.company_id = company.id
            AR_Receipt_entry.is_hidden = False
            AR_Receipt_entry.bank_id = rec_entry.bank_id
            AR_Receipt_entry.currency_id = rec_entry.currency_id
            AR_Receipt_entry.payment_code_id = rec_entry.payment_code_id
            AR_Receipt_entry.payment_check_number = rec_entry.payment_check_number
            AR_Receipt_entry.reference = rec_entry.reference
            AR_Receipt_entry.transaction_type = rec_entry.transaction_type
            AR_Receipt_entry.document_number = rec_entry.document_number
            AR_Receipt_entry.invoice_number = rec_entry.invoice_number
            AR_Receipt_entry.customer = rec_entry.customer
            AR_Receipt_entry.account_set = rec_entry.account_set
            AR_Receipt_entry.document_date = today
            AR_Receipt_entry.posting_date = today
            fsc_calendar = FiscalCalendar.objects.filter(company_id=company.id, is_hidden=0, start_date__lte=today, end_date__gte=today).first()
            if fsc_calendar:
                year = fsc_calendar.fiscal_year
                month = fsc_calendar.period
            else:
                year = today.year
                month = today.month
            AR_Receipt_entry.perd_month = month
            AR_Receipt_entry.perd_year = year
            AR_Receipt_entry.is_manual_doc = rec_entry.is_manual_doc
            AR_Receipt_entry.document_number = AR_AP_generate_document_number(
                    company.id,
                    dict(TRANSACTION_TYPES)['AR Receipt'])
            AR_Receipt_entry.amount = rec_entry.amount
            AR_Receipt_entry.tax_amount = rec_entry.tax_amount
            AR_Receipt_entry.total_amount = rec_entry.total_amount
            AR_Receipt_entry.save()

            # get latest exchange rate
            from_currency = rec_entry.bank.currency_id
            to_currency = company.currency_id
            exchange_rate = ExchangeRate.objects.filter(is_hidden=False, company_id=company.id,
                                                        from_currency_id=from_currency,
                                                        to_currency_id=to_currency,
                                                        exchange_date__lte=AR_Receipt_entry.document_date,
                                                        flag='ACCOUNTING').order_by('exchange_date').last()
            if not exchange_rate:
                if from_currency == to_currency:
                    AR_Receipt_entry.exchange_rate = 1
                    AR_Receipt_entry.exchange_rate_fk_id = None
                else:
                    try:
                        transactionlib.rollback()
                    except:
                        pass
            else:
                AR_Receipt_entry.exchange_rate = exchange_rate.rate
                AR_Receipt_entry.exchange_rate_fk_id = exchange_rate.id
                if exchange_rate.exchange_date.month != today.month:
                    AR_Receipt_entry.has_old_rate == True
            AR_Receipt_entry.update_by = rec_entry.update_by
            AR_Receipt_entry.save()

            # add related transaction for Payment/Misc Payment journal
            # Debit for AP, Credit for AR
            transaction_list = RecurringEntryDetail.objects.filter(company_id=company.id, rec_entry_id=rec_entry.id)
            for transaction in transaction_list:
                trans = Transaction()
                trans.is_credit_account = True
                trans.is_debit_account = False
                trans.distribution_code_id = transaction.distribution_code_id
                trans.account_id = transaction.account_id
                trans.amount = transaction.amount
                trans.base_tax_amount = transaction.amount
                trans.tax_amount = transaction.tax_amount
                trans.total_amount = transaction.total_amount
                trans.tax_id = transaction.tax_id
                trans.currency_id = rec_entry.currency_id
                trans.journal_id = AR_Receipt_entry.id
                trans.company_id = company.id
                trans.is_tax_include = transaction.is_tax_include
                trans.is_tax_transaction = transaction.is_tax_transaction
                trans.is_manual_tax_input = transaction.is_manual_tax_input
                trans.description = transaction.description
                trans.remark = transaction.remark
                trans.reference = AR_Receipt_entry.reference
                trans.exchange_rate = AR_Receipt_entry.exchange_rate
                trans.functional_currency_id = company.currency_id
                trans.functional_amount = float(trans.total_amount) * float(AR_Receipt_entry.exchange_rate)
                if exchange_rate:
                    trans.rate_date = exchange_rate.exchange_date
                else:
                    trans.rate_date = AR_Receipt_entry.document_date
                trans.functional_balance_type = (BALANCE_TYPE_DICT['Credit'],
                                                    BALANCE_TYPE_DICT['Debit'])[trans.is_debit_account]
                trans.transaction_date = today
                trans.save()

        # update run date
        rec_entry.run_date = today
        rec_entry.save()

        batch.no_entries = batch.no_entries + 1
        batch.save()

        doc_number = update_next_doc_number(company.id, AR_Receipt_entry.document_number, dict(TRANSACTION_TYPES)['AR Receipt'])

    except OSError as e:
        print(e)


def updateAccountHistory():
    try:
        journal = Journal.objects.filter(is_hidden=False,
                                         journal_type=dict(
                                             TRANSACTION_TYPES)['GL'],
                                         status=int(
                                             STATUS_TYPE_DICT['Posted']),
                                         error_entry=0,
                                         ).order_by('-perd_year', '-perd_month').first()
        if journal:
            result = carry_forward_balance(journal.perd_month, journal.perd_year)
    except Exception as e:
        print(e)

    return True


def carry_forward_balance(from_month, from_year):
    company = Company.objects.filter(is_hidden=False).first()
    history_list = AccountHistory.objects.filter(is_hidden=False, company_id=company.id,
                                                account__is_hidden=False, account__company_id=company.id,
                                                period_month=from_month, period_year=from_year)\
                        .exclude(source_currency_id__isnull=True)\
                        .select_related('account', 'source_currency')
                        # .exclude(Q(source_net_change=0) & Q(functional_net_change=0))\
                        # .exclude(account__account_type=int(ACCOUNT_TYPE_DICT['Income Statement']))\

    for account_history in history_list:
        src_eb = account_history.source_end_balance
        func_eb = account_history.functional_end_balance
        for i in range(from_month + 1, 13):
            try:
                next_history = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                is_hidden=False, company_id=company.id,
                                                                account_id=account_history.account_id,
                                                                period_month=i, period_year=from_year,
                                                                source_currency_id=account_history.source_currency_id)\
                    .exclude(source_currency_id__isnull=True)\
                    .first()

                next_history.source_begin_balance = src_eb
                next_history.source_end_balance = round_number(
                    next_history.source_begin_balance) + round_number(next_history.source_net_change)
                next_history.functional_begin_balance = func_eb
                next_history.functional_end_balance = round_number(
                    next_history.functional_begin_balance) + round_number(next_history.functional_net_change)
                next_history.save()
                src_eb = next_history.source_end_balance
                func_eb = next_history.functional_end_balance
            except Exception as e:
                print(e)

        period_ADJ = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                is_hidden=False, company_id=company.id,
                                                                account_id=account_history.account_id,
                                                                period_month__in=['ADJ'],
                                                                period_year=from_year,
                                                                source_currency_id=account_history.source_currency_id)\
            .exclude(source_currency_id__isnull=True)

        for ADJ_CLS in period_ADJ:
            ADJ_CLS.source_begin_balance = src_eb
            ADJ_CLS.source_end_balance = round_number(
                ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
            ADJ_CLS.functional_begin_balance = func_eb
            ADJ_CLS.functional_end_balance = round_number(
                ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
            ADJ_CLS.save()

        period_CLS = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                is_hidden=False, company_id=company.id,
                                                                account_id=account_history.account_id,
                                                                period_month__in=['CLS'],
                                                                period_year=from_year,
                                                                source_currency_id=account_history.source_currency_id)\
            .exclude(source_currency_id__isnull=True)

        for ADJ_CLS in period_CLS:
            ADJ_CLS.source_begin_balance = src_eb
            ADJ_CLS.source_end_balance = round_number(
                ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
            ADJ_CLS.functional_begin_balance = func_eb
            ADJ_CLS.functional_end_balance = round_number(
                ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
            ADJ_CLS.save()
            src_eb = ADJ_CLS.source_end_balance
            func_eb = ADJ_CLS.functional_end_balance


        for year in range(int(from_year) + 1, int(from_year) + 2):
            last_day = None
            for i in range(12):
                _, num_days = calendar.monthrange(year, i + 1)
                last_day = datetime.date(year, i + 1, num_days)
                try:
                    next_history = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                                    is_hidden=False,
                                                                    company_id=company.id,
                                                                    account_id=account_history.account_id,
                                                                    period_month=i + 1,
                                                                    period_year=year,
                                                                    source_currency_id=account_history.source_currency_id)\
                        .exclude(source_currency_id__isnull=True)\
                        .first()

                    next_history.source_begin_balance = src_eb
                    next_history.source_end_balance = round_number(
                        next_history.source_begin_balance) + round_number(next_history.source_net_change)
                    next_history.functional_begin_balance = func_eb
                    next_history.functional_end_balance = round_number(
                        next_history.functional_begin_balance) + round_number(next_history.functional_net_change)
                    next_history.save()
                    src_eb = next_history.source_end_balance
                    func_eb = next_history.functional_end_balance
                except Exception as e:
                    print(e)
                    period = i + 1
                    create_account_history(company.id, year, period, last_day, account_history.account_id,
                                            account_history.source_currency_id,
                                            src_eb, company.currency_id,
                                            func_eb)

            period_ADJO = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                            is_hidden=False,
                                                            company_id=company.id,
                                                            account_id=account_history.account_id,
                                                            period_month__in=['ADJ'],
                                                            period_year=year,
                                                            source_currency_id=account_history.source_currency_id)\
                .exclude(source_currency_id__isnull=True)
            if period_ADJO:
                for ADJ_CLS in period_ADJO:
                    ADJ_CLS.source_begin_balance = src_eb
                    ADJ_CLS.source_end_balance = round_number(
                        ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                    ADJ_CLS.functional_begin_balance = func_eb
                    ADJ_CLS.functional_end_balance = round_number(
                        ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                    ADJ_CLS.save()
            else:
                create_account_history(company.id, year, 'ADJ', last_day, account_history.account_id,
                                        account_history.source_currency_id, src_eb,
                                        company.currency_id, func_eb)

            period_CLSO = AccountHistory.objects.select_related('account', 'source_currency').filter(
                                                            is_hidden=False,
                                                            company_id=company.id,
                                                            account_id=account_history.account_id,
                                                            period_month__in=['CLS'],
                                                            period_year=year,
                                                            source_currency_id=account_history.source_currency_id)\
                .exclude(source_currency_id__isnull=True)
            if period_CLSO:
                for ADJ_CLS in period_CLSO:
                    ADJ_CLS.source_begin_balance = src_eb
                    ADJ_CLS.source_end_balance = round_number(
                        ADJ_CLS.source_begin_balance) + round_number(ADJ_CLS.source_net_change)
                    ADJ_CLS.functional_begin_balance = func_eb
                    ADJ_CLS.functional_end_balance = round_number(
                        ADJ_CLS.functional_begin_balance) + round_number(ADJ_CLS.functional_net_change)
                    ADJ_CLS.save()
                    src_eb = ADJ_CLS.source_end_balance
                    func_eb = ADJ_CLS.functional_end_balance
            else:
                create_account_history(company.id, year, 'CLS', last_day, account_history.account_id,
                                        account_history.source_currency_id, src_eb,
                                        company.currency_id, func_eb)

    return True


def create_account_history(company_id, year, period, last_day, account_id, source_currency_id, source_net_change,
                           functional_currency_id, func_net_change):
    try:
        account_history = AccountHistory()
        account_history.period_year = year
        account_history.period_month = period
        account_history.period_date = last_day
        account_history.company_id = company_id
        account_history.account_id = account_id
        account_history.source_currency_id = source_currency_id
        account_history.source_begin_balance = source_net_change
        account_history.source_net_change = 0
        account_history.source_end_balance = account_history.source_begin_balance + \
            account_history.source_net_change
        account_history.functional_currency_id = functional_currency_id
        account_history.functional_begin_balance = func_net_change
        account_history.functional_net_change = 0
        account_history.functional_end_balance = account_history.functional_begin_balance + \
            account_history.functional_net_change
        account_history.create_date = datetime.datetime.today()
        account_history.save()
        return True
    except Exception as e:
        print(e)
        return False

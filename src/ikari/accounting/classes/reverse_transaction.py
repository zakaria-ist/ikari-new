from copy import deepcopy
from datetime import datetime
from decimal import getcontext

from accounting.models import Batch, Journal, FiscalCalendar
from companies.models import Company
from transactions.models import Transaction
from utilities.constants import SOURCE_APPLICATION, INPUT_TYPE_DICT, SOURCE_LEDGER_DICT, STATUS_TYPE_DICT, \
    TRANSACTION_TYPES, PAYMENT_TRANSACTION_TYPES_DICT, BALANCE_TYPE_DICT
from utilities.messages import REVERSE_TRANSACTION_FAILED1, RV_ERR_CREATE_BATCH, MESSAGE_ERROR, BATCH_ERROR, \
    REVERSE_TRANSACTION_SUCCESS, BANK_FISCAL_LOCKED_ERROR, REVERSE_TRANSACTION_FAILED2, GL_FISCAL_LOCKED_ERROR


class C_Reverse_Transaction:
    request = None
    company_id = 0
    d_company = None
    error_count = 0
    batch = None
    invoice_source = None
    source_application = None
    journal_list = None

    def __init__(self, request, journal_list):
        getcontext().prec = 6
        self.request = request
        self.company_id = request.session['login_company_id'] if request.session['login_company_id'] else 0
        self.d_company = Company.objects.get(pk=self.company_id)
        self.invoice_source = []
        self.source_application = dict(SOURCE_APPLICATION)
        self.journal_list = journal_list

    def reverseTransaction(self):
        result = self.checkFiscalCalendar()
        if result[0]:
            result = self.createBatch()
            if result[0]:
                result = self.createEntries()
        return result

    def createBatch(self):
        batch_entry = None
        status = None
        try:
            if int(self.request.POST['journal_type']) == dict(TRANSACTION_TYPES)['AR Receipt']:
                source_batch_source_ledger = SOURCE_LEDGER_DICT['Account Receivable']
            else:
                source_batch_source_ledger = SOURCE_LEDGER_DICT['Account Payable']
            batch_entry = Batch()
            batch_entry.company_id = self.company_id
            batch_entry.status = STATUS_TYPE_DICT['Open']
            batch_entry.input_type = INPUT_TYPE_DICT['Generated']
            batch_entry.batch_type = dict(TRANSACTION_TYPES)['GL']
            batch_entry.description = 'Reverse from ' + self.source_application.get(
                self.request.POST['journal_type']) + ' ' + datetime.now().strftime("%Y-%m-%d")
            batch_entry.currency_id = self.request.POST['currency']
            batch_entry.batch_no = self.generateBatchNumber(self.company_id, 5)
            batch_entry.no_entries = 0
            batch_entry.batch_amount = 0
            batch_entry.source_ledger = source_batch_source_ledger
            batch_entry.create_date = datetime.now()
            batch_entry.update_by = self.request.user.id
            batch_entry.save()
            self.batch = batch_entry
        except:
            status = REVERSE_TRANSACTION_FAILED1 + RV_ERR_CREATE_BATCH
        return [batch_entry, status]

    def createEntries(self):
        result = False
        status = ''
        error_count = 0
        if len(self.journal_list) > 0:
            for journal in self.journal_list:
                try:
                    payment_entry = Journal.objects.get(pk=journal['journal_id'])
                    reverse_journal = deepcopy(payment_entry)
                    reverse_journal.pk = None
                    reverse_journal.status = STATUS_TYPE_DICT['Open']
                    reverse_journal.bank_id = self.request.POST['bank']
                    reverse_journal.update_by = self.request.user.id
                    reverse_journal.create_date = datetime.now()
                    reverse_journal.batch_id = self.batch.id
                    reverse_journal.document_number = self.generateDocumentNumber(self.company_id, 5,
                                                                                  datetime.now().strftime("%Y-%m-%d"))
                    reverse_journal.source_type = \
                        ('AP-PY', 'AR-PY')[int(self.request.POST['journal_type']) == dict(TRANSACTION_TYPES)['AR Receipt']]
                    reverse_journal.document_date = datetime.strptime(journal['reversal_date'], '%Y-%m-%d')
                    fsc_calendar = FiscalCalendar.objects.filter(company_id=self.company_id, is_hidden=0, 
                                                                    start_date__lte=reverse_journal.document_date, 
                                                                    end_date__gte=reverse_journal.document_date).first()
                    if fsc_calendar:
                        year = fsc_calendar.fiscal_year
                        month = fsc_calendar.period
                    else:
                        year = reverse_journal.document_date.year
                        month = reverse_journal.document_date.month
                    reverse_journal.perd_month = month
                    reverse_journal.perd_year = year
                    reverse_journal.save()
                    current_payment_amount = self.createTransaction(payment_entry.batch_id, reverse_journal, journal)
                    error_count += 1
                    if current_payment_amount > 0:
                        if self.updateBatch(current_payment_amount):
                            if self.updateEntry(reverse_journal, current_payment_amount):
                                if self.updatePaymentEntry(payment_entry):
                                    if self.updateInvoiceSource(payment_entry, current_payment_amount):
                                        error_count -= 1
                    else:
                        error_count += 1

                except Exception as e:
                    error_count += 1

            if error_count >= len(self.journal_list):
                self.invoice_source = []
                if self.setBatchAsError(self.batch.id):
                    status = BATCH_ERROR % (self.batch.batch_no)
            else:
                status = REVERSE_TRANSACTION_SUCCESS % (self.batch.batch_no)
                result = True
        else:
            status = REVERSE_TRANSACTION_FAILED1 + REVERSE_TRANSACTION_FAILED2

        return [result, status]

    def createTransaction(self, batch_id, journal, reverse_info):
        current_payment_amount = 0
        try:
            transactions = self.getGLEntries(batch_id, journal.code)
            if transactions:
                for transaction in transactions:
                    reverse_transaction = deepcopy(transaction)
                    reverse_transaction.id = None
                    reverse_transaction.is_debit_account = (True, False)[transaction.is_debit_account]
                    reverse_transaction.is_credit_account = not reverse_transaction.is_debit_account
                    reverse_transaction.functional_balance_type = (BALANCE_TYPE_DICT['Debit'],
                                                                   BALANCE_TYPE_DICT['Credit'])[
                        transaction.is_debit_account]
                    reverse_transaction.journal_id = journal.id
                    reverse_transaction.transaction_date = reverse_info['reversal_date']
                    reverse_transaction.remark = reverse_info['reason']
                    reverse_transaction.create_date = datetime.now()
                    reverse_transaction.update_by = self.request.user.id
                    reverse_transaction.save()
                    if transaction.is_debit_account:
                        current_payment_amount += transaction.functional_amount
        except Exception as e:
            pass
        return current_payment_amount

    def checkFiscalCalendar(self):
        result = True
        status = None
        if len(self.journal_list) > 0:
            for journal in self.journal_list:
                status = self.isFiscalPeriodClosed(journal['reversal_date'])
                if not status:
                    status = self.isFiscalPeriodClosed(journal['transaction_date'])
                if status:
                    result = False
                    break
        else:
            result = False
            status = REVERSE_TRANSACTION_FAILED1 + REVERSE_TRANSACTION_FAILED2
        return [result, status]

    def isFiscalPeriodClosed(self, p_period_date):
        result = None
        try:
            period_date = datetime.strptime(p_period_date, '%Y-%m-%d')
            fiscal_period = FiscalCalendar.objects.filter(is_hidden=0, company_id=self.company_id,
                                                          start_date__lte=period_date,
                                                          end_date__gte=period_date).first()
            if fiscal_period:
                if fiscal_period.is_bank_locked:
                    result = REVERSE_TRANSACTION_FAILED1 + '<br />' + BANK_FISCAL_LOCKED_ERROR % (
                        'Reversal Date/Document Date', period_date.date(),
                        fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date, fiscal_period.fiscal_year)
                elif fiscal_period.is_gl_locked:
                    result = REVERSE_TRANSACTION_FAILED1 + '<br />' + GL_FISCAL_LOCKED_ERROR % (
                        'Reversal Date/Document Date', period_date.date(),
                        fiscal_period.period, fiscal_period.start_date, fiscal_period.end_date, fiscal_period.fiscal_year)
        except:
            pass
        return result

    def getGLEntries(self, batch_id, entry_num):
        gl_transactions = None
        try:
            gl_entries = Journal.objects.filter(company_id=self.company_id, is_hidden=False,
                                                code=entry_num,
                                                batch__related_batch_id=batch_id,
                                                batch__status__in=(
                                                    int(STATUS_TYPE_DICT['Open']), int(STATUS_TYPE_DICT['Posted'])),
                                                batch__is_hidden=False).first()
            gl_entries.status = STATUS_TYPE_DICT['Reversed']
            gl_entries.save()
            gl_transactions = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                                                         journal_id=gl_entries.id)
        except Exception as e:
            pass
        return gl_transactions

    def updateBatch(self, amount):
        result = True
        try:
            self.batch.no_entries += 1
            self.batch.batch_amount += float(amount)
            self.batch.save()
        except Exception as e:
            result = False
        return result

    def updateEntry(self, entry, amount):
        result = True
        try:
            entry.total_amount = float(amount)
            entry.code = self.batch.no_entries
            entry.save()
        except Exception as e:
            result = False
        return result

    def updatePaymentEntry(self, payment_entry):
        result = True
        try:
            payment_entry.status = STATUS_TYPE_DICT['Reversed']
            payment_entry.save()
        except Exception as e:
            result = False
        return result

    def updateInvoiceSource(self, payment_entry, transaction_amount):
        result = True
        try:
            if int(payment_entry.transaction_type) < int(PAYMENT_TRANSACTION_TYPES_DICT['Misc Payment']):
                invoice_source = self.getInvoiceSource(payment_entry.id)
                if invoice_source:
                    invoice_source.paid_amount = float(invoice_source.paid_amount) - float(transaction_amount)
                    invoice_source.outstanding_amount = float(invoice_source.document_amount) - float(
                        invoice_source.paid_amount)
                    if float(invoice_source.document_amount) == float(invoice_source.paid_amount):
                        invoice_source.is_fully_paid = True
                    else:
                        invoice_source.is_fully_paid = False
                    invoice_source.update_by = self.request.user.id
                    invoice_source.update_date = datetime.now()
                    invoice_source.save()
                else:
                    result = False
        except Exception as e:
            result = False
        return result

    def getInvoiceSource(self, payment_id):
        related_invoice_id = Transaction.objects.filter(company_id=self.company_id, is_hidden=False,
                                                        journal__id=payment_id). \
            exclude(related_invoice_id__isnull=True).first().related_invoice_id
        invoice_entry = Journal.objects.get(pk=related_invoice_id)
        return invoice_entry

    def generateBatchNumber(self, company_id, batch_type):
        batchs = Batch.objects.filter(company_id=company_id, batch_type=batch_type, is_hidden=False)
        cnt = 0
        batch_last = 0
        if batchs:
            cnt = batchs.count()
            if batchs.last().batch_no:
                batch_last = int(batchs.last().batch_no)
        batch_number = cnt + 1 if cnt > batch_last else batch_last + 1
        return batch_number

    def generateDocumentNumber(self, company_id, journal_type, document_date):
        year = document_date.split('-')[0]
        month = document_date.split('-')[1]
        fsc_calendar = FiscalCalendar.objects.filter(company_id=company_id, is_hidden=0, start_date__lte=document_date, 
                                                        end_date__gte=document_date).first()
        if fsc_calendar:
            year = fsc_calendar.fiscal_year
            month = fsc_calendar.period
        journals = Journal.objects.filter(journal_type__in=(dict(TRANSACTION_TYPES)['AR Receipt'],
                                                            dict(TRANSACTION_TYPES)['AP Payment']),
                                          company_id=self.company_id, is_hidden=False,
                                          perd_month=month,
                                          perd_year=year,
                                          is_manual_doc=False)
        cnt = 0
        doc_last = 0
        if journals:
            cnt = journals.count()
            if journals.last().document_number:
                doc_last = int(journals.last().document_number.split('-')[-1])
        postfix = cnt + 1 if cnt > doc_last else doc_last + 1
        prefix = 'PY'
        document_number = prefix + '-' + year + month + '-' + '{:05}'.format(postfix % 100000)
        return document_number

    def setBatchAsError(self, batch_id):
        result = True
        try:
            batch = Batch.objects.get(pk=batch_id)
            batch.status = STATUS_TYPE_DICT['ERROR']
            batch.save()
        except:
            result = False
        return result

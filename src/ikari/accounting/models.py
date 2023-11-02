from datetime import date, datetime
from django.db import models
from accounts.models import AccountSet, Account, DistributionCode
from banks.models import Bank
from companies.models import Company
from currencies.models import Currency, ExchangeRate
from transactions.models import Transaction
from orders.models import Order
from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce
from taxes.models import Tax
from utilities.constants import PAYMENT_TYPE, SOURCE_LEDGER, SOURCE_TYPES, DOCUMENT_TYPES, INPUT_TYPES, \
    REVERSE_TO_PERIOD_LIST, TRANSACTION_TYPES, STATUS_TYPE_DICT, DOCUMENT_TYPE_DICT, INPUT_TYPE_DICT, \
    FLAG_TYPE, RECURRING_PERIOD_DICT, RECURRING_ENTRY_MODE, RECURRING_USER_MODE, \
    REVALUATION_METHODS, RATE_TYPES


# Create your models here.
class PaymentCode(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=4000, null=True)
    payment_type = models.CharField(max_length=1, choices=PAYMENT_TYPE, null=True)
    source_type = models.CharField(max_length=15, null=True)
    is_active = models.BooleanField(default=True)
    create_date = models.DateField(default=date.today)
    update_date = models.DateField(default=date.today)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField()


class Batch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    batch_no = models.CharField(max_length=50, null=True)
    batch_date = models.DateField(default=date.today)
    description = models.CharField(max_length=250, null=True)
    batch_type = models.IntegerField(default=dict(TRANSACTION_TYPES)['Undefined'])
    document_type = models.CharField(max_length=2, default=DOCUMENT_TYPE_DICT['Undefined'], choices=DOCUMENT_TYPES)
    no_entries = models.IntegerField(default=0)
    batch_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount after tax
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    input_type = models.CharField(max_length=2, default=INPUT_TYPE_DICT['Undefined'], choices=INPUT_TYPES)
    posting_sequence = models.CharField(max_length=50, null=True)
    status = models.IntegerField(default=int(STATUS_TYPE_DICT['Undefined']))
    update_date = models.DateField(auto_now=True)
    create_date = models.DateField(auto_now_add=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    related_batch_id = models.IntegerField(default=0)
    source_ledger = models.CharField(max_length=50, null=True, choices=SOURCE_LEDGER)
    flag = models.CharField(max_length=1, choices=FLAG_TYPE, default=0)


# Create your models here.
class Journal(models.Model):
    code = models.CharField(max_length=50, null=True)
    name = models.CharField(max_length=4000, null=True, default='')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    journal_type = models.IntegerField(default=dict(TRANSACTION_TYPES)['Undefined'], db_index=True)
    document_type = models.CharField(max_length=2, default=DOCUMENT_TYPE_DICT['Undefined'], choices=DOCUMENT_TYPES, db_index=True)
    transaction_type = models.CharField(max_length=2,
                                        default="0")  # ==> PAYMENT_TRANSACTION_TYPES or RECEIPT_TRANSACTION_TYPES
    source_type = models.CharField(max_length=50, null=True, choices=SOURCE_TYPES)  # ==> Use For 5: GL
    # GL-AP: AP Adjustments...GL-RV: GL Revaluation Transactions
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, null=True,
                                 related_name="journal_customer", db_index=True)
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.CASCADE, null=True,
                                 related_name="journal_supplier", db_index=True)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    po_number = models.CharField(max_length=50, null=True, default='')
    order_number = models.CharField(max_length=50, null=True, default='')
    document_number = models.CharField(max_length=50, null=True, db_index=True, default='')
    is_manual_doc = models.BooleanField(default=False)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)  # Add invoice_number for Misc Payment/Receipt entry
    reference = models.CharField(max_length=50, null=True, blank=True)
    document_date = models.DateField(default=date.today, db_index=True)
    posting_date = models.DateField(null=True)
    due_date = models.DateField(null=True)
    account_set = models.ForeignKey(AccountSet, on_delete=models.CASCADE, null=True, related_name="journal_account_set")
    amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    tax_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    total_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount after tax
    document_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount related to GR/DO invoice
    # Use for 3: AR Receipt; 4: AP Payment;
    payment_number = models.IntegerField(default=0)  # count the times an invoice got pay
    paid_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Paided-amount of invoice
    outstanding_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Havent paid yet - amount of invoice
    real_outstanding = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Havent paid yet - amount of invoice
    is_fully_paid = models.BooleanField(default=False)
    # End Use
    # Use for 3: AR Receipt; 4: AP Payment;
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True)
    payment_code = models.ForeignKey(PaymentCode, on_delete=models.CASCADE, null=True)
    payment_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                        related_name="payment_refer_account")
    payment_check_number = models.CharField(max_length=50, null=True)
    payment_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    payment_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, related_name="payment_currency")
    original_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    original_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True,
                                          related_name="original_currency")
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    exchange_rate_fk = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, null=True)

    receipt_unapplied = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    customer_unapplied = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    # End Use
    status = models.IntegerField(default=int(STATUS_TYPE_DICT['Undefined']))
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    # batch id when
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True)
    source_ledger = models.CharField(max_length=50, null=True, choices=SOURCE_LEDGER)
    orig_exch_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    orig_exch_rate_fk = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, null=True,
                                          related_name="orig_exch_rate_fk")
    is_auto_reverse = models.BooleanField(default=False)
    reverse_to_period = models.CharField(max_length=1, null=True, choices=REVERSE_TO_PERIOD_LIST)
    reverse_to_period_val = models.DateField(null=True)
    is_rev_do = models.BooleanField(default=False)
    perd_year = models.IntegerField(default=0)
    perd_month = models.IntegerField(default=0)
    is_reversed_entry = models.BooleanField(default=False)
    is_auto_reversed_entry = models.BooleanField(default=False)
    rev_perd_month = models.IntegerField(default=0)
    rev_perd_year = models.IntegerField(default=0)
    flag = models.CharField(max_length=1, choices=FLAG_TYPE, default=0)

    # Reference for adjustment journal
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True,
                                    related_name="transaction")

    discount_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount for discount
    real_discount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount for discount
    adjustment_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount for adjustment
    real_adjustment = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount for adjustment

    fully_paid_date = models.DateField(null=True)
    error_entry = models.IntegerField(default=0)
    reverse_reconciliation = models.BooleanField(default=False)

    tax_exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    has_old_rate = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ": " + self.document_type + " " + self.document_number

    def check_is_fully_paid(self, cutoff_date):
        if not self.outstanding_amount == 0:
            return False

        full_transaction_list = self.related_invoice.select_related('journal').filter(
            journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
        ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True
                                                   ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True)
        # check if the journal assign to other
        # if it is then we can consider it is fully paid, regardless of amount
        # in such case the amount, will be transferred to the related journal
        transaction = Transaction.objects.filter(journal=self, journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
                                                 ).exclude(journal__reverse_reconciliation=True)\
            .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True).exclude(related_invoice_id=None).aggregate(
                total=Coalesce(Sum('journal__outstanding_amount'), Value(0)))

        payment_total = 0
        payment_total += abs(transaction['total'])

        total_amount = self.total_amount - abs(self.adjustment_amount) - abs(self.discount_amount)
        if full_transaction_list:
            if self.customer:
                full_transaction_list = full_transaction_list.filter(journal__customer_id=self.customer_id)
                is_credit_journal = self.journal.first().is_credit_account if self.journal.first() else False
                for transaction in full_transaction_list:
                    if transaction.journal.document_type == DOCUMENT_TYPE_DICT['Adjustment']:
                        payment_total += (transaction.amount + transaction.tax_amount)
                    elif transaction.is_credit_account == is_credit_journal:
                        payment_total += (transaction.amount + transaction.tax_amount)
                    elif transaction.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                        if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount += (transaction.amount + transaction.tax_amount)
                        else:
                            total_amount -= (transaction.amount + transaction.tax_amount)
                    else:
                        payment_total += (transaction.amount + transaction.tax_amount)

                    if transaction.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                        total_amount += (transaction.amount + transaction.tax_amount)
                        payment_total -= (transaction.amount + transaction.tax_amount)
            elif self.supplier:
                full_transaction_list = full_transaction_list.filter(journal__supplier_id=self.supplier_id)
                for transaction in full_transaction_list:
                    if transaction.journal.document_type in [DOCUMENT_TYPE_DICT['Payment'],
                                                            DOCUMENT_TYPE_DICT['Unapplied Cash']]:
                        payment_total -= (transaction.amount + transaction.tax_amount)
                        total_amount += transaction.adjustment_amount
                    elif transaction.journal.document_type == DOCUMENT_TYPE_DICT['Adjustment']:
                        payment_total += (transaction.amount + transaction.tax_amount)
                    elif transaction.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                        if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount += (transaction.amount + transaction.tax_amount)
                        else:
                            total_amount -= (transaction.amount + transaction.tax_amount)
                    elif transaction.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                        if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            total_amount -= (transaction.amount + transaction.tax_amount)
                        else:
                            total_amount += (transaction.amount + transaction.tax_amount)
                    else:
                        payment_total += (transaction.amount + transaction.tax_amount)

        return total_amount <= abs(payment_total)

    # test function for u-amount
    def has_outstanding(self, cutoff_date, paid=False):
        # if self.id in [4532]:
        #     print('document', self.document_number)
        self_type = 'AR'
        if self.journal_type in [dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AR Invoice']]:
            last_payment_transaction = self.related_invoice.filter(Q(
                journal__document_date__lte=cutoff_date, journal__journal_type=dict(TRANSACTION_TYPES)['AR Invoice'], journal__status=int(STATUS_TYPE_DICT['Posted'])) | Q(
                journal__document_date__lte=cutoff_date, journal__journal_type__in=[dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AD']],
                journal__status=int(STATUS_TYPE_DICT['Posted']))
            ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True
            ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True).order_by('transaction_date', 'id')
        else:
            self_type = 'AP'
            last_payment_transaction = self.related_invoice.filter(Q(
                journal__document_date__lte=cutoff_date, journal__journal_type=dict(TRANSACTION_TYPES)['AP Invoice'], journal__status=int(STATUS_TYPE_DICT['Posted'])) | Q(
                journal__document_date__lte=cutoff_date, journal__journal_type=dict(TRANSACTION_TYPES)['AP Payment'], journal__status=int(STATUS_TYPE_DICT['Posted'])),
            ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True
            ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True).order_by('journal__document_date', 'id')

        if not paid and last_payment_transaction.exists():
            last_payment_transaction = last_payment_transaction.last()
            outstanding = last_payment_transaction.related_journal_outstanding
            if outstanding:
                return [True, outstanding]
            else:
                if self.journal_type == dict(TRANSACTION_TYPES)['AR Receipt'] and self.customer_unapplied != 0:
                    return [True, self.customer_unapplied * (-1)]
                elif self.outstanding_amount - abs(self.adjustment_amount) - abs(self.discount_amount) != 0:
                    return [True, self.outstanding_amount - abs(self.adjustment_amount) - abs(self.discount_amount)]
                else:
                    return [False, 0]
        else:
            if self.journal_type in [dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AP Payment']] and self.customer_unapplied != 0:
                return [True, self.customer_unapplied * (-1)]
            elif self.document_type == DOCUMENT_TYPE_DICT['Unapplied Cash']:
                return [True, self.total_amount * (-1)]
            elif self.document_type == DOCUMENT_TYPE_DICT['Credit Note'] or self.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
                try:
                    transactions = Transaction.objects.filter(is_hidden=False, journal_id=self.id)\
                        .exclude(related_invoice_id__isnull=True)

                    if transactions.exists():
                        if self.journal_type == dict(TRANSACTION_TYPES)['AR Invoice']:
                            if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                outstanding = self.get_related_outstanding(
                                    transactions.first(), (-1) * self.document_amount, cutoff_date, self_type)
                                if outstanding >= 0:
                                    return [False, 0]
                                else:
                                    return [True, outstanding]
                            else:
                                if self.outstanding_amount != 0:
                                    return [True, self.outstanding_amount]
                                else:
                                    return [False, 0]
                            # return [False, 0]
                        else:
                            if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                                outstanding = self.get_related_outstanding(
                                    transactions.first(), (-1) * self.document_amount, cutoff_date, self_type)
                                if outstanding >= 0:
                                    return [False, 0]
                                else:
                                    return [True, outstanding]
                            else:
                                if self.outstanding_amount != 0:
                                    return [True, self.outstanding_amount]
                                else:
                                    return [False, 0]
                    else:
                        if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                            return [True, self.total_amount * (-1)]
                        else:
                            return [True, self.total_amount]

                except Exception as e:
                    print(e)
                    if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                        return [True, self.total_amount * (-1)]
                    else:
                        return [True, self.total_amount]
            else:
                return [True, self.total_amount]

    def get_related_outstanding(self, transaction, self_amount, cutoff_date, self_type):
        start = transaction
        outstanding = self_amount
        while transaction and transaction.related_invoice_id:
            try:
                related_invoice_id = transaction.related_invoice_id
                related_invoice = Journal.objects.get(pk=related_invoice_id)
                cut_date = datetime.strptime(cutoff_date, '%Y-%m-%d')
                if related_invoice.fully_paid_date:
                    paid_date = datetime.strptime(str(related_invoice.fully_paid_date), '%Y-%m-%d')
                    if paid_date < cut_date:
                        outstanding = 0
                        break
                if related_invoice.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                    related_invoice_amount = (-1) * (related_invoice.document_amount)
                else:
                    related_invoice_amount = related_invoice.document_amount
                outstanding += related_invoice_amount
                # if start.journal_id in [31267]:
                #     print('trans_id', transaction.id, outstanding)
                if self_type == 'AR':
                    other_trans = Transaction.objects.filter(is_hidden=False, related_invoice_id=related_invoice.id,\
                        journal__journal_type__in=[dict(TRANSACTION_TYPES)['AR Invoice']])\
                        .exclude(id=transaction.id).exclude(transaction_date__gt=cutoff_date).exclude(id__gt=transaction.id)
                else:
                    other_trans = Transaction.objects.filter(is_hidden=False, related_invoice_id=related_invoice.id,\
                        journal__journal_type__in=[dict(TRANSACTION_TYPES)['AP Invoice']])\
                        .exclude(id=transaction.id).exclude(journal__document_date__gt=cutoff_date).exclude(id__gt=transaction.id)
                for trans in other_trans:
                    if trans.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
                        outstanding += (-1) * (trans.total_amount)
                    else:
                        outstanding += trans.total_amount
                    # if start.journal_id in [31267]:
                    #     print('trans_id', trans.id, outstanding)
                transaction = Transaction.objects.filter(is_hidden=False, journal_id=related_invoice.id)\
                    .exclude(related_invoice_id__isnull=True).first()
            except Exception as e:
                print('journal_id_error', start.journal_id)
                print('get_related_outstanding : ERROR : ', e)
                transaction = None
        # if start.journal_id in [31267]:
        #     print('journal_id', start.journal_id)
        #     print('outstanding', outstanding)
        return outstanding
    
    # test function for u-amount
    # def update_rel_outs_amount(self):
    #     # if not self.outstanding_amount == 0:
    #     #     return False

    #     full_transaction_list = self.related_invoice.select_related('journal').filter(
    #         # journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
    #         journal__status=int(STATUS_TYPE_DICT['Posted'])
    #     ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True
    #     ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True).order_by('transaction_date', 'id')
    #     # check if the journal assign to other
    #     # if it is then we can consider it is fully paid, regardless of amount
    #     # in such case the amount, will be transferred to the related journal
    #     # transaction = Transaction.objects.filter(journal=self, journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
    #     #                                          ).exclude(journal__reverse_reconciliation=True)\
    #     #     .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True).exclude(related_invoice_id=None).aggregate(
    #     #         total=Coalesce(Sum('journal__outstanding_amount'), Value(0)))

    #     payment_total = 0
    #     # payment_total += abs(transaction['total'])
    #     if self.journal_type in [dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AP Payment']] and self.customer_unapplied != 0:
    #         total_amount = self.customer_unapplied * (-1) if self.customer_unapplied > 0 else self.customer_unapplied
    #     elif self.document_type == DOCUMENT_TYPE_DICT['Credit Note'] or self.document_type == DOCUMENT_TYPE_DICT['Unapplied Cash']:  # Credit Note
    #         total_amount = self.total_amount * (-1)
    #     else:
    #         total_amount = self.total_amount - abs(self.adjustment_amount) - abs(self.discount_amount)
    #     if full_transaction_list:
    #         if self.customer:
    #             full_transaction_list = full_transaction_list.filter(journal__customer_id=self.customer_id)
    #         elif self.supplier:
    #             full_transaction_list = full_transaction_list.filter(journal__supplier_id=self.supplier_id)

    #         # is_credit_journal = self.journal.first().is_credit_account if self.journal.first() else False
    #         for transaction in full_transaction_list:
    #             # if self.id == 11896:
    #             #     print('rel_transaction', transaction.id)
    #             payment_amount = 0
    #             if transaction.journal.document_type == DOCUMENT_TYPE_DICT['Adjustment']:
    #                 payment_amount += (transaction.amount + transaction.tax_amount)
    #             # elif transaction.is_credit_account == is_credit_journal:
    #             #     payment_amount += (transaction.amount + transaction.tax_amount)
    #             elif transaction.journal.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
    #                 # if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
    #                 #     payment_amount -= (transaction.amount + transaction.tax_amount)
    #                 # else:
    #                 payment_amount += (transaction.amount + transaction.tax_amount)
    #             elif transaction.journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
    #                 # if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
    #                 #     payment_amount += (transaction.amount + transaction.tax_amount)
    #                 # else:
    #                 payment_amount -= (transaction.amount + transaction.tax_amount)
    #             elif self.journal_type in [dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AP Payment']] and self.customer_unapplied != 0:
    #                 payment_amount -= (transaction.amount + transaction.tax_amount)
    #             elif self.document_type == DOCUMENT_TYPE_DICT['Unapplied Cash']:  # Credit Note
    #                 payment_amount -= (transaction.amount + transaction.tax_amount)
    #             elif transaction.journal.journal_type in [dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AP Payment']]:
    #                 if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
    #                     payment_amount -= (transaction.amount + transaction.tax_amount)
    #                 else:
    #                     payment_amount += (transaction.amount + transaction.tax_amount)
    #             elif transaction.journal.document_type == DOCUMENT_TYPE_DICT['Unapplied Cash']:  # Credit Note
    #                 if self.document_type == DOCUMENT_TYPE_DICT['Credit Note']:
    #                     payment_amount -= (transaction.amount + transaction.tax_amount)
    #                 else:
    #                     payment_amount += (transaction.amount + transaction.tax_amount)
    #             else:
    #                 payment_amount += (transaction.amount + transaction.tax_amount)


    #             # if self.id == 11896:
    #             #     print('total_amount', total_amount)
    #             #     print('payment_amount', payment_amount)

    #             # if payment_amount > 0:
    #             payment_total += payment_amount
    #             outstanding = total_amount - payment_total
    #             # if self.id == 11896:
    #             #     print('payment_total', payment_total)
    #             #     print('outstanding', outstanding)
    #             if self.journal_type in [dict(TRANSACTION_TYPES)['AR Invoice'], dict(TRANSACTION_TYPES)['AP Invoice']] and\
    #                 not self.document_type == DOCUMENT_TYPE_DICT['Credit Note'] and outstanding < 0:
    #                 outstanding = 0

    #             transaction.related_journal_outstanding = outstanding
    #             transaction.save()

    #     return True


class FiscalCalendar(models.Model):
    fiscal_year = models.CharField(max_length=4, null=True)
    period = models.IntegerField(default=0)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    is_ap_locked = models.BooleanField(default=False)
    is_ar_locked = models.BooleanField(default=False)
    is_gl_locked = models.BooleanField(default=False)
    is_bank_locked = models.BooleanField(default=False)
    is_ic_locked = models.BooleanField(default=False)
    is_sp_locked = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    is_adj_locked = models.BooleanField(default=False)
    is_cls_locked = models.BooleanField(default=False)


class Revaluation_count(models.Model):
    year_rev = models.IntegerField(default=0)
    period_rev = models.IntegerField(default=0)
    rev_count = models.IntegerField(default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=50, null=True)
    remark = models.CharField(max_length=50, null=True)


class RevaluationLogs(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    journal_type = models.IntegerField(default=dict(TRANSACTION_TYPES)['Undefined'])
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    revaluation_date = models.DateField(default=date.today)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    rate_date = models.DateField(default=date.today, null=True)
    rate_type = models.CharField(max_length=50, null=True, choices=RATE_TYPES)
    posting_sequence = models.CharField(max_length=50, null=True)
    posting_date = models.DateField(default=date.today, null=True)
    revaluation_method = models.IntegerField(default=dict(REVALUATION_METHODS)['Undefined'], null=True)

    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class RevaluationDetails(models.Model):
    posting = models.ForeignKey(RevaluationLogs, on_delete=models.CASCADE, null=True)
    document_no = models.CharField(max_length=50, null=True)
    document_date = models.DateField(default=date.today, null=True)
    due_date = models.DateField(default=date.today, null=True)
    source_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    prior_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    rev_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    prior_functional = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    new_functional = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    gain_loss = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.CASCADE, null=True)

    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class Schedule(models.Model):
    code = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=60, null=True)
    user_mode = models.IntegerField(default=0, choices=RECURRING_USER_MODE)
    recur_period = models.IntegerField(default=RECURRING_PERIOD_DICT['Daily'])

    daily_frequency = models.IntegerField(default=0)  # Every x days
    weekly_frequency = models.IntegerField(default=0)  # Every x weeks
    monthly_frequency = models.IntegerField(default=0)  # Every x months
    monthly_choice = models.IntegerField(default=0)  # mothly choice option
    yearly_choice = models.IntegerField(default=0)  # yearly choice option
    daily_choice = models.IntegerField(default=0)  # daily choice option

    frequency_week_of_month = models.IntegerField(default=0)  # On xth week of month
    frequency_weekday_index = models.IntegerField(default=0)  # On xth weekday
    frequency_bimonthly_date1 = models.IntegerField(default=0)  # On xth day of month
    frequency_bimonthly_date2 = models.IntegerField(default=0)  # On yth day of month
    frequency_date = models.IntegerField(default=0)  # On xth day of month
    frequency_month = models.IntegerField(default=0)  # On xth month

    # End Use
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class RecurringBatch(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    batch_no = models.CharField(max_length=50, null=True)
    batch_date = models.DateField(default=date.today)
    description = models.CharField(max_length=250, null=True)
    batch_type = models.IntegerField(default=dict(TRANSACTION_TYPES)['Undefined'])
    document_type = models.CharField(max_length=2, default=DOCUMENT_TYPE_DICT['Undefined'], choices=DOCUMENT_TYPES)
    no_entries = models.IntegerField(default=0)
    batch_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount after tax
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    input_type = models.CharField(max_length=2, default=INPUT_TYPE_DICT['Undefined'], choices=INPUT_TYPES)
    posting_sequence = models.CharField(max_length=50, null=True)
    status = models.IntegerField(default=int(STATUS_TYPE_DICT['Undefined']))
    update_date = models.DateField(auto_now=True)
    create_date = models.DateField(auto_now_add=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    related_batch_id = models.IntegerField(default=0)
    source_ledger = models.CharField(max_length=50, null=True, choices=SOURCE_LEDGER)
    flag = models.CharField(max_length=1, choices=FLAG_TYPE, default=0)

class RecurringEntry(models.Model):
    code = models.CharField(max_length=50, null=True)
    re_description = models.CharField(max_length=60, null=True)
    description = models.CharField(max_length=60, null=True)
    name = models.CharField(max_length=4000, null=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True)
    start_date = models.DateField(default=date.today)
    expire_date = models.DateField(null=True)
    run_date = models.DateField(null=True)
    action_date = models.DateField(null=True)
    maintained_date = models.DateField(null=True)
    is_expire = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    journal_desc = models.CharField(max_length=60, null=True)
    source_type = models.CharField(max_length=50, null=True, choices=SOURCE_TYPES)  # ==> Use For 5: GL
    entry_mode = models.IntegerField(default=0, choices=RECURRING_ENTRY_MODE)
    is_auto_reverse = models.BooleanField(default=False)
    exch_rate_type = models.CharField(max_length=20, null=True)
    exch_rate = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, null=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)

    orig_exch_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)
    orig_exch_rate_fk = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, null=True,
                                          related_name="re_orig_exch_rate_fk")
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    rounding_acc = models.CharField(max_length=60, null=True)

    po_number = models.CharField(max_length=50, null=True)
    order_number = models.CharField(max_length=50, null=True)

    debit = models.DecimalField(max_digits=20, decimal_places=7, default=0)
    credit = models.DecimalField(max_digits=20, decimal_places=7, default=0)
    balance = models.DecimalField(max_digits=20, decimal_places=7, default=0)

    reverse_to_period = models.CharField(max_length=1, null=True, choices=REVERSE_TO_PERIOD_LIST)
    reverse_to_period_val = models.DateField(null=True)
    perd_month = models.IntegerField(default=0)
    perd_year = models.IntegerField(default=0)

    journal_type = models.IntegerField(default=dict(TRANSACTION_TYPES)['Undefined'])
    document_type = models.CharField(
        max_length=2, default=DOCUMENT_TYPE_DICT['Undefined'], choices=DOCUMENT_TYPES)
    transaction_type = models.CharField(max_length=2,
                                        default="0")  # ==> PAYMENT_TRANSACTION_TYPES or RECEIPT_TRANSACTION_TYPES
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, null=True,
                                 related_name="rec_entry_journal_customer")
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.CASCADE, null=True,
                                 related_name="rec_entry_journal_supplier")
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    document_number = models.CharField(max_length=50, null=True)
    is_manual_doc = models.BooleanField(default=False)
    # Add invoice_number for Misc Payment/Receipt entry
    invoice_number = models.CharField(max_length=50, null=True)
    posting_date = models.DateField(null=True)
    account_set = models.ForeignKey(AccountSet, on_delete=models.CASCADE, null=True, related_name="rec_entry_journal_account_set")
    amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    tax_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    document_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount related to GR/DO invoice
    # Use for 3: AR Receipt; 4: AP Payment;
    payment_number = models.IntegerField(default=1)  # count the times an invoice got pay
    paid_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Paided-amount of invoice
    outstanding_amount = models.DecimalField(max_digits=20, decimal_places=6,
                                             default=0)  # Havent paid yet - amount of invoice
    is_fully_paid = models.BooleanField(default=False)
    reference = models.CharField(max_length=50, null=True)

    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True)
    payment_code = models.ForeignKey(PaymentCode, on_delete=models.CASCADE, null=True)
    payment_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True,
                                        related_name="rec_entry_payment_refer_account")
    payment_check_number = models.CharField(max_length=50, null=True)
    payment_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    payment_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, related_name="rec_entry_journal_currency")
    original_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    original_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True,
                                          related_name="rec_entry_original_currency")

    receipt_unapplied = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    customer_unapplied = models.DecimalField(max_digits=20, decimal_places=6, default=0)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)
    batch = models.ForeignKey(RecurringBatch, on_delete=models.CASCADE, null=True)


class RecurringEntryDetail(models.Model):
    rec_entry = models.ForeignKey(RecurringEntry, on_delete=models.CASCADE, null=True)

    reference = models.CharField(max_length=50, null=True)
    description = models.CharField(max_length=60, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)

    is_debit_account = models.BooleanField(default=0)
    is_credit_account = models.BooleanField(default=0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True)
    source_debit = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    source_credit = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    journal_date = models.DateField(auto_now_add=True)

    source_type = models.CharField(max_length=50, null=True, choices=SOURCE_TYPES)  # ==> Use For 5: GL
    exch_rate = models.ForeignKey(ExchangeRate, on_delete=models.CASCADE, null=True)
    exch_rate_date = models.DateField(auto_now_add=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=10, default=0)

    func_debit = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    func_credit = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    comment = models.CharField(max_length=60, null=True)
    remark = models.CharField(max_length=60, null=True)

    tax = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True)
    distribution_code = models.ForeignKey(DistributionCode, on_delete=models.CASCADE, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount before tax
    tax_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    total_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount after tax
    is_tax_include = models.BooleanField(default=False)
    is_tax_transaction = models.BooleanField(default=False)
    is_manual_tax_input = models.BooleanField(default=False)
    is_auto_exch = models.BooleanField(default=False)

    document_number = models.CharField(max_length=50, null=True)
    document_type = models.CharField(
        max_length=2, default=DOCUMENT_TYPE_DICT['Undefined'], choices=DOCUMENT_TYPES)
    document_date = models.DateField(null=True)
    due_date = models.DateField(null=True)
    payment_number = models.IntegerField(default=1)
    pending_balance = models.DecimalField(max_digits=20, decimal_places=7, default=0)
    net_balance = models.DecimalField(max_digits=20, decimal_places=7, default=0)
    applied_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    original_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)
    discount_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount discount
    adjustment_amount = models.DecimalField(max_digits=20, decimal_places=6, default=0)  # Amount adjustment (+/-)
    related_invoice = models.ForeignKey(
        "accounting.Journal", on_delete=models.CASCADE, null=True, related_name='re_related_invoice')

    # End Use
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class APGLIntegration(models.Model):
    transaction_type = models.CharField(max_length=100)
    transaction_field = models.CharField(max_length=100)

    # End Use
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)


class APGLIntegrationDetail(models.Model):
    parent = models.ForeignKey(APGLIntegration, on_delete=models.CASCADE, null=True)
    segment_0 = models.CharField(max_length=50, null=True)
    segment_1 = models.CharField(max_length=50, null=True)
    segment_2 = models.CharField(max_length=50, null=True)
    segment_3 = models.CharField(max_length=50, null=True)
    segment_4 = models.CharField(max_length=50, null=True)

    # End Use
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class ARGLIntegration(models.Model):
    transaction_type = models.CharField(max_length=100)
    transaction_field = models.CharField(max_length=100)

    # End Use
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_active = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)


class ARGLIntegrationDetail(models.Model):
    parent = models.ForeignKey(ARGLIntegration, on_delete=models.CASCADE, null=True)
    segment_0 = models.CharField(max_length=50, null=True)
    segment_1 = models.CharField(max_length=50, null=True)
    segment_2 = models.CharField(max_length=50, null=True)
    segment_3 = models.CharField(max_length=50, null=True)
    segment_4 = models.CharField(max_length=50, null=True)

    # End Use
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class AROptions(models.Model):
    invoice_prefix = models.CharField(max_length=6, null=True, default='IN')
    invoice_length = models.IntegerField(null=True, default=22)
    invoice_next_number = models.IntegerField(null=True, default=1)
    cnote_prefix = models.CharField(max_length=6, null=True, default='CN')
    cnote_length = models.IntegerField(null=True, default=22)
    cnote_next_number = models.IntegerField(null=True, default=1)
    dnote_prefix = models.CharField(max_length=6, null=True, default='DN')
    dnote_length = models.IntegerField(null=True, default=22)
    dnote_next_number = models.IntegerField(null=True, default=1)
    interest_prefix = models.CharField(max_length=6, null=True, default='INT')
    interest_length = models.IntegerField(null=True, default=22)
    interest_next_number = models.IntegerField(null=True, default=1)
    recurring_prefix = models.CharField(max_length=6, null=True, default='RC')
    recurring_length = models.IntegerField(null=True, default=22)
    recurring_next_number = models.IntegerField(null=True, default=1)
    prepayment_prefix = models.CharField(max_length=6, null=True, default='PP')
    prepayment_length = models.IntegerField(null=True, default=22)
    prepayment_next_number = models.IntegerField(null=True, default=1)
    ucash_prefix = models.CharField(max_length=6, null=True, default='UC')
    ucash_length = models.IntegerField(null=True, default=22)
    ucash_next_number = models.IntegerField(null=True, default=1)
    adjustment_prefix = models.CharField(max_length=6, null=True, default='AD')
    adjustment_length = models.IntegerField(null=True, default=22)
    adjustment_next_number = models.IntegerField(null=True, default=1)
    receipt_prefix = models.CharField(max_length=6, null=True, default='PY')
    receipt_length = models.IntegerField(null=True, default=22)
    receipt_next_number = models.IntegerField(null=True, default=1)
    refund_prefix = models.CharField(max_length=6, null=True, default='RF')
    refund_length = models.IntegerField(null=True, default=22)
    refund_next_number = models.IntegerField(null=True, default=1)

    aging_period_1 = models.IntegerField(null=True, default=31)
    aging_period_2 = models.IntegerField(null=True, default=61)
    aging_period_3 = models.IntegerField(null=True, default=91)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)


class APOptions(models.Model):
    recurring_pay_prefix = models.CharField(max_length=6, null=True, default='RP')
    recurring_pay_length = models.IntegerField(null=True, default=22)
    recurring_pay_next_number = models.IntegerField(null=True, default=1)
    prepayment_prefix = models.CharField(max_length=6, null=True, default='PP')
    prepayment_length = models.IntegerField(null=True, default=22)
    prepayment_next_number = models.IntegerField(null=True, default=1)
    adjustment_prefix = models.CharField(max_length=6, null=True, default='AD')
    adjustment_length = models.IntegerField(null=True, default=22)
    adjustment_next_number = models.IntegerField(null=True, default=1)
    payment_prefix = models.CharField(max_length=6, null=True, default='PY')
    payment_length = models.IntegerField(null=True, default=22)
    payment_next_number = models.IntegerField(null=True, default=1)

    aging_period_1 = models.IntegerField(null=True, default=31)
    aging_period_2 = models.IntegerField(null=True, default=61)
    aging_period_3 = models.IntegerField(null=True, default=91)

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    create_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    update_by = models.CharField(max_length=50, null=True)
    is_hidden = models.BooleanField(default=False)

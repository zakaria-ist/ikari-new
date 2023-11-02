import json
from collections import namedtuple
from decimal import Decimal
from functools import lru_cache, wraps
from django.db.models import Q, Sum, F, Value
from django.db.models.functions import Coalesce
from accounting.models import Journal
from customers.models import Customer
from suppliers.models import Supplier
from transactions.models import Transaction
from utilities.common import get_customer_filter_range, get_vendor_filter_range
from utilities.constants import TRANSACTION_TYPES, DOCUMENT_TYPE_DICT, STATUS_TYPE_DICT
import time


AR_collections = namedtuple('AR_collections', [
                            'journal_item_list', 'adjustment_journal_list', 'journal_amount_list'])
AP_collections = namedtuple('AP_collections', [
                            'journal_item_list', 'adjustment_journal_list', 'journal_amount_list'])


def get_due_period(diff_day: int, period_current: int, period_1st: int,
                   period_2nd: int, period_3rd: int, total: Decimal) -> dict:
    """ Calculate due date compare with cutoff date """
    data = {
        'total_current': 0,
        'total_1st': 0,
        'total_2nd': 0,
        'total_3rd': 0,
        'total_4th': 0,
        'due_day_calculate': 0
    }
    if diff_day <= period_current:
        data['total_current'] = total
        data['due_day_calculate'] = period_current
    elif period_current < diff_day <= period_1st:
        data['total_1st'] = total
        data['due_day_calculate'] = period_1st
    elif period_1st < diff_day <= period_2nd:
        data['total_2nd'] = total
        data['due_day_calculate'] = period_2nd
    elif period_2nd < diff_day <= period_3rd:
        data['total_3rd'] = total
        data['due_day_calculate'] = period_3rd
    else:
        data['total_4th'] = total
        data['due_day_calculate'] = period_3rd + 1
    return data


def get_ar_transactions(
        is_detail_report: bool,
        company_id: int,
        cus_no: str,
        cutoff_date: str,
        date_type: str,
        paid_full: str,
        doc_type_array: list
) -> AR_collections:
    """
    Processing all Journal to get related AR transactions
    """
    cust_item = Customer.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    t0 = time.time()
    if cus_no != '0':
        id_cus_range = cus_no.split(',')
        cust_id_from = int(id_cus_range[0])
        cust_id_to = int(id_cus_range[1])
        if cust_id_from > 0 and cust_id_to > 0:
            customer_range = get_customer_filter_range(company_id,
                                                       int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                                       int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')
            cust_item = cust_item.filter(pk__in=customer_range)
    cust_list = cust_item.values_list('code', flat=True).distinct()
    # cust_list = ['TR-IKA', ]

    # AR INVOICE INCLUDES THE PY, INV, CR, DB, IT
    journal_item_list = Journal.objects.select_related('customer').prefetch_related('related_invoice').filter(
        # ~Q(total_amount=0),
        Q(journal_type=dict(TRANSACTION_TYPES)['AR Receipt'], customer_unapplied__gt=0) |
        Q(journal_type=dict(TRANSACTION_TYPES)['AR Receipt'], customer_unapplied__lt=0) |
        Q(document_type=DOCUMENT_TYPE_DICT['Unapplied Cash']) | 
        Q(journal_type=dict(TRANSACTION_TYPES)['AR Invoice']),
        company_id=company_id, is_hidden=0, document_type__in=doc_type_array,
        customer__code__in=cust_list, status=int(STATUS_TYPE_DICT['Posted'])
    ).exclude(reverse_reconciliation=True)

    if cutoff_date:
        if int(date_type) == 2:
            journal_item_list = journal_item_list.filter(posting_date__lte=cutoff_date).order_by(
                'customer__code', 'currency__code', 'document_date', '-document_type')
        else:
            journal_item_list = journal_item_list.filter(document_date__lte=cutoff_date).order_by(
                'customer__code', 'currency__code', 'document_date', '-document_type')
        if int(paid_full) != 1:
            journal_item_list = journal_item_list.filter(
                Q(fully_paid_date__isnull=True) | Q(fully_paid_date__gt=cutoff_date)
            )

    fully_paid_adjustments = []
    adjustment_journal_list = {}
    excludeList = []
    journal_amount_list = {}
    if int(paid_full) == 1:
        journal_item_ids = journal_item_list.filter().values('id')
        journal_item_list = Journal.objects.filter(
            Q(id__in=journal_item_ids) |
            Q(journal_type=dict(TRANSACTION_TYPES)[
                'AR Receipt'], customer_unapplied__gt=0, document_date__lte=cutoff_date,
                status=int(STATUS_TYPE_DICT['Posted']), is_hidden=0, customer__code__in=cust_list) |
            Q(company_id=company_id, document_type='0', document_date__lte=cutoff_date,
              journal_type=dict(TRANSACTION_TYPES)['AR Receipt'], customer__code__in=cust_list,
              status=int(STATUS_TYPE_DICT['Posted']), is_hidden=0)).exclude(
            customer_id__isnull=True).order_by('customer__code', 'currency__code', 'document_date', 'document_number')

    else:
        journal_item_list = journal_item_list.order_by('customer__code', 'currency__code', 'document_date',
                                                       'document_type', 'document_number')

        # filter the latest payments
        journal_ids = journal_item_list.values_list('id', flat=True)

        last_payment_journal_ids = Transaction.objects.filter(related_invoice_id__in=journal_ids,
            journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
        ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True
        ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']
        ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['AD']
        ).exclude(is_hidden=True
        ).exclude(related_journal_outstanding__gt=0
        ).exclude(related_journal_outstanding__lt=0
        ).order_by('-transaction_date', '-id'
        ).values_list('related_invoice_id', flat=True)

        journal_item_list = journal_item_list.exclude(id__in=last_payment_journal_ids)

        for journal in journal_item_list:
            # if journal in journal_item_list: 
            # if journal.check_is_fully_paid(cutoff_date=cutoff_date):
            #     # journal_item_list = journal_item_list.exclude(id=journal.id)
            #     excludeList.append(journal.id)

            #     adjustment_transactions = journal.related_invoice.filter(
            #         journal__document_type=DOCUMENT_TYPE_DICT['Adjustment'], journal__status=int(STATUS_TYPE_DICT['Posted']),
            #         journal__document_date__lte=cutoff_date, journal__customer_id=journal.customer_id
            #     ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True).exclude(
            #         journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True)

            #     for adjustment_trx in adjustment_transactions:
            #         fully_paid_adjustments.append(adjustment_trx.journal)

            #     related_invoice_ids = journal.related_invoice.filter(
            #         journal__document_date__lte=cutoff_date, journal__customer_id=journal.customer_id, journal__status=int(STATUS_TYPE_DICT['Posted']),
            #     ).exclude(journal_id__isnull=True)\
            #         .exclude(journal__reverse_reconciliation=True)\
            #         .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL'])\
            #         .exclude(is_hidden=True).values_list('journal_id', flat=True)
            #     if not journal.fully_paid_date:
            #         paid_journals = Journal.objects.filter(id__in=related_invoice_ids).order_by('document_date')
            #         if len(paid_journals):
            #             last_paid_journal = paid_journals.last()
            #             last_date = last_paid_journal.document_date
            #             journal.fully_paid_date = last_paid_journal.document_date
            #             for paid_journal in paid_journals:
            #                 if paid_journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt'] \
            #                     and paid_journal.outstanding_amount == 0:
            #                         paid_journal.fully_paid_date = last_date
            #                 else:
            #                     paid_journal.fully_paid_date = last_date
            #                 paid_journal.save()
            #         else:
            #             last_date = journal.document_date
            #             if journal.journal_type == dict(TRANSACTION_TYPES)['AR Receipt'] \
            #                 and journal.outstanding_amount == 0:
            #                     journal.fully_paid_date = last_date
            #             else:
            #                 journal.fully_paid_date = last_date
            #         journal.save()

            #     # journal_item_list = journal_item_list.exclude(id__in=related_invoice_ids)
            #     excludeList.extend(related_invoice_ids)
            # else:
                # current_customer = journal.customer
                # if not previous_customer:
                #     previous_customer = current_customer

                # if previous_customer == current_customer:
                #     t_amount = calculate_total_amount(journal, journal.journal_type, cutoff_date)
                #     # Invoice is over paid
                #     if journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice'] and\
                #          journal.document_type != DOCUMENT_TYPE_DICT['Credit Note'] and t_amount < 0:
                #         t_amount = 0
                #         sp_journals.append(journal.id)
                #     customer_total_amount += t_amount
                # else:
                #     if customer_total_amount == 0:
                #         journal_item_list = journal_item_list.exclude(customer_id=previous_customer.id)

                #     previous_customer = current_customer
                #     customer_total_amount = 0
                #     t_amount = calculate_total_amount(journal, journal.journal_type, cutoff_date)
                #     # Invoice is over paid
                #     if journal.journal_type == dict(TRANSACTION_TYPES)['AR Invoice'] and\
                #          journal.document_type != DOCUMENT_TYPE_DICT['Credit Note'] and t_amount < 0:
                #         t_amount = 0
                #         sp_journals.append(journal.id)
                #     customer_total_amount += t_amount
                # # Remove CR/DB journal that have been fully applied
                # cr_db_transactions = journal.related_invoice.filter(
                #     Q(journal__document_type=DOCUMENT_TYPE_DICT['Credit Note']) |
                #     Q(journal__document_type=DOCUMENT_TYPE_DICT['Debit Note']), journal__status=int(STATUS_TYPE_DICT['Posted']),
                #     journal__document_date__lte=cutoff_date, journal__supplier_id=journal.supplier_id,
                #     total_amount__lte=journal.total_amount
                # ).exclude(journal_id__isnull=True)\
                #     .exclude(journal__reverse_reconciliation=True)\
                #     .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL'])\
                #     .exclude(is_hidden=True)

                # for tx in cr_db_transactions:
                #     # if tx.total_amount <= journal.total_amount:
                #     journal_item_list = journal_item_list.exclude(id=tx.journal_id)
                #     tx.journal.fully_paid_date = tx.journal.document_date
                #     tx.journal.save()
            remaining_result = journal.has_outstanding(
                cutoff_date=cutoff_date)
            if not remaining_result[0]:
                if int(paid_full) != 1:
                    related_invoice_ids = journal.related_invoice.filter(
                        journal__document_date__lte=cutoff_date, 
                        journal__customer_id=journal.customer_id, 
                        journal__status=int(STATUS_TYPE_DICT['Posted']))\
                        .exclude(journal_id__isnull=True)\
                        .exclude(journal__reverse_reconciliation=True)\
                        .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL'])\
                        .exclude(is_hidden=True).values_list('journal_id', flat=True)

                    excludeList.extend(related_invoice_ids)

                    excludeList.append(journal.id)
                
                key = str(journal.id)
                journal_amount_list[key] = remaining_result[1]
            else:
                key = str(journal.id)
                journal_amount_list[key] = remaining_result[1]

            adjustment_transactions = journal.related_invoice.filter(
                journal__document_type=DOCUMENT_TYPE_DICT['Adjustment'],
                journal__document_date__lte=cutoff_date, journal__customer_id=journal.customer_id,
                journal__status=int(STATUS_TYPE_DICT['Posted']),
            ).exclude(journal_id__isnull=True)\
                .exclude(journal__reverse_reconciliation=True)\
                .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL'])\
                .exclude(is_hidden=True)
            adjustment = adjustment_transactions.aggregate(
                total=Coalesce(Sum(F('amount') + F('tax_amount')), Value(0)))

            for adjustment_trx in adjustment_transactions:
                adjustment_journal_list.update(
                    {
                        str(journal.id): {
                            'doc': adjustment_trx.journal.document_number,
                            'amount': adjustment['total'],
                            'doc_date': adjustment_trx.transaction_date
                        }
                    }
                )
        # if customer_total_amount == 0 and previous_customer:
        #     journal_item_list = journal_item_list.exclude(customer_id=previous_customer.id)
    journal_item_list = journal_item_list.exclude(id__in=excludeList)
    if is_detail_report:
        # If Detail Report, include fully paid AD transactions for show.
        # If Summary Report, no need to include, will create mis-calculate.
        fully_paid_adjustments = Journal.objects.filter(id__in=[adj.id for adj in fully_paid_adjustments])
        for adj in fully_paid_adjustments:
            if not journal_item_list.filter(customer_id=adj.customer_id):
                fully_paid_adjustments = fully_paid_adjustments.exclude(customer_id=adj.customer_id)

        journal_item_list = (journal_item_list | fully_paid_adjustments)
    print('Time', time.time()-t0)
    
    journal_item_list = journal_item_list.order_by('customer__code', 'currency__code', 'document_date',
                                                   'document_number')
    return AR_collections(journal_item_list=journal_item_list, adjustment_journal_list=adjustment_journal_list, journal_amount_list=journal_amount_list)


def calculate_total_amount(journal, journal_type, cutoff_date):
    """
    Calculate total amount for related Journal remaining amount on cutoff_date
    """
    total_amount = 0
    if journal.customer:
        param = Q(journal__customer_id=journal.customer_id)
    elif journal.supplier:
        param = Q(journal__supplier_id=journal.supplier_id)

    full_transaction_list = journal.related_invoice.filter(
        param, journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted']),
    ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True)\
        .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True)
    credit_note = full_transaction_list.filter(journal__document_type=DOCUMENT_TYPE_DICT['Credit Note'], journal__document_date__lte=cutoff_date).aggregate(
        total=Coalesce(Sum(F('amount') + F('tax_amount')), Value(0)))
    debit_note = full_transaction_list.filter(journal__document_type=DOCUMENT_TYPE_DICT['Debit Note'], journal__document_date__lte=cutoff_date).aggregate(
        total=Coalesce(Sum(F('amount') + F('tax_amount')), Value(0)))
    transaction = full_transaction_list.filter(~Q(journal__document_type__in=(DOCUMENT_TYPE_DICT['Credit Note'], DOCUMENT_TYPE_DICT['Debit Note'])),
                                               transaction_date__lte=cutoff_date).aggregate(
        total=Coalesce(Sum(F('amount') + F('tax_amount')), Value(0)))
    transaction_adj = full_transaction_list.filter(~Q(journal__document_type__in=(DOCUMENT_TYPE_DICT['Credit Note'], DOCUMENT_TYPE_DICT['Debit Note'])),
                                                   transaction_date__lte=cutoff_date).aggregate(total=Coalesce(Sum('adjustment_amount'), Value(0)))

    if journal.document_type:
        if journal_type in [dict(TRANSACTION_TYPES)['AR Receipt'], dict(TRANSACTION_TYPES)['AP Payment']] and journal.customer_unapplied != 0:
            total_amount = journal.customer_unapplied * (-1)
            if total_amount < 0:
                total_amount += credit_note['total'] + debit_note['total'] + abs(transaction['total'])
            else:
                total_amount -= credit_note['total'] + debit_note['total'] + abs(transaction['total'])
        elif journal.document_type == DOCUMENT_TYPE_DICT['Credit Note'] or journal.document_type == DOCUMENT_TYPE_DICT['Unapplied Cash']:  # Credit Note
            total_amount = journal.total_amount * (-1)
            total_amount = total_amount + debit_note['total'] + transaction['total'] - credit_note['total'] + abs(transaction_adj['total'])
        elif journal.document_type == DOCUMENT_TYPE_DICT['Debit Note']:
            total_amount = journal.total_amount + debit_note['total'] - credit_note['total'] - transaction['total'] - abs(transaction_adj['total'])
        else:
            if journal_type in [dict(TRANSACTION_TYPES)['AP Invoice'], dict(TRANSACTION_TYPES)['AP Payment'], dict(TRANSACTION_TYPES)['GL']]:
                total_amount = journal.total_amount - credit_note['total'] + debit_note['total'] - abs(transaction['total'])
            else:
                total_amount = journal.total_amount - credit_note['total'] + debit_note['total'] - transaction['total'] - abs(transaction_adj['total'])

    return total_amount


# @lru_cache(maxsize=None)
def get_ap_transactions(
        company_id: int,
        cus_no: str,
        cutoff_date: str,
        date_type: str,
        paid_full: str,
        doc_type_array: tuple
) -> AP_collections:
    """
    Processing all Journal to get related AP transactions
    """
    t0 = time.time()
    cust_item = Supplier.objects.filter(is_hidden=0, company_id=company_id, is_active=1)
    # get part no
    if cus_no != '0':
        id_cus_range = cus_no.split(',')
        cust_id_from = int(id_cus_range[0])
        cust_id_to = int(id_cus_range[1])
        if cust_id_from > 0 and cust_id_to > 0:
            customer_range = get_vendor_filter_range(company_id,
                                                     int(cust_id_from) if int(cust_id_from) < int(cust_id_to) else int(cust_id_to),
                                                     int(cust_id_to) if int(cust_id_from) < int(cust_id_to) else int(cust_id_from), 'id')
            cust_item = cust_item.filter(pk__in=customer_range)
    # Get list of part no
    cust_list = cust_item.values_list('code', flat=True).distinct()
    journal_item_list = Journal.objects.select_related('supplier', 'currency').filter(
        # Q(journal_type=dict(TRANSACTION_TYPES)['AP Payment'], outstanding_amount__gt=0) |
        # Q(journal_type=dict(TRANSACTION_TYPES)['AP Payment'], outstanding_amount__lt=0) |
        # ~Q(total_amount=0), company_id=company_id, is_hidden=0, document_type__in=doc_type_array,
        Q(journal_type=dict(TRANSACTION_TYPES)['AP Invoice']),
        company_id=company_id, is_hidden=0, document_type__in=doc_type_array,
        supplier__code__in=cust_list, status=int(STATUS_TYPE_DICT['Posted'])
    ).exclude(reverse_reconciliation=True)

    if cutoff_date:
        if int(date_type) == 2:
            journal_item_list = journal_item_list.filter(posting_date__lte=cutoff_date).order_by(
                'supplier__code', 'currency__code', 'document_date', 'document_number')
        else:
            journal_item_list = journal_item_list.filter(document_date__lte=cutoff_date).order_by(
                'supplier__code', 'currency__code', 'document_date', 'document_number')

        if int(paid_full) != 1:
            journal_item_list = journal_item_list.filter(
                Q(fully_paid_date__isnull=True) | Q(fully_paid_date__gt=cutoff_date)
            )

    adjustment_journal_list = {}
    excludeList = []
    journal_amount_list = {}
    if int(paid_full) == 1:
        journal_item_ids = journal_item_list.filter().values('id')
        journal_item_list = Journal.objects.filter(Q(id__in=journal_item_ids) |
                                                   Q(journal_type=dict(TRANSACTION_TYPES)[
                                                     'AP Payment'], customer_unapplied__gt=0, document_date__lte=cutoff_date,
                                                     status=int(STATUS_TYPE_DICT['Posted']), is_hidden=0, supplier__code__in=cust_list) 
                                                    # |
                                                    # Q(company_id=company_id, document_type='0', document_date__lte=cutoff_date,
                                                    #     journal_type=dict(TRANSACTION_TYPES)['AP Payment'],
                                                    #     status=int(STATUS_TYPE_DICT['Posted']), is_hidden=0,
                                                    #     supplier__code__in=cust_list, status=int(STATUS_TYPE_DICT['Posted'])
                                                    # )
                                                   ).exclude(supplier_id__isnull=True).order_by('supplier__code',
                                                                                                'currency__code',
                                                                                                'document_date')
    else:
        journal_item_list = journal_item_list.order_by('supplier__code', 'currency__code', 'document_date',
                                                       'document_type', 'document_number')

        # previous_supplier = None
        # supplier_total_amount = 0

        # filter the latest payments
        journal_ids = journal_item_list.values_list('id', flat=True)
        last_payment_journal_ids = Transaction.objects.filter(related_invoice_id__in=journal_ids,
            journal__document_date__lte=cutoff_date, journal__status=int(STATUS_TYPE_DICT['Posted'])
        ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True
        ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']
        ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['AD']
        ).exclude(is_hidden=True
        ).exclude(related_journal_outstanding__gt=0
        ).exclude(related_journal_outstanding__lt=0
        ).order_by('-journal__document_date', '-id'
        ).values_list('related_invoice_id', flat=True)
        
        journal_item_list = journal_item_list.exclude(id__in=last_payment_journal_ids)

        for journal in journal_item_list:
            # if journal.id == 89:
                # print(journal.id, journal.document_number)
            # if journal in journal_item_list:
            # if journal.check_is_fully_paid(cutoff_date=cutoff_date):
            #     # journal_item_list = journal_item_list.exclude(id=journal.id)
            #     excludeList.append(journal.id)
            #     related_invoice_ids = journal.related_invoice.filter(
            #         journal__document_date__lte=cutoff_date, journal__supplier_id=journal.supplier_id, journal__status=int(STATUS_TYPE_DICT['Posted'])
            #     ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True)\
            #         .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True).values_list('journal_id', flat=True)

            #     if not journal.fully_paid_date:
            #         paid_journals = Journal.objects.filter(id__in=related_invoice_ids).order_by('document_date')
            #         if len(paid_journals):
            #             last_paid_journal = paid_journals.last()
            #             last_date = last_paid_journal.document_date
            #             journal.fully_paid_date = last_paid_journal.document_date
            #             for paid_journal in paid_journals:
            #                 paid_journal.fully_paid_date=last_date
            #                 paid_journal.save()
            #         else:
            #             last_date = journal.document_date
            #             journal.fully_paid_date = last_date
            #         journal.save()

            #     # journal_item_list = journal_item_list.exclude(id__in=related_invoice_ids)
            #     excludeList.extend(related_invoice_ids)
            # else:
                # current_supplier = journal.supplier
                # if not previous_supplier:
                #     previous_supplier = current_supplier

                # if previous_supplier == current_supplier:
                #     supplier_total_amount += calculate_total_amount(journal, journal.journal_type, cutoff_date)
                # else:
                #     if supplier_total_amount == 0:
                #         journal_item_list = journal_item_list.exclude(supplier_id=previous_supplier.id)

                #     previous_supplier = current_supplier
                #     supplier_total_amount = 0
                #     supplier_total_amount += calculate_total_amount(journal, journal.journal_type, cutoff_date)
                # cr_db_transactions = journal.related_invoice.filter(
                #     Q(journal__document_type=DOCUMENT_TYPE_DICT['Credit Note']) |
                #     Q(journal__document_type=DOCUMENT_TYPE_DICT['Debit Note']),
                #     journal__document_date__lte=cutoff_date, journal__supplier_id=journal.supplier_id,
                #     journal__status=int(STATUS_TYPE_DICT['Posted']),
                #     total_amount__lte=journal.total_amount
                # ).exclude(journal_id__isnull=True)\
                #     .exclude(journal__reverse_reconciliation=True)\
                #     .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL'])\
                #     .exclude(is_hidden=True)

                # for tx in cr_db_transactions:
                #     # if tx.total_amount <= journal.total_amount:
                #     journal_item_list = journal_item_list.exclude(id=tx.journal_id)
                #     tx.journal.fully_paid_date = tx.journal.document_date
                #     tx.journal.save()
            remaining_result = journal.has_outstanding(
                cutoff_date=cutoff_date)
            if not remaining_result[0]:
                key = str(journal.id)
                journal_amount_list[key] = remaining_result[1]
                if int(paid_full) != 1:
                    related_invoice_ids = journal.related_invoice.filter(
                        journal__document_date__lte=cutoff_date, 
                        journal__supplier_id=journal.supplier_id, 
                        journal__status=int(STATUS_TYPE_DICT['Posted'])
                        ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True
                        ).exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True).values_list('journal_id', flat=True)

                    excludeList.extend(related_invoice_ids)

                    excludeList.append(journal.id)
            else:
                key = str(journal.id)
                journal_amount_list[key] = remaining_result[1]

            adjustment_transactions = journal.related_invoice.filter(
                journal__document_type=DOCUMENT_TYPE_DICT['Adjustment'],
                journal__document_date__lte=cutoff_date, journal__supplier_id=journal.supplier_id,
                journal__status=int(STATUS_TYPE_DICT['Posted'])
            ).exclude(journal_id__isnull=True).exclude(journal__reverse_reconciliation=True)\
                .exclude(journal__journal_type=dict(TRANSACTION_TYPES)['GL']).exclude(is_hidden=True)
            adjustment = adjustment_transactions.aggregate(
                total=Coalesce(Sum(F('amount') + F('tax_amount')), Value(0)))

            for adjustment_trx in adjustment_transactions:
                adjustment_journal_list.update(
                    {
                        str(journal.id): {
                            'doc': adjustment_trx.journal.document_number,
                            'amount': adjustment['total'],
                            'doc_date': adjustment_trx.transaction_date
                        }
                    }
                )

        # if supplier_total_amount == 0 and previous_supplier:
        #     journal_item_list = journal_item_list.exclude(supplier_id=previous_supplier.id)
    print('TIME', time.time() - t0)
    journal_item_list = journal_item_list.exclude(id__in=excludeList)
    return AP_collections(journal_item_list=journal_item_list, adjustment_journal_list=adjustment_journal_list, journal_amount_list=journal_amount_list)

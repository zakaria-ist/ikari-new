from django.conf.urls import url

from accounting import views

urlpatterns = [
    url(r'^$', views.JournalList__asJson, name='index'),
    url(r'^landing_acc/$', views.page_acc, name='page_acc'),
    url(r'^list/(?P<journal_type>.*)/(?P<batch_id>.*)/$', views.load_list, name='journal_list'),
    url(r'^batch_list/(?P<batch_type>.*)/$', views.batch_list, name='batch_list'),
    url(r'^delete/batch_invocie/(?P<batch_id>.*)/$', views.batch_invocie_delete, name='batch_invocie_delete'),
    url(r'^payment/list/(?P<journal_type>.*)/$', views.payment_list, name='payment_list'),
    url(r'^general_ledger/list/(?P<journal_type>.*)/$', views.general_ledger_list, name='general_ledger_list'),

    # Reopen ARAP
    url(r'^reopen/ARAP/(?P<batch_id>.*)/$', views.reopen_ARAP, name='reopen_ARAP'),

    # AR journal
    url(r'^add/AR/(?P<batch_id>.*)/$', views.journal_AR_add, name='journal_AR_add'),
    url(r'^edit/AR/(?P<journal_id>.*)/$', views.journal_AR_edit, name='journal_AR_edit'),
    url(r'^delete/AR/(?P<journal_id>.*)/$', views.journal_AR_delete, name='journal_AR_delete'),
    url(r'^send/AR/(?P<batch_id>.*)/$', views.send_AR_batch, name='send_AR_batch'),
    url(r'^print/AP/$', views.print_AP_reports, name='print_AP_reports'),
    url(r'^print/AR_customers/$', views.print_customers_reports, name='print_customers_reports'),
    url(r'^print/AP_vendor/$', views.print_vend_reports, name='print_vend_reports'),
    url(r'^print/AR/$', views.print_AR_reports, name='print_AR_reports'),
    url(r'^print/AR/note/(?P<journal_id>.*)/$', views.print_AR_note_reports, name='print_AR_note_reports'),
    url(r'^print/GL/transaction_listing/$', views.print_Gl_transaction_listing, name='print_Gl_transaction_listing'),
    url(r'^payment/edit/AR/(?P<payment_id>.*)/$', views.payment_AR_edit, name='payment_AR_edit'),

    # AP journal
    url(r'^add/AP/(?P<batch_id>.*)/$', views.journal_AP_add, name='journal_AP_add'),
    url(r'^edit/AP/(?P<journal_id>.*)/$', views.journal_AP_edit, name='journal_AP_edit'),
    url(r'^delete/AP/(?P<journal_id>.*)/$', views.journal_AP_delete, name='journal_AP_delete'),
    url(r'^send/AP/(?P<batch_id>.*)/$', views.send_AP_batch, name='send_AP_batch'),

    # AP Payment
    url(r'^add/APPayment/(?P<batch_id>.*)/$', views.journal_AP_Payment_add, name='journal_AP_Payment_add'),
    url(r'^edit/APPayment/(?P<batch_id>.*)/(?P<journal_id>.*)/$', views.journal_AP_Payment_edit,
        name='journal_AP_Payment_edit'),
    url(r'^delete/APPayment/(?P<journal_id>.*)/$', views.journal_AP_Payment_delete, name='journal_AP_Payment_delete'),
    url(r'^delete/Batch/APPayment/(?P<batch_id>.*)/$', views.journal_AP_Payment_batch_delete,
        name='journal_AP_Payment_batch_delete'),
    url(r'^send/APPayment/(?P<batch_id>.*)/$', views.send_AP_Payment_batch, name='send_AP_Payment_batch'),


    # Payment Code
    url(r'^payment_codes_list/(?P<source_type>.*)/$', views.payment_codes_list, name='payment_codes_list'),
    url(r'^payment_codes_add/(?P<source_type>.*)/$', views.payment_code_add, name='payment_code_add'),
    url(r'^payment_codes_edit/(?P<payment_code_id>.*)/$', views.payment_code_edit, name='payment_code_edit'),
    url(r'^payment_code_delete/(?P<payment_code_id>.*)/$', views.payment_code_delete, name='payment_code_delete'),

    # Datatable Section
    url(r'^supplier_list/$', views.SupplierList__asJson, name='AccSupplierList__asJson'),
    url(r'^supplier_document_list/$', views.SupplierDocumentsList_as_json, name='AccSupplierDocumentsList_as_json'),
    url(r'^customer_document_list/$', views.CustomerDocumentsList_as_json, name='AccCustomerDocumentsList_as_json'),
    url(r'^customer_list/$', views.CustomerList__asJson, name='AccCuscomterList__asJson'),
    url(r'^document_list_aplly/$', views.ApllyDocumentsList_as_json, name='ApllyDocumentsList_as_json'),
    url(r'^journal_list/(?P<journal_type>.*)/(?P<batch_id>.*)/$', views.JournalList__asJson,
        name='JournalList__asJson'),
    url(r'^batch_list_json/(?P<batch_type>.*)/$', views.BatchList__asJson, name='BatchList__asJson'),
    url(r'^payment_list/(?P<journal_type>.*)/paging$', views.PaymentList__asJson, name='PaymentList__asJson'),
    url(r'^account_list/$', views.APAccountList__asJson, name='AccAPAccountList__asJson'),
    url(r'^exchange_rate_list/$', views.ExchangeRateList__asJson, name='ExchangeRateList__asJson'),
    url(r'^exchange_rate_day/(?P<currency_id>.*)/(?P<days>.*)/$', views.ExchangeRateDay__asJson,
        name='ExchangeRateDay__asJson'),

    url(r'^migration/netchange/(?P<year>.*)/(?P<month>.*)/$', views.Migrate_GL_netchange, name='Migrate_GL_netchange'),
    url(r'^migration/opening/(?P<year>.*)/(?P<month>.*)/$', views.Migrate_GL_open, name='Migrate_GL_opening'),
    url(r'^migration/closing/(?P<year>.*)/$', views.Migrate_GL_closing, name='Migrate_GL_Closing'),
    url(r'^migration/$', views.create_migration, name='create_migration'),

    # TAX
    url(r'^clear_tax_tracking/(?P<from_date>.*)/(?P<to_date>.*)/(?P<type>.*)/$', views.clear_tax_tracking, name='clear_tax_tracking'),


    url(r'^ExchangeRateHistory__asJson/$', views.ExchangeRateHistory__asJson, name='ExchangeRateHistory__asJson'),
    url(r'^document_payment_list/$', views.PaymentDocumentsList_as_json, name='AccPaymentDocumentsList_as_json'),

    # Auto search when focusout input
    url(r'^search_supplier/$', views.search_supplier_customer, name='AccSearch_supplier_customer'),
    url(r'^search_customer/$', views.search_supplier_customer, name='AccSearch_supplier_customer'),
    url(r'^search_accountset/$', views.search_accountset, name='AccSearch_accountset'),
    url(r'^search_document/$', views.search_document, name='AccSearch_document'),
    url(r'^load_currency/$', views.load_currency, name='AccLoad_currency'),
    url(r'^load_supplier/$', views.load_supplier, name='AccLoad_supplier'),
    url(r'^load_supplier_select/$', views.load_supplier_Select, name='load_supplier_select'),
    url(r'^load_payment_type/$', views.load_payment_type, name='AccLoad_payment_type'),  # GL journal
    # GL
    url(r'^general_ledger_list/(?P<journal_type>.*)/paging$', views.GLList__asJson, name='GLList__asJson'),
    url(r'^add/GL/(?P<batch_id>.*)/$', views.journal_GL_add, name='journal_GL_add'),
    url(r'^edit/GL/(?P<journal_id>.*)/$', views.journal_GL_edit, name='journal_GL_edit'),
    url(r'^view/GL/(?P<journal_id>.*)/$', views.journal_GL_view, name='journal_GL_view'),
    url(r'^delete/gl_batch/(?P<batch_id>.*)/$', views.gl_batch_delete, name='gl_batch_delete'),
    url(r'^delete/GL/(?P<journal_id>.*)/$', views.journal_GL_delete, name='journal_GL_delete'),
    url(r'^delete/GL_JE_TRX/(?P<trx_id>.*)/(?P<journal_id>.*)/$', views.journal_GL_delete_trx,
        name='journal_GL_delete_trx'),
    url(r'^reopen/GL/(?P<batch_id>.*)/$', views.reopen_GL_batch, name='reopen_GL_batch'),
    url(r'^remove/GL/(?P<batch_id>.*)/$', views.gl_batch_remove, name='remove_GL_batch'),
    url(r'^send/GL/(?P<batch_id>.*)/(?P<is_provisional>.*)/$', views.send_GL_batch, name='send_GL_batch'),
    url(r'^journal_GL_get_trx/(?P<batch_id>.*)/(?P<journal_num>.*)/(?P<isNext>.*)/$', views.journal_GL_get_trx,
        name='journal_GL_get_trx'),
    url(r'^journal_GL_add_trx/(?P<batch_id>.*)/(?P<journal_id>.*)/$', views.journal_GL_add_trx,
        name='journal_GL_add_trx'),
    url(r'^gl_revaluation/$', views.gl_revaluation, name='gl_revaluation'),
    url(r'^print/GL/balance_listing/$', views.print_Gl_balance_listing, name='print_Gl_balance_listing'),
    url(r'^print/GL/profit_listing/$', views.print_Gl_profit_listing, name='print_Gl_profit_listing'),
    url(r'^print/GL/trial_balance_listing/$', views.print_Gl_trial_balance_listing,
        name='print_Gl_trial_balance_listing'),
    url(r'^load_customer/$', views.load_customer, name='load_customer'),
    url(r'^load_bank_list/$', views.load_bank_list, name='load_bank_list'),
    url(r'^load_customer_list/$', views.load_customer_list, name='load_customer_list'),
    url(r'^load_account_list/$', views.load_account_list, name='load_account_list'),
    url(r'^load_payment_list/(?P<source_type>.*)/$', views.load_payment_list, name='load_payment_list'),
    url(r'^ReceiptDocumentsList_as_json/$', views.receipt_documents_list_as_json, name='ReceiptDocumentsList_as_json'),
    url(r'^UnpostedBatch__asJson/$', views.UnpostedBatch__asJson, name='UnpostedBatch__asJson'),
    url(r'^create_reverse_batch/$', views.create_reverse_batch, name='create_reverse_batch'),
    url(r'^new_empty_batch/$', views.new_empty_batch, name='new_empty_batch'),
    url(r'^delete_empty_batch/$', views.delete_empty_batch, name='delete_empty_batch'),

    # AR Receipt Entry
    url(r'^add/ARReceipt/(?P<batch_id>.*)/$', views.ar_receipt_add, name='add_ar_receipt'),

    url(r'^edit/ARReceipt/(?P<journal_id>.*)/$', views.ar_receipt_edit, name='edit_ar_receipt'),
    url(r'^delete/ARReceipt/(?P<journal_id>.*)/$', views.ar_receipt_delete, name='ar_receipt_delete'),
    url(r'^delete/Batch/ARReceipt/(?P<batch_id>.*)/$', views.delete_batch_receipt, name='delete_batch_receipt'),
    url(r'^send/ARReceipt/(?P<batch_id>.*)/$', views.send_batch_receipt, name='send_batch_receipt'),
    # ------------------
    url(r'^revaluation/(?P<type_transaction>.*)/$', views.revaluation, name='revaluation'),
    url(r'^revaluation_report/(?P<batch_type>.*)/$', views.revaluation_report, name='revaluation_report'),
    url(r'^revaluation_list_json/(?P<type_transaction>.*)/$', views.RevaluationList__asJson, name='RevaluationList__asJson'),

    url(r'^payment/list/pagination/(?P<source_type>.*)$', views.PaymentCode__asJson, name='PaymentCode__asJson'),

    # Fiscal Calendars
    url(r'^fiscal-calendars/(?P<year>.*)/(?P<module_type>.*)/$', views.fiscal_calendars, name='fiscal_calendars'),
    # Reverse Transaction
    url(r'^reverse_transaction/$', views.reverse_transaction, name='reverse_transaction'),
    url(r'^advance_search_form/$', views.advance_search_form, name='advance_search_form'),
    url(r'^JournalList__inReverseTransaction/$', views.JournalList__inReverseTransaction,
        name='JournalList__inReverseTransaction'),
    url(r'^advanceSearch__inReverseTransaction/$', views.advanceSearch__inReverseTransaction,
        name='advanceSearch__inReverseTransaction'),

    url(r'^account_set_list/(?P<account_set_type>.*)/$', views.AccountSetList__asJson, name='AccountSetList__asJson'),
    url(r'^load_account_set/(?P<account_set_type>.*)/$', views.load_account_set, name='acc_load_account_set'),
    # Closing
    url(r'^monthly_closing/(?P<module_type>.*)/$', views.monthly_closing, name='monthly_closing'),
    url(r'^closing/$', views.closing, name='closing'),
    url(r'^load_fiscal_period/$', views.load_fiscal_period, name='load_fiscal_period'),
    url(r'^inventory_closing/$', views.inventory_closing, name='inventory_closing'),
    url(r'^sp_closing/$', views.sp_closing, name='sp_closing'),

    url(r'^taxBySupplier/(?P<id_supplier>.*)/$', views.TaxBySupplier__asJson, name='TaxBySupplier__asJson'),
    url(r'^taxByDisctibutor/(?P<id_distributor>.*)/$', views.TaxByDisctibutor__asJson, name='TaxByDisctibutor__asJson'),
    url(r'^post_batches/(?P<module_type>.*)/$', views.post_batches, name='post_batches'),
    url(r'^post_batch/(?P<batch_id>.*)/$', views.post_batch, name='post_batch'),
    url(r'^print/tax_tracking/$', views.print_tax_tracking_rpt, name='print_tax_tracking_rpt'),
    url(r'^get_batches/(?P<module_type>.*)/$', views.get_batches, name='get_batches'),
    url(r'^batchDetail__asJson/(?P<batch_id>.*)/$', views.batchDetail__asJson, name='batchDetail__asJson'),
    url(r'^journalDetail__asJson/(?P<journal_id>.*)/$', views.journalDetail__asJson, name='journalDetail__asJson'),
    url(r'^check_batch/$', views.check_batch, name='check_batch'),
    url(r'^uncheck_batch/$', views.uncheck_batch, name='uncheck_batch'),
    url(r'^check_journal/$', views.check_journal, name='check_journal'),
    url(r'^uncheck_journal/$', views.uncheck_journal, name='uncheck_journal'),
    url(r'^flag_check_journal/$', views.flag_check_journal, name='flag_check_journal'),
    url(r'^flag_uncheck_journal/$', views.flag_uncheck_journal, name='flag_uncheck_journal'),
    url(r'^check_fiscal_calendar/(?P<post_date>.*)/$', views.check_fiscal_calendar, name='check_fiscal_calendar'),
    url(r'^add/AP-RE/(?P<batch_id>.*)/$', views.add_ap_recurring_entry, name='add_ap_recurring_entry'),
    url(r'^edit/AP-RE/(?P<id>.*)/$', views.edit_ap_recurring_entry, name='edit_ap_recurring_entry'),
    url(r'^add/AR-RE/(?P<batch_id>.*)/$', views.add_ar_recurring_entry, name='add_ar_recurring_entry'),
    url(r'^edit/AR-RE/(?P<id>.*)/$', views.edit_ar_recurring_entry, name='edit_ar_recurring_entry'),
    url(r'^add/APPayment-RE/(?P<batch_id>.*)/$', views.add_appayment_recurring_entry, name='add_appayment_recurring_entry'),
    url(r'^edit/APPayment-RE/(?P<id>.*)/$', views.edit_appayment_recurring_entry, name='edit_appayment_recurring_entry'),
    url(r'^add/ARReceipt-RE/(?P<batch_id>.*)/$', views.add_arreceipt_recurring_entry, name='add_arreceipt_recurring_entry'),
    url(r'^edit/ARReceipt-RE/(?P<id>.*)/$', views.edit_arreceipt_recurring_entry, name='edit_arreceipt_recurring_entry'),
    url(r'^add/RE/(?P<batch_id>.*)/$', views.add_recurring_entry, name='add_recurring_entry'),
    url(r'^edit/RE/(?P<id>.*)/$', views.edit_recurring_entry, name='edit_recurring_entry'),
    url(r'^list-RE/(?P<journal_type>.*)/(?P<batch_id>.*)/$', views.list_recurring_entries, name='list_recurring_entries'),
    url(r'^add/SE/$', views.add_schedule_entry, name='add_schedule_entry'),
    url(r'^edit/SE/(?P<id>.*)/$', views.edit_schedule_entry, name='edit_schedule_entry'),
    url(r'^list/SE/$', views.list_schedule_entries, name='list_schedule_entries'),
    url(r'^get-re-detail-transaction/$', views.get_re_detail_transaction, name='get_re_detail_transaction'),
    url(r'^delete-re-transaction/(?P<id>.*)/$', views.delete_re_transaction, name='delete_re_transaction'),
    url(r'^delete-schedule-entry/$', views.delete_schedule_entry, name='delete_schedule_entry'),
    url(r'^delete/batch_recurring/(?P<batch_id>.*)/$', views.batch_recurring_delete, name='batch_recurring_delete'),
    url(r'^rec_batch_list/(?P<batch_type>.*)/$', views.recurring_batch_list, name='recurring_batch_list'),
    url(r'^rec_batch_list_json/(?P<batch_type>.*)/$', views.RecBatchList__asJson, name='RecBatchList__asJson'),
    url(r'^rec_entries_as_Json/(?P<journal_type>.*)/(?P<batch_id>.*)/$', views.rec_entries_as_Json, name='rec_entries_as_Json'),
    url(r'^rec_batchDetail__asJson/(?P<batch_id>.*)/$', views.RecbatchDetail__asJson, name='RecbatchDetail__asJson'),
    url(r'^rec_entry_detail__asJson/(?P<id>.*)/$', views.rec_entry_detail__asJson, name='rec_entry_detail__asJson'),

    url(r'^invoice-transactions-list-as-json/$', views.invoice_transactions_list_as_json, name='invoice_transactions_list_as_json'),
    url(r'^load_applied_doc_history/$', views.load_applied_doc_history, name='load_applied_doc_history'),

    url(r'^save_templates/(?P<type>.*)/$', views.save_templates, name='save_templates'),
    url(r'^get_fiscal_data/$', views.get_fiscal_data, name='get_fiscal_data'),
    url(r'^get_cls_fiscal_data/$', views.get_cls_fiscal_data, name='get_cls_fiscal_data'),

    # GL Integration
    url(r'^ar_settings/$', views.ar_gl_integration, name='ar_gl_integration'),
    url(r'^ap_settings/$', views.ap_gl_integration, name='ap_gl_integration'),
    url(r'^ar_options/$', views.ar_options, name='ar_options'),
    url(r'^ap_options/$', views.ap_options, name='ap_options'),
    url(r'^gl_integration_list/(?P<type>.*)/$', views.GLIntegrtionList__asJson, name='GLIntegrtionList__asJson'),
    url(r'^gl_integration/edit/(?P<id>.*)/(?P<type>.*)/$', views.gl_integration_edit, name='gl_integration_edit'),
    url(r'^fix_ar_adjustments/$', views.fix_ar_adjustments, name='fix_ar_adjustments'),
    url(r'^fix_payments_outs_amount/(?P<type>.*)/(?P<journal_ids>.*)/$', views.fix_payments_outs_amount, name='fix_payments_outs_amount'),
    url(r'^fix_real_outs_amount/(?P<type>.*)/$', views.fix_real_outs_amount, name='fix_real_outs_amount'),
    url(r'^fix_journal_year_period/$', views.fix_journal_year_period, name='fix_journal_year_period'),
    url(r'^check_if_duplicate/(?P<type>.*)/(?P<field>.*)/$', views.check_if_duplicate, name='check_if_duplicate'),
    url(r'^get_batch_entries/(?P<batch_type>.*)/(?P<batch_no>.*)/$', views.get_batch_entries, name='get_batch_entries'),
]

from django.conf.urls import url
from reports import views

urlpatterns = [
    url(r'^$', views.view_report, name='view_report'),
    url(r'^print_blank/$', views.print_blank, name='print_blank'),
    url(r'^print_no_data_found/$', views.print_no_data_found, name='print_no_data_found'),
    url(r'^view_report/(?P<order_type>.*)/(?P<order_id>.*)/(?P<print_type>.*)/(?P<category_id>.*)/$', views.view_report,
        name='view_report'),
    url(r'^view_report/(?P<order_type>.*)/(?P<order_id>.*)/(?P<print_type>.*)/$', views.view_report,
        name='view_report'),

    # S&P Order related
    url(r'^print_order/(?P<order_id>.*)/$', views.print_order, name='report_print_order'),
    url(r'^print_po_order/(?P<order_id>.*)/(?P<print_header>.*)/(?P<remove_address>.*)/(?P<address>.*)/(?P<signature>.*)/(?P<part_group>.*)$', views.print_po_order, name='report_print_po_order'),
    url(r'^print_po_orders/(?P<from_order_id>.*)/(?P<to_order_id>.*)/(?P<print_header>.*)/(?P<remove_address>.*)/(?P<address>.*)/(?P<signature>.*)/(?P<part_group>.*)$',
        views.print_po_orders, name='report_print_po_orders'),
    url(r'^print_do/(?P<order_id>.*)/(?P<print_header>.*)/(?P<part_group>.*)$', views.print_do_order, name='print_do'),
    url(r'^print_packing_list/(?P<order_id>.*)/(?P<print_header>.*)/(?P<part_group>.*)$', views.print_packing_list,
        name='report_print_packing_list'),
    url(r'^print_po_order_pdf/(?P<order_id>.*)/(?P<print_header>.*)/$', views.print_po_order_pdf,
        name='report_print_po_order_pdf'),
    url(r'^print_tax_invoice/(?P<order_id>.*)/(?P<print_header>.*)/(?P<part_group>.*)$', views.print_tax_invoice,
        name='report_print_tax_invoice'),
    url(r'^print_invoice/(?P<order_id>.*)/(?P<print_header>.*)/(?P<part_group>.*)$', views.print_invoice,
        name='report_print_invoice'),
    url(r'^print_shipping_invoice/(?P<order_id>.*)/(?P<print_header>.*)/(?P<part_group>.*)/(?P<address>.*)$', views.print_shipping_invoice,
        name='print_shipping_invoice'),
    url(r'^print_shipping_invoice_2/(?P<order_id>.*)/(?P<print_header>.*)/(?P<part_group>.*)/(?P<address>.*)$', views.print_shipping_invoice_2,
        name='print_shipping_invoice_2'),

    # AJAX calls
    url(r'^get_current_month_amount/(?P<order_type>.*)/(?P<month>.*)/(?P<year>.*)/$', views.get_current_month_amount,
        name='get_current_month_amount'),
    url(r'^get_current_month_profit/(?P<month>.*)/(?P<year>.*)/$', views.get_current_month_profit,
        name='get_current_month_profit'),
    url(r'^get_current_month_profit_percent/(?P<month>.*)/(?P<year>.*)/$', views.get_current_month_profit_percent,
        name='get_current_month_profit_percent'),
    url(r'^get_reports_by_category/(?P<cat_id>.*)/$', views.get_reports_by_category, name='get_reports_by_category'),
    url(r'^get_sales_analysis_data/(?P<date_from>.*)/(?P<date_to>.*)/$', views.get_sales_analysis_data, name='get_sales_analysis_data'),
    url(r'^get_supplier_list/(?P<date_from>.*)/(?P<date_to>.*)/(?P<data_type>.*)/$', views.get_supplier_list, name='get_supplier_list'),
    url(r'^get_customer_po/(?P<date_from>.*)/(?P<date_to>.*)/(?P<supplier_id>.*)/(?P<order_code>.*)/$', views.get_customer_po, name='get_customer_po'),
    url(r'^get_customer_list/(?P<date_from>.*)/(?P<date_to>.*)/(?P<data_type>.*)/$', views.get_customer_list, name='get_customer_list'),
    url(r'^get_document_no/(?P<date_from>.*)/(?P<date_to>.*)/(?P<order_code>.*)/$', views.get_document_no, name='get_document_no'),
    url(r'^get_SL3_data/(?P<date_from>.*)/(?P<date_to>.*)/(?P<order_code>.*)/$', views.get_SL3_data, name='get_SL3_data'),
    url(r'^get_document_numbers/(?P<date_from>.*)/(?P<date_to>.*)/(?P<order_code>.*)/(?P<customer_id>.*)/$', views.get_document_numbers, name='get_document_numbers'),
    url(r'^get_monthly_purchase/(?P<year_month>.*)/(?P<parameter_id>.*)/(?P<data_type>.*)/$', views.get_monthly_purchase, name='get_monthly_purchase'),
    url(r'^get_gr_data/(?P<date_from>.*)/(?P<date_to>.*)/(?P<data_type>.*)/$', views.get_gr_data, name='get_gr_data'),
    url(r'^get_report_filters/(?P<date_from>.*)/(?P<date_to>.*)/(?P<order_code>.*)/(?P<date_type>.*)/$', views.get_report_filters, name='get_report_filters'),
    url(r'^get_delivery_addr/$', views.get_delivery_addr, name='get_delivery_addr'),
    url(r'^get_po_data/(?P<date_from>.*)/(?P<date_to>.*)/(?P<data_type>.*)/$', views.get_po_data, name='get_po_data'),
    url(r'^get_inv_location/$', views.get_inv_location, name='get_inv_location'),
    url(r'^get_SR8500_data/(?P<location_id>.*)$', views.get_SR8500_data, name='get_SR8500_data'),
    url(r'^get_so_data/(?P<date_from>.*)/(?P<date_to>.*)/(?P<data_type>.*)/$', views.get_so_data, name='get_so_data'),
    url(r'^get_sales_info/(?P<year_month>.*)/(?P<data_type>.*)/$', views.get_sales_info, name='get_sales_info'),
    url(r'^get_part_group/(?P<date_from>.*)/(?P<date_to>.*)/(?P<order_code>.*)/$', views.get_part_group, name='get_part_group'),
    url(r'^get_oustanding_sales/(?P<date_from>.*)/(?P<date_to>.*)/(?P<doc_from>.*)/(?P<doc_to>.*)/(?P<cus_po_from>.*)/(?P<cus_po_to>.*)/(?P<data_type>.*)/$', views.get_oustanding_sales,
        name='get_oustanding_sales'),

    # S&P SL3xxx
    url(r'^print_SL3300/$', views.print_SL3300, name='print_SL3300'),
    url(r'^print_SL3301/$', views.print_SL3301, name='print_SL3301'),
    url(r'^print_SL3A00/$', views.print_SL3A00, name='print_SL3A00'),
    url(r'^print_SL3A01/$', views.print_SL3A01, name='print_SL3A01'),
    
    # S&P SR83xx
    url(r'^print_SR8300/$', views.print_SR8300, name='print_SR8300'),
    url(r'^print_SR8301/$', views.print_SR8301, name='print_SR8301'),
    url(r'^print_SR8400/$', views.print_SR8400, name='print_SR8400'),
   
   # S&P SR88xx
    url(r'^print_SR8800/$', views.print_SR8800, name='print_SR8800'),
    url(r'^print_SR8801/$', views.print_SR8801, name='print_SR8801'),

    # S&P SR71xx
    url(r'^print_SR7101/$', views.print_SR7101, name='print_SR7101'),
    url(r'^print_xls_SR7101/$', views.print_SR7101_excel, name='print_SR7101_excel'),
    url(r'^print_SR7102/$', views.print_SR7102, name='print_SR7102'),
    url(r'^print_xls_SR7102/$', views.print_SR7102_excel, name='print_SR7102_excel'),
    url(r'^print_SR7103/$', views.print_SR7103, name='print_SR7103'),
    url(r'^print_xls_SR7103/$', views.print_SR7103_excel, name='print_SR7103_excel'),

    # S&P SR72xx
    url(r'^print_xls_SR7201/$', views.print_xls_SR7201, name='print_xls_SR7201'),
    url(r'^print_SR7201/$', views.print_SR7201, name='print_SR7201'),
    url(r'^print_SR7202/$', views.print_SR7202, name='print_SR7202'),
    url(r'^print_xls_SR7202/$', views.print_xls_SR7202, name='print_xls_SR7202'),
    url(r'^print_SR7204/$', views.print_SR7204, name='print_SR7204'),
    url(r'^print_xls_SR7204/$', views.print_xls_SR7204, name='print_xls_SR7204'),
    url(r'^print_SR7203/$', views.print_SR7203, name='print_SR7203'),
    url(r'^print_xls_SR7203/$', views.print_xls_SR7203, name='print_xls_SR7203'),
    url(r'^print_SR7205/$', views.print_SR7205, name='print_SR7205'),
    url(r'^print_xls_SR7205/$', views.print_xls_SR7205, name='print_xls_SR7205'),
    url(r'^print_SR7206/(?P<date_from>.*)/(?P<date_to>.*)/(?P<supplier_no>.*)/$', views.print_SR7206,
        name='print_SR7206'),

    # S&P SR73xx
    url(r'^print_SR7300/$', views.print_SR7300, name='print_SR7300'),
    url(r'^print_SR7301/$', views.print_SR7301, name='print_SR7301'),
    url(r'^print_SR7302/$', views.print_SR7302, name='print_SR7302'),
    url(r'^print_SR7303/$', views.print_SR7303, name='print_SR7303'),
    url(r'^print_xls_SR7303/$', views.print_xls_SR7303, name='print_xls_SR7303'),

    # S&P SR74xx
    url(r'^print_SR7401/$', views.print_SR7401, name='print_SR7401'),
    url(r'^print_SR7402/$', views.print_SR7402, name='print_SR7402'),
    url(r'^print_xls_SR7402/$', views.print_xls_SR7402, name='print_xls_SR7402'),
    url(r'^print_SR7403/$', views.print_SR7403, name='print_SR7403'),
    url(r'^print_xls_SR7403/$', views.print_xls_SR7403, name='print_xls_SR7403'),
    url(r'^print_SR7404/$', views.print_SR7404, name='print_SR7404'),
    url(r'^print_xls_SR7404/$', views.print_xls_SR7404, name='print_xls_SR7404'),
    url(r'^print_SR7405/(?P<date_from>.*)/(?P<date_to>.*)/(?P<customer_code>.*)/$', views.print_SR7405,
        name='print_SR7405'),

    # S&P SR75xx
    url(r'^print_SR7501/$', views.print_SR7501, name='print_SR7501'),
    url(r'^print_xls_SR7501/$', views.print_xls_SR7501, name='print_xls_SR7501'),
    url(r'^print_SR7502/$', views.print_SR7502, name='print_SR7502'),
    url(r'^print_xls_SR7502/$', views.print_xls_SR7502, name='print_xls_SR7502'),
    url(r'^print_SR7503/$', views.print_SR7503, name='print_SR7503'),
    url(r'^print_xls_SR7503/$', views.print_xls_SR7503, name='print_xls_SR7503'),
    url(r'^print_SR7504/$', views.print_SR7504, name='print_SR7504'),
    url(r'^print_xls_SR7504/$', views.print_xls_SR7504, name='print_xls_SR7504'),

    # S&P SR76xx
    # url(r'^print_SR7601/$', views.print_SR7601, name='print_SR7601'),
    # url(r'^print_SR7602/$', views.print_SR7602, name='print_SR7602'),
    url(r'^print_SR7601/$', views.print_SR7601, name='print_SR7601'),
    url(r'^print_SR7602/$', views.print_SR7602, name='print_SR7602'),
    url(r'^print_SR7603/$', views.print_SR7603, name='print_SR7603'),
    url(r'^print_xls_SR7603/$', views.print_xls_SR7603, name='print_xls_SR7603'),

    # S&P SR85xx
    url(r'^print_SR8500/$', views.print_SR8500, name='print_SR8500'),
    url(r'^print_xls_SR8500/$', views.print_xls_SR8500, name='print_xls_SR8500'),

    # S&P SR86xx
    url(r'^print_SR8600/(?P<from_month>.*)/(?P<to_month>.*)$', views.print_SR8600, name='print_SR8600'),
    url(r'^print_xls_SR8600/(?P<from_month>.*)/(?P<to_month>.*)$', views.print_xls_SR8600, name='print_xls_SR8600'),
    url(r'^print_SR8601/(?P<from_month>.*)/(?P<to_month>.*)/$', views.print_SR8601, name='print_SR8601'),
    url(r'^print_xls_SR8601/(?P<from_month>.*)/(?P<to_month>.*)/$', views.print_xls_SR8601, name='print_xls_SR8601'),
    url(r'^print_SR8602/(?P<from_month>.*)/(?P<to_month>.*)/$', views.print_SR8602, name='print_SR8602'),
    url(r'^print_xls_SR8602/(?P<from_month>.*)/(?P<to_month>.*)/$', views.print_xls_SR8602, name='print_xls_SR8602'),
    url(r'^print_SR8603/(?P<from_month>.*)/(?P<to_month>.*)/$', views.print_SR8603, name='print_SR8603'),
    url(r'^print_xls_SR8603/(?P<from_month>.*)/(?P<to_month>.*)/$', views.print_xls_SR8603, name='print_xls_SR8603'),
    url(r'^print_SR8602/$', views.print_SR8602, name='print_SR8602'),
    url(r'^print_SR8603/$', views.print_SR8603, name='print_SR8603'),

    # S&P SR87xx
    url(r'^print_SR8700/(?P<select_month>.*)/$', views.print_SR8700, name='print_SR8700'),
    url(r'^print_SR8700_1/(?P<select_month>.*)/$', views.print_SR8700_1, name='print_SR8700'),
    url(r'^print_SR8701/(?P<select_month>.*)/$', views.print_SR8701, name='print_SR8701'),
    url(r'^print_SR8700/$', views.print_SR8700, name='print_SR8700'),
    url(r'^print_SR8700_1/(?P<select_month>.*)/$', views.print_SR8700_1, name='print_SR8700'),
    url(r'^print_SR8701/$', views.print_SR8701, name='print_SR8701'),

    # S&P Listings
    url(r'^print_GL2200/(?P<selected_month>.*)/$', views.print_GL2200, name='print_GL2200'),
    url(r'^print_CL2400/$', views.print_CL2400, name='print_CL2400'),
    url(r'^print_DL2400/$', views.print_DL2400, name='print_DL2400'),
    url(r'^print_SL2100/$', views.print_SL2100, name='print_SL2100'),
    url(r'^print_xls_SL2100/$', views.print_xls_SL2100, name='print_xls_SL2100'),
    url(r'^print_SL2200/$', views.print_SL2200, name='print_SL2200'),
    url(r'^print_xls_SL2200/$', views.print_xls_SL2200, name='print_xls_SL2200'),
    url(r'^print_SL2201/$', views.print_SL2201, name='print_SL2201'),
    url(r'^print_xls_SL2201/$', views.print_xls_SL2201, name='print_xls_SL2201'),
    url(r'^print_TL1200/$', views.print_TL1200, name='print_TL1200'),
    url(r'^print_CL2100/(?P<code>.*)/$', views.print_CL2100, name='print_CL2100'),

    # AR Notes
    url(r'^print_AR_note/(?P<journal_id>.*)/(?P<print_header>.*)/$', views.print_AR_note, name='print_AR_note'),

    # AR Customers
    url(
        r'^print_AR_customers/(?P<report_type>.*)/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/$',
        views.print_ARCustomers,
        name='print_ARCustomers'),
    url(
        r'^print_AR_customers_letter/(?P<report_type>.*)/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/$',
        views.print_ARCustomers_letter,
        name='print_ARCustomers_letter'),
    url(
        r'^print_AR_customers_Label/(?P<report_type>.*)/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/$',
        views.print_ARCustomers_Label,
        name='print_ARCustomers_Label'),

    # ARx
    url(
        r'^print_AR1/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_ARAgedTrialSummary,
        name='print_ARAgedTrialSummary'),
    url(
        r'^print_AR2/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_ARAgedTrialDetail,
        name='print_ARAgedTrialDetail'),
    url(
        r'^print_AR_XLS1/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_ARAgedTrialSummary_XLS,
        name='print_ARAgedTrialSummary_XLS'),
    url(
        r'^print_AR_XLS2/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_ARAgedTrialDetail_XLS,
        name='print_ARAgedTrialDetail_XLS'),

    # AP Vendors
    url(
        r'^print_AP_vendor_letter/(?P<report_type>.*)/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/$',
        views.print_APvendor_letter,
        name='print_APvendor_letter'),
    url(
        r'^print_AP_vendor_Label/(?P<report_type>.*)/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/$',
        views.print_APvendor_Label,
        name='print_APvendor_Label'),

    # APx
    url(
        r'^print_AP1/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_APAgedTrialSummary,
        name='print_APAgedTrialSummary'),
    url(
        r'^print_AP2/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_APAgedTrialDetail,
        name='print_APAgedTrialDetail'),
    url(
        r'^print_AP_XLS1/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_APAgedTrialSummary_XLS,
        name='print_APAgedTrialSummary_XLS'),
    url(
        r'^print_AP_XLS2/(?P<age_from>.*)/(?P<cutoff_date>.*)/(?P<cus_no>.*)/(?P<date_type>.*)/(?P<doc_type>.*)/(?P<curr_list>.*)/(?P<paid_full>.*)/(?P<periods>.*)/(?P<appl_detail>.*)/$',
        views.print_APAgedTrialDetail_XLS,
        name='print_APAgedTrialDetail_XLS'),

    # GLx
    url(
        r'^print_GL1/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLFunctionBalance,
        name='print_GLFunctionBalance'),
    url(
        r'^print_GL1a/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLFunction,
        name='print_GLFunction'),
    url(
        r'^print_GL2/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLSourceBalance,
        name='print_GLSourceBalance'),
    url(
        r'^print_GL2a/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLSource,
        name='print_GLSource'),
    url(
        r'^print_GL1_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLFunctionBalance_XLS,
        name='print_GLFunctionBalance_XLS'),
    url(
        r'^print_GL1a_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLFunction_XLS,
        name='print_GLFunction_XLS'),
    url(
        r'^print_GL2_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLSourceBalance_XLS,
        name='print_GLSourceBalance_XLS'),
    url(
        r'^print_GL2a_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLSource_XLS,
        name='print_GLSourceXLS'),

    # Stock Related STx
    url(
        r'^print_ST1/(?P<issue_from>.*)/(?P<location>.*)/$', views.print_ST_report_IL2601,
        name='print_ST_report_IL2601'),
    url(
        r'^print_ST2/(?P<issue_from>.*)/(?P<issue_to>.*)/$', views.print_STOutBalance,
        name='print_STOutBalance'),
    url(
        r'^print_ST3/(?P<sort_order>.*)/(?P<print_selection>.*)/$', views.print_ST_stock_value,
        name='print_ST_stock_value'),
    url(
        r'^print_ST4/(?P<issue_from>.*)/(?P<trx_code>.*)/$', views.print_ST_years_trx,
        name='print_ST_years_trx'),
    url(
        r'^print_ST5/(?P<issue_from>.*)/$', views.print_ST_report_IR4600,
        name='print_ST_report_IR4600'),
    url(
        r'^print_ST6/(?P<issue_from>.*)/$', views.print_ST_report_IR4300,
        name='print_ST_report_IR4300'),
    url(
        r'^print_ST7/(?P<issue_from>.*)/$', views.print_ST_report_IR4200,
        name='print_ST_report_IR4200'),

    # Balance Sheet and Profit & Loss
    url(
        r'^print_GLBalance/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print_GLBalanceSheet,
        name='print_GLBalanceSheet'),
    url(
        r'^print_GLBalance_new/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print_GLBalanceSheet_new,
        name='print_GLBalanceSheet_new'),
    url(
        r'^print_GLBalanceXLS/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print_GLBalanceSheetXLS,
        name='print_GLBalanceSheetXLS'),
    url(
        r'^print_GLBalanceXLS_new/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print_GLBalanceSheetXLS_new,
        name='print_GLBalanceSheetXLS_new'),
    url(
        r'^print_GLProfit/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print__GLProfitLoss,
        name='print__GLProfitLoss'),
    url(
        r'^print_GLProfit_new/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print__GLProfitLoss_new,
        name='print__GLProfitLoss_new'),
    url(
        r'^print_GLProfit_excel/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print__GLProfitLoss_excel,
        name='print__GLProfitLoss_excel'),
    url(
        r'^print_GLProfit_excel_new/(?P<issue_from>.*)/(?P<report_type>.*)/(?P<filter_type>.*)/(?P<from_val>.*)/(?P<to_val>.*)/$', views.print__GLProfitLoss_excel_new,
        name='print__GLProfitLoss_excel_new'),

    # Trial Balance
    url(
        r'^print_GLTrial1/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<acc_list>.*)/(?P<is_activity>.*)/$', views.print__GLTrialBalanceSheet,
        name='print__GLTrialBalanceSheet'),
    url(
        r'^print_GLTrial2/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<acc_list>.*)/(?P<is_activity>.*)/$',
        views.print__GLTrialNetSheet,
        name='print__GLTrialNetSheet'),
    url(
        r'^print_GLTrial_excel/(?P<gl_type>.*)/(?P<issue_from>.*)/(?P<issue_end>.*)/(?P<acc_list>.*)/(?P<is_activity>.*)/$', views.print__GLTrial_excel,
        name='print__GLTrial_excel'),

    # Batch Related
    url(
        r'^print_GL2Batch/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLSourceBalanceBatch,
        name='print_GLSourceBalanceBatch'),
    url(
        r'^print_GL2aBatch/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLSourceBatch,
        name='print_GLSourceBatch'),
    url(
        r'^print_GL1Batch/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLFunctionBalanceBatch,
        name='print_GLFunctionBalanceBatch'),
    url(
        r'^print_GL1aBatch/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<line_1>.*)/(?P<line_2>.*)/(?P<line_3>.*)/(?P<acc_list>.*)/$', views.print_GLFunctionBatch,
        name='print_GLFunctionBatch'),
    url(
        r'^print_GL2Batch_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLSourceBalanceBatch_XLS,
        name='print_GLSourceBalanceBatch_XLS'),
    url(
        r'^print_GL2aBatch_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLSourceBatch_XLS,
        name='print_GLSourceBatch_XLS'),
    url(
        r'^print_GL1Batch_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLFunctionBalanceBatch_XLS,
        name='print_GLFunctionBalanceBatch_XLS'),
    url(
        r'^print_GL1aBatch_XLS/(?P<issue_from>.*)/(?P<issue_to>.*)/(?P<status_type>.*)/(?P<acc_list>.*)/$', views.print_GLFunctionBatch_XLS,
        name='print_GLFunctionBatch_XLS'),

    url(
        r'^print_BatchNumber/(?P<batch_type>.*)/(?P<batch_from>.*)/(?P<batch_to>.*)/(?P<currency>.*)/(?P<entry_from>.*)/(?P<entry_to>.*)/$', views.print_BatchNumber,
        name='print_BatchNumber'),


    # Tax related
    url(r'^print_tax_tracking/(?P<tax_authority>.*)/(?P<from_period_year>.*)/(?P<to_period_year>.*)/(?P<print_type>.*)/(?P<report_by>.*)/(?P<print_by>.*)/(?P<transaction_type>.*)/(?P<is_history>.*)/$',
        views.print_tax_tracking, name='print_tax_tracking'),
    url(r'^print_tracking_items/(?P<tax_authority>.*)/(?P<from_period_year>.*)/(?P<to_period_year>.*)/(?P<print_type>.*)/(?P<report_by>.*)/(?P<print_by>.*)/(?P<transaction_type>.*)/(?P<is_history>.*)/$',
        views.print_tax_item, name='print_tax_item'),
    url(r'^print_tracking_auth/(?P<tax_authority>.*)/(?P<from_period_year>.*)/(?P<to_period_year>.*)/(?P<print_type>.*)/(?P<report_by>.*)/(?P<print_by>.*)/(?P<transaction_type>.*)/(?P<is_history>.*)/$',
        views.print_tax_auth, name='print_tax_auth'),
    
    url(r'^print_tax_auth_XLS/(?P<tax_authority>.*)/(?P<from_period_year>.*)/(?P<to_period_year>.*)/(?P<print_type>.*)/(?P<report_by>.*)/(?P<print_by>.*)/(?P<transaction_type>.*)/(?P<is_history>.*)/$',
        views.print_tax_auth_XLS, name='print_tax_auth_XLS'),
    url(r'^print_item_tax_XLS/(?P<tax_authority>.*)/(?P<from_period_year>.*)/(?P<to_period_year>.*)/(?P<print_type>.*)/(?P<report_by>.*)/(?P<print_by>.*)/(?P<transaction_type>.*)/(?P<is_history>.*)/$',
        views.print_item_tax_XLS, name='print_item_tax_XLS'),

    # Revaluation
    url(r'^print_ar_revaluation/(?P<from_posting>.*)/(?P<to_posting>.*)/$', views.print_AR_revaluation, name='print_AR_revaluation'),
    url(r'^print_ap_revaluation/(?P<from_posting>.*)/(?P<to_posting>.*)/$', views.print_AP_revaluation, name='print_AP_revaluation'),
    url(r'^print_gl_revaluation/(?P<from_posting>.*)/(?P<to_posting>.*)/$', views.print_GL_revaluation, name='print_GL_revaluation'),
]

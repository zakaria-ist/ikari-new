ATTRS_AREA = {'class': "form-control", 'style': 'width:100%; max-width:400px;', 'rows': '4'}
ATTRS_AREA_L = {'class': "form-control", 'style': 'width:100%; max-width:800px;', 'rows': '4'}
ATTRS_TXT_S = {'class': "form-control", 'style': 'width:100%; max-width:200px;'}
ATTRS_TXT_XS = {'class': "form-control", 'style': 'width:100%; max-width:100px;'}
ATTRS_TXT_XXS = {'class': "form-control", 'style': 'width:100%; max-width:80px;'}
ATTRS_TXT = {'class': "form-control", 'style': 'width:100%; max-width:400px;'}
ATTRS_TXT_L = {'class': "form-control", 'style': 'width:100%; max-width:600px;'}

GROUP_CATEGORY = (
    ('01', 'Cash and Cash Equivalents'),
    ('02', 'Account Receivable'),
    ('03', 'Inventory'),
    ('04', 'Other Current Assets'),
    ('05', 'Fixed Assets'),
    ('06', 'Accumulated Depreciation'),
    ('07', 'Other Assets'),
    ('08', 'Account Payable'),
    ('09', 'Other Current Liabilities'),
    ('10', 'Long Term Liabilities'),
    ('11', 'Other Liabilities'),
    ('12', 'Share Capital'),
    ('13', 'Shareholders Equity'),
    ('14', 'Revenue'),
    ('15', 'Cost of Sales'),
    ('16', 'Other Revenue'),
    ('17', 'Other Expenses'),
    ('18', 'Depreciation Expense'),
    ('19', 'Gains / Losses'),
    ('20', 'Interest Expense'),
    ('21', 'Income Taxes'),
)

CATEGORY = (
    ('1', 'Income'),
    ('2', 'Expense'),
    ('3', 'Asset'),
    ('4', 'Liability'),
    ('5', 'Equity'),
)

REPORT_CATEGORY = (
    ('1', 'Accounting Group'),
    ('2', 'Balance Sheet Group'),
    ('3', 'Profit and Loss Group'),
)

ACCOUNT_TYPE = (
    ('2', 'Balance Sheet'),
    ('3', 'Retained Earning'),
    ('1', 'Income Statement'),
)

ACCOUNT_TYPE_DICT = dict([account[::-1] for account in ACCOUNT_TYPE])

BALANCE_TYPE = (
    ('1', 'Debit'),
    ('2', 'Credit'),
)

BALANCE_TYPE_DICT = dict([type[::-1] for type in BALANCE_TYPE])

PAYMENT_TYPE = (
    ('1', 'Cash'),
    ('2', 'Check'),
    ('3', 'Credit'),
    ('4', 'Other'),
)

AP_REPORT_LIST = (
    ('2', 'By Due Date - Detail'),
    ('1', 'By Due Date - Summary'),
)

AR_REPORT_LIST = (
    ('2', 'By Due Date - Detail'),
    ('1', 'By Due Date - Summary'),
)

AP_CUST_REPORT = (
    ('1', 'Letter'),
    ('2', 'Label'),
)
AR_CUST_REPORT = (
    ('1', 'Statement'),
    ('2', 'Letter'),
    ('3', 'Label'),
)

DATE_TYPE = (
    ('1', 'Document Date'),
    ('2', 'Posting Date'),
)

CUR_TYPE = (
    ('1', 'Customers Currency'),
    ('2', 'Functional Currency'),
)

VEN_CUR_TYPE = (
    ('1', 'Suppliers Currency'),
    ('2', 'Functional Currency'),
)

STATUS_TYPE = (
    ('1', 'Open'),
    ('2', 'Posted'),
    ('3', 'Deleted'),
    ('4', 'Reversed'),
    ('5', 'ERROR'),
    ('6', 'Auto Reverse Entry'),
    ('7', 'Prov. Posted'),
    ('8', 'Draft'),
    ('9', 'Removed'),
    ('0', 'Undefined'),

)

STATUS_TYPE_DICT = dict([status[::-1] for status in STATUS_TYPE])

RECURRING_USER_MODE = (
    (0, 'No User'),
    (1, 'Admin'),
    (2, 'Root')
)

RECUR_EXCHANGE_RATE_TYPE = (
    (0, 'Current Rate'),
    (1, 'Recurring Entry Rate'),
)

RECURRING_ENTRY_MODE = (
    (0, 'Normal'),
    (1, 'Quick')
)

WEEKDAYS = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
)

WEEKDAYS_DICT = dict([period[::-1] for period in WEEKDAYS])

MONTHS_STR = (
    ('JAN', '01'),
    ('FEB', '02'),
    ('MAR', '03'),
    ('APR', '04'),
    ('MAY', '05'),
    ('JUN', '06'),
    ('JUL', '07'),
    ('AUG', '08'),
    ('SEP', '09'),
    ('OCT', '10'),
    ('NOV', '11'),
    ('DEC', '12'),
)

MONTHS_STR_DICT = dict([month[::-1] for month in MONTHS_STR])

MONTH_NAMES = (
    (0, 'January'),
    (1, 'February'),
    (2, 'March'),
    (3, 'April'),
    (4, 'May'),
    (5, 'June'),
    (6, 'July'),
    (7, 'August'),
    (8, 'September'),
    (9, 'October'),
    (10, 'November'),
    (11, 'December'),
)
WEEK_NUMBER = (
    (0, 'First'),
    (1, 'Second'),
    (2, 'Third'),
    (3, 'Fourth'),
    (4, 'Fifth'),
)

MOTNHDATES = (
    (0, '1st'),
    (1, '2nd'),
    (2, '3rd'),
    (3, '4th'),
    (4, '5th'),
    (5, '6th'),
    (6, '7th'),
    (7, '8th'),
    (8, '9th'),
    (9, '10th'),
    (10, '11th'),
    (11, '12th'),
    (12, '13th'),
    (13, '14th'),
    (14, '15th'),
    (15, '16th'),
    (16, '17th'),
    (17, '18th'),
    (18, '19th'),
    (19, '20th'),
    (20, '21st'),
    (21, '22nd'),
    (22, '23rd'),
    (23, '24th'),
    (24, '25th'),
    (25, '26th'),
    (26, '27th'),
    (27, '28th'),
    (28, '29th'),
    (29, '30th'),
    (30, '31st'),
)

MOTNHDATES_DICT = dict([period[::-1] for period in MOTNHDATES])

FREQUENCY_DAILY = (
    (0, 'Every'),
    (0, 'These Work Days'),
)

FLAG_TYPE = (
    (0, 'UNMARKED'),
    (1, 'CHECKED'),
    (2, 'MODIFIED')
)

FLAG_TYPE_DICT = dict([flag[::-1] for flag in FLAG_TYPE])

DOCUMENT_TYPES_IN_REPORT = (
    ('1', 'IN'),
    ('2', 'DB'),
    ('3', 'CR'),
    ('4', 'IT'),
    ('5', 'UC'),
    ('6', 'PI'),
    ('7', 'PY'),
    ('8', 'RF'),
    ('9', 'PY'),
    ('10', 'AD'),
    ('11', 'MC'),
    ('12', 'MP'),
)

UNDEFINED_LIST = list([('Undefined', '0')])


AP_INV_DOCUMENT_TYPES = (
    ('1', 'Invoice'),
    ('2', 'Debit Note'),
    ('3', 'Credit Note'),
    # ('4', 'Interest'),
)


AR_INV_DOCUMENT_TYPES = (
    ('1', 'Invoice'),
    ('2', 'Debit Note'),
    ('3', 'Credit Note'),
    # ('4', 'Interest'),
)


DOCUMENT_TYPES = (
    ('1', 'Invoice'),
    ('2', 'Debit Note'),
    ('3', 'Credit Note'),
    ('4', 'Interest'),
    ('5', 'Unapplied Cash'),
    ('6', 'Prepayment'),
    ('7', 'Receipt'),
    ('8', 'Refund'),
    ('9', 'Payment'),
    ('10', 'Adjustment'),
    ('11', 'Miscellaneous Receipt'),
    ('12', 'Miscellaneous Payment'),
)

DOCUMENT_TYPE_REVERSED = list([type[::-1] for type in DOCUMENT_TYPES])
DOCUMENT_TYPE_DICT = dict(DOCUMENT_TYPE_REVERSED + UNDEFINED_LIST)


GL_INTEGRATION_OPTIONS = (
    ('G/L Entry Description', '0'),
    ('G/L Detail Reference', '1'),
    ('G/L Detail Description', '2'),
    ('G/L Detail Comment', '3')
)
GL_INTEGRATION_OPTIONS_DICT = dict([ledger[::-1] for ledger in GL_INTEGRATION_OPTIONS])


AR_GL_SOURCE_TYPE = (
    ('Invoice', '100'),
    ('Invoice Detail', '101'),
    ('Debit Note', '200'),
    ('Debit Note Detail', '201'),
    ('Credit Note', '300'),
    ('Credit Note Detail', '301'),
    ('Receipt', '400'),
    ('Receipt Detail', '401'),
    ('Receipt Advance Credit Claim', '402'),
    ('Prepayment', '500'),
    ('Unapplied Cash', '600'),
    # ('Apply Document', '700'),
    # ('Apply Document Detail', '701'),
    ('Miscellaneous Receipt', '800'),
    ('Miscellaneous Receipt Detail', '801'),
    # ('Miscellaneous Adjustment', '900'),
    # ('Miscellaneous Adjustment Detail', '901'),
    # ('Adjustment', '1000'),
    # ('Adjustment Detail', '1001'),
    # ('Refund', '1100'),
    # ('Refund Detail', '1101'),
    # ('Return Customer Check', '1300'),
)
AR_GL_SOURCE_TYPE_DICT = dict([ledger[::-1] for ledger in AR_GL_SOURCE_TYPE])


AP_GL_SOURCE_TYPE = (
    ('Invoice', '100'),
    ('Invoice Detail', '101'),
    ('Debit Note', '200'),
    ('Debit Note Detail', '201'),
    ('Credit Note', '300'),
    ('Credit Note Detail', '301'),
    ('Payment', '400'),
    ('Payment Detail', '401'),
    # ('Payment Advance Credit Claim', '402'),
    # ('Prepayment', '500'),
    # ('Apply Document', '600'),
    # ('Apply Document Detail', '601'),
    ('Miscellaneous Payment', '700'),
    ('Miscellaneous Payment Detail', '701'),
    # ('Miscellaneous Adjustment', '800'),
    # ('Miscellaneous Adjustment Detail', '801'),
    # ('Adjustment', '900'),
    # ('Adjustment Detail', '901'),
    # ('Reverse Check', '1100'),
)
AP_GL_SOURCE_TYPE_DICT = dict([ledger[::-1] for ledger in AP_GL_SOURCE_TYPE])


AR_TRANSACTION_SEGMENT_TYPES = (
    # ('Adjustment Number', '1'),
    # ('Apply By Document Type', '2'),
    ('Apply-To Document Number', '3'),
    ('Bank Code', '4'),
    ('Batch Number', '5'),
    ('Batch Type', '6'),
    # ('Category', '7'),
    ('Check Date', '8'),
    # ('Check Number', '9'),
    ('Check/Receipt Number', '10'),
    ('Comment', '11'),
    # ('Contract', '12'),
    ('Customer Name', '13'),
    ('Customer Number', '14'),
    ('Customer Short Name', '15'),
    ('Description', '16'),
    ('Detail Description', '17'),
    ('Detail Reference', '18'),
    ('Distribution Code', '19'),
    ('Document Number', '20'),
    ('Document Type', '21'),
    ('Entry Number', '22'),
    ('Invoice Number', '23'),
    # ('Item Number/Distribution Code', '24'),
    ('Order Number', '25'),
    ('Payer', '26'),
    ('Payment Code', '27'),
    # ('Payment Type', '28'),
    # ('Posting Sequence', '29'),
    # ('Project', '30'),
    # ('Purchase Order Number', '31'),
    ('Reference', '32'),
    # ('Resource', '33'),
    # ('Reversal Date', '34'),
    # ('Reversal Description', '35'),
    # ('Ship-To Location', '36'),
    ('Tax Group', '37'),
    ('Transaction Type', '38'),
    # ('Deposit Number', '39')
)
AR_TRANSACTION_SEGMENT_TYPES_DICT = dict([ledger[::-1] for ledger in AR_TRANSACTION_SEGMENT_TYPES])


AP_TRANSACTION_SEGMENT_TYPES = (
    # ('Adjustment Number', '1'),
    # ('Apply By Document Type', '2'),
    ('Apply-To Document Number', '3'),
    ('Bank Code', '4'),
    ('Batch Number', '5'),
    ('Batch Type', '6'),
    # ('Category', '7'),
    ('Check Date', '8'),
    ('Check Number', '9'),
    ('Comment', '10'),
    # ('Contract', '11'),
    ('Description', '12'),
    ('Detail Description', '13'),
    ('Detail Reference', '14'),
    ('Distribution Code', '15'),
    ('Document Number', '16'),
    ('Document Type', '17'),
    ('Entry Number', '18'),
    ('Invoice Number', '19'),
    ('Order Number', '20'),
    ('Payee', '21'),
    ('Payment Code', '22'),
    # ('Posting Sequence', '23'),
    # ('Project', '24'),
    # ('Purchase Order Number', '25'),
    ('Reference', '26'),
    # ('Remit To', '27'),
    # ('Remit-To Location', '28'),
    # ('Resource', '29'),
    # ('Reversal Date', '30'),
    # ('Reversal Description', '31'),
    ('Tax Group', '32'),
    ('Transaction Type', '33'),
    ('Vendor Name', '34'),
    ('Vendor Number', '35'),
    ('Vendor Short Name', '36'),
)
AP_TRANSACTION_SEGMENT_TYPES_DICT = dict([ledger[::-1] for ledger in AP_TRANSACTION_SEGMENT_TYPES])


ACCOUNT_TYPES = (
    # ('1', 'Open Item'),
    ('2', 'Balance Forward'),
    ('3', 'All Customer'),
)

REVERSE_TO_PERIOD_LIST = (
    ('1', 'Next Period'),
    ('2', 'Specific Period'),
)

SOURCE_LEDGER = (
    ('SP', 'Sales & Purchase'),
    ('INV', 'Inventory'),
    ('AR', 'Account Receivable'),
    ('AP', 'Account Payable'),
    ('GL', 'General Ledger'),
    ('NOL', 'Undefined')
)

SOURCE_LEDGER_DICT = dict([ledger[::-1] for ledger in SOURCE_LEDGER])


RATE_TYPES = (
    ('AV', 'Monthly Average Rate'),
    ('SP', 'Daily Spot Rate'),
    ('SR', 'Source Rate'),
    ('TA', 'Financial Trnslation-Average'),
    ('TR', 'Financial Trnslation-Current')
)

RATE_TYPES_DICT = dict([ledger[::-1] for ledger in RATE_TYPES])


SOURCE_TYPES_GL = (
    ('GL-AD', 'Audit Adjustments (G/L Entry)'),
    ('GL-CL', 'G/L Closing Entry'),
    ('GL-CV', 'G/L Data Conversion Entry'),
    ('GL-JE', 'G/L Journal Entry'),
    ('GL-PV', 'G/L Payment Voucher'),
    ('GL-RV', 'G/L Revaluation Transactions')
)

SOURCE_TYPES_GL_KEY = list([(type[0], type[0]) for type in SOURCE_TYPES_GL])

SOURCE_TYPES_AP = (
    ('AP-AD', 'A/P Adjustments'),
    ('AP-CR', 'A/P Credit Note'),
    ('AP-DB', 'A/P Debit Note'),
    ('AP-GL', 'A/P Revaluation'),
    ('AP-IN', 'A/P Invoice'),
    ('AP-PY', 'A/P Check'),
    ('AP-RD', 'A/P Rounding'),
    ('AP-RV', 'A/P Revaluation'),
)

SOURCE_TYPES_AR = (
    ('AR-AD', 'A/R Adjustments'),
    ('AR-CR', 'A/R Credit Note'),
    ('AR-DB', 'A/R Debit Note'),
    ('AR-GL', 'A/R Revaluation'),
    ('AR-IN', 'A/R Invoice'),
    ('AR-PY', 'A/R Payment Received'),
    ('AR-RD', 'A/R Rounding'),
    ('AR-RV', 'A/R Revaluation'),
)

SOURCE_TYPES = tuple(list(SOURCE_TYPES_GL) + list(SOURCE_TYPES_AP) + list(SOURCE_TYPES_AR))

CURRENCY_REPORT_LIST = (
    ('1', 'Functional Currency'),
    ('2', 'Source and Functional Currency '),
)

REVALUATION_METHODS = (
    ('Undefined', 0),
    ('Realized and Unrealized Gain/Loss', 1),
    ('Realized Gain/Loss', 2),
)


TRANSACTION_TYPES = (
    ('Undefined', 0),
    ('AR Invoice', 1),
    ('AP Invoice', 2),
    ('AR Receipt', 3),
    ('AP Payment', 4),
    ('GL', 5),
    ('AD', 11),
)

TRANSACTION_TYPES_REVERSED = list([type[::-1] for type in TRANSACTION_TYPES])


PRINT_TYPES = dict((
    ('Print Preview', 0),
    ('Print Delivery Order', 1),
    ('Print Tax Invoice', 2),
    ('Print Packing List', 3),
))

CONTACT_TYPES = (
    ('Undefined', '0'),
    ('Customer', '1'),
    ('Supplier', '2'),
    ('Location', '3'),
    ('Delivery', '4'),
    ('Consignee', '5'),
)

CONTACT_TYPES_DICT = dict(CONTACT_TYPES)

SEGMENT_FILTER = (
    ('Segment', '2'),
    ('Account', '1'),
)

SEGMENT_FILTER_DICT = dict(SEGMENT_FILTER)

REPORT_TYPE = (
    ('Provisional', '2'),
    ('Standard', '1'),
)

INV_IN_OUT_FLAG = (
    ('IN', '1'),
    ('Transfer', '2'),
    ('OUT', '3'),
)

INV_PRICE_FLAG = (
    ('1', 'PURCHASE'),
    ('2', 'STOCKLIST'),
    ('3', 'RETAIL'),
)

COSTING_METHOD = (
    (False, 'Standard Costing'),
    (False, 'Moving Average'),
    (True, 'FIFO'),
    (False, 'LIFO'),
    (False, 'Weighted Average'),
)

INV_DOC_TYPE = (
    ('0', 'Order'),
    ('1', 'DO/Invoice'),
    ('2', 'Sales D/N'),
    ('3', 'Sales C/N'),
    ('4', 'Purchase D/N'),
    ('5', 'Purchase C/N'),
    ('6', 'Inventory'),
)


SLS_NUM_DOC_TYPE = (
    ('0', 'Sales Order'),
    ('1', 'Sales Invoice'),
    ('2', 'Sales Debit Note'),
    ('3', 'Sales Credit Note'),
    ('4', 'Sales Receipt'),
    ('5', 'Sales Interest'),
    ('6', 'Sales Revaluation'),
)

PUR_NUM_DOC_TYPE = (
    ('0', 'Purchase Order'),
    ('1', 'Purchase Invoice'),
    ('2', 'Purchase Debit Note'),
    ('3', 'Purchase Credit Note'),
    ('4', 'Purchase Payment'),
    ('5', 'Purchase Interest'),
    ('6', 'Purchase Revaluation'),
)


RECEIPT_TRANSACTION_TYPES = (
    ('1', 'Receipt'),
    ('2', 'Misc Receipt'),
    ('3', 'Unapplied Cash'),
)

RECEIPT_TRANSACTION_TYPES_DICT = dict([type[::-1] for type in RECEIPT_TRANSACTION_TYPES])

PAYMENT_TRANSACTION_TYPES = (
    ('1', 'Payment'),
    ('2', 'Misc Payment'),
)

PAYMENT_TRANSACTION_TYPES_DICT = dict([type[::-1] for type in PAYMENT_TRANSACTION_TYPES])

TERMS_CODE = (
    ('0', '0 days'),
    ('30', '30 days'),
    ('60', '60 days'),
    ('90', '90 days'),
)

INPUT_TYPES = (
    ('1', 'Generated'),
    ('2', 'Manual Entry'),
    ('3', 'Imported'),
)

INPUT_TYPE_REVERSED = list([type[::-1] for type in INPUT_TYPES])
INPUT_TYPE_DICT = dict(INPUT_TYPE_REVERSED + UNDEFINED_LIST)

GL_REPORT_LIST = (
    ('1', 'Balances as of Year/Period'),
    ('2', 'Net Changes for the Period'),

)

SOURCE_APPLICATION = (
    ('4', 'Account Payable'),
    ('3', 'Account Receivable')
)

ACCOUNT_SET_TYPE = (
    ('1', 'AR Account Set'),
    ('2', 'AP Account Set'),
)

ACCOUNT_SET_TYPE_DICT = dict([account[::-1] for account in ACCOUNT_SET_TYPE])

DIS_CODE_TYPE = (
    ('1', 'AR Distribution Code'),
    ('2', 'AP Distribution Code'),
)

DIS_CODE_TYPE_REVERSED = list([type[::-1] for type in DIS_CODE_TYPE])
DIS_CODE_TYPE_DICT = dict(DIS_CODE_TYPE_REVERSED)

PAYMENT_CODE_TYPE = (
    ('1', 'AR Payment Code'),
    ('2', 'AP Payment Code'),
)

PAYMENT_CODE_TYPE_DICT = dict([account[::-1] for account in PAYMENT_CODE_TYPE])

ST_REPORT_LIST = (
    # ('1', 'IL2601 Stock Listing (FIFO) by Location & Item'),
    ('1', 'IL2601 Stock Listing (FIFO)'),
    ('3', 'IR4C00 Stock Value Report By Location'),
    ('4', 'IR4900 Yearly Transaction Summary By Transaction Code'),
    ('5', 'IR4600 Monthly Transaction Summary By Item & Location'),
    ('6', 'IR4300 Stock Value Report By Location & Item'),
    ('7', 'IR4200 Stock Value Report By Item And Location'),
)

EXCHANGE_RATE_TYPE = {
    '1': 'SALES',
    '2': 'PURCHASE',
    '3': 'ACCOUNTING',
}

RETAINAGE_REPORT_TYPES = (
    ('1', 'No Reporting'),
    ('2', 'At Time of Retainage Document'),
    ('3', 'At Time of Original Document'),
)

TAX_BASE_TYPES = (
    ('1', 'Selling price'),
    ('2', 'Standard cost'),
    ('3', 'Most recent cost'),
    ('4', 'Alternate amount 1'),
    ('5', 'Alternate amount 2'),
)

TAX_CLASS = (
    ('Standard Rate', 1),
    ('Zero Rate', 2),
    ('Exempted', 3),
    ('Out of Scope', 4),
)

TAX_CLASS_DICT = dict(TAX_CLASS)

TAX_TRACK_CLASS = (
    (0, 'UNDEFINED'),
    (1, 'STANDARD RATED'),
    (2, 'ZERO RATED'),
    (3, 'EXEMPTED',),
    (4, 'OUT OF SCOPE'),
)

TAX_TRACK_CLASS_DICT = dict(TAX_TRACK_CLASS)

LOCATION_TABS = dict((
    ('Location', '0'),
    ('Contact', '1'),
    ('Item', '2'),
))

ITEM_TABS = dict((
    ('Load Stock', '1'),
    ('Item', '2'),
))

EDIT_TYPE = dict((
    ('Copy', '1'),
    ('Edit', '0'),
))

TAX_REPORT_LEVEL = (
    ('1', 'At invoice level'),
    ('2', 'No reporting'),
)

TAX_TRX_TYPES = (
    ('1', 'Sales'),
    ('2', 'Purchases'),
)

TAX_TRX_TYPES_2 = (
    ('1', 'Sale'),
    ('2', 'Purchase'),
)

TAX_TRX_TYPES_DICT = dict([tax_type[::-1] for tax_type in TAX_TRX_TYPES])

TAX_TYPE = (
    ('1', 'Customer/Vendor'),
    ('2', 'Item'),
)

TAX_TYPE_REVERSED = list([type[::-1] for type in TAX_TYPE])
TAX_TYPE_DICT = dict(TAX_TYPE_REVERSED)

TAX_CLASS = (
    ('1', 'Standard Rate'),
    ('2', 'Zero Rate'),
    ('3', 'Exempted'),
    ('4', 'Out of Scope'),
)

REPORT_TEMPLATE_TYPES = (
    ('0', 'Profit & Loss'),
    ('1', 'Balance Sheet'),
)

REPORT_TEMPLATE_TYPES_REVERSED = list([type[::-1] for type in REPORT_TEMPLATE_TYPES])
REPORT_TEMPLATE_TYPES_DICT = dict(REPORT_TEMPLATE_TYPES_REVERSED)

TAX_CALCULATION_METHOD = (
    ('1', 'Calculate tax by summary'),
    ('2', 'Calculate tax by detail'),
)

# Setting Accounts Default
ACCOUNT_SALES = '001'
ACCOUNT_PURCHASES = '002'
ACCOUNT_RECEIVABLE = '003'
ACCOUNT_PAYABLE = '004'
FOREIGN_EXCHANGE_GAIN_LOSS = '5041'

AP_FUNCTION_LIST = [
    'journal_AP_add',
    'journal_AP_edit',
    'send_AP_batch',
    'journal_AP_Payment_add',
    'journal_AP_Payment_edit',
    'journal_AP_Payment_send'
]

AR_FUNCTION_LIST = [
    'journal_AR_add',
    'journal_AR_edit',
    'send_AR_batch',
    'ar_receipt_add',
    'ar_receipt_edit',
    'send_batch_receipt'
]

GL_FUNCTION_LIST = [
    'journal_GL_add',
    'journal_GL_edit',
    'send_GL_batch'
]

BANK_FUNCTION_LIST = [
    'reverse_transaction',
]

SEND_FUNCTION_LIST = [
    'send_AP_batch',
    'send_AR_batch',
    'journal_AP_Payment_send',
    'send_batch_receipt',
    'send_GL_batch'
]

MSG_APPLY_CONTENT = u"""
Dear %s:

The attached statement reflects your account balance as of %s. To
view and print the statement, double-click on the statement icon, and then
choose File, Print when the statement is displayed. To save the statement,
copy it from this e-mail to another folder on your computer.

If you have any questions regarding this statement, please contact me.

Note: You require Adobe Acrobat Reader to view this attachment. Adobe
Acrobat Reader is available from www.adobe.com.

Regards,
            """

MSG_APPLY_SUBJECT = u"""Statement of account with %s"""

SOURCE_TYPE_APPLICATION = {
    '1': 'Accounts Payable',
    '2': 'Accounts Receivable',
    '3': 'General Ledger',
    '4': 'Bank Services'
}

ORDER_STATUS = (
    ('Draft', 1),
    ('Sent', 2),
    ('Received', 3),
    ('Delivered', 4),
    ('Partial', 6),
    ('Undefined', 0),
)

ORDER_TYPE = (
    ('SALES ORDER', 1),
    ('PURCHASE ORDER', 2),
    ('SALES DEBIT NOTE', 3),
    ('SALES CREDIT NOTE', 4),
    ('PURCHASE INVOICE', 5),
    ('SALES INVOICE', 6),
    ('PURCHASE DEBIT NOTE', 7),
    ('PURCHASE CREDIT NOTE', 8),
    ('PURCHASE CR DB NOTE', 9),
    ('SALES CR DB NOTE', 10),
    ('UPDATE SALES STATUS', 998),
    ('UPDATE PURCHASE STATUS', 999),
    ('UPDATE S&P STATUS', 1000),
)

ORDER_TYPE_DICT = dict(ORDER_TYPE)

RECURRING_PERIOD_STR = (
    ('Daily', 0),
    ('Weekly', 1),
    # ('Bi-Monthly', 2),
    ('Monthly', 3),
    ('Yearly', 4),
)

RECURRING_PERIOD = tuple([period[::-1] for period in RECURRING_PERIOD_STR])

RECURRING_PERIOD_DICT = dict(RECURRING_PERIOD_STR)

TYPE_ITEM_CATEGORY = {
    ('1', 'S&P MODULE'),
    ('2', '----- ALL ------'),
    ('3', 'INVENTORY MODULE')
}


LOCATION_PRICE_TYPE = (
    ('1', 'SIN $'),
    ('2', 'OTHERS')
)

LOCATION_STOCK_CLASS = (
    ('1', 'Internal Stock'),
    ('2', 'External Stock'),
)

TRN_CODE_TYPE = (
    ('Global', '0'),
    ('Inventory Code', '1'),
    ('Sales Number File', '2'),
    ('Purchase Number File', '3'),
    ('Accounting', '4'),
)

TRN_CODE_TYPE_DICT = dict(TRN_CODE_TYPE)

PAGE_TYPE = dict((
    ('Inventory', '0'),
    ('S&P', '1'),
    ('Accounting', '2'),
))

GR_DOC_TYPE = (
    ('D', 'D/O'),
    ('I', 'Invoice'),
    ('B', 'D/O and Invoice')
)

GR_DOC_TYPE_REVERSED = list([type[::-1] for type in GR_DOC_TYPE])
GR_DOC_TYPE_DICT = dict(GR_DOC_TYPE_REVERSED)

TRANS_CODE = (
    ('1', 'PDN - Purchase Debit Note'),
    ('2', 'PCN - Purchase Credit Note')
)

QTY_CHOICES = (
    ('1', 'Quantity'),
    ('2', 'Amount'),
    ('3', 'Quantity & Amount')
)

TRANSACTION_CODE = (('1', 'S/O'),
                    ('2', 'P/O'),
                    ('5', 'G/R'),
                    ('6', 'D/O')
                    )

COPY_ID = (
    ('Edit Existing', 0),
    ('Copy', 1),
)

EMAIL_MSG_CONST = {
    'company_name': 'COMPANY_NAME',
    'company_phone': 'COMPANY_PHONE',
    'vendor_name': 'VENDOR_NAME',
    'customer_name': 'CUSTOMER_NAME',
    'currency': 'AMOUNT_CURRENCY',
    'amount': 'OUTSTANDING_AMOUNT',
    'due_days': 'DAYS_OVERDUE',
    'pay_term': 'CUS_PAYMENT_TERM',
    'date': 'DATE',
}

VENDOR_DEFAULT_MSG = """                                                                    COMPANY_NAME


DATE


Dear VENDOR_NAME,

Enclosed please find our check as payment on our account.
If you have any questions regarding the payment, please call our accounting department at COMPANY_PHONE
Yours Sincerely,
COMPANY_NAME



Manager
Accounts Payable

"""


CUSTOMER_DEFAULT_MSG = """                                                                    COMPANY_NAME


DATE


Dear CUSTOMER_NAME,


It has come to our attention that a portion of the balance of your account has long been outstanding; that is a total of AMOUNT_CURRENCY OUTSTANDING_AMOUNT has been outstanding for more than DAYS_OVERDUE days.

We wish to point out that our terms of payment are met CUS_PAYMENT_TERM days, and, if this unpaid amount is not cleared up immediately, we will be forced to initiate legal action.

Yours Sincerely,


Credit Manager
COMPANY_NAME

"""

GL_TRX_REPORT_OPTIONS = dict((
    ('Emtpy', '0'),
    ('GL Entry Description', '1'),
    ('GL Transaction Reference', '2'),
    ('GL Transaction Description', '3'),
    ('GL Transaction Comment', '4'),
))

-- INSERT ACCOUNTING TRANSACTIONS DATA --
-- WARNING: You need to replace @company_id with the actual number in order to run this query!! --
SET @company_id = 6; -- 6 = Kento

-- insert accounting_batch --
INSERT INTO accounting_batch(
`batch_no`, `description`, `status`, `update_date`, `create_date`,
`update_by`, `is_hidden`, `batch_date`, `input_type`, `posting_sequence`,
`batch_amount`, `batch_type`, `company_id`, `no_entries`, `currency_id`,
`document_type`, `related_batch_id`, `source_ledger`)
SELECT CNTBTCH batch_no
	  ,BTCHDESC description
	  ,(CASE WHEN BTCHSTTS=3 THEN 2 WHEN BTCHSTTS=4 THEN 3 ELSE 1 END) AS status
    ,date_format(DTELSTEDIT,'%Y-%m-%d') update_date
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,null update_by
    ,0 is_hidden
    ,date_format(DATEBTCH,'%Y-%m-%d') batch_date
    ,if(BTCHTYPE=1,'2','1') input_type -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    ,POSTSEQNBR posting_sequence
    ,AMTENTR batch_amount
    ,2 batch_type -- TRANSACTION_TYPES['AP Invoice'] --
    ,@company_id company_id
    ,CNTINVCENT no_entries
    ,(select id from currencies_currency where code='SGD') currency_id
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
    ,null related_batch_id
    ,SRCEAPPL source_ledger
FROM ikari_db_sage300.apibc -- AP Invoice Batches --
UNION
SELECT CNTBTCH batch_no
	  ,BATCHDESC description
	  ,(CASE WHEN BATCHSTAT=3 THEN 2 WHEN BATCHSTAT=4 THEN 3 ELSE 1 END) AS status
    ,date_format(DATELSTEDT,'%Y-%m-%d') update_date
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,null update_by
    ,0 is_hidden
    ,date_format(DATEBTCH,'%Y-%m-%d') batch_date
    ,if(BATCHTYPE=1,'2','1') input_type -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    ,POSTSEQNBR posting_sequence -- Posting Sequence No --
    ,AMTENTER batch_amount -- Batch Total --
    ,4 batch_type -- TRANSACTION_TYPES['AP Payment'] --
    ,@company_id company_id
    ,CNTENTER no_entries -- Count Entries --
    ,(CASE WHEN CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURN)
      END) currency_id
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
    ,null related_batch_id
    ,SRCEAPPL source_ledger -- Source Application --
FROM ikari_db_sage300.apbta -- AP Payment and Adjustment Batches --
WHERE PAYMTYPE='PY' -- Payment Type --
UNION
SELECT CNTBTCH batch_no
	  ,BTCHDESC description
	  ,(CASE WHEN BTCHSTTS=3 THEN 2 WHEN BTCHSTTS=4 THEN 3 ELSE 1 END) AS status
    ,date_format(DTELSTEDIT,'%Y-%m-%d') update_date
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,null update_by
    ,0 is_hidden
    ,date_format(DATEBTCH,'%Y-%m-%d') batch_date
    ,if(BTCHTYPE=1,'2','1') input_type -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    ,POSTSEQNBR posting_sequence
    ,AMTENTR batch_amount
    ,1 batch_type -- TRANSACTION_TYPES['AR Invoice'] --
    ,@company_id company_id
    ,CNTINVCENT no_entries
    ,(select id from currencies_currency where code='SGD') currency_id
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
    ,null related_batch_id
    ,SRCEAPPL source_ledger
FROM ikari_db_sage300.aribc -- AR Invoice Batches --
UNION
SELECT CNTBTCH batch_no
	  ,BATCHDESC description
	  ,(CASE WHEN BATCHSTAT=3 THEN 2 WHEN BATCHSTAT=4 THEN 3 ELSE 1 END) AS status
    ,date_format(DATELSTEDT,'%Y-%m-%d') update_date
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,null update_by
    ,0 is_hidden
    ,date_format(DATEBTCH,'%Y-%m-%d') batch_date
    ,if(BATCHTYPE=1,'2','1') input_type -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    ,POSTSEQNBR posting_sequence
    ,AMTENTER batch_amount
    ,3 batch_type -- TRANSACTION_TYPES['AR Receipt'] --
    ,@company_id company_id
    ,CNTENTER no_entries
    ,(CASE WHEN CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURN)
      END) currency_id
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
    ,null related_batch_id
    ,SRCEAPPL source_ledger
FROM ikari_db_sage300.arbta -- AR Receipt and Adjustment Batches --
where CODEPYMTYP='CA' -- Code Payment Type --
UNION
SELECT
	  `BATCHID` AS `batch_no`,
	  `BTCHDESC` AS `description`,
	  (CASE WHEN `BATCHSTAT` = '4' THEN 2 WHEN `BATCHSTAT` = '3' THEN 3 WHEN `BATCHSTAT` = '6' THEN 7 ELSE 1 END) AS `status`,
    DATE_FORMAT(DATEEDIT,'%Y-%m-%d') AS `update_date`,
    DATE_FORMAT(DATECREAT,'%Y-%m-%d') AS `create_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    DATE_FORMAT(`DATECREAT`,'%Y-%m-%d') AS `batch_date`,
    IF(`BATCHTYPE` = 1, '2', '1') AS `input_type`, -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    `POSTNGSEQ` AS `posting_sequence`,
    `DEBITTOT` AS `batch_amount`,
    5 AS `batch_type`, -- TRANSACTION_TYPES['GL'] --
    @company_id AS `company_id`,
    `ENTRYCNT` AS `no_entries`,
    /* (CASE WHEN `gljed`.`SCURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `gljed`.`SCURNCODE`)
      END) AS `currency_id`, */
    (SELECT `id` FROM `currencies_currency` WHERE `id` = (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id)) AS `currency_id`,
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `related_batch_id`,
    `SRCELEDGR` AS `source_ledger`
FROM `ikari_db_sage300`.`glbctl`; -- AR Receipt and Adjustment Batches --
/* LEFT JOIN (
	SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
	FROM `ikari_db_sage300`.`gljed` GROUP BY `ikari_db_sage300`.`gljed`.`BATCHNBR`
) AS `gljed` ON `gljed`.`BATCHNBR` = `ikari_db_sage300`.`glbctl`.`BATCHID`
WHERE `gljed`.`SRCETYPE` = 'JE'; -- Code Payment Type -- */

#Insert accounting_journal
INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`, `orig_exch_rate_fk_id`,
`is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`, `perd_month`, `perd_year`,
`receipt_unapplied`, `customer_unapplied`, `error_entry`)
SELECT j.CNTITEM code
	,j.INVCDESC name
	,2 journal_type -- TRANSACTION_TYPES)['AP Invoice'] --
	,j.TEXTTRX document_type -- DOCUMENT_TYPE_DICT --
	,j.PONBR po_number
	,j.ORDRNBR order_number
	,j.IDINVC document_number
    ,date_format(j.DATEINVC,'%Y-%m-%d') document_date
    ,date_format(j.DATEBUS,'%Y-%m-%d') posting_date
    ,j.AMTTOTDIST amount
    ,j.AMTTAXTOT tax_amount
    ,j.AMTGROSTOT total_amount
    ,(select status
        from accounting_batch
        where batch_type=2 -- TRANSACTION_TYPES['AP Invoice'] --
            and batch_no=j.CNTBTCH
            and company_id=@company_id
     ) status
    ,date_format(j.AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(j.AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN j.CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=j.CODECURN)
      END) currency_id
    ,NULL customer_id
    ,NULL order_id
    ,(SELECT id FROM suppliers_supplier WHERE code=j.IDVEND AND company_id=@company_id) supplier_id
    ,(SELECT id from taxes_tax
      WHERE tax_group_id =
      (SELECT id FROM taxes_taxgroup WHERE
        code = j.CODETAXGRP and
        transaction_type =2 and -- TAX_TRX_TYPES_DICT['Purchases'] --
        company_id=@company_id)
      and number = j.TAXCLASS1
      and company_id=@company_id) tax_id
    ,j.AMTGROSTOT document_amount
    ,date_format(j.DATEDUE,'%Y-%m-%d') due_date
    ,j.EXCHRATEHC exchange_rate
    ,0 original_amount
    ,NULL original_currency_id
    ,NULL payment_account_id
    ,0 payment_amount
    ,NULL payment_check_number
    ,NULL payment_code_id
    ,NULL payment_currency_id
    ,NULL reference
    ,NULL source_type
    ,'0' transaction_type
    ,NULL bank_id
    ,j.AMTGROSTOT outstanding_amount
    ,0 paid_amount
    ,(CASE WHEN bl.SWPAID=NULL THEN 0 ELSE bl.SWPAID END) is_fully_paid
    ,0 payment_number
    ,NULL invoice_number
    ,1 is_manual_doc
    ,(select id from accounting_batch
      where batch_type=2 -- TRANSACTION_TYPES['AP Invoice'] --
      and batch_no=j.CNTBTCH
      and company_id=@company_id) batch_id
    ,(select id from accounts_accountset
      where code = j.IDACCTSET
      and company_id=@company_id) account_set_id
    ,NULL exchange_rate_fk_id
    ,NULL source_ledger
    ,j.ORIGRATEHC orig_exch_rate
    ,NULL orig_exch_rate_fk_id
    ,0 is_auto_reverse
    ,NULL reverse_to_period
    ,NULL reverse_to_period_val
    ,0 is_rev_do
    ,date_format(j.DATEBUS,'%m') perd_month
    ,date_format(j.DATEBUS,'%Y') perd_year
    ,0 receipt_unapplied
    ,0 customer_unapplied
    ,0 error_entry
FROM ikari_db_sage300.apibh j -- AP Invoices --
LEFT JOIN ikari_db_sage300.apobl bl
on j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.txttrxtype
UNION
SELECT CNTENTR code
    ,TEXTRMIT name
    ,4 journal_type -- TRANSACTION_TYPES)['AP Payment'] --
    ,(CASE
        WHEN RMITTYPE = 1 THEN '9'
        WHEN RMITTYPE = 4 THEN '12'
        WHEN RMITTYPE = 2 THEN '6'
        WHEN RMITTYPE = 3 THEN '0' -- no constant document_type available for rmittype = 3 = apply document
        ELSE '10'
      END) document_type -- DOCUMENT_TYPE_DICT
    ,NULL po_number
    ,NULL order_number
    ,DOCNBR document_number
    ,date_format(DATERMIT,'%Y-%m-%d') document_date
    ,date_format(DATEBUS,'%Y-%m-%d') posting_date
    ,if(CODETAXGRP IS NULL or CODETAXGRP = '',AMTRMIT,TXBSE1TC) amount
    ,TXTOTTC tax_amount
    ,AMTRMIT total_amount
    ,(select status
        from accounting_batch
        where batch_type=4 -- TRANSACTION_TYPES['AP Payment'] --
            and batch_no=CNTBTCH
            and company_id=@company_id
     ) status -- STATUS_TYPE_DICT --
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) currency_id
    ,NULL customer_id
    ,NULL order_id
    ,(SELECT id FROM suppliers_supplier WHERE code=IDVEND AND company_id=@company_id) supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id =
            (SELECT id FROM taxes_taxgroup WHERE
                CODE = CODETAXGRP and
                transaction_type =2 and -- TAX_TRX_TYPES_DICT['Purchases'] --
                company_id=@company_id)
        and number = TAXCLASS1
        and company_id=@company_id) tax_id
    ,0 document_amount
    ,NULL due_date
    ,RATEEXCHHC exchange_rate
    ,AMTRMITTC original_amount
    ,(CASE WHEN CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURN)
      END) original_currency_id
    ,NULL payment_account_id
    ,AMTRMIT payment_amount
    ,IDRMIT payment_check_number
    ,(SELECT id FROM accounting_paymentcode where code=PAYMCODE and source_type='2'
        and company_id=@company_id) payment_code_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) payment_currency_id
    ,TXTRMITREF reference
    ,NULL source_type
    ,(CASE
        when RMITTYPE=1 then '1'
        when RMITTYPE=4 then '2'
        else '0'
     END) transaction_type
    ,(select id from banks_bank where code=IDBANK and company_id=@company_id) bank_id
    ,0 outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,CNTPAYMENT payment_number
    ,if(RMITTYPE=1,NULL,IDINVCMTCH) invoice_number
    ,1 is_manual_doc
    ,(select id from accounting_batch
      where batch_type=4 -- TRANSACTION_TYPES['AP Payment'] --
      and batch_no=CNTBTCH
      and company_id=@company_id) batch_id
    ,(select id from accounts_accountset
      where code = IDACCTSET
      and company_id=@company_id) account_set_id
    ,NULL exchange_rate_fk_id
    ,NULL source_ledger
    ,NULL orig_exch_rate
    ,NULL orig_exch_rate_fk_id
    ,0 is_auto_reverse
    ,NULL reverse_to_period
    ,NULL reverse_to_period_val
    ,0 is_rev_do
    ,date_format(DATEBUS,'%m') perd_month
    ,date_format(DATEBUS,'%Y') perd_year
    ,0 receipt_unapplied
    ,0 customer_unapplied
    ,0 error_entry
FROM ikari_db_sage300.aptcr
UNION
SELECT j.CNTITEM code
    ,j.INVCDESC name
    ,1 journal_type -- TRANSACTION_TYPES)['AR Invoice'] --
    ,j.TEXTTRX document_type -- DOCUMENT_TYPE_DICT --
    ,j.CUSTPO po_number
    ,j.ORDRNBR order_number
    ,j.IDINVC document_number
    ,date_format(j.DATEINVC,'%Y-%m-%d') document_date
    ,date_format(j.DATEBUS,'%Y-%m-%d') posting_date
    ,j.AMTINVCTOT amount
    ,j.AMTTAXTOT tax_amount
    ,j.AMTNETTOT total_amount
    ,(select status
        from accounting_batch
        where batch_type=1 -- TRANSACTION_TYPES['AR Invoice'] --
            and batch_no=j.CNTBTCH
            and company_id=@company_id
     ) status -- STATUS_TYPE_DICT --
    ,date_format(j.AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(j.AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN j.CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=j.CODECURN)
      END) currency_id
    ,(select id from customers_customer
      where code=j.IDCUST and company_id=@company_id) customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id =
            (SELECT id FROM taxes_taxgroup WHERE
                CODE = j.CODETAXGRP and
                transaction_type =1 and -- TAX_TRX_TYPES_DICT['Sales'] --
                company_id=@company_id)
        and number = j.TAXSTTS1
        and company_id=@company_id) tax_id
    ,j.AMTNETTOT document_amount
    ,date_format(j.DATEDUE,'%Y-%m-%d') due_date
    ,j.EXCHRATEHC exchange_rate
    ,0 original_amount
    ,NULL original_currency_id
    ,NULL payment_account_id
    ,0 payment_amount
    ,NULL payment_check_number
    ,NULL payment_code_id
    ,NULL payment_currency_id
    ,NULL reference
    ,NULL source_type
    ,'0' transaction_type
    ,NULL bank_id
    ,j.AMTNETTOT outstanding_amount
    ,0 paid_amount
    ,bl.swpaid is_fully_paid
    ,0 payment_number
    ,NULL invoice_number
    ,1 is_manual_doc
    ,(select id from accounting_batch
      where batch_type=1 -- TRANSACTION_TYPES['AR Invoice'] --
      and batch_no=j.CNTBTCH
      and company_id=@company_id) batch_id
    ,(select id from accounts_accountset
      where code = j.IDACCTSET
      and company_id=@company_id) account_set_id
    ,NULL exchange_rate_fk_id
    ,NULL source_ledger
    ,j.ORIGRATEHC orig_exch_rate
    ,NULL orig_exch_rate_fk_id
    ,0 is_auto_reverse
    ,NULL reverse_to_period
    ,NULL reverse_to_period_val
    ,0 is_rev_do
    ,date_format(j.DATEBUS,'%m') perd_month
    ,date_format(j.DATEBUS,'%Y') perd_year
    ,0 receipt_unapplied
    ,0 customer_unapplied
    ,0 error_entry
FROM ikari_db_sage300.aribh j
JOIN ikari_db_sage300.arobl bl
on j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.trxtypetxt
UNION
SELECT CNTITEM code
    ,TEXTRMIT name
    ,3 journal_type -- TRANSACTION_TYPES['AR Receipt'] --
    ,(CASE
        WHEN RMITTYPE = 1 THEN '7'
        WHEN RMITTYPE = 5 THEN '11'
        WHEN RMITTYPE = 2 THEN '6'
        WHEN RMITTYPE = 3 THEN '5'
        WHEN (RMITTYPE = 4 OR RMITTYPE = 6)
            THEN '0' -- no constant document_type available for rmittype = 4,6 = apply document, Write-Off
        ELSE '10'
      END) document_type -- DOCUMENT_TYPE_DICT
    ,NULL po_number
    ,NULL order_number
    ,DOCNBR document_number
    ,date_format(DATERMIT,'%Y-%m-%d') document_date
    ,date_format(DATEBUS,'%Y-%m-%d') posting_date
    ,if(CODETAXGRP IS NULL or CODETAXGRP = '',AMTRMIT,TXBSE1TC) amount
    ,TXTOTTC tax_amount
    ,AMTRMIT total_amount
    ,(select status
        from accounting_batch
        where batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
            and batch_no=CNTBTCH
            and company_id=@company_id
     ) status -- STATUS_TYPE_DICT --
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) currency_id
    ,(select id from customers_customer
      where code=IDCUST and company_id=@company_id) customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id =
            (SELECT id FROM taxes_taxgroup WHERE
                CODE = CODETAXGRP and
                transaction_type =1 and -- TAX_TRX_TYPES_DICT['Sales'] --
                company_id=@company_id)
        and number = TAXCLASS1
        and company_id=@company_id) tax_id
    ,0 document_amount
    ,NULL due_date
    ,RATEEXCHHC exchange_rate
    ,AMTRMITTC original_amount
    ,(CASE WHEN CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURN)
      END) original_currency_id
    ,NULL payment_account_id
    ,AMTRMIT payment_amount
    ,IDRMIT payment_check_number
    ,(SELECT id FROM accounting_paymentcode where code=CODEPAYM and source_type='1'
        and company_id=@company_id) payment_code_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) payment_currency_id
    ,TXTRMITREF reference
    ,NULL source_type
    ,(CASE
        when RMITTYPE=1 then '1'
        when RMITTYPE=5 then '2'
        else '0'
     END) transaction_type
    ,(select id from banks_bank where code=IDBANK and company_id=@company_id) bank_id
    ,0 outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,NULL payment_number
    ,if(RMITTYPE=1,NULL,IDINVCMTCH) invoice_number
    ,1 is_manual_doc
    ,(select id from accounting_batch
        where batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
            and batch_no=CNTBTCH
            and company_id=@company_id) batch_id
    ,(select id from accounts_accountset
        where code = IDACCTSET
            and company_id=@company_id) account_set_id
    ,NULL exchange_rate_fk_id
    ,NULL source_ledger
    ,NULL orig_exch_rate
    ,NULL orig_exch_rate_fk_id
    ,0 is_auto_reverse
    ,NULL reverse_to_period
    ,NULL reverse_to_period_val
    ,0 is_rev_do
    ,date_format(DATEBUS,'%m') perd_month
    ,date_format(DATEBUS,'%Y') perd_year
    ,REMUNAPL receipt_unapplied
    ,REMUNAPLTC customer_unapplied
    ,0 error_entry
FROM ikari_db_sage300.artcr
UNION
SELECT `j`.`BTCHENTRY` AS `code`,
    `j`.`JRNLDESC` AS `name`,
    5 AS `journal_type`, -- TRANSACTION_TYPES)['GL'] --
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT --
    NULL AS `po_number`,
    NULL AS `order_number`,
    NULL AS `document_number`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `document_date`,
    NULL AS `posting_date`,
    `j`.`JRNLDR` AS `amount`,
    0 AS `tax_amount`,
    `j`.`JRNLDR` AS `total_amount`,
    (SELECT `status`
     FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHID`
     AND `company_id` = @company_id) AS `status`, -- STATUS_TYPE_DICT --
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`j`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
    NULL AS `customer_id`,
    NULL AS `order_id`,
    NULL AS `supplier_id`,
    NULL AS `tax_id`,
    `j`.`JRNLDR` AS `document_amount`,
    NULL AS `due_date`,
    1 AS `exchange_rate`,
    0 AS `original_amount`,
    NULL AS `original_currency_id`,
    NULL AS `payment_account_id`,
    0 AS `payment_amount`,
    NULL AS `payment_check_number`,
    NULL AS `payment_code_id`,
    NULL AS `payment_currency_id`,
    NULL AS `reference`,
    CONCAT( 'GL-',`j`.`SRCETYPE`) AS `source_type`,
    '0' AS `transaction_type`,
    NULL AS `bank_id`,
    `j`.`JRNLDR` AS `outstanding_amount`,
    0 AS `paid_amount`,
    0 AS `is_fully_paid`,
    0 AS `payment_number`,
    NULL AS `invoice_number`,
    0 AS `is_manual_doc`,
    (SELECT `id`
     FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHID`
     AND `company_id` = @company_id) AS `batch_id`,
    NULL AS `account_set_id`,
    NULL AS `exchange_rate_fk_id`,
    'GL' AS `source_ledger`,
    NULL AS `orig_exch_rate`,
    NULL AS `orig_exch_rate_fk_id`,
    0 AS `is_auto_reverse`,
    NULL AS `reverse_to_period`,
    NULL AS `reverse_to_period_val`,
    0 AS `is_rev_do`,
    `j`.`FSCSPERD` AS `perd_month`,
    `j`.`FSCSYR` AS `perd_year`,
    0 AS receipt_unapplied,
    0 AS customer_unapplied,
    `j`.`ERRENTRY` AS error_entry
FROM `ikari_db_sage300`.`gljeh` AS `j`
WHERE `j`.`SRCETYPE` IN ('JE', 'RV', 'RE');


#insert transactions_transaction (AR Entry)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
select t1.* from(select
       (case when j.TEXTTRX=3 then 0 else 1 end) is_credit_account
      ,(case when j.TEXTTRX=3 then 1 else 0 end) is_debit_account
      ,t.AMTTXBL amount
      ,date_format(t.AUDTDATE,'%Y-%m-%d') transaction_date
      ,NULL remark
      ,NULL number
      ,0 is_close
      ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
      ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
      ,NULL update_by
      ,0 is_hidden
      ,(select aa.id from accounts_account aa
        where aa.code=REPLACE(t.IDACCTREV, '-', '')
        and aa.company_id=@company_id) account_id
      ,@company_id company_id
      ,NULL method_id
      ,NULL order_id
      ,(CASE
          WHEN (select CODECURN from ikari_db_sage300.arcus where IDCUST = j.IDCUST)='DOS'
            THEN (select id from currencies_currency where code='SGD')
          ELSE
            (SELECT id from currencies_currency
            where code=(select CODECURN from ikari_db_sage300.arcus where IDCUST = j.IDCUST))
      END)
      ,NULL pair_id
      ,(select id from accounting_journal
        where batch_id=(select id from accounting_batch
                        where batch_no=t.cntbtch
                        and batch_type=1 -- TRANSACTION_TYPES['AR Invoice'] --
                        and company_id=@company_id)
        and code=t.cntitem) journal_id
      ,(SELECT id from taxes_tax
        where tax_group_id =
            (SELECT id FROM taxes_taxgroup WHERE
                CODE =j.CODETAX1 and
                transaction_type =1 and -- TAX_TRX_TYPES_DICT['Sales'] --
                company_id=@company_id)
        and number = t.TAXSTTS1
        and company_id=@company_id) tax_id
      ,t.BASETAX1 base_tax_amount
      ,t.TOTTAX tax_amount
      ,(t.AMTTXBL+t.TOTTAX) total_amount
      ,(select id from accounts_distributioncode
        where code=t.IDDIST
        and company_id=@company_id
        and type=1) distribution_code_id -- DIS_CODE_TYPE['AR Distribution Code'] --
      ,NULL description
      ,j.EXCHRATEHC exchange_rate
      ,(t.TXBSE1HC+t.TXAMT1HC) functional_amount
      ,(select id from currencies_currency where code='SGD') functional_currency_id
      ,date_format(j.DATERATE ,'%Y-%m-%d') rate_date
      ,NULL reference
      ,NULL source_type
      ,(SELECT j0.id FROM accounting_journal j0, accounting_batch b0
        WHERE j0.batch_id = b0.id
        AND j0.document_number = j.INVCAPPLTO
        AND j0.journal_type=1 -- TRANSACTION_TYPES)['AR Invoice'] --
        AND j0.company_id=@company_id
        AND j0.company_id = b0.company_id
        AND b0.batch_no < t.cntbtch
        ORDER BY b0.batch_no desc LIMIT 1) related_invoice_id
      ,t.SWTAXINCL1 is_tax_include
      ,0 is_tax_transaction
      ,if(j.TEXTTRX=3,'1','2')
      ,0 is_report,0 is_clear_tax
FROM ikari_db_sage300.aribd t, ikari_db_sage300.aribh j
where t.cntbtch=j.cntbtch
and t.cntitem=j.cntitem) t1;


#insert AR receipt (receipt)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `adjustment_amount`, `discount_amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT t1.* FROM(SELECT
        1 is_credit_transaction
        ,0 is_debit_transaction
        ,abs(t.AMTPAYM) amount
        ,t.amtadjtot adjustment_amount
        ,t.amtdisctot discount_amount
        ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,t.CNTLINE number
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,aas.control_account_id account_id
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN
            (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `j`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,(select id from accounting_journal
          where batch_id=ab.id
          and code=j.CNTITEM and company_id=@company_id) journal_id
        ,NULL tax_id
        ,0 base_tax_amount
        ,0 tax_amount
        ,abs(t.AMTPAYM) total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,tx.RATEEXCHTC exchange_rate
        ,abs(t.AMTPAYMHC) functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
        ,date_format(tx.RATEDATETC,'%Y-%m-%d') rate_date
        ,NULL reference
        ,NULL source_type
        ,(select id from accounting_journal
          where batch_id = (select id from accounting_batch
          where batch_type=1 -- TRANSACTION_TYPES['AR Invoice'] --
          and batch_no=inv.cntbtch
          and company_id=@company_id)
          and code=inv.cntitem) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'2' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
FROM ikari_db_sage300.artcr j
RIGHT OUTER JOIN ikari_db_sage300.artcp t on j.cntbtch=t.cntbtch
    AND j.CNTITEM=t.CNTITEM
LEFT OUTER JOIN banks_bank bnk on j.idbank=bnk.code
    and bnk.company_id=@company_id
LEFT OUTER JOIN accounts_accountset aas on j.idacctset=aas.code
    and aas.company_id=@company_id
LEFT OUTER JOIN accounting_batch ab on j.cntbtch=ab.batch_no
    and ab.batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
LEFT OUTER JOIN ikari_db_sage300.arpjh tx on t.CODEPAYM=tx.typebtch
    and t.cntbtch=tx.cntbtch
    and t.CNTITEM=tx.cntitem
LEFT OUTER JOIN ikari_db_sage300.aribh inv on t.idinvc=inv.idinvc
    and t.cntbtch=tx.cntbtch
    and t.CNTITEM=tx.cntitem) t1;


#insert AR receipt (misc. receipt)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT t1.* FROM (SELECT
        1 is_credit_transaction
        ,0 is_debit_transaction
        ,t.AMTNETTC amount
        ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,t.CNTLINE number
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,aa.id account_id
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN
            (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `j`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,(select id from accounting_journal
          where batch_id=ab.id
          and code=j.CNTITEM and company_id=@company_id) journal_id
        ,(SELECT id from taxes_tax
            where tax_group_id =
                (SELECT id FROM taxes_taxgroup WHERE
                    CODE =j.codetax1 and
                    transaction_type =1 and -- TAX_TRX_TYPES_DICT['Sales'] --
                    company_id=@company_id)
            and number = tax.TAXCLASS1
            and company_id=@company_id) tax_id
        ,t.TXBSE1TC base_tax_amount
        ,t.TXTOTTC tax_amount
        ,t.AMTDISTTC total_amount
        ,ad.id distribution_code_id
        ,t.GLDESC description
        ,tx.RATEEXCHTC exchange_rate
        ,t.AMTDISTHC functional_amount
        ,(select id from currencies_currency where code='SGD') functional_currency_id
        ,date_format(tx.RATEDATETC,'%Y-%m-%d') rate_date
        ,t.GLREF reference
        ,NULL source_type
        ,NULL related_invoice_id
        ,t.SWTAXINCL1 is_tax_include
        ,0 is_tax_transaction
        ,'2' functional_balance_type
        ,0 is_report,0 is_clear_tax
FROM ikari_db_sage300.artcr j
RIGHT OUTER JOIN ikari_db_sage300.artcn t on j.cntbtch=t.cntbtch
    AND j.CNTITEM=t.CNTITEM
LEFT OUTER JOIN accounting_batch ab on j.cntbtch=ab.batch_no
    and ab.batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
LEFT OUTER JOIN ikari_db_sage300.arpjh tx on t.CODEPAYM=tx.typebtch
    and t.cntbtch=tx.cntbtch
    and t.CNTITEM=tx.cntitem
LEFT OUTER JOIN ikari_db_sage300.arrrd tax on  t.cntbtch=tax.CNTBTCH
    and t.CNTITEM=tax.CNTITEM
    and t.IDACCT=tax.IDACCT
LEFT OUTER JOIN accounts_account aa on t.idacct=aa.code
    and aa.company_id = @company_id
LEFT OUTER JOIN accounts_distributioncode ad on t.IDDISTCODE=ad.code
    and ad.company_id = @company_id) t1;


#Manually remove duplicate AR Receipt transaction
DELETE t1 FROM `transactions_transaction` t1
INNER JOIN `transactions_transaction` t2
WHERE
    `t1`.`company_id`=@company_id
    AND `t2`.`company_id`=@company_id
    AND `t1`.`id` > `t2`.`id`
    AND `t1`.`journal_id` = `t2`.`journal_id`
    AND `t1`.`is_credit_account` = `t2`.`is_credit_account`
    AND `t1`.`is_debit_account` = `t2`.`is_debit_account`
    AND `t1`.`transaction_date` = `t2`.`transaction_date`
    AND `t1`.`number` = `t2`.`number`
    AND `t1`.`currency_id` = `t2`.`currency_id`
    AND `t1`.`amount` = `t2`.`amount`
    AND `t1`.`tax_amount` = `t2`.`tax_amount`
    AND `t1`.`functional_balance_type` = `t2`.`functional_balance_type`
    AND `t1`.`account_id` = `t2`.`account_id`
    AND `t1`.`journal_id` IN (SELECT `id` FROM `accounting_journal` WHERE `journal_type`=3 AND `transaction_type`='2' AND `company_id`=@company_id);


#Insert AD AR-RECEIPT JOURNAL
INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`, `orig_exch_rate_fk_id`,
`is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`, `perd_month`, `perd_year`)
SELECT t1.* FROM (SELECT '1' code
    ,t.idinvc name
    ,11 journal_type -- TRANSACTION_TYPES['AD'] --
    ,'10' document_type -- DOCUMENT_TYPE_DICT
    ,NULL po_number
    ,NULL order_number
    ,t.cntadj document_number
    ,date_format(ar.DATERMIT,'%Y-%m-%d') document_date
    ,date_format(ar.DATEBUS,'%Y-%m-%d') posting_date
    ,abs(t.amtadjtot) amount
    ,0 tax_amount
    ,abs(t.amtadjtot) total_amount
    ,(select status
        from accounting_batch
        where batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
            and batch_no=ar.CNTBTCH
            and company_id=@company_id
     ) status -- STATUS_TYPE_DICT --
    ,date_format(ar.AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(ar.AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN ar.CODECURNBC='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=ar.CODECURNBC)
      END) currency_id
    ,(select id from customers_customer
      where code=ar.IDCUST and company_id=@company_id) customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,NULL tax_id
    ,abs(t.amtadjtot) document_amount
    ,NULL due_date
    ,ar.RATEEXCHHC exchange_rate
    ,0 original_amount
    ,NULL original_currency_id
    ,NULL payment_account_id
    ,0 payment_amount
    ,ar.IDRMIT payment_check_number
    ,(SELECT id FROM accounting_paymentcode where code=ar.CODEPAYM
       and source_type='1' and company_id=@company_id) payment_code_id
    ,NULL payment_currency_id
    ,t.glref reference
    ,NULL source_type
    ,(CASE
        when ar.RMITTYPE=1 then '1'
        when ar.RMITTYPE=5 then '2'
        else '0'
     END) transaction_type
    ,(select id from banks_bank where code=ar.IDBANK and company_id=@company_id) bank_id
    ,0 outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,NULL payment_number
    ,if(ar.RMITTYPE=1,NULL,ar.IDINVCMTCH) invoice_number
    ,1 is_manual_doc
    ,(select id from accounting_batch
        where batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
            and batch_no=ar.CNTBTCH
            and company_id=@company_id) batch_id
    ,(select id from accounts_accountset
        where code = ar.IDACCTSET
            and company_id=@company_id) account_set_id
    ,NULL exchange_rate_fk_id
    ,NULL source_ledger
    ,NULL orig_exch_rate
    ,NULL orig_exch_rate_fk_id
    ,0 is_auto_reverse
    ,NULL reverse_to_period
    ,NULL reverse_to_period_val
    ,0 is_rev_do
    ,date_format(ar.DATEBUS,'%m') perd_month
    ,date_format(ar.DATEBUS,'%Y') perd_year
FROM ikari_db_sage300.artcp t
RIGHT OUTER JOIN ikari_db_sage300.artcr ar on t.cntbtch=ar.cntbtch AND t.CNTITEM=ar.CNTITEM
where t.amtadjtot <> 0 
and t.codepaym = 'CA') t1;



#Insert AD AR-RECEIPT TRANSACTION
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT t1.* FROM(SELECT
        IF(t.amtadjtot < 0, 1, 0) AS `is_credit_account`
        ,IF(t.amtadjtot < 0, 0, 1) AS `is_debit_account`
        ,abs(t.amtadjtot) amount
        ,date_format(ar.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,t.cntline number
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,(SELECT id FROM accounts_account where description=REPLACE(pj.idacct, '-', '') and company_id=@company_id) account_id
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,(CASE WHEN `ar`.`CODECURN` = 'DOS' THEN
            (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `ar`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,(select id from accounting_journal
          where document_number=t.cntadj and
          journal_type=11 and
          document_type='10' and
          company_id=@company_id LIMIT 1) journal_id
        ,NULL tax_id
        ,abs(t.amtadjtot) base_tax_amount
        ,0 tax_amount
        ,abs(t.amtadjtot) total_amount
        ,NULL distribution_code_id
        ,t.textadj description
        ,pj.RATEEXCHHC exchange_rate
        ,abs(t.amtadjhc) functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
        ,pj.RATEDATE rate_date
        ,t.idinvc reference
        ,NULL source_type
        ,(select id from accounting_journal
          where journal_type=1 -- TRANSACTION_TYPES['AR Invoice'] --
          AND document_type IN ('1','2','3')
          and document_number=t.idinvc
          and company_id=@company_id LIMIT 1) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,IF(t.amtadjtot < 0, 2, 1) AS `functional_balance_type`
        ,0 is_report
        ,0 is_clear_tax
FROM ikari_db_sage300.artcp t
RIGHT OUTER JOIN ikari_db_sage300.artcr ar on ar.cntbtch=t.cntbtch AND ar.CNTITEM=t.CNTITEM
LEFT OUTER JOIN ikari_db_sage300.arpjd pj on t.cntbtch=pj.cntbtch AND t.CNTITEM=pj.CNTITEM AND t.amtdbadjtc=pj.amtextndtc AND pj.SRCETYPE='AD' AND pj.ACCTTYPE=2
where t.amtadjtot <> 0 
and t.codepaym = 'CA') t1;


#insert transactions_transaction (AP ENTRY)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
select t1.* from(select
       (case when j.TEXTTRX=3 then 1 else 0 end) is_credit_account
      ,(case when j.TEXTTRX=3 then 0 else 1 end) is_debit_account
      ,t.AMTDISTNET amount
      ,date_format(t.BILLDATE,'%Y-%m-%d') transaction_date
      ,NULL remark
      ,NULL number
      ,0 is_close
      ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
      ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
      ,NULL update_by
      ,0 is_hidden
      ,(select aa.id from accounts_account aa
      where aa.code=t.IDGLACCT
      and aa.company_id=@company_id) account_id
      ,@company_id company_id
      ,NULL method_id
      ,NULL order_id
      ,(CASE
          WHEN (select CURNCODE from ikari_db_sage300.apven where VENDORID = j.idvend)='DOS'
            THEN (select id from currencies_currency where code='SGD')
          ELSE
            (SELECT id from currencies_currency
            where code=(select CURNCODE from ikari_db_sage300.apven where VENDORID = j.idvend))
      END) currency_id
      ,NULL pair_id
      ,(select id from accounting_journal
        where batch_id=(select id from accounting_batch
                        where batch_no=t.cntbtch
                        and batch_type=2 -- TRANSACTION_TYPES['AP Invoice'] --
                        and company_id=@company_id)
        and code=t.cntitem) journal_id
      ,(SELECT id from taxes_tax
        where tax_group_id =
            (SELECT id FROM taxes_taxgroup WHERE
                CODE =j.CODETAX1 and
                transaction_type =2 and -- TAX_TRX_TYPES_DICT['Purchases'] --
                company_id=@company_id)
        and number = t.TAXCLASS1
        and company_id=@company_id) tax_id
      ,t.BASETAX1 base_tax_amount
      ,t.AMTTOTTAX tax_amount
      ,t.AMTDIST total_amount
      ,(select id from accounts_distributioncode
        where code=t.IDDIST
        and company_id=@company_id
        and type=2) distribution_code_id -- DIS_CODE_TYPE['AP Distribution Code'] --
      ,NULL description
      ,j.EXCHRATEHC exchange_rate
      ,t.AMTDISTHC functional_amount
      ,(select id from currencies_currency where code='SGD') functional_currency_id
      ,date_format(j.DATERATE ,'%Y-%m-%d') rate_date
      ,NULL reference
      ,NULL source_type
      ,(SELECT j0.id FROM accounting_journal j0, accounting_batch b0
        WHERE j0.batch_id = b0.id
        AND j0.document_number = j.INVCAPPLTO
        AND j0.journal_type=2 -- TRANSACTION_TYPES)['AP Invoice'] --
        AND j0.company_id=@company_id
        AND j0.company_id = b0.company_id
        AND b0.batch_no < t.cntbtch
        ORDER BY b0.batch_no desc LIMIT 1) related_invoice_id
      ,t.SWTAXINCL1 is_tax_include
      ,0 is_tax_transaction
      ,if(j.TEXTTRX=3,'2','1')
      ,0 is_report,0 is_clear_tax
  FROM ikari_db_sage300.apibd t, ikari_db_sage300.apibh j
  where t.cntbtch=j.cntbtch
  and t.cntitem=j.cntitem) t1;



#insert AP Payment (Payment)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `adjustment_amount`, `discount_amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT t1.*FROM (SELECT DISTINCT
        0 is_credit_transaction
        ,1 is_debit_transaction
        ,abs(t.AMTPAYM) amount
        ,t.amtadjtot adjustment_amount
        ,t.amtdisctot discount_amount
        ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,t.CNTLINE number
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,aas.control_account_id account_id
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN
            (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `j`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,(SELECT `accounting_journal`.`id` FROM `accounting_journal`
	      LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	      WHERE `accounting_journal`.`document_number` = `j`.`DOCNBR`
 	      AND `accounting_journal`.`reference` = `j`.`TXTRMITREF`
	      AND `accounting_batch`.`batch_type` = 4 -- TRANSACTION_TYPES['AP Payment'] --
	      AND `accounting_journal`.`company_id` = @company_id) AS `journal_id`
        ,NULL tax_id
        ,0 base_tax_amount
        ,0 tax_amount
        ,abs(t.AMTPAYM) total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,tx.RATEEXCHTC exchange_rate
        ,abs(t.AMTPAYMHC) functional_amount
        ,(select id from currencies_currency where code='SGD') functional_currency_id
        ,date_format(tx.RATEDATETC ,'%Y-%m-%d') rate_date
        ,NULL reference
        ,NULL source_type
        ,(select id from accounting_journal
          where batch_id = (select id from accounting_batch
          where batch_type=2 -- TRANSACTION_TYPES['AP Invoice'] --
          and batch_no=inv.cntbtch
          and company_id=@company_id)
          and code=inv.cntitem) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'1' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
FROM ikari_db_sage300.aptcr j
RIGHT OUTER JOIN ikari_db_sage300.aptcp t on j.cntbtch=t.cntbtch
    AND j.cntentr=t.cntrmit
LEFT OUTER JOIN banks_bank bnk on j.idbank=bnk.code
    and bnk.company_id=@company_id
LEFT OUTER JOIN accounts_accountset aas on j.idacctset=aas.code
    and aas.company_id=@company_id
LEFT OUTER JOIN ikari_db_sage300.appjh tx on t.batchtype=tx.typebtch
    and t.cntbtch=tx.cntbtch
    and t.cntrmit=tx.cntitem
LEFT OUTER JOIN ikari_db_sage300.apibh inv on t.idinvc=inv.idinvc
    and t.cntbtch=tx.cntbtch
    and t.cntrmit=tx.cntitem) t1;



#insert AP payment (Misc. Payment)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT t1.* FROM (SELECT DISTINCT
        0 is_credit_transaction
        ,1 is_debit_transaction
        ,t.AMTNETTC amount
        ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,NULL number
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,aa.id account_id
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN
            (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `j`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,(SELECT `accounting_journal`.`id` FROM `accounting_journal`
	      LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	      WHERE `accounting_journal`.`document_number` = `j`.`DOCNBR`
 	      AND `accounting_journal`.`reference` = `j`.`TXTRMITREF`
	      AND `accounting_batch`.`batch_type` = 4 -- TRANSACTION_TYPES['AP Payment'] --
	      AND `accounting_journal`.`company_id` = @company_id) AS `journal_id`
        ,(SELECT id from taxes_tax
            where tax_group_id =
                (SELECT id FROM taxes_taxgroup WHERE
                    CODE =j.codetax1 and
                    transaction_type =2 and -- TAX_TRX_TYPES_DICT['Purchases'] --
                    company_id=@company_id)
            and number = t.taxclass1
            and company_id=@company_id) tax_id
        ,t.TXBSE1TC base_tax_amount
        ,t.TXTOTTC tax_amount
        ,t.AMTDISTTC total_amount
        ,ad.id distribution_code_id
        ,t.GLDESC description
        ,tx.RATEEXCHTC exchange_rate
        ,t.AMTDISTHC functional_amount
        ,(select id from currencies_currency where code='SGD') functional_currency_id
        ,date_format(tx.RATEDATETC,'%Y-%m-%d') rate_date
        ,t.GLREF reference
        ,NULL source_type
        ,NULL related_invoice_id
        ,t.SWTAXINCL1 is_tax_include
        ,0 is_tax_transaction
        ,'1' functional_balance_type
        ,0 is_report,0 is_clear_tax
FROM ikari_db_sage300.aptcr j
RIGHT OUTER JOIN ikari_db_sage300.aptcn t on j.cntbtch=t.cntbtch
    AND j.cntentr=t.cntrmit
LEFT OUTER JOIN ikari_db_sage300.appjh tx on t.batchtype=tx.typebtch
    and t.cntbtch=tx.cntbtch
    and t.cntrmit=tx.cntitem
LEFT OUTER JOIN accounts_distributioncode ad on t.IDDISTCODE=ad.code
    and ad.company_id=@company_id
LEFT OUTER JOIN accounts_account aa on t.idacct=aa.code
    and aa.company_id=@company_id) t1;


#insert GL Entry
INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`,
`orig_exch_rate_fk_id`, `is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`,
`perd_month`, `perd_year`, `error_entry`)
SELECT gl_crown.BTCHENTRY code
    ,gl_crown.JRNLDESC name
    ,5 journal_type -- TRANSACTION_TYPES)['GL'] --
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
    ,NULL po_number
    ,NULL order_number
    ,NULL document_number
    ,date_format(gl_crown.DATEENTRY,'%Y-%m-%d') document_date
    ,date_format(gl_crown.DATEENTRY,'%Y-%m-%d') posting_date
    ,gl_crown.JRNLCR amount
    ,0 tax_amount
    ,JRNLCR total_amount
    ,(select status
        from accounting_batch
        where batch_type=5 -- TRANSACTION_TYPES['GL'] --
            and batch_no=gl_crown.BATCHID
            and company_id=@company_id
     ) status
    ,date_format(gl_crown.DATEENTRY,'%Y-%m-%d') create_date
    ,date_format(gl_crown.DATEENTRY,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(select id from currencies_currency where code='SGD') currency_id
    ,NULL customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,NULL tax_id
    ,gl_crown.JRNLCR document_amount
    ,date_format(gl_crown.AUDTDATE,'%Y-%m-%d') due_date
    ,1 exchange_rate
    ,gl_crown.JRNLCR original_amount
    ,NULL original_currency_id
    ,NULL payment_account_id
    ,0 payment_amount
    ,0 payment_check_number
    ,null payment_code_id
    ,NULL payment_currency_id
    ,NULL reference
    ,CONCAT( gl_crown.SRCELEDGER,'-',gl_crown.SRCETYPE) source_type
    ,'0' transaction_type
    ,NULL bank_id
    ,NULL outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,NULL payment_number
    ,NULL invoice_number
    ,NULL is_manual_doc
    ,(select id from accounting_batch
     where batch_type=5 -- TRANSACTION_TYPES['GL'] --
     and batch_no=gl_crown.BATCHID
     and company_id=@company_id) batch_id
    ,NULL account_set_id
    ,NULL exchange_rate_fk_id
    ,gl_crown.SRCELEDGER source_ledger
    ,NULL orig_exch_rate
    ,NULL orig_exch_rate_fk_id
    ,IF(gl_crown.SWREVERSE>0,1,0) is_auto_reverse
    ,(CASE
      WHEN gl_crown.SWREVERSE=1 THEN '1'
      WHEN gl_crown.SWREVERSE=2 THEN '2'
      ELSE NULL
    END) reverse_to_period
    ,IF(gl_crown.SWREVERSE=2,gl_crown.REVPERD,NULL) reverse_to_period_val
    ,0 is_rev_do
    ,gl_crown.FSCSPERD perd_month
    ,gl_crown.FSCSYR perd_year
    ,gl_crown.ERRENTRY error_entry
FROM ikari_db_sage300.gljeh gl_crown
RIGHT OUTER JOIN  ikari_db_sage300.glbctl gl_entry  on gl_crown.BATCHID = gl_entry.BATCHID
WHERE gl_entry.BATCHTYPE IN (1, 3, 4)
AND gl_crown.SRCELEDGER IN ('GL')
AND gl_crown.SRCETYPE NOT IN ('JE', 'RV', 'RE');


INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
select t1.* from(select
      IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`
      ,IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_account`
      ,replace(t.SCURNAMT , '-', '') amount
      ,date_format(t.TRANSDATE,'%Y-%m-%d') transaction_date
      ,NULL remark
      ,t.TRANSNBR number
      ,0 is_close
      ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
      ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
      ,NULL update_by
      ,0 is_hidden
      ,(select aa.id from accounts_account aa
      where aa.code=t.ACCTID
      and aa.company_id=@company_id) account_id
      ,@company_id company_id
      ,NULL method_id
      ,NULL order_id
      ,(CASE WHEN t.SCURNCODE='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=t.SCURNCODE)
      END) currency_id
      ,NULL pair_id
      ,(select id from accounting_journal
        where batch_id=(select id from accounting_batch
                        where batch_no=t.BATCHNBR
                        and batch_type=5 -- TRANSACTION_TYPES['GL'] --
                        and company_id=@company_id)
        and code=t.JOURNALID) journal_id
      ,NULL tax_id
      ,0 base_tax_amount
      ,0 tax_amount
      ,replace(t.SCURNAMT , '-','') total_amount
      ,NULL distribution_code_id
      ,t.TRANSDESC description
      ,t.CONVRATE exchange_rate
      ,replace(t.TRANSAMT , '-','') functional_amount
      ,(select id from currencies_currency where code='SGD') functional_currency_id
      ,date_format(t.RATEDATE ,'%Y-%m-%d') rate_date
      ,t.TRANSREF reference
      ,concat(t.SRCELDGR,'-',t.SRCETYPE) source_type
      ,NULL related_invoice_id
      ,0 is_tax_include
      ,0 is_tax_transaction
      ,IF(t.TRANSAMT>=0,1,2) functional_balance_type
      ,0 is_report
      ,0 is_clear_tax
FROM  ikari_db_sage300.glbctl b
RIGHT OUTER JOIN  ikari_db_sage300.gljeh j ON b.BATCHID = j.BATCHID
LEFT OUTER JOIN ikari_db_sage300.gljed t ON j.BTCHENTRY = t.JOURNALID and j.BATCHID = t.BATCHNBR
where b.BATCHTYPE IN (1, 3, 4)
AND j.SRCETYPE NOT IN ('JE', 'RV', 'RE')
) t1;
# END INSERT GL ENTRY


#insert GL RV Journal
INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`,
`orig_exch_rate_fk_id`, `is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`,
`perd_month`, `perd_year`, `is_auto_reversed_entry`)
SELECT DISTINCT
	`j`.`ENTRYNBR` AS `code`,
    'Revaluation Entries' AS `name`,
    5 AS `journal_type`, -- TRANSACTION_TYPES)['GL'] --
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `po_number`,
    NULL AS `order_number`,
    NULL AS `document_number`,
    DATE_FORMAT(`j`.`JRNLDATE`,'%Y-%m-%d') AS `document_date`,
    DATE_FORMAT(`j`.`JRNLDATE`,'%Y-%m-%d') AS `posting_date`,
    `j`.`TRANSAMT` AS `amount`,
    0 AS `tax_amount`,
    `j`.`TRANSAMT` AS `total_amount`,
    (SELECT `status` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHNBR`
     AND `company_id` = @company_id) AS `status`,
    DATE_FORMAT(`j`.`JRNLDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`j`.`JRNLDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD') AS `currency_id`,
    NULL AS `customer_id`,
    NULL AS `order_id`,
    NULL AS `supplier_id`,
    NULL AS `tax_id`,
    `j`.`TRANSAMT` AS `document_amount`,
    DATE_FORMAT(`j`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
    1 AS `exchange_rate`,
    `j`.`TRANSAMT` AS `original_amount`,
    NULL AS `original_currency_id`,
    NULL AS `payment_account_id`,
    0 AS `payment_amount`,
    0 AS `payment_check_number`,
    null AS `payment_code_id`,
    NULL AS `payment_currency_id`,
    `j`.`JNLDTLREF` AS `reference`,
    CONCAT(`j`.`SRCELEDGER`, '-', `j`.`SRCETYPE`) AS `source_type`,
    '0' AS `transaction_type`,
    NULL AS `bank_id`,
    NULL AS `outstanding_amount`,
    0 AS `paid_amount`,
    0 AS `is_fully_paid`,
    NULL AS `payment_number`,
    NULL AS `invoice_number`,
    NULL AS `is_manual_doc`,
    (SELECT `id` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHNBR`
     AND `company_id` = @company_id) AS `batch_id`,
    NULL AS `account_set_id`,
    NULL AS `exchange_rate_fk_id`,
    `j`.`SRCELEDGER` AS `source_ledger`,
    NULL AS `orig_exch_rate`,
    NULL AS `orig_exch_rate_fk_id`,
    IF(`j`.`SWREVERSE` > 0, 1, 0) AS `is_auto_reverse`,
    (CASE
     WHEN `j`.`SWREVERSE` = 1 THEN '1'
     WHEN `j`.`SWREVERSE` = 2 THEN '2'
     ELSE NULL
     END) AS `reverse_to_period`,
     NULL AS `reverse_to_period_val`,
    0 AS `is_rev_do`,
    `j`.`FISCALPERD` AS `perd_month`,
    `j`.`FISCALYR` AS `perd_year`,
    0 AS `is_auto_reversed_entry`
FROM `ikari_db_sage300`.`glpjd` AS `j`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `j`.`BATCHNBR`
WHERE `j`.`SRCELEDGER` = 'GL'
AND `j`.`SRCETYPE` IN ('RV', 'RE')
AND `j`.`TRANSAMT` > 0
AND `b`.`BATCHTYPE` = 4
GROUP BY `j`.`BATCHNBR`, `j`.`ENTRYNBR`; 


UPDATE `accounting_journal` t2, `accounting_journal` t1 
SET t2.error_entry = t1.error_entry
WHERE `t1`.`company_id`=@company_id
    AND `t2`.`company_id`=@company_id
    AND `t1`.`id` < `t2`.`id`
    AND `t1`.`code` = `t2`.`code`
    AND `t1`.`journal_type` = 5
    AND `t2`.`journal_type` = 5
    AND `t1`.`batch_id` = `t2`.`batch_id`
    AND `t1`.`document_date` = `t2`.`document_date`
    AND `t1`.`currency_id` = `t2`.`currency_id`
    AND `t1`.`amount` = `t2`.`amount`
    AND `t1`.`tax_amount` = `t2`.`tax_amount`
    AND `t1`.`source_type` = `t2`.`source_type`;


DELETE t1 FROM `accounting_journal` t1
INNER JOIN `accounting_journal` t2
WHERE
    `t1`.`company_id`=@company_id
    AND `t2`.`company_id`=@company_id
    AND `t1`.`id` < `t2`.`id`
    AND `t1`.`code` = `t2`.`code`
    AND `t1`.`journal_type` = 5
    AND `t2`.`journal_type` = 5
    AND `t1`.`batch_id` = `t2`.`batch_id`
    AND `t1`.`document_date` = `t2`.`document_date`
    AND `t1`.`currency_id` = `t2`.`currency_id`
    AND `t1`.`amount` = `t2`.`amount`
    AND `t1`.`tax_amount` = `t2`.`tax_amount`
    AND `t1`.`source_type` = `t2`.`source_type`;


#insert GL Entry
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT
	IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
	IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_account`,
	ABS(`t`.`SCURNAMT`) AS `amount`,
	DATE_FORMAT(`t`.`TRANSDATE`,'%Y-%m-%d') AS `transaction_date`,
	NULL AS `remark`,
	`t`.`TRANSNBR` AS `number`,
	0 AS `is_close`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
	NULL AS `update_by`,
	0 AS `is_hidden`,
	(SELECT `id`
	 FROM `accounts_account`
	 WHERE `code` = `t`.`ACCTID`
	 AND `company_id` = @company_id) AS `account_id`,
	@company_id AS `company_id`,
	NULL AS `method_id`,
	NULL AS `order_id`,
	(CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
	NULL AS `pair_id`,
	(SELECT `accounting_journal`.`id`
	  FROM `accounting_journal`
	  LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	  WHERE `accounting_batch`.`batch_no` = `t`.`BATCHNBR`
      AND `accounting_journal`.`code` = `t`.`JOURNALID`
	  AND `accounting_journal`.`company_id` = @company_id
	  LIMIT 1
    ) AS `journal_id`,
	NULL AS `tax_id`,
  0 AS `base_tax_amount`,
	0 AS `tax_amount`,
	ABS(`t`.`SCURNAMT`) AS `total_amount`,
	NULL AS `distribution_code_id`,
	`t`.`TRANSDESC` AS `description`,
	`t`.`CONVRATE` AS `exchange_rate`,
	ABS(`t`.`TRANSAMT`) AS `functional_amount`,
	(SELECT `id`
	 FROM `currencies_currency`
	 WHERE `code` = 'SGD'
    ) AS `functional_currency_id`,
	DATE_FORMAT(`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
	`t`.`TRANSREF` AS `reference`,
	concat(t.SRCELDGR,'-',t.SRCETYPE) source_type,
	NULL AS `related_invoice_id`,
	0 AS `is_tax_include`,
	0 AS `is_tax_transaction`,
	IF(`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
	0 AS `is_report`,
	0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`gljed` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `j`.`BTCHENTRY` = `t`.`JOURNALID`
WHERE `j`.`SRCETYPE` IN ('JE', 'RV', 'RE');
/* WHERE `j`.`SRCETYPE` IN ('JE'); */


#insert GL RV Reverse Entry
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT DISTINCT
	IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
	IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_account`,
	ABS(`t`.`SCURNAMT`) AS `amount`,
	DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
	NULL AS `remark`,
	`t`.`TRANSNBR` AS `number`,
	0 AS `is_close`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
	NULL AS `update_by`,
	0 AS `is_hidden`,
	(SELECT `id`
	 FROM `accounts_account`
	 WHERE `code` = `t`.`ACCTID`
	 AND `company_id` = @company_id) AS `account_id`,
	@company_id AS `company_id`,
	NULL AS `method_id`,
	NULL AS `order_id`,
	(CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
	NULL AS `pair_id`,
	(SELECT `accounting_journal`.`id`
	  FROM `accounting_journal`
	  LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	  WHERE `accounting_batch`.`batch_no` = `t`.`BATCHNBR`
	  AND `accounting_journal`.`code` = `t`.`ENTRYNBR`
      AND `accounting_journal`.`company_id` = @company_id
	  LIMIT 1
    ) AS `journal_id`,
	NULL AS `tax_id`,
  0 AS `base_tax_amount`,
	0 AS `tax_amount`,
	ABS(`t`.`SCURNAMT`) AS `total_amount`,
	NULL AS `distribution_code_id`,
	`t`.`JNLDTLDESC` AS `description`,
	`t`.`CONVRATE` AS `exchange_rate`,
	ABS(`t`.`TRANSAMT`) AS `functional_amount`,
	(SELECT `id`
	 FROM `currencies_currency`
	 WHERE `code` = 'SGD'
    ) AS `functional_currency_id`,
	DATE_FORMAT(`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
	`t`.`JNLDTLREF` AS `reference`,
	CONCAT('GL', '-', `j`.`SRCETYPE`) AS `source_type`,
	NULL AS `related_invoice_id`,
	0 AS `is_tax_include`,
	0 AS `is_tax_transaction`,
	IF(`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
	0 AS `is_report`,
	0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR`
WHERE `j`.`SRCETYPE` IN ('RV', 'RE');


DELETE t1 FROM `transactions_transaction` t1
INNER JOIN `transactions_transaction` t2
WHERE
    `t1`.`company_id`=@company_id
    AND `t2`.`company_id`=@company_id
    AND `t1`.`id` > `t2`.`id`
    AND `t1`.`journal_id` = `t2`.`journal_id`
    AND `t1`.`is_credit_account` = `t2`.`is_credit_account`
    AND `t1`.`is_debit_account` = `t2`.`is_debit_account`
    AND `t1`.`transaction_date` = `t2`.`transaction_date`
    AND `t1`.`description` = `t2`.`description`
    AND CAST(`t1`.`number` AS UNSIGNED INTEGER) = CAST(`t2`.`number` AS UNSIGNED INTEGER)
    AND `t1`.`currency_id` = `t2`.`currency_id`
    AND `t1`.`functional_amount` = `t2`.`functional_amount`
    AND `t1`.`exchange_rate` = `t2`.`exchange_rate`
    -- AND `t1`.`source_type` = `t2`.`source_type`
    AND `t1`.`functional_balance_type` = `t2`.`functional_balance_type`
    AND `t1`.`account_id` = `t2`.`account_id`
    AND `t1`.`journal_id` IN (SELECT `id` FROM `accounting_journal` WHERE `journal_type`=5 AND `company_id`=@company_id);


#insert GL RV Journal
INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`,
`orig_exch_rate_fk_id`, `is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`,
`perd_month`, `perd_year`, `is_auto_reversed_entry`, `error_entry`)
SELECT DISTINCT
	`j`.`BTCHENTRY` AS `code`,
    `j`.`JRNLDESC` AS `name`,
    5 AS `journal_type`, -- TRANSACTION_TYPES)['GL'] --
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `po_number`,
    NULL AS `order_number`,
    NULL AS `document_number`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `document_date`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `posting_date`,
    `j`.`JRNLDR` AS `amount`,
    0 AS `tax_amount`,
    `j`.`JRNLDR` AS `total_amount`,
    (SELECT `status` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHID`
     AND `company_id` = @company_id) AS `status`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD') AS `currency_id`,
    NULL AS `customer_id`,
    NULL AS `order_id`,
    NULL AS `supplier_id`,
    NULL AS `tax_id`,
    `t`.`TRANSAMT` AS `document_amount`,
    DATE_FORMAT(`j`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
    1 AS `exchange_rate`,
    `t`.`TRANSAMT` AS `original_amount`,
    NULL AS `original_currency_id`,
    NULL AS `payment_account_id`,
    0 AS `payment_amount`,
    0 AS `payment_check_number`,
    null AS `payment_code_id`,
    NULL AS `payment_currency_id`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT(`j`.`SRCELEDGER`, '-', `j`.`SRCETYPE`) AS `source_type`,
    '0' AS `transaction_type`,
    NULL AS `bank_id`,
    NULL AS `outstanding_amount`,
    0 AS `paid_amount`,
    0 AS `is_fully_paid`,
    NULL AS `payment_number`,
    NULL AS `invoice_number`,
    NULL AS `is_manual_doc`,
    (SELECT `id` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHID`
     AND `company_id` = @company_id) AS `batch_id`,
    NULL AS `account_set_id`,
    NULL AS `exchange_rate_fk_id`,
    `j`.`SRCELEDGER` AS `source_ledger`,
    NULL AS `orig_exch_rate`,
    NULL AS `orig_exch_rate_fk_id`,
    IF(`j`.`SWREVERSE` > 0, 1, 0) AS `is_auto_reverse`,
    (CASE
     WHEN `j`.`SWREVERSE` = 1 THEN '1'
     WHEN `j`.`SWREVERSE` = 2 THEN '2'
     ELSE NULL
     END) AS `reverse_to_period`,
    IF(`j`.`SWREVERSE` = 2, `j`.`REVPERD`, NULL) AS `reverse_to_period_val`,
    0 AS `is_rev_do`,
    `j`.`FSCSPERD` AS `perd_month`,
    `j`.`FSCSYR` AS `perd_year`,
    0 AS `is_auto_reversed_entry`,
    `j`.`ERRENTRY` AS error_entry
FROM `ikari_db_sage300`.`gljeh` AS `j`
LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
AND `j`.`SRCETYPE` = 'GL'
AND `t`.`TRANSAMT` > 0
AND `t`.`JNLDTLREF` <> 'REVERSING ENTRY'
AND `b`.`BATCHTYPE` IN (2, 4)
GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`;


INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`,
`orig_exch_rate_fk_id`, `is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`,
`perd_month`, `perd_year`, `is_auto_reversed_entry`)
SELECT DISTINCT
	`t`.`ENTRYNBR` AS `code`,
    `t`.`JNLDTLDESC` AS `name`,
    5 AS `journal_type`, -- TRANSACTION_TYPES)['GL'] --
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `po_number`,
    NULL AS `order_number`,
    NULL AS `document_number`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `document_date`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `posting_date`,
    `t`.`TRANSAMT` AS `amount`,
    0 AS `tax_amount`,
    `t`.`TRANSAMT` AS `total_amount`,
    (SELECT `status` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `t`.`BATCHNBR`
     AND `company_id` = @company_id) AS `status`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD') AS `currency_id`,
    NULL AS `customer_id`,
    NULL AS `order_id`,
    NULL AS `supplier_id`,
    NULL AS `tax_id`,
    `t`.`TRANSAMT` AS `document_amount`,
    DATE_FORMAT(`t`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
    1 AS `exchange_rate`,
    `t`.`TRANSAMT` AS `original_amount`,
    NULL AS `original_currency_id`,
    NULL AS `payment_account_id`,
    0 AS `payment_amount`,
    0 AS `payment_check_number`,
    null AS `payment_code_id`,
    NULL AS `payment_currency_id`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT(`t`.`SRCELEDGER`, '-', `t`.`SRCETYPE`) AS `source_type`,
    '0' AS `transaction_type`,
    NULL AS `bank_id`,
    NULL AS `outstanding_amount`,
    0 AS `paid_amount`,
    0 AS `is_fully_paid`,
    NULL AS `payment_number`,
    NULL AS `invoice_number`,
    NULL AS `is_manual_doc`,
    (SELECT `id` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `t`.`BATCHNBR`
     AND `company_id` = @company_id) AS `batch_id`,
    NULL AS `account_set_id`,
    NULL AS `exchange_rate_fk_id`,
    `t`.`SRCELEDGER` AS `source_ledger`,
    NULL AS `orig_exch_rate`,
    NULL AS `orig_exch_rate_fk_id`,
    IF(`t`.`SWREVERSE` > 0, 1, 0) AS `is_auto_reverse`,
    (CASE
     WHEN `t`.`SWREVERSE` = 1 THEN '1'
     WHEN `t`.`SWREVERSE` = 2 THEN '2'
     ELSE NULL
     END) AS `reverse_to_period`,
    NULL AS `reverse_to_period_val`,
    0 AS `is_rev_do`,
    `t`.`FISCALPERD` AS `perd_month`,
    `t`.`FISCALYR` AS `perd_year`,
    0 AS `is_auto_reversed_entry`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
WHERE `t`.`SRCELEDGER` IN ('AR', 'AP')
AND `t`.`SRCETYPE` = 'GL'
AND `t`.`TRANSAMT` > 0
AND `t`.`JNLDTLREF` = 'REVERSING ENTRY'
AND `b`.`BATCHTYPE` IN (2, 4)
GROUP BY `t`.`BATCHNBR`, `t`.`ENTRYNBR`;


#insert GL CR/DB Journal
INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`,
`orig_exch_rate_fk_id`, `is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`,
`perd_month`, `perd_year`, `is_auto_reversed_entry`, `error_entry`)
SELECT DISTINCT
	`j`.`BTCHENTRY` AS `code`,
    `j`.`JRNLDESC` AS `name`,
    5 AS `journal_type`, -- TRANSACTION_TYPES)['GL'] --
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `po_number`,
    NULL AS `order_number`,
    NULL AS `document_number`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `document_date`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `posting_date`,
    `j`.`JRNLDR` AS `amount`,
    0 AS `tax_amount`,
    `j`.`JRNLDR` AS `total_amount`,
    (SELECT `status` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHID`
     AND `company_id` = @company_id) AS `status`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD') AS `currency_id`,
    NULL AS `customer_id`,
    NULL AS `order_id`,
    NULL AS `supplier_id`,
    NULL AS `tax_id`,
    `t`.`TRANSAMT` AS `document_amount`,
    DATE_FORMAT(`j`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
    1 AS `exchange_rate`,
    `t`.`TRANSAMT` AS `original_amount`,
    NULL AS `original_currency_id`,
    NULL AS `payment_account_id`,
    0 AS `payment_amount`,
    0 AS `payment_check_number`,
    null AS `payment_code_id`,
    NULL AS `payment_currency_id`,
    NULL AS `reference`,
    CONCAT(`j`.`SRCELEDGER`, '-', `j`.`SRCETYPE`) AS `source_type`,
    '0' AS `transaction_type`,
    NULL AS `bank_id`,
    NULL AS `outstanding_amount`,
    0 AS `paid_amount`,
    0 AS `is_fully_paid`,
    NULL AS `payment_number`,
    NULL AS `invoice_number`,
    NULL AS `is_manual_doc`,
    (SELECT `id` FROM `accounting_batch`
     WHERE `batch_type` = 5 -- TRANSACTION_TYPES['GL'] --
     AND `batch_no` = `j`.`BATCHID`
     AND `company_id` = @company_id) AS `batch_id`,
    NULL AS `account_set_id`,
    NULL AS `exchange_rate_fk_id`,
    `j`.`SRCELEDGER` AS `source_ledger`,
    NULL AS `orig_exch_rate`,
    NULL AS `orig_exch_rate_fk_id`,
    IF(`j`.`SWREVERSE` > 0, 1, 0) AS `is_auto_reverse`,
    (CASE
     WHEN `j`.`SWREVERSE` = 1 THEN '1'
     WHEN `j`.`SWREVERSE` = 2 THEN '2'
     ELSE NULL
     END) AS `reverse_to_period`,
    IF(`j`.`SWREVERSE` = 2, `j`.`REVPERD`, NULL) AS `reverse_to_period_val`,
    0 AS `is_rev_do`,
    `j`.`FSCSPERD` AS `perd_month`,
    `j`.`FSCSYR` AS `perd_year`,
    0 AS `is_auto_reversed_entry`,
    `j`.`ERRENTRY` AS error_entry
FROM `ikari_db_sage300`.`gljeh` AS `j`
LEFT JOIN `ikari_db_sage300`.`gljed` AS `t` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`JOURNALID` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
AND `j`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY', 'RD', 'AD')
AND `t`.`TRANSAMT` > 0
AND `b`.`BATCHTYPE` = 2
GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`;


#insert GL CR/DB Entry
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT
	IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
	IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_account`,
	ABS(`t`.`SCURNAMT`) AS `amount`,
	DATE_FORMAT(`t`.`TRANSDATE`,'%Y-%m-%d') AS `transaction_date`,
	NULL AS `remark`,
	`t`.`TRANSNBR` AS `number`,
	0 AS `is_close`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
	NULL AS `update_by`,
	0 AS `is_hidden`,
	(SELECT `id`
	 FROM `accounts_account`
	 WHERE `code` = `t`.`ACCTID`
	 AND `company_id` = @company_id) AS `account_id`,
	@company_id AS `company_id`,
	NULL AS `method_id`,
	NULL AS `order_id`,
	(CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
	NULL AS `pair_id`,
	(SELECT `accounting_journal`.`id`
	  FROM `accounting_journal`
	  LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	  WHERE `accounting_batch`.`batch_no` = `t`.`BATCHNBR`
	  AND `accounting_journal`.`code` = `t`.`JOURNALID`
      AND `accounting_journal`.`company_id` = @company_id
      ORDER BY `id` DESC
	  LIMIT 1
    ) AS `journal_id`,
	NULL AS `tax_id`,
	0 AS `base_tax_amount`,
	0 AS `tax_amount`,
	ABS(`t`.`SCURNAMT`) AS `total_amount`,
	NULL AS `distribution_code_id`,
	`t`.`TRANSDESC` AS `description`,
	`t`.`CONVRATE` AS `exchange_rate`,
	ABS(`t`.`TRANSAMT`) AS `functional_amount`,
	(SELECT `id`
	 FROM `currencies_currency`
	 WHERE `code` = 'SGD'
    ) AS `functional_currency_id`,
	DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
	`t`.`TRANSREF` AS `reference`,
	CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
	(SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`TRANSREF` AND
    `company_id` = @company_id AND
    `journal_type` = 1 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
	0 AS `is_tax_include`,
	0 AS `is_tax_transaction`,
	IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
	0 AS `is_report`,
	0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`gljed` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`JOURNALID` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
WHERE `t`.`SRCELDGR` = 'AR'
AND `t`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY', 'RD', 'AD')
AND `b`.`BATCHTYPE` = 2;

INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT
	IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
	IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_account`,
	ABS(`t`.`SCURNAMT`) AS `amount`,
	DATE_FORMAT(`t`.`TRANSDATE`,'%Y-%m-%d') AS `transaction_date`,
	NULL AS `remark`,
	`t`.`TRANSNBR` AS `number`,
	0 AS `is_close`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
	NULL AS `update_by`,
	0 AS `is_hidden`,
	(SELECT `id`
	 FROM `accounts_account`
	 WHERE `code` = `t`.`ACCTID`
	 AND `company_id` = @company_id) AS `account_id`,
	@company_id AS `company_id`,
	NULL AS `method_id`,
	NULL AS `order_id`,
	(CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
	NULL AS `pair_id`,
	(SELECT `accounting_journal`.`id`
	  FROM `accounting_journal`
	  LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	  WHERE `accounting_batch`.`batch_no` = `t`.`BATCHNBR`
	  AND `accounting_journal`.`code` = `t`.`JOURNALID`
      AND `accounting_journal`.`company_id` = @company_id
      ORDER BY `id` DESC
	  LIMIT 1
    ) AS `journal_id`,
	NULL AS `tax_id`,
	0 AS `base_tax_amount`,
	0 AS `tax_amount`,
	ABS(`t`.`SCURNAMT`) AS `total_amount`,
	NULL AS `distribution_code_id`,
	`t`.`TRANSDESC` AS `description`,
	`t`.`CONVRATE` AS `exchange_rate`,
	ABS(`t`.`TRANSAMT`) AS `functional_amount`,
	(SELECT `id`
	 FROM `currencies_currency`
	 WHERE `code` = 'SGD'
    ) AS `functional_currency_id`,
	DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
	`t`.`TRANSREF` AS `reference`,
	CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
	(SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`TRANSREF` AND
    `company_id` = @company_id AND
    `journal_type` = 2 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
	0 AS `is_tax_include`,
	0 AS `is_tax_transaction`,
	IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
	0 AS `is_report`,
	0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`gljed` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`JOURNALID` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
WHERE `t`.`SRCELDGR` = 'AP'
AND `t`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY', 'RD', 'AD')
AND `b`.`BATCHTYPE` = 2;


#insert GL RV Reverse Entry
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT
	IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
	IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_account`,
	ABS(`t`.`SCURNAMT`) AS `amount`,
	DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
	NULL AS `remark`,
	`t`.`TRANSNBR` AS `number`,
	0 AS `is_close`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
	NULL AS `update_by`,
	0 AS `is_hidden`,
	(SELECT `id`
	 FROM `accounts_account`
	 WHERE `code` = `t`.`ACCTID`
	 AND `company_id` = @company_id) AS `account_id`,
	@company_id AS `company_id`,
	NULL AS `method_id`,
	NULL AS `order_id`,
	(CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
	NULL AS `pair_id`,
	(SELECT `accounting_journal`.`id`
	  FROM `accounting_journal`
	  LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	  WHERE `accounting_batch`.`batch_no` = `t`.`BATCHNBR`
	  AND `accounting_journal`.`code` = `t`.`ENTRYNBR`
      AND `accounting_journal`.`company_id` = @company_id
      ORDER BY `id` DESC
	  LIMIT 1
    ) AS `journal_id`,
	NULL AS `tax_id`,
  0 AS `base_tax_amount`,
	0 AS `tax_amount`,
	ABS(`t`.`SCURNAMT`) AS `total_amount`,
	NULL AS `distribution_code_id`,
	`t`.`JNLDTLDESC` AS `description`,
	`t`.`CONVRATE` AS `exchange_rate`,
	ABS(`t`.`TRANSAMT`) AS `functional_amount`,
	(SELECT `id`
	 FROM `currencies_currency`
	 WHERE `code` = 'SGD'
    ) AS `functional_currency_id`,
	DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
	`t`.`JNLDTLREF` AS `reference`,
	'AR-GL' AS `source_type`,
	(SELECT `id`
    FROM `accounting_journal`
    WHERE `t`.`JNLDTLDESC` IS NOT NULL
    AND `t`.`JNLDTLREF` IS NOT NULL
    AND `name` = `t`.`JNLDTLDESC`
    AND `document_number` = `t`.`JNLDTLREF`
    AND `company_id` = @company_id
    AND `journal_type` = 1) AS `related_invoice_id`,
	0 AS `is_tax_include`,
	0 AS `is_tax_transaction`,
	IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
	0 AS `is_report`,
	0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
WHERE `t`.`SRCELEDGER` = 'AR'
AND `t`.`SRCETYPE` = 'GL'
AND `b`.`BATCHTYPE` = 2;


INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT
	IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
	IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_account`,
	ABS(`t`.`SCURNAMT`) AS `amount`,
	DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
	NULL AS `remark`,
	`t`.`TRANSNBR` AS `number`,
	0 AS `is_close`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
	DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
	NULL AS `update_by`,
	0 AS `is_hidden`,
	(SELECT `id`
	 FROM `accounts_account`
	 WHERE `code` = `t`.`ACCTID`
	 AND `company_id` = @company_id) AS `account_id`,
	@company_id AS `company_id`,
	NULL AS `method_id`,
	NULL AS `order_id`,
	(CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
	NULL AS `pair_id`,
	(SELECT `accounting_journal`.`id`
	  FROM `accounting_journal`
	  LEFT JOIN `accounting_batch` ON `accounting_journal`.`batch_id` = `accounting_batch`.`id`
	  WHERE `accounting_batch`.`batch_no` = `t`.`BATCHNBR`
	  AND `accounting_journal`.`code` = `t`.`ENTRYNBR`
      AND `accounting_journal`.`company_id` = @company_id
      ORDER BY `id` DESC
	  LIMIT 1
    ) AS `journal_id`,
	NULL AS `tax_id`,
  0 AS `base_tax_amount`,
	0 AS `tax_amount`,
	ABS(`t`.`SCURNAMT`) AS `total_amount`,
	NULL AS `distribution_code_id`,
	`t`.`JNLDTLDESC` AS `description`,
	`t`.`CONVRATE` AS `exchange_rate`,
	ABS(`t`.`TRANSAMT`) AS `functional_amount`,
	(SELECT `id`
	 FROM `currencies_currency`
	 WHERE `code` = 'SGD'
    ) AS `functional_currency_id`,
	DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
	`t`.`JNLDTLREF` AS `reference`,
	'AP-GL' AS `source_type`,
	(SELECT `id`
    FROM `accounting_journal`
    WHERE `t`.`JNLDTLDESC` IS NOT NULL
    AND `t`.`JNLDTLREF` IS NOT NULL
    AND `name` = `t`.`JNLDTLDESC`
    AND `document_number` = `t`.`JNLDTLREF`
    AND `company_id` = @company_id
    AND `journal_type` = 2) AS `related_invoice_id`,
	0 AS `is_tax_include`,
	0 AS `is_tax_transaction`,
	IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
	0 AS `is_report`,
	0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
WHERE `t`.`SRCELEDGER` = 'AP'
AND `t`.`SRCETYPE` = 'GL'
AND `b`.`BATCHTYPE` = 2;


-- insert journal AR-AD and AP-AD
INSERT INTO accounting_journal (
`code`, `name`, `journal_type`, `document_type`, `po_number`,
`order_number`, `document_number`, `document_date`, `posting_date`,
`amount`, `tax_amount`, `total_amount`, `status`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `currency_id`,
`customer_id`, `order_id`, `supplier_id`, `tax_id`, `document_amount`,
`due_date`, `exchange_rate`, `original_amount`, `original_currency_id`, `payment_account_id`,
`payment_amount`, `payment_check_number`, `payment_code_id`, `payment_currency_id`, `reference`,
`source_type`, `transaction_type`, `bank_id`, `outstanding_amount`, `paid_amount`,
`is_fully_paid`, `payment_number`, `invoice_number`, `is_manual_doc`, `batch_id`,
`account_set_id`, `exchange_rate_fk_id`, `source_ledger`, `orig_exch_rate`, `orig_exch_rate_fk_id`,
`is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`, `perd_month`, `perd_year`)
select t0.* from(select 
     j.CNTENTR code
    ,j.TEXTRMIT name
    ,11 journal_type -- TRANSACTION_TYPES)['AP Invoice'] --
    ,'10' document_type -- DOCUMENT_TYPE_DICT --
    ,NULL po_number
    ,NULL order_number
    ,jp.cntadj document_number
    ,date_format(j.DATERMIT,'%Y-%m-%d') document_date
    ,date_format(j.DATEBUS,'%Y-%m-%d') posting_date
    ,j.AMTADJTCUR amount
    ,j.TXTOTTC tax_amount
    ,j.AMTADJHCUR total_amount
    ,ab.status
    ,date_format(j.AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(j.AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN j.CODECURN='DOS' THEN 9
      ELSE
        (select id from currencies_currency where code=j.CODECURN)
      END) currency_id
    ,NULL customer_id
    ,NULL order_id
    ,s.id supplier_id
    ,(SELECT id from taxes_tax
      WHERE tax_group_id = tg.id
      and number = j.TAXCLASS1
      and company_id=@company_id) tax_id
    ,j.AMTADJTCUR document_amount
    ,NULL due_date
    ,j.RATEEXCHTC exchange_rate
    ,0 original_amount
    ,NULL original_currency_id
    ,NULL payment_account_id
    ,0 payment_amount
    ,NULL payment_check_number
    ,NULL payment_code_id
    ,NULL payment_currency_id
    ,j.TXTRMITREF reference
    ,NULL source_type
    ,'4' transaction_type
    ,NULL bank_id
    ,0 outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,0 payment_number
    ,NULL invoice_number
    ,1 is_manual_doc
    ,ab.id batch_id
    ,aas.id account_set_id
    ,NULL exchange_rate_fk_id
    ,NULL source_ledger
    ,j.RATEEXCHTC orig_exch_rate
    ,NULL orig_exch_rate_fk_id
    ,0 is_auto_reverse
    ,NULL reverse_to_period
    ,NULL reverse_to_period_val
    ,0 is_rev_do
    ,date_format(j.DATEBUS,'%m') perd_month
    ,date_format(j.DATEBUS,'%Y') perd_year
  FROM ikari_db_sage300.aptcr j
  LEFT JOIN ikari_db_sage300.aptcp jp
    ON j.btchtype = jp.batchtype AND j.CNTBTCH = jp.CNTBTCH AND j.cntentr = jp.cntrmit
  LEFT JOIN accounting_batch ab
    /* ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id AND ab.document_type='10' */
    ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id
  LEFT JOIN suppliers_supplier s
    ON j.IDVEND = s.code AND s.company_id = @company_id
  LEFT JOIN taxes_taxgroup tg
    ON j.CODETAXGRP = tg.code AND tg.transaction_type = 2 AND tg.company_id = @company_id
  LEFT JOIN accounts_accountset aas
    ON j.IDACCTSET = aas.code AND aas.company_id = @company_id AND aas.type=2
 WHERE j.btchtype = 'AD'
UNION ALL
SELECT j.CNTITEM code
        ,j.TEXTRMIT name
        ,11 journal_type -- TRANSACTION_TYPES)['AR Invoice'] --
        ,'10' document_type -- DOCUMENT_TYPE_DICT --
        ,NULL po_number
        ,NULL order_number
        ,jp.cntadj document_number
        ,date_format(j.DATERMIT,'%Y-%m-%d') document_date
        ,date_format(j.DATEBUS,'%Y-%m-%d') posting_date
        ,j.AMTADJHC amount
        ,j.TXTOTTC tax_amount
        ,j.AMTADJHC+j.TXTOTTC total_amount
        ,ab.status -- STATUS_TYPE_DICT --
        ,date_format(j.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(j.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,@company_id company_id
        ,(CASE WHEN j.CODECURN='DOS' THEN
            9
          ELSE
            (select id from currencies_currency where code=j.CODECURN)
          END) currency_id
        ,c.id customer_id
        ,NULL order_id
        ,NULL supplier_id
        ,(select id from taxes_tax
            WHERE tax_group_id = tg.id
            and number = j.TAXCLASS1
            and company_id=@company_id) tax_id
        ,j.AMTADJHC document_amount
        ,NULL due_date
        ,j.RATEEXCHTC exchange_rate
        ,0 original_amount
        ,NULL original_currency_id
        ,NULL payment_account_id
        ,0 payment_amount
        ,NULL payment_check_number
        ,NULL payment_code_id
        ,NULL payment_currency_id
        ,j.txtrmitref reference
        ,NULL source_type
        ,'3' transaction_type
        ,NULL bank_id
        ,REMUNAPLTC outstanding_amount
        ,0 paid_amount
        ,0 is_fully_paid
        ,0 payment_number
        ,NULL invoice_number
        ,1 is_manual_doc
        ,ab.id batch_id
        ,aas.id account_set_id
        ,NULL exchange_rate_fk_id
        ,NULL source_ledger
        ,j.RATEEXCHTC orig_exch_rate
        ,NULL orig_exch_rate_fk_id
        ,0 is_auto_reverse
        ,NULL reverse_to_period
        ,NULL reverse_to_period_val
        ,0 is_rev_do
        ,date_format(j.DATEBUS,'%m') perd_month
        ,date_format(j.DATEBUS,'%Y') perd_year
  FROM ikari_db_sage300.artcr j
  LEFT JOIN ikari_db_sage300.artcp jp
    ON j.CODEPYMTYP = jp.codepaym AND j.CNTBTCH = jp.CNTBTCH AND j.cntitem = jp.cntitem
  LEFT JOIN accounting_batch ab
    /* ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 1 AND ab.company_id = @company_id AND ab.document_type='10' */
    ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 1 AND ab.company_id = @company_id
  LEFT JOIN taxes_taxgroup tg
    ON j.CODETAXGRP = tg.code AND tg.transaction_type = 1 AND tg.company_id = @company_id
  LEFT JOIN accounts_accountset aas
    ON j.IDACCTSET = aas.code AND aas.company_id = @company_id AND aas.type=1
  LEFT JOIN customers_customer c
    ON j.IDCUST = c.code AND c.company_id = @company_id
 WHERE j.CODEPYMTYP = 'AD') t0;


-- trx AP-AD
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
select t0.* from(select 
         0 is_credit_transaction
        ,1 is_debit_transaction
        ,t.AMTADJTOT amount
        ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,t.CNTLINE number
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,IFNULL(aas.control_account_id,bnk.account_id) account_id -- get account from vendor or bank
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,kurs.id2 AS `currency_id`
        ,NULL pair_id
        ,aj.id AS `journal_id`
        ,NULL tax_id
        ,0 base_tax_amount
        ,0 tax_amount
        ,t.AMTADJTOT total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,j.RATEEXCHTC exchange_rate
        ,t.AMTADJHC functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
        ,date_format(j.DATERATETC ,'%Y-%m-%d') rate_date
        ,NULL reference
        ,'AP-AD' source_type
        ,(SELECT id FROM accounting_journal
           WHERE journal_type IN (2, 4)
            --  AND document_type IN ('1','2','3')
             AND document_number = t.idinvc
             AND company_id = @company_id LIMIT 1) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'1' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
 FROM ikari_db_sage300.aptcr j
RIGHT JOIN ikari_db_sage300.aptcp t
   ON j.btchtype = t.batchtype AND j.cntbtch = t.cntbtch AND j.cntentr = t.cntrmit
 LEFT JOIN accounting_batch ab
   ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id
 LEFT JOIN accounting_journal aj
   ON ab.id = aj.batch_id AND j.cntentr=aj.code AND aj.journal_type=11 AND aj.company_id=@company_id
 LEFT JOIN suppliers_supplier s
   ON j.IDVEND = s.code AND s.company_id = @company_id
 LEFT JOIN accounts_accountset aas
   ON s.account_set_id = aas.id AND aas.company_id = @company_id AND aas.type=2
 LEFT JOIN banks_bank bnk
   ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
 LEFT JOIN cur_kurs kurs
   ON j.CODECURN = kurs.code
WHERE t.batchtype = 'AD') t0;



-- trx AR-AD
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
select t0.* from(select  
        1 is_credit_transaction
        ,0 is_debit_transaction
        ,t.AMTADJTOT amount
        ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,t.CNTLINE number
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,aas.control_account_id account_id
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,kurs.id2 AS `currency_id`
        ,NULL pair_id
        ,aj.id journal_id
        ,NULL tax_id
        ,0 base_tax_amount
        ,0 tax_amount
        ,t.AMTADJTOT total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,tx.RATEEXCHTC exchange_rate
        ,t.AMTADJHC functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
        ,date_format(tx.RATEDATETC,'%Y-%m-%d') rate_date
        ,NULL reference
        ,'AR-AD' source_type
        ,(SELECT id FROM accounting_journal
           WHERE journal_type IN (1, 3)
          --  AND document_type IN ('1','2','3')
           AND document_number = t.idinvc
           AND customer_id = cus.id
           AND company_id=@company_id LIMIT 1) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'2' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
 FROM ikari_db_sage300.artcr j
RIGHT JOIN ikari_db_sage300.artcp t
   ON j.codepymtyp=t.codepaym AND j.cntbtch=t.cntbtch AND j.CNTITEM=t.CNTITEM -- add codepymtyp=codepaym to have this query use an index
 LEFT JOIN customers_customer cus
   ON j.IDCUST=cus.code and cus.company_id=@company_id
 LEFT JOIN accounts_accountset aas
   ON cus.account_set_id = aas.id AND aas.company_id=@company_id AND aas.type=1
 LEFT JOIN accounting_batch ab
   ON j.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id
 LEFT JOIN accounting_journal aj
   ON ab.id=aj.batch_id AND j.CNTITEM=aj.code AND aj.journal_type=11 AND aj.company_id=@company_id
 LEFT JOIN ikari_db_sage300.arpjh tx
   ON t.CODEPAYM=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.CNTITEM=tx.cntitem
 LEFT JOIN cur_kurs kurs
   ON j.CODECURN = kurs.code
WHERE t.codepaym = 'AD') t0;


INSERT INTO accounting_revaluationlogs (
  `company_id`, `journal_type`, `currency_id`, `revaluation_date`, `exchange_rate`, `rate_date`, `rate_type`,
  `posting_sequence`, `posting_date`, `revaluation_method`, `create_date`, `update_date`,
  `update_by`, `is_hidden`)

SELECT
      @company_id AS `company_id`,
      1 AS `journal_type`,
      (CASE WHEN `CURNCYCODE` = 'DOS' THEN
          (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
        ELSE
          (SELECT `id` FROM `currencies_currency` WHERE `code` = `CURNCYCODE`)
        END) AS `currency_id`,
      DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `revaluation_date`,
      CONVRATE AS `exchange_rate`,
      DATE_FORMAT(`CONVDATE`,'%Y-%m-%d') AS `rate_date`,
      CURTBLTYPE AS `rate_type`,
      POSTSEQNCE AS `posting_sequence`,
      DATE_FORMAT(`DATEPOSTED`,'%Y-%m-%d') AS `posting_date`,
      SWRVMETHOD AS `revaluation_method`,
      DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `create_date`,
      DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `update_date`,
      NULL AS `update_by`,
      0 AS `is_hidden`
FROM ikari_db_sage300.arrvllog
UNION
SELECT
      @company_id AS `company_id`,
      2 AS `journal_type`,
      (CASE WHEN `CURNCYCODE` = 'DOS' THEN
          (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
        ELSE
          (SELECT `id` FROM `currencies_currency` WHERE `code` = `CURNCYCODE`)
        END) AS `currency_id`,
      DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `revaluation_date`,
      CONVRATE AS `exchange_rate`,
      DATE_FORMAT(`CONVDATE`,'%Y-%m-%d') AS `rate_date`,
      CURTBLTYPE AS `rate_type`,
      POSTSEQNCE AS `posting_sequence`,
      DATE_FORMAT(`DATEPOSTED`,'%Y-%m-%d') AS `posting_date`,
      SWRVMETHOD AS `revaluation_method`,
      DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `create_date`,
      DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `update_date`,
      NULL AS `update_by`,
      0 AS `is_hidden`
FROM ikari_db_sage300.aprvllog;

-- AR Revaluation detail
INSERT INTO accounting_revaluationdetails (
  `posting_id`, `document_no`, `document_date`, `due_date`, `source_amount`, `prior_rate`, `rev_rate`, `prior_functional`, `new_functional`,
  `gain_loss`, `customer_id`, `supplier_id`, `create_date`, `update_date`, `update_by`, `is_hidden`)

SELECT
      (SELECT `id` FROM `accounting_revaluationlogs`
        WHERE `jh`.`POSTSEQNCE`=`posting_sequence`
        AND `company_id`=@company_id
        AND `journal_type`=1
        AND `jh`.`RATETYPETC`=`rate_type`
        AND `currency_id`=(SELECT `id` FROM `currencies_currency` WHERE `code`=`jh`.`CODECURNTC`)) AS `posting_id`,
      `jh`.`IDINVC` AS `document_no`,
      DATE_FORMAT(`jh`.`DATEINVC`,'%Y-%m-%d') AS `document_date`,
      DATE_FORMAT(`jh`.`DATEDUE`,'%Y-%m-%d') AS `due_date`,
      (SELECT `jd`.`AMTADJTCUR` FROM ikari_db_sage300.arpjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `source_amount`,
      (SELECT `jd`.`RATEDOC` FROM ikari_db_sage300.arpjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `prior_rate`,
      (SELECT `jd`.`RATEEXCHHC` FROM ikari_db_sage300.arpjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `rev_rate`,
      (SELECT `jd`.`AMTADJHCUR` FROM ikari_db_sage300.arpjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `prior_functional`,
      (SELECT (`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`) FROM ikari_db_sage300.arpjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `new_functional`,
      (SELECT ABS(`jd`.`AMTEXTNDHC`) FROM ikari_db_sage300.arpjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `gain_loss`,
      (SELECT `id` FROM customers_customer WHERE `code`=`jh`.`IDCUST` AND company_id=@company_id) AS `customer_id`,
      NULL AS `supplier_id`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `create_date`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `update_date`,
      NULL AS `update_by`,
      0 AS `is_hidden`
FROM ikari_db_sage300.arpjh AS `jh`
WHERE `jh`.`TYPEBTCH`='RV'
HAVING `posting_id` IS NOT NULL;

-- AP Revaluation detail
INSERT INTO accounting_revaluationdetails (
  `posting_id`, `document_no`, `document_date`, `due_date`, `source_amount`, `prior_rate`, `rev_rate`, `prior_functional`, `new_functional`,
  `gain_loss`, `customer_id`, `supplier_id`, `create_date`, `update_date`, `update_by`, `is_hidden`)

SELECT
      (SELECT `id` FROM `accounting_revaluationlogs`
        WHERE `jh`.`POSTSEQNCE`=`posting_sequence`
        AND `company_id`=@company_id
        AND `journal_type`=2
        AND `jh`.`RATETYPETC`=`rate_type`
        AND `currency_id`=(SELECT `id` FROM `currencies_currency` WHERE `code`=`jh`.`CODECURNTC`)) AS `posting_id`,
      `jh`.`IDINVC` AS `document_no`,
      DATE_FORMAT(`jh`.`DATEINVC`,'%Y-%m-%d') AS `document_date`,
      DATE_FORMAT(`jh`.`DATEDUE`,'%Y-%m-%d') AS `due_date`,
      (SELECT `jd`.`AMTADJTCUR` FROM ikari_db_sage300.appjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `source_amount`,
      (SELECT `jd`.`RATEDOC` FROM ikari_db_sage300.appjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `prior_rate`,
      (SELECT `jd`.`RATEEXCHHC` FROM ikari_db_sage300.appjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `rev_rate`,
      (SELECT `jd`.`AMTADJHCUR` FROM ikari_db_sage300.appjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `prior_functional`,
      (SELECT (`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`) FROM ikari_db_sage300.appjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `new_functional`,
      (SELECT ABS(`jd`.`AMTEXTNDHC`) FROM ikari_db_sage300.appjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `gain_loss`,
      NULL AS `customer_id`,
      (SELECT `id` FROM suppliers_supplier WHERE `code`=`jh`.`IDVEND` AND company_id=@company_id) AS `supplier_id`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `create_date`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `update_date`,
      NULL AS `update_by`,
      0 AS `is_hidden`
FROM ikari_db_sage300.appjh AS `jh`
WHERE `jh`.`TYPEBTCH`='RV'
HAVING `posting_id` IS NOT NULL;

-- Delete Transaction Entries whicg are not belongs to any Journal
DELETE FROM transactions_transaction WHERE journal_id IS NULL;
ALTER TABLE transactions_transaction AUTO_INCREMENT = 1;

delimiter $$
DROP PROCEDURE IF EXISTS fix_batch_no$$
create procedure fix_batch_no()
begin

UPDATE
   accounting_batch
SET
   batch_no = CASE
   WHEN LENGTH(batch_no) = 1 THEN CONCAT('00000', batch_no)
   WHEN LENGTH(batch_no) = 2 THEN CONCAT('0000', batch_no)
   WHEN LENGTH(batch_no) = 3 THEN CONCAT('000', batch_no)
   WHEN LENGTH(batch_no) = 4 THEN CONCAT('00', batch_no)
   WHEN LENGTH(batch_no) = 5 THEN CONCAT('0', batch_no)
   ELSE batch_no
--    Following line is for length 6 or more. because without leading zero batch no can not be sorted --
--    ELSE CONCAT('0', batch_no) --
   END;

end$$
delimiter ;

call fix_batch_no();


delimiter $$
DROP PROCEDURE IF EXISTS fix_exchange_rates$$
create procedure fix_exchange_rates()
begin

UPDATE
   transactions_transaction
SET
   exchange_rate = CASE
   WHEN exchange_rate = 0 THEN 1
   ELSE exchange_rate
   END;

end$$
delimiter ;

call fix_exchange_rates();


delimiter $$
DROP PROCEDURE IF EXISTS update_journal_reconciliation_status$$
CREATE procedure update_journal_reconciliation_status()
BEGIN

DECLARE doc varchar(30);
DECLARE stat int;
DECLARE source varchar(4);
DECLARE n INT DEFAULT 0;
DECLARE i INT DEFAULT 0;
DECLARE trx_cursor CURSOR FOR
  SELECT srceapp, status, srcedocnum FROM ikari_db_sage300.bktrand WHERE status=4;
SET i=0;
OPEN trx_cursor;
SELECT FOUND_ROWS() into n;
WHILE i<n DO 
  FETCH trx_cursor INTO source, stat, doc;

  IF stat=4 AND source='AP' THEN
    UPDATE
      accounting_journal
    SET
      reverse_reconciliation = 1
    WHERE
      company_id=@company_id AND
      journal_type=4 AND
      document_number=doc;
  END IF;

  IF stat=4 AND source='AR' THEN
    UPDATE
      accounting_journal
    SET
      reverse_reconciliation = 1
    WHERE
      company_id=@company_id AND
      journal_type=3 AND
      document_number=doc;
  END IF;
  
  SET i = i + 1;
END WHILE;

end$$
delimiter ;

call update_journal_reconciliation_status();
-- INSERT ACCOUNTING TRANSACTIONS DATA --
-- WARNING: You need to replace @company_id with the actual number in order to run this query!! --
SET @company_id = 1;

SELECT id 
  INTO @func_curr
  FROM currencies_currency
 WHERE code = 'SGD';

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
      (CASE WHEN `BATCHSTAT` = '4' THEN 2 WHEN `BATCHSTAT` = '3' THEN 3 ELSE 1 END) AS `status`,
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
    (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD') AS `currency_id`,
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
`is_auto_reverse`, `reverse_to_period`, `reverse_to_period_val`, `is_rev_do`, `perd_month`, `perd_year`)
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
    ,bl.SWPAID is_fully_paid
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
FROM ikari_db_sage300.apibh j -- AP Invoices --
JOIN ikari_db_sage300.apobl bl
on j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.txttrxtype
UNION
SELECT CNTENTR code
    ,TEXTRMIT name
    ,4 journal_type -- TRANSACTION_TYPES)['AP Payment'] --
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
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
    ,0 original_amount
    ,NULL original_currency_id
    ,NULL payment_account_id
    ,0 payment_amount
    ,IDRMIT payment_check_number
    ,(SELECT id FROM accounting_paymentcode where code=PAYMCODE) payment_code_id
    ,NULL payment_currency_id
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
FROM ikari_db_sage300.aribh j
JOIN ikari_db_sage300.arobl bl
on j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.trxtypetxt
UNION
SELECT CNTITEM code
    ,TEXTRMIT name
    ,3 journal_type -- TRANSACTION_TYPES['AR Receipt'] --
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
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
    ,0 original_amount
    ,NULL original_currency_id
    ,NULL payment_account_id
    ,0 payment_amount
    ,IDRMIT payment_check_number
    ,(SELECT id FROM accounting_paymentcode where code=CODEPAYM) payment_code_id
    ,NULL payment_currency_id
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
    'GL-JE' AS `source_type`,
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
    NULL AS `source_ledger`,
    NULL AS `orig_exch_rate`,
    NULL AS `orig_exch_rate_fk_id`,
    0 AS `is_auto_reverse`,
    NULL AS `reverse_to_period`,
    NULL AS `reverse_to_period_val`,
    0 AS `is_rev_do`,
    `j`.`FSCSPERD` AS `perd_month`,
    `j`.`FSCSYR` AS `perd_year`
FROM `ikari_db_sage300`.`gljeh` AS `j`
WHERE `SRCETYPE` = 'JE';


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


#insert transactions_transaction (AR Entry)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT (case when j.TEXTTRX=3 then 0 else 1 end) is_credit_account
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
      ,aa.id account_id
      ,@company_id company_id
      ,NULL method_id
      ,NULL order_id
      ,(CASE
          WHEN ac.CODECURN='DOS'
            THEN @func_curr
          ELSE
            (SELECT id from currencies_currency where code=ac.CODECURN)
       END)
      ,NULL pair_id
      ,(select id from accounting_journal
        where batch_id=ab.id
        and code=t.cntitem) journal_id
      ,(SELECT id from taxes_tax
        where tax_group_id=tg.id
        and number = t.TAXSTTS1
        and company_id=@company_id) tax_id
      ,t.BASETAX1 base_tax_amount
      ,t.TOTTAX tax_amount
      ,t.AMTEXTN total_amount
      ,ad.id distribution_code_id -- DIS_CODE_TYPE['AR Distribution Code'] --
      ,NULL description
      ,j.EXCHRATEHC exchange_rate
      ,t.AMTEXTNHC functional_amount
      ,@func_curr functional_currency_id
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
FROM ikari_db_sage300.aribd t
JOIN ikari_db_sage300.aribh j
  ON t.cntbtch=j.cntbtch
 AND t.cntitem=j.cntitem
LEFT JOIN (SELECT id,code FROM accounts_account 
            WHERE company_id=@company_id) aa
       ON REPLACE(t.IDACCTREV, '-', '') = aa.code
LEFT JOIN (SELECT id,batch_no FROM accounting_batch
            WHERE batch_type=1
              AND company_id=@company_id) ab 
       ON t.cntbtch=ab.batch_no
LEFT JOIN (SELECT id,code FROM taxes_taxgroup
            WHERE transaction_type=1
              AND company_id=@company_id) tg 
       ON j.CODETAX1=tg.code
LEFT JOIN (SELECT id,code FROM accounts_distributioncode 
            WHERE type=1
              AND company_id=@company_id) ad 
       ON t.IDDIST = ad.code
LEFT JOIN (SELECT IDCUST,CODECURN FROM ikari_db_sage300.arcus) ac
       ON j.IDCUST = ac.IDCUST;


#insert AP Payment (Payment)
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
        ,t.AMTPAYM amount
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
            @func_curr
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
        ,t.AMTPAYM total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,tx.RATEEXCHTC exchange_rate
        ,t.AMTPAYMHC functional_amount
        ,@func_curr functional_currency_id
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
LEFT OUTER JOIN accounts_accountset aas on j.idacctset=aas.code
    and aas.company_id=@company_id
LEFT OUTER JOIN ikari_db_sage300.appjh tx on t.batchtype=tx.typebtch
    and t.cntbtch=tx.cntbtch
    and t.cntrmit=tx.cntitem
LEFT OUTER JOIN ikari_db_sage300.apibh inv on t.idinvc=inv.idinvc) t1;


#insert AR receipt (receipt)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT t1.* FROM(SELECT
        1 is_credit_transaction
        ,0 is_debit_transaction
        ,t.AMTPAYM amount
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
            @func_curr
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
        ,t.AMTPAYM total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,tx.RATEEXCHTC exchange_rate
        ,t.AMTPAYMHC functional_amount
        ,@func_curr functional_currency_id
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
LEFT OUTER JOIN (select control_account_id,code from accounts_accountset where company_id=@company_id) aas on j.idacctset=aas.code
LEFT OUTER JOIN (select id,batch_no from accounting_batch where company_id=@company_id and batch_type=3) ab on j.cntbtch=ab.batch_no
LEFT OUTER JOIN (select cntbtch,cntitem,typebtch,RATEEXCHTC,RATEDATETC 
                from ikari_db_sage300.arpjh) tx 
     on t.CODEPAYM=tx.typebtch
    and t.cntbtch=tx.cntbtch
    and t.CNTITEM=tx.cntitem
LEFT OUTER JOIN (select cntbtch,cntitem,idinvc from ikari_db_sage300.aribh) inv 
     on t.idinvc=inv.idinvc
    and t.cntbtch=inv.cntbtch
    and t.CNTITEM=inv.cntitem) t1;


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
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN @func_curr
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
        ,@func_curr functional_currency_id
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
LEFT OUTER JOIN (select cntbtch,cntitem,typebtch,RATEDATETC,RATEEXCHTC 
                  from ikari_db_sage300.appjh) tx 
     on t.batchtype=tx.typebtch
    and t.cntbtch=tx.cntbtch
    and t.cntrmit=tx.cntitem
LEFT OUTER JOIN (select id,code from accounts_distributioncode where company_id=@company_id) ad on t.IDDISTCODE=ad.code
LEFT OUTER JOIN (select id,code from accounts_account where company_id=@company_id) aa on t.idacct=aa.code) t1;


#insert AR receipt (misc. receipt)
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT   1 is_credit_transaction
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
            @func_curr
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
        ,@func_curr functional_currency_id
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
LEFT OUTER JOIN (select id,batch_no from accounting_batch 
        where batch_type=3 and company_id=@company_id) ab on j.cntbtch=ab.batch_no
LEFT OUTER JOIN (select cntbtch,cntitem,typebtch,RATEDATETC,RATEEXCHTC 
                  from ikari_db_sage300.arpjh) tx
         on t.CODEPAYM=tx.typebtch
        and t.cntbtch=tx.cntbtch
        and t.CNTITEM=tx.cntitem
LEFT OUTER JOIN (select TAXCLASS1,CNTBTCH,CNTITEM,IDACCT from ikari_db_sage300.arrrd) tax
     on  t.cntbtch=tax.CNTBTCH
    and t.CNTITEM=tax.CNTITEM
    and t.IDACCT=tax.IDACCT
LEFT OUTER JOIN (select id,code from accounts_account where company_id=@company_id) aa on t.idacct=aa.code
LEFT OUTER JOIN (select id,code from accounts_distributioncode where company_id=@company_id) ad on t.IDDISTCODE=ad.code;

# INSERT GL ENTRY
/* INSERT INTO accounting_batch(
`batch_no`, `description`, `status`, `update_date`, `create_date`
, `update_by`, `is_hidden`, `batch_date`, `input_type`, `posting_sequence`
, `batch_amount`, `batch_type`, `company_id`, `no_entries`, `currency_id`
, `document_type`, `related_batch_id`, `source_ledger`)
SELECT BATCHID batch_no
    ,BTCHDESC description
    ,(CASE WHEN BATCHSTAT = '4' THEN 2 WHEN BATCHSTAT = '3' THEN 3 ELSE 1 END) status
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,null update_by
    ,0 is_hidden
    ,date_format(DATECREAT,'%Y-%m-%d') batch_date
    ,if(BATCHTYPE=1,'2','1') input_type -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    ,POSTNGSEQ posting_sequence
    ,DEBITTOT batch_amount
    ,5 batch_type -- TRANSACTION_TYPES['GL'] --
    ,@company_id company_id
    ,ENTRYCNT no_entries
    ,(select id from currencies_currency where code='SGD') currency_id
    ,0 document_type -- DOCUMENT_TYPE_DICT['Undefined'] --
    ,null related_batch_id
    ,SRCELEDGR source_ledger
FROM ikari_db_sage300.glbctl
LEFT JOIN (
    SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
    FROM `ikari_db_sage300`.`gljed` GROUP BY `ikari_db_sage300`.`gljed`.`BATCHNBR`
) AS `gljed` ON `gljed`.`BATCHNBR` = `ikari_db_sage300`.`glbctl`.`BATCHID`
WHERE BATCHTYPE IN (1, 3, 4)
AND `gljed`.`SRCETYPE` !='JE'; */
-- FROM ikari_db_sage300.glbctl WHERE BATCHTYPE =4 and BATCHID between '000001' and '000026'; --

INSERT INTO accounting_journal ( -- disini
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
`perd_month`, `perd_year`)
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
FROM ikari_db_sage300.gljeh gl_crown
RIGHT OUTER JOIN  ikari_db_sage300.glbctl gl_entry  on gl_crown.BATCHID = gl_entry.BATCHID
WHERE gl_entry.BATCHTYPE IN (1, 3, 4)
AND gl_crown.SRCETYPE NOT IN ('JE', 'RV', 'RE');

#insert GL Entry -- disini
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT
    IF(`t`.`SCURNAMT` < 0, 1, 0) AS `is_credit_account`,
    IF(`t`.`SCURNAMT` < 0, 0, 1) AS `is_debit_account`,
    ABS(`t`.`SCURNAMT`) AS `amount`,
    DATE_FORMAT(`t`.`TRANSDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`JOURNALID` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      where `accounting_journal`.batch_id = ab.id
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
    @func_curr AS `functional_currency_id`,
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
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `j`.`SRCETYPE` IN ('JE');


INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
select t1.* from(select
    (CASE WHEN t.SCURNAMT>=0 AND t.TRANSAMT>=0 THEN '0' ELSE '1' END) is_credit_account
    ,(CASE WHEN t.SCURNAMT>=0 AND t.TRANSAMT>=0 THEN '1' ELSE '0' END) is_debit_account
    ,replace(t.SCURNAMT , '-', '') amount
      ,date_format(t.TRANSDATE,'%Y-%m-%d') transaction_date
      ,NULL remark
      ,t.JOURNALID number
      ,0 is_close
      ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
      ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
      ,NULL update_by
      ,0 is_hidden
      ,aa.id account_id
      ,@company_id company_id
      ,NULL method_id
      ,NULL order_id
      ,(CASE WHEN t.SCURNCODE='DOS' THEN @func_curr
      ELSE
        (select id from currencies_currency where code=t.SCURNCODE)
      END) currency_id
      ,NULL pair_id
      ,(select id from accounting_journal
        where batch_id=ab.id
        and code=t.JOURNALID) journal_id
      ,NULL tax_id
      ,0 base_tax_amount
      ,0 tax_amount
      ,replace(t.SCURNAMT , '-','') total_amount
      ,NULL distribution_code_id
      ,t.TRANSDESC description
      ,t.CONVRATE exchange_rate
      ,replace(t.TRANSAMT , '-','') functional_amount
      ,@func_curr functional_currency_id
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
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
where b.BATCHTYPE IN (1, 3, 4)
AND j.SRCETYPE NOT IN ('JE', 'RV', 'RE')
) t1;
# END INSERT GL ENTRY


#insert GL RV Reverse Journal
/* INSERT INTO accounting_journal (
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
    `j`.`JRNLDESC` AS `name`,
    5 AS `journal_type`, -- TRANSACTION_TYPES)['GL'] --
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `po_number`,
    NULL AS `order_number`,
    NULL AS `document_number`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `document_date`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `posting_date`,
    `t`.`TRANSAMT` AS `amount`,
    0 AS `tax_amount`,
    `t`.`TRANSAMT` AS `total_amount`,
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
    1 AS `is_auto_reversed_entry`
FROM `ikari_db_sage300`.`gljeh` AS `j`
LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` != `j`.`BTCHENTRY`
WHERE `j`.`SRCETYPE` = 'RV' AND `t`.`JNLDTLREF` = 'REVERSING ENTRY' AND `t`.`TRANSAMT` > 0; */


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
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      WHERE `accounting_journal`.batch_id = ab.id 
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
    @func_curr AS `functional_currency_id`,
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
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `j`.`SRCETYPE` IN ('RV', 'RE');


# INSERT GL RV Batch
/* INSERT INTO accounting_batch(
`batch_no`, `description`, `status`, `update_date`, `create_date`
, `update_by`, `is_hidden`, `batch_date`, `input_type`, `posting_sequence`
, `batch_amount`, `batch_type`, `company_id`, `no_entries`, `currency_id`
, `document_type`, `related_batch_id`, `source_ledger`)
SELECT DISTINCT
    `b`.`BATCHID` AS `batch_no`,
    `b`.`BTCHDESC` AS `description`,
    (CASE WHEN `b`.`BATCHSTAT` = '4' THEN 2 WHEN `b`.`BATCHSTAT` = '3' THEN 3 ELSE 1 END) AS `status`,
    DATE_FORMAT(`b`.`AUDTDATE`, '%Y-%m-%d') AS `update_date`,
    DATE_FORMAT(`b`.`AUDTDATE`, '%Y-%m-%d') AS `create_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    DATE_FORMAT(`b`.`DATECREAT`, '%Y-%m-%d') AS `batch_date`,
    IF(`b`.`BATCHTYPE` = 1, '2', '1') AS `input_type`, -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    `b`.`POSTNGSEQ` AS `posting_sequence`,
    `b`.`DEBITTOT` AS `batch_amount`,
    5 AS `batch_type`, -- TRANSACTION_TYPES['GL'] --
    @company_id AS `company_id`,
    `b`.`ENTRYCNT` AS `no_entries`,
    (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD') AS `currency_id`,
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `related_batch_id`,
    `b`.`SRCELEDGR` AS `source_ledger`
FROM `ikari_db_sage300`.`glbctl` AS `b`
LEFT JOIN (
    SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
    FROM `ikari_db_sage300`.`gljed` AS `j` GROUP BY `j`.`BATCHNBR`
) AS `gljed` ON `gljed`.`BATCHNBR` = `b`.`BATCHID`
LEFT JOIN `ikari_db_sage300`.`gljeh` ON `gljeh`.`BATCHID` = `b`.`BATCHID`
WHERE `b`.`BATCHTYPE` = 2
AND `gljed`.`SRCETYPE` != 'JE'
AND `gljeh`.`SRCELEDGER` IN ('AP', 'AR')
AND `gljeh`.`SRCETYPE` = 'GL'; */


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
    ab.status,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    @func_curr AS `currency_id`,
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
    ab.id AS `batch_id`,
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
    0 AS `is_auto_reversed_entry`
FROM `ikari_db_sage300`.`gljeh` AS `j`
LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no,status from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on j.BATCHID=ab.batch_no
WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
AND `j`.`SRCETYPE` = 'GL'
AND `t`.`TRANSAMT` > 0
AND `t`.`JNLDTLREF` != 'REVERSING ENTRY'
AND `b`.`BATCHTYPE` = 2
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
    ab.status,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    @func_curr AS `currency_id`,
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
    ab.id AS `batch_id`,
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
LEFT JOIN (select id,batch_no,status from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
WHERE `t`.`SRCELEDGER` IN ('AR', 'AP')
AND `t`.`SRCETYPE` = 'GL'
AND `t`.`TRANSAMT` > 0
AND `t`.`JNLDTLREF` = 'REVERSING ENTRY'
AND `b`.`BATCHTYPE` = 2
GROUP BY `t`.`BATCHNBR`, `t`.`ENTRYNBR`;


# INSERT GL CR/DB
/* INSERT INTO accounting_batch(
`batch_no`, `description`, `status`, `update_date`, `create_date`
, `update_by`, `is_hidden`, `batch_date`, `input_type`, `posting_sequence`
, `batch_amount`, `batch_type`, `company_id`, `no_entries`, `currency_id`
, `document_type`, `related_batch_id`, `source_ledger`)
SELECT DISTINCT
    `b`.`BATCHID` AS `batch_no`,
    `b`.`BTCHDESC` AS `description`,
    (CASE WHEN `b`.`BATCHSTAT` = '4' THEN 2 WHEN `b`.`BATCHSTAT` = '3' THEN 3 ELSE 1 END) AS `status`,
    DATE_FORMAT(`b`.`AUDTDATE`, '%Y-%m-%d') AS `update_date`,
    DATE_FORMAT(`b`.`AUDTDATE`, '%Y-%m-%d') AS `create_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    DATE_FORMAT(`b`.`DATECREAT`, '%Y-%m-%d') AS `batch_date`,
    IF(`b`.`BATCHTYPE` = 1, '2', '1') AS `input_type`, -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
    `b`.`POSTNGSEQ` AS `posting_sequence`,
    `b`.`DEBITTOT` AS `batch_amount`,
    5 AS `batch_type`, -- TRANSACTION_TYPES['GL'] --
    @company_id AS `company_id`,
    `b`.`ENTRYCNT` AS `no_entries`,
    (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD') AS `currency_id`,
    0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
    NULL AS `related_batch_id`,
    `b`.`SRCELEDGR` AS `source_ledger`
FROM `ikari_db_sage300`.`glbctl` AS `b`
LEFT JOIN (
    SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
    FROM `ikari_db_sage300`.`gljed` AS `j` GROUP BY `j`.`BATCHNBR`
) AS `gljed` ON `gljed`.`BATCHNBR` = `b`.`BATCHID`
LEFT JOIN `ikari_db_sage300`.`gljeh` ON `gljeh`.`BATCHID` = `b`.`BATCHID`
WHERE `b`.`BATCHTYPE` = 2
AND `gljed`.`SRCETYPE` != 'JE'
AND `gljeh`.`SRCELEDGER` IN ('AP', 'AR')
AND `gljeh`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY'); */


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
`perd_month`, `perd_year`, `is_auto_reversed_entry`)
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
    ab.status,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    @func_curr AS `currency_id`,
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
    ab.id AS `batch_id`,
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
    0 AS `is_auto_reversed_entry`
FROM `ikari_db_sage300`.`gljeh` AS `j`
LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no,status from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on j.BATCHID=ab.batch_no
WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
AND `j`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY')
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
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      where `accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
    DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
    (SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`JNLDTLREF` AND
    `company_id` = @company_id AND
    `journal_type` = 1 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
    0 AS `is_tax_include`,
    0 AS `is_tax_transaction`,
    IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
    0 AS `is_report`,
    0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `t`.`SRCELEDGER` = 'AR'
AND `t`.`SRCETYPE` IN ('CR', 'DB')
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
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      where `accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
    DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
    (SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`JNLDTLREF` AND
    `company_id` = @company_id AND
    `journal_type` = 1 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
    0 AS `is_tax_include`,
    0 AS `is_tax_transaction`,
    IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
    0 AS `is_report`,
    0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `t`.`SRCELEDGER` = 'AR'
AND `t`.`SRCETYPE` = 'IN'
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
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      where `accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
    DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
    (SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`JNLDTLREF` AND
    `company_id` = @company_id AND
    `journal_type` = 1 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
    0 AS `is_tax_include`,
    0 AS `is_tax_transaction`,
    IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
    0 AS `is_report`,
    0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `t`.`SRCELEDGER` = 'AR'
AND `t`.`SRCETYPE` = 'PY'
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
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      WHERE`accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
    DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
    (SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`JNLDTLREF` AND
    `company_id` = @company_id AND
    `journal_type` = 2 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
    0 AS `is_tax_include`,
    0 AS `is_tax_transaction`,
    IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
    0 AS `is_report`,
    0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `t`.`SRCELEDGER` = 'AP'
AND `t`.`SRCETYPE` IN ('CR', 'DB')
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
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      WHERE`accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
    DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
    (SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`JNLDTLREF` AND
    `company_id` = @company_id AND
    `journal_type` = 2 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
    0 AS `is_tax_include`,
    0 AS `is_tax_transaction`,
    IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
    0 AS `is_report`,
    0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `t`.`SRCELEDGER` = 'AP'
AND `t`.`SRCETYPE` = 'IN'
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
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      WHERE`accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
    DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
    `t`.`JNLDTLREF` AS `reference`,
    CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
    (SELECT `id` FROM `accounting_journal`
    WHERE `document_number` = `t`.`JNLDTLREF` AND
    `company_id` = @company_id AND
    `journal_type` = 2 AND
    `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
    ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
    0 AS `is_tax_include`,
    0 AS `is_tax_transaction`,
    IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
    0 AS `is_report`,
    0 AS `is_clear_tax`
FROM `ikari_db_sage300`.`glpjd` AS `t`
LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `t`.`SRCELEDGER` = 'AP'
AND `t`.`SRCETYPE` = 'PY'
AND `b`.`BATCHTYPE` = 2;


#insert GL RV Reverse Entry -- TAI
INSERT INTO transactions_transaction (
`is_credit_account`, `is_debit_account`, `amount`, `transaction_date`, `remark`,
`number`, `is_close`, `create_date`, `update_date`, `update_by`,
`is_hidden`, `account_id`, `company_id`, `method_id`, `order_id`,
`currency_id`, `pair_id`, `journal_id`, `tax_id`, `base_tax_amount`, `tax_amount`,
`total_amount`, `distribution_code_id`, `description`, `exchange_rate`, `functional_amount`,
`functional_currency_id`, `rate_date`, `reference`, `source_type`, `related_invoice_id`,
`is_tax_include`, `is_tax_transaction`, `functional_balance_type`, `is_report`, `is_clear_tax`)
SELECT
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      WHERE `accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
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
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
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
    IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
    IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
    ABS(`t`.`TRANSAMT`) AS `amount`,
    DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
    NULL AS `remark`,
    `t`.`ENTRYNBR` AS `number`,
    0 AS `is_close`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    0 AS `is_hidden`,
    aa.id AS `account_id`,
    @company_id AS `company_id`,
    NULL AS `method_id`,
    NULL AS `order_id`,
    (CASE WHEN `t`.`SCURNCODE` = 'DOS' THEN
        @func_curr
      ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `t`.`SCURNCODE`)
      END) AS `currency_id`,
    NULL AS `pair_id`,
    (SELECT `accounting_journal`.`id`
      FROM `accounting_journal`
      WHERE `accounting_journal`.`batch_id` = ab.id
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
    @func_curr AS `functional_currency_id`,
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
LEFT JOIN (select id,batch_no from accounting_batch 
        where batch_type=5 and company_id=@company_id) ab on t.BATCHNBR=ab.batch_no
LEFT JOIN (SELECT id,code from accounts_account where company_id=@company_id) aa ON t.ACCTID = aa.code
WHERE `t`.`SRCELEDGER` = 'AP'
AND `t`.`SRCETYPE` = 'GL'
AND `b`.`BATCHTYPE` = 2;


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
        AND `company_id`=@company_id
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
      (SELECT (`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`) - (`jd`.`AMTADJHCUR`) FROM ikari_db_sage300.arpjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `gain_loss`,
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
        AND `company_id`=@company_id
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
      (SELECT (`jd`.`AMTADJHCUR`) - (`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`) FROM ikari_db_sage300.appjd AS `jd` WHERE `jd`.`TYPEBTCH`='RV' AND `jd`.`POSTSEQNCE`=`jh`.`POSTSEQNCE` AND `jd`.`IDINVC`=`jh`.`IDINVC` ORDER BY `jd`.`IDINVC` LIMIT 1) AS `gain_loss`,
      NULL AS `customer_id`,
      (SELECT `id` FROM suppliers_supplier WHERE `code`=`jh`.`IDVEND` AND company_id=@company_id) AS `supplier_id`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `create_date`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `update_date`,
      NULL AS `update_by`,
      0 AS `is_hidden`
FROM ikari_db_sage300.appjh AS `jh`
WHERE `jh`.`TYPEBTCH`='RV'
HAVING `posting_id` IS NOT NULL;


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

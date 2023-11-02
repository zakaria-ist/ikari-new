-- INSERT ACCOUNTING TRANSACTIONS DATA --
-- WARNING: You need to replace @company_id with the actual number in order to run this query!! --
SET @company_id = 42;

SELECT id 
  INTO @func_curr
  FROM currencies_currency
 WHERE code = 'SGD';


-- insert accounting_batch --
SELECT max(id) into @row_number FROM accounting_batch;
SELECT (@row_number:=@row_number + 1) AS id, t0.*, 0 flag
INTO OUTFILE 'C:/ikari_migration_files/batch_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
FROM `ikari_db_sage300`.`glbctl`) t0;-- AR Receipt and Adjustment Batches --
/* LEFT JOIN (
    SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
    FROM `ikari_db_sage300`.`gljed` GROUP BY `ikari_db_sage300`.`gljed`.`BATCHNBR`
) AS `gljed` ON `gljed`.`BATCHNBR` = `ikari_db_sage300`.`glbctl`.`BATCHID`
WHERE `gljed`.`SRCETYPE` = 'JE'; -- Code Payment Type -- */

LOAD DATA INFILE 'c:/ikari_migration_files/batch_1.txt' IGNORE INTO TABLE accounting_batch
   FIELDS TERMINATED BY ',' ENCLOSED BY '"'
   LINES TERMINATED BY '\n';

COMMIT;



#Insert accounting_journal
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
    ,ab.status
    ,date_format(j.AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(j.AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN j.CODECURN='DOS' THEN @func_curr
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
    ,'2' transaction_type
    ,NULL bank_id
    ,j.AMTGROSTOT outstanding_amount
    ,0 paid_amount
    ,bl.SWPAID is_fully_paid
    ,0 payment_number
    ,NULL invoice_number
    ,1 is_manual_doc
    ,ab.id batch_id
    ,aas.id account_set_id
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
  ON j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.txttrxtype
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN suppliers_supplier s
  ON j.IDVEND = s.code aND s.company_id = @company_id
LEFT JOIN taxes_taxgroup tg
  ON j.CODETAXGRP = tg.code AND transaction_type = 2 AND tg.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id
UNION
SELECT CNTENTR code
    ,TEXTRMIT name
    ,4 journal_type -- TRANSACTION_TYPES)['AP Payment'] --
    ,(CASE 
        WHEN (j.RMITTYPE = 1 OR j.RMITTYPE = 4) -- no constant document_type available for rmittype = 4 = Misc. Payment.
            THEN '9'                            -- (Considered as Payment on assupmtion)
        WHEN j.RMITTYPE = 2 THEN '6'
        WHEN j.RMITTYPE = 3 THEN '0' -- no constant document_type available for rmittype = 3 = apply document
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
    ,ab.status -- STATUS_TYPE_DICT --
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
        @func_curr
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) currency_id
    ,NULL customer_id
    ,NULL order_id
    ,s.id supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id = tg.id
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
    ,pc.id payment_code_id
    ,NULL payment_currency_id
    ,TXTRMITREF reference
    ,NULL source_type
    ,'4' transaction_type
    ,bnk.id bank_id
    ,0 outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,CNTPAYMENT payment_number
    ,if(RMITTYPE=1,NULL,IDINVCMTCH) invoice_number
    ,1 is_manual_doc
    ,ab.id batch_id
    ,aas.id account_set_id
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
FROM ikari_db_sage300.aptcr j
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 4 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN suppliers_supplier s
  ON j.IDVEND = s.code AND s.company_id = @company_id
LEFT JOIN taxes_taxgroup tg
  ON j.CODETAXGRP = tg.code AND tg.transaction_type = 2 AND tg.company_id = @company_id
LEFT JOIN banks_bank bnk
  ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id
LEFT JOIN accounting_paymentcode pc
  ON j.PAYMCODE = pc.code
WHERE j.btchtype = 'PY'
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
    ,ab.status -- STATUS_TYPE_DICT --
    ,date_format(j.AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(j.AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN j.CODECURN='DOS' THEN
        @func_curr
      ELSE
        (select id from currencies_currency where code=j.CODECURN)
      END) currency_id
    ,c.id customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id = tg.id
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
    ,'1' transaction_type
    ,NULL bank_id
    ,j.AMTNETTOT outstanding_amount
    ,0 paid_amount
    ,bl.swpaid is_fully_paid
    ,0 payment_number
    ,NULL invoice_number
    ,1 is_manual_doc
    ,ab.id batch_id
    ,aas.id account_set_id
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
  ON j.cntbtch = bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.trxtypetxt
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 1 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN taxes_taxgroup tg
  ON j.CODETAXGRP = tg.code AND tg.transaction_type = 1 AND tg.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id
LEFT JOIN customers_customer c
  ON j.IDCUST = c.code AND c.company_id = @company_id
UNION
SELECT CNTITEM code
    ,TEXTRMIT name
    ,3 journal_type -- TRANSACTION_TYPES['AR Receipt'] --
    ,(CASE 
        WHEN (j.RMITTYPE = 1 OR j.RMITTYPE = 5) -- no constant document_type available for rmittype 5 = Misc. Receipt
            THEN '7'                            -- (considered as Receipt on assumption)
        WHEN j.RMITTYPE = 2 THEN '6'
        WHEN j.RMITTYPE = 3 THEN '5'
        WHEN (j.RMITTYPE = 4 OR j.RMITTYPE = 6)
            THEN '0' -- no constant document_type available for rmittype = 4,6 = apply document, Write-Off
        ELSE '10'
      END) document_type -- DOCUMENT_TYPE_DICT
    ,NULL po_number
    ,NULL order_number
    ,DOCNBR document_number
    ,date_format(DATERMIT,'%Y-%m-%d') document_date
    ,date_format(DATEBUS,'%Y-%m-%d') posting_date
    ,if(CODETAXGRP IS NULL or CODETAXGRP = '',AMTRMITTC,TXBSE1TC) amount
    ,TXTOTTC tax_amount
    ,AMTRMITTC total_amount
    ,ab.status -- STATUS_TYPE_DICT --
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
        @func_curr
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) currency_id
    ,c.id customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id = tg.id
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
    ,pc.id payment_code_id
    ,NULL payment_currency_id
    ,TXTRMITREF reference
    ,NULL source_type
    ,'3' transaction_type
    ,bnk.id bank_id
    ,REMUNAPLTC outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,NULL payment_number
    ,if(RMITTYPE=1,NULL,IDINVCMTCH) invoice_number
    ,1 is_manual_doc
    ,ab.id batch_id
    ,aas.id account_set_id
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
FROM ikari_db_sage300.artcr j
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 3 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN taxes_taxgroup tg
  ON j.CODETAXGRP = tg.code AND tg.transaction_type = 1 AND tg.company_id = @company_id
LEFT JOIN banks_bank bnk
  ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id
LEFT JOIN customers_customer c
  ON j.IDCUST = c.code AND c.company_id = @company_id
LEFT JOIN accounting_paymentcode pc
  ON j.CODEPAYM = pc.code
WHERE j.CODEPYMTYP='CA' -- Payment Type --
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
    1 AS `status`, -- STATUS_TYPE_DICT --
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
    NULL AS `source_type`,
    '0' AS `transaction_type`,
    NULL AS `bank_id`,
    `j`.`JRNLDR` AS `outstanding_amount`,
    0 AS `paid_amount`,
    0 AS `is_fully_paid`,
    0 AS `payment_number`,
    NULL AS `invoice_number`,
    0 AS `is_manual_doc`,
    ab.id AS `batch_id`,
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
LEFT JOIN accounting_batch ab
  ON j.BATCHID = ab.batch_no AND ab.batch_type = 5 AND ab.company_id = @company_id AND ab.document_type <> '10'
WHERE `SRCETYPE` = 'JE') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_1.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert transactions_transaction (AP ENTRY)  -- 53696
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT (case when j.TEXTTRX=3 then 1 else 0 end) is_credit_account
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
      ,aa.id account_id
      ,@company_id company_id
      ,NULL method_id
      ,NULL order_id
      ,(CASE
          WHEN (select CURNCODE from ikari_db_sage300.apven where VENDORID = j.idvend)='DOS'
            THEN @func_curr
          ELSE
            (SELECT id from currencies_currency
            where code=(select CURNCODE from ikari_db_sage300.apven where VENDORID = j.idvend))
      END) currency_id
      ,NULL pair_id
      ,aj.id journal_id
      ,(SELECT id from taxes_tax
        where tax_group_id = tg.id
        and number = t.TAXCLASS1
        and company_id=@company_id) tax_id
      ,t.AMTTOTTAX tax_amount
      ,t.AMTDIST total_amount
      ,ad.id distribution_code_id -- DIS_CODE_TYPE['AP Distribution Code'] --
      ,NULL description
      ,j.EXCHRATEHC exchange_rate
      ,t.AMTDISTHC functional_amount
      ,@func_curr functional_currency_id
      ,date_format(j.DATERATE ,'%Y-%m-%d') rate_date
      ,NULL reference
      ,NULL source_type
      ,(SELECT j0.id FROM accounting_journal j0, accounting_batch b0
        WHERE j0.batch_id = b0.id
        AND j0.document_number = j.INVCAPPLTO
        AND j0.journal_type=2 -- TRANSACTION_TYPES)['AP Invoice'] --
        AND j0.company_id=@company_id
        AND j0.company_id = b0.company_id
        AND b0.batch_no <= t.cntbtch
        ORDER BY b0.batch_no desc LIMIT 1) related_invoice_id
      ,t.SWTAXINCL1 is_tax_include
      ,0 is_tax_transaction
      ,if(j.TEXTTRX=3,'2','1')
      ,0 is_report,0 is_clear_tax
      ,0 adjamt, 0 discamt
      ,t.BASETAX1 base_tax_amount
  FROM ikari_db_sage300.apibd t
  JOIN ikari_db_sage300.apibh j
    ON t.cntbtch=j.cntbtch AND t.cntitem=j.cntitem
  LEFT JOIN accounts_account aa 
    ON REPLACE(t.IDGLACCT,'-','') = aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab 
    ON t.cntbtch=ab.batch_no AND ab.company_id=@company_id AND ab.batch_type=2
  LEFT JOIN accounting_journal aj
    ON ab.id = aj.batch_id AND t.cntitem=aj.code AND aj.company_id=@company_id
  LEFT JOIN taxes_taxgroup tg
    ON j.CODETAX1=tg.code AND tg.transaction_type=2 AND tg.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDIST = ad.code AND ad.type=2 AND ad.company_id=@company_id) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_1.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert transactions_transaction (AR Entry) -- part1
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_2_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT 1 is_credit_account
      ,0 is_debit_account
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
      ,aj.id journal_id
      ,tx.id tax_id
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
      ,NULL related_invoice_id
      ,t.SWTAXINCL1 is_tax_include
      ,0 is_tax_transaction
      ,'2'
      ,0 is_report,0 is_clear_tax
      ,0 adjamt, 0 discamt
      ,t.BASETAX1 base_tax_amount
  FROM ikari_db_sage300.aribd t
  JOIN ikari_db_sage300.aribh j
    ON t.cntbtch=j.cntbtch AND t.cntitem=j.cntitem
  LEFT JOIN accounts_account aa
    ON REPLACE(t.IDACCTREV, '-', '') = aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab 
    ON t.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id = aj.batch_id AND t.cntitem=aj.code AND aj.company_id=@company_id
  LEFT JOIN taxes_taxgroup tg
    ON j.CODETAX1=tg.code AND tg.transaction_type=1 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax tx
    ON tg.id = tx.tax_group_id AND t.TAXSTTS1=tx.number AND tx.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDIST = ad.code AND ad.type=1 AND ad.company_id=@company_id
  LEFT JOIN ikari_db_sage300.arcus ac
    ON j.IDCUST = ac.IDCUST
 WHERE j.TEXTTRX = 1
UNION ALL
SELECT 1 is_credit_account
      ,0 is_debit_account
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
      ,aj.id journal_id
      ,tx.id tax_id
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
        AND b0.batch_no <= t.cntbtch
        AND j0.customer_id = cus.id
        ORDER BY b0.batch_no desc LIMIT 1) related_invoice_id
      ,t.SWTAXINCL1 is_tax_include
      ,0 is_tax_transaction
      ,'2'
      ,0 is_report,0 is_clear_tax
      ,0 adjamt, 0 discamt
      ,t.BASETAX1 base_tax_amount
  FROM ikari_db_sage300.aribd t
  JOIN ikari_db_sage300.aribh j
    ON t.cntbtch=j.cntbtch AND t.cntitem=j.cntitem
  LEFT JOIN customers_customer cus
    ON j.IDCUST=cus.code and cus.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON REPLACE(t.IDACCTREV, '-', '') = aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab 
    ON t.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id and ab.document_type <> '10'
  LEFT JOIN accounting_journal aj
    ON ab.id = aj.batch_id AND t.cntitem=aj.code AND aj.company_id=@company_id
  LEFT JOIN taxes_taxgroup tg
    ON j.CODETAX1=tg.code AND tg.transaction_type=1 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax tx
    ON tg.id = tx.tax_group_id AND t.TAXSTTS1=tx.number AND tx.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDIST = ad.code AND ad.type=1 AND ad.company_id=@company_id
  LEFT JOIN ikari_db_sage300.arcus ac
    ON j.IDCUST = ac.IDCUST
 WHERE j.TEXTTRX = 2
 ) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_2_1.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert transactions_transaction (AR Entry) -- part2
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_2_2.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT 1 is_credit_account
      ,0 is_debit_account
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
      ,aj.id journal_id
      ,tx.id tax_id
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
      ,(CASE
            WHEN j.INVCAPPLTO = '' OR j.INVCAPPLTO IS NULL THEN
                IFNULL(
                    (SELECT j1.id
                       FROM accounting_journal j1
                      WHERE j1.journal_type = 1
                         AND j1.document_type = '1'
                         AND j1.customer_id = cus.id
                         AND j1.company_id=42
                         AND j1.is_fully_paid=0
                         AND j1.name = j.INVCDESC
                         AND j1.total_amount = j.AMTNETTOT),
                    (SELECT j2.id
                      FROM accounting_journal j2
                     WHERE j2.journal_type = 1
                        AND j2.document_type = '1'
                        AND j2.customer_id = cus.id
                        AND j2.company_id=42
                        AND j2.is_fully_paid=0
                        AND j2.total_amount = j.AMTNETTOT))
            ELSE 
                (SELECT id FROM accounting_journal
                  WHERE journal_type = 1
                    AND document_type = '1'
                    AND document_number = j.INVCAPPLTO
                    AND company_id=42
                    AND customer_id = cus.id)
        END) related_invoice_id
      ,t.SWTAXINCL1 is_tax_include
      ,0 is_tax_transaction
      ,'2'
      ,0 is_report,0 is_clear_tax
      ,0 adjamt, 0 discamt
      ,t.BASETAX1 base_tax_amount
  FROM ikari_db_sage300.aribd t
  JOIN ikari_db_sage300.aribh j
    ON t.cntbtch=j.cntbtch AND t.cntitem=j.cntitem
  LEFT JOIN customers_customer cus
    ON j.IDCUST=cus.code and cus.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON REPLACE(t.IDACCTREV, '-', '') = aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab 
    ON t.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id = aj.batch_id AND t.cntitem=aj.code AND aj.company_id=@company_id
  LEFT JOIN taxes_taxgroup tg
    ON j.CODETAX1=tg.code AND tg.transaction_type=1 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax tx
    ON tg.id = tx.tax_group_id AND t.TAXSTTS1=tx.number AND tx.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDIST = ad.code AND ad.type=1 AND ad.company_id=@company_id
  LEFT JOIN ikari_db_sage300.arcus ac
    ON j.IDCUST = ac.IDCUST
 WHERE j.TEXTTRX = 3
 ) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_2_2.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert AP Payment (Payment)
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_3.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT DISTINCT
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
        ,IFNULL(aas.control_account_id,bnk.account_id) account_id -- get account from vendor or bank
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN
            @func_curr
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `j`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,aj.id AS `journal_id`
        ,NULL tax_id
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
        ,(SELECT id FROM accounting_journal
           WHERE journal_type = 2
           AND document_type = '1'  -- hati-hati ini
           AND document_number = t.idinvc
           AND supplier_id = s.id
           AND company_id=@company_id) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'1' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
 FROM ikari_db_sage300.aptcr j
RIGHT JOIN ikari_db_sage300.aptcp t
   ON j.btchtype=t.batchtype AND j.cntbtch=t.cntbtch AND j.cntentr=t.cntrmit
 LEFT JOIN ikari_db_sage300.appjh tx
   ON t.batchtype=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.cntrmit=tx.cntitem
 LEFT JOIN accounting_batch ab
   ON t.cntbtch=ab.batch_no AND ab.batch_type=4 AND ab.company_id=@company_id
 LEFT JOIN accounting_journal aj
   ON ab.id = aj.batch_id AND j.DOCNBR=aj.document_number AND j.TXTRMITREF = aj.reference AND aj.company_id=@company_id
 LEFT JOIN suppliers_supplier s 
   ON j.IDVEND = s.code AND s.company_id = @company_id
 LEFT JOIN accounts_accountset aas
   ON s.account_set_id = aas.id AND aas.company_id = @company_id
 LEFT JOIN banks_bank bnk
   ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
WHERE t.batchtype = 'PY') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_3.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;



#insert AR receipt (receipt)
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_4.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT   1 is_credit_transaction
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
        ,aj.id journal_id
        ,NULL tax_id
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
        ,(SELECT id FROM accounting_journal
           WHERE journal_type = 1
           AND document_type IN ('1','2','3')
           AND document_number = t.idinvc
           AND customer_id = cus.id
           AND company_id=@company_id) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'2' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
 FROM ikari_db_sage300.artcr j
RIGHT JOIN ikari_db_sage300.artcp t 
   ON j.codepymtyp=t.codepaym AND j.cntbtch=t.cntbtch AND j.CNTITEM=t.CNTITEM -- add codepymtyp=codepaym to have this query use an index
 LEFT JOIN customers_customer cus
   ON j.IDCUST=cus.code and cus.company_id=@company_id
 LEFT JOIN accounts_accountset aas
   ON cus.account_set_id = aas.id AND aas.company_id=@company_id
 LEFT JOIN accounting_batch ab
   ON j.cntbtch=ab.batch_no AND ab.batch_type=3 AND ab.company_id=@company_id
 LEFT JOIN accounting_journal aj
   ON ab.id=aj.batch_id AND j.CNTITEM=aj.code AND aj.company_id=@company_id
 LEFT JOIN ikari_db_sage300.arpjh tx 
   ON t.CODEPAYM=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.CNTITEM=tx.cntitem
WHERE t.codepaym = 'CA') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_4.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;




#insert AP payment (Misc. Payment)  -- 24583
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_5.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT DISTINCT
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
        ,aj.id AS `journal_id`
        ,tax.id tax_id
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
        ,0 adjamt, 0 discamt
        ,t.TXBSE1TC base_tax_amount
  FROM ikari_db_sage300.aptcr j
 RIGHT JOIN ikari_db_sage300.aptcn t 
    ON j.btchtype=t.batchtype AND j.cntbtch=t.cntbtch AND j.cntentr=t.cntrmit
  LEFT JOIN ikari_db_sage300.appjh tx 
    ON t.batchtype=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.cntrmit=tx.cntitem
  LEFT JOIN accounts_account aa
    ON REPLACE(t.idacct,'-','')=aa.description AND aa.company_id=@company_id
  LEFT JOIN taxes_taxgroup tg
    ON j.codetax1=tg.code AND tg.transaction_type=2 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax tax 
    ON tg.id = tax.tax_group_id AND t.taxclass1=tax.number AND tax.company_id=@company_id
  LEFT JOIN accounting_batch ab
   ON t.cntbtch=ab.batch_no AND ab.batch_type=4 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
   ON ab.id=aj.batch_id AND j.DOCNBR=aj.document_number AND j.TXTRMITREF=aj.reference AND aj.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDISTCODE=ad.code AND ad.type=2 AND ad.company_id=@company_id) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_5.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert AR receipt (misc. receipt)  -- 1232
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_6.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
        ,aj.id journal_id
        ,ntax.id tax_id
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
        ,0 adjamt, 0 discamt
        ,t.TXBSE1TC base_tax_amount
  FROM ikari_db_sage300.artcr j
 RIGHT OUTER JOIN ikari_db_sage300.artcn t 
    ON j.codepymtyp=t.codepaym AND j.cntbtch=t.cntbtch AND j.CNTITEM=t.CNTITEM
  LEFT JOIN accounting_batch ab
    ON t.cntbtch=ab.batch_no AND ab.batch_type=3 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.CNTITEM=aj.code AND aj.company_id=@company_id
  LEFT JOIN ikari_db_sage300.arrrd otax
    ON  t.cntbtch=otax.CNTBTCH AND t.CNTITEM=otax.CNTITEM AND t.IDACCT=otax.IDACCT
  LEFT JOIN taxes_taxgroup tg
    ON j.codetax1=tg.code AND tg.transaction_type=1 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax ntax 
    ON tg.id = ntax.tax_group_id AND otax.TAXCLASS1=ntax.number AND ntax.company_id=@company_id
  LEFT JOIN ikari_db_sage300.arpjh tx
    ON t.CODEPAYM=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.CNTITEM=tx.cntitem
  LEFT JOIN accounts_account aa
    ON REPLACE(t.idacct,'-','')=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDISTCODE=ad.code AND ad.type=1 AND ad.company_id=@company_id) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_6.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


-- 1734
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_2.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  gl_crown.BTCHENTRY code
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
       ,ab.status status
       ,date_format(gl_crown.DATEENTRY,'%Y-%m-%d') create_date
       ,date_format(gl_crown.DATEENTRY,'%Y-%m-%d') update_date
       ,NULL update_by
       ,0 is_hidden
       ,@company_id company_id
       ,@func_curr currency_id
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
       ,ab.id batch_id
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
 RIGHT JOIN  ikari_db_sage300.glbctl gl_entry
    ON gl_crown.BATCHID = gl_entry.BATCHID
  LEFT JOIN accounting_batch ab
    ON gl_crown.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE gl_entry.BATCHTYPE IN ('1', '3', '4')
   AND gl_crown.SRCETYPE NOT IN ('JE', 'RV')) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_2.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL Entry  -- 20157
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_7.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`SCURNAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`gljed` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` 
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `j`.`BTCHENTRY` = `t`.`JOURNALID`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.JOURNALID=aj.code AND aj.company_id=@company_id
 WHERE `j`.`SRCETYPE` = 'JE') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_7.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


-- 40618
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_8.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  (CASE WHEN t.SCURNAMT>=0 AND t.TRANSAMT>=0 THEN '0' ELSE '1' END) is_credit_account
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
       ,aj.id journal_id
       ,NULL tax_id
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
       ,0 adjamt, 0 discamt
       ,0 base_tax_amount
  FROM ikari_db_sage300.glbctl b
 RIGHT JOIN  ikari_db_sage300.gljeh j
    ON b.BATCHID = j.BATCHID
  LEFT JOIN ikari_db_sage300.gljed t
    ON j.BTCHENTRY = t.JOURNALID and j.BATCHID = t.BATCHNBR
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.JOURNALID=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
 WHERE b.BATCHTYPE IN ('1', '3', '4')
   AND j.SRCETYPE NOT IN ('JE', 'RV')) t0;
# END INSERT GL ENTRY


LOAD DATA INFILE 'c:/ikari_migration_files/trx_8.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL RV Journal  -- 1142
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_3.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  DISTINCT
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
        ab.status AS `status`,
        DATE_FORMAT(`j`.`JRNLDATE`,'%Y-%m-%d') AS `create_date`,
        DATE_FORMAT(`j`.`JRNLDATE`,'%Y-%m-%d') AS `update_date`,
        NULL AS `update_by`,
        0 AS `is_hidden`,
        @company_id AS `company_id`,
        @func_curr AS `currency_id`,
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
        NULL AS `reverse_to_period_val`,
        0 AS `is_rev_do`,
        `j`.`FISCALPERD` AS `perd_month`,
        `j`.`FISCALYR` AS `perd_year`,
        0 AS `is_auto_reversed_entry`
  FROM `ikari_db_sage300`.`glpjd` AS `j`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `j`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` = 'GL'
   AND `j`.`SRCETYPE` = 'RV'
   AND `j`.`TRANSAMT` > 0
   AND `b`.`BATCHTYPE` = '4'
 GROUP BY `j`.`BATCHNBR`, `j`.`ENTRYNBR`) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_3.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL RV Reverse Entry  -- 2282
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_9.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        `t`.`JNLDTLDESC` AS `description`,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        @func_curr AS `functional_currency_id`,
        DATE_FORMAT(`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        'GL-RV' AS `source_type`,
        NULL AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
 WHERE `j`.`SRCETYPE` = 'RV') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_9.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL RV Journal
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_4.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
  LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
   AND `j`.`SRCETYPE` = 'GL'
   AND `t`.`TRANSAMT` > 0
   AND `t`.`JNLDTLREF` != 'REVERSING ENTRY'
   AND `b`.`BATCHTYPE` = 2
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_4.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


-- 740
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_5.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `t`.`SRCELEDGER` IN ('AR', 'AP')
   AND `t`.`SRCETYPE` = 'GL'
   AND `t`.`TRANSAMT` > 0
   AND `t`.`JNLDTLREF` = 'REVERSING ENTRY'
   AND `b`.`BATCHTYPE` = 2
 GROUP BY `t`.`BATCHNBR`, `t`.`ENTRYNBR`) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_5.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;



#insert GL CR/DB Journal  --- SERVER KILLER, this one tries to get journal record by finding it transaction and do distinc and grouping. It's super crazy!
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_6.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
  LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY` AND t.SRCELEDGER = j.SRCELEDGER
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
   AND `j`.`SRCETYPE` IN ('CR', 'DB')
   AND `t`.`TRANSAMT` > 0
   AND `b`.`BATCHTYPE` = 2
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_6.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_7.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
  LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY` AND t.SRCELEDGER = j.SRCELEDGER
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
   AND `j`.`SRCETYPE` = 'IN'
   AND `t`.`TRANSAMT` > 0
   AND `b`.`BATCHTYPE` = 2
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_7.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_8.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
  LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY` AND t.SRCELEDGER = j.SRCELEDGER
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
   AND `j`.`SRCETYPE` = 'PY'
   AND `t`.`TRANSAMT` > 0
   AND `b`.`BATCHTYPE` = 2
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_8.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_9.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
  LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY` AND t.SRCELEDGER = j.SRCELEDGER
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
   AND `j`.`SRCETYPE` IN ('RD','AD')
   AND `t`.`TRANSAMT` > 0
   AND `b`.`BATCHTYPE` = 2
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_9.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_10.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AR'
   AND `t`.`SRCETYPE` IN ('CR', 'DB')
   AND `b`.`BATCHTYPE` = 2) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_10.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_11.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AR'
   AND `t`.`SRCETYPE` = 'IN'
   AND `b`.`BATCHTYPE` = 2) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_11.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_12.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AR'
   AND `t`.`SRCETYPE` = 'PY'
   AND `b`.`BATCHTYPE` = 2) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_12.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_13.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` IN ('CR', 'DB')
   AND `b`.`BATCHTYPE` = 2) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_13.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_14.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        WHERE id > 114505
        AND `journal_type` = 2
        and `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
        and `document_number` = `t`.`JNLDTLREF`
        ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'IN'
   AND `b`.`BATCHTYPE` = 2) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_14.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_15.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        WHERE id > 114505
        AND `journal_type` = 2
        and `document_type` = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
        and `document_number` = `t`.`JNLDTLREF`
        ORDER BY `id` DESC LIMIT 1) AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'PY'
   AND `b`.`BATCHTYPE` = 2) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_15.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL RV Reverse Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_16.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AR'
   AND `t`.`SRCETYPE` = 'GL'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_16.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_17.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        (SELECT `id` FROM `accounting_journal`
        WHERE id > 114505
        AND `journal_type` = 2
        and `document_number` = `t`.`JNLDTLREF`
        and `t`.`JNLDTLDESC` IS NOT NULL
        AND `t`.`JNLDTLREF` IS NOT NULL
        AND `name` = `t`.`JNLDTLDESC`) AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'GL'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_17.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;

#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_18.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AR'
   AND `t`.`SRCETYPE` IN ('RD', 'AD')
   AND `b`.`BATCHTYPE` = 2) t0;

LOAD DATA INFILE 'c:/ikari_migration_files/trx_18.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_19.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
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
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
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
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` IN ('RD', 'AD')
   AND `b`.`BATCHTYPE` = 2) t0;

LOAD DATA INFILE 'c:/ikari_migration_files/trx_19.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;




########################################## CAUTION !!!!############################################
# CODES BELOW MUST BE RUN AFTER ALL QUERIES COMPLETED, OTHERWISE THERE WILL BE DUPLICATES RECORDS #

-- insert accounting_batch --
SELECT max(id) into @row_number FROM accounting_batch;
SELECT (@row_number:=@row_number + 1) AS id, t0.*, 0 flag
INTO OUTFILE 'C:/ikari_migration_files/batch_AP_AR_AD.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
    ,2 batch_type -- TRANSACTION_TYPES['AP Invoice'] -- AD is categorized as invoice
    ,@company_id company_id
    ,CNTENTER no_entries -- Count Entries --
    ,(CASE WHEN CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURN)
      END) currency_id
    ,10 document_type 
    ,null related_batch_id
    ,SRCEAPPL source_ledger -- Source Application --
FROM ikari_db_sage300.apbta -- AP Payment and Adjustment Batches --
WHERE PAYMTYPE = 'AD' -- Payment Type --
UNION ALL
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
    ,1 batch_type -- TRANSACTION_TYPES['AR Invoice'] -- AD is categorized as invoice
    ,@company_id company_id
    ,CNTENTER no_entries
    ,(CASE WHEN CODECURN='DOS' THEN
        (select id from currencies_currency where code='SGD')
      ELSE
        (select id from currencies_currency where code=CODECURN)
      END) currency_id
    ,10 document_type 
    ,null related_batch_id
    ,SRCEAPPL source_ledger
FROM ikari_db_sage300.arbta -- AR Receipt and Adjustment Batches --
where CODEPYMTYP = 'AD') t0;

LOAD DATA INFILE 'c:/ikari_migration_files/batch_AP_AR_AD.txt' IGNORE INTO TABLE accounting_batch
   FIELDS TERMINATED BY ',' ENCLOSED BY '"'
   LINES TERMINATED BY '\n';

COMMIT;


-- insert journal AR-AD and AP-AD
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year
INTO OUTFILE 'C:/ikari_migration_files/journal_AR_AP_AD.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT j.CNTENTR code
    ,j.TEXTRMIT name
    ,2 journal_type -- TRANSACTION_TYPES)['AP Invoice'] --
    ,10 document_type -- DOCUMENT_TYPE_DICT --
    ,NULL po_number
    ,NULL order_number
    ,jp.idinvc document_number
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
    ,(CASE WHEN j.CODECURN='DOS' THEN @func_curr
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
    ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id AND ab.document_type='10'
  LEFT JOIN suppliers_supplier s
    ON j.IDVEND = s.code AND s.company_id = @company_id
  LEFT JOIN taxes_taxgroup tg 
    ON j.CODETAXGRP = tg.code AND tg.transaction_type = 2 AND tg.company_id = @company_id
  LEFT JOIN accounts_accountset aas
    ON j.IDACCTSET = aas.code AND aas.company_id = @company_id
 WHERE j.btchtype = 'AD'
UNION ALL
SELECT j.CNTITEM code
        ,j.TEXTRMIT name
        ,1 journal_type -- TRANSACTION_TYPES)['AR Invoice'] --
        ,10 document_type -- DOCUMENT_TYPE_DICT --
        ,NULL po_number
        ,NULL order_number
        ,jp.idinvc document_number
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
            @func_curr
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
    ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 1 AND ab.company_id = @company_id AND ab.document_type='10'
  LEFT JOIN taxes_taxgroup tg 
    ON j.CODETAXGRP = tg.code AND tg.transaction_type = 1 AND tg.company_id = @company_id
  LEFT JOIN accounts_accountset aas
    ON j.IDACCTSET = aas.code AND aas.company_id = @company_id
  LEFT JOIN customers_customer c
    ON j.IDCUST = c.code AND c.company_id = @company_id
 WHERE j.CODEPYMTYP = 'AD') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/journal_AR_AP_AD.txt' IGNORE INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


-- trx AP-AD
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_AP_AD.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  DISTINCT
         0 is_credit_transaction
        ,1 is_debit_transaction
        ,t.AMTADJTOT amount
        ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
        ,NULL remark
        ,t.CNTLINE trx_no
        ,0 is_close
        ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
        ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
        ,NULL update_by
        ,0 is_hidden
        ,IFNULL(aas.control_account_id,bnk.account_id) account_id -- get account from vendor or bank
        ,@company_id company_id
        ,NULL method_id
        ,NULL order_id
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN
            @func_curr
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `j`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,aj.id AS `journal_id`
        ,NULL tax_id
        ,0 tax_amount
        ,t.AMTPAYM total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,j.RATEEXCHTC exchange_rate
        ,t.AMTPAYMHC functional_amount
        ,@func_curr functional_currency_id
        ,date_format(j.DATERATETC ,'%Y-%m-%d') rate_date
        ,NULL reference
        ,NULL source_type
        ,(SELECT id FROM accounting_journal
           WHERE journal_type = 2
             AND document_type = '1'
             AND document_number = t.idinvc
             AND company_id = @company_id) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'1' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
 FROM ikari_db_sage300.aptcr j
RIGHT JOIN ikari_db_sage300.aptcp t
   ON j.btchtype = t.batchtype AND j.cntbtch = t.cntbtch AND j.cntentr = t.cntrmit
 LEFT JOIN accounting_batch ab 
   ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id AND ab.document_type = '10'
 LEFT JOIN accounting_journal aj
   ON ab.id = aj.batch_id AND t.idinvc=aj.document_number AND aj.company_id=@company_id
 LEFT JOIN suppliers_supplier s 
   ON j.IDVEND = s.code AND s.company_id = @company_id
 LEFT JOIN accounts_accountset aas
   ON s.account_set_id = aas.id AND aas.company_id = @company_id
 LEFT JOIN banks_bank bnk
   ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
WHERE t.batchtype = 'AD') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_AP_AD.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;



-- trx AR-AD
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/trx_AR_AD.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT   1 is_credit_transaction
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
        ,(CASE WHEN `j`.`CODECURN` = 'DOS' THEN
            @func_curr
          ELSE
            (SELECT `id` FROM `currencies_currency` WHERE `code` = `j`.`CODECURN`)
          END) AS `currency_id`
        ,NULL pair_id
        ,aj.id journal_id
        ,NULL tax_id
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
        ,(SELECT id FROM accounting_journal
           WHERE journal_type = 1
           AND document_type = '1'
           AND document_number = t.idinvc
           AND customer_id = cus.id
           AND company_id=@company_id) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'2' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
 FROM ikari_db_sage300.artcr j
RIGHT JOIN ikari_db_sage300.artcp t 
   ON j.codepymtyp=t.codepaym AND j.cntbtch=t.cntbtch AND j.CNTITEM=t.CNTITEM -- add codepymtyp=codepaym to have this query use an index
 LEFT JOIN customers_customer cus
   ON j.IDCUST=cus.code and cus.company_id=@company_id
 LEFT JOIN accounts_accountset aas
   ON cus.account_set_id = aas.id AND aas.company_id=@company_id
 LEFT JOIN accounting_batch ab
   ON j.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id and ab.document_type = '10'
 LEFT JOIN accounting_journal aj
   ON ab.id=aj.batch_id AND j.CNTITEM=aj.code AND aj.company_id=@company_id
 LEFT JOIN ikari_db_sage300.arpjh tx 
   ON t.CODEPAYM=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.CNTITEM=tx.cntitem
WHERE t.codepaym = 'AD') t0;


LOAD DATA INFILE 'c:/ikari_migration_files/trx_AR_AD.txt' IGNORE INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;
############################################ END CAUTION #########################################



#Insert accounting_revaluationlogs
SELECT max(id) into @row_number FROM accounting_revaluationlogs;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/revlog_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT
      1 AS `journal_type`,
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
      0 AS `is_hidden`,
      @company_id AS `company_id`,
      (CASE WHEN `CURNCYCODE` = 'DOS' THEN
          @func_curr
        ELSE
          (SELECT `id` FROM `currencies_currency` WHERE `code` = `CURNCYCODE`)
        END) AS `currency_id`
FROM ikari_db_sage300.arrvllog
UNION
SELECT 
      2 AS `journal_type`,
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
      0 AS `is_hidden`,
      @company_id AS `company_id`,
      (CASE WHEN `CURNCYCODE` = 'DOS' THEN
          @func_curr
       ELSE
          (SELECT `id` FROM `currencies_currency` WHERE `code` = `CURNCYCODE`)
       END) AS `currency_id`
FROM ikari_db_sage300.aprvllog) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/revlog_1.txt' IGNORE INTO TABLE accounting_revaluationlogs
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#Insert accounting_revaluationdetails
SELECT max(id) into @row_number FROM accounting_revaluationdetails;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE 'C:/ikari_migration_files/revdtl_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT
      `jh`.`IDINVC` AS `document_no`,
      `jd`.`AMTADJTCUR` source_amount,
      `jd`.`RATEDOC` prior_rate,
      `jd`.`RATEEXCHHC` rev_rate,
      `jd`.`AMTADJHCUR` prior_functional,
      (`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`) new_functional,
      ((`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`) - (`jd`.`AMTADJHCUR`)) gain_loss,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `create_date`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `update_date`,
      NULL AS `update_by`,
      0 AS `is_hidden`,
      cus.id AS `customer_id`,
      arl.id AS `posting_id`,
      NULL AS `supplier_id`,
      DATE_FORMAT(`jh`.`DATEINVC`,'%Y-%m-%d') AS `document_date`,
      DATE_FORMAT(`jh`.`DATEDUE`,'%Y-%m-%d') AS `due_date`
FROM ikari_db_sage300.arpjh AS `jh`
  LEFT JOIN ikari_db_sage300.arpjd jd
    ON `jh`.`POSTSEQNCE` = `jd`.`POSTSEQNCE`
   AND `jh`.`IDINVC` = `jd`.`IDINVC`
   AND `jh`.`TYPEBTCH` = `jd`.`TYPEBTCH`
   AND jd.cntseqence = 1
  LEFT JOIN customers_customer cus
    ON `jh`.`IDCUST` = cus.code AND cus.company_id=@company_id
  LEFT JOIN currencies_currency cur
    ON `jh`.`CODECURNTC` = cur.code
  LEFT JOIN accounting_revaluationlogs arl
    ON `jh`.`POSTSEQNCE` = arl.posting_sequence
   AND `jh`.`RATETYPETC` = arl.rate_type
   AND cur.id = arl.currency_id
   AND arl.journal_type = 1
   AND arl.company_id = @company_id
 WHERE `jh`.`TYPEBTCH`='RV'
HAVING `posting_id` IS NOT NULL
UNION ALL
SELECT
      `jh`.`IDINVC` AS `document_no`,
      `jd`.`AMTADJTCUR` source_amount,
      `jd`.`RATEDOC` prior_rate,
      `jd`.`RATEEXCHHC` rev_rate,
      `jd`.`AMTADJHCUR` prior_functional,
      (`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`) new_functional,
      ((`jd`.`AMTADJHCUR`) - (`jd`.`AMTADJTCUR` * `jd`.`RATEEXCHHC`)) gain_loss,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `create_date`,
      DATE_FORMAT(`jh`.`DATEBTCH`,'%Y-%m-%d') AS `update_date`,
      NULL AS `update_by`,
      0 AS `is_hidden`,
      NULL AS `customer_id`,
      arl.id AS `posting_id`,
      sup.id `supplier_id`,
      DATE_FORMAT(`jh`.`DATEINVC`,'%Y-%m-%d') AS `document_date`,
      DATE_FORMAT(`jh`.`DATEDUE`,'%Y-%m-%d') AS `due_date`
FROM ikari_db_sage300.appjh AS `jh`
  LEFT JOIN ikari_db_sage300.appjd jd
    ON `jh`.`POSTSEQNCE` = `jd`.`POSTSEQNCE`
   AND `jh`.`IDINVC` = `jd`.`IDINVC`
   AND `jh`.`TYPEBTCH` = `jd`.`TYPEBTCH`
   AND jd.cntseqence = 1
  LEFT JOIN currencies_currency cur
    ON `jh`.`CODECURNTC` = cur.code
  LEFT JOIN accounting_revaluationlogs arl
    ON `jh`.`POSTSEQNCE` = arl.posting_sequence
   AND `jh`.`RATETYPETC` = arl.rate_type
   AND cur.id = arl.currency_id
   AND arl.journal_type = 2
   AND arl.company_id = @company_id
  LEFT JOIN suppliers_supplier sup
    ON `jh`.`IDVEND` = sup.code AND sup.company_id = @company_id
 WHERE `jh`.`TYPEBTCH`='RV'
HAVING `posting_id` IS NOT NULL) t0;


LOAD DATA INFILE 'c:/ikari_migration_files/revdtl_1.txt' IGNORE INTO TABLE accounting_revaluationdetails
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


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

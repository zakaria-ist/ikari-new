### INSERT MASTER DATA ###
-- WARNING: You need to replace all @company_id to specific company_id to run this query!! --
-- SET @company_id = 8; -- 3 = Crown, 4 = Nitto, 5 = Front

insert into accounting_paymentcode (
  `code`, `name`, `source_type`, `payment_type`, `company_id`,
  `is_active`, `create_date`, `update_date`, `update_by`, `is_hidden`)
select
      paymcode code,
      textdesc name,
      '2' source_type,
      paymtype payment_type,
      @company_id company_id,
      actvsw is_active,
      date_format(AUDTDATE,'%Y-%m-%d') create_date,
      date_format(AUDTDATE,'%Y-%m-%d') update_date,
      null update_by,
      0 is_hidden
from ikari_db_sage300.apptp;


insert into accounting_paymentcode (
  `code`, `name`, `source_type`, `payment_type`, `company_id`,
  `is_active`, `create_date`, `update_date`, `update_by`, `is_hidden`)
select
      paymcode code,
      textdesc name,
      '1' source_type,
      paymtype payment_type,
      @company_id company_id,
      actvsw is_active,
      date_format(AUDTDATE,'%Y-%m-%d') create_date,
      date_format(AUDTDATE,'%Y-%m-%d') update_date,
      null update_by,
      0 is_hidden
from ikari_db_sage300.arptp;


insert into accounting_aroptions (
  `invoice_prefix`, `invoice_length`, `invoice_next_number`, `cnote_prefix`,
  `cnote_length`, `cnote_next_number`, `dnote_prefix`, `dnote_length`, `dnote_next_number`,
  `interest_prefix`, `interest_length`, `interest_next_number`, `recurring_prefix`,
  `recurring_length`, `recurring_next_number`, `prepayment_prefix`, `prepayment_length`,
  `prepayment_next_number`, `ucash_prefix`, `ucash_length`, `ucash_next_number`, `adjustment_prefix`,
  `adjustment_length`, `adjustment_next_number`, `receipt_prefix`, `receipt_length`,
  `receipt_next_number`, `refund_prefix`, `refund_length`, `refund_next_number`, `aging_period_1`,
  `aging_period_2`, `aging_period_3`, `company_id`, `create_date`, `update_date`, `update_by`, `is_hidden`)
select
      ar2.TEXTIVPF invoice_prefix,
      ar2.CNTIVPFLEN invoice_length,
      ar2.CNTIVSEQ invoice_next_number,
      ar2.TEXTCRPF cnote_prefix,
      ar2.CNTCRPFLEN cnote_length,
      ar2.CNTCRSEQ cnote_next_number,
      ar2.TEXTDRPF dnote_prefix,
      ar2.CNTDRPFLEN dnote_length,
      ar2.CNTDRSEQ dnote_next_number,
      ar2.TEXTITPF interest_prefix,
      ar2.CNTITPFLEN interest_length,
      ar2.CNTITSEQ interest_next_number,
      ar2.TEXTRCPF recurring_prefix,
      ar2.CNTRCPFLEN recurring_length,
      ar2.CNTRCSEQ recurring_next_number,
      ar3.PPDPREFIX prepayment_prefix,
      ar3.PPDPFXLEN prepayment_length,
      ar3.CNTPPDSEQ prepayment_next_number,
      ar3.UCPREFIX ucash_prefix,
      ar3.UCPFXLEN ucash_length,
      ar3.CNTUCSEQ ucash_next_number,
      ar3.ADPREFIX adjustment_prefix,
      ar3.ADPFXLEN adjustment_length,
      ar3.CNTADSEQ adjustment_next_number,
      ar3.PYPREFIX receipt_prefix,
      ar3.PYPFXLEN receipt_length,
      ar3.CNTPYSEQ receipt_next_number,
      ar3.RFPREFIX refund_prefix,
      ar3.RFPFXLEN refund_length,
      ar3.CNTRFSEQ refund_next_number,
      ar4.AGINPERD1 aging_period_1,
      ar4.AGINPERD2 aging_period_2,
      ar4.AGINPERD3 aging_period_3,
      @company_id company_id,
      '2020-01-01' create_date,
      '2020-01-01' update_date,
      null update_by,
      0 is_hidden
from ikari_db_sage300.arr02 ar2, ikari_db_sage300.arr03 ar3, ikari_db_sage300.arr04 ar4;


insert into accounting_apoptions (
  `recurring_pay_prefix`, `recurring_pay_length`, `recurring_pay_next_number`, `prepayment_prefix`, `prepayment_length`,
  `prepayment_next_number`, `adjustment_prefix`, `adjustment_length`, `adjustment_next_number`, `payment_prefix`,
  `payment_length`, `payment_next_number`, `aging_period_1`, `aging_period_2`, `aging_period_3`, `company_id`,
  `create_date`, `update_date`, `update_by`, `is_hidden`)
select
      ap3.RPPFX recurring_pay_prefix,
      ap3.RPPFXLEN recurring_pay_length,
      ap3.RPNEXTSEQ recurring_pay_next_number,
      ap3.PPDPREFIX prepayment_prefix,
      ap3.PPDPFXLEN prepayment_length,
      ap3.CNTPPDBTCH prepayment_next_number,
      ap3.ADPFX adjustment_prefix,
      ap3.ADPFXLEN adjustment_length,
      ap3.ADNEXTSEQ adjustment_next_number,
      ap3.PYPFX payment_prefix,
      ap3.PYPFXLEN payment_length,
      ap3.PYNEXTSEQ payment_next_number,
      ap3.AGINPRD1 aging_period_1,
      ap3.AGINPRD2 aging_period_2,
      ap3.AGINPRD3 aging_period_3,
      @company_id company_id,
      '2020-01-01' create_date,
      '2020-01-01' update_date,
      null update_by,
      0 is_hidden
from ikari_db_sage300.app03 ap3;


#insert companies_costcenters
insert into companies_costcenters (
`name`, `code`, `description`, `is_active`,
`create_date`, `update_date`, `update_by`, `is_hidden`, `company_id`)
select
    SEGVALDESC name
    ,SEGVAL code
    ,SEGVALDESC description
    ,1 is_active
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,@company_id company_id
from ikari_db_sage300.glasv o;

#insert accounts_account
insert into accounts_account (
`name`, `code`, `description`, `is_editable`, `is_active`,
`create_date`, `update_date`, `update_by`, `is_hidden`, `company_id`,
`account_group_id`, `account_type`, `balance_type`, `credit_amount`, `debit_amount`,
`is_multicurrency`, `is_specific_currency`, `default_currency_id`, `profit_loss_group_id`)
select
    ACCTDESC name
    ,ACCTFMTTD code  -- modified by SF, to match visual as sage300
    ,ACCTID description -- modified by SF, this field will replace field code in join with all sage300's tables in all scripts
    ,1 is_editable
    ,1 is_active
    ,date_format(CREATEDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(select id from accounts_accounttype where code = (SELECT oo.ACCTGRPCOD from ikari_db_sage300.glacgrp oo
     where oo.ACCTGRPCOD=o.ACCTGRPCOD) and company_id=@company_id) account_group_id
    ,(case when ACCTTYPE='B' then '2' -- ACCOUNT_TYPE_DICT['Balance Sheet'] --
     when ACCTTYPE='I' then '1' -- ACCOUNT_TYPE_DICT['Income Statement'] --
     else '3' -- ACCOUNT_TYPE_DICT['Retained Earning'] --
     end) account_type -- ACCOUNT_TYPE --
    ,acctbal balance_type -- BALANCE_TYPE --
    ,0 credit_amount
    ,0 debit_amount
    ,MCSW is_multicurrency
    ,SPECSW is_specific_currency
    ,(CASE WHEN DEFCURNCOD = 'DOS' THEN
      (SELECT id from currencies_currency WHERE code='SGD')
      ELSE
        (SELECT id from currencies_currency WHERE code=DEFCURNCOD)
      END) default_currency_id
    ,NULL profit_loss_group_id
from ikari_db_sage300.glamf o;

update accounts_account
set account_segment = LEFT(code , 4) where company_id=@company_id;

update accounts_account acc
set segment_code_id = (select id from companies_costcenters where code = SUBSTRING(acc.code , 5) and company_id=@company_id) where company_id=@company_id;


#insert currencies_exchangerate
INSERT INTO currencies_exchangerate (
`rate`, `exchange_date`, `description`, `create_date`, `update_date`,
`update_by`, `is_hidden`, `company_id`, `from_currency_id`, `to_currency_id`,
`flag`, `apply_flag`)
SELECT
    RATE rate
    ,date_format(RATEDATE,'%Y-%m-%d') exchange_date
    ,NULL description
    ,date_format(RATEDATE,'%Y-%m-%d') create_date
    ,date_format(RATEDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN SOURCECUR = 'DOS' THEN
      (SELECT id from currencies_currency WHERE code='SGD')
      ELSE
        (SELECT id from currencies_currency WHERE code=SOURCECUR)
      END) from_currency_id
    ,(CASE WHEN HOMECUR = 'DOS' THEN
      (SELECT id from currencies_currency WHERE code='SGD')
      ELSE
        (SELECT id from currencies_currency WHERE code=HOMECUR)
      END) to_currency_id
    ,'ACCOUNTING' flag
    ,1 apply_flag
FROM ikari_db_sage300.cscrd;


#insert accounts_accountset:
INSERT INTO `accounts_accountset` (
`create_date`, `update_date`, `code`, `is_active`, `is_hidden`,
`company_id`, `control_account_id`, `currency_id`, `revaluation_account_id`, `type`,
`name`, `revaluation_realized_gain_id`, `revaluation_realized_loss_id`, `revaluation_rounding_id`,
`revaluation_unrealized_gain_id`, `revaluation_unrealized_loss_id`, `discount_account_id`,
`prepayment_account_id`, `writeoff_account_id`)
SELECT
    DATE_FORMAT(AUDTDATE,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(AUDTDATE,'%Y-%m-%d') AS `update_date`,
    `ACCTSET` AS `code`,
    1 AS `is_active`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    `ctrl_acc`.`id` AS `control_account_id`,
    (CASE WHEN `CURRCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
    ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `CURRCODE`)
    END) AS `currency_id`,
    NULL AS `revaluation_account_id`,
    2 AS `type`, -- ACCOUNT_SET_TYPE['AP Account Set'] --
    `TEXTDESC` AS `name`,
    `rlzdgain_acc`.`id` AS `revaluation_realized_gain_id`,
    `rlzdloss_acc`.`id` AS `revaluation_realized_loss_id`,
    `rounding_acc`.`id` AS `revaluation_rounding_id`,
    `unrlgain_acc`.`id` AS `revaluation_unrealized_gain_id`,
    `unrlloss_acc`.`id` AS `revaluation_unrealized_loss_id`,
    `discount_acc`.`id` AS `discount_account_id`,
    `prepayment_acc`.`id` AS `prepayment_account_id`,
     NULL AS `writeoff_account_id`
FROM `ikari_db_sage300`.`apras`
LEFT JOIN `accounts_account` AS `ctrl_acc` ON `ctrl_acc`.`code` = REPLACE(`IDACCTAP`, '-', '') AND `ctrl_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `rlzdgain_acc` ON `rlzdgain_acc`.`code` = REPLACE(`RLZGNACT`, '-', '') AND `rlzdgain_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `rlzdloss_acc` ON `rlzdloss_acc`.`code` = REPLACE(`RLZLSACT`, '-', '') AND `rlzdloss_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `rounding_acc` ON `rounding_acc`.`code` = REPLACE(`RNDACCT`, '-', '') AND `rounding_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `unrlgain_acc` ON `unrlgain_acc`.`code` = REPLACE(`URLZGNACT`, '-', '') AND `unrlgain_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `unrlloss_acc` ON `unrlloss_acc`.`code` = REPLACE(`URLZLSACT`, '-', '') AND `unrlloss_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `prepayment_acc` ON `prepayment_acc`.`code` = REPLACE(`PPAYACCT`, '-', '') AND `prepayment_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `discount_acc` ON `discount_acc`.`code` = REPLACE(`DISCACCT`, '-', '') AND `discount_acc`.`company_id` = @company_id
UNION
SELECT
    DATE_FORMAT(AUDTDATE,'%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(AUDTDATE,'%Y-%m-%d') AS `update_date`,
    `IDACCTSET` AS `code`,
    1 AS `is_active`,
    0 AS `is_hidden`,
    @company_id AS `company_id`,
    `ctrl_acc`.`id` AS `control_account_id`,
    (CASE WHEN `CURNCODE` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
    ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `CURNCODE`)
    END) AS `currency_id`,
    NULL AS `revaluation_account_id`,
    1 AS `type`, -- ACCOUNT_SET_TYPE['AR Account Set'] --
    `TEXTDESC` AS `name`,
    `rlzdgain_acc`.`id` AS `revaluation_realized_gain_id`,
    `rlzdloss_acc`.`id` AS `revaluation_realized_loss_id`,
    `rounding_acc`.`id` AS `revaluation_rounding_id`,
    `unrlgain_acc`.`id` AS `revaluation_unrealized_gain_id`,
    `unrlloss_acc`.`id` AS `revaluation_unrealized_loss_id`,
    `discount_acc`.`id` AS `discount_account_id`,
    `prepayment_acc`.`id` AS `prepayment_account_id`,
    `writeoff_acc`.`id` AS `writeoff_account_id`
FROM `ikari_db_sage300`.`arras`
LEFT JOIN `accounts_account` AS `ctrl_acc` ON `ctrl_acc`.`code` = REPLACE(`ARIDACCT`, '-', '') AND `ctrl_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `rlzdgain_acc` ON `rlzdgain_acc`.`code` = REPLACE(`RLZDGAIN`, '-', '') AND `rlzdgain_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `rlzdloss_acc` ON `rlzdloss_acc`.`code` = REPLACE(`RLZDLOSS`, '-', '') AND `rlzdloss_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `rounding_acc` ON `rounding_acc`.`code` = REPLACE(`RNDACCT`, '-', '') AND `rounding_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `unrlgain_acc` ON `unrlgain_acc`.`code` = REPLACE(`UNRLGAIN`, '-', '') AND `unrlgain_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `unrlloss_acc` ON `unrlloss_acc`.`code` = REPLACE(`UNRLLOSS`, '-', '') AND `unrlloss_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `prepayment_acc` ON `prepayment_acc`.`code` = REPLACE(`CASHLIAB`, '-', '') AND `prepayment_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `discount_acc` ON `discount_acc`.`code` = REPLACE(`ACCTDISC`, '-', '') AND `discount_acc`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `writeoff_acc` ON `writeoff_acc`.`code` = REPLACE(`ACCTWROF`, '-', '') AND `writeoff_acc`.`company_id` = @company_id;

#insert banks_bank
INSERT INTO banks_bank (
`name`, `account_owner`, `account_number`, `description`, `is_active`,
`create_date`, `update_date`, `update_by`, `is_hidden`, `company_id`,
`country_id`, `currency_id`, `account_id`, `code`)
SELECT
    NAME name
    ,null account_owner
    ,null account_number
    ,NAME description
    ,1 is_active
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,@company_id company_id
    ,null country_id
    ,(CASE WHEN CURNSTMT = 'DOS' THEN
        (select id from currencies_currency where code= 'SGD')
     ELSE
        (select id from currencies_currency where code= CURNSTMT)
     END) currency_id
    ,(select id from accounts_account
     where code=IDACCT and company_id=@company_id) account_id
    ,BANK code
FROM ikari_db_sage300.bkacct;

UPDATE banks_bank as bnk
  SET gain_account_id = (SELECT id FROM accounts_account 
                          WHERE company_id=@company_id AND code = 
                            (SELECT gainacct FROM ikari_db_sage300.bkcur WHERE bank = bnk.code)),
      loss_account_id = (SELECT id FROM accounts_account 
                          WHERE company_id=@company_id AND code = 
                            (SELECT lossacct FROM ikari_db_sage300.bkcur WHERE bank = bnk.code)),
      round_account_id = (SELECT id FROM accounts_account 
                          WHERE company_id=@company_id AND code = 
                            (SELECT roundacct FROM ikari_db_sage300.bkcur WHERE bank = bnk.code))
  WHERE company_id=@company_id AND bnk.code <> 'CONVERT';

#insert revaluationcode
INSERT INTO `accounts_revaluationcode`(
  `code`, `description`, `is_hidden`, `create_date`, `update_date`, `rate_type`, `source_type`,
  `company_id`, `revaluation_unrealized_gain_id`, `revaluation_unrealized_loss_id`)
SELECT
	`RVALID` AS `code`,
	`DESC` AS `description`,
	0 AS `is_hidden`,
	date_format(`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
	date_format(`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
	'SR' AS `rate_type`,
	CONCAT(`SRCELDGR`, '-', `SRCETYPE`) AS `source_type`,
	@company_id AS `company_id`,
	`acc_gain`.`id` AS `revaluation_unrealized_gain_id`,
	`acc_loss`.`id` AS `revaluation_unrealized_loss_id`
FROM `ikari_db_sage300`.`glrval`
LEFT JOIN `accounts_account` AS `acc_gain` ON `acc_gain`.`code` = `ikari_db_sage300`.`glrval`.`ACCTGAIN` AND `acc_gain`.`company_id` = @company_id
LEFT JOIN `accounts_account` AS `acc_loss` ON `acc_loss`.`code` = `ikari_db_sage300`.`glrval`.`ACCTLOSS` AND `acc_loss`.`company_id` = @company_id;


#insert accounts_distributioncode
INSERT INTO accounts_distributioncode(
`create_date`, `update_date`, `code`, `name`, `is_active`,
`gl_account_id`, `company_id`, `is_hidden`, `type`)
SELECT
    date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,IDDIST code
    ,TEXTDESC name
    ,1 is_active
    ,(SELECT ID FROM accounts_account WHERE code=(SELECT REPLACE(IDACCTREV, '-', '')) and company_id=@company_id) gl_account_id
    ,@company_id company_id
    ,0 is_hidden
    ,1 type -- DIS_CODE_TYPE['AR Distribution Code'] --
FROM ikari_db_sage300.arrdc
UNION
SELECT
    date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,DISTID code
    ,TEXTDESC name
    ,1 is_active
    ,(SELECT ID FROM accounts_account WHERE code=(SELECT REPLACE(IDGLACCT, '-', '')) and company_id=@company_id) gl_account_id
    ,@company_id company_id
    ,0 is_hidden
    ,2 type -- DIS_CODE_TYPE['AP Distribution Code'] --
FROM ikari_db_sage300.aprdc;


INSERT INTO accounts_accountcurrency(
`name`, `is_active`, `is_hidden`, `create_date`, `update_date`,
`update_by`, `account_id`, `currency_id`, `revaluation_code_id`)
SELECT
    `glavc`.`ACCTID` AS `name`,
    `glavc`.`REVALSW` AS `is_active`,
    0 AS `is_hidden`,
    DATE_FORMAT(`glavc`.`AUDTDATE`, '%Y-%m-%d') AS `create_date`,
    DATE_FORMAT(`glavc`.`AUDTDATE`, '%Y-%m-%d') AS `update_date`,
    NULL AS `update_by`,
    (SELECT `id` FROM `accounts_account`
     WHERE `code` = `glavc`.`ACCTID` AND `company_id` = @company_id) AS `account_id`,
    (CASE WHEN `glavc`.`CURNID` = 'DOS' THEN
        (SELECT `id` FROM `currencies_currency` WHERE `code` = 'SGD')
     ELSE
        (SELECT `id` FROM `currencies_currency` WHERE `code` = `glavc`.`CURNID`)
     END) AS `currency_id`,
    (SELECT `id` FROM `accounts_revaluationcode` WHERE `code` = `glavc`.`REVALID` AND `company_id` = @company_id) AS `revaluation_code_id`
FROM `ikari_db_sage300`.`glavc` AS `glavc`;



#insert taxauthority
INSERT INTO taxes_taxauthority(
`code`, `name`, `retainage_rpt_type`, `max_tax_allowable`, `no_tax_charged_below`
, `tax_base`, `report_level`, `is_recoverable`, `is_expense_separately`, `create_date`
, `update_date`, `update_by`, `is_hidden`, `currency_id`, `expense_account_id`
, `liability_account_id`, `recoverable_account_id`, `company_id`, `recoverable_rate`)
SELECT
    AUTHORITY code
    ,AUTHORITY name
    ,1 retainage_rpt_type -- RETAINAGE_REPORT_TYPES['No Reporting'] --
    ,MAXTAX  max_tax_allowable
    ,0.000000 no_tax_charged_below
    ,TXBASE tax_base
    ,AUDITLEVEL report_level
    ,RECOVERABL is_recoverable
    ,EXPSEPARTE is_expense_separately
    ,date_format(LASTMAINT,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,(CASE WHEN SCURN = 'DOS' THEN
        (select id from currencies_currency where code= 'SGD')
     ELSE
        (select id from currencies_currency where code= SCURN)
     END) currency_id
    ,(select id from accounts_account
     where code = ACCTEXP and company_id=@company_id) expense_account_id
    ,(select id from accounts_account
     where code = LIABILITY and company_id=@company_id) liability_account_id
    ,(select id from accounts_account
     where code = ACCTRECOV and company_id=@company_id) recoverable_account_id
    ,@company_id company_id
    ,RATERECOV recoverable_rate
FROM ikari_db_sage300.txauth;


#insert taxgroup
INSERT INTO taxes_taxgroup(
`code`, `name`, `transaction_type`, `calculation_method`, `is_taxable`
, `is_surtax`, `create_date`, `update_date`, `update_by`, `is_hidden`
, `currency_id`, `surtax_authority_id`, `tax_authority_id`, `company_id`)
SELECT
    GROUPID code
    ,GROUPID name
    ,TTYPE transaction_type -- TAX_TRX_TYPES --
    ,CALCMETHOD calculation_method
    ,TAXABLE1 is_taxable
    ,SURTAX1 is_surtax
    ,date_format(LASTMAINT,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,(CASE WHEN SRCCURN = 'DOS' THEN
        (select id from currencies_currency where code= 'SGD')
     ELSE
        (select id from currencies_currency where code= SRCCURN)
     END) currency_id
    ,(SELECT id FROM taxes_taxauthority WHERE CODE = AUTHORITY1 and company_id=@company_id ) surtax_authority_id
    ,(SELECT id FROM taxes_taxauthority WHERE CODE = AUTHORITY1  and company_id=@company_id) tax_authority_id
    ,@company_id company_id
 FROM ikari_db_sage300.txgrp;


#insert taxes_tax
INSERT INTO taxes_tax(
`name`, `rate`, `number`, `create_date`, `update_date`,
`update_by`, `is_hidden`, `code`, `mtd`, `mtdoc`,
`tax_account_code_id`, `tax_type`, `ytd`, `ytdoc`, `shortname`,
`distribution_code_id`, `company_id` ,tax_authority_id , tax_group_id)
select
    concat(tax.tax_authority,' - ',CONVERT(transaction_type,BINARY),' - ',tax.description,' - ',tax.tax_rate,'%') name
    ,tax.tax_rate rate
    ,class number
    ,date_format(tax.update_date,'%Y-%m-%d') create_date
    ,date_format(tax.update_date,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,null code
    ,null mtd
    ,null mtdoc
    ,(CASE WHEN tax.transaction_type='SALES' THEN
        (SELECT id from accounts_account WHERE code=tax.tax_account_code AND company_id=@company_id)
     ELSE
        (SELECT recoverable_account_id FROM taxes_taxauthority WHERE code=tax.tax_authority AND company_id=@company_id)
     END) tax_account_code_id
    ,classaxis tax_type -- TAX_TYPE --
    ,null ytd
    ,null ytdoc
    ,null shortname
    ,null distribution_code_id
    ,@company_id company_id
    ,(SELECT id FROM taxes_taxauthority WHERE CODE = tax.tax_authority
        and company_id=@company_id) tax_authority_id
    ,(SELECT id FROM taxes_taxgroup WHERE CODE = tax.tax_group
        and transaction_type =type -- TAX_TRX_TYPES --
        and company_id=@company_id) tax_group_id
from (
    SELECT
        `tg`.`GROUPID` AS `tax_group`,
        `tc`.`CLASSTYPE` AS `type`,
        `ta`.`AUTHORITY` AS `tax_authority`,
        `ta`.`SCURN` AS `currency`,
        IF(`tc`.`CLASSTYPE` = 1, 'SALES', 'PURCHASE') AS `transaction_type`, -- TAX_TRX_TYPES_DICT['Sales'], TAX_TRX_TYPES_DICT['Purchases']  --
        `tc`.`CLASSAXIS` AS `classaxis`,
        IF(`tc`.`classaxis` = 1, 'Customers', 'Items') AS `class_type`, -- TAX_TYPE['Customer/Vendor'], TAX_TYPE['Item'] --
        `tc`.`CLASS` AS `class`,
        `tc`.`DESC` AS `description`,
        ROUND(`tr`.`ITEMRATE1`, 5) AS `tax_rate`,
        `tr`.`LASTMAINT` AS `last_maintained`,
        `tr`.`AUDTDATE` AS `update_date`,
        REPLACE(IF(`tc`.`CLASSTYPE` = 1, `ta`.`LIABILITY`, `ta`.`ACCTRECOV`), '-', '') AS `tax_account_code`,
        IF(`tc`.`CLASSTYPE` = 1, `ga_out`.`ACCTDESC`, `ga_in`.`ACCTDESC`) AS `tax_account_desc`
    FROM `ikari_db_sage300`.`txclass` AS `tc`
    LEFT JOIN `ikari_db_sage300`.`txauth` AS `ta` ON `ta`.`AUTHORITY` = `tc`.`AUTHORITY`
    LEFT JOIN `ikari_db_sage300`.`txrate` AS `tr` ON `tr`.`AUTHORITY` = `tc`.`AUTHORITY` AND `tr`.`TTYPE` = `tc`.`CLASSTYPE` AND `tr`.`BUYERCLASS` = `tc`.`CLASS`
    LEFT JOIN `ikari_db_sage300`.`glamf` AS `ga_out` ON `ga_out`.`ACCTID` = REPLACE(`ta`.`LIABILITY`, '-', '')
    LEFT JOIN `ikari_db_sage300`.`glamf` AS `ga_in` ON `ga_in`.`ACCTID` = REPLACE(`ta`.`ACCTRECOV`, '-', '')
    LEFT JOIN `ikari_db_sage300`.`txgrp` AS `tg` ON `tg`.`AUTHORITY1` = `ta`.`AUTHORITY` AND `tg`.`TTYPE` = `tc`.`CLASSTYPE`
    WHERE `tc`.`CLASSAXIS` = 1 -- TAX_TYPE['Customer/Vendor'] --
    ORDER BY `ta`.`AUTHORITY`, `tc`.`CLASSTYPE`, `tc`.`CLASS`
) tax;


#insert suppliers_supplier
INSERT INTO suppliers_supplier(
`name`, `code`, `address`, `postal_code`, `email`,
`phone`, `fax`, `ship_info_1`, `ship_info_2`, `is_active`,
`create_date`, `update_date`, `update_by`, `is_hidden`, `company_id`,
`country_id`, `currency_id`, `term_days`, `accode_ap`, `accode_bnk`,
`accode_chr`, `accode_exc`, `accode_pur`, `center_ap`, `center_bnk`,
`center_chr`, `center_exc`, `center_pur`, `credit_limit`, `payment_mode_id`,
`ship_via`, `tax_id`, `distribution_id`, `payment_code_id`, `account_set_id`, `bank_id`)
SELECT
    vendname name
    ,vendorid code
    ,null address
    ,null postal_code
    ,null email
    ,null phone
    ,null fax
    ,null ship_info_1
    ,null ship_info_2
    ,1 is_active
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(DATELASTMN,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,@company_id company_id
    ,null country_id
    ,(CASE WHEN CURNCODE='DOS'
      THEN (SELECT id FROM currencies_currency WHERE code='SGD')
      ELSE (SELECT id FROM currencies_currency WHERE code=CURNCODE)
      END) currency_id
    ,(SELECT SUBSTRING( TERMSCODE, 1, 2 )) term_days
    ,0 accode_ap
    ,0 accode_bnk
    ,0 accode_chr
    ,0 accode_exc
    ,0 accode_pur
    ,0 center_ap
    ,0 center_bnk
    ,0 center_chr
    ,0 center_exc
    ,0 center_pur
    ,0 credit_limit
    ,null payment_mode_id
    ,0 ship_via
    ,(select id from taxes_tax
        WHERE tax_group_id =
            (SELECT id FROM taxes_taxgroup WHERE
                CODE = CODETAXGRP and
                transaction_type =2 and -- TAX_TRX_TYPES_DICT['Purchases'] --
                company_id=@company_id)
            and number = TAXCLASS1
            and company_id=@company_id
     ) tax_id
    ,(select id from accounts_distributioncode
        where code=DISTCODE
            and company_id=@company_id
            and type=2 -- DIS_CODE_TYPE['AP Distribution Code'] --
     ) distribution_id
    ,null payment_code_id
    ,(select id from accounts_accountset
        where code = IDACCTSET
            and company_id=@company_id
     ) account_set_id
     ,null bank_id
FROM ikari_db_sage300.apven;


#insert customers_customer
INSERT INTO customers_customer (
`name`, `code`, `postal_code`, `phone`, `email`,
`fax`, `note1`, `note2`, `note3`, `is_active`,
`create_date`, `update_date`, `update_by`, `is_hidden`, `company_id`,
`country_id`, `currency_id`, `tax_id`, `address`, `accode_ar`,
`accode_bnk`, `accode_chr`, `accode_exc`, `accode_int`, `accode_sal`,
`center_ar`, `center_bnk`, `center_chr`, `center_exc`, `center_int`,
`center_sal`, `credit_limit`, `customer_type`, `interest_1`, `interest_2`,
`interest_3`, `interest_4`, `interest_5`, `interest_flag`, `location_id`,
`payment_mode_id`, `payment_term`, `pricing_type`, `payment_code_id`, `account_set_id`,
`interest_profile_id`, `statement`)
SELECT
    NAMECUST name
    ,IDCUST code
    ,CODEPSTL postal_code
    ,TEXTPHON1 phone
    ,EMAIL1 email
    ,null fax
    ,TEXTSTRE1 note1
    ,TEXTSTRE2 note2
    ,TEXTSTRE3 note3
    ,SWACTV is_active
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(DATELASTMN,'%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
    ,@company_id company_id
    ,null country_id
    ,(CASE WHEN CODECURN='DOS'
      THEN (SELECT id FROM currencies_currency WHERE code='SGD')
      ELSE (SELECT id FROM currencies_currency WHERE code=CODECURN)
      END) currency_id
    ,(select id from taxes_tax WHERE
        tax_group_id = (SELECT id FROM taxes_taxgroup WHERE
            CODE = CODETAXGRP  and
            transaction_type =1 and -- TAX_TRX_TYPES_DICT['Sales'] --
            company_id=@company_id)
        and number = TAXSTTS1
        and company_id=@company_id) tax_id
    ,NAMECITY address
    ,0 accode_ar
    ,0 accode_bnk
    ,0 accode_chr
    ,0 accode_exc
    ,0 accode_int
    ,0 accode_sal
    ,0 center_ar
    ,0 center_bnk
    ,0 center_chr
    ,0 center_exc
    ,0 center_int
    ,0 center_sal
    ,AMTCRLIMT credit_limit
    ,0 customer_type
    ,0 interest_1
    ,0 interest_2
    ,0 interest_3
    ,0 interest_4
    ,0 interest_5
    ,0 interest_flag
    ,null location_id
    ,null payment_mode_id
    ,(SELECT SUBSTRING( CODETERM, 1, 2 )) payment_term
    ,0 pricing_type
    ,(select id from accounting_paymentcode
        where code= PAYMCODE
        and source_type='AR'
        and company_id=@company_id) payment_code_id
    ,(SELECT id from accounts_accountset
        where code = IDACCTSET
        and company_id = @company_id
     ) account_set_id
    ,(SELECT id from accounts_accountset
        where code = IDSVCCHRG
        and company_id = @company_id
     ) interest_profile_id
    ,null statement
FROM ikari_db_sage300.arcus;

# INSERT accounting_fiscalcalendar
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_fiscalcalendar $$
CREATE PROCEDURE insert_fiscalcalendar(in year_from varchar(4), in year_to varchar(4), in company int)
BEGIN
  DECLARE year_from_int int;
  DECLARE year_to_int int;

  DECLARE bndate1 int;
  DECLARE bndate2 int;
  DECLARE bndate3 int;
  DECLARE bndate4 int;
  DECLARE bndate5 int;
  DECLARE bndate6 int;
  DECLARE bndate7 int;
  DECLARE bndate8 int;
  DECLARE bndate9 int;
  DECLARE bndate10 int;
  DECLARE bndate11 int;
  DECLARE bndate12 int;
  DECLARE endate1 int;
  DECLARE endate2 int;
  DECLARE endate3 int;
  DECLARE endate4 int;
  DECLARE endate5 int;
  DECLARE endate6 int;
  DECLARE endate7 int;
  DECLARE endate8 int;
  DECLARE endate9 int;
  DECLARE endate10 int;
  DECLARE endate11 int;
  DECLARE endate12 int;
  DECLARE statADJ int;
  DECLARE statCLS int;
  DECLARE rowCount int;

  SET year_from_int = CAST(year_from AS UNSIGNED);
  SET year_to_int = CAST(year_to AS UNSIGNED);


  DELETE FROM `accounting_fiscalcalendar` WHERE company_id=company;

  loop_tahun:  LOOP
    IF  year_from_int > year_to_int THEN
      LEAVE  loop_tahun;
    END  IF;

        SELECT bgndate1, bgndate2, bgndate3, bgndate4, bgndate5, bgndate6, bgndate7, bgndate8, bgndate9, bgndate10, bgndate11, bgndate12,
              enddate1, enddate2, enddate3, enddate4, enddate5, enddate6, enddate7, enddate8, enddate9, enddate10, enddate11, enddate12, statusadj, statuscls
        INTO
              bndate1, bndate2, bndate3, bndate4, bndate5, bndate6, bndate7, bndate8, bndate9, bndate10, bndate11, bndate12,
              endate1, endate2, endate3, endate4, endate5, endate6, endate7, endate8, endate9, endate10, endate11, endate12, statADJ, statCLS
        FROM `ikari_db_sage300`.`csfsc` WHERE `FSCYEAR`=CAST(year_from_int AS CHAR) AND `ACTIVE`=1;

        SELECT FOUND_ROWS() INTO rowCount;

        IF rowCount=1 THEN
          INSERT INTO accounting_fiscalcalendar (`fiscal_year`, `period`, `start_date`, `end_date`, `is_ap_locked`, `is_ar_locked`, `is_gl_locked`, `is_bank_locked`, `create_date`, `update_date`, `update_by`, `is_hidden`, `company_id`, `is_ic_locked`, `is_sp_locked`, `is_adj_locked`, `is_cls_locked`)
          VALUES
            (CAST(year_from_int AS CHAR),1,date_format(bndate1,'%Y-%m-%d'),date_format(endate1,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),2,date_format(bndate2,'%Y-%m-%d'),date_format(endate2,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),3,date_format(bndate3,'%Y-%m-%d'),date_format(endate3,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),4,date_format(bndate4,'%Y-%m-%d'),date_format(endate4,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),5,date_format(bndate5,'%Y-%m-%d'),date_format(endate5,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),6,date_format(bndate6,'%Y-%m-%d'),date_format(endate6,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),7,date_format(bndate7,'%Y-%m-%d'),date_format(endate7,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),8,date_format(bndate8,'%Y-%m-%d'),date_format(endate8,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),9,date_format(bndate9,'%Y-%m-%d'),date_format(endate9,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),10,date_format(bndate10,'%Y-%m-%d'),date_format(endate10,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),11,date_format(bndate11,'%Y-%m-%d'),date_format(endate11,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1)),
            (CAST(year_from_int AS CHAR),12,date_format(bndate12,'%Y-%m-%d'),date_format(endate12,'%Y-%m-%d'),0,0,0,0,now(),now(),NULL,0,company,0,0,if(statADJ=1,0,1),if(statCLS=1,0,1));
        END IF;

    SET year_from_int = year_from_int + 1;
    ITERATE  loop_tahun;
  END LOOP loop_tahun;

END $$
DELIMITER ;

call insert_fiscalcalendar('2000', '2021',@company_id);


# UPDATE accounting_fiscalcalendar
DELIMITER $$
DROP PROCEDURE IF EXISTS update_fiscalcalendar $$
CREATE PROCEDURE update_fiscalcalendar(in year_from varchar(4), in year_to varchar(4), in company int)
BEGIN
  DECLARE year_from_int int;
  DECLARE year_to_int int;

  DECLARE stat1 int;
  DECLARE stat2 int;
  DECLARE stat3 int;
  DECLARE stat4 int;
  DECLARE stat5 int;
  DECLARE stat6 int;
  DECLARE stat7 int;
  DECLARE stat8 int;
  DECLARE stat9 int;
  DECLARE stat10 int;
  DECLARE stat11 int;
  DECLARE stat12 int;
  DECLARE rowCount int;


  SET year_from_int = CAST(year_from AS UNSIGNED);
  SET year_to_int = CAST(year_to AS UNSIGNED);

  loop_tahun:  LOOP
    IF  year_from_int > year_to_int THEN
      LEAVE  loop_tahun;
    END  IF;
        /* AP */
        SELECT status1, status2, status3, status4, status5, status6, status7, status8, status9, status10, status11, status12
        INTO
              stat1, stat2, stat3, stat4, stat5, stat6, stat7, stat8, stat9, stat10, stat11, stat12
        FROM `ikari_db_sage300`.`csfscst` WHERE `FSCYEAR`=CAST(year_from_int AS CHAR) AND `PGMID`='AP';

        SELECT FOUND_ROWS() INTO rowCount;

        IF rowCount=1 THEN
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat1=1,0,1) WHERE `company_id`=company AND `period`=1 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat2=1,0,1) WHERE `company_id`=company AND `period`=2 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat3=1,0,1) WHERE `company_id`=company AND `period`=3 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat4=1,0,1) WHERE `company_id`=company AND `period`=4 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat5=1,0,1) WHERE `company_id`=company AND `period`=5 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat6=1,0,1) WHERE `company_id`=company AND `period`=6 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat7=1,0,1) WHERE `company_id`=company AND `period`=7 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat8=1,0,1) WHERE `company_id`=company AND `period`=8 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat9=1,0,1) WHERE `company_id`=company AND `period`=9 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat10=1,0,1) WHERE `company_id`=company AND `period`=10 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat11=1,0,1) WHERE `company_id`=company AND `period`=11 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ap_locked` = if(stat12=1,0,1) WHERE `company_id`=company AND `period`=12 AND `fiscal_year`=CAST(year_from_int AS CHAR);
        END IF;

        /* AR */
        SELECT status1, status2, status3, status4, status5, status6, status7, status8, status9, status10, status11, status12
        INTO
              stat1, stat2, stat3, stat4, stat5, stat6, stat7, stat8, stat9, stat10, stat11, stat12
        FROM `ikari_db_sage300`.`csfscst` WHERE `FSCYEAR`=CAST(year_from_int AS CHAR) AND `PGMID`='AR';

        SELECT FOUND_ROWS() INTO rowCount;

        IF rowCount=1 THEN
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat1=1,0,1) WHERE `company_id`=company AND `period`=1 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat2=1,0,1) WHERE `company_id`=company AND `period`=2 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat3=1,0,1) WHERE `company_id`=company AND `period`=3 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat4=1,0,1) WHERE `company_id`=company AND `period`=4 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat5=1,0,1) WHERE `company_id`=company AND `period`=5 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat6=1,0,1) WHERE `company_id`=company AND `period`=6 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat7=1,0,1) WHERE `company_id`=company AND `period`=7 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat8=1,0,1) WHERE `company_id`=company AND `period`=8 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat9=1,0,1) WHERE `company_id`=company AND `period`=9 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat10=1,0,1) WHERE `company_id`=company AND `period`=10 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat11=1,0,1) WHERE `company_id`=company AND `period`=11 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_ar_locked` = if(stat12=1,0,1) WHERE `company_id`=company AND `period`=12 AND `fiscal_year`=CAST(year_from_int AS CHAR);
        END IF;

        /* GL */
        SELECT status1, status2, status3, status4, status5, status6, status7, status8, status9, status10, status11, status12
        INTO
              stat1, stat2, stat3, stat4, stat5, stat6, stat7, stat8, stat9, stat10, stat11, stat12
        FROM `ikari_db_sage300`.`csfscst` WHERE `FSCYEAR`=CAST(year_from_int AS CHAR) AND `PGMID`='GL';

        SELECT FOUND_ROWS() INTO rowCount;

        IF rowCount=1 THEN
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat1=1,0,1) WHERE `company_id`=company AND `period`=1 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat2=1,0,1) WHERE `company_id`=company AND `period`=2 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat3=1,0,1) WHERE `company_id`=company AND `period`=3 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat4=1,0,1) WHERE `company_id`=company AND `period`=4 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat5=1,0,1) WHERE `company_id`=company AND `period`=5 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat6=1,0,1) WHERE `company_id`=company AND `period`=6 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat7=1,0,1) WHERE `company_id`=company AND `period`=7 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat8=1,0,1) WHERE `company_id`=company AND `period`=8 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat9=1,0,1) WHERE `company_id`=company AND `period`=9 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat10=1,0,1) WHERE `company_id`=company AND `period`=10 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat11=1,0,1) WHERE `company_id`=company AND `period`=11 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_gl_locked` = if(stat12=1,0,1) WHERE `company_id`=company AND `period`=12 AND `fiscal_year`=CAST(year_from_int AS CHAR);
        END IF;

        /* BANK */
        SELECT status1, status2, status3, status4, status5, status6, status7, status8, status9, status10, status11, status12
        INTO
              stat1, stat2, stat3, stat4, stat5, stat6, stat7, stat8, stat9, stat10, stat11, stat12
        FROM `ikari_db_sage300`.`csfscst` WHERE `FSCYEAR`=CAST(year_from_int AS CHAR) AND `PGMID`='BK';

        SELECT FOUND_ROWS() INTO rowCount;

        IF rowCount=1 THEN
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat1=1,0,1) WHERE `company_id`=company AND `period`=1 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat2=1,0,1) WHERE `company_id`=company AND `period`=2 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat3=1,0,1) WHERE `company_id`=company AND `period`=3 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat4=1,0,1) WHERE `company_id`=company AND `period`=4 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat5=1,0,1) WHERE `company_id`=company AND `period`=5 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat6=1,0,1) WHERE `company_id`=company AND `period`=6 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat7=1,0,1) WHERE `company_id`=company AND `period`=7 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat8=1,0,1) WHERE `company_id`=company AND `period`=8 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat9=1,0,1) WHERE `company_id`=company AND `period`=9 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat10=1,0,1) WHERE `company_id`=company AND `period`=10 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat11=1,0,1) WHERE `company_id`=company AND `period`=11 AND `fiscal_year`=CAST(year_from_int AS CHAR);
          UPDATE accounting_fiscalcalendar
            SET `is_bank_locked` = if(stat12=1,0,1) WHERE `company_id`=company AND `period`=12 AND `fiscal_year`=CAST(year_from_int AS CHAR);
        END IF;

    SET year_from_int = year_from_int + 1;
    ITERATE  loop_tahun;
  END LOOP loop_tahun;

END $$
DELIMITER ;

call update_fiscalcalendar('2000', '2021',@company_id);


# INSERT update_fiscalcalendar for S&P if there is
DELIMITER $$
DROP PROCEDURE IF EXISTS update_fiscalcalendar_sp $$
CREATE PROCEDURE update_fiscalcalendar_sp(in year_from varchar(4), in year_to varchar(4), in company int)
BEGIN
  DECLARE year_from_int int;
  DECLARE year_to_int int;
  DECLARE period_month int;
  DECLARE company_month int;
  DECLARE company_year int;

  SET year_from_int = CAST(year_from AS UNSIGNED);
  SET year_to_int = CAST(year_to AS UNSIGNED);

  SELECT current_period_month, current_period_year INTO company_month, company_year FROM companies_company WHERE id = company;

  loop_tahun:  LOOP
    IF  year_from_int > year_to_int THEN
      LEAVE  loop_tahun;
    END  IF;

        SET period_month = 1;
        loop_insert: LOOP
          IF period_month > 12 THEN
            LEAVE loop_insert;
          END IF;

          IF year_from_int = company_year AND period_month >= company_month THEN
            UPDATE `accounting_fiscalcalendar`
            SET `is_ic_locked`=0, `is_sp_locked`=0
            WHERE `company_id`=company AND `period`=period_month AND `fiscal_year`=CAST(year_from_int AS CHAR);

          ELSEIF year_from_int > company_year THEN
            UPDATE `accounting_fiscalcalendar`
            SET `is_ic_locked`=0, `is_sp_locked`=0
            WHERE `company_id`=company AND `period`=period_month AND `fiscal_year`=CAST(year_from_int AS CHAR);

          ELSE
            UPDATE `accounting_fiscalcalendar`
            SET `is_ic_locked`=1, `is_sp_locked`=1
            WHERE `company_id`=company AND `period`=period_month AND `fiscal_year`=CAST(year_from_int AS CHAR);
          END IF;

          SET period_month = period_month + 1;
          ITERATE  loop_insert;
        END LOOP loop_insert;

    SET year_from_int = year_from_int + 1;
    ITERATE  loop_tahun;
  END LOOP loop_tahun;

END $$
DELIMITER ;

call update_fiscalcalendar_sp('2000', '2021', @company_id);
# END INSERT accounting_fiscalcalendar



# INSERT empty accounts_accounthistory
delimiter $$
DROP PROCEDURE IF EXISTS insert_accounthistory $$
CREATE PROCEDURE insert_accounthistory(in year_from varchar(4), in company int)
BEGIN

DECLARE year_to varchar(4);
DECLARE year_from_int int;
DECLARE year_to_int int;
DECLARE exit_loop INT DEFAULT FALSE;
DECLARE account_id int;
DECLARE functional_currency_id int;
DECLARE cursor_count int DEFAULT 0;
DECLARE index_count int DEFAULT 1;
DECLARE account_cursor CURSOR FOR
  SELECT id FROM accounts_account WHERE company_id=company;
DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

SET year_to = YEAR(now());
SET year_from_int = CAST(year_from AS UNSIGNED);
SET year_to_int = CAST(year_to AS UNSIGNED)+2;

SELECT currency_id FROM companies_company WHERE id=company INTO functional_currency_id;

loop_tahun:  LOOP
 IF  year_from_int > year_to_int THEN
  LEAVE  loop_tahun;
 END  IF;

 OPEN account_cursor;
 select FOUND_ROWS() into cursor_count;
 account_loop: LOOP
    FETCH account_cursor INTO account_id;
    IF index_count > cursor_count THEN
      CLOSE account_cursor;
      LEAVE account_loop;
    END IF;

    INSERT INTO `accounts_accounthistory` (`period_month`, `period_year`, `period_date`, `source_debit_amount`, `source_credit_amount`, `source_net_change`, `source_begin_balance`, `source_end_balance`, `functional_debit_amount`, `functional_credit_amount`, `functional_net_change`, `functional_begin_balance`, `functional_end_balance`, `create_date`, `update_date`, `update_by`, `is_hidden`, `account_id`, `functional_currency_id`, `source_currency_id`, `company_id`)
    VALUES
      ('1',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-01-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('2',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-02-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('3',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-03-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('4',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-04-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('5',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-05-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('6',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-06-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('7',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-07-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('8',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-08-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('9',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-09-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('10',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-10-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('11',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-11-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('12',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-12-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('ADJ',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-12-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company),
      ('CLS',CAST(year_from_int AS CHAR),LAST_DAY(CONCAT(CAST(year_from_int AS CHAR),'-12-01')),0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,now(),now(),NULL,0,account_id,functional_currency_id,NULL,company);

    SET index_count := index_count + 1;
  END LOOP account_loop;

 SET index_count = 1;
 SET year_from_int = year_from_int + 1;
 ITERATE  loop_tahun;

END LOOP loop_tahun;

END $$
delimiter ;

call insert_accounthistory('2011',@company_id);
# END INSERT empty accounts_accounthistory



# Add spesific account into accounts_accounthistory
delimiter $$
DROP PROCEDURE IF EXISTS add_accounthistory $$
CREATE PROCEDURE add_accounthistory(in acctid varchar(4), in currid int, in s_amt DECIMAL(20,6), in f_amt DECIMAL(20,6), in company int)
BEGIN

DECLARE year_from, year_to, company_currency int;

SELECT currency_id FROM companies_company WHERE id=company INTO company_currency;
SELECT CAST(max(period_year) AS UNSIGNED)+1 FROM accounts_accounthistory
WHERE account_id=acctid
AND source_currency_id=currid
AND company_id=company INTO year_from;
SELECT CAST(max(period_year) AS UNSIGNED) FROM accounts_accounthistory WHERE company_id=company INTO year_to;

loop_tahun:  LOOP
  IF  year_from > year_to THEN
    LEAVE  loop_tahun;
  END  IF;

  INSERT INTO `accounts_accounthistory` (`period_month`, `period_year`, `period_date`, `source_debit_amount`, `source_credit_amount`, `source_net_change`, `source_begin_balance`, `source_end_balance`, `functional_debit_amount`, `functional_credit_amount`, `functional_net_change`, `functional_begin_balance`, `functional_end_balance`, `create_date`, `update_date`, `update_by`, `is_hidden`, `account_id`, `functional_currency_id`, `source_currency_id`, `company_id`)
  VALUES
    ('1',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-01-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('2',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-02-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('3',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-03-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('4',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-04-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('5',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-05-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('6',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-06-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('7',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-07-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('8',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-08-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('9',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-09-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('10',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-10-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('11',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-11-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('12',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-12-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('ADJ',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-12-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('CLS',CAST(year_from AS CHAR),LAST_DAY(CONCAT(CAST(year_from AS CHAR),'-12-01')),0.000000,0.000000,0.000000,s_amt,s_amt,0.000000,0.000000,0.000000,f_amt,f_amt,now(),now(),NULL,0,acctid,company_currency,currid,company);

 SET year_from = year_from + 1;
 ITERATE  loop_tahun;

END LOOP loop_tahun;

END $$
delimiter ;
# End Add spesific account into accounts_accounthistory



# fill accounts_accounthistory with data from glafs
delimiter $$
DROP PROCEDURE IF EXISTS fill_accounthistory $$
CREATE PROCEDURE fill_accounthistory(in company int)
BEGIN

DECLARE year, currid, currcode, acctid, acctcode TEXT;
DECLARE s_openbal,netprd1,netprd2,netprd3,netprd4,netprd5,netprd6,netprd7,netprd8,netprd9,
        netprd10,netprd11,netprd12,netprd13,netprd14,netprd15,f_openbal,fnetprd1,fnetprd2,
        fnetprd3,fnetprd4,fnetprd5,fnetprd6,fnetprd7,fnetprd8,fnetprd9,fnetprd10,fnetprd11,
        fnetprd12,fnetprd13,fnetprd14,fnetprd15 DECIMAL(20,6) DEFAULT 0;
DECLARE s_begin1,s_begin2,s_begin3,s_begin4,s_begin5,s_begin6,s_begin7,s_begin8,s_begin9,
        s_begin10,s_begin11,s_begin12,s_begin14,s_begin15,f_begin1,f_begin2,f_begin3,f_begin4,
        f_begin5,f_begin6,f_begin7,f_begin8,f_begin9,f_begin10,f_begin11,f_begin12,
        f_begin14,f_begin15 DECIMAL(20,6) DEFAULT 0;
DECLARE exit_loop INT DEFAULT FALSE;
DECLARE company_currency INT;
DECLARE cursor_count INT DEFAULT 0;
DECLARE index_count INT DEFAULT 1;
DECLARE acct_hist CURSOR FOR
  SELECT acct_hist.*
    ,(CASE
        WHEN acct_hist.currency='DOS'
          THEN (SELECT id FROM currencies_currency WHERE code='SGD')
          ELSE (SELECT id FROM currencies_currency WHERE code=acct_hist.currency)
      END) currency_id
  FROM (
  SELECT s.*
    ,CAST(COALESCE(e.openbal,f.openbal,0) AS DECIMAL(20,6)) fopenbal
    ,CAST(COALESCE(e.netperd1,f.netperd1,0) AS DECIMAL(20,6)) fnetperd1
    ,CAST(COALESCE(e.netperd2,f.netperd2,0) AS DECIMAL(20,6)) fnetperd2
    ,CAST(COALESCE(e.netperd3,f.netperd3,0) AS DECIMAL(20,6)) fnetperd3
    ,CAST(COALESCE(e.netperd4,f.netperd4,0) AS DECIMAL(20,6)) fnetperd4
    ,CAST(COALESCE(e.netperd5,f.netperd5,0) AS DECIMAL(20,6)) fnetperd5
    ,CAST(COALESCE(e.netperd6,f.netperd6,0) AS DECIMAL(20,6)) fnetperd6
    ,CAST(COALESCE(e.netperd7,f.netperd7,0) AS DECIMAL(20,6)) fnetperd7
    ,CAST(COALESCE(e.netperd8,f.netperd8,0) AS DECIMAL(20,6)) fnetperd8
    ,CAST(COALESCE(e.netperd9,f.netperd9,0) AS DECIMAL(20,6)) fnetperd9
    ,CAST(COALESCE(e.netperd10,f.netperd10,0) AS DECIMAL(20,6)) fnetperd10
    ,CAST(COALESCE(e.netperd11,f.netperd11,0) AS DECIMAL(20,6)) fnetperd11
    ,CAST(COALESCE(e.netperd12,f.netperd12,0) AS DECIMAL(20,6)) fnetperd12
    ,CAST(COALESCE(e.netperd13,f.netperd13,0) AS DECIMAL(20,6)) fnetperd13
    ,CAST(COALESCE(e.netperd14,f.netperd14,0) AS DECIMAL(20,6)) fnetperd14
    ,CAST(COALESCE(e.netperd15,f.netperd15,0) AS DECIMAL(20,6)) fnetperd15
  FROM
  (SELECT afs.fscsyr period_year
    ,afs.fscscurn currency
    ,aa.id account_id
    ,afs.acctid account_code
    ,IFNULL(openbal,0) openbal
    ,IFNULL(netperd1,0) netperd1
    ,IFNULL(netperd2,0) netperd2
    ,IFNULL(netperd3,0) netperd3
    ,IFNULL(netperd4,0) netperd4
    ,IFNULL(netperd5,0) netperd5
    ,IFNULL(netperd6,0) netperd6
    ,IFNULL(netperd7,0) netperd7
    ,IFNULL(netperd8,0) netperd8
    ,IFNULL(netperd9,0) netperd9
    ,IFNULL(netperd10,0) netperd10
    ,IFNULL(netperd11,0) netperd11
    ,IFNULL(netperd12,0) netperd12
    ,IFNULL(netperd13,0) netperd13
    ,IFNULL(netperd14,0) netperd14
    ,IFNULL(netperd15,0) netperd15
  FROM ikari_db_sage300.glafs afs
  LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
  LEFT OUTER JOIN accounts_account aa ON afs.acctid=aa.code AND aa.company_id=company
  WHERE afs.fscsdsg='A'
  /* AND afs.activitysw>0 */
  AND amf.mcsw=1
  AND afs.curntype='S') s
  LEFT OUTER JOIN (
    SELECT afs.fscsyr,afs.acctid,afs.fscscurn
      ,IFNULL(openbal,0) openbal
      ,IFNULL(netperd1,0) netperd1
      ,IFNULL(netperd2,0) netperd2
      ,IFNULL(netperd3,0) netperd3
      ,IFNULL(netperd4,0) netperd4
      ,IFNULL(netperd5,0) netperd5
      ,IFNULL(netperd6,0) netperd6
      ,IFNULL(netperd7,0) netperd7
      ,IFNULL(netperd8,0) netperd8
      ,IFNULL(netperd9,0) netperd9
      ,IFNULL(netperd10,0) netperd10
      ,IFNULL(netperd11,0) netperd11
      ,IFNULL(netperd12,0) netperd12
      ,IFNULL(netperd13,0) netperd13
      ,IFNULL(netperd14,0) netperd14
      ,IFNULL(netperd15,0) netperd15
      FROM ikari_db_sage300.glafs afs
      LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
      where afs.fscsdsg='A'
      AND afs.activitysw>0
      and amf.mcsw=1
      and afs.curntype='E'
    ) e ON s.period_year=e.fscsyr AND s.account_code=e.acctid AND s.currency=e.fscscurn
  LEFT OUTER JOIN (
    SELECT afs.fscsyr,afs.acctid,afs.fscscurn
      ,IFNULL(openbal,0) openbal
      ,IFNULL(netperd1,0) netperd1
      ,IFNULL(netperd2,0) netperd2
      ,IFNULL(netperd3,0) netperd3
      ,IFNULL(netperd4,0) netperd4
      ,IFNULL(netperd5,0) netperd5
      ,IFNULL(netperd6,0) netperd6
      ,IFNULL(netperd7,0) netperd7
      ,IFNULL(netperd8,0) netperd8
      ,IFNULL(netperd9,0) netperd9
      ,IFNULL(netperd10,0) netperd10
      ,IFNULL(netperd11,0) netperd11
      ,IFNULL(netperd12,0) netperd12
      ,IFNULL(netperd13,0) netperd13
      ,IFNULL(netperd14,0) netperd14
      ,IFNULL(netperd15,0) netperd15
      FROM ikari_db_sage300.glafs afs
      LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
      where afs.fscsdsg='A'
      AND afs.activitysw>0
      and amf.mcsw=1
      and afs.curntype='F'
    ) f ON s.period_year=f.fscsyr AND s.account_code=f.acctid AND s.currency=f.fscscurn
  UNION ALL
  SELECT dos.period_year,dos.currency,dos.account_id,dos.account_code
        ,0 openbal,0 netperd1,0 netperd2,0 netperd3,0 netperd4,0 netperd5,0 netperd6,0 netperd7
        ,0 netperd8,0 netperd9,0 netperd10,0 netperd11,0 netperd12,0 netperd13,0 netperd14,0 netperd15
        ,dos.openbal fopenbal,dos.netperd1 fnetperd1,dos.netperd2 fnetperd2,dos.netperd3 fnetperd3
        ,dos.netperd4 fnetperd4,dos.netperd5 fnetperd5,dos.netperd6 fnetperd6,dos.netperd7 fnetperd7
        ,dos.netperd8 fnetperd8,dos.netperd9 fnetperd9,dos.netperd10 fnetperd10,dos.netperd11 fnetperd11
        ,dos.netperd12 fnetperd12,dos.netperd13 fnetperd13,dos.netperd14 fnetperd14,dos.netperd15 fnetperd15
  FROM (SELECT afs.fscsyr period_year
        ,afs.fscscurn currency
        ,aa.id account_id
        ,afs.acctid account_code
        ,IFNULL(openbal,0) openbal
        ,IFNULL(netperd1,0) netperd1
        ,IFNULL(netperd2,0) netperd2
        ,IFNULL(netperd3,0) netperd3
        ,IFNULL(netperd4,0) netperd4
        ,IFNULL(netperd5,0) netperd5
        ,IFNULL(netperd6,0) netperd6
        ,IFNULL(netperd7,0) netperd7
        ,IFNULL(netperd8,0) netperd8
        ,IFNULL(netperd9,0) netperd9
        ,IFNULL(netperd10,0) netperd10
        ,IFNULL(netperd11,0) netperd11
        ,IFNULL(netperd12,0) netperd12
        ,IFNULL(netperd13,0) netperd13
        ,IFNULL(netperd14,0) netperd14
        ,IFNULL(netperd15,0) netperd15
      FROM ikari_db_sage300.glafs afs
      LEFT OUTER JOIN accounts_account aa ON afs.acctid=aa.code AND aa.company_id=company
      WHERE afs.fscsdsg='A'
      AND afs.activitysw>0
      AND afs.fscscurn=(SELECT CASE WHEN code='SGD' THEN 'DOS' ELSE code END FROM currencies_currency WHERE id = (SELECT currency_id FROM companies_company WHERE id=company))
      AND afs.curntype='F') dos
  WHERE NOT EXISTS
    ( SELECT s.* FROM
        (SELECT afs.fscsyr period_year
          ,afs.fscscurn currency
          ,aa.id account_id
        FROM ikari_db_sage300.glafs afs
        LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
        LEFT OUTER JOIN accounts_account aa ON afs.acctid=aa.code AND aa.company_id=company
        WHERE afs.fscsdsg='A'
        AND afs.activitysw>0
        AND amf.mcsw=1
        AND afs.curntype='S') s
        WHERE dos.period_year=s.period_year and dos.currency=s.currency and dos.account_id=s.account_id)
  ) acct_hist
  ORDER BY acct_hist.account_code,acct_hist.period_year,acct_hist.currency;

DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

SELECT currency_id FROM companies_company WHERE id=company INTO company_currency;

OPEN acct_hist;
SELECT FOUND_ROWS() INTO cursor_count;
glafs_loop: LOOP
  FETCH acct_hist INTO year,currcode,acctid,acctcode,s_openbal,
        netprd1,netprd2,netprd3,netprd4,netprd5,netprd6,netprd7,
        netprd8,netprd9,netprd10,netprd11,netprd12,netprd13,netprd14,netprd15,
        f_openbal,fnetprd1,fnetprd2,fnetprd3,fnetprd4,fnetprd5,fnetprd6,fnetprd7,
        fnetprd8,fnetprd9,fnetprd10,fnetprd11,fnetprd12,fnetprd13,fnetprd14,fnetprd15,currid;
  IF index_count > cursor_count THEN
    CLOSE acct_hist;
    LEAVE glafs_loop;
  END IF;

  DELETE FROM accounts_accounthistory WHERE company_id=company AND account_id=acctid AND period_year>=year AND source_currency_id = currid;

  DELETE FROM accounts_accounthistory WHERE company_id=company AND account_id=acctid AND period_year>=year AND source_currency_id is NULL;

  SET s_begin1 := s_openbal;
  SET s_begin2 := s_begin1+netprd1;
  SET s_begin3 := s_begin2+netprd2;
  SET s_begin4 := s_begin3+netprd3;
  SET s_begin5 := s_begin4+netprd4;
  SET s_begin6 := s_begin5+netprd5;
  SET s_begin7 := s_begin6+netprd6;
  SET s_begin8 := s_begin7+netprd7;
  SET s_begin9 := s_begin8+netprd8;
  SET s_begin10 := s_begin9+netprd9;
  SET s_begin11 := s_begin10+netprd10;
  SET s_begin12 := s_begin11+netprd11;
  SET s_begin14 := s_begin12+netprd12+netprd13;
  SET s_begin15 := s_begin14+netprd14;

  SET f_begin1 := f_openbal;
  SET f_begin2 := f_begin1+fnetprd1;
  SET f_begin3 := f_begin2+fnetprd2;
  SET f_begin4 := f_begin3+fnetprd3;
  SET f_begin5 := f_begin4+fnetprd4;
  SET f_begin6 := f_begin5+fnetprd5;
  SET f_begin7 := f_begin6+fnetprd6;
  SET f_begin8 := f_begin7+fnetprd7;
  SET f_begin9 := f_begin8+fnetprd8;
  SET f_begin10 := f_begin9+fnetprd9;
  SET f_begin11 := f_begin10+fnetprd10;
  SET f_begin12 := f_begin11+fnetprd11;
  SET f_begin14 := f_begin12+fnetprd12+fnetprd13;
  SET f_begin15 := f_begin14+fnetprd14;

  INSERT INTO `accounts_accounthistory` (`period_month`, `period_year`, `period_date`,
    `source_debit_amount`, `source_credit_amount`, `source_net_change`, `source_begin_balance`,
    `source_end_balance`, `functional_debit_amount`, `functional_credit_amount`, `functional_net_change`,
    `functional_begin_balance`, `functional_end_balance`, `create_date`, `update_date`, `update_by`,
    `is_hidden`, `account_id`, `functional_currency_id`, `source_currency_id`, `company_id`)
  VALUES
    ('1',year,LAST_DAY(CONCAT(year,'-01-01')),
      0, 0, netprd1, s_begin1, s_begin1+netprd1,
      0, 0, fnetprd1, f_begin1, f_begin1+fnetprd1,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('2',year,LAST_DAY(CONCAT(year,'-02-01')),
      0, 0, netprd2, s_begin2, s_begin2+netprd2,
      0, 0, fnetprd2, f_begin2, f_begin2+fnetprd2,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('3',year,LAST_DAY(CONCAT(year,'-03-01')),
      0, 0, netprd3, s_begin3, s_begin3+netprd3,
      0, 0, fnetprd3, f_begin3, f_begin3+fnetprd3,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('4',year,LAST_DAY(CONCAT(year,'-04-01')),
      0, 0, netprd4, s_begin4, s_begin4+netprd4,
      0, 0, fnetprd4, f_begin4, f_begin4+fnetprd4,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('5',year,LAST_DAY(CONCAT(year,'-05-01')),
      0, 0, netprd5, s_begin5, s_begin5+netprd5,
      0, 0, fnetprd5, f_begin5, f_begin5+fnetprd5,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('6',year,LAST_DAY(CONCAT(year,'-06-01')),
      0, 0, netprd6, s_begin6, s_begin6+netprd6,
      0, 0, fnetprd6, f_begin6, f_begin6+fnetprd6,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('7',year,LAST_DAY(CONCAT(year,'-07-01')),
      0, 0, netprd7, s_begin7, s_begin7+netprd7,
      0, 0, fnetprd7, f_begin7, f_begin7+fnetprd7,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('8',year,LAST_DAY(CONCAT(year,'-08-01')),
      0, 0, netprd8, s_begin8, s_begin8+netprd8,
      0, 0, fnetprd8, f_begin8, f_begin8+fnetprd8,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('9',year,LAST_DAY(CONCAT(year,'-09-01')),
      0, 0, netprd9, s_begin9, s_begin9+netprd9,
      0, 0, fnetprd9, f_begin9, f_begin9+fnetprd9,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('10',year,LAST_DAY(CONCAT(year,'-10-01')),
      0, 0, netprd10, s_begin10, s_begin10+netprd10,
      0, 0, fnetprd10, f_begin10, f_begin10+fnetprd10,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('11',year,LAST_DAY(CONCAT(year,'-11-01')),
      0, 0, netprd11, s_begin11, s_begin11+netprd11,
      0, 0, fnetprd11, f_begin11, f_begin11+fnetprd11,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('12',year,LAST_DAY(CONCAT(year,'-12-01')),
      0, 0, netprd12, s_begin12, s_begin12+netprd12,
      0, 0, fnetprd12, f_begin12, f_begin12+fnetprd12,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('ADJ',year,LAST_DAY(CONCAT(year,'-12-01')),
      0, 0, netprd14, s_begin14, s_begin14+netprd14,
      0, 0, fnetprd14, f_begin14, f_begin14+fnetprd14,
      now(),now(),NULL,0,acctid,company_currency,currid,company),
    ('CLS',year,LAST_DAY(CONCAT(year,'-12-01')),
      0, 0, netprd15, s_begin15, s_begin15+netprd15,
      0, 0, fnetprd15, f_begin15, f_begin15+fnetprd15,
      now(),now(),NULL,0,acctid,company_currency,currid,company);

    call add_accounthistory(acctid,currid,s_begin15+netprd15,f_begin15+fnetprd15,company);

  SET index_count := index_count + 1;
END LOOP glafs_loop;

END $$
delimiter ;

call fill_accounthistory(@company_id);
# END fill accounts_accounthistory with data from glafs

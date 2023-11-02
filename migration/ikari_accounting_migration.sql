SET @company_id=8; -- Ikari --
SET FOREIGN_KEY_CHECKS=0;

SHOW WARNINGS;

delimiter $$
DROP PROCEDURE IF EXISTS change_customer_code$$
create procedure change_customer_code(in code1 varchar(20), in code2 varchar(20))
begin

UPDATE customers_customer set
	code := code2
where company_id=@company_id and `code`=code1 ;

end$$
delimiter ;


delimiter $$
DROP PROCEDURE IF EXISTS change_supplier_code$$
create procedure change_supplier_code(in code1 varchar(20), in code2 varchar(20))
begin

UPDATE suppliers_supplier set
	code := code2
where company_id=@company_id and `code`=code1 ;

end$$
delimiter ;


call change_customer_code('AINA-Y', 'ALEYEN');
call change_customer_code('ARAI-Y', 'APCYEN');
call change_customer_code('BMS-U', 'BMNUS$');
call change_customer_code('CROWN-Y', 'CFSPYEN');
call change_customer_code('CROWN-U', 'CFSUS$');
call change_customer_code('CROWN-S', 'CFSPS$');
call change_customer_code('GSK-U', 'GSKUS$');
call change_customer_code('GSKS-U', 'GSKSUS');
call change_customer_code('HOEI-U', 'HOEUS$');
call change_customer_code('IKARIH-Y', 'IKAYEN');
call change_customer_code('JPK-Y', 'JAPYEN');
call change_customer_code('JOLSON-Y', 'JOLYEN');
call change_customer_code('VICTOR-U', 'JVCUS$');
call change_customer_code('KIM-S', 'KLOUS$');
call change_customer_code('LIVELY-S', 'LIVES$');
call change_customer_code('MINGGE-S', 'MINGS$');
call change_customer_code('MPS-U', 'MSPUS$');
call change_customer_code('MPS-Y', 'MSPYEN');
call change_customer_code('MUTO-U', 'MUTOUS');
call change_customer_code('NIDAI-U', 'NSSUS$');
call change_customer_code('NITTO-S', 'NITTS$');
call change_customer_code('NITTO-U', 'NDKUS$');
call change_customer_code('OLIP-S', 'OLIPS$');
call change_customer_code('PCM-U', 'PNSMUS');
call change_customer_code('RE&S-S', 'R&ESS$');
call change_customer_code('SANKO-S', 'SANKS$');
call change_customer_code('SEMB-S', 'SEMBS$');
call change_customer_code('SENT-S', 'SENTS$');
call change_customer_code('SHIN-S', 'SMWAS$');
call change_customer_code('SHINJ-S', 'SHWJS$');
call change_customer_code('SUNT-U', 'SUNTS$');
call change_customer_code('TAKATA-U', 'TAKUS$');
call change_customer_code('YET-U', 'YETUS$');


call change_supplier_code('ABE-U', 'ABEHUS');
call change_supplier_code('CKD-S', 'CKDSS$');
call change_supplier_code('CROWN-U', 'CFSUS$');
call change_supplier_code('CROWN-Y', 'CROWNYEN');
call change_supplier_code('DICK-Y', 'DICYEN');
call change_supplier_code('ETO-U', 'ETOUS$');
call change_supplier_code('FDK-U', 'FDKUS$');
call change_supplier_code('GAO-S', 'GAOSS$');
call change_supplier_code('GP-S', 'GPMSS$');
call change_supplier_code('HAN-U', 'HTSUS$');
call change_supplier_code('HICHEM-U', 'HICUS$');
call change_supplier_code('HUPHONG-S', 'HUPHS$');
call change_supplier_code('IIDA-Y', 'IT1YEN');
call change_supplier_code('IKARIH-U', 'IKAUS$');
call change_supplier_code('JSB-U', 'JSBUS$');
call change_supplier_code('VICTOR-U', 'JVCYEN');
call change_supplier_code('KMM-U', 'KATOMUS$');
call change_supplier_code('KMS-U', 'KATUS$');
call change_supplier_code('KCK-Y', 'KCKYEN');
call change_supplier_code('KCK-B', 'KCKBHT');
call change_supplier_code('KONDO-U', 'KONUS$');
call change_supplier_code('LIAN-S', 'LIANS$');
call change_supplier_code('MIKURO-U', 'MIKUS$');
call change_supplier_code('NATURAL-S', 'NATFS$');
call change_supplier_code('NHK-S', 'NHKIS$');
call change_supplier_code('NICHI-U', 'NE1US$');
call change_supplier_code('NICHI-S', 'NICHS$');
call change_supplier_code('NIDEC-U', 'NIDUS$');
call change_supplier_code('NITTO-U', 'NDSUS$');
call change_supplier_code('NITTO-S', 'NITTS$');
call change_supplier_code('OLIP-S', 'OLI1SG');
call change_supplier_code('OLIP-U', 'OLI1US');
call change_supplier_code('PGJ-Y', 'PGJYEN');
call change_supplier_code('SANKO-U', 'SPSUS$');
call change_supplier_code('SSS-R', 'SHARMB');
call change_supplier_code('TRUST-U', 'TRUUS$');
call change_supplier_code('SHIN-Y', 'STKYEN');
call change_supplier_code('SIFLEX-U', 'SIFUS$');
call change_supplier_code('SOHRYU-U', 'SOHUS$');
call change_supplier_code('SUNWA-U', 'SU1US$');
call change_supplier_code('SUNLIT-Y', 'SULYEN');
call change_supplier_code('SUNT-U', 'SUNUS$');
call change_supplier_code('SUNT-Y', 'SUNYEN');
call change_supplier_code('SWS-U', 'SWSUS$');
call change_supplier_code('TAN-U', 'TANUS$');
call change_supplier_code('YAAN-U', 'YAAUS$');
call change_supplier_code('TOWA-Y', 'TSCYEN');
call change_supplier_code('TOWA-B', 'TSTBAT');
call change_supplier_code('TOWA-U', 'TOWUS$');
call change_supplier_code('VICTOR-Y', 'VCOUS$');
call change_supplier_code('VEPL-S', 'VICTS$');
call change_supplier_code('WAH-U', 'WAHSUS');
call change_supplier_code('WITSF-Y', 'WDIYEN');
call change_supplier_code('WITSF-U', 'WITSUS$');
call change_supplier_code('XEROM-U', 'XERUS$');
call change_supplier_code('YET-U', 'YETUS$');

# DELETE ACC TRANSACTIONS DATA
delete from transactions_transactionmethod
where company_id=@company_id;
ALTER TABLE transactions_transactionmethod AUTO_INCREMENT = 1;

INSERT INTO transactions_transactionmethod (
    `name`, `code`, `is_debit`, `is_credit`, `company_id`, `is_hidden`, `update_by`, `create_date`, `update_date`)
VALUES
    ('Check', 'CHQ', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Chash', 'CSH', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Credit', 'CRE', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Letter of Credit', 'L/C', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('B/L at sight', 'B/L', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Telegraphic Transfer', 'TT', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('INTERNAL TRANSFER', 'TRF', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01');


delete from transactions_transaction
where company_id=@company_id;
ALTER TABLE transactions_transaction AUTO_INCREMENT = 1;

delete from accounting_journal
where company_id=@company_id;
ALTER TABLE accounting_journal AUTO_INCREMENT = 1;

delete from accounting_batch
where company_id=@company_id;
ALTER TABLE accounting_batch AUTO_INCREMENT = 1;

delete from accounting_paymentcode
where company_id=@company_id;
ALTER TABLE accounting_paymentcode AUTO_INCREMENT = 1;

delete from accounting_aroptions
where company_id=@company_id;
ALTER TABLE accounting_aroptions AUTO_INCREMENT = 1;

delete from accounting_apoptions
where company_id=@company_id;
ALTER TABLE accounting_apoptions AUTO_INCREMENT = 1;

delete from accounts_accountcurrency
where account_id in (select id from accounts_account where company_id=@company_id);
delete from accounts_accountcurrency
where name in (select code from accounts_account where company_id=@company_id);
ALTER TABLE accounts_accountcurrency AUTO_INCREMENT = 1;

delete from accounts_accounthistory
where company_id=@company_id;
ALTER TABLE accounts_accounthistory AUTO_INCREMENT = 1;

delete from accounts_accountset
where company_id=@company_id;
ALTER TABLE accounts_accountset AUTO_INCREMENT = 1;

delete from accounts_revaluationcode
where company_id=@company_id;
ALTER TABLE accounts_revaluationcode AUTO_INCREMENT = 1;

delete from accounting_revaluationdetails
where posting_id in (select id from accounting_revaluationlogs where company_id=@company_id);
ALTER TABLE accounting_revaluationdetails AUTO_INCREMENT = 1;

delete from accounting_revaluationlogs
where company_id=@company_id;
ALTER TABLE accounting_revaluationlogs AUTO_INCREMENT = 1;

delete from banks_bank
where company_id=@company_id;
ALTER TABLE banks_bank AUTO_INCREMENT = 1;

delete from accounts_distributioncode
where company_id=@company_id;
ALTER TABLE accounts_distributioncode AUTO_INCREMENT = 1;

delete from accounts_reportgroup
where company_id=@company_id;
ALTER TABLE accounts_reportgroup AUTO_INCREMENT = 1;

delete from accounts_account
where company_id=@company_id;
ALTER TABLE accounts_account AUTO_INCREMENT = 1;

delete from accounts_accounttype
where company_id is null; -- this line is spesific for crown only
delete from accounts_accounttype
where company_id=@company_id;
ALTER TABLE accounts_accounttype AUTO_INCREMENT = 1;

delete from companies_costcenters
where company_id=@company_id;
ALTER TABLE companies_costcenters AUTO_INCREMENT = 1;


#insert accounts_accounttype
INSERT INTO accounts_accounttype(
`name`, `code`, `is_debit`, `is_credit`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `category`)
SELECT
    ACCTGRPDES name
    ,ACCTGRPCOD code
    ,0 is_debit
    ,0 is_credit
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,1 category
FROM ikari_db_sage300.glacgrp;


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
CREATE PROCEDURE add_accounthistory(in acctid char(11), in currid int, in s_amt DECIMAL(20,6), in f_amt DECIMAL(20,6), in company int)
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

set autocommit = 0;

##################################################################################
#                            03_Transaction.sql BEGIN                            #
##################################################################################

-- insert accounting_batch --
SELECT max(id) into @row_number FROM accounting_batch;
SELECT (@row_number:=@row_number + 1) AS id, t0.*, 0 flag
INTO OUTFILE '/Users/ikari_migration_files/batch_1.txt'
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
FROM `ikari_db_sage300`.`glbctl`) t0;-- AR Receipt and Adjustment Batches --
/* LEFT JOIN (
    SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
    FROM `ikari_db_sage300`.`gljed` GROUP BY `ikari_db_sage300`.`gljed`.`BATCHNBR`
) AS `gljed` ON `gljed`.`BATCHNBR` = `ikari_db_sage300`.`glbctl`.`BATCHID`
WHERE `gljed`.`SRCETYPE` = 'JE'; -- Code Payment Type -- */

LOAD DATA INFILE '/Users/ikari_migration_files/batch_1.txt' INTO TABLE accounting_batch
   FIELDS TERMINATED BY ',' ENCLOSED BY '"'
   LINES TERMINATED BY '\n';

COMMIT;



#Insert accounting_journal
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_1.txt'
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
      and company_id=@company_id LIMIT 1) tax_id
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
    ,j.FISCPER perd_month
    ,j.FISCYR perd_year
    ,0 is_reversed_entry
    ,0 flag
    ,0 adjustment_amount
    ,0 discount_amount
    ,NULL transaction_id
    ,0 is_auto_reversed_entry
    ,0 rev_perd_month
    ,0 rev_perd_year
    ,0 customer_unapplied
    ,0 receipt_unapplied
    ,NULL fully_paid_date
    ,0 error_entry
    ,0 reverse_reconciliation
    ,j.RATERC tax_exchange_rate
FROM ikari_db_sage300.apibh j -- AP Invoices --
JOIN ikari_db_sage300.apobl bl
  ON j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.txttrxtype
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN suppliers_supplier s
  ON j.IDVEND = s.code aND s.company_id = @company_id
LEFT JOIN taxes_taxgroup tg
  ON tg.code IN ('GSTDOS', 'GSTSGD') AND transaction_type = 2 AND tg.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id AND aas.type=2
UNION
SELECT CNTENTR code
    ,TEXTRMIT name
    ,4 journal_type -- TRANSACTION_TYPES)['AP Payment'] --
    ,(CASE
        WHEN j.RMITTYPE = 1 THEN '9'
        WHEN j.RMITTYPE = 4 THEN '12'
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
        9
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) currency_id
    ,NULL customer_id
    ,NULL order_id
    ,s.id supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id = tg.id
        and number = TAXCLASS1
        and company_id=@company_id LIMIT 1) tax_id
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
    ,pc.id payment_code_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
      (select id from currencies_currency where code='SGD')
      ELSE
      (select id from currencies_currency where code=CODECURNBC)
      END) payment_currency_id
    ,TXTRMITREF reference
    ,NULL source_type
    ,(CASE
        when j.RMITTYPE=1 then '1'
        when j.RMITTYPE=4 then '2'
        else '0'
     END) transaction_type
    ,bnk.id bank_id
    ,0 outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,CNTPAYMENT payment_number
    ,if(j.RMITTYPE=1,NULL,IDINVCMTCH) invoice_number
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
    ,j.FISCPER perd_month
    ,j.FISCYR perd_year
    ,0 is_reversed_entry
    ,0 flag
    ,0 adjustment_amount
    ,0 discount_amount
    ,NULL transaction_id
    ,0 is_auto_reversed_entry
    ,0 rev_perd_month
    ,0 rev_perd_year
    ,0 customer_unapplied
    ,0 receipt_unapplied
    ,NULL fully_paid_date
    ,0 error_entry
    ,0 reverse_reconciliation
    ,j.RATERC tax_exchange_rate
FROM ikari_db_sage300.aptcr j
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 4 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN suppliers_supplier s
  ON j.IDVEND = s.code AND s.company_id = @company_id
LEFT JOIN taxes_taxgroup tg
  ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type = 2 AND tg.company_id = @company_id
LEFT JOIN banks_bank bnk
  ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id AND aas.type=2
LEFT JOIN accounting_paymentcode pc
  ON j.PAYMCODE = pc.code and pc.source_type='2' and pc.company_id=@company_id
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
        9
      ELSE
        (select id from currencies_currency where code=j.CODECURN)
      END) currency_id
    ,c.id customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id = tg.id
        and number = j.TAXSTTS1
        and company_id=@company_id LIMIT 1) tax_id
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
    ,j.FISCPER perd_month
    ,j.FISCYR perd_year
    ,0 is_reversed_entry
    ,0 flag
    ,0 adjustment_amount
    ,0 discount_amount
    ,NULL transaction_id
    ,0 is_auto_reversed_entry
    ,0 rev_perd_month
    ,0 rev_perd_year
    ,0 customer_unapplied
    ,0 receipt_unapplied
    ,NULL fully_paid_date
    ,0 error_entry
    ,0 reverse_reconciliation
    ,j.RATERC tax_exchange_rate
FROM ikari_db_sage300.aribh j
JOIN ikari_db_sage300.arobl bl
  ON j.cntbtch = bl.cntbtch AND j.cntitem=bl.cntitem and j.TEXTTRX = bl.trxtypetxt
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 1 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN taxes_taxgroup tg
  ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type = 1 AND tg.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id AND aas.type=1
LEFT JOIN customers_customer c
  ON j.IDCUST = c.code AND c.company_id = @company_id
UNION
SELECT CNTITEM code
    ,TEXTRMIT name
    ,3 journal_type -- TRANSACTION_TYPES['AR Receipt'] --
    ,(CASE
        WHEN j.RMITTYPE = 1 THEN '7'
        WHEN j.RMITTYPE = 5 THEN '11'
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
        9
      ELSE
        (select id from currencies_currency where code=CODECURNBC)
      END) currency_id
    ,c.id customer_id
    ,NULL order_id
    ,NULL supplier_id
    ,(select id from taxes_tax
        WHERE tax_group_id = tg.id
        and number = TAXCLASS1
        and company_id=@company_id LIMIT 1) tax_id
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
    ,pc.id payment_code_id
    ,(CASE WHEN CODECURNBC='DOS' THEN
      (select id from currencies_currency where code='SGD')
      ELSE
      (select id from currencies_currency where code=CODECURNBC)
      END) payment_currency_id
    ,TXTRMITREF reference
    ,NULL source_type
    ,(CASE
        when j.RMITTYPE=1 then '1'
        when j.RMITTYPE=5 then '2'
        else '0'
     END) transaction_type
    ,bnk.id bank_id
    ,REMUNAPLTC outstanding_amount
    ,0 paid_amount
    ,0 is_fully_paid
    ,NULL payment_number
    ,if(j.RMITTYPE=1,NULL,IDINVCMTCH) invoice_number
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
    ,j.FISCPER perd_month
    ,j.FISCYR perd_year
    ,0 is_reversed_entry
    ,0 flag
    ,0 adjustment_amount
    ,0 discount_amount
    ,NULL transaction_id
    ,0 is_auto_reversed_entry
    ,0 rev_perd_month
    ,0 rev_perd_year
    ,j.REMUNAPLTC customer_unapplied
    ,j.REMUNAPL receipt_unapplied
    ,NULL fully_paid_date
    ,0 error_entry
    ,0 reverse_reconciliation
    ,j.RATERC tax_exchange_rate
FROM ikari_db_sage300.artcr j
LEFT JOIN accounting_batch ab
  ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 3 AND ab.company_id = @company_id AND ab.document_type <> '10'
LEFT JOIN taxes_taxgroup tg
  ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type = 1 AND tg.company_id = @company_id
LEFT JOIN banks_bank bnk
  ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
LEFT JOIN accounts_accountset aas
  ON j.IDACCTSET = aas.code AND aas.company_id = @company_id AND aas.type=1
LEFT JOIN customers_customer c
  ON j.IDCUST = c.code AND c.company_id = @company_id
LEFT JOIN accounting_paymentcode pc
  ON j.CODEPAYM = pc.code and pc.source_type='1' and pc.company_id=@company_id
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
    `ab`.`status` AS `status`, -- STATUS_TYPE_DICT --
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
    '' AS `reference`,
    CONCAT( 'GL-',`j`.`SRCETYPE`) AS `source_type`,
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
    'GL' AS `source_ledger`,
    NULL AS `orig_exch_rate`,
    NULL AS `orig_exch_rate_fk_id`,
    0 AS `is_auto_reverse`,
    NULL AS `reverse_to_period`,
    NULL AS `reverse_to_period_val`,
    0 AS `is_rev_do`,
    `j`.`FSCSPERD` AS `perd_month`,
    `j`.`FSCSYR` AS `perd_year`,
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year,
    0 customer_unapplied,
    0 receipt_unapplied,
    NULL fully_paid_date,
    `j`.`ERRENTRY` AS error_entry,
    0 reverse_reconciliation,
    0 tax_exchange_rate
FROM `ikari_db_sage300`.`gljeh` AS `j`
LEFT JOIN accounting_batch ab
  ON j.BATCHID = ab.batch_no AND ab.batch_type = 5 AND ab.company_id = @company_id AND ab.document_type <> '10'
WHERE `j`.`SRCETYPE` IN ('JE', 'RV', 'RE')) t0;

DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_1.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum1.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;



#insert transactions_transaction (AP ENTRY)  -- 53696
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_1.txt'
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
            THEN 9
          ELSE
            (SELECT id from currencies_currency
            where code=(select CURNCODE from ikari_db_sage300.apven where VENDORID = j.idvend))
      END) currency_id
      ,NULL pair_id
      ,aj.id journal_id
      ,(SELECT id from taxes_tax
        where tax_group_id = tg.id
        and number = t.TAXCLASS1
        and company_id=@company_id LIMIT 1) tax_id
      ,t.AMTTOTTAX tax_amount
      ,t.AMTDIST total_amount
      ,ad.id distribution_code_id -- DIS_CODE_TYPE['AP Distribution Code'] --
      ,NULL description
      ,j.EXCHRATEHC exchange_rate
      ,t.AMTDISTHC functional_amount
      ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
      ,date_format(j.DATERATE ,'%Y-%m-%d') rate_date
      ,NULL reference
      ,NULL source_type
      ,(CASE
            WHEN LENGTH(j.invcapplto) > 0 THEN
                (SELECT id FROM accounting_journal
                  WHERE journal_type = 2
                    AND document_type IN ('1','2','3')
                    AND document_number = j.invcapplto
                    AND supplier_id = s.id
                    AND company_id=@company_id)
            ELSE
                NULL
        END) related_invoice_id
      ,t.SWTAXINCL1 is_tax_include
      ,0 is_tax_transaction
      ,if(j.TEXTTRX=3,'2','1')
      ,0 is_report,0 is_clear_tax
      ,0 adjamt, 0 discamt
      ,t.BASETAX1 base_tax_amount
  FROM ikari_db_sage300.apibd t
  JOIN ikari_db_sage300.apibh j
    ON t.cntbtch=j.cntbtch AND t.cntitem=j.cntitem
  LEFT JOIN suppliers_supplier s
    ON j.IDVEND = s.code AND s.company_id = @company_id
  LEFT JOIN accounts_account aa
    ON REPLACE(t.IDGLACCT,'-','') = aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.cntbtch=ab.batch_no AND ab.company_id=@company_id AND ab.batch_type=2 AND ab.document_type <> '10'
  LEFT JOIN accounting_journal aj
    ON ab.id = aj.batch_id AND t.cntitem=aj.code AND aj.company_id=@company_id
  LEFT JOIN taxes_taxgroup tg
    ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type=2 AND tg.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDIST = ad.code AND ad.type=2 AND ad.company_id=@company_id
) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_1.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert transactions_transaction (AR Entry)
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_2.txt'
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
      ,kurs.id2 currency_id
      ,NULL pair_id
      ,aj.id journal_id
      ,tx.id tax_id
      ,t.TOTTAX tax_amount
      ,(t.AMTTXBL+t.TOTTAX) total_amount
      ,ad.id distribution_code_id -- DIS_CODE_TYPE['AR Distribution Code'] --
      ,NULL description
      ,j.EXCHRATEHC exchange_rate
      ,(t.TXBSE1HC+t.TXAMT1HC) functional_amount
      ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`
      ,date_format(j.DATERATE ,'%Y-%m-%d') rate_date
      ,NULL reference
      ,NULL source_type
      ,(CASE
            WHEN LENGTH(j.invcapplto) > 0 THEN
                (SELECT id FROM accounting_journal
                  WHERE journal_type = 1
                    AND document_type IN ('1','2','3')
                    AND document_number = j.invcapplto
                    AND customer_id = cus.id
                    AND company_id=@company_id)
            ELSE
                NULL
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
    ON j.IDCUST=cus.code AND cus.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON REPLACE(t.IDACCTREV, '-', '') = aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id AND ab.document_type <> '10'
  LEFT JOIN accounting_journal aj
    ON ab.id = aj.batch_id AND t.cntitem=aj.code AND aj.company_id=@company_id
  LEFT JOIN taxes_taxgroup tg
    ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type=1 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax tx
    ON tg.id = tx.tax_group_id AND t.TAXSTTS1=tx.number AND tx.company_id=@company_id
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDIST = ad.code AND ad.type=1 AND ad.company_id=@company_id
  LEFT JOIN ikari_db_sage300.arcus ac
    ON j.IDCUST = ac.IDCUST
  LEFT JOIN cur_kurs kurs
    ON ac.CODECURN = kurs.code
 ) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_2.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert AP Payment (Payment)
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_3.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT DISTINCT
        0 is_credit_transaction
        ,1 is_debit_transaction
        ,abs(t.AMTPAYM) amount
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
        ,0 tax_amount
        ,abs(t.AMTPAYM) total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,tx.RATEEXCHTC exchange_rate
        ,abs(t.AMTPAYMHC) functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`
        ,date_format(tx.RATEDATETC ,'%Y-%m-%d') rate_date
        ,NULL reference
        ,NULL source_type
        ,(SELECT id FROM accounting_journal
           WHERE journal_type = 2
           AND document_type IN ('1','2','3')
           AND document_number = t.IDINVC
           AND supplier_id = s.id
           AND company_id=@company_id) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'1' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
        ,t.amtadjtot adjustment_amount
        ,t.amtdisctot discount_amount
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
   ON t.IDVEND = s.code AND s.company_id = @company_id
 LEFT JOIN accounts_accountset aas
   ON s.account_set_id = aas.id AND aas.company_id = @company_id AND aas.type=2
 LEFT JOIN banks_bank bnk
   ON j.IDBANK = bnk.code AND bnk.company_id = @company_id
 LEFT JOIN cur_kurs kurs
   ON j.CODECURN = kurs.code
WHERE t.batchtype = 'PY') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_3.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;



#insert AR receipt (receipt)
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_4.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT   1 is_credit_transaction
        ,0 is_debit_transaction
        ,abs(t.AMTPAYM) amount
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
        ,0 tax_amount
        ,abs(t.AMTPAYM) total_amount
        ,NULL distribution_code_id
        ,NULL description
        ,tx.RATEEXCHTC exchange_rate
        ,abs(t.AMTPAYMHC) functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`
        ,date_format(tx.RATEDATETC,'%Y-%m-%d') rate_date
        ,NULL reference
        ,NULL source_type
        ,(SELECT id FROM accounting_journal
           WHERE journal_type IN (1, 3)
           AND document_type IN ('1','2','3','5','7')
           AND document_number = t.IDINVC
           AND customer_id = cus.id
           AND company_id=@company_id) related_invoice_id
        ,0 is_tax_include
        ,0 is_tax_transaction
        ,'2' functional_balance_type
        ,0 is_report
        ,0 is_clear_tax
        ,t.amtadjtot adjustment_amount
        ,t.amtdisctot discount_amount
        ,0 base_tax_amount
 FROM ikari_db_sage300.artcr j
RIGHT JOIN ikari_db_sage300.artcp t
   ON j.codepymtyp=t.codepaym AND j.cntbtch=t.cntbtch AND j.CNTITEM=t.CNTITEM -- add codepymtyp=codepaym to have this query use an index
 LEFT JOIN customers_customer cus
   ON j.IDCUST=cus.code and cus.company_id=@company_id
 LEFT JOIN accounts_accountset aas
   ON cus.account_set_id = aas.id AND aas.company_id=@company_id AND aas.type=1
 LEFT JOIN accounting_batch ab
   ON j.cntbtch=ab.batch_no AND ab.batch_type=3 AND ab.company_id=@company_id
 LEFT JOIN accounting_journal aj
   ON ab.id=aj.batch_id AND j.CNTITEM=aj.code AND aj.company_id=@company_id
 LEFT JOIN ikari_db_sage300.arpjh tx
   ON t.CODEPAYM=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.CNTITEM=tx.cntitem
 LEFT JOIN cur_kurs kurs
   ON j.CODECURN = kurs.code
WHERE t.codepaym = 'CA') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_4.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;




#insert AP payment (Misc. Payment)  -- 24583
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_5.txt'
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
        ,kurs.id2 currency_id
        ,NULL pair_id
        ,aj.id AS `journal_id`
        ,tax.id tax_id
        ,t.TXTOTTC tax_amount
        ,t.AMTDISTTC total_amount
        ,ad.id distribution_code_id
        ,REPLACE(t.GLDESC,'"','''') description
        ,tx.RATEEXCHTC exchange_rate
        ,t.AMTDISTHC functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
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
    ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type=2 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax tax
    ON tg.id = tax.tax_group_id AND t.taxclass1=tax.number AND tax.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.cntbtch=ab.batch_no AND ab.batch_type=4 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND j.DOCNBR=aj.document_number AND j.TXTRMITREF=aj.reference AND aj.company_id=@company_id
  LEFT JOIN cur_kurs kurs
    ON j.CODECURN = kurs.code
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDISTCODE=ad.code AND ad.type=2 AND ad.company_id=@company_id) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_5.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert AR receipt (misc. receipt)  -- 1232
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_6.txt'
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
        ,kurs.id2 AS `currency_id`
        ,NULL pair_id
        ,aj.id journal_id
        ,ntax.id tax_id
        ,t.TXTOTTC tax_amount
        ,t.AMTDISTTC total_amount
        ,ad.id distribution_code_id
        ,REPLACE(t.GLDESC,'"','''') description
        ,tx.RATEEXCHTC exchange_rate
        ,t.AMTDISTHC functional_amount
        ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
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
    ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type=1 AND tg.company_id=@company_id
  LEFT JOIN taxes_tax ntax
    ON tg.id = ntax.tax_group_id AND otax.TAXCLASS1=ntax.number AND ntax.company_id=@company_id
  LEFT JOIN ikari_db_sage300.arpjh tx
    ON t.CODEPAYM=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.CNTITEM=tx.cntitem
  LEFT JOIN accounts_account aa
    ON REPLACE(t.idacct,'-','')=aa.description AND aa.company_id=@company_id
  LEFT JOIN cur_kurs kurs
    ON j.CODECURN = kurs.code
  LEFT JOIN accounts_distributioncode ad
    ON t.IDDISTCODE=ad.code AND ad.type=1 AND ad.company_id=@company_id) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_6.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


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
    ,ar.FISCPER perd_month
    ,ar.FISCYR perd_year
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


-- Sometime there are duplicate AR Misc transaction.
-- This script is to remove those
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



-- 1734
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_2.txt'
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
       ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) currency_id
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
       ,0 is_reversed_entry
       ,0 flag
       ,0 adjustment_amount
       ,0 discount_amount
       ,NULL transaction_id
       ,0 is_auto_reversed_entry
       ,0 rev_perd_month
       ,0 rev_perd_year
       ,0 customer_unapplied
       ,0 receipt_unapplied
       ,NULL fully_paid_date
       ,gl_crown.ERRENTRY error_entry
  FROM ikari_db_sage300.gljeh gl_crown
 RIGHT JOIN  ikari_db_sage300.glbctl gl_entry
    ON gl_crown.BATCHID = gl_entry.BATCHID
  LEFT JOIN accounting_batch ab
    ON gl_crown.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE gl_entry.BATCHTYPE IN ('1', '3', '4')
   AND gl_crown.SRCETYPE NOT IN ('JE', 'RV', 'RE')) t0;

DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_2.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum2.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum2.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;


-- 40618
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_8.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`
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
       ,aa.id account_id
       ,@company_id company_id
       ,NULL method_id
       ,NULL order_id
       ,kurs.id2 currency_id
       ,NULL pair_id
       ,aj.id journal_id
       ,NULL tax_id
       ,0 tax_amount
       ,replace(t.SCURNAMT , '-','') total_amount
       ,NULL distribution_code_id
       ,REPLACE(t.TRANSDESC,'"','''') description
       ,t.CONVRATE exchange_rate
       ,replace(t.TRANSAMT , '-','') functional_amount
       ,(SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) functional_currency_id
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE b.BATCHTYPE IN ('1', '3', '4')
   AND j.SRCETYPE NOT IN ('JE', 'RV', 'RE')) t0;
# END INSERT GL ENTRY


LOAD DATA INFILE '/Users/ikari_migration_files/trx_8.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL RV Journal  -- 1110
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_100.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  DISTINCT
        `j`.`BTCHENTRY` AS `code`,
        'Revaluation Entries' AS `name`,
        5 AS `journal_type`, -- TRANSACTION_TYPES)['GL'] --
        0 AS `document_type`, -- DOCUMENT_TYPE_DICT['Undefined'] --
        NULL AS `po_number`,
        NULL AS `order_number`,
        NULL AS `document_number`,
        DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `document_date`,
        NULL AS `posting_date`,
        `j`.`JRNLDR` AS `amount`,
        0 AS `tax_amount`,
        `j`.`JRNLDR` AS `total_amount`,
        ab.status AS `status`,
        DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
        DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `update_date`,
        NULL AS `update_by`,
        0 AS `is_hidden`,
        @company_id AS `company_id`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
        NULL AS `customer_id`,
        NULL AS `order_id`,
        NULL AS `supplier_id`,
        NULL AS `tax_id`,
        `j`.`JRNLDR` AS `document_amount`,
        DATE_FORMAT(`j`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
        1 AS `exchange_rate`,
        `j`.`JRNLDR` AS `original_amount`,
        NULL AS `original_currency_id`,
        NULL AS `payment_account_id`,
        0 AS `payment_amount`,
        0 AS `payment_check_number`,
        null AS `payment_code_id`,
        NULL AS `payment_currency_id`,
        '' AS `reference`,
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
        `j`.`FSCSPERD` AS `perd_month`,
        `j`.`FSCSYR` AS `perd_year`,
        0 is_reversed_entry,
        0 flag,
        0 adjustment_amount,
        0 discount_amount,
        NULL transaction_id,
        0 is_auto_reversed_entry,
        0 rev_perd_month,
        0 rev_perd_year,
        0 customer_unapplied,
        0 receipt_unapplied,
        NULL fully_paid_date,
        `j`.`ERRENTRY` AS error_entry
  FROM `ikari_db_sage300`.`gljeh` AS `j`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `j`.`BATCHID`
  LEFT JOIN accounting_batch ab
    ON j.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` = 'GL'
   AND `j`.`SRCETYPE` IN ('RV', 'RE')
   AND `b`.`BATCHSTAT` = '1'
   AND `b`.`BATCHTYPE` = '4'
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`) t0;

DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_100.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum1000.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum1000.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;


SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_3.txt'
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
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
        0 is_reversed_entry,
        0 flag,
        0 adjustment_amount,
        0 discount_amount,
        NULL transaction_id,
        0 is_auto_reversed_entry,
        0 rev_perd_month,
        0 rev_perd_year,
        0 customer_unapplied,
        0 receipt_unapplied,
        NULL fully_paid_date,
        0 error_entry
  FROM `ikari_db_sage300`.`glpjd` AS `j`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `j`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` = 'GL'
   AND `j`.`SRCETYPE` IN ('JE', 'RV', 'RE')
   AND `j`.`TRANSAMT` > 0
   AND `b`.`BATCHTYPE` = '4'
 GROUP BY `j`.`BATCHNBR`, `j`.`ENTRYNBR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_3.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum3.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum3.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;


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


#insert GL Entry  -- 20157
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_7.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.TRANSDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `j`.`SRCETYPE` IN ('JE', 'RV', 'RE')) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_7.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL RV Reverse Entry  -- 2282
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_1000.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT DISTINCT
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.TRANSDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`TRANSREF` AS `reference`,
        CONCAT('GL', '-', `j`.`SRCETYPE`) AS `source_type`,
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
    ON `j`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.status=1 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.JOURNALID=aj.code AND aj.company_id=@company_id
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `j`.`SRCETYPE` IN ('RV', 'RE')) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_1000.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_9.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('GL', '-', `j`.`SRCETYPE`) AS `source_type`,
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `j`.`SRCETYPE` IN ('JE', 'RV', 'RE')) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_9.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


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
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_4.txt'
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
    (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year,
    0 customer_unapplied,
    0 receipt_unapplied,
    NULL fully_paid_date,
    `j`.`ERRENTRY` AS error_entry
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
   AND `t`.`JNLDTLREF` <> 'REVERSING ENTRY'
   AND `b`.`BATCHTYPE` = '2'
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_4.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum4.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum4.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;




SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_5.txt'
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
    (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
    0 is_reversed_entry,
    0 flag,
    0 adjustment_amount,
    0 discount_amount,
    NULL transaction_id,
    0 is_auto_reversed_entry,
    0 rev_perd_month,
    0 rev_perd_year,
    0 customer_unapplied,
    0 receipt_unapplied,
    NULL fully_paid_date,
    0 error_entry
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `t`.`SRCELEDGER` IN ('AR', 'AP')
   AND `t`.`SRCETYPE` = 'GL'
   AND `t`.`TRANSAMT` > 0
   AND `t`.`JNLDTLREF` = 'REVERSING ENTRY'
   AND `b`.`BATCHTYPE` = '2'
 GROUP BY `t`.`BATCHNBR`, `t`.`ENTRYNBR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_5.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum5.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum5.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;



#insert GL CR/DB Journal
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_6.txt'
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
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
        0 is_reversed_entry,
        0 flag,
        0 adjustment_amount,
        0 discount_amount,
        NULL transaction_id,
        0 is_auto_reversed_entry,
        0 rev_perd_month,
        0 rev_perd_year,
        0 customer_unapplied,
        0 receipt_unapplied,
        NULL fully_paid_date,
        `j`.`ERRENTRY` AS error_entry
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
   AND `b`.`BATCHTYPE` = '2'
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_6.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum6.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum6.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;


SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_7.txt'
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
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
        0 is_reversed_entry,
        0 flag,
        0 adjustment_amount,
        0 discount_amount,
        NULL transaction_id,
        0 is_auto_reversed_entry,
        0 rev_perd_month,
        0 rev_perd_year,
        0 customer_unapplied,
        0 receipt_unapplied,
        NULL fully_paid_date,
        `j`.`ERRENTRY` AS error_entry
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
   AND `b`.`BATCHTYPE` = '2'
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_7.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum7.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum7.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;




SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_8.txt'
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
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
        0 is_reversed_entry,
        0 flag,
        0 adjustment_amount,
        0 discount_amount,
        NULL transaction_id,
        0 is_auto_reversed_entry,
        0 rev_perd_month,
        0 rev_perd_year,
        0 customer_unapplied,
        0 receipt_unapplied,
        NULL fully_paid_date,
        `j`.`ERRENTRY` AS error_entry
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
   AND `b`.`BATCHTYPE` = '2'
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_8.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum8.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum8.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;


SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_9.txt'
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
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
        0 is_reversed_entry,
        0 flag,
        0 adjustment_amount,
        0 discount_amount,
        NULL transaction_id,
        0 is_auto_reversed_entry,
        0 rev_perd_month,
        0 rev_perd_year,
        0 customer_unapplied,
        0 receipt_unapplied,
        NULL fully_paid_date,
        `j`.`ERRENTRY` AS error_entry
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
   AND `b`.`BATCHTYPE` = '2'
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_9.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum9.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum9.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_10.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON aj0.batch_id = ab0.id AND ab0.company_id=@company_id AND ab0.batch_type = 5
          WHERE aj0.journal_type = 1
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id=@company_id) AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `j`.`BTCHENTRY`=`t`.`ENTRYNBR`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
  WHERE `t`.`SRCELEDGER` = 'AR'
    AND `t`.`SRCETYPE` = 'CR'
    AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_10.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;



#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_10_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON aj0.batch_id = ab0.id AND ab0.company_id=@company_id AND ab0.batch_type = 5
          WHERE aj0.journal_type = 1
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id=@company_id) AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `j`.`BTCHENTRY`=`t`.`ENTRYNBR`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
  WHERE `t`.`SRCELEDGER` = 'AR'
    AND `t`.`SRCETYPE` = 'DB'
    AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_10_1.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_11.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON aj0.batch_id = ab0.id AND ab0.company_id=@company_id AND ab0.batch_type = 5
          WHERE aj0.journal_type = 1
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id=@company_id) AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `j`.`BTCHENTRY`=`t`.`ENTRYNBR`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
  WHERE `t`.`SRCELEDGER` = 'AR'
    AND `t`.`SRCETYPE` = 'IN'
    AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_11.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_12.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON aj0.batch_id = ab0.id AND ab0.company_id=@company_id AND ab0.batch_type = 5
          WHERE aj0.journal_type = 1
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id=@company_id) AS `related_invoice_id`,
        0 AS `is_tax_include`,
        0 AS `is_tax_transaction`,
        IF(`t`.`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`,
        0 AS `is_report`,
        0 AS `is_clear_tax`
        ,0 adjamt, 0 discamt
        ,0 AS `base_tax_amount`
  FROM `ikari_db_sage300`.`glpjd` AS `t`
  LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `j`.`BTCHENTRY`=`t`.`ENTRYNBR`
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounts_account aa
    ON t.ACCTID=aa.description AND aa.company_id=@company_id
  LEFT JOIN accounting_batch ab
    ON t.BATCHNBR=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
  LEFT JOIN accounting_journal aj
    ON ab.id=aj.batch_id AND t.ENTRYNBR=aj.code AND aj.company_id=@company_id
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
  WHERE `t`.`SRCELEDGER` = 'AR'
    AND `t`.`SRCETYPE` = 'PY'
    AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_12.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_13.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON ab0.id = aj0.batch_id AND ab0.company_id = @company_id  AND ab0.batch_type = 5
          WHERE aj0.journal_type = 2
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id = @company_id) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'CR'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_13.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_13_1.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON ab0.id = aj0.batch_id AND ab0.company_id = @company_id  AND ab0.batch_type = 5
          WHERE aj0.journal_type = 2
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id = @company_id) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'DB'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_13_1.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_14.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON ab0.id = aj0.batch_id AND ab0.company_id = @company_id  AND ab0.batch_type = 5
          WHERE aj0.journal_type = 2
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id = @company_id) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'IN'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_14.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_15.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AP-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0
           JOIN accounting_batch ab0
             ON ab0.id = aj0.batch_id AND ab0.company_id = @company_id  AND ab0.batch_type = 5
          WHERE aj0.journal_type = 2
            AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
            AND aj0.document_number = t.JNLDTLREF
            AND aj0.company_id = @company_id) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON `t`.`SCURNCODE` = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'PY'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_15.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL RV Reverse Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_16.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        'AR-GL' AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0, accounting_batch ab0
        WHERE aj0.batch_id = ab0.id
          AND ab0.company_id = @company_id
          AND ab0.batch_type = 5
          AND t.JNLDTLDESC IS NOT NULL
          AND t.JNLDTLREF IS NOT NULL
          and aj0.name = t.JNLDTLDESC
          AND aj0.document_number = t.JNLDTLREF
          AND aj0.company_id = @company_id
          AND aj0.journal_type = 1) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AR'
   AND `t`.`SRCETYPE` = 'GL'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_16.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_17.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        'AP-GL' AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0, accounting_batch ab0
        WHERE aj0.batch_id = ab0.id
          AND ab0.company_id = @company_id
          AND ab0.batch_type = 5
          AND t.JNLDTLDESC IS NOT NULL
          AND t.JNLDTLREF IS NOT NULL
          and aj0.name = t.JNLDTLDESC
          AND aj0.document_number = t.JNLDTLREF
          AND aj0.company_id = @company_id
          AND aj0.journal_type = 2) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` = 'GL'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_17.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;

#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_18.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0, accounting_batch ab0
        WHERE aj0.batch_id = ab0.id
          AND ab0.company_id = @company_id
          AND ab0.batch_type = 5
          AND aj0.document_number = t.JNLDTLREF
          AND aj0.company_id = @company_id
          AND aj0.journal_type = 1
          AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
        ORDER BY aj0.id DESC LIMIT 1) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AR'
   AND `t`.`SRCETYPE` IN ('RD', 'AD')
   AND `b`.`BATCHTYPE` = '2') t0;

LOAD DATA INFILE '/Users/ikari_migration_files/trx_18.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_19.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0, accounting_batch ab0
        WHERE aj0.batch_id = ab0.id
          AND ab0.company_id = @company_id
          AND ab0.batch_type = 5
          AND aj0.document_number = t.JNLDTLREF
          AND aj0.company_id = @company_id
          AND aj0.journal_type = 1
          AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
        ORDER BY aj0.id DESC LIMIT 1) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `t`.`SRCELEDGER` = 'AP'
   AND `t`.`SRCETYPE` IN ('RD', 'AD')
   AND `b`.`BATCHTYPE` = '2') t0;

LOAD DATA INFILE '/Users/ikari_migration_files/trx_19.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;



##################################################################################################
# Additional journal UC                                                                          #
##################################################################################################

SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_GL_UC.txt'
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
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `currency_id`,
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
        0 is_reversed_entry,
        0 flag,
        0 adjustment_amount,
        0 discount_amount,
        NULL transaction_id,
        0 is_auto_reversed_entry,
        0 rev_perd_month,
        0 rev_perd_year,
        0 customer_unapplied,
        0 receipt_unapplied,
        NULL fully_paid_date,
        `j`.`ERRENTRY` AS error_entry
  FROM `ikari_db_sage300`.`gljeh` AS `j`
  LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t`
    ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY` AND t.SRCELEDGER = j.SRCELEDGER
  LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b`
    ON `b`.`BATCHID` = `t`.`BATCHNBR`
  LEFT JOIN accounting_batch ab
    ON j.BATCHID=ab.batch_no AND ab.batch_type=5 AND ab.company_id=@company_id
 WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
   AND `j`.`SRCETYPE` = 'UC'
   AND `t`.`TRANSAMT` > 0
   AND `b`.`BATCHTYPE` = '2'
 GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`) t0;


DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_GL_UC.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum_GL_UC.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum_GL_UC.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;



#insert GL CR/DB Entry
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_GL_UC.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_account`,
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
        aa.id AS `account_id`,
        @company_id AS `company_id`,
        NULL AS `method_id`,
        NULL AS `order_id`,
        kurs.id2 AS `currency_id`,
        NULL AS `pair_id`,
        aj.id AS `journal_id`,
        NULL AS `tax_id`,
        0 AS `tax_amount`,
        ABS(`t`.`SCURNAMT`) AS `total_amount`,
        NULL AS `distribution_code_id`,
        REPLACE(t.JNLDTLDESC,'"','''') description,
        `t`.`CONVRATE` AS `exchange_rate`,
        ABS(`t`.`TRANSAMT`) AS `functional_amount`,
        (SELECT `currency_id` FROM `companies_company` WHERE `id` = @company_id) AS `functional_currency_id`,
        DATE_FORMAT(`t`.`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
        `t`.`JNLDTLREF` AS `reference`,
        CONCAT('AR-', `t`.`SRCETYPE`) AS `source_type`,
        (SELECT aj0.id FROM accounting_journal aj0, accounting_batch ab0
        WHERE aj0.batch_id = ab0.id
          AND ab0.company_id = @company_id
          AND ab0.batch_type = 5
          AND aj0.document_number = t.JNLDTLREF
          AND aj0.company_id = @company_id
          AND aj0.journal_type = 1
          AND aj0.document_type = CASE WHEN `t`.`TRANSAMT` < 0 THEN '3' ELSE '2' END
        ORDER BY aj0.id DESC LIMIT 1) AS `related_invoice_id`,
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
  LEFT JOIN cur_kurs kurs
    ON t.SCURNCODE = kurs.code
 WHERE `t`.`SRCELEDGER` IN ('AR','AP')
   AND `t`.`SRCETYPE` = 'UC'
   AND `b`.`BATCHTYPE` = '2') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_GL_UC.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;

###################################################################################################
# End Additional Journal UC                                                                       #
###################################################################################################



########################################## CAUTION !!!!############################################
# CODES BELOW MUST BE RUN AFTER ALL QUERIES COMPLETED, OTHERWISE THERE WILL BE DUPLICATES RECORDS #

-- insert accounting_batch --
/* SELECT max(id) into @row_number FROM accounting_batch;
SELECT (@row_number:=@row_number + 1) AS id, t0.*, 0 flag
INTO OUTFILE '/Users/ikari_migration_files/batch_AP_AR_AD.txt'
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
where CODEPYMTYP = 'AD') t0; */

/* LOAD DATA INFILE '/Users/ikari_migration_files/batch_AP_AR_AD.txt' INTO TABLE accounting_batch
   FIELDS TERMINATED BY ',' ENCLOSED BY '"'
   LINES TERMINATED BY '\n';

COMMIT; */


-- insert journal AR-AD and AP-AD
SELECT max(id) into @row_number FROM accounting_journal;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/journal_AR_AP_AD.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT j.CNTENTR code
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
      and company_id=@company_id LIMIT 1) tax_id
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
    ,j.FISCPER perd_month
    ,j.FISCYR perd_year
    ,0 is_reversed_entry
    ,0 flag
    ,0 adjustment_amount
    ,0 discount_amount
    ,NULL transaction_id
    ,0 is_auto_reversed_entry
    ,0 rev_perd_month
    ,0 rev_perd_year
    ,0 customer_unapplied
    ,0 receipt_unapplied
    ,NULL fully_paid_date
    ,0 error_entry
  FROM ikari_db_sage300.aptcr j
  LEFT JOIN ikari_db_sage300.aptcp jp
    ON j.btchtype = jp.batchtype AND j.CNTBTCH = jp.CNTBTCH AND j.cntentr = jp.cntrmit
  LEFT JOIN accounting_batch ab
    /* ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id AND ab.document_type='10' */
    ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id
  LEFT JOIN suppliers_supplier s
    ON j.IDVEND = s.code AND s.company_id = @company_id
  LEFT JOIN taxes_taxgroup tg
    ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type = 2 AND tg.company_id = @company_id
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
            and company_id=@company_id LIMIT 1) tax_id
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
        ,j.FISCPER perd_month
        ,j.FISCYR perd_year
        ,0 is_reversed_entry
        ,0 flag
        ,0 adjustment_amount
        ,0 discount_amount
        ,NULL transaction_id
        ,0 is_auto_reversed_entry
        ,0 rev_perd_month
        ,0 rev_perd_year
        ,0 customer_unapplied
        ,0 receipt_unapplied
        ,NULL fully_paid_date
        ,0 error_entry
  FROM ikari_db_sage300.artcr j
  LEFT JOIN ikari_db_sage300.ARTCP jp
    ON j.CODEPYMTYP = jp.codepaym AND j.CNTBTCH = jp.CNTBTCH AND j.cntitem = jp.cntitem
  LEFT JOIN accounting_batch ab
    /* ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 1 AND ab.company_id = @company_id AND ab.document_type='10' */
    ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 1 AND ab.company_id = @company_id
  LEFT JOIN taxes_taxgroup tg
    ON tg.code IN ('GSTDOS', 'GSTSGD') AND tg.transaction_type = 1 AND tg.company_id = @company_id
  LEFT JOIN accounts_accountset aas
    ON j.IDACCTSET = aas.code AND aas.company_id = @company_id AND aas.type=1
  LEFT JOIN customers_customer c
    ON j.IDCUST = c.code AND c.company_id = @company_id
 WHERE j.CODEPYMTYP = 'AD') t0;

DROP TABLE IF EXISTS jdum;
CREATE TABLE jdum AS SELECT * FROM accounting_journal WHERE 1=0;

LOAD DATA INFILE '/Users/ikari_migration_files/journal_AR_AP_AD.txt' INTO TABLE jdum
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;

UPDATE jdum
SET transaction_id = NULL;

COMMIT;

SELECT *
INTO OUTFILE '/Users/ikari_migration_files/jdum10.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM jdum;

LOAD DATA INFILE '/Users/ikari_migration_files/jdum10.txt' INTO TABLE accounting_journal
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';
COMMIT;


-- trx AP-AD
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_AP_AD.txt'
  FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY ''
  LINES TERMINATED BY '\n'
FROM (
SELECT  DISTINCT
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
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
 FROM ikari_db_sage300.aptcr j
RIGHT JOIN ikari_db_sage300.aptcp t
   ON j.btchtype = t.batchtype AND j.cntbtch = t.cntbtch AND j.cntentr = t.cntrmit
 LEFT JOIN accounting_batch ab
   /* ON j.CNTBTCH = ab.batch_no AND ab.batch_type = 2 AND ab.company_id = @company_id AND ab.document_type = '10' */
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


LOAD DATA INFILE '/Users/ikari_migration_files/trx_AP_AD.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;



-- trx AR-AD
SELECT max(id) into @row_number FROM transactions_transaction;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/trx_AR_AD.txt'
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
        ,kurs.id2 AS `currency_id`
        ,NULL pair_id
        ,aj.id journal_id
        ,NULL tax_id
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
        ,0 adjamt, 0 discamt
        ,0 base_tax_amount
 FROM ikari_db_sage300.artcr j
RIGHT JOIN ikari_db_sage300.artcp t
   ON j.codepymtyp=t.codepaym AND j.cntbtch=t.cntbtch AND j.CNTITEM=t.CNTITEM -- add codepymtyp=codepaym to have this query use an index
 LEFT JOIN customers_customer cus
   ON j.IDCUST=cus.code and cus.company_id=@company_id
 LEFT JOIN accounts_accountset aas
   ON cus.account_set_id = aas.id AND aas.company_id=@company_id AND aas.type=1
 LEFT JOIN accounting_batch ab
   /* ON j.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id and ab.document_type = '10' */
   ON j.cntbtch=ab.batch_no AND ab.batch_type=1 AND ab.company_id=@company_id
 LEFT JOIN accounting_journal aj
   ON ab.id=aj.batch_id AND j.CNTITEM=aj.code AND aj.journal_type=11 AND aj.company_id=@company_id
 LEFT JOIN ikari_db_sage300.arpjh tx
   ON t.CODEPAYM=tx.typebtch AND t.cntbtch=tx.cntbtch AND t.CNTITEM=tx.cntitem
 LEFT JOIN cur_kurs kurs
   ON j.CODECURN = kurs.code
WHERE t.codepaym = 'AD') t0;


LOAD DATA INFILE '/Users/ikari_migration_files/trx_AR_AD.txt' INTO TABLE transactions_transaction
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;
############################################ END CAUTION #########################################



#Insert accounting_revaluationlogs
SELECT max(id) into @row_number FROM accounting_revaluationlogs;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/revlog_1.txt'
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
          9
        WHEN `CURNCYCODE` = 'JPY' THEN
          34
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
          9
       WHEN `CURNCYCODE` = 'JPY' THEN
          34
       ELSE
          (SELECT `id` FROM `currencies_currency` WHERE `code` = `CURNCYCODE`)
       END) AS `currency_id`
FROM ikari_db_sage300.aprvllog) t0;


LOAD DATA INFILE '/Users/ikari_migration_files/revlog_1.txt' INTO TABLE accounting_revaluationlogs
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;


#Insert accounting_revaluationdetails
SELECT max(id) into @row_number FROM accounting_revaluationdetails;
SELECT (@row_number:=@row_number + 1) AS id, t0.*
INTO OUTFILE '/Users/ikari_migration_files/revdtl_1.txt'
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
    ON IF(`jh`.`CODECURNTC`='DOS','SGD',`jh`.`CODECURNTC`) = cur.code
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
    ON IF(`jh`.`CODECURNTC`='DOS','SGD',`jh`.`CODECURNTC`) = cur.code
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


LOAD DATA INFILE '/Users/ikari_migration_files/revdtl_1.txt' INTO TABLE accounting_revaluationdetails
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\n';

COMMIT;

-- Delete Transaction Entries which are not belongs to any Journal
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

##################################################################################
#                             03_Transaction.sql END                             #
##################################################################################

set autocommit = 1;


call change_customer_code('ALEYEN', 'AINA-Y');
call change_customer_code('APCYEN', 'ARAI-Y');
call change_customer_code('BMNUS$', 'BMS-U');
call change_customer_code('CFSPYEN', 'CROWN-Y');
call change_customer_code('CFSUS$', 'CROWN-U');
call change_customer_code('CFSPS$', 'CROWN-S');
call change_customer_code('GSKUS$', 'GSK-U');
call change_customer_code('GSKSUS', 'GSKS-U');
call change_customer_code('HOEUS$', 'HOEI-U');
call change_customer_code('IKAYEN', 'IKARIH-Y');
call change_customer_code('JAPYEN', 'JPK-Y');
call change_customer_code('JOLYEN', 'JOLSON-Y');
call change_customer_code('JVCUS$', 'VICTOR-U');
call change_customer_code('KLOUS$', 'KIM-S');
call change_customer_code('LIVES$', 'LIVELY-S');
call change_customer_code('MINGS$', 'MINGGE-S');
call change_customer_code('MSPUS$', 'MPS-U');
call change_customer_code('MSPYEN', 'MPS-Y');
call change_customer_code('MUTOUS', 'MUTO-U');
call change_customer_code('NSSUS$', 'NIDAI-U');
call change_customer_code('NITTS$', 'NITTO-S');
call change_customer_code('NDKUS$', 'NITTO-U');
call change_customer_code('OLIPS$', 'OLIP-S');
call change_customer_code('PNSMUS', 'PCM-U');
call change_customer_code('R&ESS$', 'RE&S-S');
call change_customer_code('SANKS$', 'SANKO-S');
call change_customer_code('SEMBS$', 'SEMB-S');
call change_customer_code('SENTS$', 'SENT-S');
call change_customer_code('SMWAS$', 'SHIN-S');
call change_customer_code('SHWJS$', 'SHINJ-S');
call change_customer_code('SUNTS$', 'SUNT-U');
call change_customer_code('TAKUS$', 'TAKATA-U');
call change_customer_code('YETUS$', 'YET-U');


call change_supplier_code('ABEHUS', 'ABE-U');
call change_supplier_code('CKDSS$', 'CKD-S');
call change_supplier_code('CFSUS$', 'CROWN-U');
call change_supplier_code('CROWNYEN', 'CROWN-Y');
call change_supplier_code('DICYEN', 'DICK-Y');
call change_supplier_code('ETOUS$', 'ETO-U');
call change_supplier_code('FDKUS$', 'FDK-U');
call change_supplier_code('GAOSS$', 'GAO-S');
call change_supplier_code('GPMSS$', 'GP-S');
call change_supplier_code('HTSUS$', 'HAN-U');
call change_supplier_code('HICUS$', 'HICHEM-U');
call change_supplier_code('HUPHS$', 'HUPHONG-S');
call change_supplier_code('IT1YEN', 'IIDA-Y');
call change_supplier_code('IKAUS$', 'IKARIH-U');
call change_supplier_code('JSBUS$', 'JSB-U');
call change_supplier_code('JVCYEN', 'VICTOR-U');
call change_supplier_code('KATOMUS$', 'KMM-U');
call change_supplier_code('KATUS$', 'KMS-U');
call change_supplier_code('KCKYEN', 'KCK-Y');
call change_supplier_code('KCKBHT', 'KCK-B');
call change_supplier_code('KONUS$', 'KONDO-U');
call change_supplier_code('LIANS$', 'LIAN-S');
call change_supplier_code('MIKUS$', 'MIKURO-U');
call change_supplier_code('NATFS$', 'NATURAL-S');
call change_supplier_code('NHKIS$', 'NHK-S');
call change_supplier_code('NE1US$', 'NICHI-U');
call change_supplier_code('NICHS$', 'NICHI-S');
call change_supplier_code('NIDUS$', 'NIDEC-U');
call change_supplier_code('NDSUS$', 'NITTO-U');
call change_supplier_code('NITTS$', 'NITTO-S');
call change_supplier_code('OLI1SG', 'OLIP-S');
call change_supplier_code('OLI1US', 'OLIP-U');
call change_supplier_code('PGJYEN', 'PGJ-Y');
call change_supplier_code('SPSUS$', 'SANKO-U');
call change_supplier_code('SHARMB', 'SSS-R');
call change_supplier_code('TRUUS$', 'TRUST-U');
call change_supplier_code('STKYEN', 'SHIN-Y');
call change_supplier_code('SIFUS$', 'SIFLEX-U');
call change_supplier_code('SOHUS$', 'SOHRYU-U');
call change_supplier_code('SU1US$', 'SUNWA-U');
call change_supplier_code('SULYEN', 'SUNLIT-Y');
call change_supplier_code('SUNUS$', 'SUNT-U');
call change_supplier_code('SUNYEN', 'SUNT-Y');
call change_supplier_code('SWSUS$', 'SWS-U');
call change_supplier_code('TANUS$', 'TAN-U');
call change_supplier_code('YAAUS$', 'YAAN-U');
call change_supplier_code('TSCYEN', 'TOWA-Y');
call change_supplier_code('TSTBAT', 'TOWA-B');
call change_supplier_code('TOWUS$', 'TOWA-U');
call change_supplier_code('VCOUS$', 'VICTOR-Y');
call change_supplier_code('VICTS$', 'VEPL-S');
call change_supplier_code('WAHSUS', 'WAH-U');
call change_supplier_code('WDIYEN', 'WITSF-Y');
call change_supplier_code('WITSUS$', 'WITSF-U');
call change_supplier_code('XERUS$', 'XEROM-U');
call change_supplier_code('YETUS$', 'YET-U');

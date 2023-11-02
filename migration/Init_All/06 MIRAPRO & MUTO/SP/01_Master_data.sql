#SET @company_id = 1;

/* UPDATE companies_company set
    fiscal_period = now()
    ,current_period_month = DATE_FORMAT(now(), '%m')
    ,current_period_year = DATE_FORMAT(now(),'%Y')
where id=@company_id; */

/* update accounting_fiscalcalendar set
    is_sp_locked = 1
    ,is_ic_locked = 0
where fiscal_year<2018 and company_id=@company_id; */

-- BEGIN DELETE ALL S/P TRANSACTIONS DATA --


-- run one time --

-- INSERT INTO `items_itemmeasure`
-- (`name`, `is_active`, `create_date`, `update_date`, `update_by`, `is_hidden`, `code`)
-- VALUES
-- 	('LITRE', 1, '2017-09-13', '2009-10-08', NULL, 0, 'LITRE'),
-- 	('LOT', 1, '2017-09-13', '2009-10-08', NULL, 0, 'LOT'),
-- 	('QUANTITY', 1, '2017-09-13', '2009-10-08', NULL, 0, 'QTY'),
-- 	('POUND', 1, '2017-09-13', '2009-10-08', NULL, 0, 'LBS'),
-- 	('DRUM', 1, '2017-09-13', '2009-10-08', NULL, 0, 'DRUM'),
-- 	('SHEET', 1, '2017-09-13', '2009-10-08', NULL, 0, 'SHEET'),
-- 	('BOTTLE', 1, '2017-09-13', '2009-10-08', NULL, 0, 'BOTTLE'),
-- 	('BAG', 1, '2017-09-13', '2009-10-08', NULL, 0, 'BAG'),
-- 	('BAR', 1, '2017-09-13', '2009-10-08', NULL, 0, 'BAR'),
-- 	('PLATE', 1, '2017-09-13', '2009-10-08', NULL, 0, 'PLATE'),
-- 	('TUBE', 1, '2017-09-13', '2009-10-08', NULL, 0, 'TUBE'),
-- 	('GALLON', 1, '2017-09-13', '2009-10-08', NULL, 0, 'GALLON'),
-- 	('RACK', 1, '2017-09-13', '2009-10-08', NULL, 0, 'RACK'),
-- 	('SHOTS', 1, '2017-09-13', '2009-10-08', NULL, 0, 'SHOTS'),
-- 	('UNIT', 1, '2017-09-13', '2009-10-08', NULL, 0, 'UNIT'),
-- 	('BLOCK', 1, '2017-09-13', '2009-10-08', NULL, 0, 'BLOCK'),
-- 	('PANEL', 1, '2017-09-13', '2009-10-08', NULL, 0, 'PANEL'),
-- 	('CAN', 1, '2017-09-13', '2009-10-08', NULL, 0, 'CAN') ;

-- run one time --

DELETE FROM orders_orderitem
where order_id in (select id from orders_order where company_id=@company_id);

DELETE FROM orders_orderdelivery
where order_id in (select id from orders_order where company_id=@company_id);

DELETE FROM orders_orderheader
where order_id in (select id from orders_order where company_id=@company_id);

DELETE FROM inventory_incoming
where company_id=@company_id;

DELETE from inventory_outgoing
where company_id=@company_id;
DELETE FROM inventory_history WHERE company_id=@company_id;

DELETE FROM inventory_stocktransactiondetail
where parent_id in (select id from inventory_stocktransaction where company_id=@company_id);

DELETE FROM inventory_stocktransaction
where company_id=@company_id;

DELETE FROM orders_order
where company_id=@company_id;
-- END DELETE ALL S/P TRANSACTIONS DATA --


-- BEGIN DELETE ALL Inventory TRANSACTIONS DATA --
DELETE FROM inventory_transactioncode
WHERE company_id=@company_id;
-- END DELETE ALL Inventory TRANSACTIONS DATA --

-- Delete master data --
DELETE FROM customers_delivery
WHERE company_id=@company_id;

DELETE FROM contacts_contact
WHERE company_id=@company_id;

DELETE FROM customers_customeritem
where item_id in (select id from items_item where company_id=@company_id);

DELETE FROM suppliers_supplieritem
where item_id in (select id from items_item where company_id=@company_id);

DELETE FROM locations_locationitem
where item_id in (select id from items_item where company_id=@company_id);

DELETE FROM items_item
where company_id=@company_id;

DELETE FROM items_itemcategory
where company_id=@company_id;

-- End Delete master data --


#INSERT country
INSERT INTO countries_country(
`code`,`name`,`create_date`,`update_date`,`update_by`,
`is_hidden`,`currency_id`)
SELECT
    CTY_CODE code
    ,CCOD_CDESC name
    ,date_format('2017-01-19','%Y-%m-%d') create_date
    ,date_format('2017-01-19','%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,1 currency_id
FROM
    (SELECT * FROM
        (SELECT
            CCOD_CODE CTY_CODE
            ,CCOD_CDESC
            ,CCOD_CODTY
            ,CCOD_TAXPC FROM ikari_db_foxpro_sp.ccod_fil where CCOD_CODTY=1
        UNION
        SELECT
            DCOD_CODE
            ,DCOD_CDESC
            ,DCOD_CODTY
            ,NULL FROM ikari_db_foxpro_sp.dcod_fil
        WHERE DCOD_CODTY=1
        AND DCOD_CODE NOT IN (SELECT CCOD_CODE FROM ikari_db_foxpro_sp.ccod_fil where CCOD_CODTY=1)
        ) cty
    WHERE cty.cty_code NOT IN (SELECT code FROM countries_country)) cty_list;

#INSERT tax code
INSERT INTO taxes_tax(
`code`,`name`,`rate`,`company_id`,`create_date`,
`update_date`,`update_by`,`is_hidden`)
SELECT
    CCOD_CODE code
    ,CCOD_CDESC name
    ,CCOD_TAXPC rate
    ,@company_id company_id
    ,ccod_lupdt create_date
    ,ccod_lupdt update_date
    ,null update_by
    ,0 is_hidden
FROM ikari_db_foxpro_sp.ccod_fil WHERE CCOD_CODTY=7;

INSERT INTO taxes_tax(
`code`,`name`,`rate`,`company_id`,`create_date`,
`update_date`,`update_by`,`is_hidden`)
SELECT
    ftx.TAX_CODE code
    ,ftx.TAX_DESC name
    ,ftx.TAX_RATE rate
    ,@company_id company_id
    ,date_format('2017-01-19','%Y-%m-%d') create_date
    ,date_format('2017-01-19','%Y-%m-%d') update_date
    ,null update_by
    ,0 is_hidden
FROM ikari_db_foxpro_sp.taxm_fil ftx
LEFT OUTER JOIN taxes_tax itx ON ftx.TAX_CODE=itx.code;

delimiter $$
DROP PROCEDURE IF EXISTS remove_duplicate$$
create procedure remove_duplicate(IN I_company_id int)
begin
UPDATE taxes_tax as t1
    INNER JOIN taxes_tax as t2 ON
        (t1.rate = t2.rate AND t1.company_id = t2.company_id and t1.id < t2.id and
        t1.code = t2.code)
SET t2.is_hidden = 1;

DELETE FROM taxes_tax WHERE is_hidden = 1 and company_id=I_company_id;

end$$
delimiter ;


call remove_duplicate(@company_id);

delimiter $$
DROP PROCEDURE IF EXISTS clean_taxes_tax_data$$
create procedure clean_taxes_tax_data(IN I_company_id int)
begin

/* UPDATE taxes_tax tx set `code` = CONCAT('OG', tx.number) where `name` like '%SALES%' and company_id=I_company_id and tx.number is not null; */
/* UPDATE taxes_tax tx set `code` = CONCAT('IG', tx.number) where `name` like '%PURCHASE%' and company_id=I_company_id and tx.number is not null; */

UPDATE taxes_tax tx set `tax_type` = 1 -- TAX_TYPE_DICT['Customer/Vendor'] --
    where company_id=I_company_id;

UPDATE taxes_tax tx set `number` = 2 -- TAX_CLASS_DICT['Zero Rate'] --
    where `name` like '%0%' and company_id=I_company_id;
UPDATE taxes_tax tx set `number` = 2 -- TAX_CLASS_DICT['Zero Rate'] --
    where `name` like '%Z%' and company_id=I_company_id;
UPDATE taxes_tax tx set `number` = 2 -- TAX_CLASS_DICT['Zero Rate'] --
    where `name` like '%FREIGHT%' and company_id=I_company_id;
UPDATE taxes_tax tx set `number` = 1 -- TAX_CLASS_DICT['Standard Rate'] --
    where rate <> 0.00 and company_id=I_company_id;
UPDATE taxes_tax tx set `number` = 2 -- TAX_CLASS_DICT['Zero Rate'] --
    where `name` like '%EXPORT%' and company_id=I_company_id;
UPDATE taxes_tax tx set `number` = 3 -- TAX_CLASS_DICT['Exempted'] --
    where `name` like '%EXEM%' and company_id=I_company_id;
UPDATE taxes_tax tx set `number` = 4 -- TAX_CLASS_DICT['OUT OF SCOPE'] --
    where `name` like '%SCOPE%' and company_id=I_company_id;

UPDATE taxes_tax tx set `update_date` = '2017-01-01' where `update_date` = '0000-00-00' and company_id=I_company_id;

select
	@tax_group_sales_id := id
from taxes_taxgroup tx where company_id=I_company_id and transaction_type=1 limit 1;

select
	@tax_group_purchase_id := id
from taxes_taxgroup tx where company_id=I_company_id and transaction_type=2 limit 1;

select
	/* @tax_account_code_id := tax_account_code_id, */
	@tax_authority_id := tax_authority_id
from taxes_tax tx where company_id=I_company_id limit 1;

UPDATE taxes_tax set
	/* tax_account_code_id = @tax_account_code_id, */
	tax_authority_id := @tax_authority_id,
	tax_group_id := @tax_group_sales_id
where company_id=I_company_id and (`name` like '%SALE%' or  `code` like 'O%');

UPDATE taxes_tax set
	/* tax_account_code_id = @tax_account_code_id, */
	tax_authority_id := @tax_authority_id,
	tax_group_id := @tax_group_purchase_id
where company_id=I_company_id and (`name` like '%PUR%' or  `code` like 'I%');

UPDATE taxes_tax as tax SET tax_account_code_id = (SELECT liability_account_id FROM taxes_taxauthority WHERE id=tax.tax_authority_id) WHERE tax_group_id=1;
UPDATE taxes_tax as tax SET tax_account_code_id = (SELECT recoverable_account_id FROM taxes_taxauthority WHERE id=tax.tax_authority_id) WHERE tax_group_id=2;

end$$
delimiter ;

call clean_taxes_tax_data(@company_id);

##### INSERT TRANSACTION_CODE
INSERT INTO inventory_transactioncode (
code, name, io_flag, price_flag, doc_type
,auto_generate ,ics_prefix ,create_date ,update_date ,update_by
,is_hidden ,company_id ,menu_type ,last_no)
SELECT
    ICOD_CODE code
    ,ICOD_CDESC name
    ,ICOD_IOFLG io_flag
    ,ICOD_PRCFG price_flag
    ,ICOD_DOCTP doc_type
	,if(ICOD_AUTOG='Y',1,0) auto_generate
	,ICOD_ICPFX ics_prefix
	,ICOD_LUPDT create_date
	,ICOD_LUPDT update_date
	,null update_by
	,0 is_hidden
	,@company_id company_id
	,'1' menu_type -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	,icod_lstno last_no
FROM ikari_db_foxpro_sp.icod_fil
WHERE ICOD_CODTY='2'
UNION ALL
# SALES_NUMBER_FILE
SELECT
    DNUM_TRNCD code
    ,DNUM_NDESC name
	,COALESCE(invcd.io_flag,'3') io_flag
	,COALESCE(invcd.price_flag,'1') price_flag
	,DNUM_DOCTY doc_type
	,if(DNUM_AUTOG='Y',1,0) auto_generate
	,DNUM_DLPFX ics_prefix
	,DNUM_LUPDT create_date
	,DNUM_LUPDT update_date
	,null update_by
	,0 is_hidden
	,@company_id company_id
	,'2' menu_type -- TRN_CODE_TYPE_DICT['Sales Number File'] --
	,DNUM_LSTNO last_no
FROM ikari_db_foxpro_sp.dnum_fil slscd
LEFT OUTER JOIN (
	SELECT
	    ICOD_CODE
	    ,ICOD_IOFLG io_flag
	    ,ICOD_PRCFG price_flag
	FROM ikari_db_foxpro_sp.icod_fil WHERE ICOD_CODTY='2') invcd
ON slscd.DNUM_TRNCD=invcd.ICOD_CODE
UNION ALL
# PURCHASE_NUMBER_FILE
SELECT
    CNUM_TRNCD code
    ,CNUM_NDESC name
	,COALESCE(invcd.io_flag,'1') io_flag
	,COALESCE(invcd.price_flag,'1') price_flag
	,CNUM_DOCTY doc_type
	,if(CNUM_AUTOG='Y',1,0) auto_generate
	,CNUM_CLPFX ics_prefix
	,CNUM_LUPDT create_date
	,CNUM_LUPDT update_date
	,null update_by
	,0 is_hidden
	,@company_id company_id
	,'3' menu_type -- TRN_CODE_TYPE_DICT['Purchase Number File'] --
	,CNUM_LSTNO last_no
FROM ikari_db_foxpro_sp.cnum_fil purcd
LEFT OUTER JOIN (
	SELECT
	    ICOD_CODE
	    ,ICOD_IOFLG io_flag
	    ,ICOD_PRCFG price_flag
	FROM ikari_db_foxpro_sp.icod_fil WHERE ICOD_CODTY='2') invcd
ON purcd.CNUM_TRNCD=invcd.ICOD_CODE;


#INSERT items_itemcategory
INSERT INTO items_itemcategory(
`code`,`name`,`company_id`,`create_date`,`update_date`
,`update_by`,`is_hidden`,`type`)
SELECT * FROM (SELECT
    all_code.code code
	,COALESCE(item_grp.name,item_cat.name) name
	,COALESCE(item_grp.company_id,item_cat.company_id) company_id
	,COALESCE(item_grp.create_date,item_cat.create_date) create_date
	,COALESCE(item_grp.update_date,item_cat.update_date) update_date
	,COALESCE(item_grp.update_by,item_cat.update_by) update_by
	,COALESCE(item_grp.is_hidden,item_cat.is_hidden) is_hidden
	,(CASE
		WHEN (SELECT COUNT(ICOD_CODE) test FROM ikari_db_foxpro_sp.icod_fil where ICOD_CODTY=4 AND ICOD_CODE = all_code.code) <= 0
			AND (SELECT COUNT(DCOD_CODE) test FROM ikari_db_foxpro_sp.dcod_fil where DCOD_CODTY=7 AND DCOD_CODE = all_code.code) > 0
			THEN '1'
		WHEN (SELECT COUNT(ICOD_CODE) test FROM ikari_db_foxpro_sp.icod_fil where ICOD_CODTY=4 AND ICOD_CODE = all_code.code) > 0
			AND (SELECT COUNT(DCOD_CODE) test FROM ikari_db_foxpro_sp.dcod_fil where DCOD_CODTY=7 AND DCOD_CODE = all_code.code) > 0
			THEN '2'
		WHEN (SELECT COUNT(ICOD_CODE) test FROM ikari_db_foxpro_sp.icod_fil where ICOD_CODTY=4 AND ICOD_CODE = all_code.code) > 0
			AND (SELECT COUNT(DCOD_CODE) test FROM ikari_db_foxpro_sp.dcod_fil where DCOD_CODTY=7 AND DCOD_CODE = all_code.code) <= 0
			THEN '3'
	END) type
FROM (
	SELECT DCOD_CODE code
	FROM ikari_db_foxpro_sp.dcod_fil WHERE DCOD_CODTY=7
	UNION
	SELECT ICOD_CODE code
	FROM ikari_db_foxpro_sp.icod_fil WHERE ICOD_CODTY=4
) all_code
LEFT OUTER JOIN
    (select
        ICOD_CODE code
        ,ICOD_CDESC name
        ,@company_id company_id
        ,ICOD_LUPDT create_date
        ,ICOD_LUPDT update_date
        ,null update_by
        ,0 is_hidden
    FROM ikari_db_foxpro_sp.icod_fil where ICOD_CODTY=4) item_grp
ON all_code.code=item_grp.code
LEFT OUTER JOIN
    (SELECT
        DCOD_CODE code
        ,DCOD_CDESC name
        ,@company_id company_id
        ,DCOD_LUPDT create_date
        ,DCOD_LUPDT update_date
        ,null update_by
        ,0 is_hidden
    FROM ikari_db_foxpro_sp.dcod_fil where DCOD_CODTY=7) item_cat
ON all_code.code=item_cat.code
) item_grp_all
ORDER BY code;


#INSERT items_item
INSERT INTO items_item(
`code`,`short_description`,`name`,`sale_price`,`purchase_price`,
`minimun_order`,`size`,`weight`,`is_active`,`create_date`,
`update_date`,`update_by`,`is_hidden`,`company_id`,`purchase_currency_id`,
`sale_currency_id`,`category_id`,`country_id`,`inv_measure_id`,`model_qty`,
`person_incharge`,`report_measure_id`,`sales_measure_id`,`ratio`,`purchase_measure_id`
,`book_value`,`par_value`,`cost_price`,`last_purchase_price`,`stockist_price`
,`last_purchase_date`,`last_purchase_doc`,`balance_qty`,`balance_amount`,`retail_price`,
`move_date`,`po_qty`,`so_qty`,`backorder_qty`,`in_qty`,`out_qty`)
SELECT
    all_item.cd code
	,COALESCE(sp.mpth_sdesc,inv.iitm_itmd1,sp.mpth_prtno,null) short_description
	,COALESCE(sp.mpth_ldesc,concat(inv.iitm_itmd1,' ',sp.mpth_prtno),null) name
	,COALESCE(mpth_sprc,0) sale_price
	,COALESCE(mpth_pprc,iitm_pcprc,0) purchase_price
	,COALESCE(mpth_minoq,0) minimun_order
	,0 size
	,COALESCE(iitm_untwt,0) weight
	,1 is_active
	,COALESCE(sp.mpth_lupdt,inv.iitm_lupdt) create_date
	,COALESCE(sp.mpth_lupdt,inv.iitm_lupdt) update_date
	,null update_by
	,0 is_hidden
	,@company_id company_id
	,COALESCE(pur_currency_id,null) purchase_currency_id
	,COALESCE(sale_currency_id,null) sale_currency_id
	,COALESCE(sp.category_id,inv.category_id,null) category_id
	,COALESCE(country_id,null) country_id
	,COALESCE(inv.inv_measure_id,sp.inv_measure_id,null) inv_measure_id
	,COALESCE(sp.mpth_qtypm,0) model_qty
	,COALESCE(sp.mpth_pic,null) person_incharge
	,COALESCE(sp.report_measure_id,null) report_measure_id
	,COALESCE(inv.sales_measure_id,sp.sales_measure_id) sales_measure_id
	,COALESCE(sp.mpth_ratio,0) ratio
	,COALESCE(inv.purchase_measure_id,sp.purchase_measure_id) purchase_measure_id
	,0 book_value
	,0 par_value
	,COALESCE(inv.iitm_ctprc,0) cost_price
	,COALESCE(inv.iitm_lpprc,0) last_purchase_price
	,COALESCE(inv.iitm_skpr1,iitm_skpr2,iitm_skpr3,iitm_skpr4,iitm_skpr5,0) stockist_price
	,COALESCE(inv.iitm_lpcdt,null) last_purchase_date
	,COALESCE(inv.iitm_lpdoc,null) last_purchase_doc
	,COALESCE(inv.iitm_blqty,0) balance_qty
	,COALESCE(inv.iitm_blamt,0) balance_amount
	,COALESCE(inv.iitm_slpr1,0) retail_price
	,COALESCE(inv.iitm_liodt,null) move_date
	,COALESCE(inv.iitm_pord,0) po_qty
	,COALESCE(inv.iitm_sord,0) so_qty
	,COALESCE(inv.iitm_bkord,0) backorder_qty
	,COALESCE(inv.iitm_inqty,0) in_qty
	,COALESCE(inv.iitm_otqty,0) out_qty
FROM (SELECT mpth_prtno cd FROM ikari_db_foxpro_sp.mpth_fil
UNION SELECT iitm_itmcd from ikari_db_foxpro_sp.iitm_fil) all_item
LEFT OUTER JOIN (
    SELECT
        iitm_fil.*
        ,(SELECT id FROM items_itemcategory WHERE SUBSTRING(code,1,8) = iitm_itmgr and company_id=@company_id) category_id
        ,(SELECT id FROM items_itemmeasure WHERE code=iitm_mment) inv_measure_id
        ,(SELECT id FROM items_itemmeasure WHERE code=iitm_oment) sales_measure_id
        ,(SELECT id FROM items_itemmeasure WHERE code=iitm_iment) purchase_measure_id
    FROM ikari_db_foxpro_sp.iitm_fil) inv
ON all_item.cd=inv.iitm_itmcd
LEFT OUTER JOIN (
    SELECT
        mpth_prtno -- code --
        ,mpth_sdesc -- short_description --
        ,mpth_ldesc -- name --
        ,mpth_sprc -- sale_price --
        ,mpth_pprc -- purchase_price --
        ,mpth_minoq -- minimun_order --
        ,mpth_lupdt -- update_date --
        ,mpth_group
        ,mpth_qtypm -- model_qty --
        ,mpth_pic -- person_incharge --
        ,mpth_ratio -- ratio --
        ,(SELECT id FROM items_itemcategory WHERE SUBSTRING(code,1,8) = mpth_group and company_id=@company_id) category_id
        ,(SELECT id FROM currencies_currency WHERE code=new_mpth_pcur) sale_currency_id
        ,(SELECT id FROM currencies_currency WHERE code=new_mpth_pcur) pur_currency_id
        ,(SELECT id FROM items_itemmeasure WHERE code=mpth_mment) inv_measure_id
        ,(SELECT id FROM items_itemmeasure WHERE code=mpth_oment) sales_measure_id
        ,(SELECT id FROM items_itemmeasure WHERE code=mpth_iment) purchase_measure_id
        ,(SELECT id FROM items_itemmeasure WHERE code=mpth_ruom) report_measure_id
        ,(SELECT id FROM countries_country WHERE code=mpth_ctryo) country_id
    FROM (SELECT mpth_fil.*
		,(CASE
	        WHEN mpth_pcur='US$' THEN 'USD'
	        WHEN mpth_pcur='S$' THEN 'SGD'
	        ELSE mpth_pcur
	    END) new_mpth_pcur
	    FROM ikari_db_foxpro_sp.mpth_fil) sp_item
    ) sp
ON all_item.cd=sp.mpth_prtno;


#INSERT customers_customer
INSERT INTO customers_customer(
`code`,`name`,`address`,`phone`,`fax`,`note1`,`note2`,
`is_active`,`is_hidden`,`create_date`,`update_date`,`update_by`,
`company_id`,`country_id`,`currency_id`,`tax_id`,
`location_id`,`payment_mode_id`,`payment_term`,`credit_limit`,
`customer_type`,`pricing_type`,`interest_flag`,
`interest_1`,`interest_2`,`interest_3`,`interest_4`,`interest_5`,
`accode_ar`,`accode_sal`,`accode_exc`,`accode_int`,`accode_bnk`,`accode_chr`,
`center_ar`,`center_sal`,`center_exc`,`center_int`,`center_bnk`,`center_chr`)
SELECT
    mcus_cuscd code
    ,mcus_cusnm name
    ,CONCAT(mcus_cusa1,'\n',mcus_cusa2,'\n',mcus_cusa3,'\n',mcus_cusa4) address
    ,mcus_custl phone
    ,mcus_cusfx fax
    ,'' note1
    ,'' note2
    ,1 is_active
    ,0 is_hidden
    ,mcus_lupdt create_date
    ,mcus_lupdt update_date
    ,null update_by
    ,@company_id company_id
    ,(select id from countries_country where code=mcus_ctycd) country_id
    ,(select id from currencies_currency where code=new_mcus_cuscr) currency_id
    ,(select id from taxes_tax where code=mcus_taxcd and company_id=@company_id) tax_id
    ,(select id from locations_location where code=mcus_loccd and company_id=@company_id) location_id
    ,(select id from transactions_transactionmethod where code=mcus_paymd and company_id=@company_id) payment_mode_id
    ,mcus_paytm payment_term
    ,mcus_crlmt credit_limit
    ,mcus_custy customer_type
    ,mcus_prcty pricing_type
    ,mcus_intfg interest_flag
    ,mcus_irte1 interest_1
    ,mcus_irte2 interest_2
    ,mcus_irte3 interest_3
    ,mcus_irte4 interest_4
    ,mcus_irte5 interest_5
    ,mcus_slacc accode_sal
    ,mcus_aracc accode_ar
    ,mcus_exacc accode_exc
    ,mcus_inacc accode_int
    ,mcus_bkacc accode_bnk
    ,mcus_chacc accode_chr
    ,mcus_slcen center_ar
    ,mcus_arcen center_sal
    ,mcus_excen center_exc
    ,mcus_incen center_int
    ,mcus_bkcen center_bnk
    ,mcus_chcen center_chr
FROM
    (SELECT mcusfil0.*
        ,(CASE
            WHEN mcusfil0.mcus_cuscr='US$' THEN 'USD'
            WHEN mcusfil0.mcus_cuscr='S$' THEN 'SGD'
            ELSE mcusfil0.mcus_cuscr
        END ) new_mcus_cuscr
    FROM ikari_db_foxpro_sp.mcus_fil mcusfil0
) mcus_fil;


#INSERT suppliers_supplier
INSERT INTO suppliers_supplier(
`name`,`code`,`address`,`phone`,`fax`,`ship_info_1`,`ship_info_2`,
`is_active`,`is_hidden`,`create_date`,`update_date`,`update_by`,
`company_id`,`country_id`,`currency_id`,`payment_mode_id`,`tax_id`,
`credit_limit`,`ship_via`,`term_days`,
`accode_ap`,`accode_pur`,`accode_exc`,`accode_bnk`,`accode_chr`,
`center_ap`,`center_pur`,`center_exc`,`center_bnk`,`center_chr`)
SELECT
    msup_supnm name
    ,msup_supcd code
    ,CONCAT(msup_supa1,'\n',msup_supa2,'\n',msup_supa3,'\n',msup_supa4) address
	,msup_suptl phone
	,msup_supfx fax
	,'' ship_info_1
	,'' ship_info_2
	,1 is_active
	,0 is_hidden
	,msup_lupdt create_date
	,msup_lupdt update_date
	,null update_by
	,@company_id company_id
	,(select id from countries_country where code=msup_ctycd) country_id
	,(select id from currencies_currency where code=new_msup_supcr) currency_id
	,(select id from transactions_transactionmethod where code=msup_paymd and company_id=@company_id) payment_mode_id
	,(select id from taxes_tax where code=msup_taxcd and company_id=@company_id) tax_id
	,msup_crlmt credit_limit
	,msup_spvia ship_via
	,msup_paytm term_days
	,msup_pracc accode_ap
	,msup_apacc accode_pur
	,msup_exacc accode_exc
	,msup_bkacc accode_bnk
	,msup_chacc accode_chr
	,msup_prcen center_ap
	,msup_apcen center_pur
	,msup_excen center_exc
	,msup_bkcen center_bnk
	,msup_chcen center_chr
FROM (
    SELECT msupfil0.*
        ,(CASE
            WHEN msupfil0.msup_supcr='US$' THEN 'USD'
            WHEN msupfil0.msup_supcr='S$' THEN 'SGD'
            ELSE msupfil0.msup_supcr
        END ) new_msup_supcr
    FROM ikari_db_foxpro_sp.msup_fil msupfil0
) msup_fil;


#insert currencies_exchangerate
INSERT INTO currencies_exchangerate (
`rate`, `exchange_date`, `description`, `create_date`, `update_date`,
`update_by`, `is_hidden`, `company_id`, `from_currency_id`, `to_currency_id`,
`flag`, `apply_flag`)
SELECT
    GCUR_XRATE rate
    ,(CASE WHEN GCUR_APMTH < 10 THEN
		date_format(CONCAT(CAST(GCUR_APYR AS CHAR), '-0', CAST(GCUR_APMTH AS CHAR), '-01'),'%Y-%m-%d')
	 ELSE
		date_format(CONCAT(CAST(GCUR_APYR AS CHAR), '-', CAST(GCUR_APMTH AS CHAR), '-01'),'%Y-%m-%d')
	 END) exchange_date
    ,NULL description
    ,date_format(GCUR_LUPDT,'%Y-%m-%d') create_date
    ,date_format(GCUR_LUPDT,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,(CASE WHEN GCUR_CURFR = 'S$' THEN
        (SELECT id from currencies_currency WHERE code='SGD')
	  WHEN GCUR_CURFR = 'US$' THEN
        (SELECT id from currencies_currency WHERE code='USD')
	  WHEN GCUR_CURFR = 'RM' THEN
        (SELECT id from currencies_currency WHERE code='MYR')
	  WHEN GCUR_CURFR = 'BHT' THEN
        (SELECT id from currencies_currency WHERE code='BAH')
	  WHEN GCUR_CURFR = '€' THEN
        (SELECT id from currencies_currency WHERE code='EUR')
      ELSE
        (SELECT id from currencies_currency WHERE code=GCUR_CURFR)
      END) from_currency_id
    ,(CASE WHEN GCUR_CURTO = 'S$' THEN
        (SELECT id from currencies_currency WHERE code='SGD')
	  WHEN GCUR_CURTO = 'US$' THEN
        (SELECT id from currencies_currency WHERE code='USD')
	  WHEN GCUR_CURTO = 'RM' THEN
        (SELECT id from currencies_currency WHERE code='MYR')
      WHEN GCUR_CURTO = 'BHT' THEN
        (SELECT id from currencies_currency WHERE code='BAH')
      WHEN GCUR_CURFR = '€' THEN
        (SELECT id from currencies_currency WHERE code='EUR')
      ELSE
        (SELECT id from currencies_currency WHERE code=GCUR_CURTO)
      END) to_currency_id
    ,'ACCOUNTING' flag
    ,1 apply_flag
FROM ikari_db_foxpro_sp.gcur_fil;



delimiter $$
DROP PROCEDURE IF EXISTS remove_duplicate$$
create procedure remove_duplicate()
begin
UPDATE accounts_distributioncode as t1
    INNER JOIN accounts_distributioncode as t2 ON
        (t1.code = t2.code AND t1.company_id = t2.company_id and t1.id < t2.id and
        t1.name = t2.name and t1.type = t2.type and
        t1.is_active = t2.is_active)
SET t2.is_hidden = 1;

end$$
delimiter ;

call remove_duplicate();


delimiter $$
DROP PROCEDURE IF EXISTS remove_duplicate$$
create procedure remove_duplicate()
begin
UPDATE currencies_exchangerate as t1
    INNER JOIN currencies_exchangerate as t2 ON
        (t1.rate = t2.rate AND t1.company_id = t2.company_id and t1.id < t2.id and
        t1.from_currency_id = t2.from_currency_id and t1.to_currency_id = t2.to_currency_id and
        t1.flag = t2.flag and t1.exchange_date = t2.exchange_date)
SET t2.is_hidden = 1;

end$$
delimiter ;

call remove_duplicate();


delimiter $$
DROP PROCEDURE IF EXISTS merge_customers$$
create procedure merge_customers(in code1 varchar(20), in code2 varchar(20), IN I_company_id int)
begin
UPDATE customers_customer as t1
    INNER JOIN customers_customer as t2 ON
        (t1.code = code1 AND t2.code = code2 AND t1.company_id = t2.company_id AND t2.company_id = I_company_id and t1.id < t2.id)
SET t1.code = t2.code, t1.name = t2.name, t1.phone = t2.phone, t1.fax=t2.fax, t1.update_date = t2.update_date,
t1.country_id = t2.country_id, t1.currency_id = t2.currency_id, t1.tax_id = t2.tax_id, t1.address=t2.address,
t1.accode_ar = t2.accode_ar, t1.accode_bnk = t2.accode_bnk, t1.accode_chr = t2.accode_chr, t1.accode_exc = t2.accode_exc,
t1.accode_int = t2.accode_int, t1.accode_sal = t2.accode_sal, t1.customer_type = t2.customer_type,
t1.payment_mode_id = t2.payment_mode_id, t1.pricing_type = t2.pricing_type, t2.code = 'DELETETHIS';

UPDATE customers_customer as t1
    INNER JOIN customers_customer as t2 ON
        (t1.code = t2.code AND t1.company_id = I_company_id AND t2.company_id = I_company_id and t1.id < t2.id)
SET t2.code = 'DELETETHIS';

DELETE from customers_customer where company_id=@company_id and code='DELETETHIS';
end$$
delimiter ;


delimiter $$
DROP PROCEDURE IF EXISTS merge_suppliers$$
create procedure merge_suppliers(in code1 varchar(20), in code2 varchar(20), IN I_company_id int)
begin
UPDATE suppliers_supplier as t1
    INNER JOIN suppliers_supplier as t2 ON
        (t1.code = code1 AND t2.code = code2 AND t1.company_id = t2.company_id AND t2.company_id = I_company_id and t1.id < t2.id)
SET t1.code = t2.code, t1.name = t2.name, t1.phone = t2.phone, t1.fax=t2.fax, t1.update_date = t2.update_date, t1.term_days = t2.term_days,
t1.country_id = t2.country_id, t1.currency_id = t2.currency_id, t1.tax_id = t2.tax_id, t1.address=t2.address,
t1.accode_ap = t2.accode_ap, t1.accode_bnk = t2.accode_bnk, t1.accode_chr = t2.accode_chr, t1.accode_exc = t2.accode_exc,
t1.accode_pur = t2.accode_pur,
t1.payment_mode_id = t2.payment_mode_id, t2.code = 'DELETETHIS';

UPDATE suppliers_supplier as t1
    INNER JOIN suppliers_supplier as t2 ON
        (t1.code = t2.code AND t1.company_id = I_company_id AND t2.company_id = I_company_id and t1.id < t2.id)
SET t2.code = 'DELETETHIS';

DELETE from suppliers_supplier where company_id=I_company_id and code='DELETETHIS';
DELETE from suppliers_supplier where company_id=I_company_id and code = '';
end$$
delimiter ;

delimiter $$
DROP PROCEDURE IF EXISTS set_customer_currency$$
create procedure set_customer_currency(IN I_company_id int)
begin

-- STORE CURRENCY ID VALUE --
select
	@SGD_currency_id := id
from currencies_currency tx where code='SGD' limit 1;

select
	@USD_currency_id := id
from currencies_currency tx where code='USD' limit 1;

select
	@YEN_currency_id := id
from currencies_currency tx where code='YEN' limit 1;

-- SET USD --
UPDATE customers_customer set
	currency_id := @USD_currency_id
where company_id=I_company_id and `code` like '%-U' and currency_id is null;

UPDATE customers_customer set
	currency_id := @USD_currency_id
where company_id=I_company_id and (`code` like '%US$%' or `name` like '%US$%') and currency_id is null;

-- SET SGD --

UPDATE customers_customer set
	currency_id := @SGD_currency_id
where company_id=I_company_id and `code` like '%-S' and currency_id is null;

UPDATE customers_customer set
	currency_id := @SGD_currency_id
where company_id=I_company_id and (`code` like '%S$%' or `name` like '%S$%') and currency_id is null;

UPDATE customers_customer set
	currency_id := @SGD_currency_id
where company_id=I_company_id and (`name` like '%PTE LTD') and currency_id is null;

UPDATE customers_customer set
	currency_id := @SGD_currency_id
where company_id=I_company_id and `code` like '%SGD' and currency_id is null;

-- SET YEN --

UPDATE customers_customer set
	currency_id := @YEN_currency_id
where company_id=I_company_id and `code` like '%-Y' and currency_id is null;

end$$
delimiter ;

call set_customer_currency(@company_id);


delimiter $$
DROP PROCEDURE IF EXISTS set_supplier_currency$$
create procedure set_supplier_currency(IN I_company_id int)
begin

-- STORE CURRENCY ID VALUE --
select
	@SGD_currency_id := id
from currencies_currency tx where code='SGD' limit 1;

select
	@USD_currency_id := id
from currencies_currency tx where code='USD' limit 1;

select
	@YEN_currency_id := id
from currencies_currency tx where code='YEN' limit 1;

-- SET USD --
UPDATE suppliers_supplier set
	currency_id := @USD_currency_id
where company_id=I_company_id and `code` like '%-U' and currency_id is null;

UPDATE suppliers_supplier set
	currency_id := @USD_currency_id
where company_id=I_company_id and (`code` like '%US$%' or `name` like '%US$%') and currency_id is null;

-- SET SGD --

UPDATE suppliers_supplier set
	currency_id := @SGD_currency_id
where company_id=I_company_id and `code` like '%-S' and currency_id is null;

UPDATE suppliers_supplier set
	currency_id := @SGD_currency_id
where company_id=I_company_id and (`code` like '%S$%' or `name` like '%S$%') and currency_id is null;

UPDATE suppliers_supplier set
	currency_id := @SGD_currency_id
where company_id=I_company_id and (`name` like '%PTE LTD') and currency_id is null;

UPDATE suppliers_supplier set
	currency_id := @SGD_currency_id
where company_id=I_company_id and `code` like '%SGD' and currency_id is null;

-- SET YEN --

UPDATE suppliers_supplier set
	currency_id := @YEN_currency_id
where company_id=I_company_id and `code` like '%-Y' and currency_id is null;

end$$
delimiter ;

call set_supplier_currency(@company_id);


delimiter $$
DROP PROCEDURE IF EXISTS set_supplier_country$$
create procedure set_supplier_country(IN I_company_id int)
begin

-- STORE COUNTRY ID VALUE --
select
	@SIN_country_id := id
from countries_country tx where code='SIN' limit 1;

select
	@USA_country_id := id
from countries_country tx where code='USA' limit 1;

select
	@MAL_country_id := id
from countries_country tx where code='MAL' limit 1;

select
	@THA_country_id := id
from countries_country tx where code='THA' limit 1;

select
	@VTN_country_id := id
from countries_country tx where code='VTN' limit 1;


-- SET USA --

UPDATE suppliers_supplier set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%US$%' and country_id is null;

-- SET SIN --
UPDATE suppliers_supplier set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%PTE LTD%' and country_id is null;

UPDATE suppliers_supplier set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%P/L%' and country_id is null;

UPDATE suppliers_supplier set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%(S)PL%' and country_id is null;

UPDATE suppliers_supplier set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%(PTE)LTD%' and country_id is null;

UPDATE suppliers_supplier set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%S$%' and country_id is null;

UPDATE suppliers_supplier set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%SINGAPORE%' and country_id is null;

-- SET MAL --

UPDATE suppliers_supplier set
	country_id := @MAL_country_id
where company_id=I_company_id and `name` like '%SDN%' and country_id is null;

-- SET THA --

UPDATE suppliers_supplier set
	country_id := @THA_country_id
where company_id=I_company_id and `code` like '%BHT%' and country_id is null;

UPDATE suppliers_supplier set
	country_id := @THA_country_id
where company_id=I_company_id and `name` like '%THAILAND%' and country_id is null;

-- SET VTN --

UPDATE suppliers_supplier set
	country_id := @VTN_country_id
where company_id=I_company_id and `name` like '%VIETNAM%' and country_id is null;


end$$
delimiter ;

call set_supplier_country(@company_id);



delimiter $$
DROP PROCEDURE IF EXISTS set_customer_country$$
create procedure set_customer_country(IN I_company_id int)
begin

-- STORE COUNTRY ID VALUE --
select
	@SIN_country_id := id
from countries_country tx where code='SIN' limit 1;

select
	@USA_country_id := id
from countries_country tx where code='USA' limit 1;

select
	@MAL_country_id := id
from countries_country tx where code='MAL' limit 1;

select
	@THA_country_id := id
from countries_country tx where code='THA' limit 1;

select
	@VTN_country_id := id
from countries_country tx where code='VTN' limit 1;


-- SET USA --

UPDATE customers_customer set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%US$%' and country_id is null;

-- SET SIN --
UPDATE customers_customer set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%PTE LTD%' and country_id is null;

UPDATE customers_customer set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%P/L%' and country_id is null;

UPDATE customers_customer set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%(S)PL%' and country_id is null;

UPDATE customers_customer set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%(PTE)LTD%' and country_id is null;

UPDATE customers_customer set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%S$%' and country_id is null;

UPDATE customers_customer set
	country_id := @SIN_country_id
where company_id=I_company_id and `name` like '%SINGAPORE%' and country_id is null;

-- SET MAL --

UPDATE customers_customer set
	country_id := @MAL_country_id
where company_id=I_company_id and `name` like '%SDN%' and country_id is null;

-- SET THA --

UPDATE customers_customer set
	country_id := @THA_country_id
where company_id=I_company_id and `code` like '%BHT%' and country_id is null;

UPDATE customers_customer set
	country_id := @THA_country_id
where company_id=I_company_id and `name` like '%THAILAND%' and country_id is null;

-- SET VTN --

UPDATE customers_customer set
	country_id := @VTN_country_id
where company_id=I_company_id and `name` like '%VIETNAM%' and country_id is null;


end$$
delimiter ;

call set_customer_country(@company_id);


delimiter $$
DROP PROCEDURE IF EXISTS clean_data$$
create procedure clean_data(IN I_company_id int)
begin
-- CLEAN UP DATA --
update customers_customer set is_hidden = 1 where `name` is null and `company_id`=I_company_id;
update suppliers_supplier set is_hidden = 1 where `name` is null and `company_id`=I_company_id;

update orders_order set update_date = '2000-01-01' where update_date = '0000-00-00';
 -- add by SF 22sep19 --
update ignore orders_order set update_date = '2000-01-01' where update_date = '0000-00-00';

end$$
delimiter ;

call clean_data(@company_id);

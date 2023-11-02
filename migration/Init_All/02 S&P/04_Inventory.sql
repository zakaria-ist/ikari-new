SET @company_id = 4;


#INSERT stockTransaction
INSERT INTO inventory_stocktransaction(
`document_date`,`document_number`,`io_flag`,`price_flag`,`remark`,
`create_date`,`update_date`,`update_by`,`is_hidden`
,`company_id`,`transaction_code_id`,`order_id`,`closing_date`,
`is_closed`,`is_from_sp`,`currency_id`,`status`,`in_location_id`,
`out_location_id`)
SELECT
    itrh_isudt document_date
    ,itrh_docno document_number
    ,itrh_ioflg io_flag
    ,itrh_prcfg price_flag
    ,itrh_rem remark
    ,itrh_isudt create_date
    ,itrh_isudt update_date
    ,null update_by
    ,0 is_hidden
	,@company_id company_id
	,(SELECT id
	    FROM inventory_transactioncode
	    WHERE company_id=@company_id
	        AND code=itrh_trncd
	        AND menu_type='1' -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	 ) transaction_code_id
	,(SELECT id
	    FROM orders_order
	    WHERE company_id=@company_id AND document_number=itrh_docno
	 ) order_id
	,itrh_ldcdt closing_date
	,(CASE
		WHEN itrh_updfg='Y' THEN 1
		WHEN itrh_updfg='N' THEN 0
		ELSE 0
	 END) is_closed
	,(CASE
		WHEN itrh_spflg='Y' THEN 1
		WHEN itrh_spflg='N' THEN 0
		ELSE 0
	 END) is_from_sp
	,(SELECT currency_id FROM companies_company WHERE id=@company_id) currency_id
	,1 status -- ORDER_STATUS['Sent'] --
	,if(itrh_ioflg=1,
	    (select id
	        from locations_location
	        where code=t2.itrd_inloc and company_id=@company_id),NULL
	 ) in_location_id
	,if(itrh_ioflg=3,
	    (select id
            from locations_location
            where code=t2.itrd_otloc and company_id=@company_id),NULL
	 ) out_location_id
FROM ikari_db_foxpro_sp.itrh_fil t1
LEFT OUTER JOIN
    (SELECT itrd_docno, itrd_inloc, itrd_otloc FROM ikari_db_foxpro_sp.itrd_fil GROUP BY itrd_docno) t2
ON t1.itrh_docno=t2.itrd_docno;



#INSERT stockTransactionDetail
INSERT INTO inventory_stocktransactiondetail(
`line_number`,`quantity`,`price`,`amount`,`remark`,
`create_date`,`update_date`,`update_by`,`is_hidden`
,`item_id`,`parent_id`,`outstanding_quantity`,`cost`,
`cost_price`,`in_location_id`,`out_location_id`)
SELECT
    itrd_line line_number
    ,itrd_qty quantity
    ,itrd_price price
    ,itrd_amt amount
    ,itrd_rem remark
	,NOW() create_date
	,NOW() update_date
    ,null update_by
    ,0 is_hidden
	,(SELECT id from items_item WHERE company_id=@company_id AND code=itrd_itmcd) item_id
	,(SELECT id from inventory_stocktransaction
		WHERE company_id=@company_id
            AND transaction_code_id =
                (SELECT id FROM inventory_transactioncode
                 WHERE company_id=@company_id
                    AND code=itrd_trncd
                    AND menu_type='1') -- TRN_CODE_TYPE_DICT['Inventory Code'] --
            and order_id =
                (SELECT id FROM orders_order
                 WHERE company_id=@company_id AND document_number=itrd_docno)
			ORDER BY `is_closed` DESC
			LIMIT 1
     ) parent_id
	,itrd_oqty outstanding_quantity
	,itrd_cost cost
	,itrd_ctprc cost_price
	,(select id from locations_location
	    where code = itrd_inloc and company_id=@company_id) in_location_id
	,(select id from locations_location
	    where code = itrd_otloc and company_id=@company_id) out_location_id
FROM ikari_db_foxpro_sp.itrd_fil
WHERE (
	SELECT id from inventory_stocktransaction
	WHERE company_id=@company_id
    AND transaction_code_id = (
    	SELECT id FROM inventory_transactioncode
        WHERE company_id=@company_id
        AND code=itrd_trncd
        AND menu_type='1') -- TRN_CODE_TYPE_DICT['Inventory Code'] --
    and order_id = (
    	SELECT id FROM orders_order
        WHERE company_id=@company_id AND document_number=itrd_docno)
	ORDER BY `is_closed` DESC
	LIMIT 1
) IS NOT NULL;



#INSERT stockTransaction history
INSERT INTO inventory_stocktransaction(
`document_date`,`document_number`,`io_flag`,`price_flag`,`remark`,
`create_date`,`update_date`,`update_by`,`is_hidden`,`company_id`,
`transaction_code_id`,`order_id`,`closing_date`,`is_closed`,`is_from_sp`,
`currency_id`,`status`,`in_location_id`,`out_location_id`)
SELECT
    itrh_isudt document_date
    ,itrh_docno document_number
    ,itrh_ioflg io_flag
    ,itrh_prcfg price_flag
    ,itrh_rem remark
    ,itrh_isudt create_date
    ,itrh_ldcdt update_date
    ,null update_by
    ,0 is_hidden
	,@company_id company_id
	,(SELECT id FROM inventory_transactioncode
	    WHERE company_id=@company_id
	        AND code=itrh_trncd
	        AND menu_type='1' -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	 ) transaction_code_id
	,(SELECT id FROM orders_order
	    WHERE company_id=@company_id AND document_number=itrh_docno) order_id
	,itrh_ldcdt closing_date
	,(CASE
		WHEN itrh_updfg='Y' THEN 1
		WHEN itrh_updfg='N' THEN 0
		ELSE 0
	 END) is_closed
	,(CASE
		WHEN itrh_spflg='Y' THEN 1
		WHEN itrh_spflg='N' THEN 0
		ELSE 0
	 END) is_from_sp
	,(SELECT currency_id FROM companies_company WHERE id=@company_id) currency_id
	,1 status -- ORDER_STATUS['Sent'] --
	,if(itrh_ioflg=1,
	    (select id from locations_location where code=t2.itrd_inloc and company_id=@company_id),NULL) in_location_id
	,if(itrh_ioflg=3,
	    (select id from locations_location where code=t2.itrd_otloc and company_id=@company_id),NULL) out_location_id
FROM ikari_db_foxpro_sp.itrh_his t1
LEFT OUTER JOIN
    (SELECT itrd_docno, itrd_inloc, itrd_otloc FROM ikari_db_foxpro_sp.itrd_his GROUP BY itrd_docno) t2
ON t1.itrh_docno=t2.itrd_docno;


#INSERT stockTransactionDetail history
INSERT INTO inventory_stocktransactiondetail(
`line_number`,`quantity`,`price`,`amount`,`remark`,
`create_date`,`update_date`,`update_by`,`is_hidden`,
`item_id`,`parent_id`,`outstanding_quantity`,`cost`,
`cost_price`,`in_location_id`,`out_location_id`)
SELECT
    itrd_line line_number
    ,itrd_qty quantity
    ,itrd_price price
    ,itrd_amt amount
    ,itrd_rem remark
    ,NOW() create_date
    ,NOW() update_date
    ,null update_by
    ,0 is_hidden
	,ii.id item_id
	,(SELECT id from inventory_stocktransaction
		WHERE company_id=@company_id
		    AND transaction_code_id =
		        (SELECT id FROM inventory_transactioncode
		            WHERE company_id=@company_id
		            AND code=itrd_trncd
		            AND menu_type='1') -- TRN_CODE_TYPE_DICT['Inventory Code'] --
		    and document_number = itrd_docno
		ORDER BY `is_closed` DESC
		LIMIT 1
     ) parent_id
	,itrd_oqty outstanding_quantity
	,itrd_cost cost
	,itrd_ctprc cost_price
	,(select id from locations_location
	    where code = itrd_inloc and company_id=@company_id) in_location_id
	,(select id from locations_location
	    where code = itrd_otloc and company_id=@company_id) out_location_id
FROM ikari_db_foxpro_sp.itrd_his ih
LEFT OUTER JOIN items_item ii ON ih.itrd_itmcd=ii.code
WHERE ii.company_id=@company_id;


delimiter $$

DROP PROCEDURE IF EXISTS update_stocktransactiondetail$$
create procedure update_stocktransactiondetail()
begin

UPDATE inventory_stocktransactiondetail
	SET 
		create_date = (SELECT create_date FROM inventory_stocktransaction WHERE company_id=@company_id AND id=inventory_stocktransactiondetail.parent_id),
		update_date = (SELECT update_date FROM inventory_stocktransaction WHERE company_id=@company_id AND id=inventory_stocktransactiondetail.parent_id);

end$$
delimiter ;

call update_stocktransactiondetail();


#INSERT inventory_incoming
INSERT INTO inventory_incoming(
`document_number`,`line_number`,`purchase_date`,`out_qty`,`unit_price`,
`balance_qty`,`create_date`,`update_date`,`update_by`,`is_hidden`,
`is_history`,`company_id`, `item_id`, `location_id`, `transaction_code_id`,
`order_id`)
SELECT
    ifrc_docno document_number
    ,ifrc_line line_number
    ,ifrc_rcdat purchase_date
    ,ifrc_oqty out_qty
    ,ifrc_price unit_price
    ,ifrc_bqty balance_qty
    ,ifrc_rcdat create_date
    ,ifrc_rcdat update_date
    ,null update_by
	,0 is_hidden
	,0 is_history
	,@company_id company_id
	,(select id from items_item
	    where company_id=@company_id and code=ifrc_itmcd) item_id
	,(select id from locations_location
	    where company_id=@company_id and code=ifrc_loccd) location_id
	,(select id from inventory_transactioncode
	    where company_id=@company_id
	        and code=ifrc_trncd
	        and menu_type='1' -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	 ) transaction_code_id
 	,(select id from orders_order
 	    where company_id=@company_id and document_number=ifrc_docno) order_id
FROM ikari_db_foxpro_sp.ifrc_fil;


#INSERT inventory_incoming history
INSERT INTO inventory_incoming(
`document_number`,`line_number`,`purchase_date`,`out_qty`,`unit_price`,
`balance_qty`,`create_date`,`update_date`,`update_by`,`is_hidden`,
`is_history`,`company_id`,`item_id`,`location_id`,`transaction_code_id`,
`order_id`)
select * from (
SELECT
    ifrc_docno document_number
    ,ifrc_line line_number
    ,ifrc_rcdat purchase_date
    ,ifrc_oqty out_qty
    ,ifrc_price unit_price
    ,ifrc_bqty balance_qty
    ,ifrc_rcdat create_date
    ,ifrc_rcdat update_date
    ,null update_by
	,0 is_hidden
	,1 is_history
	,@company_id company_id
	,ii.id item_id
	,ll.id location_id
	,(select id from inventory_transactioncode
	    where company_id=@company_id
	        and code=ifrc_trncd
	        and menu_type='1' -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	 ) transaction_code_id
	,oo.id order_id
FROM ikari_db_foxpro_sp.ifrc_his ih
    LEFT OUTER JOIN items_item ii
        ON ih.ifrc_itmcd = ii.code
            AND ii.company_id=@company_id
    LEFT OUTER JOIN locations_location ll
        ON ih.ifrc_loccd=ll.code
            and ll.company_id=@company_id
    LEFT OUTER JOIN orders_order oo
        ON ih.ifrc_docno=oo.document_number
            AND oo.company_id=@company_id
            AND oo.order_type in (5,6) -- ORDER_TYPE_DICT['PURCHASE INVOICE'], ORDER_TYPE_DICT['SALES INVOICE'] --
    ) asd
where item_id is not null;


#INSERT inventory_outgoing
INSERT INTO inventory_outgoing(
`document_number`,`line_number`,`sales_date`,`out_qty`,`in_qty`,
`unit_price`,`ref_line`,`purchase_date`,`document_line`,
`sales_price`,`create_date`,`update_date`,`update_by`,`is_hidden`,
`is_history`,`company_id`,`item_id`,`location_id`,`transaction_code_id`,
`order_id`)
SELECT
    ifis_docno document_number
    ,ifis_line line_number
    ,ifis_isdat sales_date
    ,ifis_oqty out_qty
    ,ifis_iqty in_qty
    ,ifis_price unit_price
    ,ifis_refln ref_line
    ,ifis_rcdat purchase_date
    ,ifis_docln document_line
    ,ifis_slprc sales_price
	,ifis_rcdat create_date
	,ifis_isdat update_date
	,null update_by
	,0 is_hidden
	,0 is_history
	,@company_id company_id
	,(select id from items_item
	    where company_id=@company_id and code=ifis_itmcd) item_id
	,(select id from locations_location
	    where company_id=@company_id and code=ifis_loccd) location_id
	,(select id from inventory_transactioncode
	    where company_id=@company_id
	        and code=ifis_trncd
	        and menu_type='1' -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	 ) transaction_code_id
 	,(select id from orders_order
 	    where company_id=@company_id and document_number=ifis_docno) order_id
FROM ikari_db_foxpro_sp.ifis_fil;


#INSERT inventory_outgoing history
INSERT INTO inventory_outgoing(
`document_number`,`line_number`,`sales_date`,`out_qty`,`in_qty`,
`unit_price`,`ref_line`,`purchase_date`,`document_line`,`sales_price`,
`create_date`,`update_date`,`update_by`,`is_hidden`,`is_history`,
`company_id`,`item_id`,`location_id`,`transaction_code_id`,`order_id`)
select * from (
SELECT
    ifis_docno document_number
    ,ifis_line line_number
    ,ifis_isdat sales_date
    ,ifis_oqty out_qty
    ,ifis_iqty in_qty
    ,ifis_price unit_price
    ,ifis_refln ref_line
    ,ifis_rcdat purchase_date
    ,ifis_docln document_line
    ,ifis_slprc sales_price
	,ifis_rcdat create_date
	,ifis_isdat update_date
	,null update_by
	,0 is_hidden
	,1 is_history
	,@company_id company_id
	,ii.id item_id
	,ll.id location_id
	,(select id from inventory_transactioncode
	    where company_id=@company_id
	        and code=ifis_trncd
	        and menu_type='1' -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	 ) transaction_code_id
	,oo.id order_id
FROM ikari_db_foxpro_sp.ifis_his ih
    LEFT OUTER JOIN items_item ii
        ON ih.ifis_itmcd = ii.code
            AND ii.company_id=@company_id
    LEFT OUTER JOIN locations_location ll
        ON ih.ifis_loccd=ll.code
            and ll.company_id=@company_id
    LEFT OUTER JOIN orders_order oo
        ON ih.ifis_docno=oo.document_number
            AND oo.company_id=@company_id
            AND oo.order_type in (5,6) -- ORDER_TYPE_DICT['PURCHASE INVOICE'], ORDER_TYPE_DICT['SALES INVOICE'] --
) asd
where item_id is not null;


# INSERT inventory_history
INSERT INTO inventory_history (
`year`, `month`, `io_flag`, `quantity`, `amount`,
`cost`, `create_date`, `update_date`, `update_by`,`is_hidden`,
`company_id`, `item_code_id`, `location_id`, `transaction_code_id`)
SELECT
    ihis_pyear year
    ,ihis_pmth month
    ,ihis_ioflg io_flag
    ,ihis_qty quantity
    ,ihis_amt amount
    ,ihis_cost cost
	,date_format(CONCAT(CAST(ihis_pyear AS CHAR), '-', CAST(ihis_pmth AS CHAR), '-01'),'%Y-%m-%d') create_date
	,date_format(CONCAT(CAST(ihis_pyear AS CHAR), '-', CAST(ihis_pmth AS CHAR), '-01'),'%Y-%m-%d') update_date
    ,null update_by
	,0 is_hidden
	,@company_id company_id
	,(select id from items_item
	    where company_id=@company_id and code=ihis_itmcd) item_code_id
	,(select id from locations_location
	    where company_id=@company_id and code=ihis_loccd) location_id
	,(select id from inventory_transactioncode
	    where company_id=@company_id
	        and code=ihis_trncd
	        and menu_type='1' -- TRN_CODE_TYPE_DICT['Inventory Code'] --
	 ) transaction_code_id
FROM ikari_db_foxpro_sp.ihis_fil;

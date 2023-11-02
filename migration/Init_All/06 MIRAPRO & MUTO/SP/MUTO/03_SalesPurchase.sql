#SET @company_id = 2;

#INSERT customers_customeritem
INSERT INTO customers_customeritem(
item_id, customer_id, currency_id, sales_price, new_price,
leading_days, effective_date, is_active, create_date, update_date,
update_by, is_hidden)
SELECT (
    select id from items_item where code = mptd_prtno and company_id=@company_id) item_id
	,(select id from customers_customer where code = mptd_spcs and company_id=@company_id ORDER BY id LIMIT 1) customer_id
	,COALESCE(
	    (select currency_id from customers_customer where code = mptd_spcs and company_id=@company_id ORDER BY id LIMIT 1),
	    (SELECT id from currencies_currency where code='USD')
	 ) currency_id
	,mptd_price sales_price
	,mptd_nprce new_price
	,mptd_lead leading_days
	,mptd_edate effective_date
	,1 is_active
	,mptd_lupdt create_date
	,mptd_lupdt update_date
	,null update_by
	,0 is_hidden
FROM ikari_db_foxpro_sp.mptd_fil where mptd_prity='S' and INSTR(mptd_spcs, 'TEST')=0;


#INSERT suppliers_supplieritem
INSERT INTO suppliers_supplieritem(
`item_id`,`supplier_id`,`currency_id`,`purchase_price`,`new_price`,
`leading_days`,`effective_date`,`is_active`,`create_date`,`update_date`,
`update_by`,`is_hidden`)
SELECT
    (select id from items_item where code = mptd_prtno and company_id=@company_id) item_id
	,(select id from suppliers_supplier where code = mptd_spcs and company_id=@company_id ORDER BY id LIMIT 1) supplier_id
	,COALESCE(
	    (select currency_id from suppliers_supplier where code = mptd_spcs and company_id=@company_id ORDER BY id LIMIT 1),
	    (SELECT id from currencies_currency where code='USD')
	 ) currency_id
	,mptd_price purchase_price
	,mptd_nprce new_price
	,mptd_lead leading_days
	,mptd_edate effective_date
	,1 is_active
	,mptd_lupdt create_date
	,mptd_lupdt update_date
	,null update_by
	,0 is_hidden
FROM ikari_db_foxpro_sp.mptd_fil where mptd_prity='P' and INSTR(mptd_spcs, 'TEST')=0 HAVING supplier_id IS NOT NULL;


#INSERT Sales Order Header
INSERT INTO orders_order(
`document_date`,`order_code`,`reference_number`,`due_date`,
`discount`,`subtotal`,`total`,`tax_amount`,`balance`,
`header_text`,`footer`,`note`,`remark`,`packing_number`,
`create_date`,`update_date`,`update_by_id`,`is_hidden`,
`company_id`,`cost_center_id`,`currency_id`,`customer_id`,`supplier_id`,
`tax_id`,`status`,`document_number`,`invoice_date`,`order_type`,
`parent_id`,`delivery_date`,`exchange_rate`,`is_confirm`)
SELECT
    ssoh_docdt document_date
    ,ssoh_docno order_code
    ,ssoh_refno reference_number
    ,ssoh_docdt due_date
    ,0 discount
    ,IFNULL(ssoh_oamt,0) subtotal
    ,IFNULL(ssoh_oamt,0) total
    ,0 tax_amount
    ,0 balance
	,'' header_text
	,'' footer
	,'' note
	,'' remark
	,null packing_number
	,ssoh_lupdt create_date
	,ssoh_lupdt update_date
	,null update_by_id
	,0 is_hidden
	,@company_id company_id
	,null cost_center_id
	,(select currency_id from customers_customer where code = ssoh_cuscd and company_id=@company_id ORDER BY id LIMIT 1) currency_id
	,(select id from customers_customer where code = ssoh_cuscd and company_id=@company_id ORDER BY id LIMIT 1) customer_id
	,null supplier_id
	,null tax_id
	,2 status -- ORDER_STATUS['Sent'] --
	,ssoh_docno document_number
	,ssoh_docdt invoice_date
	,1 order_type -- ORDER_TYPE_DICT['SALES ORDER'] --
	,null parent_id
	,null delivery_date
	,ssoh_xrate exchange_rate
	,SSOH_SOPRN is_confirm
FROM ikari_db_foxpro_sp.ssoh_fil;


#INSERT Sales Order Detail
INSERT INTO orders_orderitem(
`item_id`,`order_id`,`line_number`,`refer_line`,`reference_id`,
`customer_po_no`,`quantity`,`price`,`amount`,`description`,
`stock_quantity`,`delivery_quantity`,`create_date`,`update_date`,
`last_delivery_date`, `update_by_id`,`is_hidden`,
`receive_quantity`,`refer_code`,`refer_number`,`schedule_date`,`wanted_date`,
`from_currency_id`,`to_currency_id`,`exchange_rate`,`supplier_id`,`location_id`)
SELECT
    item_id item_id
    ,order_id order_id
    ,ssod_line line_number
    ,ssod_dmln refer_line
    ,null reference_id
    ,ssod_cuspo customer_po_no
	,IFNULL(ssod_qty,0) quantity
	,IFNULL(ssod_upric,0) price
	,(CAST(IFNULL(ssod_qty,0) as DECIMAL(18,6))*CAST(IFNULL(ssod_upric,0) as DECIMAL(18,6))) amount
	,ssod_rem description
	,IFNULL(ssod_oqty,0) stock_quantity
	,IFNULL(ssod_ivqty,0) delivery_quantity
	,ssod_lupdt create_date
	,ssod_lupdt update_date
	,ssod_livdt last_delivery_date
	,null update_by_id
	,0 is_hidden
	,0 receive_quantity
	,0 refer_code
	,'' refer_number
	,ssod_wantd schedule_date
	,ssod_wantd wanted_date
	,order_currency_id from_currency_id
	,order_currency_id to_currency_id
	,1 exchange_rate
	,(select id from suppliers_supplier where code = ssod_supcd and company_id=@company_id ORDER BY id LIMIT 1) supplier_id
	,(select id from locations_location where code = ssod_loccd and company_id=@company_id ORDER BY id LIMIT 1) location_id
from (
	select
	    soh.*
	    ,oo.id order_id
	    ,oo.currency_id order_currency_id
	    ,ii.id item_id
	from ikari_db_foxpro_sp.ssod_fil soh, orders_order oo, items_item ii
	where soh.ssod_docno = oo.document_number
        and soh.ssod_prtno = ii.code
        and oo.company_id=@company_id
        and ii.company_id=oo.company_id
) sod;


#INSERT Purchase Order Header
INSERT INTO orders_order(
`document_date`,`order_code`,`reference_number`,`due_date`,
`discount`,`subtotal`,`total`,`tax_amount`,`balance`,
`header_text`,`footer`,`note`,`remark`,`packing_number`,
`create_date`,`update_date`,`update_by_id`,`is_hidden`,
`company_id`,`cost_center_id`,`currency_id`,`customer_id`,`supplier_id`,`tax_id`,
`status`,`document_number`,`invoice_date`,`order_type`,`parent_id`,
`delivery_date`,`exchange_rate`, `is_confirm`)
SELECT
    ppoh_docdt document_date
    ,ppoh_docno order_code
    ,'' reference_number
    ,ppoh_docdt due_date
    ,0 discount
	,IFNULL(ppoh_oamt,0) subtotal
	,IFNULL(ppoh_oamt,0) total
	,0 tax_amount
	,0 balance
	,'' header_text
	,'' footer
	,'' note
	,PPOH_REM remark
	,NULL packing_number
	,ppoh_lupdt create_date
	,ppoh_lupdt update_date
	,null update_by_id
	,0 is_hidden
	,@company_id company_id
	,NULL cost_center_id
	,ss.currency_id currency_id
	,NULL customer_id
	,ss.id supplier_id
	,NULL tax_id
	,2 status -- ORDER_STATUS['Sent'] --
	,ppoh_docno document_number
	,ppoh_docdt invoice_date
	,2 order_type -- ORDER_TYPE_DICT['PURCHASE ORDER'] --
	,NULL parent_id
	,NULL delivery_date
	,ppoh_xrate exchange_rate
	,ppoh_poprn is_confirm
FROM ikari_db_foxpro_sp.ppoh_fil poh
LEFT OUTER JOIN suppliers_supplier ss
ON poh.ppoh_supcd=ss.code and ss.company_id=@company_id;


#INSERT Purchase Order Details
INSERT INTO orders_orderitem(
`item_id`,`order_id`,`line_number`,`refer_line`,`reference_id`,
`refer_code`,`refer_number`,`customer_po_no`,`quantity`,`price`,
`amount`,`description`,`stock_quantity`,`delivery_quantity`,`receive_quantity`,
`create_date`,`update_date`,`update_by_id`,`is_hidden`,`schedule_date`,
`wanted_date`,`last_receive_date`,`from_currency_id`,`to_currency_id`,`exchange_rate`,
`supplier_id`,`location_id`)
SELECT
    podtl.*
	,(select oi.location_id
        from orders_orderitem oi, orders_order oo
        where oo.id=podtl.reference_id
            and oo.id=oi.order_id
            and oo.company_id=@company_id
            and oo.order_type=1 -- ORDER_TYPE_DICT['SALES ORDER'] --
            and oi.line_number=podtl.refer_line limit 1) location_id
FROM (
    SELECT
        item_id item_id
        ,order_id order_id
        ,ppod_line line_number
        ,ppod_refln refer_line
        ,(SELECT id
          FROM orders_order
          WHERE document_number=ppod_refno
            and company_id=@company_id
            and order_type=1 -- ORDER_TYPE_DICT['SALES ORDER'] --
			limit 1
         ) reference_id
        ,ppod_refcd refer_code
        ,ppod_refno refer_number
        ,ppod_cuspo customer_po_no
        ,IFNULL(ppod_qty,0) quantity
        ,IFNULL(ppod_upric,0) price
        ,(CAST(IFNULL(ppod_qty,0) as DECIMAL(18,6))*CAST(IFNULL(ppod_upric,0) as DECIMAL(18,6))) amount
        ,ppod_rem description
        ,IFNULL(ppod_qty,0) stock_quantity
        ,0 delivery_quantity
        ,IFNULL(ppod_rcqty,0) receive_quantity
        ,ppod_lupdt create_date
        ,ppod_lupdt update_date
        ,NULL update_by
        ,0 is_hidden
        ,ppod_wantd schedule_date
        ,ppod_wantd wanted_date
        ,ppod_lrcdt last_receive_date
        ,ss.currency_id from_currency_id
        ,ss.currency_id to_currency_id
        ,1 exchange_rate
        ,ss.id supplier_id
    FROM (
        SELECT
            sp_pod.*
            ,oo.id order_id
            ,oo.currency_id order_currency_id
            ,ii.id item_id
        FROM ikari_db_foxpro_sp.ppod_fil sp_pod
            LEFT OUTER JOIN orders_order oo ON sp_pod.ppod_docno = oo.document_number
            LEFT OUTER JOIN items_item ii ON sp_pod.ppod_prtno = ii.code
        WHERE oo.company_id=@company_id AND ii.company_id=oo.company_id
    ) pod
LEFT OUTER JOIN suppliers_supplier ss
ON pod.ppod_supcd=ss.code AND ss.company_id=@company_id) podtl;


#INSERT Goods Receive Header
INSERT INTO orders_order(
`document_date`,`order_code`,`reference_number`,`due_date`,`discount`,
`subtotal`,`total`,`tax_amount`,`balance`,`header_text`,
`footer`,`note`,`remark`,`packing_number`,`create_date`,
`update_date`,`update_by_id`,`is_hidden`,`company_id`,`cost_center_id`,
`currency_id`,`customer_id`,`supplier_id`,`tax_id`,`status`,
`document_number`,`invoice_date`,`order_type`,`parent_id`,`delivery_date`,
`exchange_rate`,`is_confirm`,`tax_exchange_rate`, `supllier_exchange_rate`,
`document_type`)
SELECT
    pgrh_docdt document_date
    ,pgrh_docno order_code
    ,'' reference_number
    ,pgrh_docdt due_date
    ,0 discount
    ,IFNULL(pgrh_ob4tx,0) subtotal
    ,IFNULL(pgrh_otxiv,0) total
    ,IFNULL(pgrh_otxam,0) tax_amount
    ,0 balance
	,'' header_text
	,'' footer
	,'' note
	,'' remark
	,NULL packing_number
	,pgrh_lupdt create_date
	,pgrh_lupdt update_date
	,null update_by_id
	,0 is_hidden
	,@company_id company_id
	,NULL cost_center_id
	,currency_id currency_id
	,NULL customer_id
	,supplier_id supplier_id
	,tax_id tax_id
	,2 status -- ORDER_STATUS['Sent'] --
	,pgrh_docno document_number
	,pgrh_docdt invoice_date
	,5 order_type -- ORDER_TYPE_DICT['PURCHASE INVOICE'] --
	,null parent_id
	,null delivery_date
	,pgrh_xrate exchange_rate
	,pgrh_updfg is_confirm
	,pgrh_trate tax_exchange_rate
	,pgrh_supex supllier_exchange_rate
	,pgrh_docty document_type
FROM (
	SELECT pgrh.*
		,ss.id supplier_id
		,ss.currency_id
		,tx.id tax_id
	FROM ikari_db_foxpro_sp.pgrh_fil pgrh
        LEFT OUTER JOIN suppliers_supplier ss ON pgrh.pgrh_supcd=ss.code
        LEFT OUTER JOIN taxes_tax tx ON pgrh.pgrh_taxcd=tx.code
	WHERE ss.company_id=@company_id AND tx.company_id=ss.company_id
) grh;


#INSERT Goods Receive Detail
INSERT INTO orders_orderitem(
`item_id`,`order_id`,`line_number`,`customer_po_no`,`reference_id`,
`refer_line`,`refer_code`,`refer_number`,`quantity`,`price`,
`amount`,`description`,`stock_quantity`,`delivery_quantity`,
`create_date`,`update_date`,`update_by_id`,`is_hidden`,
`receive_quantity`,`schedule_date`,`wanted_date`,
`from_currency_id`,`to_currency_id`,`exchange_rate`,`supplier_id`,`location_id`)
SELECT
    ii.id item_id
    ,oo.id order_id
    ,pgrd_line line_number
    ,pgrd_cuspo customer_po_no
	,(select id
	  from orders_order
	  where document_number = pgrd_refno
	    and company_id=@company_id
	    and order_type=2 -- ORDER_TYPE_DICT['PURCHASE ORDER'] --
	    and total <> 0 -- SF add here 22sep19
		limit 1
	 ) reference_id
	,pgrd_refln refer_line
	,pgrd_refcd refer_code
	,pgrd_refno refer_number
	,IFNULL(pgrd_qty,0) quantity
	,IFNULL(pgrd_upric,0) price
	,IFNULL(pgrd_oamt,0) amount
	,pgrd_rem description
	,IFNULL(pgrd_qty,0) stock_quantity
	,0 delivery_quantity
	,pgrd_lupdt create_date
	,pgrd_lupdt update_date
	,null update_by_id
	,0 is_hidden
	,IFNULL(pgrd_qty,0) receive_quantity
	,NULL schedule_date
	,NULL wanted_date
	,oo.currency_id from_currency_id
	,oo.currency_id to_currency_id
	,1 exchange_rate
	,oo.supplier_id supplier_id
	,(select id from locations_location where code=pgrd.pgrd_locno and company_id=@company_id) location_id -- TAGA HAVE NO INVENTORY
FROM ikari_db_foxpro_sp.pgrd_fil pgrd
LEFT OUTER JOIN orders_order oo ON pgrd.pgrd_docno = oo.document_number
LEFT OUTER JOIN items_item ii ON pgrd.pgrd_prtno = ii.code
WHERE oo.company_id=@company_id AND ii.company_id=oo.company_id;


#INSERT Delivery Order Header
INSERT INTO orders_order(
`document_date`,`order_code`,`reference_number`,`due_date`,
`discount`,`subtotal`,`total`,`tax_amount`,`balance`,
`header_text`,`footer`,`note`,`remark`,`packing_number`,
`create_date`,`update_date`,`update_by_id`,`is_hidden`,
`company_id`,`cost_center_id`,`currency_id`,`customer_id`,`supplier_id`,`tax_id`,
`status`,`document_number`,`invoice_date`,`order_type`,`parent_id`,
`delivery_date`,`exchange_rate` , `is_confirm`,`tax_exchange_rate`,
`ship_from_id`, `ship_to_id`)
SELECT
    sivh_docdt document_date
    ,sivh_docno order_code
    ,NULL reference_number
    ,sivh_docdt due_date
	,0 discount
	,IFNULL(sivh_ob4tx,0) subtotal
	,IFNULL(sivh_otxiv,0) total
	,IFNULL(sivh_otxam,0) tax_amount
	,0 balance
	,'' header_text
	,'' footer
	,replace(sivh_delc,',','\n') note
	,concat(sivh_rem,'\n',sivh_rem2,'\n',sivh_rem3,'\n',sivh_rem4,'\n',sivh_rem5,'\n') remark
	,NULL packing_number
	,sivh_lupdt create_date
	,sivh_lupdt update_date
	,null update_by_id
	,0 is_hidden
	,@company_id company_id
	,NULL cost_center_id
	,cc.currency_id
	,cc.id customer_id
	,null supplier_id
	,tx.id tax_id
	,2 status -- ORDER_STATUS['Sent'] --
	,sivh_docno document_number
	,sivh_docdt invoice_date
	,6 order_type -- ORDER_TYPE_DICT['SALES INVOICE'] --
	,NULL parent_id
	,NULL delivery_date
	,SIVH_XRATE exchange_rate
	,SIVH_IVPRN is_confirm
	,sivh_trate tax_exchange_rate
	,(select id from countries_country where code like new_sivh_shpfr) ship_from_id
	,(select id from countries_country where code like new_sivh_shpto) ship_to_id
FROM (
	SELECT sivh.*
		,if(sivh_shpfr='JKT','IND',sivh_shpfr) new_sivh_shpfr
		,if(sivh_shpto='JKT','IND',sivh_shpto) new_sivh_shpto
    FROM ikari_db_foxpro_sp.sivh_fil sivh
) sivh2
LEFT OUTER JOIN customers_customer cc ON sivh2.sivh_cuscd = cc.code
LEFT OUTER JOIN taxes_tax tx ON sivh2.sivh_taxcd = tx.code
WHERE cc.company_id=@company_id and tx.company_id=cc.company_id;


#INSERT Delivery Order Detail
INSERT INTO orders_orderitem(
`item_id`,`order_id`,`line_number`,`customer_po_no`,
`reference_id`,`refer_line`,`refer_code`,`refer_number`,
`quantity`,`price`,`amount`,`description`,`stock_quantity`,`delivery_quantity`,
`create_date`,`update_date`,`update_by_id`,`is_hidden`,
`receive_quantity`,`schedule_date`,`wanted_date`,
`from_currency_id`,`to_currency_id`,`exchange_rate`,`supplier_id`,`location_id`,
`carton_no`,`carton_total`,`net_weight`,`gross_weight`,`m3_number`, `origin_country_id`)
SELECT
    ii.id item_id
    ,oo.id order_id
    ,sivd_line line_number
    ,sivd_cuspo customer_po_no
	,(select id
	  from orders_order
	  where document_number = sivd_refno
	    and company_id=@company_id
	    and order_type=1 -- ORDER_TYPE_DICT['SALES ORDER'] --
		limit 1
	) reference_id
	,sivd_refln refer_line
	,sivd_refcd refer_code
	,sivd_refno refer_number
	,IFNULL(sivd_qty,0) quantity
	,IFNULL(sivd_upric,0) price
	,IFNULL(sivd_oamt,0) amount
	,sivd_rem description
	,IFNULL(sivd_ivqty,0) stock_quantity
	,IFNULL(sivd_qty,0) delivery_quantity
	,sivd_lupdt create_date
	,sivd_lupdt update_date
	,1 update_by_id
	,0 is_hidden
	,0 receive_quantity
	,NULL schedule_date
	,NULL wanted_date
	,oo.currency_id from_currency_id
	,oo.currency_id to_currency_id
	,NULL exchange_rate
	,NULL supplier_id
	,(select id from locations_location where code=sivd.sivd_loccd and company_id=@company_id) location_id
	,sivd_ctnno carton_no
	,sivd_tcart carton_total
	,sivd_nwght net_weight
	,sivd_nwght gross_weight
	,sivd_m3 m3_number
	,(select id from countries_country where code=sivd_ctyog) origin_country_id
FROM ikari_db_foxpro_sp.sivd_fil sivd
LEFT OUTER JOIN orders_order oo ON sivd.sivd_docno = oo.document_number
LEFT OUTER JOIN items_item ii ON sivd.sivd_prtno = ii.code
WHERE oo.company_id=@company_id AND ii.company_id=oo.company_id;


delimiter $$

DROP PROCEDURE IF EXISTS update_po_reference_number$$
create procedure update_po_reference_number(IN I_company_id int)
begin

UPDATE orders_order
	SET reference_number = CASE
		WHEN company_id=I_company_id AND order_type=2
		THEN (SELECT refer_number FROM orders_orderitem WHERE order_id=orders_order.id LIMIT 1)
		END;

end$$
delimiter ;

call update_po_reference_number(@company_id);


#insert Customers Delivery Data
INSERT INTO customers_delivery(
`code`,`name`,`address`,`attention`,`phone`,
`fax`,`note_1`,`company_id`,`is_active`,`create_date`,
`update_date`,`update_by`,`is_hidden`)
SELECT
    mdel_code code
    ,mdel_name name
    ,concat(mdel_add1,'\n',mdel_add2,'\n',mdel_add3) address
	,mdel_att attention
	,mdel_tel phone
	,mdel_fax fax
	,mdel_rem1 note_1
	,@company_id company_id
	,1 is_active
	,mdel_lupdt create_date
	,mdel_lupdt update_date
	,null update_by
	,0 is_hidden
FROM ikari_db_foxpro_sp.mdel_fil;

INSERT INTO contacts_contact(
`name`,`address`,`attention`,`company_name`,`designation`,
`phone`,`fax`,`note`,`company_id`,`contact_type`,
`customer_id`,`consignee_id`,`is_active`,`create_date`,
`update_date`,`update_by`,`is_hidden`)
SELECT
    mcus_coatt name
	,concat(mcus_coad1,'\n',mcus_coad2,'\n',mcus_coad3,'\n',mcus_coad4,'\n') address
	,mcus_attn attention
	,mcus_consi company_name
	,mcus_dsgn designation
	,mcus_cotel phone
	,NULL fax
	,mcus_rem note
	,@company_id company_id
	,5 contact_type -- CONTACT_TYPES_DICT['Consignee'] --
	,(select id from customers_customer where company_id=@company_id and code=mcus_cuscd ORDER BY id LIMIT 1) customer_id
	,(select id from customers_customer where company_id=@company_id and code=mcus_cuscd ORDER BY id LIMIT 1) consignee_id
	,1 is_active
	,mcus_lupdt create_date
	,mcus_lupdt update_date
	,null update_by
	,0 is_hidden
FROM (
    SELECT mcusfil0.*
        ,(CASE
            WHEN mcusfil0.mcus_cuscr='US$' THEN 'USD'
            WHEN mcusfil0.mcus_cuscr='S$' THEN 'SGD'
            WHEN mcusfil0.mcus_cuscr='€' THEN 'EUR'
            ELSE mcusfil0.mcus_cuscr
        END ) new_mcus_cuscr
    FROM ikari_db_foxpro_sp.mcus_fil mcusfil0
) mcus_fil;


INSERT INTO contacts_contact(
`name`,`address`,`attention`,`company_name`,`designation`,
`phone`,`fax`,`note`,`company_id`,`contact_type`,
`supplier_id`,`is_active`,`create_date`,
`update_date`,`update_by`,`is_hidden`)
SELECT
    msup_attn name
	,concat(msup_supa1,'\n',msup_supa2,'\n',msup_supa3,'\n') address
	,msup_attn attention
	,null company_name
	,msup_dsgn designation
	,msup_suptl phone
	,msup_supfx fax
	-- ,msup_rem note -- remark by sf 22sep19
	 ,msup_remit note
	,@company_id company_id
	,5 contact_type -- CONTACT_TYPES_DICT['Consignee'] --
	,(select id from suppliers_supplier where company_id=@company_id and code=msup_supcd ORDER BY id LIMIT 1) supplier_id
	,1 is_active
	,msup_lupdt create_date
	,msup_lupdt update_date
	,null update_by
	,0 is_hidden
FROM ikari_db_foxpro_sp.msup_fil;


#INSERT orders_orderdelivery
INSERT INTO orders_orderdelivery(
`name`, `address`, `phone`, `note_1`, `create_date`,
`update_date`, `update_by_id`, `is_hidden`, `order_id`, `delivery_id`, `attention`)
SELECT
    cd.name name
	,concat(sivh_spad1,'\n',sivh_spad2,'\n',sivh_spad3,'\n',sivh_spad4) address
	,cd.phone phone
	,cd.note_1 note_1
	,t1.sivh_docdt create_date
	,t1.sivh_lupdt update_date
	,NULL update_by_id
	,0 is_hidden
	,t1.order_id order_id
	,cd.id delivery_id
	,cd.name name
FROM (
	SELECT
	    sivh_docno
	    ,sivh_docdt
	    ,sivh_lupdt
	    ,sivh_consi
	    ,sivh_spad1
	    ,sivh_spad2
	    ,sivh_spad3
	    ,sivh_spad4
		,oo.id order_id
	FROM ikari_db_foxpro_sp.sivh_fil sivh
	LEFT OUTER JOIN orders_order oo ON sivh.sivh_docno = oo.document_number
        where oo.company_id=@company_id
        and oo.order_type=6 -- ORDER_TYPE_DICT['SALES INVOICE'] --
        and CHAR_LENGTH(sivh_consi) > 0
    ) t1
LEFT OUTER JOIN customers_delivery cd
ON t1.sivh_consi=cd.code WHERE cd.company_id=@company_id;


INSERT INTO orders_orderdelivery(
`name`, `address`, `phone`, `note_1`, `create_date`,
`update_date`, `update_by_id`, `is_hidden`, `order_id`, `contact_id`, `attention`)
SELECT
    con.name name
	,concat(sivh_spad1,'\n',sivh_spad2,'\n',sivh_spad3,'\n',sivh_spad4) address
	,con.phone phone
	,con.note note_1
	,t1.sivh_docdt create_date
	,t1.sivh_lupdt update_date
	,NULL update_by_id
	,0 is_hidden
	,t1.order_id order_id
	,con.id contact_id
	,con.name name
FROM (
	SELECT
	    sivh_docno
		,sivh_docdt
	    ,sivh_lupdt
	    ,sivh_consi
	    ,sivh_spad1
	    ,sivh_spad2
	    ,sivh_spad3
	    ,sivh_spad4
		,oo.id order_id
		,cc.id customer_id
	FROM ikari_db_foxpro_sp.sivh_fil sivh
        LEFT OUTER JOIN orders_order oo ON sivh.sivh_docno = oo.document_number
        LEFT OUTER JOIN customers_customer cc ON sivh.sivh_cuscd = cc.code
	WHERE oo.company_id=@company_id
        AND oo.order_type=6 -- ORDER_TYPE_DICT['SALES INVOICE'] --
        AND CHAR_LENGTH(sivh.sivh_consi) <= 0
        AND cc.company_id=oo.company_id
	) t1
LEFT OUTER JOIN contacts_contact con ON t1.customer_id=con.customer_id
WHERE con.company_id=@company_id;


delimiter $$ -- add by SF 22sep19 --
DROP PROCEDURE IF EXISTS clean_data1$$
create procedure clean_data1(IN I_company_id int)
begin
-- CLEAN UP DATA --
update customers_customer set is_hidden = 1 where `name` is null and `company_id`=I_company_id;
update suppliers_supplier set is_hidden = 1 where `name` is null and `company_id`=I_company_id;

update ignore orders_order set update_date = '2000-01-01' where update_date = '0000-00-00';

end$$
delimiter ;

call clean_data1(@company_id);


delimiter $$
DROP PROCEDURE IF EXISTS set_distribution_code_and_tax$$
create procedure set_distribution_code_and_tax(IN I_company_id int)
begin

UPDATE
   suppliers_supplier
SET
   distribution_id = IF(distribution_id IS NULL,  (SELECT distribution_code_id from transactions_transaction WHERE
   journal_id = (SELECT id from accounting_journal WHERE supplier_id = suppliers_supplier.id AND
   journal_type = 2 AND company_id = I_company_id
   ORDER BY document_date LIMIT 1) ORDER BY id DESC LIMIT 1), distribution_id),

   tax_id = IF(tax_id IS NULL, (SELECT tax_id from transactions_transaction WHERE
   journal_id = (SELECT id from accounting_journal WHERE supplier_id = suppliers_supplier.id AND
   company_id = I_company_id AND journal_type = 2 ORDER BY document_date LIMIT 1) ORDER BY id DESC LIMIT 1), tax_id)

WHERE company_id = I_company_id;

UPDATE
   customers_customer
SET
   distribution_code_id = IF(distribution_code_id IS NULL, (SELECT distribution_code_id from transactions_transaction WHERE
   journal_id = (SELECT id from accounting_journal WHERE customer_id = customers_customer.id AND
   journal_type = 1 AND company_id = I_company_id ORDER BY document_date LIMIT 1) ORDER BY id DESC LIMIT 1), distribution_code_id),

   tax_id = IF(tax_id IS NULL, (SELECT tax_id from transactions_transaction WHERE
   journal_id = (SELECT id from accounting_journal WHERE customer_id = customers_customer.id AND
   journal_type = 1 AND company_id = I_company_id ORDER BY document_date LIMIT 1) ORDER BY id DESC LIMIT 1), tax_id)

WHERE company_id = I_company_id;

end$$
delimiter ;

call set_distribution_code_and_tax(@company_id);


-- UPDATE SUPPLIER_ID IN ORDERS_ORDERITEM FOR PURCHASE INVOICE
UPDATE orders_orderitem AS t1
INNER JOIN
(select d.id
     , (select oi.supplier_id
        from orders_orderitem oi
           , orders_order oo
        where oo.is_hidden = 0
        and oo.order_type = 5 -- get_gr_from_po
        and oo.id = oi.order_id
        and oi.reference_id = (
            select oi1.order_id
            from orders_orderitem oi1
               , orders_order oo1
            where oo1.is_hidden = 0
            and oo1.order_type = 2 -- get_po_from_so
            and oo1.id = oi1.order_id
            and oi1.reference_id = (
                select oi2.order_id
                from orders_orderitem oi2, orders_order oo2
                where oo2.order_type = 1 -- get_so_from_do
                and oo2.is_hidden = 0
                and oi2.order_id = oo2.id
                and oi2.order_id = d.reference_id
                and oi2.item_id = d.item_id
                and oi2.refer_line = d.refer_line
                limit 1)
            and oi1.item_id = d.item_id
            limit 1
            )
        and oi.item_id = d.item_id
        limit 1
        ) supplier_id
 from orders_orderitem d, orders_order h, customers_customer c
where d.order_id = h.id
and c.id = h.customer_id
and c.company_id = 5
and h.company_id = c.company_id
and d.is_hidden = h.is_hidden
and d.is_hidden = 0
and h.order_type = 6 -- purchase invoice
and h.status > 1 -- other than draft
and h.customer_id is not null
and d.item_id is not null) as t2 ON
(t1.id = t2.id)
SET t1.supplier_id = t2.supplier_id;

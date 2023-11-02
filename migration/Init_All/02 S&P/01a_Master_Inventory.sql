SET @company_id = 4;

-- Delete master data --
DELETE FROM locations_location
WHERE company_id=@company_id;
-- End Delete master data --


#INSERT location (this code spesific for nitto, company_is_inventory=true)
INSERT INTO locations_location(
`code`,`name`,`address`,`phone`,`fax`,`company_id`,
`pricing_type`,`stock_class`,`stock_limit`,`stock_take_date`,`stock_take_flag`,
`create_date`,`update_date`,`update_by`,`is_hidden`,`is_active`)
SELECT
    iloc_loccd code
    ,iloc_locnm name
    ,CONCAT(replace(iloc_loca1,',','\n'),CHAR(13),replace(iloc_loca2,',','\n'),CHAR(13),replace(iloc_loca3,',','\n')) address
	,iloc_ltel phone
	,iloc_lfax fax
	,@company_id company_id
	,iloc_locty pricing_type
	,iloc_stkcl stock_class
	,iloc_stklm stock_limit
	,iloc_lstdt stock_take_date
	,iloc_stflg stock_take_flag
	,iloc_lupdt create_date
	,iloc_lupdt update_date
	,null update_by
	,0 is_hidden
	,1 is_active
FROM ikari_db_foxpro_sp.iloc_fil;



#INSERT locations_locationitem (this code spesific for nitto, company_is_inventory=true)
INSERT INTO locations_locationitem(
`onhand_qty`,`onhand_amount`,`cost_price`,`in_qty`,`out_qty`,
`min_qty`,`max_qty`,`reorder_qty`,`back_order_qty`,`stock_qty`,
`last_open_qty`,`last_closing_qty`,`month_open_qty`,`month_closing_qty`,`year_open_qty`,
`is_active`,`create_date`,`update_date`,`update_by`,`is_hidden`,
`item_id`,`location_id`,`booked_amount`,`booked_qty`,`mv_cost_price`,
`mv_cost_price_flag`,`mv_qty`)
SELECT itmloc.* FROM (
SELECT
    ilst_ohqty onhand_qty
    ,ilst_ohamt onhand_amount
    ,ilst_ctprc cost_price
    ,ilst_inqty in_qty
    ,ilst_otqty out_qty
    ,ilst_loqty min_qty
    ,ilst_hiqty max_qty
    ,ilst_roqty reorder_qty
	,ilst_bkqty back_order_qty
	,ilst_stqty stock_qty
	,ilst_ldopq last_open_qty
	,ilst_ldclq last_closing_qty
	,ilst_tmopq month_open_qty
	,ilst_tmclq month_closing_qty
	,ilst_tyopq year_open_qty
	,1 is_active
	,now() create_date
	,now() update_date
	,null update_by
	,0 is_hidden
	,(select id from items_item where code = ilst_itmcd and company_id=@company_id) item_id
	,(select id from locations_location where code = ilst_loccd and company_id=@company_id) location_id
	,0 booked_amount
	,0 booked_qty
	,ilst_tmopc mv_cost_price
	,ilst_procf mv_cost_price_flag
	,ilst_procq mv_qty
FROM ikari_db_foxpro_sp.ilst_fil) itmloc
WHERE itmloc.item_id is not null;

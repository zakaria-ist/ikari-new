### WARNING : ONLY EXECUTE THIS ONLY IF WANT TO START FROM A NEW FRESH DATABASE FOR ALL COMPANY ###

/* delete from auth_user_groups where company_id=@company_id;
ALTER TABLE auth_user_groups AUTO_INCREMENT = 1;
delete from auth_user_user_permissions where user_id!=1;
ALTER TABLE auth_user_user_permissions AUTO_INCREMENT = 1;
delete from staffs_staff where company_id=@company_id;
ALTER TABLE staffs_staff AUTO_INCREMENT = 1;
delete from auth_user where id>1;
ALTER TABLE auth_user AUTO_INCREMENT = 2;
delete from companies_company where company_id=@company_id;
ALTER TABLE companies_company AUTO_INCREMENT = 1; */


# INSERT currencies
-- DELETE FROM currencies_currency where company_id=@company_id;
-- ALTER TABLE currencies_currency AUTO_INCREMENT = 1; 
-- INSERT INTO currencies_currency (`id`, `name`, `code`, `symbol`, `is_decimal`, `format`, `create_date`, `update_date`, `update_by`, `is_hidden`) VALUES
-- (1, 'Austrian Schilling', 'ATS', 'AtS', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (2, 'Australian Dollars', 'AUD', '$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (3, 'Thai Baht', 'BAH', 'ß', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (4, 'Belgian Franc', 'BEF', 'BeF', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (5, 'Canadian Dollars', 'CAD', '$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (6, 'Swiss Francs', 'CHF', 'SwF', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (7, 'People''s Rep of China Renminbi', 'CNY', 'RMB', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (8, 'Deutsche Mark', 'DEM', 'DM', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (9, 'Singapore Dollar', 'DOS', 'S$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (10, 'Spanish Peseta', 'ESP', 'Pta', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (11, 'Euro', 'EUR', '€', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (12, 'Finnish Markka', 'FIM', 'FiM', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (13, 'Fijian Dollars', 'FJD', '$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (14, 'French Francs', 'FRF', 'F', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (15, 'Pound Sterling', 'GBP', '£', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (16, 'Hong Kong Dollars', 'HKD', '$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (17, 'Indonesian Rupiah', 'IDR', 'Rp.', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (18, 'Irish Punt', 'IEP', 'Ir£', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (19, 'Italian Lira', 'ITL', 'L.', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (20, 'Laos Kip', 'KIP', 'KIP', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (21, 'Luxembourg Franc', 'LUF', 'LuF', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (22, 'Mexican Pesos', 'MXP', '$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (23, 'Malaysian Ringgit', 'MYR', 'RM', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (24, 'Netherland Guilders', 'NLG', 'f.', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (25, 'New Taiwan Dollar', 'NTD', 'NT$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (26, 'New Zealand Dollars', 'NZD', '$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (27, 'Papua New Guinea Kina', 'PGK', 'K', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (28, 'Portuguese Escudo', 'PTE', 'Esc.', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (29, 'People''s Rep of China Renminbi', 'RMB', 'RMB', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (30, 'Sri Lankan Rupees', 'SLR', 'Rs.', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (31, 'Thai Baht', 'THB', 'ß', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (32, 'U.S. Dollars', 'USD', '$', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (33, 'Viet Nam Dong', 'VND', 'VND', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (34, 'Japanese Yen', 'YEN', '¥', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (35, 'South African Rand', 'ZAR', 'R', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (36, 'South Korean Won', 'KRW', '₩', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (37, 'North Korean Won', 'KPW', '₩', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0),
-- (38, 'Philippine Peso', 'PHP', '₱', 1, NULL, '2017-04-18', '2017-04-18', NULL, 0);



# INSERT countries
-- DELETE FROM countries_country where company_id=@company_id;
-- ALTER TABLE countries_country AUTO_INCREMENT = 1;
-- INSERT INTO `countries_country` (`id`, `name`, `code`, `create_date`, `update_date`, `update_by`, `is_hidden`, `currency_id`)
-- VALUES
-- 	(1, 'SPAIN', 'SPN', now(), now(), '12', 0, 10),
-- 	(2, 'UNITED KINGDOM', 'UK', now(), now(), '1', 0, 15),
-- 	(3, 'SINGAPORE', 'SIN', now(), now(), '1', 0, 5),
-- 	(4, 'UNITED STATES', 'USA', now(), now(), '1', 0, 32),
-- 	(5, 'CHINA', 'CHI', now(), now(), '12', 0, 7),
-- 	(6, 'INDONESIA', 'IND', now(), now(), '12', 0, 17),
-- 	(7, 'HONG KONG', 'HK', now(), now(), '1', 0, 16),
-- 	(8, 'THAILAND', 'THA', now(), now(), '1', 0, 31),
-- 	(9, 'TAIWAN', 'TWN', now(), now(), '1', 0, 25),
-- 	(10, 'THAILAND', 'THA', now(), now(), '1', 0, 3),
-- 	(11, 'VIETNAM', 'VTN', now(), now(), '12', 0, 33),
--	(12, 'JAPAN', 'JPN', now(), now(), '14', 0, 34),
--	(13, 'Malaysia', 'MAL', now(), now(), '14', 0, 23),
--	(14, 'NORTH KOREA', 'KOR', now(), now(), '14', 0, 37),
--	(16, 'THAILAND', 'THA', now(), now(), '14', 0, 3),
--	(17, 'PHILIPPINES', 'PHI', now(), now(), '14', 0, 38),
--	(18, 'GERMANY', 'GER', now(), now(), '14', 0, 8),
--	(19, 'EUROPE', 'EUR', now(), now(), '14', 0, 11),
--	(20, 'BANGKOK', 'BKK', now(), now(), '14', 0, 16),
--	(21, 'SOUTH KOREA', 'SKR', now(), now(), '14', 0, 36);

# INSERT new_company
-- SET @company_id = 4;
-- SET @country_code='SIN';
-- SET @currency_code='SGD';
-- DELETE FROM companies_company WHERE id=@company_id;
-- INSERT INTO `companies_company` (`id`,`name`,`postal_code`
-- 	,`address`
-- 	,`phone`,`email`,`fax`,`logo`,`is_active`,`create_date`,`update_date`,`update_by`,`is_hidden`
-- 	,`country_id`
-- 	,`currency_id`
-- 	,`footer_logo`,`header_logo`,`is_inventory`)
-- select @company_id,'NITTO DENSEN KOUGYOU (S) PTE LTD','069046'
-- 	,'20 McCallum Street # 17 -  04. Asia Chambers. Singapore 069046' address
-- 	,'65-227-2087','nitto@c2sg.asia','65-227-9232',logo,1,now(),now(),null,0
-- 	,(select id from countries_country where code=@country_code) country_id
-- 	,(select id from currencies_currency where code=@currency_code) currency_id
-- 	,footer_logo,header_logo,1
-- from companies_company
-- where id=3;

# THIS CODE IS NOT COMPATIBLE WITH CURRENT SCRIPT SINCE CURRENT SCRIPT USE HARDCODE VALUE FOR "COMPANY_ID"
/* INSERT INTO `companies_company` (
	`id`,`name`,`postal_code`
	,`address`
	,`phone`,`email`,`fax`,`logo`,`is_active`,`create_date`,`update_date`,`update_by`,`is_hidden`
	,`country_id`
	,`currency_id`
	,`footer_logo`,`header_logo`,`is_inventory`
	,`extent_item`,`group_item`,`code_size`,`price_decimal`,`category_size`,`stock_take`,`uom_item`,`cost_method`
	)
	select @company_id,ICON_COMNM,'069046'
		,ICON_COMA1
		,'65-227-2087','nitto@c2sg.asia','65-227-9232',logo,1,now(),now(),null,0
		,(select id from countries_country where code=@country_code) country_id
		,(select id from currencies_currency where code=@currency_code) currency_id
		,footer_logo,header_logo,1
		,ICON_ITMP3,ICON_ITMGR,ICON_ITMP1,ICON_DECSZ, ICON_ITMP2 ,ICON_STTRN , ICON_MMENT ,ICON_COSMD
	from icon_fil */
# END THIS CODE IS NOT COMPATIBLE WITH CURRENT SCRIPT SINCE CURRENT SCRIPT USE HARDCODE VALUE FOR "COMPANY_ID"


# INSERT UOM
-- DETELE FROM items_itemmeasure;
-- ALTER TABLE auth_user_groups AUTO_INCREMENT = 1;
-- INSERT INTO `items_itemmeasure`
-- (`code`,`name`,`create_date`,`update_date`,`update_by`,`is_hidden`,`is_active`)
-- SELECT ICOD_CODE, ICOD_CDESC, now(), ICOD_LUPDT, 1,0,1
-- FROM icod_fil where icod_fil.ICOD_CODTY=1
-- UNION
-- SELECT 'SET','SET',now(), now(), 1,0,1;

#I NSERT transactions_transactionmethod
-- DELETE FROM transactions_transactionmethod where company_id=@company_id;
-- ALTER TABLE transactions_transactionmethod AUTO_INCREMENT = 1; 
-- INSERT INTO `transactions_transactionmethod`
-- (`code`,`name`,`create_date`,`update_date`,`update_by`,`is_hidden`,`company_id`)
-- SELECT DCOD_CODE, DCOD_CDESC, now(),DCOD_LUPDT,null,0,@company_id
-- FROM dcod_fil where DCOD_CODTY=4
-- union
-- select 'TRF','INTERNAL TRANSFER', now(),now(),null,0,@company_id;
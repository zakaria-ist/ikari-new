#SET @company_id = 1;

DELETE FROM accounting_apglintegrationdetail
where parent_id in (select id from accounting_apglintegration
where company_id=@company_id);
ALTER TABLE accounting_apglintegrationdetail AUTO_INCREMENT = 1;

DELETE FROM accounting_apglintegration
where company_id=@company_id;
ALTER TABLE accounting_apglintegration AUTO_INCREMENT = 1;

DELETE FROM accounting_arglintegrationdetail
where parent_id in (select id from accounting_arglintegration
where company_id=@company_id);
ALTER TABLE accounting_arglintegrationdetail AUTO_INCREMENT = 1;

DELETE FROM accounting_arglintegration
where company_id=@company_id;
ALTER TABLE accounting_arglintegration AUTO_INCREMENT = 1;


INSERT INTO accounting_arglintegration(
`transaction_type`, `transaction_field`, `company_id`, `create_date`,
`update_date`, `update_by`, `is_active`, `is_hidden`)
VALUES
	( '100', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '100', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '100', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '100', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '101', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '101', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '101', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '201', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '201', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '201', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '301', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '301', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '301', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '401', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '401', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '401', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '402', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '402', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '402', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '701', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '701', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '701', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '800', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '800', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '800', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '800', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '801', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '801', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '801', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	-- ( '900', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '900', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '900', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '900', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '901', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '901', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '901', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1000', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1000', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1000', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1000', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1001', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1001', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1001', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1101', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1101', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1101', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1300', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1300', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1300', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1300', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0);


INSERT INTO accounting_apglintegration(
`transaction_type`, `transaction_field`, `company_id`, `create_date`,
`update_date`, `update_by`, `is_active`, `is_hidden`)
VALUES
	( '100', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '100', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '100', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '100', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
    ( '101', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '101', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '101', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '200', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
    ( '201', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '201', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '201', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '300', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
    ( '301', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '301', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '301', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '400', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
    ( '401', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '401', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '401', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '402', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '402', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '402', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '500', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '600', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '601', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '601', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '601', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '700', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
    ( '701', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '701', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '701', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	-- ( '800', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '800', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '800', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '800', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
    ( '801', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '801', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '801', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '900', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '900', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '900', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '900', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
    ( '901', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '901', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '901', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '0', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '1', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '2', @company_id, '2019-01-01', '2019-01-01', null, 1, 0),
	( '1100', '3', @company_id, '2019-01-01', '2019-01-01', null, 1, 0);

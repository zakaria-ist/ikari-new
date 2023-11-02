#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR TAGA)
set @company_id = 42;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4006', '4007', '4008', '4009', '4010', '4011', 
	'4012', '4013', '4014', '4015', '4016', '4017', '4018');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4500', '4509', '4510', '4511', '4512', '4515', 
	'4516', '4517', '4518', '4519', '4520', '4521', '4900');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4021', '4022', '4023', '4024', '4025', '4026',
	'4027', '4028', '4029', '4030', '4031', '4032');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5000', '5001', '5002', '5003', '5004', '5009', '5010', '5011', '5012', '5013', 
	'5018', '5019', '5020', '5021', '5022', '5023', '5024', '5028', '5029', '5030', '5031', '5032',
	'5034', '5035', '5036', '5042', '5050', '5051', '5060', '5061', '5070', '5079', '5080', '5081',
	'5082', '5084', '5085', '5088', '5125', '5126', '5127', '5130', '5139', '5140', '5141', '5142',
	'5200', '5201', '5202', '5209', '5210', '5211', '5215', '5216', '5219', '5220', '5221', '5222',
	'5223', '5224', '5225', '5226', '5227', '5228', '5229', '5230', '5231', '5232', '5233', '5234',
	'5235', '5236', '5237', '5238', '5239', '5240', '5241', '5242', '5243', '5244', '5245', '5246', 
	'5247', '5248', '5249', '5250', '5251', '5252', '5253', '5254', '5255', '5256', '5257', '5258',
	'5259', '5260', '5261', '5262', '5263', '5264', '5265', '5266', '5267', '5268', '5269', '5270',
	'5271', '5272', '5273');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment like upper('%fore%exch%gain%');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment = '5040';

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-FA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1000', '1150', '1010', '1160', '1020', '1170', '1030', '1080', '1040', '1185') ;

-- MIRAPRO doesn't have NA
-- update accounts_account
-- set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
-- where company_id=@company_id
-- and account_segment in ('1190', '1195');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3501', '1204', '1205', '1400', '1401', '1420', '1430', '1431', '1432',
	'1433', '1434', '1435', '1436', '1437', '1438', '1439', '1440', '1450', '1480', '1500',
	'2107', '1600', '1601', '1602', '1603', '1604', '1605', '1606', '1607', '1608', '1609', '1610');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1801','1901','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009',
	'2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024',
	'2025','2026','2027','2028','2029','2030','2031','2032','2033','2034','2035','2036','2037','2038','2039',
	'2040','2041','2042','2043','2044','2045','2046','2047','2048','2049','2050','2051','2052','2053','2054',
	'2055','2056','2057','2058','2059','2060','2061','2062','2063','2064','2065','2066','2067','2068','2069',
	'2070','2071','2072','2073','2074','2075','2076','2077','2078','2079','2080','2081','2082','2083','2084',
	'2085','2086','2087','2088','2089','2090','2091','2092','2093','2094','2095','2096','2097','2098','2099',
	'2100','2101','2102','2103','2104','2105','2351','2380','2381','3002');

-- SENTIAL doesn't have BS-LL
-- update accounts_account
-- set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-LL' and category='2' AND company_id=@company_id)
-- where company_id=@company_id
-- and account_segment='3100';

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3500','3900');



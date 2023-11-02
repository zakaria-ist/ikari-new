#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR TAGA)
#set @company_id = 5;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('511', '512', '513');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('531', '541', '542', '561');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('810', '811', '812', '819');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('533', '679', '709', '710', '711', '712', '713',
'721', '724', '725', '726', '727', '728', '729','731','732', '733', '735', '736', '738', '739',
'741', '742', '743', '746', '747', '750', '751','752', '753', '754', '755', '762', '763', '779',
'780', '790', '791', '822');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
-- and account_segment like upper('%fore%exch%gain%'); --this line is need a review
and name like upper('%exch%gain%');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('817', '820');

-- -- TAGA have no FIXED ASSET
-- update accounts_account
-- set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-FA' and category='2' AND company_id=@company_id)
-- where company_id=@company_id
-- and account_segment in ('1000', '1001') ;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('215','216','218','110');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('115','120','121','122','148','152','153','154','178','181','185',
	'243','245','248');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('312','313','314','322','323','328','335','339');

-- -- TAGA have no LONG TERM LIABILITIES
-- update accounts_account
-- set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-LL' and category='2' AND company_id=@company_id)
-- where company_id=@company_id
-- and account_segment='3100';

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('411','437');

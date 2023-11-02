#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR TAGA)
#set @company_id = 1;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4001', '4002', '4003', '4004', '4010');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4500', '4510', '4511' '4512', '4513', '4514', '5011', '4550');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4024', '4025', '4026', '4027', '4028');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5005', '5009', '5010', '5015', '5030', '5031', '5035', '5036', '5037', '5038', '5040', '5050',
		'5051', '5060', '5065', '5100', '5120', '5145', '5146', '5150', '5200', '5201', '5202', '5401', '5402', '5403',
		'5404', '5405', '5500', '5501', '5502', '5503', '5504', '5506', '5600', '5601', '5602', '5603', '5605');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment like upper('%fore%exch%gain%');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5041', '6000');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-FA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1000', '1001', '1010', '1011') ;

-- MIRAPRO doesn't have NA
-- update accounts_account
-- set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
-- where company_id=@company_id
-- and account_segment in ('1190', '1195');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1100', '1150', '1151', '1200', '1201', '1202', '1203', '1204', '1205', '1250', '1400', '1430',
		'1450', '1480', '1550', '1600', '1601', '1602', '1603', '1604', '1605', '1606', '1700', '2381');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('2000', '2001', '2002', '2003', '2004', '2005', '2100', '2101', '2351', '2380', '2400');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-LL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment='3100';

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3000', '3010', '3500');

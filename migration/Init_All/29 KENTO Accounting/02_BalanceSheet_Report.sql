#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR CROWN)
SET @company_id = 6; -- 6 = Kento

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4001', '4002', '4003', '4004', '4005', '4006', '4007', '4008', '4010', '5011');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4500', '4510', '4511', '4512', '4900');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4024', '4025', '4026');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5000', '5003', '5004', '5005', '5006', '5007', '5010', '5012', '5013', '5014', '5020', '5021', '5022', '5023',
             '5024', '5030', '5031', '5032', '5033', '5034', '5035', '5036', '5037', '5039', '5041', '5042', '5060', '5080', '5081', '5082', '5083',
             '5084', '5085', '5125', '5140', '5200', '5201', '5202', '5205', '5210', '5219', '5220', '5221', '5222', '5223', '5224', '5225', '5227',
             '5228', '5229', '5230', '5231', '5232', '5233', '5234', '5235', '5260');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment like upper('%fore%exch%gain%');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('6001', '6002');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-FA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1000', '1010', '1020', '1150', '1160', '1170');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1191');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1204', '1208', '1400', '1430', '1450', '1480', '1500', '1601', '1602', '1603',
                '1604');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('2100', '2101', '2103', '2351', '2380', '2381', '3004');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3500', '3900');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-LL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment='3100';

#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR CROWN)
set @company_id = 3;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4001', '4002', '4003', '4004', '4005');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4500', '4511', '4512', '4513', '4514', '4515', '4550');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4024', '4025', '4026');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5001', '5003', '5011', '5021', '5031', '5032', '5033', '5034', '5035', '5044', '5051', '5061', '5062', '5065', '5068',
             '5071', '5201', '5202', '5203', '5212', '5213', '5221', '5222', '5223', '5224', '5225', '5231', '5232', '5233');

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
and account_segment in ('1000', '1001') ;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1190', '1195');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1100', '1200', '1201', '1202', '1204', '1400', '1430', '1450', '1480', '1550', '1601', '1602', '1603', '1604',
             '1700', '2381');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('2000', '2001', '2002', '2004', '2006', '2100', '2101', '2351', '2380');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3000', '3500');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-LL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment='3100';


#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR FRONT)
set @company_id = 5;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4001', '4002', '4003', '4004', '4005', '4006', '4007', '4008', '4009', '4010', '4011', '4012', '5011');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4500', '4510', '4511', '4512', '4513', '4514', '4515', '4900');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4025');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5000', '5003', '5004', '5005', '5006', '5010', '5012', '5013', '5014', '5020', '5021', '5022', '5023',
'5030', '5031', '5032', '5033', '5034', '5035', '5036', '5037', '5039', '5041', '5042', '5060', '5080', '5081', '5082', '5083',
'5125', '5140', '5200', '5201', '5202', '5205', '5210', '5220', '5221', '5222', '5223', '5224', '5225', '5227', '5228', '5229',
'5230', '5231', '5232', '5233', '5234', '5235', '5260');

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
and account_segment in ('1000', '1150', '1010', '1160', '1020', '1170') ;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1191');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1200', '1201', '1202', '1203', '1204', '1205', '1206', '1208', '1400', '1430', '1450', '1480', '1500', '1601', '1602', '1603');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('2100', '2101', '2103', '2351', '2380', '2381', '3004');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3500', '3900');


#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR Nitto)
set @company_id = 4;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4001', '4002', '4003', '4004', '4005');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4500', '4510', '4511', '4512', '4513', '4514', '4530', '4550');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4024', '4025', '4026', '4027');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5005', '5007', '5010', '5021', '5030', '5034', '5035', '5036', '5038', '5041', '5050', '5060', '5070',
            '5075', '5080', '5090', '5200', '5201', '5202', '5204', '5402', '5500', '5501', '5502', '5503', '5506', '5600', '5601', '5603');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment like upper('%fore%exch%gain%');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5040', '6000');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-FA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1000', '1001') ;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1040', '1041');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1100', '1150', '1200', '1201', '1202', '1203', '1204', '1205', '1206', '1400', '1430', '1450', '1480', '1550', '1601', '1602', '1603', '1604',
             '1605', '1606', '1607', '1608', '1650', '2381');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('2000', '2001', '2002', '2003', '2004', '2099', '2100', '2101', '2351', '2352', '2380', '2400');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3000', '3500');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-LL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment='3100';

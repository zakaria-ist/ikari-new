
#SETUP FOR BALANCE_SHEET REPORTS (SPECIFIC ONLY FOR Ikari)
-- set @company_id = 8;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-NETSALE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4001', '4002', '4003', '4004', '4005', '4006', '4007', '4008', '4009', '4020', '4022', '4028', '4029', '4031');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-COGS' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4500', '4508', '4509', '4510', '4511', '4512', '4513', '4514', '4515', '4517', '4518', '4519', '4520', '4521', '4900');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-REVENUE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('4021', '4023', '4024', '4025', '4026', '4027', '4030', '5143');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXPENSE' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5000', '5001', '5002', '5003', '5004', '5005', '5007', '5010', '5011', '5020', '5022', '5024', '5025', '5021', '5030', '5031',
            '5032', '5033', '5034', '5035', '5036', '5037', '5038', '5043', '5044', '5050', '5051', '5060', '5070', '5079',
            '5075', '5080', '5081', '5082', '5083', '5084', '5085', '5086', '5087', '5090', '5120', '5125', '5139', '5140', '5141', '5200', '5201',
            '5202', '5203', '5205', '5210', '5211', '5218', '5219', '5220', '5221', '5222', '5223', '5224', '5225', '5226', '5227', '5229', '5230',
            '5231', '5232', '5233', '5234', '5236', '5241', '5242', '5243', '5244', '5245', '5247', '5248', '5249', '5260', '5262');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment like upper('%fore%exch%gain%');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='PL-EXC' and category='3' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('5040', '5041', '5042', '5045', '6000');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-FA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1000', '1010', '1020', '1030', '1150', '1155', '1160', '1165') ;

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-NA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1040', '1041');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CA' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('1190', '1200', '1201', '1202', '1203', '1204', '1400', '1410', '1430', '1450', '1451', '1461', '1480', '1500', '1550', '1601', '1602', '1603', '1604',
             '1605', '1606', '1607', '1608', '1610', '1630', '1631', '1632', '1635', '1636', '1637');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-CL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('2000', '2001', '2002', '2003', '2004', '2005', '2099', '2100', '2101', '2201', '2202', '2203', '2204', '2205', '2206',
             '2207', '2351', '2380', '2381', '3002');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-SE' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment in ('3500', '3501', '3900');

update accounts_account
set  profit_loss_group_id= (select id from accounts_accounttype where code='BS-LL' and category='2' AND company_id=@company_id)
where company_id=@company_id
and account_segment='3100';

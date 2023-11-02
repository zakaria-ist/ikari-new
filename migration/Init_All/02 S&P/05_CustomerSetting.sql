-- For Crown Only --
set @company_id=3;
-- Customer --
update customers_customer as t1, (select id from accounts_accountset where code='TDDUSD' and company_id=@company_id) as t2
set t1.account_set_id = t2.id, t1.interest_profile_id = t2.id
where t1.code in ('YEM-U', 'YES-U', 'DAIKIN-U', 'FCI-U') and t1.company_id=@company_id;

update customers_customer as t1, (select id from accounts_accountset where code='TDDYEN' and company_id=@company_id) as t2
set t1.account_set_id = t2.id, t1.interest_profile_id = t2.id
where t1.code in ('IKARI-Y', 'YES-Y') and t1.company_id=@company_id;

-- Supplier --
update suppliers_supplier as t1, (select id from accounts_accountset where code='TCDUSD' and company_id=@company_id) as t2
set t1.account_set_id = t2.id
where t1.code in ('HANJIN-U', 'NICHI-U') and t1.company_id=@company_id;

update suppliers_supplier as t1, (select id from accounts_accountset where code='TCDYEN' and company_id=@company_id) as t2
set t1.account_set_id = t2.id
where t1.code = 'SUNTEC-Y' and t1.company_id=@company_id;


-- For Nitto Only --
set @company_id=4;
-- Customer --
update customers_customer as t1, (select id from accounts_accountset where code='REDUSD' and company_id=@company_id) as t2
set t1.account_set_id = t2.id, t1.interest_profile_id = t2.id
where t1.code='NNEG-U' and t1.company_id=@company_id;

update customers_customer as t1, (select id from accounts_accountset where code='REDYEN' and company_id=@company_id) as t2
set t1.account_set_id = t2.id, t1.interest_profile_id = t2.id
where t1.code='N(T)-Y' and t1.company_id=@company_id;

update customers_customer as t1, (select id from accounts_accountset where code='TDDYEN' and company_id=@company_id) as t2
set t1.account_set_id = t2.id, t1.interest_profile_id = t2.id
where t1.code='IPI-Y' and t1.company_id=@company_id;

update customers_customer as t1, (select id from accounts_accountset where code='TDDUSD' and company_id=@company_id) as t2
set t1.account_set_id = t2.id, t1.interest_profile_id = t2.id
where t1.code in ('PJVM-U', 'JVC-U', 'YEM-U', 'YES-U', 'JVM-U', 'HIGA-I-U', 'KNT-U', 'JPA-U', 'IK') and t1.company_id=@company_id;

update customers_customer as t1, (select id from accounts_accountset where code='TDDSGD' and company_id=@company_id) as t2
set t1.account_set_id = t2.id, t1.interest_profile_id = t2.id
where t1.code in ('TAISHO-S', 'IK-S') and t1.company_id=@company_id;

-- Supplier --
update suppliers_supplier as t1, (select id from accounts_accountset where code='TCDUSD' and company_id=@company_id) as t2
set t1.account_set_id = t2.id
where t1.code in ('IK-U', 'CHUO-U', 'MINEB-U', 'CCS-U', 'XYRIX-U', 'SMY-U', 'MP-U') and t1.company_id=@company_id;

update suppliers_supplier as t1, (select id from accounts_accountset where code='TCDSGD' and company_id=@company_id) as t2
set t1.account_set_id = t2.id
where t1.code in ('IK-S', 'AMP-S', 'DID-S', 'GT-S', 'MINEB-S') and t1.company_id=@company_id;

update suppliers_supplier as t1, (select id from accounts_accountset where code='TCDYEN' and company_id=@company_id) as t2
set t1.account_set_id = t2.id
where t1.code = 'MORIMI-Y' and t1.company_id=@company_id;

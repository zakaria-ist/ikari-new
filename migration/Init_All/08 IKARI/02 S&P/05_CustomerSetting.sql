-- Need to update for Ikari Only --
set @company_id=8;

/* UPDATE customers_customer as t1,
(select account_set_id, interest_profile_id from customers_customer where company_id=@company_id and code='KAYABA-U') as t2
set
	t1.account_set_id = t2.account_set_id,
	t1.interest_profile_id = t2.interest_profile_id
where t1.company_id=@company_id and t1.code='FCI-U';

UPDATE customers_customer as t1,
(select account_set_id, interest_profile_id from customers_customer where company_id=@company_id and code='KAYABA-U') as t2
set
	t1.account_set_id = t2.account_set_id,
	t1.interest_profile_id = t2.interest_profile_id
where t1.company_id=@company_id and t1.code='DAIKIN-U';

UPDATE customers_customer as t1,
(select account_set_id, interest_profile_id from customers_customer where company_id=@company_id and code='SANKO-U') as t2
set
	t1.account_set_id = t2.account_set_id,
	t1.interest_profile_id = t2.interest_profile_id
where t1.company_id=@company_id and t1.code in ('YEM-U', 'YES-U');

UPDATE customers_customer as t1,
(select account_set_id, interest_profile_id from customers_customer where company_id=@company_id and code='IKARI-Y') as t2
set
	t1.account_set_id = t2.account_set_id,
	t1.interest_profile_id = t2.interest_profile_id
where t1.company_id=@company_id and t1.code='YES-Y';

update accounting_journal as t1,
(select account_set_id, id from customers_customer where company_id=@company_id and code='FCI-U') as  t2
	set t1.account_set_id = t2.account_set_id
where t1.company_id=@company_id and customer_id=t2.id; */

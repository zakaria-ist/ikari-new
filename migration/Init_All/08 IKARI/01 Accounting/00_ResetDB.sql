### RESET IKARI DB ###
-- SET @company_id = 8; -- 3 = Crown, 4 = Nitto, 5 = Front
SET FOREIGN_KEY_CHECKS=0;

SHOW WARNINGS;

# UPDATE COMPANIES_COMPANY
SET @company_curr_month = (SELECT ICON_CMTH FROM ikari_db_foxpro_sp.icon_fil);
SET @company_curr_year = (SELECT ICON_CYEAR FROM ikari_db_foxpro_sp.icon_fil);
SET @company_closing_date = (SELECT ICON_LDCDT FROM ikari_db_foxpro_sp.icon_fil);
UPDATE companies_company set
    fiscal_period = (SELECT DATE_ADD(@company_closing_date, INTERVAL 1 MONTH)),
    current_period_month = @company_curr_month,
    current_period_year = @company_curr_year,
    closing_date = @company_closing_date
where id=@company_id;


# DELETE ACC TRANSACTIONS DATA
delete from transactions_transactionmethod
where company_id=@company_id;
ALTER TABLE transactions_transactionmethod AUTO_INCREMENT = 1;

INSERT INTO transactions_transactionmethod (
    `name`, `code`, `is_debit`, `is_credit`, `company_id`, `is_hidden`, `update_by`, `create_date`, `update_date`)
VALUES
    ('Check', 'CHQ', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Chash', 'CSH', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Credit', 'CRE', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Letter of Credit', 'L/C', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('B/L at sight', 'B/L', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('Telegraphic Transfer', 'TT', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01'),
    ('INTERNAL TRANSFER', 'TRF', 0, 0, @company_id, 0, null, '2017-01-01', '2017-01-01');


delete from transactions_transaction
where company_id=@company_id;
ALTER TABLE transactions_transaction AUTO_INCREMENT = 1;

delete from accounting_journal
where company_id=@company_id;
ALTER TABLE accounting_journal AUTO_INCREMENT = 1;

delete from accounting_batch
where company_id=@company_id;
ALTER TABLE accounting_batch AUTO_INCREMENT = 1;
# END DELETE ACC TRANSACTIONS DATA


# DELETE S/P TRANSACTIONS DATA
DELETE FROM orders_orderitem
where order_id in (select id from orders_order where company_id=@company_id);
ALTER TABLE orders_orderitem AUTO_INCREMENT = 1;

DELETE FROM orders_orderdelivery
where order_id in (select id from orders_order where company_id=@company_id);
ALTER TABLE orders_orderdelivery AUTO_INCREMENT = 1;

DELETE FROM orders_orderheader
where order_id in (select id from orders_order where company_id=@company_id);
ALTER TABLE orders_orderheader AUTO_INCREMENT = 1;

DELETE FROM inventory_incoming
where company_id=@company_id;
ALTER TABLE inventory_incoming AUTO_INCREMENT = 1;

DELETE from inventory_outgoing
where company_id=@company_id;
ALTER TABLE inventory_outgoing AUTO_INCREMENT = 1;

DELETE FROM inventory_history
WHERE company_id=@company_id;
ALTER TABLE inventory_history AUTO_INCREMENT = 1;

DELETE FROM inventory_stocktransactiondetail
where parent_id in (select id from inventory_stocktransaction where company_id=@company_id);
ALTER TABLE inventory_stocktransactiondetail AUTO_INCREMENT = 1;

DELETE FROM inventory_stocktransaction
where company_id=@company_id;
ALTER TABLE inventory_stocktransaction AUTO_INCREMENT = 1;

DELETE FROM orders_order
where company_id=@company_id;
ALTER TABLE orders_order AUTO_INCREMENT = 1;
# END DELETE S/P TRANSACTIONS DATA


# Delete ICS & S/P master data
DELETE FROM customers_delivery
WHERE company_id=@company_id;
ALTER TABLE customers_delivery AUTO_INCREMENT = 1;

DELETE FROM contacts_contact
WHERE company_id=@company_id;
ALTER TABLE contacts_contact AUTO_INCREMENT = 1;

DELETE FROM customers_customeritem
where item_id in (select id from items_item where company_id=@company_id);
ALTER TABLE customers_customeritem AUTO_INCREMENT = 1;

DELETE FROM customers_customer
where company_id=@company_id;
ALTER TABLE customers_customer AUTO_INCREMENT = 1;

DELETE FROM suppliers_supplieritem
where item_id in (select id from items_item where company_id=@company_id);
ALTER TABLE suppliers_supplieritem AUTO_INCREMENT = 1;

DELETE FROM suppliers_supplier
where company_id=@company_id;
ALTER TABLE suppliers_supplier AUTO_INCREMENT = 1;

DELETE FROM locations_locationitem
where item_id in (select id from items_item
where company_id=@company_id);
ALTER TABLE locations_locationitem AUTO_INCREMENT = 1;

DELETE FROM locations_location
WHERE company_id=@company_id;
ALTER TABLE locations_location AUTO_INCREMENT = 1;

DELETE FROM items_item
where company_id=@company_id;
ALTER TABLE items_item AUTO_INCREMENT = 1;

DELETE FROM items_itemcategory
where company_id=@company_id;
ALTER TABLE items_itemcategory AUTO_INCREMENT = 1;

DELETE FROM inventory_transactioncode
WHERE company_id=@company_id;
ALTER TABLE inventory_transactioncode AUTO_INCREMENT = 1;
# End Delete ICS & S/P master data


# DELETE ACC MASTER DATA
delete from accounting_paymentcode
where company_id=@company_id;
ALTER TABLE accounting_paymentcode AUTO_INCREMENT = 1;

delete from accounting_aroptions
where company_id=@company_id;
ALTER TABLE accounting_aroptions AUTO_INCREMENT = 1;

delete from accounting_apoptions
where company_id=@company_id;
ALTER TABLE accounting_apoptions AUTO_INCREMENT = 1;

delete from accounts_accountcurrency
where account_id in (select id from accounts_account where company_id=@company_id);
delete from accounts_accountcurrency
where name in (select code from accounts_account where company_id=@company_id);
ALTER TABLE accounts_accountcurrency AUTO_INCREMENT = 1;

delete from accounts_accounthistory
where company_id=@company_id;
ALTER TABLE accounts_accounthistory AUTO_INCREMENT = 1;

delete from accounts_accountset
where company_id=@company_id;
ALTER TABLE accounts_accountset AUTO_INCREMENT = 1;

delete from accounts_revaluationcode
where company_id=@company_id;
ALTER TABLE accounts_revaluationcode AUTO_INCREMENT = 1;

delete from accounting_revaluationdetails
where posting_id in (select id from accounting_revaluationlogs where company_id=@company_id);
ALTER TABLE accounting_revaluationdetails AUTO_INCREMENT = 1;

delete from accounting_revaluationlogs
where company_id=@company_id;
ALTER TABLE accounting_revaluationlogs AUTO_INCREMENT = 1;

delete from banks_bank
where company_id=@company_id;
ALTER TABLE banks_bank AUTO_INCREMENT = 1;

DELETE FROM taxes_tax
WHERE company_id=@company_id;
ALTER TABLE taxes_tax AUTO_INCREMENT = 1;

delete from taxes_taxgroup
where company_id=@company_id;
ALTER TABLE taxes_taxgroup AUTO_INCREMENT = 1;

delete from taxes_taxauthority
where company_id=@company_id;
ALTER TABLE taxes_taxauthority AUTO_INCREMENT = 1;

-- update accounts_distributioncode set gl_account_id = null where company_id=4; --
delete from accounts_distributioncode
where company_id=@company_id;
ALTER TABLE accounts_distributioncode AUTO_INCREMENT = 1;

delete from accounts_reportgroup
where company_id=@company_id;
ALTER TABLE accounts_reportgroup AUTO_INCREMENT = 1;

delete from accounts_account
where company_id=@company_id;
ALTER TABLE accounts_account AUTO_INCREMENT = 1;

delete from accounts_accounttype
where company_id is null; -- this line is spesific for crown only
delete from accounts_accounttype
where company_id=@company_id;
ALTER TABLE accounts_accounttype AUTO_INCREMENT = 1;

delete from accounting_fiscalcalendar
where company_id=@company_id;
ALTER TABLE accounting_fiscalcalendar AUTO_INCREMENT = 1;

delete from companies_costcenters
where company_id=@company_id;
ALTER TABLE companies_costcenters AUTO_INCREMENT = 1;

delete from currencies_exchangerate
where company_id=@company_id;
ALTER TABLE currencies_exchangerate AUTO_INCREMENT = 1;
# END DELETE ACC MASTER DATA


#insert accounts_accounttype
INSERT INTO accounts_accounttype(
`name`, `code`, `is_debit`, `is_credit`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `category`)
SELECT
    ACCTGRPDES name
    ,ACCTGRPCOD code
    ,0 is_debit
    ,0 is_credit
    ,date_format(AUDTDATE,'%Y-%m-%d') create_date
    ,date_format(AUDTDATE,'%Y-%m-%d') update_date
    ,NULL update_by
    ,0 is_hidden
    ,@company_id company_id
    ,1 category
FROM ikari_db_sage300.glacgrp;

/* INSERT INTO accounts_accounttype(
`name`, `code`, `is_debit`, `is_credit`, `create_date`,
`update_date`, `update_by`, `is_hidden`, `company_id`, `category`)
VALUES
	( 'NET SALES', 'PL-NETSALE', 1, 1, '2017-01-19', '2017-01-19', '2', 0, @company_id, '3'),
	( 'COST OF GOOD SOLD', 'PL-COGS', 1, 1, '2017-01-19', '2017-01-19', '2', 0, @company_id, '3'),
	( 'OTHER REVENUE', 'PL-REVENUE', 1, 1, '2017-01-19', '2017-01-19', '2', 0, @company_id, '3'),
	( 'TOTAL EXPENDITURE', 'PL-EXPENSE', 1, 1, '2017-01-19', '2017-01-19', '2', 0, @company_id, '3'),
	( 'TOTAL EXCHANGE GAIN/LOSS', 'PL-EXC', 1, 1, '2017-01-19', '2017-01-19', '2', 0, @company_id, '3'),
	( 'PURCHASE', 'PL-PURCH', 1, 1, '2017-01-19', '2017-01-19', '2', 0, @company_id, '3'),
	( 'TOTAL FIXED ASSETS', 'BS-FA', 1, 1, '2017-02-09', '2017-02-09', '2', 0, @company_id, '2'),
	( 'TOTAL NON ASSETS', 'BS-NA', 1, 1, '2017-02-09', '2017-02-09', '2', 0, @company_id, '2'),
	( 'TOTAL CURRENT ASSETS', 'BS-CA', 1, 1, '2017-02-09', '2017-02-09', '2', 0, @company_id, '2'),
	( 'TOTAL CURRENT LIABILITIES', 'BS-CL', 1, 1, '2017-02-09', '2017-02-09', '2', 0, @company_id, '2'),
	( 'TOTAL LONG-TERM LIABILITY', 'BS-LL', 1, 1, '2017-02-09', '2017-02-09', '2', 0, @company_id, '2'),
	( 'TOTAL SHAREHOLDERS EQUITY', 'BS-SE', 1, 1, '2017-02-09', '2017-02-09', '2', 0, @company_id, '2'); */

-- SET FOREIGN_KEY_CHECKS=1;

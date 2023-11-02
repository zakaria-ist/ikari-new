delimiter $$
DROP PROCEDURE IF EXISTS test_00resetdb $$

CREATE PROCEDURE test_00resetdb(
  IN  I_global_var1  varchar(30),
  IN  I_global_var2 varchar(30),
  IN  I_global_var3 varchar(30),
  IN  I_global_var4 varchar(30),
  OUT O_result varchar(1000))

BEGIN

DECLARE L_src1, L_tgt1, L_tgt2, L_tgt3, L_tgt4            varchar(30)   DEFAULT NULL;
DECLARE L_success_cnt, L_error_cnt, L_row_cnt, L_row_cnt2 int           DEFAULT 0;
DECLARE L_error_msg                                       varchar(1000) DEFAULT NULL;

SET O_result = NULL;

-- test1
SELECT DATE_ADD(@company_closing_date, INTERVAL 1 MONTH) INTO L_src1;

SELECT fiscal_period,
       current_period_month,
       current_period_year,
       closing_date 
  INTO L_tgt1,
       L_tgt2,
       L_tgt3,
       L_tgt4
  FROM companies_company
 WHERE id=I_global_var1;

IF   NOT is_match(L_src1,L_tgt1)
  OR NOT is_match(I_global_var2,L_tgt2)
  OR NOT is_match(I_global_var3,L_tgt3)
  OR NOT is_match(I_global_var4,L_tgt4)
THEN
  SET L_error_cnt := L_error_cnt + 1;
  SET L_error_msg := set_err_msg(L_error_msg,'test1');
ELSE 
  SET L_success_cnt := L_success_cnt + 1;
END IF;

-- test2
SELECT COUNT(*)
  INTO L_row_cnt
  FROM transactions_transaction
 WHERE company_id=I_global_var1;

CALL check_test('test2',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test3
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounting_journal
 WHERE company_id=I_global_var1;

CALL check_test('test3',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test4
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounting_batch
 WHERE company_id=I_global_var1;

CALL check_test('test4',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);


-- test5
SELECT COUNT(*)
  INTO L_row_cnt
  FROM orders_orderitem
 WHERE order_id IN (SELECT id FROM orders_order WHERE company_id=I_global_var1);

CALL check_test('test5',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test6
SELECT COUNT(*)
  INTO L_row_cnt
  FROM orders_orderdelivery
 WHERE order_id IN (SELECT id FROM orders_order WHERE company_id=I_global_var1);

CALL check_test('test6',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test7
SELECT COUNT(*)
  INTO L_row_cnt
  FROM orders_orderheader
 WHERE order_id IN (SELECT id FROM orders_order WHERE company_id=I_global_var1);

CALL check_test('test7',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test8
SELECT COUNT(*)
  INTO L_row_cnt
  FROM inventory_incoming
 WHERE company_id=I_global_var1;

CALL check_test('test8',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test9
SELECT COUNT(*)
  INTO L_row_cnt
  FROM inventory_outgoing
 WHERE company_id=I_global_var1;

CALL check_test('test9',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test10


-- test11
SELECT COUNT(*)
  INTO L_row_cnt
  FROM inventory_history
 WHERE company_id=I_global_var1;

CALL check_test('test11',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test12
SELECT COUNT(*)
  INTO L_row_cnt
  FROM inventory_stocktransactiondetail
 WHERE parent_id IN (SELECT id FROM inventory_stocktransaction WHERE company_id=@company_id);

CALL check_test('test12',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test13
SELECT COUNT(*)
  INTO L_row_cnt
  FROM inventory_stocktransaction
 WHERE company_id=I_global_var1;

CALL check_test('test13',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test14
SELECT COUNT(*)
  INTO L_row_cnt
  FROM orders_order
 WHERE company_id=I_global_var1;

CALL check_test('test14',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test15
SELECT COUNT(*)
  INTO L_row_cnt
  FROM customers_delivery
 WHERE company_id=I_global_var1;

CALL check_test('test15',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test16
SELECT COUNT(*)
  INTO L_row_cnt
  FROM contacts_contact
 WHERE company_id=I_global_var1;

CALL check_test('test16',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test17
SELECT COUNT(*)
  INTO L_row_cnt
  FROM customers_customeritem
 WHERE item_id IN (SELECT id FROM items_item WHERE company_id=I_global_var1);

CALL check_test('test17',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test18
SELECT COUNT(*)
  INTO L_row_cnt
  FROM customers_customer
 WHERE company_id=I_global_var1;

CALL check_test('test18',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test19
SELECT COUNT(*)
  INTO L_row_cnt
  FROM suppliers_supplieritem
 WHERE item_id IN (SELECT id FROM items_item WHERE company_id=I_global_var1);

CALL check_test('test19',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test20
SELECT COUNT(*)
  INTO L_row_cnt
  FROM suppliers_supplier
 WHERE company_id=I_global_var1;

CALL check_test('test20',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test21
SELECT COUNT(*)
  INTO L_row_cnt
  FROM locations_locationitem
 WHERE item_id IN (SELECT id FROM items_item WHERE company_id=I_global_var1);

CALL check_test('test21',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test22
SELECT COUNT(*)
  INTO L_row_cnt
  FROM locations_location
 WHERE company_id=I_global_var1;

CALL check_test('test22',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test23
SELECT COUNT(*)
  INTO L_row_cnt
  FROM items_item
 WHERE company_id=I_global_var1;

CALL check_test('test23',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test24
SELECT COUNT(*)
  INTO L_row_cnt
  FROM items_itemcategory
 WHERE company_id=I_global_var1;

CALL check_test('test24',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test25
SELECT COUNT(*)
  INTO L_row_cnt
  FROM inventory_transactioncode
 WHERE company_id=I_global_var1;

CALL check_test('test25',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test26
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounts_accountcurrency
 WHERE account_id IN (SELECT id FROM accounts_account WHERE company_id=I_global_var1);

CALL check_test('test26',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test27
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounts_accounthistory
 WHERE company_id=I_global_var1;

CALL check_test('test27',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test28
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounts_accountset
 WHERE company_id=I_global_var1;

CALL check_test('test28',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test29
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounts_revaluationcode
 WHERE company_id=I_global_var1;

CALL check_test('test29',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test30
SELECT COUNT(*)
  INTO L_row_cnt
  FROM banks_bank
 WHERE company_id=I_global_var1;

CALL check_test('test30',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test31
SELECT COUNT(*)
  INTO L_row_cnt
  FROM taxes_tax
 WHERE company_id=I_global_var1;

CALL check_test('test31',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test32
SELECT COUNT(*)
  INTO L_row_cnt
  FROM taxes_taxgroup
 WHERE company_id=I_global_var1;

CALL check_test('test32',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test33
SELECT COUNT(*)
  INTO L_row_cnt
  FROM taxes_taxauthority
 WHERE company_id=I_global_var1;

CALL check_test('test33',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test34
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounts_distributioncode
 WHERE company_id=I_global_var1;

CALL check_test('test34',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test35
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounts_reportgroup
 WHERE company_id=I_global_var1;

CALL check_test('test35',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test36
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounts_account
 WHERE company_id=I_global_var1;

CALL check_test('test36',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test37
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounting_fiscalcalendar
 WHERE company_id=I_global_var1;

CALL check_test('test37',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test38
SELECT COUNT(*)
  INTO L_row_cnt
  FROM companies_costcenters
 WHERE company_id=I_global_var1;

CALL check_test('test38',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test39
SELECT COUNT(*)
  INTO L_row_cnt
  FROM currencies_exchangerate
 WHERE company_id=I_global_var1;

CALL check_test('test39',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test40
SELECT count(*)
  INTO L_row_cnt
FROM ikari_db_sage300.glacgrp;

SET L_row_cnt := L_row_cnt + 12; -- 12 = count of general accounttype (second part of insert into accounts_accounttype statement in 00_ResetDB.sql)

SELECT count(*)
  INTO L_row_cnt2
  FROM accounts_accounttype
 WHERE company_id=I_global_var1;

IF NOT is_match(L_row_cnt,L_row_cnt2) THEN
  SET L_error_cnt := L_error_cnt + 1;
  SET L_error_msg := set_err_msg(L_error_msg,'test40');

ELSE 
  SET L_success_cnt := L_success_cnt + 1;
END IF;

-- test41
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounting_revaluationdetails
 WHERE posting_id IN (SELECT id FROM accounting_revaluationlogs WHERE company_id=I_global_var1);

CALL check_test('test41',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);

-- test42
SELECT COUNT(*)
  INTO L_row_cnt
  FROM accounting_revaluationlogs
 WHERE company_id=I_global_var1;

CALL check_test('test42',is_empty(L_row_cnt),L_error_cnt,L_success_cnt,L_error_msg);


IF L_error_msg IS NULL THEN
  SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt);
ELSE
  SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt,' (',L_error_msg,')');
END IF;

CALL add_log('00_ResetDB', O_result, I_global_var1);

END $$
delimiter ;
# End test_00resetdb



# call test_script
SET @company_id = 5;
SET @company_curr_month = (SELECT ICON_CMTH FROM ikari_db_foxprosp.icon_fil);
SET @company_curr_year = (SELECT ICON_CYEAR FROM ikari_db_foxprosp.icon_fil);
SET @company_closing_date = (SELECT ICON_LDCDT FROM ikari_db_foxprosp.icon_fil);

call test_00resetdb(@company_id,@company_curr_month,@company_curr_year,@company_closing_date,@o_output);

select @o_output;
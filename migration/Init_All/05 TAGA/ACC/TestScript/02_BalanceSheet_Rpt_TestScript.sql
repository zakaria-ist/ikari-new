delimiter $$
DROP PROCEDURE IF EXISTS test_02_BalanceSheet_Rpt $$

CREATE PROCEDURE test_02_BalanceSheet_Rpt(
  IN  I_company_id   varchar(30),
  OUT O_result       varchar(1000))

BEGIN

  DECLARE L_success_cnt, L_error_cnt int          DEFAULT 0;
  DECLARE L_value1, L_value2         varchar(30)  DEFAULT NULL;
  DECLARE L_error_msg                varchar(200) DEFAULT NULL;


  SET O_result = NULL;

  -- test1
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('511', '512', '513');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='PL-NETSALE' and category='3' AND company_id=I_company_id;

  CALL check_test('test1',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test2
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('531', '541', '542', '561');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
   WHERE code='PL-COGS' and category='3' AND company_id=I_company_id;

  CALL check_test('test2',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test3
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('810', '811', '812', '819');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='PL-REVENUE' and category='3' AND company_id=I_company_id;

  CALL check_test('test3',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test4
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('533', '679', '709', '710', '711', '712', '713', 
  '721', '724', '725', '726', '727', '728', '729','731','732', '733', '735', '736', '738', '739',
  '741', '742', '743', '746', '747', '750', '751','752', '753', '754', '755', '762', '763', '779',
  '780', '790', '791', '822');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='PL-EXPENSE' and category='3' AND company_id=I_company_id;

  CALL check_test('test4',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test5
  SELECT t5.val1
    INTO L_value1
    FROM (SELECT DISTINCT profit_loss_group_id val1
            FROM accounts_account
           WHERE company_id=I_company_id
             AND name like upper('%exch%gain%')
          UNION
          SELECT DISTINCT profit_loss_group_id
            FROM accounts_account
           WHERE company_id=I_company_id
             AND code IN ('817', '820')) t5;

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='PL-EXC' and category='3' AND company_id=I_company_id;

  CALL check_test('test5',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test6
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('215','216','218','110');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='BS-NA' and category='2' AND company_id=I_company_id;

  CALL check_test('test6',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test7
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('115','120','121','122','148','152','153','154','178','181','185',
  '243','245','248');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='BS-CA' and category='2' AND company_id=I_company_id;

  CALL check_test('test7',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test8
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('312','313','314','322','323','328','335','339');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='BS-CL' and category='2' AND company_id=I_company_id;

  CALL check_test('test8',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test9
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('411','437');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='BS-SE' and category='2' AND company_id=I_company_id;

  CALL check_test('test9',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);


  IF L_error_msg IS NULL THEN
    SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt);
  ELSE
    SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt,' (',L_error_msg,')');
  END IF;

  CALL add_log('02_BalanceSheet_Report.sql', O_result, I_company_id);



END $$
delimiter ;
# End test_02_BalanceSheet_Rpt

# call test_script
SET @company_id = 5;

call test_02_BalanceSheet_Rpt(@company_id,@o_output);

select @o_output;
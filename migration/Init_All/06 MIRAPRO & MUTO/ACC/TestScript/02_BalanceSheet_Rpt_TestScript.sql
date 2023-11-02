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
     AND code IN ('4001', '4002', '4003', '4004', '4010');

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
     AND code IN ('4500', '4510', '4511' '4512', '4513', '4514', '5011', '4550');

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
     AND code IN ('4024', '4025', '4026', '4027', '4028');

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
     AND code IN ('5005', '5009', '5010', '5015', '5030', '5031', '5035', '5036', '5037', '5038', '5040', '5050',
    '5051', '5060', '5065', '5100', '5120', '5145', '5146', '5150', '5200', '5201', '5202', '5401', '5402', '5403',
    '5404', '5405', '5500', '5501', '5502', '5503', '5504', '5506', '5600', '5601', '5602', '5603', '5605');

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
             AND code IN ('5041', '6000')) t5;

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
     AND code IN ('1000', '1001', '1010', '1011');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='BS-FA' and category='2' AND company_id=I_company_id;

  CALL check_test('test6',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test7
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code IN ('1100', '1150', '1151', '1200', '1201', '1202', '1203', '1204', '1205', '1250', '1400', '1430',
    '1450', '1480', '1550', '1600', '1601', '1602', '1603', '1604', '1605', '1606', '1700', '2381');

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
     AND code IN ('2000', '2001', '2002', '2003', '2004', '2005', '2100', '2101', '2351', '2380', '2400');

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
     AND code IN ('3000', '3010', '3500');

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='BS-SE' and category='2' AND company_id=I_company_id;

  CALL check_test('test9',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test10
  SELECT DISTINCT profit_loss_group_id
    INTO L_value1
    FROM accounts_account
   WHERE company_id=I_company_id
     AND code = '3100';

  SELECT id 
    INTO L_value2
    FROM accounts_accounttype
  where code='BS-LL' and category='2' AND company_id=I_company_id;

  CALL check_test('test10',is_match(L_value1,L_value2),L_error_cnt,L_success_cnt,L_error_msg);


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
SET @company_id = 1;

call test_02_BalanceSheet_Rpt(@company_id,@o_output);

select @o_output;
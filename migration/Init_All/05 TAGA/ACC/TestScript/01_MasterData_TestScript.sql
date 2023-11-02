delimiter $$
DROP PROCEDURE IF EXISTS test_01MasterData $$

CREATE PROCEDURE test_01MasterData(
  IN  I_global_var1  varchar(30),
  OUT O_result       varchar(1000))

BEGIN

  DECLARE L_code,L_account_segment                      varchar(10)   DEFAULT NULL;
  DECLARE L_success_cnt, L_error_cnt, L_row_cnt,
          L_row_cnt2, L_cur_count,is_error,exit_loop    int           DEFAULT 0;
  DECLARE L_error_msg                                   varchar(1000) DEFAULT NULL;
  DECLARE L_loop_index                                  int     DEFAULT 1;
                    
  DECLARE L_cur_acc CURSOR FOR
    SELECT LEFT(code,4), account_segment
      FROM accounts_account
     WHERE company_id=11;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

  SET O_result = NULL;

  -- test1
  SELECT count(*)
    INTO L_row_cnt
  FROM ikari_db_sage300.glasv;

  SELECT count(*)
    INTO L_row_cnt2
    FROM companies_costcenters
   WHERE company_id=I_global_var1;

  IF NOT is_match(L_row_cnt,L_row_cnt2) THEN
    SET L_error_cnt := L_error_cnt + 1;
    SET L_error_msg := set_err_msg(L_error_msg,'test1');

  ELSE 
    SET L_success_cnt := L_success_cnt + 1;
  END IF;

  -- test2
  SELECT count(*)
    INTO L_row_cnt
  FROM ikari_db_sage300.glamf;

  SELECT count(*)
    INTO L_row_cnt2
    FROM accounts_account
   WHERE company_id=I_global_var1;

  CALL check_test('test2',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test3
  OPEN L_cur_acc;
  select FOUND_ROWS() into L_cur_count;

  account_loop: LOOP
    IF L_loop_index > L_cur_count THEN
      CLOSE L_cur_acc;
      LEAVE account_loop;
    END IF;

    FETCH L_cur_acc INTO L_code,L_account_segment;

    IF L_code <> L_account_segment THEN
      SET is_error := 1;
      CLOSE L_cur_acc;
      LEAVE account_loop;

    END IF;

    SET L_loop_index := L_loop_index + 1;

  END LOOP account_loop;

  CALL check_test('test3',not is_error,L_error_cnt,L_success_cnt,L_error_msg);

  -- test4
  SELECT count(*)
    INTO L_row_cnt
  FROM ikari_db_sage300.cscrd;

  SELECT count(*)
    INTO L_row_cnt2
    FROM currencies_exchangerate
   WHERE company_id=I_global_var1;

  CALL check_test('test4',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test5
  SELECT count(src.acctset)
    INTO L_row_cnt
    FROM (
      SELECT ACCTSET
        FROM `ikari_db_sage300`.`apras`
      LEFT JOIN `accounts_account` AS `ctrl_acc` ON `ctrl_acc`.`code` = REPLACE(`IDACCTAP`, '-', '') AND `ctrl_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `rlzdgain_acc` ON `rlzdgain_acc`.`code` = REPLACE(`RLZGNACT`, '-', '') AND `rlzdgain_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `rlzdloss_acc` ON `rlzdloss_acc`.`code` = REPLACE(`RLZLSACT`, '-', '') AND `rlzdloss_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `rounding_acc` ON `rounding_acc`.`code` = REPLACE(`RNDACCT`, '-', '') AND `rounding_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `unrlgain_acc` ON `unrlgain_acc`.`code` = REPLACE(`URLZGNACT`, '-', '') AND `unrlgain_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `unrlloss_acc` ON `unrlloss_acc`.`code` = REPLACE(`URLZLSACT`, '-', '') AND `unrlloss_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `prepayment_acc` ON `prepayment_acc`.`code` = REPLACE(`PPAYACCT`, '-', '') AND `prepayment_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `discount_acc` ON `discount_acc`.`code` = REPLACE(`DISCACCT`, '-', '') AND `discount_acc`.`company_id` = @company_id
      UNION
      SELECT IDACCTSET
        FROM `ikari_db_sage300`.`arras`
      LEFT JOIN `accounts_account` AS `ctrl_acc` ON `ctrl_acc`.`code` = REPLACE(`ARIDACCT`, '-', '') AND `ctrl_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `rlzdgain_acc` ON `rlzdgain_acc`.`code` = REPLACE(`RLZDGAIN`, '-', '') AND `rlzdgain_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `rlzdloss_acc` ON `rlzdloss_acc`.`code` = REPLACE(`RLZDLOSS`, '-', '') AND `rlzdloss_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `rounding_acc` ON `rounding_acc`.`code` = REPLACE(`RNDACCT`, '-', '') AND `rounding_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `unrlgain_acc` ON `unrlgain_acc`.`code` = REPLACE(`UNRLGAIN`, '-', '') AND `unrlgain_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `unrlloss_acc` ON `unrlloss_acc`.`code` = REPLACE(`UNRLLOSS`, '-', '') AND `unrlloss_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `prepayment_acc` ON `prepayment_acc`.`code` = REPLACE(`CASHLIAB`, '-', '') AND `prepayment_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `discount_acc` ON `discount_acc`.`code` = REPLACE(`ACCTDISC`, '-', '') AND `discount_acc`.`company_id` = @company_id
      LEFT JOIN `accounts_account` AS `writeoff_acc` ON `writeoff_acc`.`code` = REPLACE(`ACCTWROF`, '-', '') AND `writeoff_acc`.`company_id` = @company_id) src;

  SELECT count(*)
    INTO L_row_cnt2
    FROM accounts_accountset
   WHERE company_id = I_global_var1;

  CALL check_test('test5',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test6
  SELECT count(*)
    INTO L_row_cnt
  FROM ikari_db_sage300.bkacct;

  SELECT count(*)
    INTO L_row_cnt2
    FROM banks_bank
   WHERE company_id=I_global_var1;

  CALL check_test('test6',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test7
  SELECT count(RVALID)
    INTO L_row_cnt
  FROM ikari_db_sage300.glrval
  LEFT JOIN `accounts_account` AS `acc_gain` ON `acc_gain`.`code` = `ikari_db_sage300`.`glrval`.`ACCTGAIN` AND `acc_gain`.`company_id` = I_global_var1
  LEFT JOIN `accounts_account` AS `acc_loss` ON `acc_loss`.`code` = `ikari_db_sage300`.`glrval`.`ACCTLOSS` AND `acc_loss`.`company_id` = I_global_var1;

  SELECT count(*)
    INTO L_row_cnt2
    FROM accounts_revaluationcode
   WHERE company_id=I_global_var1;

  CALL check_test('test7',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test8
  SELECT count(src.IDDIST)
    INTO L_row_cnt
  FROM (
    SELECT IDDIST
      FROM ikari_db_sage300.arrdc
    UNION
    SELECT DISTID
      FROM ikari_db_sage300.aprdc) src;

  SELECT count(*)
    INTO L_row_cnt2
    FROM accounts_distributioncode
   WHERE company_id=I_global_var1;

  CALL check_test('test8',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test9
  SELECT count(*)
    INTO L_row_cnt
  FROM ikari_db_sage300.glavc;

  SELECT count(*)
    INTO L_row_cnt2
    FROM accounts_accountcurrency t1,
         accounts_account t2
   WHERE t1.account_id = t2.id
     AND t2.company_id = I_global_var1;

  CALL check_test('test9',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test10
  SELECT count(*)
    INTO L_row_cnt
  FROM ikari_db_sage300.txauth;

  SELECT count(*)
    INTO L_row_cnt2
    FROM taxes_taxauthority
   WHERE company_id = I_global_var1;

  CALL check_test('test10',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test11
  SELECT count(*)
    INTO L_row_cnt
  FROM ikari_db_sage300.txgrp;

  SELECT count(*)
    INTO L_row_cnt2
    FROM taxes_taxgroup
   WHERE company_id = I_global_var1;

  CALL check_test('test11',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test12
  SELECT count(*)
    INTO L_row_cnt
    FROM `ikari_db_sage300`.`txclass` AS `tc`
    LEFT JOIN `ikari_db_sage300`.`txauth` AS `ta` ON `ta`.`AUTHORITY` = `tc`.`AUTHORITY`
    LEFT JOIN `ikari_db_sage300`.`txrate` AS `tr` ON `tr`.`AUTHORITY` = `tc`.`AUTHORITY` AND `tr`.`TTYPE` = `tc`.`CLASSTYPE` AND `tr`.`BUYERCLASS` = `tc`.`CLASS`
    LEFT JOIN `ikari_db_sage300`.`glamf` AS `ga_out` ON `ga_out`.`ACCTID` = REPLACE(`ta`.`LIABILITY`, '-', '')
    LEFT JOIN `ikari_db_sage300`.`glamf` AS `ga_in` ON `ga_in`.`ACCTID` = REPLACE(`ta`.`ACCTRECOV`, '-', '')
    LEFT JOIN `ikari_db_sage300`.`txgrp` AS `tg` ON `tg`.`AUTHORITY1` = `ta`.`AUTHORITY` AND `tg`.`TTYPE` = `tc`.`CLASSTYPE`
    WHERE `tc`.`CLASSAXIS` = 1 -- TAX_TYPE['Customer/Vendor'] --
    ORDER BY `ta`.`AUTHORITY`, `tc`.`CLASSTYPE`, `tc`.`CLASS`;

  SELECT count(*)
    INTO L_row_cnt2
    FROM taxes_tax
   WHERE company_id = I_global_var1;

  CALL check_test('test12',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test13
  SELECT count(*)
    INTO L_row_cnt
    FROM ikari_db_sage300.apven;

  SELECT count(*)
    INTO L_row_cnt2
    FROM suppliers_supplier
   WHERE company_id = I_global_var1;

  CALL check_test('test13',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test14
  SELECT count(*)
    INTO L_row_cnt
    FROM ikari_db_sage300.arcus;

  SELECT count(*)
    INTO L_row_cnt2
    FROM customers_customer
   WHERE company_id = I_global_var1;

  CALL check_test('test14',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test15
  SELECT fiscalcalendar_rec_cnt(2011),
         (SELECT count(*)
            FROM accounting_fiscalcalendar
           WHERE company_id = I_global_var1)
    INTO L_row_cnt,L_row_cnt2;

  CALL check_test('test15',is_match(L_row_cnt,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test16
  CALL generate_accthist_src(11,@source_tbl);

  IF @source_tbl THEN
    CALL check_test('test16',test_accthist(),L_error_cnt,L_success_cnt,L_error_msg);
  ELSE
    SET L_error_cnt := L_error_cnt + 1;
    SET L_error_msg := set_err_msg(L_error_msg,'test16');
  END IF;

  IF L_error_msg IS NULL THEN
    SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt);
  ELSE
    SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt,' (',L_error_msg,')');
  END IF;

  CALL add_log('01_Master_data', O_result, I_global_var1);

END $$
delimiter ;
# End test_01MasterData


# call test_script
SET @company_id = 5;

call test_01MasterData(@company_id,@o_output);

select @o_output;
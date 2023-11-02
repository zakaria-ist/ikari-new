delimiter $$
DROP PROCEDURE IF EXISTS test_03Transaction $$

CREATE PROCEDURE test_03Transaction(
  IN  I_company_id  varchar(30),
  OUT O_result       varchar(1000))

BEGIN

  DECLARE L_success_cnt,
          L_error_cnt,
          L_row_cnt1,
          L_row_cnt2     int          DEFAULT 0;
  DECLARE L_error_msg    varchar(200) DEFAULT NULL;


  SET O_result = NULL;

  -- test1
  SELECT src_batch(), 
         (SELECT count(*) FROM accounting_batch 
           WHERE company_id=I_company_id)
    INTO L_row_cnt1,
         L_row_cnt2;

  CALL check_test('test1',is_match(L_row_cnt1,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test2
  SELECT src_journal(I_company_id), 
         (SELECT count(*) FROM accounting_journal 
           WHERE company_id=I_company_id)
    INTO L_row_cnt1,
         L_row_cnt2;

  CALL check_test('test2',is_match(L_row_cnt1,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test3
  SELECT src_transaction(I_company_id), 
         (SELECT count(*) FROM transactions_transaction 
           WHERE company_id=I_company_id)
    INTO L_row_cnt1,
         L_row_cnt2;

  CALL check_test('test3',is_match(L_row_cnt1,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test4
  SELECT count(*)
    INTO L_row_cnt1
    FROM (
      SELECT 1 AS `journal_type`,
             DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `revaluation_date`,
             CONVRATE AS `exchange_rate`,
             DATE_FORMAT(`CONVDATE`,'%Y-%m-%d') AS `rate_date`,
             CURTBLTYPE AS `rate_type`,
             POSTSEQNCE AS `posting_sequence`,
             DATE_FORMAT(`DATEPOSTED`,'%Y-%m-%d') AS `posting_date`,
             SWRVMETHOD AS `revaluation_method`
        FROM ikari_db_sage300.arrvllog
      UNION
      SELECT 2 AS `journal_type`,
             DATE_FORMAT(`RVLDATE`,'%Y-%m-%d') AS `revaluation_date`,
             CONVRATE AS `exchange_rate`,
             DATE_FORMAT(`CONVDATE`,'%Y-%m-%d') AS `rate_date`,
             CURTBLTYPE AS `rate_type`,
             POSTSEQNCE AS `posting_sequence`,
             DATE_FORMAT(`DATEPOSTED`,'%Y-%m-%d') AS `posting_date`,
             SWRVMETHOD AS `revaluation_method`
        FROM ikari_db_sage300.aprvllog) t4;

  SELECT count(*)
    INTO L_row_cnt2
    FROM accounting_revaluationlogs
   WHERE company_id=I_company_id;

  CALL check_test('test4',is_match(L_row_cnt1,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  -- test5
  SELECT count(*)
    INTO L_row_cnt1
    FROM (
      SELECT (SELECT `id` FROM accounting_revaluationlogs
               WHERE `jh`.`POSTSEQNCE`=`posting_sequence`
                 AND `journal_type`=1
                 AND `jh`.`RATETYPETC`=`rate_type`
                 AND `currency_id`=(SELECT `id` FROM `currencies_currency` WHERE `code`=`jh`.`CODECURNTC`)
                 AND company_id=I_company_id) AS `posting_id`
        FROM ikari_db_sage300.arpjh AS `jh`
       WHERE `jh`.`TYPEBTCH`='RV'
      HAVING `posting_id` IS NOT NULL
      UNION ALL
      SELECT (SELECT `id` FROM `accounting_revaluationlogs`
               WHERE `jh`.`POSTSEQNCE`=`posting_sequence`
               AND `journal_type`=2
               AND `jh`.`RATETYPETC`=`rate_type`
               AND `currency_id`=(SELECT `id` FROM `currencies_currency` WHERE `code`=`jh`.`CODECURNTC`)
               AND company_id=I_company_id) AS `posting_id`
        FROM ikari_db_sage300.appjh AS `jh`
       WHERE `jh`.`TYPEBTCH`='RV'
      HAVING `posting_id` IS NOT NULL) t5;

  SELECT count(*)
    INTO L_row_cnt2
    FROM accounting_revaluationdetails rd,
         accounting_revaluationlogs rl
   WHERE rd.posting_id = rl.id
     AND rl.company_id = I_company_id;

  CALL check_test('test5',is_match(L_row_cnt1,L_row_cnt2),L_error_cnt,L_success_cnt,L_error_msg);

  IF L_error_msg IS NULL THEN
    SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt);
  ELSE
    SET O_result := CONCAT('TEST RESULT = Success : ', L_success_cnt,', Fail : ',L_error_cnt,' (',L_error_msg,')');
  END IF;

  CALL add_log('03_Transaction', O_result, I_company_id);


END $$
delimiter ;
# End test_03Transaction

# call test_script
SET @company_id = 5;

call test_03Transaction(@company_id,@o_output);

select @o_output;
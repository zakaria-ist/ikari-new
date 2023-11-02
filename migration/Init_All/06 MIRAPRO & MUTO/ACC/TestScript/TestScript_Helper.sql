delimiter $$
DROP PROCEDURE IF EXISTS add_log $$

CREATE PROCEDURE add_log(
  I_test_name VARCHAR(100),
  I_log       VARCHAR(1000),
  I_company_id int)

BEGIN

  DECLARE L_result int DEFAULT FALSE;

  INSERT INTO test_log (test_name, log_text, company_id)
   VALUES (I_test_name, I_log, I_company_id);

END $$
delimiter ;
# End add_log


delimiter $$
DROP FUNCTION IF EXISTS is_match $$

CREATE FUNCTION is_match(
  I_var1 varchar(30),
  I_var2 varchar(30))
RETURNS boolean

BEGIN

  DECLARE L_result int DEFAULT FALSE;

  IF I_var1=I_var2 THEN
    SET L_result := TRUE;
  END IF;

  RETURN L_result;

END $$
delimiter ;
# End is_match


delimiter $$
DROP FUNCTION IF EXISTS set_err_msg $$

CREATE FUNCTION set_err_msg(
  I_err_msg   varchar(1000),
  I_test_name varchar(10))
RETURNS varchar(1000)
BEGIN

  DECLARE L_err_msg varchar(1000) DEFAULT NULL;

  IF I_err_msg IS NULL THEN
      SET L_err_msg := I_test_name;
    ELSE
      SET L_err_msg := CONCAT(I_err_msg,', ',I_test_name);
    END IF;

  RETURN L_err_msg;

END $$
delimiter ;
# End set_err_msg


delimiter $$
DROP FUNCTION IF EXISTS is_empty $$

CREATE FUNCTION is_empty(I_row_cnt int)
RETURNS int
BEGIN

  IF I_row_cnt>0 THEN
    RETURN 0;
  ELSE
    RETURN 1;
  END IF;

END $$
delimiter ;
# End is_empty

delimiter $$
DROP PROCEDURE IF EXISTS check_test $$

CREATE PROCEDURE check_test(
  IN    I_test_name    varchar(100),
  IN    I_test_pass  int,
  INOUT IO_error_cnt   int,
  INOUT IO_success_cnt int,
  INOUT IO_error_msg   varchar(1000))

BEGIN

  IF I_test_pass THEN
    SET IO_success_cnt := IO_success_cnt + 1;

  ELSE 
    SET IO_error_cnt := IO_error_cnt + 1;
    SET IO_error_msg := set_err_msg(IO_error_msg,I_test_name);

  END IF;

END $$
delimiter ;
# End check_test


delimiter $$
DROP FUNCTION IF EXISTS fiscalcalendar_rec_cnt $$

CREATE FUNCTION fiscalcalendar_rec_cnt(I_from_year int)
RETURNS int

BEGIN

  DECLARE L_year_to_v varchar(4);
  DECLARE L_year_to_i int;

  SET L_year_to_v = YEAR(now());
  SET L_year_to_i = CAST(L_year_to_v AS UNSIGNED)+2;

  RETURN (L_year_to_i-I_from_year+1)*12;

END $$
delimiter ;
# End fiscalcalendar_rec_cnt

delimiter $$
DROP PROCEDURE IF EXISTS generate_accthist_src $$
CREATE PROCEDURE generate_accthist_src(IN I_company_id int,OUT O_result int)
BEGIN

  DECLARE year, currid, currcode, acctid, acctcode TEXT;
  DECLARE s_openbal,netprd1,netprd2,netprd3,netprd4,netprd5,netprd6,netprd7,netprd8,netprd9,
          netprd10,netprd11,netprd12,netprd13,netprd14,netprd15,f_openbal,fnetprd1,fnetprd2,
          fnetprd3,fnetprd4,fnetprd5,fnetprd6,fnetprd7,fnetprd8,fnetprd9,fnetprd10,fnetprd11,
          fnetprd12,fnetprd13,fnetprd14,fnetprd15 DECIMAL(20,6) DEFAULT 0;
  DECLARE L_s_end_bal,L_f_end_bal DECIMAL(20,6) DEFAULT 0;

  DECLARE exit_loop                                 INT DEFAULT FALSE;
  DECLARE company_currency, cursor_count, row_count INT DEFAULT 0;
  DECLARE index_count                               INT DEFAULT 1;
  DECLARE acct_hist CURSOR FOR
    SELECT acct_hist.*
    ,(CASE
        WHEN acct_hist.currency='DOS'
          THEN (SELECT id FROM currencies_currency WHERE code='SGD')
          ELSE (SELECT id FROM currencies_currency WHERE code=acct_hist.currency)
      END) currency_id
  FROM (
  SELECT s.*
    ,CAST(COALESCE(e.openbal,f.openbal,0) AS DECIMAL(20,6)) fopenbal
    ,CAST(COALESCE(e.netperd1,f.netperd1,0) AS DECIMAL(20,6)) fnetperd1
    ,CAST(COALESCE(e.netperd2,f.netperd2,0) AS DECIMAL(20,6)) fnetperd2
    ,CAST(COALESCE(e.netperd3,f.netperd3,0) AS DECIMAL(20,6)) fnetperd3
    ,CAST(COALESCE(e.netperd4,f.netperd4,0) AS DECIMAL(20,6)) fnetperd4
    ,CAST(COALESCE(e.netperd5,f.netperd5,0) AS DECIMAL(20,6)) fnetperd5
    ,CAST(COALESCE(e.netperd6,f.netperd6,0) AS DECIMAL(20,6)) fnetperd6
    ,CAST(COALESCE(e.netperd7,f.netperd7,0) AS DECIMAL(20,6)) fnetperd7
    ,CAST(COALESCE(e.netperd8,f.netperd8,0) AS DECIMAL(20,6)) fnetperd8
    ,CAST(COALESCE(e.netperd9,f.netperd9,0) AS DECIMAL(20,6)) fnetperd9
    ,CAST(COALESCE(e.netperd10,f.netperd10,0) AS DECIMAL(20,6)) fnetperd10
    ,CAST(COALESCE(e.netperd11,f.netperd11,0) AS DECIMAL(20,6)) fnetperd11
    ,CAST(COALESCE(e.netperd12,f.netperd12,0) AS DECIMAL(20,6)) fnetperd12
    ,CAST(COALESCE(e.netperd13,f.netperd13,0) AS DECIMAL(20,6)) fnetperd13
    ,CAST(COALESCE(e.netperd14,f.netperd14,0) AS DECIMAL(20,6)) fnetperd14
    ,CAST(COALESCE(e.netperd15,f.netperd15,0) AS DECIMAL(20,6)) fnetperd15
  FROM
  (SELECT afs.fscsyr period_year
    ,afs.fscscurn currency
    ,aa.id account_id
    ,afs.acctid account_code
    ,IFNULL(openbal,0) openbal
    ,IFNULL(netperd1,0) netperd1
    ,IFNULL(netperd2,0) netperd2
    ,IFNULL(netperd3,0) netperd3
    ,IFNULL(netperd4,0) netperd4
    ,IFNULL(netperd5,0) netperd5
    ,IFNULL(netperd6,0) netperd6
    ,IFNULL(netperd7,0) netperd7
    ,IFNULL(netperd8,0) netperd8
    ,IFNULL(netperd9,0) netperd9
    ,IFNULL(netperd10,0) netperd10
    ,IFNULL(netperd11,0) netperd11
    ,IFNULL(netperd12,0) netperd12
    ,IFNULL(netperd13,0) netperd13
    ,IFNULL(netperd14,0) netperd14
    ,IFNULL(netperd15,0) netperd15
  FROM ikari_db_sage300.glafs afs
  LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
  LEFT OUTER JOIN accounts_account aa ON afs.acctid=aa.code AND aa.company_id=I_company_id
  WHERE afs.fscsdsg='A'
  /* AND afs.activitysw>0 */
  AND amf.mcsw=1
  AND afs.curntype='S') s
  LEFT OUTER JOIN (
    SELECT afs.fscsyr,afs.acctid,afs.fscscurn
      ,IFNULL(openbal,0) openbal
      ,IFNULL(netperd1,0) netperd1
      ,IFNULL(netperd2,0) netperd2
      ,IFNULL(netperd3,0) netperd3
      ,IFNULL(netperd4,0) netperd4
      ,IFNULL(netperd5,0) netperd5
      ,IFNULL(netperd6,0) netperd6
      ,IFNULL(netperd7,0) netperd7
      ,IFNULL(netperd8,0) netperd8
      ,IFNULL(netperd9,0) netperd9
      ,IFNULL(netperd10,0) netperd10
      ,IFNULL(netperd11,0) netperd11
      ,IFNULL(netperd12,0) netperd12
      ,IFNULL(netperd13,0) netperd13
      ,IFNULL(netperd14,0) netperd14
      ,IFNULL(netperd15,0) netperd15
      FROM ikari_db_sage300.glafs afs
      LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
      where afs.fscsdsg='A'
      AND afs.activitysw>0
      and amf.mcsw=1
      and afs.curntype='E'
    ) e ON s.period_year=e.fscsyr AND s.account_code=e.acctid AND s.currency=e.fscscurn
  LEFT OUTER JOIN (
    SELECT afs.fscsyr,afs.acctid,afs.fscscurn
      ,IFNULL(openbal,0) openbal
      ,IFNULL(netperd1,0) netperd1
      ,IFNULL(netperd2,0) netperd2
      ,IFNULL(netperd3,0) netperd3
      ,IFNULL(netperd4,0) netperd4
      ,IFNULL(netperd5,0) netperd5
      ,IFNULL(netperd6,0) netperd6
      ,IFNULL(netperd7,0) netperd7
      ,IFNULL(netperd8,0) netperd8
      ,IFNULL(netperd9,0) netperd9
      ,IFNULL(netperd10,0) netperd10
      ,IFNULL(netperd11,0) netperd11
      ,IFNULL(netperd12,0) netperd12
      ,IFNULL(netperd13,0) netperd13
      ,IFNULL(netperd14,0) netperd14
      ,IFNULL(netperd15,0) netperd15
      FROM ikari_db_sage300.glafs afs
      LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
      where afs.fscsdsg='A'
      AND afs.activitysw>0
      and amf.mcsw=1
      and afs.curntype='F'
    ) f ON s.period_year=f.fscsyr AND s.account_code=f.acctid AND s.currency=f.fscscurn
  UNION ALL
  SELECT dos.period_year,dos.currency,dos.account_id,dos.account_code
        ,0 openbal,0 netperd1,0 netperd2,0 netperd3,0 netperd4,0 netperd5,0 netperd6,0 netperd7
        ,0 netperd8,0 netperd9,0 netperd10,0 netperd11,0 netperd12,0 netperd13,0 netperd14,0 netperd15
        ,dos.openbal fopenbal,dos.netperd1 fnetperd1,dos.netperd2 fnetperd2,dos.netperd3 fnetperd3
        ,dos.netperd4 fnetperd4,dos.netperd5 ffnetperd5,dos.netperd6 fnetperd6,dos.netperd7 fnetperd7
        ,dos.netperd8 fnetperd8,dos.netperd9 fnetperd9,dos.netperd10 fnetperd10,dos.netperd11 fnetperd11
        ,dos.netperd12 fnetperd12,dos.netperd13 fnetperd13,dos.netperd14 fnetperd14,dos.netperd15 fnetperd15
  FROM (SELECT afs.fscsyr period_year
        ,afs.fscscurn currency
        ,aa.id account_id
        ,afs.acctid account_code
        ,IFNULL(openbal,0) openbal
        ,IFNULL(netperd1,0) netperd1
        ,IFNULL(netperd2,0) netperd2
        ,IFNULL(netperd3,0) netperd3
        ,IFNULL(netperd4,0) netperd4
        ,IFNULL(netperd5,0) netperd5
        ,IFNULL(netperd6,0) netperd6
        ,IFNULL(netperd7,0) netperd7
        ,IFNULL(netperd8,0) netperd8
        ,IFNULL(netperd9,0) netperd9
        ,IFNULL(netperd10,0) netperd10
        ,IFNULL(netperd11,0) netperd11
        ,IFNULL(netperd12,0) netperd12
        ,IFNULL(netperd13,0) netperd13
        ,IFNULL(netperd14,0) netperd14
        ,IFNULL(netperd15,0) netperd15
      FROM ikari_db_sage300.glafs afs
      LEFT OUTER JOIN accounts_account aa ON afs.acctid=aa.code AND aa.company_id=I_company_id
      WHERE afs.fscsdsg='A'
      AND afs.activitysw>0
      AND afs.fscscurn='DOS'
      AND afs.curntype='F') dos
  WHERE NOT EXISTS
    ( SELECT s.* FROM
        (SELECT afs.fscsyr period_year
          ,afs.fscscurn currency
          ,aa.id account_id
        FROM ikari_db_sage300.glafs afs
        LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
        LEFT OUTER JOIN accounts_account aa ON afs.acctid=aa.code AND aa.company_id=I_company_id
        WHERE afs.fscsdsg='A'
        AND afs.activitysw>0
        AND amf.mcsw=1
        AND afs.curntype='S') s
        WHERE dos.period_year=s.period_year and dos.currency=s.currency and dos.account_id=s.account_id)
  UNION ALL
  -- SF add 28sep19
  SELECT mcsw_0.period_year,mcsw_0.currency,mcsw_0.account_id,mcsw_0.account_code
        ,0 openbal,0 netperd1,0 netperd2,0 netperd3,0 netperd4,0 netperd5,0 netperd6,0 netperd7
        ,0 netperd8,0 netperd9,0 netperd10,0 netperd11,0 netperd12,0 netperd13,0 netperd14,0 netperd15
        ,mcsw_0.openbal fopenbal,mcsw_0.netperd1 fnetperd1,mcsw_0.netperd2 fnetperd2,mcsw_0.netperd3 fnetperd3
        ,mcsw_0.netperd4 fnetperd4,mcsw_0.netperd5 ffnetperd5,mcsw_0.netperd6 fnetperd6,mcsw_0.netperd7 fnetperd7
        ,mcsw_0.netperd8 fnetperd8,mcsw_0.netperd9 fnetperd9,mcsw_0.netperd10 fnetperd10,mcsw_0.netperd11 fnetperd11
        ,mcsw_0.netperd12 fnetperd12,mcsw_0.netperd13 fnetperd13,mcsw_0.netperd14 fnetperd14,mcsw_0.netperd15 fnetperd15
  FROM (SELECT afs.fscsyr period_year
        ,afs.fscscurn currency
        ,aa.id account_id
        ,afs.acctid account_code
        ,IFNULL(openbal,0) openbal
        ,IFNULL(netperd1,0) netperd1
        ,IFNULL(netperd2,0) netperd2
        ,IFNULL(netperd3,0) netperd3
        ,IFNULL(netperd4,0) netperd4
        ,IFNULL(netperd5,0) netperd5
        ,IFNULL(netperd6,0) netperd6
        ,IFNULL(netperd7,0) netperd7
        ,IFNULL(netperd8,0) netperd8
        ,IFNULL(netperd9,0) netperd9
        ,IFNULL(netperd10,0) netperd10
        ,IFNULL(netperd11,0) netperd11
        ,IFNULL(netperd12,0) netperd12
        ,IFNULL(netperd13,0) netperd13
        ,IFNULL(netperd14,0) netperd14
        ,IFNULL(netperd15,0) netperd15
      FROM ikari_db_sage300.glafs afs
      LEFT OUTER JOIN ikari_db_sage300.glamf amf ON afs.acctid=amf.acctid
      LEFT OUTER JOIN accounts_account aa ON afs.acctid=aa.code AND aa.company_id=I_company_id
      WHERE afs.fscsdsg='A'
      AND afs.activitysw>0
      AND amf.mcsw=0
      AND afs.curntype='F'
      ) mcsw_0
  ) acct_hist
  WHERE currency <> 'SGD' -- SF add 27sep19
  ORDER BY acct_hist.account_code,acct_hist.period_year,acct_hist.currency;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = TRUE;

  SELECT currency_id FROM companies_company WHERE id=I_company_id INTO company_currency;

  -- for test purpose: this table will keep end_balance for each year from old db (sage300)
  -- create table
  DROP TABLE IF EXISTS test_accthist_src;

  CREATE TABLE test_accthist_src AS
  SELECT account_id,
         period_year,
         source_currency_id,
         source_end_balance,
         functional_currency_id,
         functional_end_balance
    FROM accounts_accounthistory
   WHERE id = -1;

  -- fill table
  OPEN acct_hist;

  SELECT FOUND_ROWS() INTO cursor_count;
  
  glafs_loop: LOOP
    FETCH acct_hist INTO year,currcode,acctid,acctcode,s_openbal,
          netprd1,netprd2,netprd3,netprd4,netprd5,netprd6,netprd7,
          netprd8,netprd9,netprd10,netprd11,netprd12,netprd13,netprd14,netprd15,
          f_openbal,fnetprd1,fnetprd2,fnetprd3,fnetprd4,fnetprd5,fnetprd6,fnetprd7,
          fnetprd8,fnetprd9,fnetprd10,fnetprd11,fnetprd12,fnetprd13,fnetprd14,fnetprd15,currid;
    IF index_count > cursor_count THEN
      CLOSE acct_hist;
      LEAVE glafs_loop;
    END IF;
    
    SET L_s_end_bal := s_openbal+netprd1+netprd2+netprd3+netprd4+netprd5+netprd6+netprd7+netprd8+
                       netprd9+netprd10+netprd11+netprd12+netprd13+netprd14+netprd15;
    
    SET L_f_end_bal := f_openbal+fnetprd1+fnetprd2+fnetprd3+fnetprd4+fnetprd5+fnetprd6+fnetprd7+fnetprd8+
                       fnetprd9+fnetprd10+fnetprd11+fnetprd12+fnetprd13+fnetprd14+fnetprd15;

    INSERT INTO test_accthist_src
      VALUES (acctid,year,currid,L_s_end_bal,company_currency,L_f_end_bal);

    SET index_count := index_count + 1;
  END LOOP glafs_loop;

  -- test table
  SELECT count(*)
    INTO row_count
    FROM test_accthist_src;

  IF row_count=index_count-1 THEN
    SET O_result := 1;
  ELSE
    SET O_result := 0;
  END IF;

END $$
delimiter ;
# End generate_accthist_src


delimiter $$
DROP FUNCTION IF EXISTS test_accthist $$
CREATE FUNCTION test_accthist(company int)
RETURNS TEXT
BEGIN

  DECLARE L_accid, L_year, L_scurrid, L_fcurrid                  TEXT;
  DECLARE L_s_end_bal1, L_s_end_bal2, L_f_end_bal1, L_f_end_bal2 DECIMAL(20,6) DEFAULT 0;
  DECLARE exit_loop,cursor_count                                 INT           DEFAULT 0;
  DECLARE index_count,test_pass                                  INT           DEFAULT 1;

  DECLARE acct_hist CURSOR FOR
    SELECT src_tbl.account_id,
           src_tbl.period_year,
           src_tbl.source_currency_id,
           src_tbl.functional_currency_id,
           src_tbl.source_end_balance source_end_balance1,
           tgt_tbl.source_end_balance source_end_balance2,
           src_tbl.functional_end_balance functional_end_balance1,
           tgt_tbl.functional_end_balance functional_end_balance2
      FROM (select distinct * from test_accthist_src) src_tbl,
           accounts_accounthistory tgt_tbl
     WHERE src_tbl.account_id = tgt_tbl.account_id
       AND src_tbl.period_year = tgt_tbl.period_year
       AND src_tbl.source_currency_id = tgt_tbl.source_currency_id
       AND tgt_tbl.period_month  = 'CLS'
       AND tgt_tbl.company_id = company;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_loop = 1;

  OPEN acct_hist;

  SELECT FOUND_ROWS() INTO cursor_count;
  
  test_acct_hist: LOOP

    FETCH acct_hist
     INTO L_accid, L_year, L_scurrid, L_fcurrid,
          L_s_end_bal1, L_s_end_bal2, L_f_end_bal1, L_f_end_bal2;

    IF index_count > cursor_count THEN
      CLOSE acct_hist;
      LEAVE test_acct_hist;
    END IF;
    
    IF    (L_s_end_bal1 <> L_s_end_bal2)
      AND (L_f_end_bal1 <> L_f_end_bal2)
    THEN
      SET test_pass := 0;

    END IF;

    SET index_count := index_count + 1;

  END LOOP test_acct_hist;

  RETURN test_pass;

END $$
delimiter ;
# End test_accthist


delimiter $$
DROP FUNCTION IF EXISTS src_batch $$

CREATE FUNCTION src_batch ()
RETURNS int
BEGIN

  DECLARE L_cnt,L_totalrow int DEFAULT 0;
  
  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT CNTBTCH
        FROM ikari_db_sage300.apibc -- AP Invoice Batches --
      UNION ALL
      SELECT CNTBTCH
        FROM ikari_db_sage300.apbta -- AP Payment and Adjustment Batches --
      WHERE PAYMTYPE='PY' -- Payment Type --
      UNION ALL
      SELECT CNTBTCH
        FROM ikari_db_sage300.aribc -- AR Invoice Batches --
      UNION ALL
      SELECT CNTBTCH
        FROM ikari_db_sage300.arbta -- AR Receipt and Adjustment Batches --
      where CODEPYMTYP='CA' -- Code Payment Type --
      UNION ALL
      SELECT BATCHID
        FROM ikari_db_sage300.glbctl -- AR Receipt and Adjustment Batches --
      LEFT JOIN (
        SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
          FROM ikari_db_sage300.gljed
          GROUP BY ikari_db_sage300.gljed.BATCHNBR
      ) AS gljed ON gljed.BATCHNBR = ikari_db_sage300.glbctl.BATCHID
      WHERE gljed.SRCETYPE = 'JE'
  ) t0;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM ikari_db_sage300.glbctl
    LEFT JOIN (
       SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
         FROM `ikari_db_sage300`.`gljed` GROUP BY `ikari_db_sage300`.`gljed`.`BATCHNBR`
    ) AS `gljed` ON `gljed`.`BATCHNBR` = `ikari_db_sage300`.`glbctl`.`BATCHID`
   WHERE BATCHTYPE IN (1, 3, 4)
     AND `gljed`.`SRCETYPE` !='JE';

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT DISTINCT
          `b`.`BATCHID` AS `batch_no`,
          `b`.`BTCHDESC` AS `description`,
          (CASE WHEN `b`.`BATCHSTAT` = '4' THEN 2 WHEN `b`.`BATCHSTAT` = '3' THEN 3 ELSE 1 END) AS `status`,
          IF(`b`.`BATCHTYPE` = 1, '2', '1') AS `input_type`, -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
          `b`.`POSTNGSEQ` AS `posting_sequence`,
          `b`.`DEBITTOT` AS `batch_amount`,
          `b`.`ENTRYCNT` AS `no_entries`,
          `b`.`SRCELEDGR` AS `source_ledger`
      FROM `ikari_db_sage300`.`glbctl` AS `b`
      LEFT JOIN (
          SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
          FROM `ikari_db_sage300`.`gljed` AS `j` GROUP BY `j`.`BATCHNBR`
      ) AS `gljed` ON `gljed`.`BATCHNBR` = `b`.`BATCHID`
      LEFT JOIN `ikari_db_sage300`.`gljeh` ON `gljeh`.`BATCHID` = `b`.`BATCHID`
      WHERE `b`.`BATCHTYPE` = 2
      AND `gljed`.`SRCETYPE` != 'JE'
      AND `gljeh`.`SRCELEDGER` IN ('AP', 'AR')
      AND `gljeh`.`SRCETYPE` = 'GL'
  ) t3;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT DISTINCT
          `b`.`BATCHID` AS `batch_no`,
          `b`.`BTCHDESC` AS `description`,
          (CASE WHEN `b`.`BATCHSTAT` = '4' THEN 2 WHEN `b`.`BATCHSTAT` = '3' THEN 3 ELSE 1 END) AS `status`,
          IF(`b`.`BATCHTYPE` = 1, '2', '1') AS `input_type`, -- INPUT_TYPE_DICT['Manual Entry'] INPUT_TYPE_DICT['Generated'] --
          `b`.`POSTNGSEQ` AS `posting_sequence`,
          `b`.`DEBITTOT` AS `batch_amount`,
          `b`.`ENTRYCNT` AS `no_entries`,
          `b`.`SRCELEDGR` AS `source_ledger`
      FROM `ikari_db_sage300`.`glbctl` AS `b`
      LEFT JOIN (
          SELECT `BATCHNBR`, COUNT(*) AS `CNTENTER`, `SCURNCODE`, `SRCELDGR`, `SRCETYPE`
          FROM `ikari_db_sage300`.`gljed` AS `j` GROUP BY `j`.`BATCHNBR`
      ) AS `gljed` ON `gljed`.`BATCHNBR` = `b`.`BATCHID`
      LEFT JOIN `ikari_db_sage300`.`gljeh` ON `gljeh`.`BATCHID` = `b`.`BATCHID`
      WHERE `b`.`BATCHTYPE` = 2
      AND `gljed`.`SRCETYPE` != 'JE'
      AND `gljeh`.`SRCELEDGER` IN ('AP', 'AR')
      AND `gljeh`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY')
  ) t4;

  SET L_totalrow := L_totalrow + L_cnt;

  RETURN L_totalrow;

END $$
delimiter ;
# End src_batch


delimiter $$
DROP FUNCTION IF EXISTS src_journal $$

CREATE FUNCTION src_journal (I_company_id int)
RETURNS int
BEGIN
  
  DECLARE L_cnt,L_totalrow int DEFAULT 0;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT j.CNTITEM
        FROM ikari_db_sage300.apibh j -- AP Invoices --
        JOIN ikari_db_sage300.apobl bl
        ON j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem AND j.TEXTTRX = bl.txttrxtype
      UNION ALL
      SELECT CNTENTR
        FROM ikari_db_sage300.aptcr
      UNION ALL
      SELECT j.CNTITEM
        FROM ikari_db_sage300.aribh j
        JOIN ikari_db_sage300.arobl bl
        ON j.cntbtch=bl.cntbtch AND j.cntitem=bl.cntitem AND j.TEXTTRX = bl.trxtypetxt
      UNION ALL
      SELECT CNTITEM
        FROM ikari_db_sage300.artcr
      UNION ALL
      SELECT j.BTCHENTRY
        FROM ikari_db_sage300.gljeh J
       WHERE SRCETYPE = 'JE'
  ) t0;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT COUNT(*)
    INTO L_cnt
    FROM ikari_db_sage300.gljeh gl_crown
  RIGHT OUTER JOIN ikari_db_sage300.glbctl gl_entry ON gl_crown.BATCHID = gl_entry.BATCHID
   WHERE gl_entry.BATCHTYPE IN (1, 3, 4)
     AND gl_crown.SRCETYPE !='JE';

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT DISTINCT
          `j`.`BTCHENTRY` AS `code`,
          `j`.`JRNLDESC` AS `name`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `document_date`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `posting_date`,
          `j`.`JRNLDR` AS `amount`,
          `j`.`JRNLDR` AS `total_amount`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `update_date`,
          `t`.`TRANSAMT` AS `document_amount`,
          DATE_FORMAT(`j`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
          `t`.`TRANSAMT` AS `original_amount`,
          `t`.`JNLDTLREF` AS `reference`,
          CONCAT(`j`.`SRCELEDGER`, '-', `j`.`SRCETYPE`) AS `source_type`,
          `j`.`SRCELEDGER` AS `source_ledger`,
          IF(`j`.`SWREVERSE` > 0, 1, 0) AS `is_auto_reverse`,
          IF(`j`.`SWREVERSE` = 2, `j`.`REVPERD`, NULL) AS `reverse_to_period_val`,
          `j`.`FSCSPERD` AS `perd_month`,
          `j`.`FSCSYR` AS `perd_year`
       FROM `ikari_db_sage300`.`gljeh` AS `j`
      LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
      LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
      WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
        AND `j`.`SRCETYPE` = 'GL'
        AND `t`.`TRANSAMT` > 0
        AND `t`.`JNLDTLREF` != 'REVERSING ENTRY'
        AND `b`.`BATCHTYPE` = 2
      GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`
  ) t2;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT DISTINCT
          `t`.`ENTRYNBR` AS `code`,
          `t`.`JNLDTLDESC` AS `name`,
          DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `document_date`,
          DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `posting_date`,
          `t`.`TRANSAMT` AS `amount`,
          `t`.`TRANSAMT` AS `total_amount`,
          DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
          DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
          `t`.`TRANSAMT` AS `document_amount`,
          DATE_FORMAT(`t`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
          `t`.`TRANSAMT` AS `original_amount`,
          `t`.`JNLDTLREF` AS `reference`,
          CONCAT(`t`.`SRCELEDGER`, '-', `t`.`SRCETYPE`) AS `source_type`,
          `t`.`SRCELEDGER` AS `source_ledger`,
          IF(`t`.`SWREVERSE` > 0, 1, 0) AS `is_auto_reverse`,
          (CASE
           WHEN `t`.`SWREVERSE` = 1 THEN '1'
           WHEN `t`.`SWREVERSE` = 2 THEN '2'
           ELSE NULL
           END) AS `reverse_to_period`,
          `t`.`FISCALPERD` AS `perd_month`,
          `t`.`FISCALYR` AS `perd_year`
      FROM `ikari_db_sage300`.`glpjd` AS `t`
      LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
      WHERE `t`.`SRCELEDGER` IN ('AR', 'AP')
        AND `t`.`SRCETYPE` = 'GL'
        AND `t`.`TRANSAMT` > 0
        AND `t`.`JNLDTLREF` = 'REVERSING ENTRY'
        AND `b`.`BATCHTYPE` = 2
      GROUP BY `t`.`BATCHNBR`, `t`.`ENTRYNBR`
  ) t3;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT DISTINCT
          `j`.`BTCHENTRY` AS `code`,
          `j`.`JRNLDESC` AS `name`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `document_date`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `posting_date`,
          `j`.`JRNLDR` AS `amount`,
          `j`.`JRNLDR` AS `total_amount`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `create_date`,
          DATE_FORMAT(`j`.`DATEENTRY`,'%Y-%m-%d') AS `update_date`,
          `t`.`TRANSAMT` AS `document_amount`,
          DATE_FORMAT(`j`.`AUDTDATE`, '%Y-%m-%d') AS `due_date`,
          `t`.`TRANSAMT` AS `original_amount`,
          CONCAT(`j`.`SRCELEDGER`, '-', `j`.`SRCETYPE`) AS `source_type`,
          `j`.`SRCELEDGER` AS `source_ledger`,
          IF(`j`.`SWREVERSE` > 0, 1, 0) AS `is_auto_reverse`,
          IF(`j`.`SWREVERSE` = 2, `j`.`REVPERD`, NULL) AS `reverse_to_period_val`,
          `j`.`FSCSPERD` AS `perd_month`,
          `j`.`FSCSYR` AS `perd_year`
      FROM `ikari_db_sage300`.`gljeh` AS `j`
      LEFT JOIN `ikari_db_sage300`.`glpjd` AS `t` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
      LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
      WHERE `j`.`SRCELEDGER` IN ('AR', 'AP')
      AND `j`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY')
      AND `t`.`TRANSAMT` > 0
      AND `b`.`BATCHTYPE` = 2
      GROUP BY `j`.`BATCHID`, `j`.`BTCHENTRY`, `j`.`BTCHENTRY`, `j`.`JRNLDR`, `j`.`JRNLCR`
  ) t4;

  SET L_totalrow := L_totalrow + L_cnt;

  RETURN L_totalrow;

END $$
delimiter ;
# End src_journal


delimiter $$
DROP FUNCTION IF EXISTS src_transaction $$

CREATE FUNCTION src_transaction (I_company_id int)
RETURNS int
BEGIN
  
  DECLARE L_cnt,L_totalrow int DEFAULT 0;

  SELECT count(*)
    INTO L_cnt
  FROM (
    SELECT 1
      FROM ikari_db_sage300.apibd t, ikari_db_sage300.apibh j
     WHERE t.cntbtch=j.cntbtch
       AND t.cntitem=j.cntitem
    UNION ALL
    SELECT 2
      FROM ikari_db_sage300.aribd t, ikari_db_sage300.aribh j
     WHERE t.cntbtch=j.cntbtch
       AND t.cntitem=j.cntitem) t12;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT DISTINCT
             t.AMTPAYM amount
             ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
             ,t.CNTLINE number
             ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
             ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
             ,aas.control_account_id account_id
             ,t.AMTPAYM total_amount
             ,tx.RATEEXCHTC exchange_rate
             ,t.AMTPAYMHC functional_amount
             ,date_format(tx.RATEDATETC ,'%Y-%m-%d') rate_date
        FROM ikari_db_sage300.aptcr j
        RIGHT OUTER JOIN ikari_db_sage300.aptcp t on j.cntbtch=t.cntbtch
            AND j.cntentr=t.cntrmit
        LEFT OUTER JOIN banks_bank bnk on j.idbank=bnk.code
            and bnk.company_id=I_company_id
        LEFT OUTER JOIN accounts_accountset aas on j.idacctset=aas.code
            and aas.company_id=I_company_id
        LEFT OUTER JOIN ikari_db_sage300.appjh tx on t.batchtype=tx.typebtch
            and t.cntbtch=tx.cntbtch
            and t.cntrmit=tx.cntitem
        LEFT OUTER JOIN ikari_db_sage300.apibh inv on t.idinvc=inv.idinvc
            and t.cntbtch=tx.cntbtch
            and t.cntrmit=tx.cntitem) t3;

  SET L_totalrow := L_totalrow + L_cnt;


  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT 3
        FROM ikari_db_sage300.artcr j
        RIGHT OUTER JOIN ikari_db_sage300.artcp t on j.cntbtch=t.cntbtch
            AND j.CNTITEM=t.CNTITEM
        LEFT OUTER JOIN banks_bank bnk on j.idbank=bnk.code
            and bnk.company_id=I_company_id
        LEFT OUTER JOIN accounts_accountset aas on j.idacctset=aas.code
            and aas.company_id=I_company_id
        LEFT OUTER JOIN accounting_batch ab on j.cntbtch=ab.batch_no
            and ab.batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
        LEFT OUTER JOIN ikari_db_sage300.arpjh tx on t.CODEPAYM=tx.typebtch
            and t.cntbtch=tx.cntbtch
            and t.CNTITEM=tx.cntitem
        LEFT OUTER JOIN ikari_db_sage300.aribh inv on t.idinvc=inv.idinvc
            and t.cntbtch=tx.cntbtch
            and t.CNTITEM=tx.cntitem) t4;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (SELECT DISTINCT
            t.AMTNETTC amount
            ,date_format(j.DATERMIT,'%Y-%m-%d') transaction_date
            ,date_format(t.AUDTDATE,'%Y-%m-%d') create_date
            ,date_format(t.AUDTDATE,'%Y-%m-%d') update_date
            ,aa.id account_id
            ,t.TXBSE1TC base_tax_amount
            ,t.TXTOTTC tax_amount
            ,t.AMTDISTTC total_amount
            ,ad.id distribution_code_id
            ,t.GLDESC description
            ,tx.RATEEXCHTC exchange_rate
            ,t.AMTDISTHC functional_amount
            ,date_format(tx.RATEDATETC,'%Y-%m-%d') rate_date
            ,t.GLREF reference
            ,t.SWTAXINCL1 is_tax_include
    FROM ikari_db_sage300.aptcr j
    RIGHT OUTER JOIN ikari_db_sage300.aptcn t on j.cntbtch=t.cntbtch
        AND j.cntentr=t.cntrmit
    LEFT OUTER JOIN ikari_db_sage300.appjh tx on t.batchtype=tx.typebtch
        and t.cntbtch=tx.cntbtch
        and t.cntrmit=tx.cntitem
    LEFT OUTER JOIN accounts_distributioncode ad on t.IDDISTCODE=ad.code
        and ad.company_id=I_company_id
    LEFT OUTER JOIN accounts_account aa on t.idacct=aa.code
        and aa.company_id=I_company_id) t5;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT 6
        FROM ikari_db_sage300.artcr j
        RIGHT OUTER JOIN ikari_db_sage300.artcn t on j.cntbtch=t.cntbtch
            AND j.CNTITEM=t.CNTITEM
        LEFT OUTER JOIN accounting_batch ab on j.cntbtch=ab.batch_no
            and ab.batch_type=3 -- TRANSACTION_TYPES['AR Receipt'] --
        LEFT OUTER JOIN ikari_db_sage300.arpjh tx on t.CODEPAYM=tx.typebtch
            and t.cntbtch=tx.cntbtch
            and t.CNTITEM=tx.cntitem
        LEFT OUTER JOIN ikari_db_sage300.arrrd tax on  t.cntbtch=tax.CNTBTCH
            and t.CNTITEM=tax.CNTITEM
            and t.IDACCT=tax.IDACCT
        LEFT OUTER JOIN accounts_account aa on t.idacct=aa.code
            and aa.company_id = I_company_id
        LEFT OUTER JOIN accounts_distributioncode ad on t.IDDISTCODE=ad.code
            and ad.company_id = I_company_id) t6;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT 7
        FROM `ikari_db_sage300`.`glpjd` AS `t`
      LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `j`.`BTCHENTRY` = `t`.`ENTRYNBR`
          WHERE `j`.`SRCETYPE` IN ('JE', 'RV')
      UNION ALL
      SELECT 8
        FROM  ikari_db_sage300.glbctl b
      RIGHT OUTER JOIN  ikari_db_sage300.gljeh j ON b.BATCHID = j.BATCHID
      LEFT OUTER JOIN ikari_db_sage300.gljed t ON j.BTCHENTRY = t.JOURNALID and j.BATCHID = t.BATCHNBR
       WHERE b.BATCHTYPE IN (1, 3, 4)
         AND j.SRCETYPE NOT IN ('JE', 'RV')) t78;

  SET L_totalrow := L_totalrow + L_cnt;

  SELECT count(*)
    INTO L_cnt
    FROM (
      SELECT DISTINCT
          IF(`t`.`TRANSAMT` < 0, 1, 0) AS `is_credit_transaction`,
          IF(`t`.`TRANSAMT` < 0, 0, 1) AS `is_debit_transaction`,
          ABS(`t`.`TRANSAMT`) AS `amount`,
          DATE_FORMAT(`t`.`JRNLDATE`,'%Y-%m-%d') AS `transaction_date`,
          `t`.`ENTRYNBR` AS `number`,
          DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `create_date`,
          DATE_FORMAT(`t`.`AUDTDATE`,'%Y-%m-%d') AS `update_date`,
          ABS(`t`.`SCURNAMT`) AS `total_amount`,
          `t`.`JNLDTLDESC` AS `description`,
          `t`.`CONVRATE` AS `exchange_rate`,
          ABS(`t`.`TRANSAMT`) AS `functional_amount`,
          DATE_FORMAT(`RATEDATE`,'%Y-%m-%d') AS `rate_date`,
          `t`.`JNLDTLREF` AS `reference`,
          IF(`TRANSAMT` < 0, 2, 1) AS `functional_balance_type`
      FROM `ikari_db_sage300`.`glpjd` AS `t`
      LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR`
      /* WHERE `j`.`SRCETYPE` = 'RV' AND `t`.`JNLDTLREF` = 'REVERSING ENTRY'; */
      WHERE `j`.`SRCETYPE` = 'RV') t9;

  SET L_totalrow := L_totalrow + L_cnt;


  SELECT count(*)
    INTO L_cnt
  FROM(
    SELECT 10
      FROM `ikari_db_sage300`.`glpjd` AS `t`
    LEFT JOIN `ikari_db_sage300`.`gljeh` AS `j` ON `j`.`BATCHID` = `t`.`BATCHNBR` AND `t`.`ENTRYNBR` = `j`.`BTCHENTRY`
    LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
        WHERE `t`.`SRCELEDGER` IN ('AP','AR')
          AND `t`.`SRCETYPE` IN ('CR', 'DB', 'IN', 'PY')
          AND `b`.`BATCHTYPE` = 2
    UNION ALL
    SELECT 11
      FROM `ikari_db_sage300`.`glpjd` AS `t`
    LEFT JOIN `ikari_db_sage300`.`glbctl` AS `b` ON `b`.`BATCHID` = `t`.`BATCHNBR`
        WHERE `t`.`SRCELEDGER` IN ('AR','AP')
          AND `t`.`SRCETYPE` = 'GL'
          AND `b`.`BATCHTYPE` = 2) t10_11;

  SET L_totalrow := L_totalrow + L_cnt;

  RETURN L_totalrow;

END $$
delimiter ;
# End src_transaction
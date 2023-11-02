
SET @company_id=3; -- Crown --

call merge_customers('CFCYEN', 'CROWNJ-Y');
call merge_customers('YAMUS$', 'YSS-U');
call merge_customers('IKAUS$', 'IKARI-U');
call merge_customers('CFHUS$', 'CROWNH-U');
call merge_customers('ECPUS$', 'ECF(T)-U');
call merge_customers('SPSUS$', 'SANKO-U');
call merge_customers('PTAUS$', 'AISIN-U');
call merge_customers('DAIUS$', 'EXEDY-U');
call merge_customers('PTKUS$', 'KAYABA-U');
call merge_customers('PTEUS$', 'EMI-U');
call merge_customers('OLIUS$', 'OLP-U');
call merge_customers('YETUS$', 'YET-U');
call merge_customers('SSPUS$', 'SHIMANO-U');


call merge_suppliers('CFCYEN', 'CROWNJ-Y');
call merge_suppliers('IKEUS$', 'IKARI-U');
call merge_suppliers('IKENS$', 'IKARI-Y');
call merge_suppliers('CHKUS$', 'CROWNH-U');
call merge_suppliers('ECFUS$', 'ECF(T)-U');
call merge_suppliers('SANUS$', 'SANKO-U');

SET @company_id=4; -- Nitto --

call merge_customers('CLARIONHKUS$', 'CIHK-U');
call merge_customers('EOGUS$', 'EMPR-U');
call merge_customers('GETUS$', 'GSK-U');
call merge_customers('GESUS$', 'GSKS-U');
call merge_customers('HIGAUS', 'HIGA-U');
call merge_customers('HOEUS$', 'HOEI-U');
call merge_customers('IKASGD', 'IKARI-S');
call merge_customers('IKAUS$', 'IKARI-U');
call merge_customers('JUNSHOU', 'OSC-U');
call merge_customers('JESUS$', 'JES-U');
call merge_customers('JVMUS$', 'JMM-U');
call merge_customers('NIKUS$', 'ND(HK)-U');
call merge_customers('NHZUS$', 'N(HZ)-U');
call merge_customers('NQZUS$', 'N(QZ)-U');
call merge_customers('NDKUS$', 'N(J)-U');
call merge_customers('NDKYEN', 'N(J)-Y');
call merge_customers('NSHZUS', 'NSDHZ-U');
call merge_customers('SAGIUS', 'SGN-U');
call merge_customers('SNVUS$', 'SNDV-U');
call merge_customers('SMUKU$', 'SMK(E)-U');
call merge_customers('SMHUS$', 'SMKHK-U');
call merge_customers('SMKUS$', 'SMK-U');
call merge_customers('SISUS$', 'SEPS-U');
call merge_customers('SUNUS$', 'SNW-U');
call merge_customers('TOKOUS', 'TOKO-U');
call merge_customers('TINCUS', 'TOKO(J)-U');
call merge_customers('YETUS$', 'YET-U');

call merge_suppliers('AAPUS$', 'ACN-U');
call merge_suppliers('AEPUS$', 'ARS-U');
call merge_suppliers('AVISUS', 'ANV-U');
call merge_suppliers('FDIUS$', 'FD-U');
call merge_suppliers('FLEUSD', 'FLEX-U');
call merge_suppliers('GSKES$', 'GSK-S');
call merge_suppliers('GSKUS$', 'GSK-U');
call merge_suppliers('HITAUS', 'HTC-U');
call merge_suppliers('IKARS$', 'IKARI-S');
call merge_suppliers('IKAUS$', 'IKARI-U');
call merge_suppliers('KANEUS', 'KNT-U');
call merge_suppliers('LUMIUS', 'LMN-U');
call merge_suppliers('NNHUS$', 'NNDKHZ-U');
call merge_suppliers('NHZUSD', 'N(HZ)-U');
call merge_suppliers('NITYEN', 'N(JP)-Y');
call merge_suppliers('NITUS$', 'N(J)-U');
call merge_suppliers('NQZUS$', 'N(QZ)-U');
call merge_suppliers('NSDUS$', 'NSDHZ-U');
call merge_suppliers('NPRIUS', 'NPL-U');
call merge_suppliers('SERUS$', 'SME-U');
call merge_suppliers('SUMSGD', 'SEPS-S');
call merge_suppliers('SEIUS$', 'SEPS-U');
call merge_suppliers('SHKUS$', 'SEI-U');
call merge_suppliers('TUBUS$', 'TFL-U');
call merge_suppliers('TYCEUS', 'TY-U');
call merge_suppliers('TYCOS$', 'TYCO-S');


####INSERT DUMMY CUSTOMER
INSERT INTO customers_customer (
`code`,`is_active`,`is_hidden`,`create_date`,`update_date`,`update_by`,`company_id`,`currency_id`)
VALUES
('JPA-U',1,0,date_format('2017-01-19','%Y-%m-%d'),date_format('2017-01-19','%Y-%m-%d'),NULL,@company_id,(SELECT id FROM currencies_currency where code='USD')),
('IK-S',1,0,date_format('2017-01-19','%Y-%m-%d'),date_format('2017-01-19','%Y-%m-%d'),NULL,@company_id,(SELECT id FROM currencies_currency where code='USD')),
('IK',1,0,date_format('2017-01-19','%Y-%m-%d'),date_format('2017-01-19','%Y-%m-%d'),NULL,@company_id,(SELECT id FROM currencies_currency where code='USD'));

####INSERT DUMMY SUPPLIER
INSERT INTO suppliers_supplier
(`code`,`is_active`,`is_hidden`,`create_date`,`update_date`,`update_by`,`company_id`,`currency_id`)
VALUES
('IK-U',1,0,date_format('2017-01-19','%Y-%m-%d'),date_format('2017-01-19','%Y-%m-%d'),NULL,@company_id,(SELECT id FROM currencies_currency where code='USD')),
('IK-S',1,0,date_format('2017-01-19','%Y-%m-%d'),date_format('2017-01-19','%Y-%m-%d'),NULL,@company_id,(SELECT id FROM currencies_currency where code='USD'));

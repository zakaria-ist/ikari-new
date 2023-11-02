
delimiter $$
DROP PROCEDURE IF EXISTS change_customer_code$$
create procedure change_customer_code(in code1 varchar(20), in code2 varchar(20))
begin

UPDATE customers_customer set
	code := code2
where company_id=@company_id and `code`=code1 ;

end$$
delimiter ;


delimiter $$
DROP PROCEDURE IF EXISTS change_supplier_code$$
create procedure change_supplier_code(in code1 varchar(20), in code2 varchar(20))
begin

UPDATE suppliers_supplier set
	code := code2
where company_id=@company_id and `code`=code1 ;

end$$
delimiter ;

SET @company_id=3; -- Crown --

/* before migration */
call change_customer_code('CROWNJ-Y', 'CFCYEN');
call change_customer_code('YSS-U', 'YAMUS$');
call change_customer_code('IKARI-U', 'IKAUS$');
call change_customer_code('CROWNH-U', 'CFHUS$');
call change_customer_code('ECF(T)-U', 'ECPUS$');
call change_customer_code('SANKO-U', 'SPSUS$');
call change_customer_code('AISIN-U', 'PTAUS$');
call change_customer_code('EXEDY-U', 'DAIUS$');
call change_customer_code('KAYABA-U', 'PTKUS$');
call change_customer_code('EMI-U', 'PTEUS$');
call change_customer_code('OLP-U', 'OLIUS$');
call change_customer_code('YET-U', 'YETUS$');
call change_customer_code('SHIMANO-U', 'SSPUS$');

call change_supplier_code('CROWNJ-Y', 'CFCYEN');
call change_supplier_code('IKARI-U', 'IKEUS$');
call change_supplier_code('IKARI-Y', 'IKENS$');
call change_supplier_code('CROWNH-U', 'CHKUS$');
call change_supplier_code('ECF(T)-U', 'ECFUS$');
call change_supplier_code('SANKO-U', 'SANUS$');


/* after migration */
call change_customer_code('CFCYEN', 'CROWNJ-Y');
call change_customer_code('YAMUS$', 'YSS-U');
call change_customer_code('IKAUS$', 'IKARI-U');
call change_customer_code('CFHUS$', 'CROWNH-U');
call change_customer_code('ECPUS$', 'ECF(T)-U');
call change_customer_code('SPSUS$', 'SANKO-U');
call change_customer_code('PTAUS$', 'AISIN-U');
call change_customer_code('DAIUS$', 'EXEDY-U');
call change_customer_code('PTKUS$', 'KAYABA-U');
call change_customer_code('PTEUS$', 'EMI-U');
call change_customer_code('OLIUS$', 'OLP-U');
call change_customer_code('YETUS$', 'YET-U');
call change_customer_code('SSPUS$', 'SHIMANO-U');

call change_supplier_code('CFCYEN', 'CROWNJ-Y');
call change_supplier_code('IKEUS$', 'IKARI-U');
call change_supplier_code('IKENS$', 'IKARI-Y');
call change_supplier_code('CHKUS$', 'CROWNH-U');
call change_supplier_code('ECFUS$', 'ECF(T)-U');
call change_supplier_code('SANUS$', 'SANKO-U');




SET @company_id=4; -- Nitto --

/* before migration */
call change_customer_code('CIHK-U', 'CLARIONHKUS$');
call change_customer_code('EMPR-U', 'EOGUS$');
call change_customer_code('GSK-U', 'GETUS$');
call change_customer_code('GSKS-U', 'GESUS$');
call change_customer_code('HIGA-U', 'HIGAUS');
call change_customer_code('HOEI-U', 'HOEUS$');
call change_customer_code('IKARI-S', 'IKASGD');
call change_customer_code('IKARI-U', 'IKAUS$');
call change_customer_code('OSC-U', 'JUNSHOU');
call change_customer_code('JES-U', 'JESUS$');
call change_customer_code('JMM-U', 'JVMUS$');
call change_customer_code('ND(HK)-U', 'NIKUS$');
call change_customer_code('N(HZ)-U', 'NHZUS$');
call change_customer_code('N(QZ)-U', 'NQZUS$');
call change_customer_code('N(J)-U', 'NDKUS$');
call change_customer_code('N(J)-Y', 'NDKYEN');
call change_customer_code('NSDHZ-U', 'NSHZUS');
call change_customer_code('SGN-U', 'SAGIUS');
call change_customer_code('SNDV-U', 'SNVUS$');
call change_customer_code('SMK(E)-U', 'SMUKU$');
call change_customer_code('SMKHK-U', 'SMHUS$');
call change_customer_code('SMK-U', 'SMKUS$');
call change_customer_code('SEPS-U', 'SISUS$');
call change_customer_code('SNW-U', 'SUNUS$');
call change_customer_code('TOKO-U', 'TOKOUS');
call change_customer_code('TOKO(J)-U', 'TINCUS');
call change_customer_code('YET-U', 'YETUS$');


call change_supplier_code('ACN-U', 'AAPUS$');
call change_supplier_code('ARS-U', 'AEPUS$');
call change_supplier_code('ANV-U', 'AVISUS');
call change_supplier_code('FD-U', 'FDIUS$');
call change_supplier_code('FLEX-U', 'FLEUSD');
call change_supplier_code('GSK-S', 'GSKES$');
call change_supplier_code('GSK-U', 'GSKUS$');
call change_supplier_code('HTC-U', 'HITAUS');
call change_supplier_code('IKARI-S', 'IKARS$');
call change_supplier_code('IKARI-U', 'IKAUS$');
call change_supplier_code('KNT-U', 'KANEUS');
call change_supplier_code('LMN-U', 'LUMIUS');
call change_supplier_code('NNDKHZ-U', 'NNHUS$');
call change_supplier_code('N(HZ)-U', 'NHZUSD');
call change_supplier_code('N(JP)-Y', 'NITYEN');
call change_supplier_code('N(J)-U', 'NITUS$');
call change_supplier_code('N(QZ)-U', 'NQZUS$');
call change_supplier_code('NSDHZ-U', 'NSDUS$');
call change_supplier_code('NPL-U', 'NPRIUS');
call change_supplier_code('SME-U', 'SERUS$');
call change_supplier_code('SEPS-S', 'SUMSGD');
call change_supplier_code('SEPS-U', 'SEIUS$');
call change_supplier_code('SEI-U', 'SHKUS$');
call change_supplier_code('TFL-U', 'TUBUS$');
call change_supplier_code('TY-U', 'TYCEUS');
call change_supplier_code('TYCO-S', 'TYCOS$');



/* after migration */
call change_customer_code('CLARIONHKUS$', 'CIHK-U');
call change_customer_code('EOGUS$', 'EMPR-U');
call change_customer_code('GETUS$', 'GSK-U');
call change_customer_code('GESUS$', 'GSKS-U');
call change_customer_code('HIGAUS', 'HIGA-U');
call change_customer_code('HOEUS$', 'HOEI-U');
call change_customer_code('IKASGD', 'IKARI-S');
call change_customer_code('IKAUS$', 'IKARI-U');
call change_customer_code('JUNSHOU', 'OSC-U');
call change_customer_code('JESUS$', 'JES-U');
call change_customer_code('JVMUS$', 'JMM-U');
call change_customer_code('NIKUS$', 'ND(HK)-U');
call change_customer_code('NHZUS$', 'N(HZ)-U');
call change_customer_code('NQZUS$', 'N(QZ)-U');
call change_customer_code('NDKUS$', 'N(J)-U');
call change_customer_code('NDKYEN', 'N(J)-Y');
call change_customer_code('NSHZUS', 'NSDHZ-U');
call change_customer_code('SAGIUS', 'SGN-U');
call change_customer_code('SNVUS$', 'SNDV-U');
call change_customer_code('SMUKU$', 'SMK(E)-U');
call change_customer_code('SMHUS$', 'SMKHK-U');
call change_customer_code('SMKUS$', 'SMK-U');
call change_customer_code('SISUS$', 'SEPS-U');
call change_customer_code('SUNUS$', 'SNW-U');
call change_customer_code('TOKOUS', 'TOKO-U');
call change_customer_code('TINCUS', 'TOKO(J)-U');
call change_customer_code('YETUS$', 'YET-U');


call change_supplier_code('AAPUS$', 'ACN-U');
call change_supplier_code('AEPUS$', 'ARS-U');
call change_supplier_code('AVISUS', 'ANV-U');
call change_supplier_code('FDIUS$', 'FD-U');
call change_supplier_code('FLEUSD', 'FLEX-U');
call change_supplier_code('GSKES$', 'GSK-S');
call change_supplier_code('GSKUS$', 'GSK-U');
call change_supplier_code('HITAUS', 'HTC-U');
call change_supplier_code('IKARS$', 'IKARI-S');
call change_supplier_code('IKAUS$', 'IKARI-U');
call change_supplier_code('KANEUS', 'KNT-U');
call change_supplier_code('LUMIUS', 'LMN-U');
call change_supplier_code('NNHUS$', 'NNDKHZ-U');
call change_supplier_code('NHZUSD', 'N(HZ)-U');
call change_supplier_code('NITYEN', 'N(JP)-Y');
call change_supplier_code('NITUS$', 'N(J)-U');
call change_supplier_code('NQZUS$', 'N(QZ)-U');
call change_supplier_code('NSDUS$', 'NSDHZ-U');
call change_supplier_code('NPRIUS', 'NPL-U');
call change_supplier_code('SERUS$', 'SME-U');
call change_supplier_code('SUMSGD', 'SEPS-S');
call change_supplier_code('SEIUS$', 'SEPS-U');
call change_supplier_code('SHKUS$', 'SEI-U');
call change_supplier_code('TUBUS$', 'TFL-U');
call change_supplier_code('TYCEUS', 'TY-U');
call change_supplier_code('TYCOS$', 'TYCO-S');
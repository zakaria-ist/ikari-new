
#SET @company_id=5; -- TAGA --

call merge_customers('EXEI-USD', 'EXEDY-U', @company_id);
call merge_customers('PTAI-YEN', 'PTAISIN-Y', @company_id);
call merge_customers('PTAKEUSD', 'PTAKE-U', @company_id);
call merge_customers('SIAM-USD', 'STP-U', @company_id);
call merge_customers('STAR-SGD', 'STARNET-S', @company_id);


call merge_suppliers('STPCLUSD', 'STP-U', @company_id);
call merge_suppliers('TAGAYEN', 'TCL-Y', @company_id);
call merge_suppliers('TATIAUSD', 'TTS-U', @company_id);

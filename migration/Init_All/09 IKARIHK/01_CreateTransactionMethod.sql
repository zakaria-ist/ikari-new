SET @company_id = 9;
SET FOREIGN_KEY_CHECKS=0;

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

SET FOREIGN_KEY_CHECKS=1;

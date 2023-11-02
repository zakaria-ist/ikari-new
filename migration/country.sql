/* vietnum */
UPDATE banks_bank SET country_id := 31 WHERE country_id IN (11, 37);
UPDATE companies_company SET country_id := 31 WHERE country_id IN (11, 37);
UPDATE customers_customer SET country_id := 31 WHERE country_id IN (11, 37);
UPDATE items_item SET country_id := 31 WHERE country_id IN (11, 37);
UPDATE orders_orderitem SET origin_country_id := 31 WHERE origin_country_id IN (11, 37);
UPDATE suppliers_supplier SET country_id := 31 WHERE country_id IN (11, 37);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (11, 37, 15);
/* canada */
UPDATE banks_bank SET country_id := 25 WHERE country_id IN (46);
UPDATE companies_company SET country_id := 25 WHERE country_id IN (46);
UPDATE customers_customer SET country_id := 25 WHERE country_id IN (46);
UPDATE items_item SET country_id := 25 WHERE country_id IN (46);
UPDATE orders_orderitem SET origin_country_id := 25 WHERE origin_country_id IN (46);
UPDATE suppliers_supplier SET country_id := 25 WHERE country_id IN (46);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (46);
/* china */
UPDATE banks_bank SET country_id := 5 WHERE country_id IN (32);
UPDATE companies_company SET country_id := 5 WHERE country_id IN (32);
UPDATE customers_customer SET country_id := 5 WHERE country_id IN (32);
UPDATE items_item SET country_id := 5 WHERE country_id IN (32);
UPDATE orders_orderitem SET origin_country_id := 5 WHERE origin_country_id IN (32);
UPDATE suppliers_supplier SET country_id := 5 WHERE country_id IN (32);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (32);
/* germany */
UPDATE banks_bank SET country_id := 18 WHERE country_id IN (43);
UPDATE companies_company SET country_id := 18 WHERE country_id IN (43);
UPDATE customers_customer SET country_id := 18 WHERE country_id IN (43);
UPDATE items_item SET country_id := 18 WHERE country_id IN (43);
UPDATE orders_orderitem SET origin_country_id := 18 WHERE origin_country_id IN (43);
UPDATE suppliers_supplier SET country_id := 18 WHERE country_id IN (43);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (43);
/* india */
UPDATE banks_bank SET country_id := 29 WHERE country_id IN (23);
UPDATE companies_company SET country_id := 29 WHERE country_id IN (23);
UPDATE customers_customer SET country_id := 29 WHERE country_id IN (23);
UPDATE items_item SET country_id := 29 WHERE country_id IN (23);
UPDATE orders_orderitem SET origin_country_id := 29 WHERE origin_country_id IN (23);
UPDATE suppliers_supplier SET country_id := 29 WHERE country_id IN (23);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (23);
/* indoneshia */
UPDATE banks_bank SET country_id := 6 WHERE country_id IN (38);
UPDATE companies_company SET country_id := 6 WHERE country_id IN (38);
UPDATE customers_customer SET country_id := 6 WHERE country_id IN (38);
UPDATE items_item SET country_id := 6 WHERE country_id IN (38);
UPDATE orders_orderitem SET origin_country_id := 6 WHERE origin_country_id IN (38);
UPDATE suppliers_supplier SET country_id := 6 WHERE country_id IN (38);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (38);
/* japan */
UPDATE banks_bank SET country_id := 12 WHERE country_id IN (33);
UPDATE companies_company SET country_id := 12 WHERE country_id IN (33);
UPDATE customers_customer SET country_id := 12 WHERE country_id IN (33);
UPDATE items_item SET country_id := 12 WHERE country_id IN (33);
UPDATE orders_orderitem SET origin_country_id := 12 WHERE origin_country_id IN (33);
UPDATE suppliers_supplier SET country_id := 12 WHERE country_id IN (33);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (33);
/* korea */
UPDATE banks_bank SET country_id := 14 WHERE country_id IN (21, 39);
UPDATE companies_company SET country_id := 14 WHERE country_id IN (21, 39);
UPDATE customers_customer SET country_id := 14 WHERE country_id IN (21, 39);
UPDATE items_item SET country_id := 14 WHERE country_id IN (21, 39);
UPDATE orders_orderitem SET origin_country_id := 14 WHERE origin_country_id IN (21, 39);
UPDATE suppliers_supplier SET country_id := 14 WHERE country_id IN (21, 39);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (21, 39);
/* malaysia */
UPDATE banks_bank SET country_id := 13 WHERE country_id IN (34);
UPDATE companies_company SET country_id := 13 WHERE country_id IN (34);
UPDATE customers_customer SET country_id := 13 WHERE country_id IN (34);
UPDATE items_item SET country_id := 13 WHERE country_id IN (34);
UPDATE orders_orderitem SET origin_country_id := 13 WHERE origin_country_id IN (34);
UPDATE suppliers_supplier SET country_id := 13 WHERE country_id IN (34);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (34);
/* philipines */
UPDATE banks_bank SET country_id := 17 WHERE country_id IN (42);
UPDATE companies_company SET country_id := 17 WHERE country_id IN (42);
UPDATE customers_customer SET country_id := 17 WHERE country_id IN (42);
UPDATE items_item SET country_id := 17 WHERE country_id IN (42);
UPDATE orders_orderitem SET origin_country_id := 17 WHERE origin_country_id IN (42);
UPDATE suppliers_supplier SET country_id := 17 WHERE country_id IN (42);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (42);
/* singapore */
UPDATE banks_bank SET country_id := 3 WHERE country_id IN (35);
UPDATE companies_company SET country_id := 3 WHERE country_id IN (35);
UPDATE customers_customer SET country_id := 3 WHERE country_id IN (35);
UPDATE items_item SET country_id := 3 WHERE country_id IN (35);
UPDATE orders_orderitem SET origin_country_id := 3 WHERE origin_country_id IN (35);
UPDATE suppliers_supplier SET country_id := 3 WHERE country_id IN (35);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (35);
/* switzerland */
UPDATE banks_bank SET country_id := 27 WHERE country_id IN (45);
UPDATE companies_company SET country_id := 27 WHERE country_id IN (45);
UPDATE customers_customer SET country_id := 27 WHERE country_id IN (45);
UPDATE items_item SET country_id := 27 WHERE country_id IN (45);
UPDATE orders_orderitem SET origin_country_id := 27 WHERE origin_country_id IN (45);
UPDATE suppliers_supplier SET country_id := 27 WHERE country_id IN (45);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (45);
/* taiwan */
UPDATE banks_bank SET country_id := 9 WHERE country_id IN (24, 26);
UPDATE companies_company SET country_id := 9 WHERE country_id IN (24, 26);
UPDATE customers_customer SET country_id := 9 WHERE country_id IN (24, 26);
UPDATE items_item SET country_id := 9 WHERE country_id IN (24, 26);
UPDATE orders_orderitem SET origin_country_id := 9 WHERE origin_country_id IN (24, 26);
UPDATE suppliers_supplier SET country_id := 9 WHERE country_id IN (24, 26);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (24, 26);
/* thailand */
UPDATE banks_bank SET country_id := 16 WHERE country_id IN (20, 36);
UPDATE companies_company SET country_id := 16 WHERE country_id IN (20, 36);
UPDATE customers_customer SET country_id := 16 WHERE country_id IN (20, 36);
UPDATE items_item SET country_id := 16 WHERE country_id IN (20, 36);
UPDATE orders_orderitem SET origin_country_id := 16 WHERE origin_country_id IN (20, 36);
UPDATE suppliers_supplier SET country_id := 16 WHERE country_id IN (20, 36);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (20, 36);
/* usa */
UPDATE banks_bank SET country_id := 4 WHERE country_id IN (22);
UPDATE companies_company SET country_id := 4 WHERE country_id IN (22);
UPDATE customers_customer SET country_id := 4 WHERE country_id IN (22);
UPDATE items_item SET country_id := 4 WHERE country_id IN (22);
UPDATE orders_orderitem SET origin_country_id := 4 WHERE origin_country_id IN (22);
UPDATE suppliers_supplier SET country_id := 4 WHERE country_id IN (22);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (22);
/* spain */
UPDATE banks_bank SET country_id := 1 WHERE country_id IN (49);
UPDATE companies_company SET country_id := 1 WHERE country_id IN (49);
UPDATE customers_customer SET country_id := 1 WHERE country_id IN (49);
UPDATE items_item SET country_id := 1 WHERE country_id IN (49);
UPDATE orders_orderitem SET origin_country_id := 1 WHERE origin_country_id IN (49);
UPDATE suppliers_supplier SET country_id := 1 WHERE country_id IN (49);
UPDATE countries_country SET is_hidden := 1 WHERE id IN (49);

UPDATE countries_country SET currency_id := 10 WHERE id IN (1);
UPDATE countries_country SET currency_id := 15 WHERE id IN (2);
UPDATE countries_country SET currency_id := 9 WHERE id IN (3);
UPDATE countries_country SET currency_id := 32 WHERE id IN (4);
UPDATE countries_country SET currency_id := 7 WHERE id IN (5);
UPDATE countries_country SET currency_id := 17 WHERE id IN (6);
UPDATE countries_country SET currency_id := 16 WHERE id IN (7);
UPDATE countries_country SET currency_id := 25 WHERE id IN (9);
UPDATE countries_country SET currency_id := 34 WHERE id IN (12);
UPDATE countries_country SET currency_id := 23 WHERE id IN (13);
UPDATE countries_country SET currency_id := 36 WHERE id IN (14);
UPDATE countries_country SET currency_id := 31 WHERE id IN (16);
UPDATE countries_country SET currency_id := 37 WHERE id IN (17);
UPDATE countries_country SET currency_id := 11 WHERE id IN (18);
UPDATE countries_country SET currency_id := 11 WHERE id IN (19);
UPDATE countries_country SET currency_id := 5 WHERE id IN (25);
UPDATE countries_country SET currency_id := 6 WHERE id IN (27);
UPDATE countries_country SET currency_id := 11 WHERE id IN (28);
UPDATE countries_country SET currency_id := 38 WHERE id IN (29);
UPDATE countries_country SET currency_id := 26 WHERE id IN (30);
UPDATE countries_country SET currency_id := 33 WHERE id IN (31);
UPDATE countries_country SET currency_id := 22 WHERE id IN (40);
UPDATE countries_country SET currency_id := 41 WHERE id IN (41);
UPDATE countries_country SET currency_id := 14 WHERE id IN (44);
UPDATE countries_country SET currency_id := 40 WHERE id IN (47);
UPDATE countries_country SET currency_id := 39 WHERE id IN (48);
UPDATE countries_country SET currency_id := 11 WHERE id IN (50);
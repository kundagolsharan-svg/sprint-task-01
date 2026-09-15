-- 1. Company count
SELECT COUNT(*) AS company_count FROM companies;
-- 2. Loaded rows by table
SELECT 'profitandloss' AS table_name, COUNT(*) AS row_count FROM profitandloss UNION ALL
SELECT 'balancesheet', COUNT(*) FROM balancesheet UNION ALL
SELECT 'cashflow', COUNT(*) FROM cashflow UNION ALL
SELECT 'stock_prices', COUNT(*) FROM stock_prices;
-- 3. Companies with the most P&L history
SELECT company_id, COUNT(*) AS years FROM profitandloss GROUP BY company_id ORDER BY years DESC LIMIT 10;
-- 4. Latest annual profit
SELECT company_id, year, net_profit FROM profitandloss WHERE year <> 'TTM' ORDER BY year DESC, net_profit DESC LIMIT 20;
-- 5. Highest net margin
SELECT company_id, year, net_margin FROM financial_ratios ORDER BY net_margin DESC LIMIT 20;
-- 6. Debt to equity by company
SELECT company_id, AVG(debt_to_equity) AS average_debt_to_equity FROM financial_ratios GROUP BY company_id ORDER BY average_debt_to_equity DESC;
-- 7. Sector coverage
SELECT broad_sector, COUNT(*) AS companies, SUM(index_weight_pct) AS index_weight FROM sectors GROUP BY broad_sector ORDER BY index_weight DESC;
-- 8. Latest stock prices
SELECT company_id, date, close_price FROM stock_prices WHERE date = (SELECT MAX(date) FROM stock_prices) ORDER BY close_price DESC;
-- 9. Companies missing a balance-sheet period
SELECT c.company_id FROM companies c LEFT JOIN balancesheet b ON b.company_id = c.company_id WHERE b.company_id IS NULL;
-- 10. Foreign-key integrity (must return zero rows)
PRAGMA foreign_key_check;
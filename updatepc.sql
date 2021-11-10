SELECT * FROM pc ORDER BY model;

SELECT 1.0*AVG(cpu*1.0) FROM (SELECT cpu FROM pc UNION SELECT cpu FROM server UNION SELECT cpu FROM desktop UNION SELECT cpu from laptop);

UPDATE pc
SET price = price*(0.9)
WHERE cpu <= (SELECT 1.0*AVG(cpu*1.0)
                FROM (SELECT cpu FROM pc UNION SELECT cpu FROM server UNION SELECT cpu FROM desktop UNION SELECT cpu from laptop));
                
SELECT * FROM pc ORDER BY model;

--tv2
SELECT * FROM (
SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, screen_size FROM tv
UNION
SELECT CONCAT('A',model) AS name, price, 'H' AS type, screen_size FROM hdtv
UNION
SELECT CONCAT('A',model) AS name, price, 'P' AS type, screen_size FROM pdptv
UNION
SELECT CONCAT('A',model) AS name, price, 'L' AS type, screen_size FROM lcdtv
--ORDER BY type,name) wholetable
WHERE price <= (SELECT 1.0*AVG(1.0*price)
      FROM( SELECT price FROM tv UNION SELECT price FROM hdtv UNION SELECT price FROM pdptv UNION SELECT price FROM lcdtv) pricelist)
      AND
      screen_size >= (SELECT 1.0*AVG(1.0*screen_size)
      FROM( SELECT screen_size FROM tv UNION SELECT screen_size FROM hdtv UNION
            SELECT screen_size FROM pdptv UNION SELECT screen_size FROM lcdtv) screenlist)      
)
WHERE ((1.0*screen_size)/(1.0*price)) = (SELECT MAX((1.0*screen_size)/(1.0*price))
      FROM( SELECT screen_size,price FROM tv UNION SELECT screen_size,price FROM hdtv UNION
            SELECT screen_size,price FROM pdptv UNION SELECT screen_size,price FROM lcdtv) ratiolist)
ORDER BY name, screen_size, price;

SELECT 1.0*MAX((1.0*screen_size)/(1.0*price))
      FROM( SELECT screen_size,price FROM tv UNION SELECT screen_size,price FROM hdtv UNION
            SELECT screen_size,price FROM pdptv UNION SELECT screen_size,price FROM lcdtv);

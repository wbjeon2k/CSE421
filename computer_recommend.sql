SELECT CONCAT('A',model) AS name, price, 'D' AS type, cpu, NULL AS feature FROM desktop
WHERE (
    price <= (SELECT AVG(price) FROM desktop)
AND
    cpu >= (SELECT AVG(cpu) FROM desktop)
)
UNION
SELECT CONCAT('A',model) AS name, price, 'L' AS type, cpu, weight AS feature FROM laptop
WHERE (
    price <= (SELECT AVG(price) FROM laptop)
AND
    cpu >= (SELECT AVG(cpu) FROM laptop)
)
UNION
--B-PC-desktop recommend
SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
WHERE(
    type = 'D' AND
    price <= (SELECT AVG(price) FROM pc WHERE type='D') AND
    cpu >= (SELECT AVG(cpu) FROM pc WHERE type='D') 
)
UNION
--B-PC-laptop recommend
SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
WHERE(
    type = 'L' AND
    price <= (SELECT AVG(price) FROM pc WHERE type='L') AND
    cpu >= (SELECT AVG(cpu) FROM pc WHERE type='L') 
)
UNION
--B-server-recommend
SELECT CONCAT(CONCAT('B',model),code) AS name, price, 'S' AS type, cpu, NULL AS feature FROM server
WHERE(
    price <= (SELECT AVG(price) FROM server) AND
    cpu >= (SELECT AVG(cpu) FROM server) 
);

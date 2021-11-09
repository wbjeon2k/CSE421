--make copy of original data
CREATE new_server AS (SELECT * FROM server);
ALTER TABLE new_server ADD feature INT NULL;
ALTER TABLE new_server ADD new_name VARCHAR(100) NULL;
ALTER TABLE new_server ADD type VARCHAR2(10) DEFAULT 'S';
UPDATE new_server SET new_name = CONCAT(CONCAT('B',model),code);
SELECT *  FROM new_server;

--prototypes
SELECT CONCAT('A',model) AS name, NULL AS feature FROM pc;
---PC-->Computer convert
SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc;
--SERVER-->Computer
SELECT CONCAT(CONCAT('B',model),code) AS name, price, 'S' AS type, cpu, NULL AS feature FROM server;
--desktop --> Computer
SELECT CONCAT('A',model) AS name, price, 'D' AS type, cpu, NULL AS feature FROM desktop;
--laptop --> Computer
SELECT CONCAT('A',model) AS name, price, 'L' AS type, cpu, weight AS feature FROM laptop;
--Computer --> #1.get all items
SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
UNION
SELECT CONCAT(CONCAT('B',model),code) AS name, price, 'S' AS type, cpu, NULL AS feature FROM server
UNION
SELECT CONCAT('A',model) AS name, price, 'D' AS type, cpu, NULL AS feature FROM desktop
UNION
SELECT CONCAT('A',model) AS name, price, 'L' AS type, cpu, weight AS feature FROM laptop
ORDER BY type,name;

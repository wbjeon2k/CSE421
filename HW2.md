# make copy of original data
CREATE new_server AS (SELECT * FROM server);
ALTER TABLE new_server ADD feature INT NULL;
ALTER TABLE new_server ADD new_name VARCHAR(100) NULL;
ALTER TABLE new_server ADD type VARCHAR2(10) DEFAULT 'S';
UPDATE new_server SET new_name = CONCAT(CONCAT('B',model),code);
SELECT *  FROM new_server;


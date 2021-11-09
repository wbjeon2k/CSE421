import cx_Oracle

#it works!

connection = cx_Oracle.connect(
    user="unist",
    password="admin",
    dsn="localhost:1521"
)

#print("Connection established")

cursor = connection.cursor()
connection.commit()

cursor.execute("""
    SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
    UNION
    SELECT CONCAT(CONCAT('B',model),code) AS name, price, 'S' AS type, cpu, NULL AS feature FROM server
    UNION
    SELECT CONCAT('A',model) AS name, price, 'D' AS type, cpu, NULL AS feature FROM desktop
    UNION
    SELECT CONCAT('A',model) AS name, price, 'L' AS type, cpu, weight AS feature FROM laptop
    ORDER BY type,name
""")
connection.commit()
tmp = cursor.fetchall()
print(tmp)

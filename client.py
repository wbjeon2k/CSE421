import cx_Oracle

connection = cx_Oracle.connect(
    user="unist",
    password="admin",
    dsn="localhost:1521"
)

print("Connection established")

cursor = connection.cursor()

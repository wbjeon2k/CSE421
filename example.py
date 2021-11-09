import cx_Oracle

connection = cx_Oracle.connect(
    user="unist",
    password="admin",
    dsn="localhost:1521"
)

print("Connection established")

cursor = connection.cursor()

cursor.execute("""
    begin
        execute immediate 'drop table testtable';
    end;""")

cursor.execute("""
    create table testtable (
        id number generated always as identity,
        description varchar(50),
        creation_ts timestamp with time zone default current_timestamp,
        done number(1,0),
        primary key (id))""")

rows = [ ("Task1", 0), ("Task2", 1), ("Task3",0)]

cursor.executemany("insert into testtable (description, done) values(:1, :2)", rows)
print(cursor.rowcount, "Rows Inserted")

connection.commit()

for row in cursor.execute('select description, done from testtable'):
    if(row[1]):
        print(row[0], "DONE")
    else:
        print(row[0], "NOT DONE")

cursor.execute('select * from testtable')
tmp = cursor.fetchall()
print(tmp)

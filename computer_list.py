import cx_Oracle
#import client

def get_connection():
    connection = cx_Oracle.connect(
        user="unist",
        password="admin",
        dsn="localhost:1521"
    )
    return connection

#print("Connection established")
def computer_list():
    connection = get_connection()
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
    ret = cursor.fetchall()
    return ret

def computer_rec_list():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    
    cursor.execute("""
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
        )
    """)
    
    connection.commit()
    ret = cursor.fetchall()
    return ret

def print_computer_list(tmp):
    #tmp = computer_list()
    length = len(tmp)
    print("List of computer, ordered by type, name")
    print('%-8s' % "name", '%-8s' % "price", 
          '%-8s' % "type", '%-8s' % "cpu", '%-8s' % "feature")
    for i in range(length):
        print('%-8s' % tmp[i][0], '%-8s' % tmp[i][1],
              '%-8s' % tmp[i][2], '%-8s' % tmp[i][3], '%-8s' % tmp[i][4])

def main():
    print_computer_list(computer_list())
    print("---------TEST---------")
    print_computer_list(computer_rec_list())
    
if __name__ == "__main__":
    main()
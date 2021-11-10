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

def return_price_query(price_input):
    format_str = """
    SELECT * FROM (
    SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, screen_size FROM tv
    UNION
    SELECT CONCAT('A',model) AS name, price, 'H' AS type, screen_size FROM hdtv
    UNION
    SELECT CONCAT('A',model) AS name, price, 'P' AS type, screen_size FROM pdptv
    UNION
    SELECT CONCAT('A',model) AS name, price, 'L' AS type, screen_size FROM lcdtv
    ORDER BY type,name) wholetable
    WHERE ABS(price - %s) = (SELECT MIN(ABS(price-%s))
    FROM( SELECT price FROM tv UNION SELECT price FROM hdtv UNION SELECT price FROM pdptv UNION SELECT price FROM lcdtv) pricelist)
    ORDER BY name, screen_size, price
    """
    price_pair = (price_input, price_input)
    ret = format_str % price_pair
    return ret

def tv_list():
    #print("Connection established")
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    search_price = input()
    price_int = int(search_price, 10)
    if(price_int<0):
        raise Exception("Error at tv price input: input must be positive")
    cursor.execute(return_price_query(search_price))
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
        

def print_TV_list(tmp):
    #tmp = computer_list()
    length = len(tmp)
    print("List of computer, ordered by type, name")
    print('%-8s' % "name", '%-8s' % "price",
          '%-8s' % "type", '%-10s' % "screensize")
    for i in range(length):
        print('%-8s' % tmp[i][0], '%-8s' % tmp[i][1],
              '%-8s' % tmp[i][2], '%-10s' % tmp[i][3])
        
def select_computer():
    while(True):
        print("selected 1. Computer")
        print("""
            1. Product list
            2. Recommended products
            3. Back
        """)
        print("INPUT: ")
        key_input = int(input(), 10)
        if(key_input == 1):
            print("#1 List of all computers availble")
            print_computer_list(computer_list())
        elif(key_input == 2):
            print("#2 List of all PC recommendations")
            print_computer_list(computer_rec_list())
        elif(key_input == 3):
            print("#3 back to menu")
            break
        else:
            raise Exception("Invalid input at select_computer")
        

def select_TV():
    while(True):
        print("selected 2. TV")
        print("""
            1. Search by price
            2. Recommended products
            3. Back
        """)
        try:
            print("INPUT: ")
            key_input = int(input(), 10)
            if(key_input == 1):
                print("#1 Search TV by price")
                try:
                    print("PRICE: ")
                    print_TV_list(tv_list())
                except Exception as exp:
                    print(exp)
            elif(key_input == 2):
                print("#2 List of all TV recommendations")
                #print_computer_list(computer_rec_list())
            elif(key_input == 3):
                print("#3 back to menu")
                break
            else:
                raise Exception("Invalid input at select_TV")
        except Exception as exp:
            print("ERROR: ",exp)

def main():
    #print_computer_list(computer_list())
    #print("---------TEST---------")
    #print_computer_list(computer_rec_list())
    #print(return_price_query("ABC"))
    #print(tv_list())
    
    while(True):
        print("Main Menu.")
        print("""
            What are you looking for?
            1. Computer
            2. Television
            3. Price update
            4. Exit
        """)
        print("INPUT: ")
        try:
            key_input = int(input(), 10)
            if(key_input == 1):
                select_computer()
            elif(key_input == 2):
                select_TV()
            elif(key_input == 4):
                print("Program Exit!")
                break
            else:
                raise Exception("Invalid input at main menu")
        except Exception as exp:
            print(exp)
            #print("Program Shutdown.")
            #break
            
    
if __name__ == "__main__":
    main()

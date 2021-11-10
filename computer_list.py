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
    cursor.close()
    return ret

def computer_rec_list():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    
    cursor.execute("""
        SELECT CONCAT('A',model) AS name, price, 'D' AS type, cpu, NULL AS feature FROM desktop
        WHERE (
            price <= (SELECT 1.0*AVG(1.0*price) FROM desktop)
        AND
            cpu >= (SELECT 1.0*AVG(1.0*cpu) FROM desktop)
        )
        UNION
        SELECT CONCAT('A',model) AS name, price, 'L' AS type, cpu, weight AS feature FROM laptop
        WHERE (
            price <= (SELECT 1.0*AVG(1.0*price) FROM laptop)
        AND
            cpu >= (SELECT 1.0*AVG(1.0*cpu) FROM laptop)
        )
        UNION
        --B-PC-desktop recommend
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
        WHERE(
            type = 'D' AND
            price <= (SELECT 1.0*AVG(1.0*price) FROM pc WHERE type='D') AND
            cpu >= (SELECT 1.0*AVG(1.0*cpu) FROM pc WHERE type='D') 
        )
        UNION
        --B-PC-laptop recommend
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
        WHERE(
            type = 'L' AND
            price <= (SELECT 1.0*AVG(1.0*price) FROM pc WHERE type='L') AND
            cpu >= (SELECT 1.0*AVG(1.0*cpu) FROM pc WHERE type='L') 
        )
        UNION
        --B-server-recommend
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, 'S' AS type, cpu, NULL AS feature FROM server
        WHERE(
            price <= (SELECT 1.0*AVG(1.0*price) FROM server) AND
            cpu >= (SELECT 1.0*AVG(1.0*cpu) FROM server) 
        )
    """)
    
    connection.commit()
    ret = cursor.fetchall()
    cursor.close()
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
    cursor.close()
    return ret


def tv_rec_list():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()

    cursor.execute("""
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
        ORDER BY name, screen_size, price
    """)
    connection.commit()
    ret = cursor.fetchall()
    cursor.close()
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
    print("List of TV, ordered by name,screen_size, price")
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
                print_TV_list(tv_rec_list())
            elif(key_input == 3):
                print("#3 back to menu")
                break
            else:
                raise Exception("Invalid input at select_TV")
        except Exception as exp:
            print("ERROR: ",exp)

def update_pc_price():
    #https://stackoverflow.com/a/42420331
    #fuck
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    cursor.execute("commit")
    sql_literal = """
    update %s
    set price = price*(0.9)
    where cpu <= (SELECT 1.0*AVG(cpu*1.0)
                    FROM (SELECT cpu FROM pc
                    UNION SELECT cpu FROM server
                    UNION SELECT cpu FROM desktop
                    UNION SELECT cpu from laptop) tmp)
    """
    
    input_sql = (
    'update PC'
    'SET price = price*(0.9)'
    'WHERE cpu <= (SELECT 1.0*AVG(cpu*1.0)'
                    'FROM (SELECT cpu FROM pc'
                    'UNION SELECT cpu FROM server'
                    'UNION SELECT cpu FROM desktop'
                    'UNION SELECT cpu from laptop) tmp)'
    )
    #class_list = ["pc"]
    class_list = ['pc', "server", "desktop", "laptop"]
    for cls in class_list:
        print("try update ", cls)
        #connection = get_connection()
        #cursor = connection.cursor()
        #query = (format_str % class_list[i])
        cursor.execute(sql_literal % cls)
        connection.commit()
    #cursor.close()
    print("Updated pc price")
    #cursor.execute("SELECT * FROM pc")
    #tmp = cursor.fetchall()
    #print_computer_list(tmp)
    print_computer_list(computer_list())
        
def update_tv_price():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    
def update_price():
    update_pc_price()
    #print("PC price updated as")
    #print_computer_list(computer_list())
    update_tv_price()
    print("TV price updated as")
    #print_computer_list(computer_list())

def initial_warnings():
    print("""
          ####################################################################
          WARNING!!!!
          Dear instructors and TAs, please read the following information.
          
          ##1. sqldeveloper setting##
          Before executing this program,
          you must set your sqldevelop setting as below.
          In SqlDeveloper preferences:
            Tools > Preferences > Database > Worksheet,
            check the option for "New Worksheet to use unshared connction"
          
          If not, update will not presume and just hang.
          
          ##2. Initialize DB##
          Please initialize all the DB information
          exactly like the given createschema.sql file.
          
          Please double check before evaluation.
          
          Press Enter if you checked this content. Thank you.
          ####################################################################
          """)
    tmp = input()

def main():
    #print_computer_list(computer_list())
    #print("---------TEST---------")
    #print_computer_list(computer_rec_list())
    #print(return_price_query("ABC"))
    #print(tv_list())
    
    
    #init_db()
    initial_warnings()
    
    print("""
          try connection as below setting:
          
          connection = cx_Oracle.connect(
            user="unist",
            password="admin",
            dsn="localhost:1521"
          )
          
          """)
    connection = get_connection()
    print("connection successful!")
    
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
            elif(key_input == 3):
                update_price()
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

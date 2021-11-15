import cx_Oracle
#import client

###########################
#acquire connection with user, password and dsn
###########################


def get_connection():
    connection = cx_Oracle.connect(
        user="unist",
        password="unist",
        dsn="localhost:1521"
    )
    return connection

###########################
#return all the list of computers
###########################


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

###########################
#return all the recommeneded list of computers,
#print average price and cpu value of both company A and B.
###########################


def computer_rec_list():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()

    a_avgprice_sql = """
    SELECT 1.0*AVG(price*1.0) FROM(
        SELECT price FROM desktop
        UNION SELECT price FROM laptop)
    """
    cursor.execute(a_avgprice_sql)
    a_avgprice = cursor.fetchone()[0]
    print("*average price of A company(laptop,desktop): ", a_avgprice)

    a_avgcpu_sql = """
    SELECT 1.0*AVG(cpu*1.0) FROM(
        SELECT cpu FROM desktop
        UNION SELECT cpu FROM laptop)
    """
    cursor.execute(a_avgcpu_sql)
    a_avgcpu = cursor.fetchone()[0]
    print("*average cpu of A company(laptop,desktop): ", a_avgcpu)

    b_avgprice_sql = """
    SELECT 1.0*AVG(price*1.0) FROM(
        SELECT price FROM pc
        UNION SELECT price FROM server)
    """
    cursor.execute(b_avgprice_sql)
    b_avgprice = cursor.fetchone()[0]
    print("*average price of B company(pc,server): ", b_avgprice)

    b_avgcpu_sql = """
    SELECT 1.0*AVG(cpu*1.0) FROM(
        SELECT cpu FROM pc
        UNION SELECT cpu FROM server)
    """
    cursor.execute(b_avgcpu_sql)
    b_avgcpu = cursor.fetchone()[0]
    print("*average cpu of B company(pc,server): ", b_avgcpu)

    cursor.execute("""
        --desktop recommend
        SELECT CONCAT('A',model) AS name, price, 'D' AS type, cpu, NULL AS feature FROM desktop
        WHERE (
            price <= (SELECT 1.0*AVG(price*1.0) FROM( SELECT price FROM desktop UNION SELECT price FROM laptop))
        AND
            cpu >= (SELECT 1.0*AVG(cpu*1.0) FROM( SELECT cpu FROM desktop UNION SELECT cpu FROM laptop))
        )
        UNION
        --laptop recommend
        SELECT CONCAT('A',model) AS name, price, 'L' AS type, cpu, weight AS feature FROM laptop
        WHERE (
            price <= (SELECT 1.0*AVG(price*1.0) FROM( SELECT price FROM desktop UNION SELECT price FROM laptop))
        AND
            cpu >= (SELECT 1.0*AVG(cpu*1.0) FROM( SELECT cpu FROM desktop UNION SELECT cpu FROM laptop))
        )
        UNION
        --B-PC-desktop recommend
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
        WHERE(
            type = 'D'
            AND
            price <= (SELECT 1.0*AVG(price*1.0) FROM( SELECT price FROM pc UNION SELECT price FROM server))
            AND
            cpu >= (SELECT 1.0*AVG(cpu*1.0) FROM( SELECT cpu FROM pc UNION SELECT cpu FROM server)) 
        )
        UNION
        --B-PC-laptop recommend
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, cpu, NULL AS feature FROM pc
        WHERE(
            type = 'L'
            AND
            price <= (SELECT 1.0*AVG(price*1.0) FROM( SELECT price FROM pc UNION SELECT price FROM server))
            AND
            cpu >= (SELECT 1.0*AVG(cpu*1.0) FROM( SELECT cpu FROM pc UNION SELECT cpu FROM server)) 
        )
        UNION
        --B-server-recommend
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, 'S' AS type, cpu, NULL AS feature FROM server
        WHERE(
            
            price <= (SELECT 1.0*AVG(price*1.0) FROM( SELECT price FROM pc UNION SELECT price FROM server))
            AND
            cpu >= (SELECT 1.0*AVG(cpu*1.0) FROM( SELECT cpu FROM pc UNION SELECT cpu FROM server)) 
        )
    """)

    connection.commit()
    ret = cursor.fetchall()
    cursor.close()
    return ret


###########################
#sql query format string.
#put the price in %s to use it.
###########################
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

###########################
#acquire ty list by price
#try to acquire price input,
#run the return_price_query with the input.
###########################


def tv_list():
    #print("Connection established")
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    search_price = input()
    price_int = int(search_price, 10)
    if(price_int < 0):
        raise Exception("Error at tv price input: input must be positive")
    cursor.execute(return_price_query(search_price))
    connection.commit()
    ret = cursor.fetchall()
    cursor.close()
    return ret


def get_singe_select_value(sql):
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    
    cursor.execute(sql)
    ret = cursor.fetchone()[0]
    
    cursor.close()
    return ret
    
    

###########################
#acquire tv recommend list
#try to acquire price input,
#run the return_price_query with the input.
###########################


def tv_rec_list():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()

    avg_tv_price_sql = """
    SELECT 1.0*AVG(1.0*price)
            FROM( SELECT price FROM tv UNION SELECT price FROM hdtv
                UNION SELECT price FROM pdptv UNION SELECT price FROM lcdtv) pricelist
    """
    avg_tv_screen_sql = """
        SELECT 1.0*AVG(1.0*screen_size)
            FROM( SELECT screen_size FROM tv UNION SELECT screen_size FROM hdtv UNION
                    SELECT screen_size FROM pdptv UNION SELECT screen_size FROM lcdtv) screenlist
    """
    
    max_tv_ratio_above_avg_sql = """
        SELECT MAX((screen_size*1.0)/(price*1.0)) FROM
(SELECT * FROM (
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, screen_size FROM tv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'H' AS type, screen_size FROM hdtv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'P' AS type, screen_size FROM pdptv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'L' AS type, screen_size FROM lcdtv
        )
        WHERE price <= (SELECT 1.0*AVG(1.0*price)
            FROM( SELECT price FROM tv UNION SELECT price FROM hdtv
                UNION SELECT price FROM pdptv UNION SELECT price FROM lcdtv) pricelist)
            AND
            screen_size >= (SELECT 1.0*AVG(1.0*screen_size)
            FROM( SELECT screen_size FROM tv UNION SELECT screen_size FROM hdtv UNION
                    SELECT screen_size FROM pdptv UNION SELECT screen_size FROM lcdtv) screenlist))
    """
    avg_price = get_singe_select_value(avg_tv_price_sql)
    avg_size = get_singe_select_value(avg_tv_screen_sql)
    max_tv_ratio_above_avg = get_singe_select_value(max_tv_ratio_above_avg_sql)

    print('%-20s' % "*avg_price", avg_price)
    print('%-20s' % "*avg_size", avg_size)
    print('%-20s' % "*max_tv_ratio_above_avg", max_tv_ratio_above_avg)
    print("*****")
    print("""max_tv_ratio_above_avg is the maximum size/price ratio of the tvs \nthose match price <= avg_price AND size >= avg_size""")
    print("*****")
    
    new_rec_sql = """
    SELECT * FROM (
SELECT * FROM (
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, screen_size FROM tv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'H' AS type, screen_size FROM hdtv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'P' AS type, screen_size FROM pdptv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'L' AS type, screen_size FROM lcdtv
        )
        WHERE price <= (SELECT 1.0*AVG(1.0*price)
            FROM( SELECT price FROM tv UNION SELECT price FROM hdtv
                UNION SELECT price FROM pdptv UNION SELECT price FROM lcdtv) pricelist)
            AND
            screen_size >= (SELECT 1.0*AVG(1.0*screen_size)
            FROM( SELECT screen_size FROM tv UNION SELECT screen_size FROM hdtv UNION
                    SELECT screen_size FROM pdptv UNION SELECT screen_size FROM lcdtv) screenlist)
        ORDER BY name, screen_size, price) aboveavg
WHERE 
(screen_size*1.0)/(price*1.0) = (SELECT MAX((screen_size*1.0)/(price*1.0)) FROM
(SELECT * FROM (
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, screen_size FROM tv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'H' AS type, screen_size FROM hdtv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'P' AS type, screen_size FROM pdptv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'L' AS type, screen_size FROM lcdtv
        )
        WHERE price <= (SELECT 1.0*AVG(1.0*price)
            FROM( SELECT price FROM tv UNION SELECT price FROM hdtv
                UNION SELECT price FROM pdptv UNION SELECT price FROM lcdtv) pricelist)
            AND
            screen_size >= (SELECT 1.0*AVG(1.0*screen_size)
            FROM( SELECT screen_size FROM tv UNION SELECT screen_size FROM hdtv UNION
                    SELECT screen_size FROM pdptv UNION SELECT screen_size FROM lcdtv) screenlist))
    )
   
    """
    
    cursor.execute(new_rec_sql)
    connection.commit()
    ret = cursor.fetchall()
    cursor.close()
    return ret

###########
old_rec_sql = """
--tv2
        SELECT * FROM (
        SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, screen_size FROM tv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'H' AS type, screen_size FROM hdtv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'P' AS type, screen_size FROM pdptv
        UNION
        SELECT CONCAT('A',model) AS name, price, 'L' AS type, screen_size FROM lcdtv
           
        )
        WHERE price <= (SELECT 1.0*AVG(1.0*price)
            FROM( SELECT price FROM tv UNION SELECT price FROM hdtv
                UNION SELECT price FROM pdptv UNION SELECT price FROM lcdtv) pricelist)
            AND
            screen_size >= (SELECT 1.0*AVG(1.0*screen_size)
            FROM( SELECT screen_size FROM tv UNION SELECT screen_size FROM hdtv UNION
                    SELECT screen_size FROM pdptv UNION SELECT screen_size FROM lcdtv) screenlist)
            AND
            ((1.0*screen_size)/(1.0*price)) = (SELECT MAX((1.0*screen_size)/(1.0*price))
            FROM( SELECT screen_size,price FROM tv UNION SELECT screen_size,price FROM hdtv UNION
                    SELECT screen_size,price FROM pdptv UNION SELECT screen_size,price FROM lcdtv) ratiolist)   
        ORDER BY name, screen_size, price
"""

###########################
#print the computers in the following format
#given tmp as the list of computers
###########################
def print_computer_list(tmp):
    #tmp = computer_list()
    length = len(tmp)
    print("""
          ----------------------------------------
          List of computer, ordered by type, name
          ----------------------------------------
    """)
    print('%-8s' % "name", '%-8s' % "price",
          '%-8s' % "type", '%-8s' % "cpu", '%-8s' % "feature")
    for i in range(length):
        print('%-8s' % tmp[i][0], '%-8s' % tmp[i][1],
              '%-8s' % tmp[i][2], '%-8s' % tmp[i][3], '%-8s' % tmp[i][4])

###########################
#print the tvs in the following format
#given tmp as the list of tvs
###########################


def print_TV_list(tmp):
    #tmp = computer_list()
    length = len(tmp)
    print("""
          ----------------------------------------------
          List of TV, ordered by name,screen_size, price
          ----------------------------------------------
    """)
    print('%-8s' % "name", '%-8s' % "price",
          '%-8s' % "type", '%-10s' % "screensize")
    for i in range(length):
        print('%-8s' % tmp[i][0], '%-8s' % tmp[i][1],
              '%-8s' % tmp[i][2], '%-10s' % tmp[i][3])

###########################
#this menu is called
#when you select 1 in the main menu.
###########################


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

###########################
#this menu is called
#when you select 2 in the main menu.
###########################


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
            print("ERROR: ", exp)

###########################
#update only pc prices
###########################


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

    class_list = ['pc', "server", "desktop", "laptop"]
    for cls in class_list:
        print("try update ", cls)
        cursor.execute(sql_literal % cls)
        connection.commit()

    print("Updated pc price")
    #print_computer_list(computer_list())

###########################
#delete only pc prices
###########################


def delete_pc_price():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    max_sql = """
    SELECT MAX(price)
                    FROM (SELECT price FROM pc
                    UNION SELECT price FROM server
                    UNION SELECT price FROM desktop
                    UNION SELECT price from laptop)
    """
    cursor.execute(max_sql)
    maxi = cursor.fetchone()[0]
    print("Max Price: ", maxi)

    class_list = ['pc', "server", "desktop", "laptop"]
    sql_literal = "DELETE FROM %s WHERE price = %i"
    for cls in class_list:
        print("try delete ", cls)
        cursor.execute(sql_literal % (cls, maxi))
        connection.commit()

    print("Deleted max pc price")
    #print_computer_list(computer_list())

###########################
#custom list of all tvs
###########################


def all_tv_list():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()
    sql_literal = """
        SELECT * FROM (
    SELECT CONCAT(CONCAT('B',model),code) AS name, price, type, screen_size FROM tv
    UNION
    SELECT CONCAT('A',model) AS name, price, 'H' AS type, screen_size FROM hdtv
    UNION
    SELECT CONCAT('A',model) AS name, price, 'P' AS type, screen_size FROM pdptv
    UNION
    SELECT CONCAT('A',model) AS name, price, 'L' AS type, screen_size FROM lcdtv
    ORDER BY type,name)
    """

    cursor.execute(sql_literal)
    ret = cursor.fetchall()
    return ret


###########################
#update price of all tvs
###########################
def update_tv_price():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()

    connection.commit()
    cursor.execute("commit")

    format_str = """
    UPDATE %s SET price = price*(1.1)
    WHERE screen_size = (SELECT MAX(screen_size)
                    FROM (SELECT screen_size FROM tv
                    UNION SELECT screen_size FROM hdtv
                    UNION SELECT screen_size FROM pdptv
                    UNION SELECT screen_size from lcdtv))
    """
    class_list = ["tv", "hdtv", "pdptv", "lcdtv"]
    for cls in class_list:
        print("try update ", cls)
        cursor.execute(format_str % cls)
        connection.commit()

    print("Updated tv price")

###########################
#delete price of all tvs those match the condition.
#print out which tvs are deleted
###########################


def delete_tv_price():
    connection = get_connection()
    cursor = connection.cursor()
    connection.commit()

    cursor.execute("""
                   SELECT MAX((1.0*screen_size)/(1.0*price))
                FROM( SELECT screen_size,price FROM tv
                UNION SELECT screen_size,price FROM hdtv
                UNION SELECT screen_size,price FROM pdptv
                UNION SELECT screen_size,price FROM lcdtv)
                   """)
    maxi = cursor.fetchone()[0]

    format_str = """
        DELETE FROM %s
        WHERE (screen_size*1.0)/(price*1.0) = %f
    """
    connection.commit()
    all_list = all_tv_list()
    for tv in all_list:
        if((tv[3]*1.0)/(tv[1]*1.0) == maxi):
            print("match TV: ", tv[0])

    class_list = ["tv", "hdtv", "pdptv", "lcdtv"]
    for cls in class_list:
        print("try delete ", cls)
        cursor.execute(format_str % (cls, maxi))
        connection.commit()

    print("deleted tv price")


###########################
#this menu is called
#when you select 3 in the main menu.
###########################
def update_price():
    update_pc_price()
    delete_pc_price()
    print("PC price updated as")
    print_computer_list(computer_list())
    update_tv_price()
    delete_tv_price()
    print("TV price updated as")
    print_TV_list(all_tv_list())

#initial booting message


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
            (한국어: "도구>환경설정>워크시트>공유되지 않은 접속을 사용할 새 워크시트)
          
          If not, update may not presume and just hang, due to oracle bug.
          (Refer to https://stackoverflow.com/a/42420331)
          
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
            password="unist",
            dsn="localhost:1521"
          )
          
          !!!Check the user/password is conenction fails!!!
          
          """)
    connection = get_connection()
    print("""connection successful!""")

    #does not terminate for invalid inputs,
    #just fall back to original menu.
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
                print("""Program Exit!""")
                break
            else:
                raise Exception("Invalid input at main menu")
        except Exception as exp:
            print(exp)
            #print("Program Shutdown.")
            #break


if __name__ == "__main__":
    main()

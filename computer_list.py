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



def main():
    #print_computer_list(computer_list())
    #print("---------TEST---------")
    #print_computer_list(computer_rec_list())
    #print(return_price_query("ABC"))
    #print(tv_list())
    
    
    #init_db()
    
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


def init_db():
    init_sql = """
    --init DB
    --DROP TABLE desktop
    --DROP TABLE hdtv
    --DROP TABLE laptop
    --DROP TABLE lcdtv
    --DROP TABLE new_server
    --DROP TABLE pc
    --DROP TABLE pdptv
    --DROP TABLE tv
    --create DB
    create table desktop (

    model	varchar2(20)	not null,

    price 	integer		not null,

    cpu	integer 	not null,

    primary key (model)

    )



    create table laptop (

    model	varchar2(20)	not null,

    price	integer 	not null,

    cpu	integer		not null,

    weight	integer		not null,

    primary key (model)

    )



    create table hdtv (

    model		varchar2(20)	not null,

    price		integer 	not null,

    screen_size	integer		not null,

    primary key (model)

    )

    create table pdptv (

    model		varchar2(20)	not null,

    price		integer 	not null,

    screen_size	integer		not null,

    primary key (model)

    )

    create table lcdtv (

    model		varchar2(20)	not null,

    price		integer 	not null,

    screen_size	integer		not null,

    primary key (model)

    )

    create table pc (

    model	varchar2(10)	not null,
    code	varchar2(10)	not null,
    type	varchar2(10) 	not null,

    price	integer 	not null,
    cpu	integer 	not null,

    primary key (model, code)

    )

    create table server (

    model	varchar2(10)	not null,
    code	varchar2(10)	not null,
    price	integer 	not null,
    cpu	integer 	not null,

    primary key (model, code)

    )


    create table tv (

    model		varchar2(10)	not null,
    code		varchar2(10)	not null,
    type		varchar2(10) 	not null,
    price		integer 	not null,
    screen_size	integer 	not null,

    primary key (model, code)

    )


    --commit



    insert into desktop values ('D101', 100, 300)
    insert into desktop values ('D102', 50, 100)
    insert into desktop values ('D103', 400, 700)
    insert into desktop values ('D104', 200, 600)
    insert into desktop values ('D105', 80, 200)
    insert into desktop values ('D106', 70, 210)
    insert into desktop values ('D107', 200, 280)
    insert into desktop values ('D108', 200, 310)
    insert into desktop values ('D109', 40, 80)
    insert into desktop values ('D110', 100, 320)
    insert into desktop values ('D111', 90, 380)
    insert into desktop values ('D112', 110, 300)



    --commit



    insert into laptop values ('L201', 200, 300, 800)
    insert into laptop values ('L202', 120, 180, 600)
    insert into laptop values ('L203', 240, 320, 1000)
    insert into laptop values ('L204', 340, 400, 900)
    insert into laptop values ('L205', 500, 600, 600)
    insert into laptop values ('L206', 400, 400, 800)
    insert into laptop values ('L207', 270, 330, 600)
    insert into laptop values ('L208', 180, 200, 700)
    insert into laptop values ('L209', 250, 250, 500)



    --commit



    insert into hdtv values ('H301', 500, 500)
    insert into hdtv values ('H302', 600, 700)
    insert into hdtv values ('H303', 400, 480)
    insert into hdtv values ('H304', 400, 460)
    insert into hdtv values ('H305', 500, 530)
    insert into hdtv values ('H306', 530, 500)
    insert into hdtv values ('H307', 600, 670)
    insert into hdtv values ('H308', 400, 300)
    insert into hdtv values ('H309', 300, 280)

    --commit



    insert into pdptv values ('P401', 370, 510)
    insert into pdptv values ('P402', 340, 500)
    insert into pdptv values ('P403', 280, 400)
    insert into pdptv values ('P404', 450, 570)
    insert into pdptv values ('P405', 400, 550)
    insert into pdptv values ('P406', 500, 610)
    insert into pdptv values ('P407', 520, 630)
    insert into pdptv values ('P408', 470, 540)
    insert into pdptv values ('P409', 260, 410)

    --commit

    insert into lcdtv values ('T501', 700, 500)
    insert into lcdtv values ('T502', 760, 530)
    insert into lcdtv values ('T503', 780, 540)
    insert into lcdtv values ('T504', 580, 400)
    insert into lcdtv values ('T505', 500, 320)
    insert into lcdtv values ('T506', 650, 480)
    insert into lcdtv values ('T507', 680, 490)
    insert into lcdtv values ('T508', 800, 570)
    insert into lcdtv values ('T509', 780, 560)
    insert into lcdtv values ('T510', 630, 450)

    --commit

    insert into pc values ('D101', 'z', 'D', 100, 300)
    insert into pc values ('P101', 'a', 'D', 110, 300)
    insert into pc values ('P102', 'b', 'D', 120, 310)
    insert into pc values ('P103', 'c', 'D', 150, 320)
    insert into pc values ('P104', 'd', 'D', 200, 400)
    insert into pc values ('P105', 'e', 'D', 240, 410)
    insert into pc values ('P106', 'f', 'D', 180, 340)
    insert into pc values ('P107', 'g', 'D', 80, 250)
    insert into pc values ('P108', 'h', 'D', 70, 200)
    insert into pc values ('P109', 'i', 'D', 300, 480)
    insert into pc values ('L101', 'j', 'L', 190, 300)
    insert into pc values ('L102', 'k', 'L', 200, 320)
    insert into pc values ('L103', 'l', 'L', 250, 340)
    insert into pc values ('L104', 'm', 'L', 300, 380)
    insert into pc values ('L105', 'n', 'L', 320, 400)
    insert into pc values ('L106', 'o', 'L', 170, 280)
    insert into pc values ('L107', 'p', 'L', 400, 500)
    insert into pc values ('L108', 'q', 'L', 360, 420)
    insert into pc values ('L109', 'r', 'L', 120, 250)

    --commit

    insert into server values ('S101', 'a', 400, 460)
    insert into server values ('S102', 'b', 500, 700)
    insert into server values ('S103', 'c', 450, 520)
    insert into server values ('S104', 'd', 300, 380)
    insert into server values ('S105', 'e', 320, 390)
    insert into server values ('S106', 'f', 370, 400)
    insert into server values ('S107', 'g', 210, 280)
    insert into server values ('S108', 'h', 410, 480)

    --commit

    insert into tv values ('H101', 'a', 'H', 500, 500)
    insert into tv values ('H102', 'b', 'H', 400, 340)
    insert into tv values ('H103', 'c', 'H', 510, 510)
    insert into tv values ('H104', 'd', 'H', 450, 400)
    insert into tv values ('H105', 'e', 'H', 470, 430)
    insert into tv values ('H106', 'f', 'H', 600, 590)
    insert into tv values ('H107', 'g', 'H', 300, 200)
    insert into tv values ('P101', 'h', 'P', 380, 500)
    insert into tv values ('P102', 'i', 'P', 310, 440)
    insert into tv values ('P103', 'j', 'P', 340, 470)
    insert into tv values ('P104', 'k', 'P', 290, 400)
    insert into tv values ('P105', 'l', 'P', 400, 540)
    insert into tv values ('P106', 'm', 'P', 600, 700)
    insert into tv values ('T101', 'n', 'L', 700, 550)
    insert into tv values ('T102', 'o', 'L', 740, 560)
    insert into tv values ('T103', 'p', 'L', 560, 390)
    insert into tv values ('T104', 'q', 'L', 610, 430)
    insert into tv values ('T105', 'r', 'L', 760, 580)
    insert into tv values ('T106', 's', 'L', 500, 350)
    insert into tv values ('T107', 's', 'L', 510, 350)

    --commit
    """
    connection = get_connection()
    cursor = connection.cursor()
    #connection.commit()
    #sql_commands = init_sql.split('')
    #for sql_command in sql_commands:
    #    cursor.execute(sql_command)
    connection.commit()
    cursor.execute(init_sql)
    print("init success!")
    
    
    
if __name__ == "__main__":
    main()

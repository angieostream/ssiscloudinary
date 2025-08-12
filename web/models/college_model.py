from flask_mysqldb import MySQL

mysql = MySQL()

def get_colleges():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM colleges")
    colleges = cur.fetchall()
    cur.close()
    return colleges

def insert_college(code, name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM colleges WHERE code=%s", (code,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        return False
    cur.execute("INSERT INTO colleges (code, name) VALUES (%s, %s)", (code, name))
    mysql.connection.commit()
    cur.close()
    return True

def update_college(old_code, new_code, name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM colleges WHERE code = %s AND code != %s", (new_code, old_code))
    exists = cur.fetchone()
    if exists:
        cur.close()
        return False
    cur.execute("UPDATE colleges SET name=%s, code=%s WHERE code=%s", (name, new_code, old_code))
    mysql.connection.commit()
    cur.close()
    return True

def delete_college(code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM colleges WHERE code=%s", (code,))
    mysql.connection.commit()
    cur.close()

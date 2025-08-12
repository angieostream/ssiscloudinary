from flask_mysqldb import MySQL

mysql = MySQL()

def get_programs_all():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM programs")
    programs = cur.fetchall()

    cur.execute("SELECT code, name FROM colleges")
    colleges = cur.fetchall()
    cur.close()
    return programs, colleges

def get_programs_by_college(college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM programs WHERE college_code = %s", (college_code,))
    programs = cur.fetchall()
    cur.close()
    return programs

def insert_program(code, name, college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM programs WHERE code = %s", (code,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        return False
    cur.execute("SELECT * FROM colleges WHERE code = %s", (college_code,))
    college = cur.fetchone()
    if not college:
        cur.close()
        return None  # college code invalid
    cur.execute("INSERT INTO programs (code, name, college_code) VALUES (%s, %s, %s)", (code, name, college_code))
    mysql.connection.commit()
    cur.close()
    return True

def update_program(old_code, new_code, name, college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM programs WHERE code = %s AND code != %s", (new_code, old_code))
    exists = cur.fetchone()
    if exists:
        cur.close()
        return False
    cur.execute("UPDATE programs SET name=%s, college_code=%s, code=%s WHERE code=%s", (name, college_code, new_code, old_code))
    mysql.connection.commit()
    cur.close()
    return True

def delete_program(code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM programs WHERE code=%s", (code,))
    mysql.connection.commit()
    cur.close()

def add_program_to_college(name, college_code):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO programs (name, college_code) VALUES (%s, %s)", (name, college_code))
    mysql.connection.commit()
    cur.close()

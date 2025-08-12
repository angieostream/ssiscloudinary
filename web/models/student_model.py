from flask_mysqldb import MySQL

mysql = MySQL()  # will be initialized in app factory, same instance used everywhere

def get_programs():
    cur = mysql.connection.cursor()
    cur.execute('SELECT code, name FROM programs')
    programs = cur.fetchall()
    cur.close()
    return programs

def get_students_paginated(offset=0, limit=10):
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM students')
    total_students = cur.fetchone()[0]

    cur.execute(
        'SELECT image_url, id, firstname, lastname, course, year, gender '
        'FROM students LIMIT %s OFFSET %s',
        (limit, offset)
    )
    students = cur.fetchall()
    cur.close()
    return students, total_students

def create_student(id, firstname, lastname, course, year, gender, image_url):
    cur = mysql.connection.cursor()

    # Check if a student with the same ID already exists
    cur.execute("SELECT * FROM students WHERE id=%s", (id,))
    existing_student = cur.fetchone()

    if existing_student:
        cur.close()
        return False

    query = '''
        INSERT INTO students (id, firstname, lastname, course, year, gender, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    '''
    try:
        cur.execute(query, (id, firstname, lastname, course, year, gender, image_url))  
        mysql.connection.commit()
    except Exception as e:
        print(f"Error inserting student: {e}")  
    finally:
        cur.close()
    
    return True

def get_students():
    cur = mysql.connection.cursor()
    cur.execute('SELECT image_url, id, firstname, lastname, course, year, gender FROM students')
    students = cur.fetchall()
    cur.close()
    return students

def delete_student(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
    mysql.connection.commit()
    cur.close()

def update_student(student_id, firstname, lastname, course, year, gender, image_url):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE students SET 
        firstname = %s, lastname = %s, course = %s, year = %s, gender = %s, image_url = %s
        WHERE id = %s
    """, (firstname, lastname, course, year, gender, image_url, student_id))
    
    mysql.connection.commit()
    cursor.close()

from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mysqldb import MySQL
import cloudinary.uploader

views = Blueprint('views', __name__)
mysql = MySQL()

@views.route('/')
def home():
    students_list = get_students()  
    programs = get_programs()           

    per_page = 10  # Pagination limit
    total_students = len(students_list)  
    total_pages = (total_students + per_page - 1) // per_page  

    return render_template(
        'students.html',
        student=students_list,
        programs=programs,
        current_page=1,  
        total_pages=total_pages
    )


# Students routes
def get_programs():
    cur = mysql.connection.cursor()
    cur.execute('SELECT code, name FROM programs')
    programs = cur.fetchall()
    cur.close()
    return programs

@views.route('/students', methods=['GET', 'POST'])
def students():
    course_filter = request.args.get('course', '')
    year_filter = request.args.get('year', '')
    gender_filter = request.args.get('gender', '')

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    query = 'SELECT image_url, id, firstname, lastname, course, year, gender FROM students WHERE 1=1'
    filters = []

    if course_filter:
        query += " AND course = %s"
        filters.append(course_filter)

    if year_filter:
        query += " AND year = %s"
        filters.append(year_filter)

    if gender_filter:
        query += " AND gender = %s"
        filters.append(gender_filter)

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(filters))
    total_students = cur.fetchall()

    query += " LIMIT %s OFFSET %s"
    filters.extend([per_page, offset])

    # Get filtered students list
    cur.execute(query, tuple(filters))
    students_list = cur.fetchall()
    cur.close()

    total_pages = (len(total_students) + per_page - 1) // per_page
    programs = get_programs()

    return render_template(
        'students.html',
        student=students_list,
        programs=programs,
        current_page=page,
        total_pages=total_pages
    )


def get_students_paginated(course_filter='', year_filter='', gender_filter='', offset=0, limit=10):
    query = 'SELECT image_url, id, firstname, lastname, course, year, gender FROM students WHERE 1=1'
    filters = []

    if course_filter:
        query += " AND course = %s"
        filters.append(course_filter)

    if year_filter:
        query += " AND year = %s"
        filters.append(year_filter)

    if gender_filter:
        query += " AND gender = %s"
        filters.append(gender_filter)

    query += " LIMIT %s OFFSET %s"
    filters.extend([limit, offset])

    cur = mysql.connection.cursor()
    cur.execute(query, tuple(filters))
    students = cur.fetchall()
    cur.close()

    return students, len(students)


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
        print("Student record inserted successfully!")  
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

@views.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
    mysql.connection.commit()
    flash("Student Record Has Been Deleted Successfully", "success")
    return redirect(url_for('views.students'))

from cloudinary.uploader import upload as cloudinary_upload

@views.route('/update', methods=['POST'])
def update():
    student_id = request.form['id']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    course = request.form['course']
    year = request.form['year']
    gender = request.form['gender']
    current_image_url = request.form['current_image_url']
    
    new_image_url = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file:
            upload_result = cloudinary_upload(file)
            new_image_url = upload_result['url']  #
            
    if not new_image_url:
        new_image_url = current_image_url

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE students SET 
        firstname = %s, lastname = %s, course = %s, year = %s, gender = %s, image_url = %s
        WHERE id = %s
    """, (firstname, lastname, course, year, gender, new_image_url, student_id))
    
    mysql.connection.commit()
    cursor.close()
    
    flash('Student updated successfully!', 'success')
    return redirect(url_for('views.students'))  



# Colleges routes
@views.route('/colleges', methods=['GET', 'POST'])
def colleges():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        college_code = request.form['college_code']  
        college_name = request.form['college_name']
        
        if not college_code or not college_name:
            flash("Both College Code and Name are required", "danger")
            return redirect(url_for('views.colleges'))
        
        cur.execute("SELECT * FROM colleges WHERE code=%s", (college_code,))  
        existing_college = cur.fetchone()
        
        if existing_college:
            flash("College Code already exists. Please use a different code.", "danger")
            return redirect(url_for('views.colleges'))

        cur.execute("INSERT INTO colleges (code, name) VALUES (%s, %s)", (college_code, college_name))  
        mysql.connection.commit()
        flash("College Added Successfully", "success")

    cur.execute("SELECT * FROM colleges")  
    colleges_data = cur.fetchall()
    cur.close()
    return render_template('colleges.html', colleges=colleges_data)

@views.route('/update_college/<string:college_code>', methods=['POST'])
def update_college(college_code):
    if request.method == 'POST':
        college_name = request.form['college_name']
        
        cur = mysql.connection.cursor()
        cur.execute("UPDATE colleges SET name=%s WHERE code=%s", (college_name, college_code))  
        mysql.connection.commit()
        flash("College Updated Successfully", "success")
        return redirect(url_for('views.colleges'))

@views.route('/delete_college/<string:college_code>', methods=['GET'])
def delete_college(college_code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM colleges WHERE code=%s", (college_code,))  
    mysql.connection.commit()
    flash("College Deleted Successfully", "success")
    return redirect(url_for('views.colleges'))

# View programs
@views.route('/programs', methods=['GET'])
def programs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM programs")
    programs_data = cur.fetchall()

    cur.execute("SELECT code, name FROM colleges")
    colleges_data = cur.fetchall()

    cur.close()
    return render_template('programs.html', programs=programs_data, colleges=colleges_data)


@views.route('/view_programs/<string:college_code>', methods=['GET'])
def view_programs(college_code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM programs WHERE college_code = %s", (college_code,))
    programs_data = cur.fetchall()
    cur.close()
    return render_template('view_programs.html', programs=programs_data, college_code=college_code)

@views.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        college_code = request.form['college_code']
        
        if not code or not name or not college_code:
            flash("All fields are required!", "danger")
            return redirect(url_for('views.programs'))
        
        cur = mysql.connection.cursor()
        
        cur.execute("SELECT * FROM programs WHERE code = %s", (code,))
        existing_program = cur.fetchone()
        
        if existing_program:
            flash("Program code already exists. Please use a different code.", "danger")
            return redirect(url_for('views.programs'))

        cur.execute("SELECT * FROM colleges WHERE code = %s", (college_code,))
        college = cur.fetchone()
        
        if not college:
            flash(f'College code {college_code} does not exist. Please choose a valid college.', 'danger')
            return redirect(url_for('views.programs'))
        
        cur.execute("INSERT INTO programs (code, name, college_code) VALUES (%s, %s, %s)", (code, name, college_code))
        mysql.connection.commit()
        cur.close()
        
        flash("Program added successfully!", "success")
        return redirect(url_for('views.programs'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM programs")
    programs_data = cur.fetchall()
    cur.close()
    
    return render_template('programs.html', programs=programs_data)


@views.route('/update_program/<string:program_code>', methods=['POST'])
def update_program(program_code):
    if request.method == 'POST':
        name = request.form['name']
        college_code = request.form['college_code']

        cur = mysql.connection.cursor()
        cur.execute("UPDATE programs SET name=%s, college_code=%s WHERE code=%s", (name, college_code, program_code))
        mysql.connection.commit()
        flash("Program updated successfully!", "success")
        return redirect(url_for('views.programs'))


@views.route('/delete_program/<string:program_code>', methods=['GET'])
def delete_program(program_code):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM programs WHERE code=%s", (program_code,))
    mysql.connection.commit()
    flash("Program Deleted Successfully", "success")
    return redirect(url_for('views.programs'))


@views.route('/add_update_program/<string:college_code>', methods=['POST'])
def add_update_program(college_code):
    if request.method == 'POST':
        program_name = request.form['program_name']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO programs (name, college_code) VALUES (%s, %s)", (program_name, college_code))
        mysql.connection.commit()
        flash("Program Added Successfully")
        return redirect(url_for('views.view_programs', college_code=college_code))

# Search 
@views.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    category = request.args.get('search_type', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    if not query and not category:
        return redirect(url_for('views.students', page=page))

    try:
        cur = mysql.connection.cursor()
        if category == 'students':
            # If the query is a single digit, search only by 'year' 
            if query.isdigit() and len(query) == 1:  # Check if it's a single-digit query
                cur.execute(
                    "SELECT COUNT(*) FROM students WHERE year = %s",
                    (query,)
                )
            else:  
                cur.execute(
                    "SELECT COUNT(*) FROM students WHERE "
                    "firstname LIKE %s OR lastname LIKE %s OR course LIKE %s OR year LIKE %s OR gender = %s",
                    tuple('%' + query + '%' for _ in range(4)) + (query,)
                )

            total_results = cur.fetchone()[0]

            if query.isdigit() and len(query) == 1:
                cur.execute(
                    "SELECT image_url, id, firstname, lastname, course, year, gender FROM students WHERE year = %s LIMIT %s OFFSET %s",
                    (query, per_page, offset)
                )
            else:
                cur.execute(
                    "SELECT image_url, id, firstname, lastname, course, year, gender FROM students WHERE "
                    "firstname LIKE %s OR lastname LIKE %s OR course LIKE %s OR year LIKE %s OR gender = %s "
                    "LIMIT %s OFFSET %s",
                    tuple('%' + query + '%' for _ in range(4)) + (query, per_page, offset)
                )
            results = cur.fetchall()
            cur.close()

            total_pages = (total_results + per_page - 1) // per_page
            if not results and page == 1:
                flash(f"No Student Record found for '{query}'.", "danger")


            return render_template(
                'students.html',
                student=results,
                programs=get_programs(),
                search_query=query,
                current_page=page,
                total_pages=total_pages
            )

        elif category == 'programs':
            cur.execute(
                "SELECT COUNT(*) FROM programs WHERE "
                "code LIKE %s OR name LIKE %s OR college_code LIKE %s",
                tuple('%' + query + '%' for _ in range(3))
            )
            total_results = cur.fetchone()[0]

            cur.execute(
                "SELECT * FROM programs WHERE "
                "code LIKE %s OR name LIKE %s OR college_code LIKE %s "
                "LIMIT %s OFFSET %s",
                tuple('%' + query + '%' for _ in range(3)) + (per_page, offset)
            )
            results = cur.fetchall()
            cur.close()

            total_pages = (total_results + per_page - 1) // per_page
            if not results and page == 1:
                flash(f"No Program Record found for '{query}'.", "danger")
            return render_template(
                'programs.html',
                programs=results,
                search_query=query,
                current_page=page,
                total_pages=total_pages
            )

        elif category == 'colleges':
            cur.execute(
                "SELECT COUNT(*) FROM colleges WHERE "
                "code LIKE %s OR name LIKE %s",
                tuple('%' + query + '%' for _ in range(2))
            )
            total_results = cur.fetchone()[0]

            cur.execute(
                "SELECT * FROM colleges WHERE "
                "code LIKE %s OR name LIKE %s "
                "LIMIT %s OFFSET %s",
                tuple('%' + query + '%' for _ in range(2)) + (per_page, offset)
            )
            results = cur.fetchall()
            cur.close()

            total_pages = (total_results + per_page - 1) // per_page
            if not results and page == 1:
                flash(f"No College Record found for '{query}'.", "danger")
            return render_template(
                'colleges.html',
                colleges=results,
                search_query=query,
                current_page=page,
                total_pages=total_pages
            )

    except Exception as e:
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for('views.students'))

    flash("No results found.", "info")
    return redirect(url_for('views.students'))



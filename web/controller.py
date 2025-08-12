from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mysqldb import MySQL
import cloudinary.uploader

views = Blueprint('views', __name__)
mysql = MySQL()

# Students routes
def get_programs():
    cur = mysql.connection.cursor()
    cur.execute('SELECT code, name FROM programs')
    programs = cur.fetchall()
    cur.close()
    return programs

@views.route("/", methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        id = request.form['id']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        course = request.form['course']
        year = request.form['year']
        gender = request.form['gender']
        image_url = request.form.get('image_url')  # <-- get URL from hidden input

        # Basic validation
        if not (id and firstname and lastname and course and year and gender):
            flash('All fields are required!', 'danger')
            return redirect(url_for('views.students'))

        # validate image_url is a valid URL or empty
        if image_url:
            from urllib.parse import urlparse
            try:
                result = urlparse(image_url)
                if not all([result.scheme, result.netloc]):
                    flash('Invalid image URL.', 'danger')
                    return redirect(url_for('views.students'))
            except Exception:
                flash('Invalid image URL.', 'danger')
                return redirect(url_for('views.students'))
        else:
            image_url = None 

        if create_student(id, firstname, lastname, course, year, gender, image_url):
            flash('Student added successfully!', 'success')
            return redirect(url_for('views.students'))
        else:
            flash('ID number already exists. Please use a different ID number.', 'danger')

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    students_list, total_students = get_students_paginated(offset, per_page)
    total_pages = (total_students + per_page - 1) // per_page
    programs = get_programs()

    return render_template(
        'students.html',
        student=students_list,
        programs=programs,
        current_page=page, 
        total_pages=total_pages,
        offset=offset,
        per_page=per_page
    )


def get_students_paginated(offset=0, limit=10):
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) FROM students')
    total_students = cur.fetchone()[0]

    cur.execute('''
        SELECT 
            s.image_url, s.id, s.firstname, s.lastname, s.course, s.year, s.gender,
            COALESCE(c.name, '') AS college_name
        FROM students s
        LEFT JOIN programs p ON s.course = p.code
        LEFT JOIN colleges c ON p.college_code = c.code
        LIMIT %s OFFSET %s
    ''', (limit, offset))
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

@views.route('/update', methods=['POST'])
def update():
    student_id = request.form['id']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    course = request.form['course']
    year = request.form['year']
    gender = request.form['gender']
    current_image_url = request.form.get('current_image_url', None)
    new_image_url = request.form.get('image_url') or current_image_url  # from hidden input or fallback

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
    
    # Handle POST (add college)
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

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # Get total count for pagination
    cur.execute("SELECT COUNT(*) FROM colleges")
    total_colleges = cur.fetchone()[0]

    # Get colleges with limit & offset
    cur.execute("SELECT * FROM colleges LIMIT %s OFFSET %s", (per_page, offset))
    colleges_data = cur.fetchall()

    total_pages = (total_colleges + per_page - 1) // per_page
    
    cur.close()
    return render_template(
        'colleges.html',
        colleges=colleges_data,
        current_page=page,
        total_pages=total_pages,
        per_page=per_page
    )


@views.route('/update_college/<string:college_code>', methods=['POST'])
def update_college(college_code):
    if request.method == 'POST':
        college_name = request.form['college_name']
        
        cur = mysql.connection.cursor()
        
        new_college_code = request.form['college_code']
        cur.execute("SELECT * FROM colleges WHERE code = %s AND code != %s", (new_college_code, college_code))
        existing_college = cur.fetchone()
        
        if existing_college:
            flash("College code already exists. Please use a different code.", "danger")
            return redirect(url_for('views.colleges'))

        cur.execute("UPDATE colleges SET name=%s, code=%s WHERE code=%s", (college_name, new_college_code, college_code))
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
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10
    offset = (page - 1) * per_page

    # Get total count for pagination
    cur.execute("SELECT COUNT(*) FROM programs")
    total_programs = cur.fetchone()[0]

    # Get programs with limit & offset
    cur.execute("SELECT * FROM programs LIMIT %s OFFSET %s", (per_page, offset))
    programs_data = cur.fetchall()

    # Also get all colleges for dropdowns etc.
    cur.execute("SELECT code, name FROM colleges")
    colleges_data = cur.fetchall()

    total_pages = (total_programs + per_page - 1) // per_page
    
    cur.close()
    return render_template(
        'programs.html',
        programs=programs_data,
        colleges=colleges_data,
        current_page=page,
        total_pages=total_pages,
        per_page=per_page
    )


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
        new_program_code = request.form['code'] 

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM programs WHERE code = %s AND code != %s", (new_program_code, program_code))
        existing_program = cur.fetchone()

        if existing_program:
            flash("Program code already exists. Please use a different code.", "danger")
            return redirect(url_for('views.programs'))

        cur.execute("UPDATE programs SET name=%s, college_code=%s, code=%s WHERE code=%s", (name, college_code, new_program_code, program_code))
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

    if not query or not category:
        return redirect(url_for('views.students', page=page))

    try:
        cur = mysql.connection.cursor()

        if category == 'students' and query.isdigit() and query in ['1', '2', '3', '4']:
            # If query is a single digit year (1-4), search only by year
            cur.execute(
                "SELECT COUNT(*) FROM students WHERE year = %s", (query,)
            )
            total_results = cur.fetchone()[0]

            cur.execute(
                "SELECT image_url, id, firstname, lastname, course, year, gender FROM students WHERE year = %s LIMIT %s OFFSET %s",
                (query, per_page, offset)
            )
            results = cur.fetchall()
            cur.close()

            total_pages = (total_results + per_page - 1) // per_page
            if not results:
                flash(f"No Student Record found for '{query}'.", "danger")

            return render_template(
                'students.html',
                student=results,
                programs=get_programs(),
                search_query=query,
                current_page=page,
                total_pages=total_pages,
                per_page=per_page
            )

        elif category == 'students':
            cur.execute(
                "SELECT COUNT(*) FROM students WHERE "
                "firstname LIKE %s OR lastname LIKE %s OR id LIKE %s OR course LIKE %s OR year LIKE %s OR gender = %s",  
                tuple('%' + query + '%' for _ in range(5)) + (query,)  
            )
            total_results = cur.fetchone()[0]

            cur.execute(
                """
                SELECT s.image_url, s.id, s.firstname, s.lastname, s.course, s.year, s.gender,
                    COALESCE(c.name, '') AS college_name
                FROM students s
                LEFT JOIN programs p ON s.course = p.code
                LEFT JOIN colleges c ON p.college_code = c.code
                WHERE s.firstname LIKE %s OR s.lastname LIKE %s OR s.id LIKE %s OR s.course LIKE %s OR s.year LIKE %s OR s.gender = %s
                LIMIT %s OFFSET %s
                """,
                tuple('%' + query + '%' for _ in range(5)) + (query, per_page, offset)
            )
            results = cur.fetchall()

            cur.close()

            total_pages = (total_results + per_page - 1) // per_page
            if not results:
                flash(f"No Student Record found for '{query}'.", "danger")

            return render_template(
                'students.html',
                student=results,
                programs=get_programs(),
                search_query=query,
                current_page=page,
                total_pages=total_pages,
                per_page=per_page
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
            if not results:
                flash(f"No Program Record found for '{query}'.", "danger")

            return render_template(
                'programs.html',
                programs=results,
                search_query=query,
                current_page=page,
                total_pages=total_pages,
                per_page=per_page
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
            if not results:
                flash(f"No College Record found for '{query}'.", "danger")

            return render_template(
                'colleges.html',
                colleges=results,
                search_query=query,
                current_page=page,
                total_pages=total_pages,
                per_page=per_page
            )

    except Exception as e:
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for('views.students', page=1))

    flash("No results found.", "info")
    return redirect(url_for('views.students'))



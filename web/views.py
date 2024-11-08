from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_mysqldb import MySQL
import cloudinary.uploader

views = Blueprint('views', __name__)
mysql = MySQL()

@views.route("/")
def navbar():
    return render_template('base.html')

# Students routes
def get_programs():
    cur = mysql.connection.cursor()
    cur.execute('SELECT code, name FROM programs')
    programs = cur.fetchall()
    cur.close()
    return programs

@views.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        image = request.files.get('image')
        id = request.form['id']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        course = request.form['course']
        year = request.form['year']
        gender = request.form['gender']

        # Handle image upload with Cloudinary
        image_url = None
        if image:
            upload_result = cloudinary.uploader.upload(image)
            image_url = upload_result.get("secure_url")
            print(f"Image URL from Cloudinary: {image_url}")

        # Check that all fields are filled
        if not (id and firstname and lastname and course and year and gender):
            flash('All fields are required!', 'danger')
            return redirect(url_for('views.students'))

        # Call create_student with correct parameter order
        if create_student(id, firstname, lastname, course, year, gender, image_url):
            flash('Student added successfully!', 'success')
            return redirect(url_for('views.students'))
        else:
            flash('ID number already exists. Please use a different ID number.', 'danger')
            return render_template('students.html', student=get_students(), programs=get_programs(), stay_open=True)

    students_list = get_students()
    programs = get_programs()

    return render_template('students.html', student=students_list, programs=programs)

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

    if not query or not category:
        flash("Please enter a search query and select a category.", "danger")
        return redirect(url_for('views.students'))

    try:
        cur = mysql.connection.cursor()
        if category == 'students':
            cur.execute("SELECT id, firstname, lastname, course, year, gender FROM students WHERE firstname LIKE %s OR lastname LIKE %s OR id LIKE %s OR course LIKE %s OR year LIKE %s OR gender LIKE %s", 
                           ('%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%', '%' + query + '%'))
            results = cur.fetchall()
            if not results:
                flash(f"No Student Record found for '{query}'.", "danger")
            return render_template('students.html', student=results, programs=get_programs(), search_query=query)

        elif category == 'programs':
            cur.execute("SELECT * FROM programs WHERE code LIKE %s OR name LIKE %s OR college_code LIKE %s", 
                           ('%' + query + '%', '%' + query + '%', '%' + query + '%'))
            results = cur.fetchall()
            if not results:
                flash(f"No Program Record found for '{query}'.", "danger")
            return render_template('programs.html', programs=results, search_query=query)

        elif category == 'colleges':
            cur.execute("SELECT * FROM colleges WHERE code LIKE %s OR name LIKE %s", 
                           ('%' + query + '%', '%' + query + '%'))
            results = cur.fetchall()
            if not results:
                flash(f"No College Record found for '{query}'.", "danger")
            return render_template('colleges.html', colleges=results, search_query=query)

    except Exception as e:
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for('views.students'))

    flash("No results found.", "info")
    return redirect(url_for('views.students'))

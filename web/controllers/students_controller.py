from flask import Blueprint, render_template, request, flash, redirect, url_for
from cloudinary.uploader import upload as cloudinary_upload
from ..models.student_model import (
    get_programs, get_students_paginated, create_student,
    get_students, delete_student, update_student
)

students_bp = Blueprint('students', __name__)

@students_bp.route("/", methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        image = request.files.get('image')
        id = request.form['id']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        course = request.form['course']
        year = request.form['year']
        gender = request.form['gender']

        image_url = None
        if image:
            upload_result = cloudinary_upload(image)
            image_url = upload_result.get("secure_url")

        if not (id and firstname and lastname and course and year and gender):
            flash('All fields are required!', 'danger')
            return redirect(url_for('students.students'))

        if create_student(id, firstname, lastname, course, year, gender, image_url):
            flash('Student added successfully!', 'success')
            return redirect(url_for('students.students'))
        else:
            flash('ID number already exists. Please use a different ID number.', 'danger')
    
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

@students_bp.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    delete_student(id_data)
    flash("Student Record Has Been Deleted Successfully", "success")
    return redirect(url_for('students.students'))

@students_bp.route('/update', methods=['POST'])
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
            new_image_url = upload_result['url']
            
    if not new_image_url:
        new_image_url = current_image_url

    update_student(student_id, firstname, lastname, course, year, gender, new_image_url)
    
    flash('Student updated successfully!', 'success')
    return redirect(url_for('students.students'))

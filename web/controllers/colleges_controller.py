from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models.college_model import get_colleges, insert_college, update_college, delete_college

colleges_bp = Blueprint('colleges', __name__)

@colleges_bp.route('/colleges', methods=['GET', 'POST'])
def colleges():
    if request.method == 'POST':
        college_code = request.form['college_code']  
        college_name = request.form['college_name']
        
        if not college_code or not college_name:
            flash("Both College Code and Name are required", "danger")
            return redirect(url_for('colleges.colleges'))
        
        if not insert_college(college_code, college_name):
            flash("College Code already exists. Please use a different code.", "danger")
            return redirect(url_for('colleges.colleges'))

        flash("College Added Successfully", "success")

    colleges_data = get_colleges()
    return render_template('colleges.html', colleges=colleges_data)

@colleges_bp.route('/update_college/<string:college_code>', methods=['POST'])
def update_college_route(college_code):
    college_name = request.form['college_name']
    new_college_code = request.form['college_code']

    if not update_college(college_code, new_college_code, college_name):
        flash("College code already exists. Please use a different code.", "danger")
        return redirect(url_for('colleges.colleges'))

    flash("College Updated Successfully", "success")
    return redirect(url_for('colleges.colleges'))

@colleges_bp.route('/delete_college/<string:college_code>', methods=['GET'])
def delete_college_route(college_code):
    delete_college(college_code)
    flash("College Deleted Successfully", "success")
    return redirect(url_for('colleges.colleges'))

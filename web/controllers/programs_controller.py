from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models.program_model import (
    get_programs_all, get_programs_by_college, insert_program,
    update_program, delete_program, add_program_to_college
)

programs_bp = Blueprint('programs', __name__)

@programs_bp.route('/programs', methods=['GET'])
def programs():
    programs_data, colleges_data = get_programs_all()
    return render_template('programs.html', programs=programs_data, colleges=colleges_data)

@programs_bp.route('/view_programs/<string:college_code>', methods=['GET'])
def view_programs(college_code):
    programs_data = get_programs_by_college(college_code)
    return render_template('view_programs.html', programs=programs_data, college_code=college_code)

@programs_bp.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == 'POST':
        code = request.form['code']
        name = request.form['name']
        college_code = request.form['college_code']

        if not code or not name or not college_code:
            flash("All fields are required!", "danger")
            return redirect(url_for('programs.programs'))

        insert_result = insert_program(code, name, college_code)
        if insert_result is None:
            flash(f'College code {college_code} does not exist. Please choose a valid college.', 'danger')
            return redirect(url_for('programs.programs'))
        elif insert_result is False:
            flash("Program code already exists. Please use a different code.", "danger")
            return redirect(url_for('programs.programs'))

        flash("Program added successfully!", "success")
        return redirect(url_for('programs.programs'))

    programs_data, _ = get_programs_all()
    return render_template('programs.html', programs=programs_data)

@programs_bp.route('/update_program/<string:program_code>', methods=['POST'])
def update_program_route(program_code):
    name = request.form['name']
    college_code = request.form['college_code']
    new_program_code = request.form['code']

    update_result = update_program(program_code, new_program_code, name, college_code)
    if not update_result:
        flash("Program code already exists. Please use a different code.", "danger")
        return redirect(url_for('programs.programs'))

    flash("Program updated successfully!", "success")
    return redirect(url_for('programs.programs'))

@programs_bp.route('/delete_program/<string:program_code>', methods=['GET'])
def delete_program_route(program_code):
    delete_program(program_code)
    flash("Program Deleted Successfully", "success")
    return redirect(url_for('programs.programs'))

@programs_bp.route('/add_update_program/<string:college_code>', methods=['POST'])
def add_update_program(college_code):
    program_name = request.form['program_name']
    add_program_to_college(program_name, college_code)
    flash("Program Added Successfully")
    return redirect(url_for('programs.view_programs', college_code=college_code))

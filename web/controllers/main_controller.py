from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models.student_model import get_programs
from flask_mysqldb import MySQL

main_bp = Blueprint('main', __name__)

@main_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    category = request.args.get('search_type', '')
    page = request.args.get('page', 1, type=int)  
    per_page = 10
    offset = (page - 1) * per_page

    if not query or not category:
        return redirect(url_for('students.students', page=page))

    try:
        cur = MySQL.connection.cursor()

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
                "SELECT image_url, id, firstname, lastname, course, year, gender FROM students WHERE "
                "firstname LIKE %s OR lastname LIKE %s OR id LIKE %s OR course LIKE %s OR year LIKE %s OR gender = %s"
                "LIMIT %s OFFSET %s",  
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
        return redirect(url_for('students.students', page=1))

    flash("No results found.", "info")
    return redirect(url_for('students.students'))

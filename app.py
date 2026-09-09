import os
import uuid
import re
import mysql.connector
import csv
from io import StringIO

from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from database.db import get_db_connection


app = Flask(__name__)
app.secret_key = "sih_portal_secret_key"


# =========================================================
# GLOBAL TEMPLATE VARIABLES
# =========================================================

@app.context_processor
def inject_template_variables():
    return {
        "dashboard": "dashboard"
    }


# =========================================================
# AUTHENTICATION DECORATORS
# =========================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        if session.get("role") != "ADMIN":
            flash("Admin access required.", "error")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function

# =========================================================
# INDUSTRY AUTHENTICATION DECORATOR
# =========================================================

def industry_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "Please login first.",
                "error"
            )
            return redirect(url_for("login"))

        if session.get("role") != "INDUSTRY":
            flash(
                "Industry access required.",
                "error"
            )
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function

# =========================================================
# COLLEGE AUTHENTICATION DECORATOR
# =========================================================

def college_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        if session.get("role") != "COLLEGE":

            flash(
                "College access required.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return redirect(url_for("login"))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash(
                "Email and password are required.",
                "error"
            )
            return render_template("login.html")

        conn = None
        cursor = None

        try:

            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    password,
                    role,
                    status
                FROM users
                WHERE email = %s
                LIMIT 1
            """, (email,))

            user = cursor.fetchone()

            # -------------------------------------------------
            # USER NOT FOUND
            # -------------------------------------------------

            if not user:
                flash(
                    "Invalid email or password.",
                    "error"
                )
                return render_template("login.html")

            # -------------------------------------------------
            # ACCOUNT STATUS
            # -------------------------------------------------

            if user["status"] != "ACTIVE":
                flash(
                    "Your account is not active.",
                    "error"
                )
                return render_template("login.html")

            # -------------------------------------------------
            # PASSWORD CHECK
            # -------------------------------------------------

            if not check_password_hash(
                user["password"],
                password
            ):
                flash(
                    "Invalid email or password.",
                    "error"
                )
                return render_template("login.html")

            # -------------------------------------------------
            # LOGIN SUCCESS
            # -------------------------------------------------

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["role"] = user["role"]

            # -------------------------------------------------
            # ADMIN
            # -------------------------------------------------

            if user["role"] == "ADMIN":

                return redirect(
                    url_for("admin_dashboard")
                )


            # -------------------------------------------------
            # INDUSTRY
            # -------------------------------------------------

            if user["role"] == "INDUSTRY":

                return redirect(
                    url_for("industry_dashboard")
                )

            # -------------------------------------------------
            # COLLEGE
            # -------------------------------------------------

            if user["role"] == "COLLEGE":

                return redirect(
                    url_for("college_dashboard")
                )


            # -------------------------------------------------
            # OTHER ROLES
            # -------------------------------------------------

            flash(
                "Login successful. Your dashboard is coming soon.",
                "success"
            )

            return redirect(
                url_for("login")
            )
        except Exception as e:

            print("=" * 60)
            print("LOGIN ERROR:")
            print(type(e).__name__)
            print(e)
            print("=" * 60)

            flash(
                "Unable to process login. Check terminal.",
                "error"
            )

            return render_template("login.html")

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    return render_template("login.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # TOTAL STUDENTS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
        """)

        total_students = cursor.fetchone()["total"]


        # =================================================
        # TOTAL COLLEGES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM colleges
        """)

        total_colleges = cursor.fetchone()["total"]


        # =================================================
        # TOTAL PLACEMENT CELLS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM placement_cells
        """)

        total_placement_cells = cursor.fetchone()["total"]


        # =================================================
        # TOTAL INDUSTRIES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM industries
        """)

        total_industries = cursor.fetchone()["total"]


        # =================================================
        # ACTIVE USERS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM users
            WHERE status = 'ACTIVE'
        """)

        active_users = cursor.fetchone()["total"]


        # =================================================
        # PENDING COLLEGES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM colleges
            WHERE status = 'PENDING'
        """)

        pending_colleges = cursor.fetchone()["total"]


        # =================================================
        # PENDING PLACEMENT CELLS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM placement_cells pc
            INNER JOIN users u
                ON pc.user_id = u.id
            WHERE u.status = 'PENDING'
        """)

        pending_placement_cells = cursor.fetchone()["total"]


        # =================================================
        # PENDING INDUSTRIES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM industries i
            INNER JOIN users u
                ON i.user_id = u.id
            WHERE u.status = 'PENDING'
        """)

        pending_industries = cursor.fetchone()["total"]


        # =================================================
        # TOTAL COLLABORATIONS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
        """)

        active_collaborations = cursor.fetchone()["total"]


        # =================================================
        # TOTAL PROJECTS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_projects
        """)

        total_projects = cursor.fetchone()["total"]


        # =================================================
        # TOTAL OPPORTUNITIES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
        """)

        total_opportunities = cursor.fetchone()["total"]


        # =================================================
        # RECENT REGISTRATIONS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                status,
                created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 10
        """)

        recent_registrations = cursor.fetchall()


        # =================================================
        # DASHBOARD TEMPLATE
        # =================================================

        return render_template(
            "admin/dashboard.html",

            # Active page
            dashboard="dashboard",

            # Statistics
            total_students=total_students,
            total_colleges=total_colleges,
            total_placement_cells=total_placement_cells,
            total_industries=total_industries,
            active_users=active_users,

            # Pending
            pending_colleges=pending_colleges,
            pending_placement_cells=pending_placement_cells,
            pending_industries=pending_industries,

            # Other statistics
            active_collaborations=active_collaborations,
            total_projects=total_projects,
            total_opportunities=total_opportunities,

            # Recent registrations
            recent_registrations=recent_registrations
        )


    except Exception as e:

        print("=" * 60)
        print("ADMIN DASHBOARD ERROR:")
        print(e)
        print("=" * 60)

        flash(
            "Unable to load dashboard. Check terminal for exact error.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENTS - LIST
# =========================================================

@app.route("/admin/students")
@admin_required
def admin_students():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # STUDENT LIST
        # Only confirmed columns from students table
        # =================================================

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                s.college_id,

                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,

                s.phone,
                s.dob,
                s.gender,
                s.address,

                s.cgpa,
                s.active_backlogs,

                u.name AS name,
                u.email AS email,
                u.status AS status,

                c.college_name AS college_name,

                /* Compatibility fields for existing HTML */
                s.passing_year AS batch,
                s.cgpa AS current_cgpa,
                '' AS city,
                '' AS state,
                0 AS profile_completion

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            ORDER BY u.created_at DESC
        """)

        students = cursor.fetchall()


        # =================================================
        # COLLEGES FOR FILTER
        # =================================================

        cursor.execute("""
            SELECT
                id,
                college_name
            FROM colleges
            ORDER BY college_name ASC
        """)

        colleges = cursor.fetchall()


        # =================================================
        # BRANCHES FOR FILTER
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                branch
            FROM students
            WHERE branch IS NOT NULL
              AND branch != ''
            ORDER BY branch ASC
        """)

        branches = [
            row["branch"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # RENDER STUDENT PAGE
        # =================================================

        return render_template(
            "admin/students.html",
            dashboard="students",
            students=students,
            colleges=colleges,
            branches=branches
        )


    except Exception as e:

        print("=" * 70)
        print("STUDENTS PAGE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Students Error</title>
        </head>

        <body style="font-family: Arial; padding: 40px;">

            <h2 style="color: #dc3545;">
                Students Page Error
            </h2>

            <p>
                <strong>Error Type:</strong>
                {type(e).__name__}
            </p>

            <pre>{e}</pre>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT DETAILS
# =========================================================

@app.route("/admin/students/<student_id>")
@admin_required
def student_details(student_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # STUDENT INFORMATION
        # =================================================

        cursor.execute("""
            SELECT
                s.*,

                u.name AS name,
                u.email AS email,
                u.status AS status,
                u.created_at AS user_created_at,

                c.college_name AS college_name,
                c.college_code AS college_code,
                c.university_name AS university_name,
                c.city AS college_city,
                c.state AS college_state

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            WHERE s.id = %s

            LIMIT 1
        """, (student_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student not found.",
                "error"
            )

            return redirect(
                url_for("admin_students")
            )


        # =================================================
        # COMPATIBILITY VALUES FOR STUDENT DETAILS PAGE
        # =================================================

        # Your actual DB has cgpa, not current_sgpa.
        student["current_sgpa"] = None

        # Your actual DB does not have profile_completion.
        student["profile_completed"] = False


        # =================================================
        # STUDENT SKILLS
        # =================================================

        cursor.execute("""
            SELECT *
            FROM student_skills
            WHERE student_id = %s
        """, (student_id,))

        skills = cursor.fetchall()


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "admin/student-details.html",

            dashboard="students",

            student=student,
            skills=skills
        )


    except Exception as e:

        print("=" * 70)
        print("STUDENT DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Student Details Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
            background: #f5f7fb;
        ">

            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                border-left: 5px solid #dc3545;
            ">

                <h2 style="color:#dc3545;">
                    Student Details Error
                </h2>

                <p>
                    <strong>Error Type:</strong>
                    {type(e).__name__}
                </p>

                <pre style="
                    background:#f1f1f1;
                    padding:15px;
                    border-radius:8px;
                    white-space:pre-wrap;
                ">{e}</pre>

            </div>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

            
# =========================================================
# STUDENT STATUS TOGGLE
# =========================================================

@app.route(
    "/admin/students/<student_id>/toggle-status",
    methods=["POST"]
)
@admin_required
def toggle_student_status(student_id):

    new_status = request.form.get("status")


    if new_status not in [
        "ACTIVE",
        "INACTIVE"
    ]:

        flash(
            "Invalid student status.",
            "error"
        )

        return redirect(
            url_for(
                "student_details",
                student_id=student_id
            )
        )


    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        cursor.execute("""
            SELECT user_id
            FROM students
            WHERE id = %s
            LIMIT 1
        """, (student_id,))

        student = cursor.fetchone()


        if not student:

            flash(
                "Student not found.",
                "error"
            )

            return redirect(
                url_for("admin_students")
            )


        cursor.execute("""
            UPDATE users
            SET status = %s
            WHERE id = %s
        """, (
            new_status,
            student["user_id"]
        ))


        conn.commit()


        flash(
            f"Student status changed to {new_status}.",
            "success"
        )


        return redirect(
            url_for(
                "student_details",
                student_id=student_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "STUDENT STATUS ERROR:",
            e
        )

        flash(
            "Unable to update student status.",
            "error"
        )

        return redirect(
            url_for(
                "student_details",
                student_id=student_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# COLLEGES - LIST
# =========================================================

@app.route("/admin/colleges")
@admin_required
def admin_colleges():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # COLLEGE LIST
        # =================================================

        cursor.execute("""
            SELECT
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,

                u.name AS user_name,
                u.status AS user_status,

                COUNT(DISTINCT s.id) AS student_count

            FROM colleges c

            LEFT JOIN users u
                ON c.user_id = u.id

            LEFT JOIN students s
                ON c.id = s.college_id

            GROUP BY
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,
                u.name,
                u.status

            ORDER BY c.created_at DESC
        """)

        colleges = cursor.fetchall()


        # =================================================
        # STATES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT state
            FROM colleges
            WHERE state IS NOT NULL
              AND state != ''
            ORDER BY state ASC
        """)

        states = [
            row["state"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # CITIES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT city
            FROM colleges
            WHERE city IS NOT NULL
              AND city != ''
            ORDER BY city ASC
        """)

        cities = [
            row["city"]
            for row in cursor.fetchall()
        ]


        return render_template(
            "admin/colleges.html",

            dashboard="colleges",

            colleges=colleges,
            states=states,
            cities=cities
        )


    except Exception as e:

        print(
            "COLLEGES ERROR:",
            e
        )

        flash(
            "Unable to load colleges.",
            "error"
        )

        return redirect(
            url_for("admin_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# COLLEGE DETAILS
# =========================================================

@app.route("/admin/colleges/<college_id>")
@admin_required
def college_details(college_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # COLLEGE INFORMATION
        # =================================================

        cursor.execute("""
            SELECT
                c.*,

                u.name AS user_name,
                u.email AS user_email,
                u.status AS user_status,
                u.created_at AS user_created_at

            FROM colleges c

            LEFT JOIN users u
                ON c.user_id = u.id

            WHERE c.id = %s
            LIMIT 1
        """, (college_id,))

        college = cursor.fetchone()


        if not college:

            flash(
                "College not found.",
                "error"
            )

            return redirect(
                url_for("admin_colleges")
            )


        # =================================================
        # STUDENT COUNT
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (college_id,))

        student_count = cursor.fetchone()["total"]


        # =================================================
        # PLACEMENT CELL
        # =================================================

        cursor.execute("""
            SELECT
                pc.*,

                u.name,
                u.email,
                u.status AS user_status

            FROM placement_cells pc

            LEFT JOIN users u
                ON pc.user_id = u.id

            WHERE pc.college_id = %s

            LIMIT 1
        """, (college_id,))

        placement_cell = cursor.fetchone()


        # =================================================
        # COLLEGE STUDENTS
        # =================================================

        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.phone,

                u.name,
                u.email,
                u.status

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.college_id = %s

            ORDER BY u.name ASC
        """, (college_id,))

        students = cursor.fetchall()


        return render_template(
            "admin/college-details.html",

            dashboard="colleges",

            college=college,
            student_count=student_count,
            placement_cell=placement_cell,
            students=students
        )


    except Exception as e:

        print(
            "COLLEGE DETAILS ERROR:",
            e
        )

        flash(
            "Unable to load college details.",
            "error"
        )

        return redirect(
            url_for("admin_colleges")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# COLLEGE STATUS TOGGLE
# =========================================================

@app.route(
    "/admin/colleges/<college_id>/toggle-status",
    methods=["POST"]
)
@admin_required
def toggle_college_status(college_id):

    new_status = request.form.get("status")


    if new_status not in [
        "ACTIVE",
        "INACTIVE"
    ]:

        flash(
            "Invalid college status.",
            "error"
        )

        return redirect(
            url_for(
                "college_details",
                college_id=college_id
            )
        )


    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # GET COLLEGE USER
        # =================================================

        cursor.execute("""
            SELECT user_id
            FROM colleges
            WHERE id = %s
            LIMIT 1
        """, (college_id,))

        college = cursor.fetchone()


        if not college:

            flash(
                "College not found.",
                "error"
            )

            return redirect(
                url_for("admin_colleges")
            )


        # =================================================
        # UPDATE COLLEGE STATUS
        # =================================================

        cursor.execute("""
            UPDATE colleges
            SET status = %s
            WHERE id = %s
        """, (
            new_status,
            college_id
        ))


        # =================================================
        # UPDATE USER STATUS
        # =================================================

        cursor.execute("""
            UPDATE users
            SET status = %s
            WHERE id = %s
        """, (
            new_status,
            college["user_id"]
        ))


        conn.commit()


        flash(
            f"College status changed to {new_status}.",
            "success"
        )


        return redirect(
            url_for(
                "college_details",
                college_id=college_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "COLLEGE STATUS ERROR:",
            e
        )

        flash(
            "Unable to update college status.",
            "error"
        )

        return redirect(
            url_for(
                "college_details",
                college_id=college_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELLS - LIST
# =========================================================

@app.route("/admin/placement-cells")
@admin_required
def admin_placement_cells():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # PLACEMENT CELL LIST
        # =================================================

        cursor.execute("""
            SELECT
                pc.id,
                pc.user_id,
                pc.college_id,
                pc.status,

                u.name AS name,
                u.email AS email,
                u.created_at AS created_at,

                c.college_name AS college_name,
                c.college_code AS college_code

            FROM placement_cells pc

            INNER JOIN users u
                ON pc.user_id = u.id

            INNER JOIN colleges c
                ON pc.college_id = c.id

            ORDER BY u.created_at DESC
        """)

        placement_cells = cursor.fetchall()


        # =================================================
        # COLLEGES FOR FILTER
        # =================================================

        cursor.execute("""
            SELECT
                id,
                college_name
            FROM colleges
            ORDER BY college_name ASC
        """)

        colleges = cursor.fetchall()


        # =================================================
        # RENDER PLACEMENT CELL PAGE
        # =================================================

        return render_template(
            "admin/placement-cells.html",

            dashboard="placement-cells",

            placement_cells=placement_cells,
            colleges=colleges
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT CELLS PAGE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Placement Cells Error</title>
        </head>

        <body style="font-family: Arial; padding: 40px;">

            <h2 style="color: #dc3545;">
                Placement Cells Page Error
            </h2>

            <p>
                <strong>Error Type:</strong>
                {type(e).__name__}
            </p>

            <pre>{e}</pre>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL DETAILS
# =========================================================

@app.route("/admin/placement-cells/<placement_cell_id>")
@admin_required
def placement_cell_details(placement_cell_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # PLACEMENT CELL INFORMATION
        # =================================================

        cursor.execute("""
            SELECT

                pc.id,
                pc.user_id,
                pc.college_id,
                pc.status,

                u.name AS name,
                u.email AS email,
                u.created_at AS created_at,

                c.college_name AS college_name,
                c.college_code AS college_code,
                c.university_name AS university_name

            FROM placement_cells pc

            INNER JOIN users u
                ON pc.user_id = u.id

            INNER JOIN colleges c
                ON pc.college_id = c.id

            WHERE pc.id = %s

            LIMIT 1
        """, (placement_cell_id,))

        placement_cell = cursor.fetchone()


        if not placement_cell:

            flash(
                "Placement cell not found.",
                "error"
            )

            return redirect(
                url_for("admin_placement_cells")
            )


        # =================================================
        # STUDENT COUNT
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM students

            WHERE college_id = %s
        """, (
            placement_cell["college_id"],
        ))

        student_count = cursor.fetchone()["total"]


        # =================================================
        # COLLEGE STUDENTS
        # =================================================

        cursor.execute("""
            SELECT

                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.phone,

                u.name AS name,
                u.email AS email,
                u.status AS status

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.college_id = %s

            ORDER BY u.name ASC
        """, (
            placement_cell["college_id"],
        ))

        students = cursor.fetchall()


        # =================================================
        # RENDER DETAILS PAGE
        # =================================================

        return render_template(
            "admin/placement-cell-details.html",

            dashboard="placement-cells",

            placement_cell=placement_cell,
            student_count=student_count,
            students=students
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT CELL DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Placement Cell Details Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
            background: #f5f7fb;
        ">

            <h2 style="color:#dc3545;">
                Placement Cell Details Error
            </h2>

            <p>
                <strong>Error Type:</strong>
                {type(e).__name__}
            </p>

            <pre>{e}</pre>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL STATUS TOGGLE
# =========================================================

@app.route(
    "/admin/placement-cells/<placement_cell_id>/toggle-status",
    methods=["POST"]
)
@admin_required
def toggle_placement_cell_status(placement_cell_id):

    new_status = request.form.get("status")


    if new_status not in [
        "ACTIVE",
        "INACTIVE"
    ]:

        flash(
            "Invalid placement cell status.",
            "error"
        )

        return redirect(
            url_for(
                "placement_cell_details",
                placement_cell_id=placement_cell_id
            )
        )


    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # GET PLACEMENT CELL USER
        # =================================================

        cursor.execute("""
            SELECT
                user_id

            FROM placement_cells

            WHERE id = %s

            LIMIT 1
        """, (
            placement_cell_id,
        ))

        placement_cell = cursor.fetchone()


        if not placement_cell:

            flash(
                "Placement cell not found.",
                "error"
            )

            return redirect(
                url_for("admin_placement_cells")
            )


        # =================================================
        # UPDATE PLACEMENT CELL STATUS
        # =================================================

        cursor.execute("""
            UPDATE placement_cells

            SET status = %s

            WHERE id = %s
        """, (
            new_status,
            placement_cell_id
        ))


        # =================================================
        # UPDATE USER STATUS
        # =================================================

        cursor.execute("""
            UPDATE users

            SET status = %s

            WHERE id = %s
        """, (
            new_status,
            placement_cell["user_id"]
        ))


        conn.commit()


        flash(
            f"Placement cell status changed to {new_status}.",
            "success"
        )


        return redirect(
            url_for(
                "placement_cell_details",
                placement_cell_id=placement_cell_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT CELL STATUS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update placement cell status.",
            "error"
        )

        return redirect(
            url_for(
                "placement_cell_details",
                placement_cell_id=placement_cell_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRIES - LIST
# =========================================================

@app.route("/admin/industries")
@admin_required
def admin_industries():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # INDUSTRY LIST
        # =================================================

        cursor.execute("""
            SELECT
                i.*,

                u.name AS user_name,
                u.email AS user_email,
                u.status AS user_status,
                u.created_at AS user_created_at

            FROM industries i

            INNER JOIN users u
                ON i.user_id = u.id

            ORDER BY u.created_at DESC
        """)

        industries = cursor.fetchall()


        # =================================================
        # INDUSTRY TYPES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                company_type
            FROM industries
            WHERE company_type IS NOT NULL
              AND company_type != ''
            ORDER BY company_type ASC
        """)

        industry_types = [
            row["company_type"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # INDUSTRY SECTORS
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                industry_sector
            FROM industries
            WHERE industry_sector IS NOT NULL
              AND industry_sector != ''
            ORDER BY industry_sector ASC
        """)

        industry_sectors = [
            row["industry_sector"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "admin/industries.html",

            dashboard="industries",

            industries=industries,
            industry_types=industry_types,
            industry_sectors=industry_sectors
        )


    except Exception as e:

        print("=" * 70)
        print("INDUSTRIES PAGE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Industries Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
        ">

            <h2 style="color:#dc3545;">
                Industries Page Error
            </h2>

            <p>
                <strong>Error Type:</strong>
                {type(e).__name__}
            </p>

            <pre>{e}</pre>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY DETAILS
# =========================================================

@app.route("/admin/industries/<industry_id>")
@admin_required
def industry_details(industry_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # INDUSTRY INFORMATION
        # =================================================

        cursor.execute("""
            SELECT
                i.*,

                u.name AS user_name,
                u.email AS user_email,
                u.status AS user_status,
                u.created_at AS user_created_at

            FROM industries i

            INNER JOIN users u
                ON i.user_id = u.id

            WHERE i.id = %s

            LIMIT 1
        """, (industry_id,))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry not found.",
                "error"
            )

            return redirect(
                url_for("admin_industries")
            )


        # =================================================
        # RENDER DETAILS
        # =================================================

        return render_template(
            "admin/industry-details.html",

            dashboard="industries",

            industry=industry
        )


    except Exception as e:

        print("=" * 70)
        print("INDUSTRY DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Industry Details Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
            background: #f5f7fb;
        ">

            <div style="
                background:white;
                padding:30px;
                border-radius:12px;
                border-left:5px solid #dc3545;
            ">

                <h2 style="color:#dc3545;">
                    Industry Details Error
                </h2>

                <p>
                    <strong>Error Type:</strong>
                    {type(e).__name__}
                </p>

                <pre style="
                    background:#f1f1f1;
                    padding:15px;
                    border-radius:8px;
                    white-space:pre-wrap;
                ">{e}</pre>

            </div>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY STATUS TOGGLE
# =========================================================

@app.route(
    "/admin/industries/<industry_id>/toggle-status",
    methods=["POST"]
)
@admin_required
def toggle_industry_status(industry_id):

    new_status = request.form.get("status")


    if new_status not in [
        "ACTIVE",
        "INACTIVE"
    ]:

        flash(
            "Invalid industry status.",
            "error"
        )

        return redirect(
            url_for(
                "industry_details",
                industry_id=industry_id
            )
        )


    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # GET INDUSTRY USER
        # =================================================

        cursor.execute("""
            SELECT
                user_id

            FROM industries

            WHERE id = %s

            LIMIT 1
        """, (
            industry_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry not found.",
                "error"
            )

            return redirect(
                url_for("admin_industries")
            )


        # =================================================
        # UPDATE INDUSTRY STATUS
        # =================================================

        cursor.execute("""
            UPDATE industries

            SET status = %s

            WHERE id = %s
        """, (
            new_status,
            industry_id
        ))


        # =================================================
        # UPDATE USER STATUS
        # =================================================

        cursor.execute("""
            UPDATE users

            SET status = %s

            WHERE id = %s
        """, (
            new_status,
            industry["user_id"]
        ))


        conn.commit()


        flash(
            f"Industry status changed to {new_status}.",
            "success"
        )


        return redirect(
            url_for(
                "industry_details",
                industry_id=industry_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()


        print("=" * 70)
        print("INDUSTRY STATUS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)


        flash(
            "Unable to update industry status.",
            "error"
        )


        return redirect(
            url_for(
                "industry_details",
                industry_id=industry_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# USERS - LIST
# =========================================================

@app.route("/admin/users")
@admin_required
def admin_users():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # ALL USERS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                status,
                created_at
            FROM users
            ORDER BY created_at DESC
        """)

        users = cursor.fetchall()


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "admin/users.html",

            dashboard="users",

            users=users
        )


    except Exception as e:

        print("=" * 70)
        print("USERS PAGE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Users Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
        ">

            <h2 style="color:#dc3545;">
                Users Page Error
            </h2>

            <p>
                <strong>Error Type:</strong>
                {type(e).__name__}
            </p>

            <pre>{e}</pre>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# USER DETAILS
# =========================================================

@app.route("/admin/users/<user_id>")
@admin_required
def user_details(user_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # USER INFORMATION
        # =================================================

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                status,
                created_at
            FROM users
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        user = cursor.fetchone()


        if not user:

            flash(
                "User not found.",
                "error"
            )

            return redirect(
                url_for("admin_users")
            )


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "admin/user-details.html",

            dashboard="users",

            user=user
        )


    except Exception as e:

        print("=" * 70)
        print("USER DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>User Details Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
            background: #f5f7fb;
        ">

            <div style="
                background:white;
                padding:30px;
                border-radius:12px;
                border-left:5px solid #dc3545;
            ">

                <h2 style="color:#dc3545;">
                    User Details Error
                </h2>

                <p>
                    <strong>Error Type:</strong>
                    {type(e).__name__}
                </p>

                <pre style="
                    background:#f1f1f1;
                    padding:15px;
                    border-radius:8px;
                    white-space:pre-wrap;
                ">{e}</pre>

            </div>

        </body>
        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# USER STATUS TOGGLE
# =========================================================

@app.route(
    "/admin/users/<user_id>/toggle-status",
    methods=["POST"]
)
@admin_required
def toggle_user_status(user_id):

    new_status = request.form.get("status")


    if new_status not in [
        "ACTIVE",
        "INACTIVE"
    ]:

        flash(
            "Invalid user status.",
            "error"
        )

        return redirect(
            url_for(
                "user_details",
                user_id=user_id
            )
        )


    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # =================================================
        # CHECK USER
        # =================================================

        cursor.execute("""
            SELECT
                id,
                role
            FROM users
            WHERE id = %s
            LIMIT 1
        """, (user_id,))

        user = cursor.fetchone()


        if not user:

            flash(
                "User not found.",
                "error"
            )

            return redirect(
                url_for("admin_users")
            )


        # =================================================
        # UPDATE STATUS
        # =================================================

        cursor.execute("""
            UPDATE users
            SET status = %s
            WHERE id = %s
        """, (
            new_status,
            user_id
        ))


        # =================================================
        # KEEP ROLE-SPECIFIC PROFILE SYNCHRONIZED
        # =================================================

        if user["role"] == "STUDENT":

            cursor.execute("""
                UPDATE students
                SET updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (user_id,))


        elif user["role"] == "COLLEGE":

            cursor.execute("""
                UPDATE colleges
                SET status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (
                new_status,
                user_id
            ))


        elif user["role"] == "PLACEMENT_CELL":

            cursor.execute("""
                UPDATE placement_cells
                SET status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (
                new_status,
                user_id
            ))


        elif user["role"] == "INDUSTRY":

            cursor.execute("""
                UPDATE industries
                SET status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (
                new_status,
                user_id
            ))


        conn.commit()


        flash(
            f"User status changed to {new_status}.",
            "success"
        )


        return redirect(
            url_for(
                "user_details",
                user_id=user_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()


        print("=" * 70)
        print("USER STATUS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)


        flash(
            "Unable to update user status.",
            "error"
        )


        return redirect(
            url_for(
                "user_details",
                user_id=user_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
            
# =========================================================
# COLLABORATIONS - LIST
# =========================================================

@app.route("/admin/collaborations")
@admin_required
def admin_collaborations():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # COLLABORATIONS
        # =================================================

        cursor.execute("""
            SELECT
                col.id,
                col.college_id,
                col.industry_id,
                col.title,
                col.description,
                col.collaboration_type,
                col.start_date,
                col.end_date,
                col.status,
                col.created_at,

                c.college_name AS college_name,
                c.college_code AS college_code,

                i.company_name AS industry_name,
                i.email AS industry_email

            FROM collaborations col

            INNER JOIN colleges c
                ON col.college_id = c.id

            INNER JOIN industries i
                ON col.industry_id = i.id

            ORDER BY col.created_at DESC
        """)

        collaborations = cursor.fetchall()


        # =================================================
        # COLLABORATION TYPES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT collaboration_type
            FROM collaborations
            WHERE collaboration_type IS NOT NULL
            ORDER BY collaboration_type ASC
        """)

        type_rows = cursor.fetchall()

        collaboration_types = [
            row["collaboration_type"]
            for row in type_rows
        ]


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "admin/collaborations.html",

            dashboard="collaborations",

            collaborations=collaborations,

            collaboration_types=collaboration_types
        )


    except Exception as e:

        print("=" * 70)
        print("COLLABORATIONS PAGE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return f"""
        <!DOCTYPE html>
        <html>

        <head>
            <title>Collaborations Page Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
            background: #f5f7fb;
        ">

            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                border-left: 5px solid #dc2626;
            ">

                <h2 style="color:#dc2626;">
                    Collaborations Page Error
                </h2>

                <p>
                    <strong>Error Type:</strong>
                    {type(e).__name__}
                </p>

                <pre style="
                    background:#f1f5f9;
                    padding:15px;
                    border-radius:8px;
                    white-space:pre-wrap;
                ">{e}</pre>

            </div>

        </body>

        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# COLLABORATION DETAILS
# =========================================================

@app.route("/admin/collaborations/<collaboration_id>")
@admin_required
def collaboration_details(collaboration_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # COLLABORATION + COLLEGE + INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                col.id,
                col.college_id,
                col.industry_id,
                col.title,
                col.description,
                col.collaboration_type,
                col.start_date,
                col.end_date,
                col.status,
                col.created_at,
                col.updated_at,

                c.college_name AS college_name,
                c.college_code AS college_code,
                c.university_name AS university_name,
                c.email AS college_email,

                i.company_name AS industry_name,
                i.email AS industry_email,
                i.company_type AS company_type,
                i.industry_sector AS industry_sector

            FROM collaborations col

            INNER JOIN colleges c
                ON col.college_id = c.id

            INNER JOIN industries i
                ON col.industry_id = i.id

            WHERE col.id = %s

            LIMIT 1
        """, (collaboration_id,))

        collaboration = cursor.fetchone()


        # =================================================
        # NOT FOUND
        # =================================================

        if not collaboration:

            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Collaboration Not Found</title>
            </head>

            <body style="
                font-family: Arial;
                padding: 40px;
                background: #f5f7fb;
            ">

                <div style="
                    background: white;
                    padding: 30px;
                    border-radius: 12px;
                ">

                    <h2 style="color:#dc2626;">
                        Collaboration Not Found
                    </h2>

                    <p>
                        The requested collaboration does not exist.
                    </p>

                    <a href="/admin/collaborations">
                        ← Back to Collaborations
                    </a>

                </div>

            </body>
            </html>
            """, 404


        # =================================================
        # RENDER DETAILS PAGE
        # =================================================

        return render_template(
            "admin/collaboration-details.html",

            dashboard="collaborations",

            collaboration=collaboration
        )


    except Exception as e:

        print("=" * 70)
        print("COLLABORATION DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)


        return f"""
        <!DOCTYPE html>
        <html>

        <head>
            <title>Collaboration Details Error</title>
        </head>

        <body style="
            font-family: Arial;
            padding: 40px;
            background: #f5f7fb;
        ">

            <div style="
                background: white;
                padding: 30px;
                border-radius: 12px;
                border-left: 5px solid #dc2626;
            ">

                <h2 style="color:#dc2626;">
                    Collaboration Details Page Error
                </h2>

                <p>
                    <strong>Error Type:</strong>
                    {type(e).__name__}
                </p>

                <pre style="
                    background:#f1f5f9;
                    padding:15px;
                    border-radius:8px;
                    white-space:pre-wrap;
                ">{e}</pre>

            </div>

        </body>

        </html>
        """


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# ADMIN - PROJECTS
# =========================================================

@app.route("/admin/projects")
def admin_projects():

    # Admin access check
    if "user_id" not in session or session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # GET ALL PROJECTS
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                sp.id,
                sp.student_id,
                sp.industry_id,
                sp.title,
                sp.description,
                sp.technology_stack,
                sp.start_date,
                sp.end_date,
                sp.status,
                sp.project_url,
                sp.report_url,
                sp.created_at,
                sp.updated_at,

                s.enrollment_no,

                u.name AS student_name,

                c.id AS college_id,
                c.college_name,
                c.college_code,

                i.company_name AS industry_name,
                i.company_type,
                i.industry_sector

            FROM student_projects sp

            INNER JOIN students s
                ON sp.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            LEFT JOIN industries i
                ON sp.industry_id = i.id

            ORDER BY sp.created_at DESC
        """)

        projects = cursor.fetchall()


        # -------------------------------------------------
        # GET COLLEGES FOR FILTER
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                college_name
            FROM colleges
            ORDER BY college_name ASC
        """)

        colleges = cursor.fetchall()


        # -------------------------------------------------
        # GET INDUSTRIES FOR FILTER
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                company_name
            FROM industries
            ORDER BY company_name ASC
        """)

        industries = cursor.fetchall()


        # -------------------------------------------------
        # PROJECT COUNTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_projects
        """)

        total_projects = cursor.fetchone()["total"]


        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_projects
            WHERE status = 'ONGOING'
        """)

        ongoing_projects = cursor.fetchone()["total"]


        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_projects
            WHERE status = 'COMPLETED'
        """)

        completed_projects = cursor.fetchone()["total"]


        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_projects
            WHERE status = 'CANCELLED'
        """)

        cancelled_projects = cursor.fetchone()["total"]


        return render_template(
            "admin/projects.html",
            projects=projects,
            colleges=colleges,
            industries=industries,
            total_projects=total_projects,
            ongoing_projects=ongoing_projects,
            completed_projects=completed_projects,
            cancelled_projects=cancelled_projects
        )

    except Exception as e:

        print("PROJECTS ERROR:", e)

        flash(
            "Unable to load projects.",
            "error"
        )

        return redirect(url_for("admin_dashboard"))

    finally:

        cursor.close()
        conn.close()


# =========================================================
# ADMIN - PROJECT DETAILS
# =========================================================

@app.route("/admin/projects/<project_id>")
def project_details(project_id):

    # Admin access check
    if "user_id" not in session or session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # GET PROJECT DETAILS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                sp.id,
                sp.student_id,
                sp.industry_id,
                sp.title,
                sp.description,
                sp.technology_stack,
                sp.start_date,
                sp.end_date,
                sp.status,
                sp.project_url,
                sp.report_url,
                sp.created_at,
                sp.updated_at,

                s.enrollment_no,

                u.name AS student_name,

                c.id AS college_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email AS college_email,

                i.company_name AS industry_name,
                i.company_type,
                i.industry_sector,
                i.email AS industry_email

            FROM student_projects sp

            INNER JOIN students s
                ON sp.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            LEFT JOIN industries i
                ON sp.industry_id = i.id

            WHERE sp.id = %s
        """, (project_id,))

        project = cursor.fetchone()


        # -------------------------------------------------
        # PROJECT NOT FOUND
        # -------------------------------------------------

        if not project:

            flash(
                "Project not found.",
                "error"
            )

            return redirect(url_for("admin_projects"))


        # -------------------------------------------------
        # RENDER DETAILS PAGE
        # -------------------------------------------------

        return render_template(
            "admin/project-details.html",
            project=project
        )

    except Exception as e:

        print("PROJECT DETAILS ERROR:", e)

        flash(
            "Unable to load project details.",
            "error"
        )

        return redirect(url_for("admin_projects"))

    finally:

        cursor.close()
        conn.close()

# =========================================================
# OPPORTUNITIES
# =========================================================

@app.route("/admin/opportunities")
def admin_opportunities():

    # Admin access check
    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # FETCH OPPORTUNITIES
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                o.id,
                o.industry_id,
                o.title,
                o.opportunity_type,
                o.description,
                o.required_skills,
                o.eligibility_criteria,
                o.location,
                o.work_mode,
                o.stipend,
                o.package,
                o.application_deadline,
                o.status,
                o.created_at,
                o.updated_at,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.email AS industry_email

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            ORDER BY o.created_at DESC
        """)

        opportunities = cursor.fetchall()

        # -------------------------------------------------
        # FETCH INDUSTRIES FOR FILTER
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                company_name
            FROM industries
            ORDER BY company_name ASC
        """)

        industries = cursor.fetchall()

        return render_template(
            "admin/opportunities.html",
            opportunities=opportunities,
            industries=industries
        )

    except Exception as e:

        print("OPPORTUNITIES ERROR:", e)

        return "Error loading opportunities", 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# OPPORTUNITY DETAILS
# =========================================================

@app.route("/admin/opportunities/<opportunity_id>")
def admin_opportunity_details(opportunity_id):

    # Admin access check
    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # FETCH OPPORTUNITY DETAILS
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                o.id,
                o.industry_id,
                o.title,
                o.opportunity_type,
                o.description,
                o.required_skills,
                o.eligibility_criteria,
                o.location,
                o.work_mode,
                o.stipend,
                o.package,
                o.application_deadline,
                o.status,
                o.created_at,
                o.updated_at,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.email AS industry_email

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE o.id = %s
        """, (opportunity_id,))

        opportunity = cursor.fetchone()

        # -------------------------------------------------
        # OPPORTUNITY NOT FOUND
        # -------------------------------------------------
        if not opportunity:
            return "Opportunity not found", 404

        return render_template(
            "admin/opportunity-details.html",
            opportunity=opportunity
        )

    except Exception as e:

        print("OPPORTUNITY DETAILS ERROR:", e)

        return "Error loading opportunity details", 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# REPORTS
# =========================================================

@app.route("/admin/reports")
def admin_reports():

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =====================================================
        # 1. STUDENT BRANCH-WISE DISTRIBUTION
        # =====================================================

        cursor.execute("""
            SELECT
                COALESCE(branch, 'Other') AS branch,
                COUNT(*) AS total
            FROM students
            GROUP BY branch
            ORDER BY total DESC
        """)

        student_distribution = cursor.fetchall()


        # =====================================================
        # 2. COLLABORATION STATUS
        # =====================================================

        cursor.execute("""
            SELECT
                status,
                COUNT(*) AS total
            FROM collaborations
            GROUP BY status
        """)

        collaboration_rows = cursor.fetchall()

        collaboration_status = {
            "ACTIVE": 0,
            "PENDING": 0,
            "COMPLETED": 0,
            "REJECTED": 0
        }

        for row in collaboration_rows:

            status = row["status"]

            if status in collaboration_status:
                collaboration_status[status] = row["total"]


        # =====================================================
        # 3. OPPORTUNITY STATUS
        # =====================================================

        cursor.execute("""
            SELECT
                status,
                COUNT(*) AS total
            FROM opportunities
            GROUP BY status
        """)

        opportunity_rows = cursor.fetchall()

        opportunity_status = {
            "OPEN": 0,
            "DRAFT": 0,
            "CLOSED": 0,
            "CANCELLED": 0
        }

        for row in opportunity_rows:

            status = row["status"]

            if status in opportunity_status:
                opportunity_status[status] = row["total"]


        # =====================================================
        # 4. ACTIVE INDUSTRIES
        # =====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM industries
            WHERE status = 'ACTIVE'
        """)

        active_industries = cursor.fetchone()["total"]


        # =====================================================
        # 5. TOTAL INDUSTRY PROJECTS
        # =====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_projects
        """)

        industry_projects = cursor.fetchone()["total"]


        # =====================================================
        # 6. TOTAL OPPORTUNITIES
        # =====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
        """)

        total_opportunities = cursor.fetchone()["total"]


        # =====================================================
        # 7. TOTAL COLLABORATIONS
        # =====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
        """)

        total_collaborations = cursor.fetchone()["total"]


        # =====================================================
        # 8. TOTAL STUDENTS
        # =====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
        """)

        total_students = cursor.fetchone()["total"]


        return render_template(
            "admin/reports.html",

            student_distribution=student_distribution,

            collaboration_status=collaboration_status,

            opportunity_status=opportunity_status,

            active_industries=active_industries,

            industry_projects=industry_projects,

            total_opportunities=total_opportunities,

            total_collaborations=total_collaborations,

            total_students=total_students
        )


    except Exception as e:

        print("REPORTS ERROR:", e)

        return "Error loading reports", 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# NOTIFICATION HELPERS
# =========================================================

def get_admin_notifications():

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        notifications = []

        # =====================================================
        # 1. RECENT STUDENT REGISTRATIONS
        # =====================================================

        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.created_at
            FROM students s
            ORDER BY s.created_at DESC
            LIMIT 10
        """)

        students = cursor.fetchall()

        for student in students:

            notifications.append({
                "category": "registration",
                "type": "normal",
                "icon": "🎓",
                "title": "New student registration",
                "description": (
                    f"Student {student['enrollment_no']} "
                    "has been registered on the portal."
                ),
                "meta": "Student Registration",
                "created_at": student["created_at"],
                "read": True,
                "url": f"/admin/students/{student['id']}"
            })


        # =====================================================
        # 2. PENDING COLLEGE REGISTRATIONS
        # =====================================================

        cursor.execute("""
            SELECT
                id,
                college_name,
                created_at
            FROM colleges
            WHERE status = 'PENDING'
            ORDER BY created_at DESC
        """)

        pending_colleges = cursor.fetchall()

        for college in pending_colleges:

            notifications.append({
                "category": "registration",
                "type": "important",
                "icon": "🏫",
                "title": "Pending college registration",
                "description": (
                    f"{college['college_name']} "
                    "is waiting for administrative review."
                ),
                "meta": "College Registration",
                "created_at": college["created_at"],
                "read": False,
                "url": f"/admin/colleges/{college['id']}"
            })


        # =====================================================
        # 3. PENDING PLACEMENT CELL REGISTRATIONS
        # =====================================================

        cursor.execute("""
            SELECT
                pc.id,
                pc.created_at,
                c.college_name
            FROM placement_cells pc
            INNER JOIN colleges c
                ON pc.college_id = c.id
            WHERE pc.status = 'PENDING'
            ORDER BY pc.created_at DESC
        """)

        pending_placement_cells = cursor.fetchall()

        for placement_cell in pending_placement_cells:

            notifications.append({
                "category": "registration",
                "type": "important",
                "icon": "🎓",
                "title": "Pending placement cell registration",
                "description": (
                    f"{placement_cell['college_name']} "
                    "placement cell is waiting for review."
                ),
                "meta": "Placement Cell Registration",
                "created_at": placement_cell["created_at"],
                "read": False,
                "url": (
                    f"/admin/placement-cells/"
                    f"{placement_cell['id']}"
                )
            })


        # =====================================================
        # 4. PENDING INDUSTRY REGISTRATIONS
        # =====================================================

        cursor.execute("""
            SELECT
                id,
                company_name,
                created_at
            FROM industries
            WHERE status = 'PENDING'
            ORDER BY created_at DESC
        """)

        pending_industries = cursor.fetchall()

        for industry in pending_industries:

            notifications.append({
                "category": "registration",
                "type": "important",
                "icon": "🏭",
                "title": "Pending industry registration",
                "description": (
                    f"{industry['company_name']} "
                    "is waiting for administrative review."
                ),
                "meta": "Industry Registration",
                "created_at": industry["created_at"],
                "read": False,
                "url": f"/admin/industries/{industry['id']}"
            })


        # =====================================================
        # 5. RECENT COLLABORATIONS
        # =====================================================

        cursor.execute("""
            SELECT
                col.id,
                col.title,
                col.created_at,
                c.college_name,
                i.company_name
            FROM collaborations col
            INNER JOIN colleges c
                ON col.college_id = c.id
            INNER JOIN industries i
                ON col.industry_id = i.id
            ORDER BY col.created_at DESC
            LIMIT 10
        """)

        collaborations = cursor.fetchall()

        for collaboration in collaborations:

            notifications.append({
                "category": "collaboration",
                "type": "normal",
                "icon": "🤝",
                "title": "New collaboration activity",
                "description": (
                    f"{collaboration['title']} between "
                    f"{collaboration['college_name']} and "
                    f"{collaboration['company_name']}."
                ),
                "meta": "Collaboration",
                "created_at": collaboration["created_at"],
                "read": True,
                "url": (
                    f"/admin/collaborations/"
                    f"{collaboration['id']}"
                )
            })


        # =====================================================
        # 6. RECENT OPPORTUNITIES
        # =====================================================

        cursor.execute("""
            SELECT
                o.id,
                o.title,
                o.created_at,
                i.company_name
            FROM opportunities o
            INNER JOIN industries i
                ON o.industry_id = i.id
            ORDER BY o.created_at DESC
            LIMIT 10
        """)

        opportunities = cursor.fetchall()

        for opportunity in opportunities:

            notifications.append({
                "category": "opportunity",
                "type": "normal",
                "icon": "💼",
                "title": "New opportunity published",
                "description": (
                    f"{opportunity['company_name']} added "
                    f"{opportunity['title']}."
                ),
                "meta": "Opportunity",
                "created_at": opportunity["created_at"],
                "read": True,
                "url": (
                    f"/admin/opportunities/"
                    f"{opportunity['id']}"
                )
            })


        # =====================================================
        # SORT
        # =====================================================

        notifications.sort(
            key=lambda item: (
                item["created_at"] is not None,
                item["created_at"]
            ),
            reverse=True
        )

        return notifications[:30]


    except Exception as e:

        print("GET ADMIN NOTIFICATIONS ERROR:", e)

        return []


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()



# =========================================================
# GLOBAL NOTIFICATION DATA
# =========================================================

@app.context_processor
def inject_notification_data():

    if session.get("role") != "ADMIN":
        return {}

    notifications = get_admin_notifications()

    unread_notification_count = sum(
        1
        for notification in notifications
        if not notification["read"]
    )

    navbar_notifications = notifications[:5]

    return {
        "navbar_notifications": navbar_notifications,
        "unread_notification_count": unread_notification_count
    }



# =========================================================
# NOTIFICATIONS PAGE
# =========================================================

@app.route("/admin/notifications")
def admin_notifications():

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    notifications = get_admin_notifications()

    return render_template(
        "admin/notifications.html",
        notifications=notifications
    )

# =========================================================
# ADMIN SETTINGS
# =========================================================

@app.route("/admin/settings")
def admin_settings():

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        admin_id = session.get("user_id")

        # Admin profile
        cursor.execute("""
            SELECT id, name, email, role, status
            FROM users
            WHERE id = %s
        """, (admin_id,))

        admin = cursor.fetchone()

        if not admin:
            return "Admin account not found", 404

        # Existing settings
        cursor.execute("""
            SELECT
                notify_registrations,
                notify_collaborations,
                notify_opportunities,
                theme_preference
            FROM admin_settings
            WHERE user_id = %s
        """, (admin_id,))

        settings = cursor.fetchone()

        # Create default settings if not available
        if not settings:

            cursor.execute("""
                INSERT INTO admin_settings (
                    user_id,
                    notify_registrations,
                    notify_collaborations,
                    notify_opportunities,
                    theme_preference
                )
                VALUES (%s, TRUE, TRUE, TRUE, 'light')
            """, (admin_id,))

            conn.commit()

            settings = {
                "notify_registrations": True,
                "notify_collaborations": True,
                "notify_opportunities": True,
                "theme_preference": "light"
            }

        return render_template(
            "admin/settings.html",
            admin=admin,
            settings=settings
        )

    except Exception as e:

        print("ADMIN SETTINGS ERROR:", e)

        return "Error loading settings", 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# UPDATE ADMIN PROFILE
# =========================================================

@app.route("/admin/settings/profile", methods=["POST"])
def update_admin_profile():

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        admin_id = session.get("user_id")

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            return {
                "success": False,
                "message": "Name and email are required."
            }, 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET name = %s,
                email = %s
            WHERE id = %s
        """, (name, email, admin_id))

        conn.commit()

        # Update current session
        session["user_name"] = name
        session["user_email"] = email

        return {
            "success": True,
            "message": "Profile updated successfully."
        }

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("UPDATE PROFILE ERROR:", e)

        return {
            "success": False,
            "message": "Email may already be in use."
        }, 400

    except Exception as e:

        if conn:
            conn.rollback()

        print("UPDATE PROFILE ERROR:", e)

        return {
            "success": False,
            "message": "Unable to update profile."
        }, 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# CHANGE ADMIN PASSWORD
# =========================================================

@app.route("/admin/settings/password", methods=["POST"])
def change_admin_password():

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        admin_id = session.get("user_id")

        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not current_password:
            return {
                "success": False,
                "message": "Current password is required."
            }, 400

        if not new_password:
            return {
                "success": False,
                "message": "New password is required."
            }, 400

        if len(new_password) < 6:
            return {
                "success": False,
                "message": "Password must be at least 6 characters."
            }, 400

        if new_password != confirm_password:
            return {
                "success": False,
                "message": "New passwords do not match."
            }, 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT password
            FROM users
            WHERE id = %s
        """, (admin_id,))

        admin = cursor.fetchone()

        if not admin:
            return {
                "success": False,
                "message": "Admin account not found."
            }, 404

        # Current project stores passwords directly.
        if admin["password"] != current_password:
            return {
                "success": False,
                "message": "Current password is incorrect."
            }, 400

        cursor.execute("""
            UPDATE users
            SET password = %s
            WHERE id = %s
        """, (new_password, admin_id))

        conn.commit()

        return {
            "success": True,
            "message": "Password changed successfully."
        }

    except Exception as e:

        if conn:
            conn.rollback()

        print("CHANGE PASSWORD ERROR:", e)

        return {
            "success": False,
            "message": "Unable to change password."
        }, 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# UPDATE NOTIFICATION PREFERENCES
# =========================================================

@app.route("/admin/settings/notifications", methods=["POST"])
def update_notification_preferences():

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        admin_id = session.get("user_id")

        notify_registrations = (
            request.form.get("notify_registrations") == "true"
        )

        notify_collaborations = (
            request.form.get("notify_collaborations") == "true"
        )

        notify_opportunities = (
            request.form.get("notify_opportunities") == "true"
        )

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO admin_settings (
                user_id,
                notify_registrations,
                notify_collaborations,
                notify_opportunities
            )
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                notify_registrations = VALUES(notify_registrations),
                notify_collaborations = VALUES(notify_collaborations),
                notify_opportunities = VALUES(notify_opportunities)
        """, (
            admin_id,
            notify_registrations,
            notify_collaborations,
            notify_opportunities
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Notification preferences saved."
        }

    except Exception as e:

        if conn:
            conn.rollback()

        print("NOTIFICATION SETTINGS ERROR:", e)

        return {
            "success": False,
            "message": "Unable to save notification preferences."
        }, 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# UPDATE THEME
# =========================================================

@app.route("/admin/settings/appearance", methods=["POST"])
def update_admin_appearance():

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))

    conn = None
    cursor = None

    try:

        admin_id = session.get("user_id")

        theme = request.form.get(
            "theme",
            "light"
        ).strip().lower()

        if theme not in ["light", "dark"]:
            return {
                "success": False,
                "message": "Invalid theme selected."
            }, 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO admin_settings (
                user_id,
                theme_preference
            )
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                theme_preference = VALUES(theme_preference)
        """, (
            admin_id,
            theme
        ))

        conn.commit()

        return {
            "success": True,
            "message": "Appearance preference saved."
        }

    except Exception as e:

        if conn:
            conn.rollback()

        print("APPEARANCE SETTINGS ERROR:", e)

        return {
            "success": False,
            "message": "Unable to save appearance preference."
        }, 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()   

# =========================================================
# ADMIN PROFILE
# =========================================================

# =========================================================
# PROFILE IMAGE CONFIGURATION
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB


# =========================================================
# CHECK ALLOWED IMAGE
# =========================================================

def allowed_image(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_IMAGE_EXTENSIONS


# =========================================================
# DELETE OLD IMAGE FILE
# =========================================================

def delete_admin_image(image_path):

    if not image_path:
        return

    try:

        # Example:
        # /static/uploads/admin/profile_xxx.jpg
        relative_path = image_path.lstrip("/")

        file_path = os.path.join(
            app.root_path,
            relative_path
        )

        if os.path.isfile(file_path):

            os.remove(file_path)

            print(
                "Deleted old image:",
                file_path
            )

    except Exception as e:

        print(
            "IMAGE DELETE ERROR:",
            e
        )


# =========================================================
# ADMIN PROFILE PAGE
# =========================================================

@app.route("/admin/profile")
def admin_profile():

    # -----------------------------------------------------
    # ADMIN ONLY
    # -----------------------------------------------------

    if session.get("role") != "ADMIN":
        return redirect(url_for("login"))


    conn = None
    cursor = None


    try:

        admin_id = session.get("user_id")


        if not admin_id:
            return redirect(url_for("login"))


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # GET ADMIN
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                status,
                created_at,
                profile_image,
                cover_image
            FROM users
            WHERE id = %s
              AND role = 'ADMIN'
        """, (
            admin_id,
        ))


        admin = cursor.fetchone()


        if not admin:

            return (
                "Admin profile not found",
                404
            )


        # -------------------------------------------------
        # PROFILE PAGE
        # -------------------------------------------------

        return render_template(
            "admin/admin-profile.html",
            admin=admin
        )


    except Exception as e:

        print(
            "ADMIN PROFILE ERROR:",
            e
        )

        return (
            "Error loading admin profile",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# UPLOAD ADMIN PROFILE / COVER IMAGE
# =========================================================

@app.route(
    "/admin/profile/upload-images",
    methods=["POST"]
)
def upload_admin_profile_images():

    # -----------------------------------------------------
    # ADMIN ONLY
    # -----------------------------------------------------

    if session.get("role") != "ADMIN":

        return {
            "success": False,
            "message": "Unauthorized access."
        }, 403


    conn = None
    cursor = None


    try:

        admin_id = session.get("user_id")


        if not admin_id:

            return {
                "success": False,
                "message": "Admin session expired."
            }, 401


        # -------------------------------------------------
        # FILES
        # -------------------------------------------------

        profile_file = request.files.get(
            "profile_image"
        )

        cover_file = request.files.get(
            "cover_image"
        )


        if (
            not profile_file
            and not cover_file
        ):

            return {
                "success": False,
                "message": "Please select an image."
            }, 400


        # -------------------------------------------------
        # UPLOAD DIRECTORY
        # -------------------------------------------------

        upload_folder = os.path.join(
            app.root_path,
            "static",
            "uploads",
            "admin"
        )


        os.makedirs(
            upload_folder,
            exist_ok=True
        )


        # -------------------------------------------------
        # GET OLD IMAGES
        # -------------------------------------------------

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT
                profile_image,
                cover_image
            FROM users
            WHERE id = %s
              AND role = 'ADMIN'
        """, (
            admin_id,
        ))


        admin = cursor.fetchone()


        if not admin:

            return {
                "success": False,
                "message": "Admin account not found."
            }, 404


        old_profile_image = admin[
            "profile_image"
        ]

        old_cover_image = admin[
            "cover_image"
        ]


        new_profile_image = None
        new_cover_image = None


        # =================================================
        # PROFILE IMAGE
        # =================================================

        if (
            profile_file
            and profile_file.filename
        ):

            # ---------------------------------------------
            # EXTENSION CHECK
            # ---------------------------------------------

            if not allowed_image(
                profile_file.filename
            ):

                return {
                    "success": False,
                    "message": (
                        "Invalid profile image format. "
                        "Use JPG, JPEG, PNG or WEBP."
                    )
                }, 400


            # ---------------------------------------------
            # FILE SIZE CHECK
            # ---------------------------------------------

            profile_file.seek(
                0,
                os.SEEK_END
            )

            profile_size = profile_file.tell()

            profile_file.seek(0)


            if profile_size > MAX_IMAGE_SIZE:

                return {
                    "success": False,
                    "message": (
                        "Profile image must be "
                        "5 MB or smaller."
                    )
                }, 400


            # ---------------------------------------------
            # SAFE EXTENSION
            # ---------------------------------------------

            extension = (
                profile_file
                .filename
                .rsplit(".", 1)[1]
                .lower()
            )


            # ---------------------------------------------
            # UNIQUE FILE NAME
            # ---------------------------------------------

            filename = (
                "profile_"
                + str(uuid.uuid4())
                + "."
                + extension
            )


            filename = secure_filename(
                filename
            )


            file_path = os.path.join(
                upload_folder,
                filename
            )


            # ---------------------------------------------
            # SAVE
            # ---------------------------------------------

            profile_file.save(
                file_path
            )


            new_profile_image = (
                "/static/uploads/admin/"
                + filename
            )


        # =================================================
        # COVER IMAGE
        # =================================================

        if (
            cover_file
            and cover_file.filename
        ):

            # ---------------------------------------------
            # EXTENSION CHECK
            # ---------------------------------------------

            if not allowed_image(
                cover_file.filename
            ):

                return {
                    "success": False,
                    "message": (
                        "Invalid cover image format. "
                        "Use JPG, JPEG, PNG or WEBP."
                    )
                }, 400


            # ---------------------------------------------
            # FILE SIZE CHECK
            # ---------------------------------------------

            cover_file.seek(
                0,
                os.SEEK_END
            )

            cover_size = cover_file.tell()

            cover_file.seek(0)


            if cover_size > MAX_IMAGE_SIZE:

                return {
                    "success": False,
                    "message": (
                        "Cover image must be "
                        "5 MB or smaller."
                    )
                }, 400


            # ---------------------------------------------
            # EXTENSION
            # ---------------------------------------------

            extension = (
                cover_file
                .filename
                .rsplit(".", 1)[1]
                .lower()
            )


            # ---------------------------------------------
            # UNIQUE FILE NAME
            # ---------------------------------------------

            filename = (
                "cover_"
                + str(uuid.uuid4())
                + "."
                + extension
            )


            filename = secure_filename(
                filename
            )


            file_path = os.path.join(
                upload_folder,
                filename
            )


            # ---------------------------------------------
            # SAVE
            # ---------------------------------------------

            cover_file.save(
                file_path
            )


            new_cover_image = (
                "/static/uploads/admin/"
                + filename
            )


        # =================================================
        # DATABASE UPDATE
        # =================================================

        if (
            new_profile_image
            and new_cover_image
        ):

            cursor.execute("""
                UPDATE users
                SET
                    profile_image = %s,
                    cover_image = %s
                WHERE id = %s
                  AND role = 'ADMIN'
            """, (
                new_profile_image,
                new_cover_image,
                admin_id
            ))


        elif new_profile_image:

            cursor.execute("""
                UPDATE users
                SET
                    profile_image = %s
                WHERE id = %s
                  AND role = 'ADMIN'
            """, (
                new_profile_image,
                admin_id
            ))


        elif new_cover_image:

            cursor.execute("""
                UPDATE users
                SET
                    cover_image = %s
                WHERE id = %s
                  AND role = 'ADMIN'
            """, (
                new_cover_image,
                admin_id
            ))


        conn.commit()


        # =================================================
        # DELETE OLD FILES
        # =================================================

        if (
            new_profile_image
            and old_profile_image
            and old_profile_image != new_profile_image
        ):

            delete_admin_image(
                old_profile_image
            )


        if (
            new_cover_image
            and old_cover_image
            and old_cover_image != new_cover_image
        ):

            delete_admin_image(
                old_cover_image
            )


        # =================================================
        # RESPONSE
        # =================================================

        return {
            "success": True,
            "message": (
                "Profile images updated successfully."
            ),
            "profile_image": new_profile_image,
            "cover_image": new_cover_image
        }


    except Exception as e:

        if conn:
            conn.rollback()


        print(
            "ADMIN IMAGE UPLOAD ERROR:",
            e
        )


        return {
            "success": False,
            "message": (
                "Unable to upload profile images."
            )
        }, 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# REMOVE ADMIN COVER IMAGE
# =========================================================

@app.route(
    "/admin/profile/remove-cover",
    methods=["POST"]
)
def remove_admin_cover():

    # -----------------------------------------------------
    # ADMIN ONLY
    # -----------------------------------------------------

    if session.get("role") != "ADMIN":

        return {
            "success": False,
            "message": "Unauthorized access."
        }, 403


    conn = None
    cursor = None


    try:

        admin_id = session.get("user_id")


        if not admin_id:

            return {
                "success": False,
                "message": "Admin session expired."
            }, 401


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # -------------------------------------------------
        # GET CURRENT COVER
        # -------------------------------------------------

        cursor.execute("""
            SELECT cover_image
            FROM users
            WHERE id = %s
              AND role = 'ADMIN'
        """, (
            admin_id,
        ))


        admin = cursor.fetchone()


        if not admin:

            return {
                "success": False,
                "message": "Admin account not found."
            }, 404


        old_cover_image = admin[
            "cover_image"
        ]


        # -------------------------------------------------
        # NOTHING TO REMOVE
        # -------------------------------------------------

        if not old_cover_image:

            return {
                "success": True,
                "message": "No cover image to remove."
            }


        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        cursor.execute("""
            UPDATE users
            SET cover_image = NULL
            WHERE id = %s
              AND role = 'ADMIN'
        """, (
            admin_id,
        ))


        conn.commit()


        # -------------------------------------------------
        # DELETE FILE
        # -------------------------------------------------

        delete_admin_image(
            old_cover_image
        )


        return {
            "success": True,
            "message": (
                "Cover image removed successfully."
            )
        }


    except Exception as e:

        if conn:
            conn.rollback()


        print(
            "REMOVE COVER ERROR:",
            e
        )


        return {
            "success": False,
            "message": (
                "Unable to remove cover image."
            )
        }, 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# REGISTRATION
# =========================================================

@app.route("/register")
def register():

    return render_template(
        "register/register.html"
    )


# =========================================================
# ROLE REGISTRATION
# =========================================================

@app.route(
    "/register/<role>",
    methods=["GET", "POST"]
)
def register_user(role):

    allowed_roles = {
        "student": "STUDENT",
        "college": "COLLEGE",
        "placement-cell": "PLACEMENT_CELL",
        "industry": "INDUSTRY"
    }


    # =====================================================
    # CHECK ROLE
    # =====================================================

    if role not in allowed_roles:

        flash(
            "Invalid registration type.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    assigned_role = allowed_roles[role]


    # =====================================================
    # STUDENT REGISTRATION
    # =====================================================

    if role == "student":

        conn = None
        cursor = None

        try:

            conn = get_db_connection()

            cursor = conn.cursor(
                dictionary=True
            )


            # =================================================
            # GET ACTIVE COLLEGES
            # =================================================

            cursor.execute("""
                SELECT
                    id,
                    college_name,
                    college_code
                FROM colleges
                WHERE status = 'ACTIVE'
                ORDER BY college_name ASC
            """)

            colleges = cursor.fetchall()


            # =================================================
            # GET REQUEST DATA
            # =================================================

            if request.method == "POST":

                # -------------------------------------------------
                # ACCOUNT INFORMATION
                # -------------------------------------------------

                name = request.form.get(
                    "name",
                    ""
                ).strip()

                email = request.form.get(
                    "email",
                    ""
                ).strip().lower()

                password = request.form.get(
                    "password",
                    ""
                )

                confirm_password = request.form.get(
                    "confirm_password",
                    ""
                )


                # -------------------------------------------------
                # STUDENT INFORMATION
                # -------------------------------------------------

                college_id = request.form.get(
                    "college_id",
                    ""
                ).strip()

                enrollment_no = request.form.get(
                    "enrollment_no",
                    ""
                ).strip()

                course = request.form.get(
                    "course",
                    ""
                ).strip()

                branch = request.form.get(
                    "branch",
                    ""
                ).strip()

                semester = request.form.get(
                    "semester",
                    ""
                ).strip()

                passing_year = request.form.get(
                    "passing_year",
                    ""
                ).strip()


                # -------------------------------------------------
                # PERSONAL INFORMATION
                # -------------------------------------------------

                phone = request.form.get(
                    "phone",
                    ""
                ).strip()

                dob = request.form.get(
                    "dob",
                    ""
                ).strip()

                # -------------------------------------------------
                # DOB VALIDATION
                # -------------------------------------------------

                if dob:

                    from datetime import datetime

                    try:

                        parsed_dob = datetime.strptime(
                            dob,
                            "%Y-%m-%d"
                        ).date()

                        current_year = datetime.now().year

                        if parsed_dob.year < 1950 or parsed_dob.year > current_year:

                            flash(
                                "Please enter a valid date of birth.",
                                "error"
                            )

                            return render_template(
                                "register/student_register.html",
                                colleges=colleges
                            )

                    except ValueError:

                        flash(
                            "Please enter a valid date of birth.",
                            "error"
                        )

                        return render_template(
                            "register/student_register.html",
                            colleges=colleges
                        )

                gender = request.form.get(
                    "gender",
                    ""
                ).strip()

                address = request.form.get(
                    "address",
                    ""
                ).strip()


                # -------------------------------------------------
                # ACADEMIC INFORMATION
                # -------------------------------------------------

                cgpa = request.form.get(
                    "cgpa",
                    ""
                ).strip()

                current_sgpa = request.form.get(
                    "current_sgpa",
                    ""
                ).strip()

                active_backlogs = request.form.get(
                    "active_backlogs",
                    "0"
                ).strip()


                # -------------------------------------------------
                # PROFESSIONAL LINKS
                # -------------------------------------------------

                linkedin_url = request.form.get(
                    "linkedin_url",
                    ""
                ).strip()

                github_url = request.form.get(
                    "github_url",
                    ""
                ).strip()

                portfolio_url = request.form.get(
                    "portfolio_url",
                    ""
                ).strip()


                # =================================================
                # BASIC VALIDATION
                # =================================================

                if not name:

                    flash(
                        "Full name is required.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                if len(name) < 2:

                    flash(
                        "Name must contain at least 2 characters.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                if len(name) > 100:

                    flash(
                        "Name cannot exceed 100 characters.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                # =================================================
                # EMAIL VALIDATION
                # =================================================

                email_pattern = (
                    r"^[A-Za-z0-9._%+-]+@"
                    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
                )


                if not email:

                    flash(
                        "Email address is required.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                if not re.match(
                    email_pattern,
                    email
                ):

                    flash(
                        "Please enter a valid email address.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                # =================================================
                # PASSWORD VALIDATION
                # =================================================

                if len(password) < 6:

                    flash(
                        "Password must be at least 6 characters.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                if password != confirm_password:

                    flash(
                        "Passwords do not match.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                # =================================================
                # STUDENT REQUIRED FIELDS
                # =================================================

                if not college_id:

                    flash(
                        "Please select your college.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                if not enrollment_no:

                    flash(
                        "Enrollment number is required.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                if not course:

                    flash(
                        "Course is required.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                if not branch:

                    flash(
                        "Branch is required.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                # =================================================
                # DUPLICATE EMAIL
                # =================================================

                cursor.execute("""
                    SELECT id
                    FROM users
                    WHERE email = %s
                    LIMIT 1
                """, (
                    email,
                ))

                existing_user = cursor.fetchone()


                if existing_user:

                    flash(
                        "An account with this email already exists.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                # =================================================
                # DUPLICATE ENROLLMENT
                # =================================================

                cursor.execute("""
                    SELECT id
                    FROM students
                    WHERE enrollment_no = %s
                    LIMIT 1
                """, (
                    enrollment_no,
                ))

                existing_student = cursor.fetchone()


                if existing_student:

                    flash(
                        "This enrollment number is already registered.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                # =================================================
                # VERIFY COLLEGE
                # =================================================

                cursor.execute("""
                    SELECT id
                    FROM colleges
                    WHERE id = %s
                      AND status = 'ACTIVE'
                    LIMIT 1
                """, (
                    college_id,
                ))

                selected_college = cursor.fetchone()


                if not selected_college:

                    flash(
                        "Selected college is not available.",
                        "error"
                    )

                    return render_template(
                        "register/student_register.html",
                        colleges=colleges
                    )


                # =================================================
                # GENERATE IDS
                # =================================================

                user_id = str(
                    uuid.uuid4()
                )

                student_id = str(
                    uuid.uuid4()
                )


                # =================================================
                # HASH PASSWORD
                # =================================================

                hashed_password = generate_password_hash(
                    password
                )


                # =================================================
                # INSERT USER
                # =================================================

                cursor.execute("""
                    INSERT INTO users (
                        id,
                        name,
                        email,
                        password,
                        role,
                        status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """, (
                    user_id,
                    name,
                    email,
                    hashed_password,
                    assigned_role,
                    "ACTIVE"
                ))


                # =================================================
                # INSERT STUDENT
                # =================================================

                cursor.execute("""
                    INSERT INTO students (
                        id,
                        user_id,
                        college_id,
                        enrollment_no,
                        course,
                        branch,
                        semester,
                        passing_year,
                        phone,
                        dob,
                        gender,
                        address,
                        cgpa,
                        current_sgpa,
                        active_backlogs,
                        linkedin_url,
                        github_url,
                        portfolio_url
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        %s,
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, '')
                    )
                """, (
                    student_id,
                    user_id,
                    college_id,
                    enrollment_no,
                    course,
                    branch,
                    semester,
                    passing_year,
                    phone,
                    dob,
                    gender,
                    address,
                    cgpa,
                    current_sgpa,
                    active_backlogs or 0,
                    linkedin_url,
                    github_url,
                    portfolio_url
                ))


                # =================================================
                # COMMIT BOTH INSERTS
                # =================================================

                conn.commit()


                # =================================================
                # SUCCESS
                # =================================================

                flash(
                    "Student registration successful. You can now login.",
                    "success"
                )

                return redirect(
                    url_for("login")
                )


            # =====================================================
            # GET REQUEST
            # =====================================================

            return render_template(
                "register/student_register.html",
                colleges=colleges
            )


        # =========================================================
        # DATABASE ERROR
        # =========================================================

        except mysql.connector.Error as e:

            if conn:
                conn.rollback()

            print("=" * 70)
            print("STUDENT REGISTRATION DATABASE ERROR:")
            print(type(e).__name__)
            print(e)
            print("=" * 70)

            flash(
                "Unable to complete student registration.",
                "error"
            )

            return render_template(
                "register/student_register.html",
                colleges=colleges if "colleges" in locals() else []
            )


        # =========================================================
        # GENERAL ERROR
        # =========================================================

        except Exception as e:

            if conn:
                conn.rollback()

            print("=" * 70)
            print("STUDENT REGISTRATION ERROR:")
            print(type(e).__name__)
            print(e)
            print("=" * 70)

            flash(
                "Unable to complete student registration.",
                "error"
            )

            return render_template(
                "register/student_register.html",
                colleges=colleges if "colleges" in locals() else []
            )


        # =========================================================
        # CLOSE DATABASE
        # =========================================================

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

    # =====================================================
    # COLLEGE REGISTRATION
    # =====================================================

    if role == "college":

        conn = None
        cursor = None

        try:

            conn = get_db_connection()

            cursor = conn.cursor(
                dictionary=True
            )


            # =================================================
            # POST REQUEST
            # =================================================

            if request.method == "POST":

                # -------------------------------------------------
                # ACCOUNT
                # -------------------------------------------------

                name = request.form.get(
                    "name",
                    ""
                ).strip()

                email = request.form.get(
                    "email",
                    ""
                ).strip().lower()

                password = request.form.get(
                    "password",
                    ""
                )

                confirm_password = request.form.get(
                    "confirm_password",
                    ""
                )


                # -------------------------------------------------
                # COLLEGE
                # -------------------------------------------------

                college_name = request.form.get(
                    "college_name",
                    ""
                ).strip()

                college_code = request.form.get(
                    "college_code",
                    ""
                ).strip().upper()

                university_name = request.form.get(
                    "university_name",
                    ""
                ).strip()

                college_email = request.form.get(
                    "college_email",
                    ""
                ).strip().lower()


                # -------------------------------------------------
                # CONTACT
                # -------------------------------------------------

                phone = request.form.get(
                    "phone",
                    ""
                ).strip()

                address = request.form.get(
                    "address",
                    ""
                ).strip()

                city = request.form.get(
                    "city",
                    ""
                ).strip()

                state = request.form.get(
                    "state",
                    ""
                ).strip()

                pincode = request.form.get(
                    "pincode",
                    ""
                ).strip()

                website = request.form.get(
                    "website",
                    ""
                ).strip()


                # =================================================
                # NAME VALIDATION
                # =================================================

                if len(name) < 2:

                    flash(
                        "Please enter a valid contact person name.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                if len(name) > 100:

                    flash(
                        "Name cannot exceed 100 characters.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                # =================================================
                # EMAIL VALIDATION
                # =================================================

                email_pattern = (
                    r"^[A-Za-z0-9._%+-]+@"
                    r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
                )


                if not re.match(
                    email_pattern,
                    email
                ):

                    flash(
                        "Please enter a valid email address.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                # =================================================
                # PASSWORD
                # =================================================

                if len(password) < 6:

                    flash(
                        "Password must be at least 6 characters.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                if password != confirm_password:

                    flash(
                        "Passwords do not match.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                # =================================================
                # COLLEGE REQUIRED FIELDS
                # =================================================

                if not college_name:

                    flash(
                        "College name is required.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                if len(college_name) > 200:

                    flash(
                        "College name cannot exceed 200 characters.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                if not college_code:

                    flash(
                        "College code is required.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                # =================================================
                # COLLEGE EMAIL VALIDATION
                # =================================================

                if (
                    college_email and
                    not re.match(
                        email_pattern,
                        college_email
                    )
                ):

                    flash(
                        "Please enter a valid college email address.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                # =================================================
                # DUPLICATE USER EMAIL
                # =================================================

                cursor.execute("""
                    SELECT id
                    FROM users
                    WHERE email = %s
                    LIMIT 1
                """, (
                    email,
                ))

                existing_user = cursor.fetchone()


                if existing_user:

                    flash(
                        "An account with this email already exists.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                # =================================================
                # DUPLICATE COLLEGE CODE
                # =================================================

                cursor.execute("""
                    SELECT id
                    FROM colleges
                    WHERE college_code = %s
                    LIMIT 1
                """, (
                    college_code,
                ))

                existing_college = cursor.fetchone()


                if existing_college:

                    flash(
                        "This college code is already registered.",
                        "error"
                    )

                    return render_template(
                        "register/college_register.html"
                    )


                # =================================================
                # GENERATE UUIDs
                # =================================================

                user_id = str(
                    uuid.uuid4()
                )

                college_id = str(
                    uuid.uuid4()
                )


                # =================================================
                # HASH PASSWORD
                # =================================================

                hashed_password = generate_password_hash(
                    password
                )


                # =================================================
                # INSERT USER
                # =================================================

                cursor.execute("""
                    INSERT INTO users (
                        id,
                        name,
                        email,
                        password,
                        role,
                        status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """, (
                    user_id,
                    name,
                    email,
                    hashed_password,
                    "COLLEGE",
                    "ACTIVE"
                ))


                # =================================================
                # INSERT COLLEGE
                # =================================================

                cursor.execute("""
                    INSERT INTO colleges (
                        id,
                        user_id,
                        college_name,
                        college_code,
                        university_name,
                        email,
                        phone,
                        address,
                        city,
                        state,
                        pincode,
                        website,
                        status
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        NULLIF(%s, ''),
                        %s
                    )
                """, (
                    college_id,
                    user_id,
                    college_name,
                    college_code,
                    university_name,
                    college_email,
                    phone,
                    address,
                    city,
                    state,
                    pincode,
                    website,
                    "ACTIVE"
                ))


                # =================================================
                # COMMIT
                # =================================================

                conn.commit()


                # =================================================
                # SUCCESS
                # =================================================

                flash(
                    "College registration successful. You can now login.",
                    "success"
                )

                return redirect(
                    url_for("login")
                )


            # =================================================
            # GET
            # =================================================

            return render_template(
                "register/college_register.html"
            )


        # =====================================================
        # DATABASE ERROR
        # =====================================================

        except mysql.connector.Error as e:

            if conn:
                conn.rollback()

            print("=" * 70)
            print("COLLEGE REGISTRATION DATABASE ERROR:")
            print(type(e).__name__)
            print(e)
            print("=" * 70)

            flash(
                "Unable to complete college registration.",
                "error"
            )

            return render_template(
                "register/college_register.html"
            )


        # =====================================================
        # GENERAL ERROR
        # =====================================================

        except Exception as e:

            if conn:
                conn.rollback()

            print("=" * 70)
            print("COLLEGE REGISTRATION ERROR:")
            print(type(e).__name__)
            print(e)
            print("=" * 70)

            flash(
                "Unable to complete college registration.",
                "error"
            )

            return render_template(
                "register/college_register.html"
            )


        # =====================================================
        # CLOSE DATABASE
        # =====================================================

        finally:

            if cursor:
                cursor.close()

            if conn:
                conn.close()

# =========================================================
# PLACEMENT CELL REGISTRATION
# =========================================================

@app.route(
    "/register/placement-cell",
    methods=["GET", "POST"]
)
def register_placement_cell():

    conn = None
    cursor = None

    try:

        # =================================================
        # FETCH REGISTERED COLLEGES
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT
                id,
                college_name,
                college_code
            FROM colleges
            WHERE status = 'ACTIVE'
            ORDER BY college_name ASC
        """)

        colleges = cursor.fetchall()

        # =================================================
        # POST REQUEST
        # =================================================

        if request.method == "POST":

            # -------------------------------------------------
            # ACCOUNT INFORMATION
            # -------------------------------------------------

            representative_name = request.form.get(
                "representative_name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip().lower()

            password = request.form.get(
                "password",
                ""
            )

            confirm_password = request.form.get(
                "confirm_password",
                ""
            )

            # -------------------------------------------------
            # COLLEGE
            # -------------------------------------------------

            college_id = request.form.get(
                "college_id",
                ""
            ).strip()

            # -------------------------------------------------
            # OTHER INFORMATION
            # -------------------------------------------------

            designation = request.form.get(
                "designation",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            # =================================================
            # NAME VALIDATION
            # =================================================

            if not representative_name:

                flash(
                    "Representative name is required.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            if len(representative_name) < 2:

                flash(
                    "Please enter a valid representative name.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            if len(representative_name) > 150:

                flash(
                    "Representative name cannot exceed 150 characters.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            # =================================================
            # EMAIL VALIDATION
            # =================================================

            if not email:

                flash(
                    "Email address is required.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            email_pattern = (
                r"^[A-Za-z0-9._%+-]+@"
                r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
            )

            if not re.match(
                email_pattern,
                email
            ):

                flash(
                    "Please enter a valid email address.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            # =================================================
            # PASSWORD VALIDATION
            # =================================================

            if len(password) < 6:

                flash(
                    "Password must be at least 6 characters.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            if password != confirm_password:

                flash(
                    "Passwords do not match.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            # =================================================
            # COLLEGE VALIDATION
            # =================================================

            if not college_id:

                flash(
                    "Please select your college.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            # =================================================
            # VERIFY COLLEGE
            # =================================================

            cursor.execute("""
                SELECT
                    id,
                    college_name
                FROM colleges
                WHERE id = %s
                  AND status = 'ACTIVE'
                LIMIT 1
            """, (
                college_id,
            ))

            selected_college = cursor.fetchone()

            if not selected_college:

                flash(
                    "Selected college is not available.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            # =================================================
            # CHECK EMAIL
            # =================================================

            cursor.execute("""
                SELECT
                    id
                FROM users
                WHERE email = %s
                LIMIT 1
            """, (
                email,
            ))

            existing_user = cursor.fetchone()

            if existing_user:

                flash(
                    "An account with this email already exists.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            # =================================================
            # CHECK ONE PLACEMENT CELL PER COLLEGE
            # =================================================

            cursor.execute("""
                SELECT
                    id
                FROM placement_cells
                WHERE college_id = %s
                LIMIT 1
            """, (
                college_id,
            ))

            existing_placement_cell = cursor.fetchone()

            if existing_placement_cell:

                flash(
                    "A placement cell is already registered for this college.",
                    "error"
                )

                return render_template(
                    "register/placement_register.html",
                    colleges=colleges
                )

            # =================================================
            # GENERATE USER ID
            # =================================================

            user_id = str(
                uuid.uuid4()
            )

            # =================================================
            # GENERATE PLACEMENT CELL ID
            # =================================================

            placement_cell_id = str(
                uuid.uuid4()
            )

            # =================================================
            # HASH PASSWORD
            # =================================================

            hashed_password = generate_password_hash(
                password
            )

            # =================================================
            # INSERT INTO USERS
            # =================================================

            cursor.execute("""
                INSERT INTO users (
                    id,
                    name,
                    email,
                    password,
                    role,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                user_id,
                representative_name,
                email,
                hashed_password,
                "PLACEMENT_CELL",
                "ACTIVE"
            ))

            # =================================================
            # INSERT INTO PLACEMENT_CELLS
            # =================================================

            cursor.execute("""
                INSERT INTO placement_cells (
                    id,
                    user_id,
                    college_id,
                    representative_name,
                    designation,
                    phone,
                    email,
                    status
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                placement_cell_id,
                user_id,
                college_id,
                representative_name,
                designation if designation else None,
                phone if phone else None,
                email,
                "ACTIVE"
            ))

            # =================================================
            # COMMIT BOTH INSERTS
            # =================================================

            conn.commit()

            # =================================================
            # SUCCESS
            # =================================================

            flash(
                "Placement Cell registration submitted successfully. "
                "Your account is pending admin approval.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        # =================================================
        # GET REQUEST
        # =================================================

        return render_template(
            "register/placement_register.html",
            colleges=colleges
        )

    # =====================================================
    # DUPLICATE / DATABASE ERROR
    # =====================================================

    except mysql.connector.IntegrityError as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT CELL DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "This registration could not be completed. "
            "The email or college may already be registered.",
            "error"
        )

        return render_template(
            "register/placement_register.html",
            colleges=colleges if "colleges" in locals() else []
        )

    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT CELL REGISTRATION ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to complete placement cell registration.",
            "error"
        )

        return render_template(
            "register/placement_register.html",
            colleges=colleges if "colleges" in locals() else []
        )

    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY REGISTRATION
# =========================================================

@app.route(
    "/register/industry",
    methods=["GET", "POST"]
)
def register_industry():

    # =====================================================
    # GET REQUEST
    # =====================================================

    if request.method == "GET":

        return render_template(
            "register/industry_register.html"
        )

    # =====================================================
    # GET FORM DATA
    # =====================================================

    contact_person = request.form.get(
        "contact_person",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    company_name = request.form.get(
        "company_name",
        ""
    ).strip()

    company_type = request.form.get(
        "company_type",
        ""
    ).strip()

    industry_sector = request.form.get(
        "industry_sector",
        ""
    ).strip()

    designation = request.form.get(
        "designation",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    website = request.form.get(
        "website",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    city = request.form.get(
        "city",
        ""
    ).strip()

    state = request.form.get(
        "state",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()


    # =====================================================
    # BASIC VALIDATION
    # =====================================================

    if not contact_person:

        flash(
            "Contact person name is required.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    if len(contact_person) < 2:

        flash(
            "Please enter a valid contact person name.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    if not email:

        flash(
            "Email address is required.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    email_pattern = (
        r"^[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    if not re.match(
        email_pattern,
        email
    ):

        flash(
            "Please enter a valid email address.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    if not password:

        flash(
            "Password is required.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    if len(password) < 6:

        flash(
            "Password must be at least 6 characters.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    if password != confirm_password:

        flash(
            "Passwords do not match.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    if not company_name:

        flash(
            "Company name is required.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    if len(company_name) < 2:

        flash(
            "Please enter a valid company name.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    # =====================================================
    # DATABASE
    # =====================================================

    conn = None
    cursor = None

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # DUPLICATE EMAIL CHECK
        # =================================================

        cursor.execute("""
            SELECT id
            FROM users
            WHERE email = %s
            LIMIT 1
        """, (
            email,
        ))

        existing_user = cursor.fetchone()


        if existing_user:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return render_template(
                "register/industry_register.html"
            )


        # =================================================
        # GENERATE USER ID
        # =================================================

        user_id = str(
            uuid.uuid4()
        )


        # =================================================
        # GENERATE INDUSTRY ID
        # =================================================

        industry_id = str(
            uuid.uuid4()
        )


        # =================================================
        # HASH PASSWORD
        # =================================================

        hashed_password = generate_password_hash(
            password
        )


        # =================================================
        # INSERT INTO USERS
        # =================================================

        cursor.execute("""
            INSERT INTO users (
                id,
                name,
                email,
                password,
                role,
                status
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            user_id,
            contact_person,
            email,
            hashed_password,
            "INDUSTRY",
            "ACTIVE"
        ))


        # =================================================
        # INSERT INTO INDUSTRIES
        # =================================================

        cursor.execute("""
            INSERT INTO industries (
                id,
                user_id,
                company_name,
                company_type,
                industry_sector,
                contact_person,
                designation,
                phone,
                email,
                website,
                address,
                city,
                state,
                description,
                status
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            industry_id,
            user_id,
            company_name,
            company_type or None,
            industry_sector or None,
            contact_person,
            designation or None,
            phone or None,
            email,
            website or None,
            address or None,
            city or None,
            state or None,
            description or None,
            "ACTIVE"
        ))


        # =================================================
        # COMMIT BOTH INSERTS
        # =================================================

        conn.commit()


        # =================================================
        # SUCCESS
        # =================================================

        flash(
            "Industry registration successful. "
            "You can now login.",
            "success"
        )

        return redirect(
            url_for("login")
        )


    # =====================================================
    # DATABASE CONSTRAINT ERROR
    # =====================================================

    except mysql.connector.IntegrityError as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("INDUSTRY REGISTRATION DATABASE ERROR:")
        print(e)
        print("=" * 70)

        flash(
            "Registration failed. "
            "The email or company information may already exist.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("INDUSTRY REGISTRATION ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to complete industry registration.",
            "error"
        )

        return render_template(
            "register/industry_register.html"
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY DASHBOARD
# =========================================================

@app.route("/industry/dashboard")
@industry_required
def industry_dashboard():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Industry session expired. Please login again.",
                "error"
            )
            return redirect(url_for("login"))


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # INDUSTRY PROFILE
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id,
                company_name,
                company_type,
                industry_sector,
                contact_person,
                designation,
                phone,
                email,
                website,
                address,
                city,
                state,
                description,
                status
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        # =================================================
        # INDUSTRY NOT FOUND
        # =================================================

        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # PROFILE COMPLETION
        # =================================================

        profile_fields = [
            "company_name",
            "company_type",
            "industry_sector",
            "contact_person",
            "designation",
            "phone",
            "email",
            "website",
            "address",
            "city",
            "state",
            "description"
        ]

        completed_fields = 0

        for field in profile_fields:

            value = industry.get(field)

            if value is not None and str(value).strip():
                completed_fields += 1


        profile_completion = round(
            (
                completed_fields /
                len(profile_fields)
            ) * 100
        )


        # =================================================
        # ACTIVE REQUIREMENTS
        # =================================================
        # Requirements are represented by OPEN opportunities
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE industry_id = %s
              AND status = 'OPEN'
        """, (
            industry["id"],
        ))

        active_requirements = cursor.fetchone()["total"]


        # =================================================
        # TOTAL APPLICATIONS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            WHERE o.industry_id = %s
        """, (
            industry["id"],
        ))

        total_applications = cursor.fetchone()["total"]


        # =================================================
        # SHORTLISTED APPLICATIONS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            WHERE o.industry_id = %s
            AND sa.status = 'SHORTLISTED'
        """, (
            industry["id"],
        ))

        shortlisted_applications = cursor.fetchone()["total"]


        # =================================================
        # ACTIVE COLLABORATIONS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE industry_id = %s
              AND status = 'ACTIVE'
        """, (
            industry["id"],
        ))

        active_collaborations = cursor.fetchone()["total"]


        # =================================================
        # RECENT COLLABORATIONS
        # =================================================

        cursor.execute("""
            SELECT
                col.id,
                col.title,
                col.description,
                col.collaboration_type,
                col.start_date,
                col.end_date,
                col.status,
                col.created_at,

                c.college_name

            FROM collaborations col

            INNER JOIN colleges c
                ON col.college_id = c.id

            WHERE col.industry_id = %s

            ORDER BY col.created_at DESC

            LIMIT 5
        """, (
            industry["id"],
        ))

        recent_collaborations = cursor.fetchall()


        # =================================================
        # RECENT REQUIREMENTS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                title,
                opportunity_type,
                required_skills,
                location,
                work_mode,
                application_deadline,
                status,
                created_at

            FROM opportunities

            WHERE industry_id = %s

            ORDER BY created_at DESC

            LIMIT 5
        """, (
            industry["id"],
        ))

        recent_requirements = cursor.fetchall()


        # =================================================
        # RECENT APPLICATIONS
        # =================================================

        cursor.execute("""
            SELECT

                sa.id AS application_id,

                sa.status,
                sa.application_date,

                u.name AS student_name,

                o.title AS opportunity_title

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            WHERE o.industry_id = %s

            ORDER BY sa.application_date DESC

            LIMIT 5
        """, (
            industry["id"],
        ))

        recent_applications = cursor.fetchall()


        # =================================================
        # RENDER DASHBOARD
        # =================================================

        return render_template(
            "industry/dashboard.html",

            dashboard="dashboard",

            industry=industry,

            profile_completion=profile_completion,

            active_requirements=active_requirements,

            total_applications=total_applications,

            shortlisted_applications=shortlisted_applications,

            active_collaborations=active_collaborations,

            recent_applications=recent_applications,

            recent_collaborations=recent_collaborations,

            recent_requirements=recent_requirements
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY DASHBOARD DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load industry dashboard.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("=" * 70)
        print("INDUSTRY DASHBOARD ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load industry dashboard.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY PROFILE
# =========================================================

@app.route("/industry/profile")
@industry_required
def industry_profile():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # DATABASE CONNECTION
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # FETCH INDUSTRY PROFILE
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id,
                company_name,
                company_type,
                industry_sector,
                contact_person,
                designation,
                phone,
                email,
                website,
                address,
                city,
                state,
                description,
                status
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))


        industry = cursor.fetchone()


        # =================================================
        # INDUSTRY NOT FOUND
        # =================================================

        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        # =================================================
        # RENDER PROFILE PAGE
        # =================================================

        return render_template(
            "industry/profile.html",
            dashboard="profile",
            industry=industry
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY PROFILE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load industry profile.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("=" * 70)
        print("INDUSTRY PROFILE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load industry profile.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY PROFILE - EDIT
# =========================================================

@app.route(
    "/industry/profile/edit",
    methods=["GET"]
)
@industry_required
def industry_profile_edit():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # DATABASE CONNECTION
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # FETCH INDUSTRY PROFILE
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id,
                company_name,
                company_type,
                industry_sector,
                contact_person,
                designation,
                phone,
                email,
                website,
                address,
                city,
                state,
                description,
                status
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))


        industry = cursor.fetchone()


        # =================================================
        # INDUSTRY NOT FOUND
        # =================================================

        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        # =================================================
        # RENDER EDIT PAGE
        # =================================================

        return render_template(
            "industry/edit_profile.html",
            dashboard="profile",
            industry=industry
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY EDIT PROFILE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load edit profile page.",
            "error"
        )

        return redirect(
            url_for("industry_profile")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("=" * 70)
        print("INDUSTRY EDIT PROFILE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load edit profile page.",
            "error"
        )

        return redirect(
            url_for("industry_profile")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY PROFILE - UPDATE
# =========================================================

@app.route(
    "/industry/profile/edit",
    methods=["POST"]
)
@industry_required
def industry_profile_update():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # GET FORM DATA
        # =================================================

        company_name = request.form.get(
            "company_name",
            ""
        ).strip()

        company_type = request.form.get(
            "company_type",
            ""
        ).strip()

        industry_sector = request.form.get(
            "industry_sector",
            ""
        ).strip()

        contact_person = request.form.get(
            "contact_person",
            ""
        ).strip()

        designation = request.form.get(
            "designation",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        website = request.form.get(
            "website",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        city = request.form.get(
            "city",
            ""
        ).strip()

        state = request.form.get(
            "state",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()


        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not company_name:

            flash(
                "Company name is required.",
                "error"
            )

            return redirect(
                url_for("industry_profile_edit")
            )


        if len(company_name) < 2:

            flash(
                "Please enter a valid company name.",
                "error"
            )

            return redirect(
                url_for("industry_profile_edit")
            )


        if not contact_person:

            flash(
                "Contact person name is required.",
                "error"
            )

            return redirect(
                url_for("industry_profile_edit")
            )


        if len(contact_person) < 2:

            flash(
                "Please enter a valid contact person name.",
                "error"
            )

            return redirect(
                url_for("industry_profile_edit")
            )


        if not email:

            flash(
                "Email address is required.",
                "error"
            )

            return redirect(
                url_for("industry_profile_edit")
            )


        email_pattern = (
            r"^[A-Za-z0-9._%+-]+@"
            r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        )

        if not re.match(
            email_pattern,
            email
        ):

            flash(
                "Please enter a valid email address.",
                "error"
            )

            return redirect(
                url_for("industry_profile_edit")
            )


        # =================================================
        # DATABASE
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # CHECK EMAIL DUPLICATE
        # Ignore current user's existing email
        # =================================================

        cursor.execute("""
            SELECT
                id
            FROM users
            WHERE email = %s
              AND id != %s
            LIMIT 1
        """, (
            email,
            user_id
        ))

        existing_user = cursor.fetchone()


        if existing_user:

            flash(
                "This email address is already registered with another account.",
                "error"
            )

            return redirect(
                url_for("industry_profile_edit")
            )


        # =================================================
        # UPDATE INDUSTRIES TABLE
        # =================================================

        cursor.execute("""
            UPDATE industries
            SET
                company_name = %s,
                company_type = %s,
                industry_sector = %s,
                contact_person = %s,
                designation = %s,
                phone = %s,
                email = %s,
                website = %s,
                address = %s,
                city = %s,
                state = %s,
                description = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND user_id = %s
        """, (
            company_name,
            company_type or None,
            industry_sector or None,
            contact_person,
            designation or None,
            phone or None,
            email,
            website or None,
            address or None,
            city or None,
            state or None,
            description or None,
            industry_id,
            user_id
        ))


        # =================================================
        # UPDATE USERS TABLE
        # Keep account information synchronized
        # =================================================

        cursor.execute("""
            UPDATE users
            SET
                name = %s,
                email = %s
            WHERE id = %s
              AND role = 'INDUSTRY'
        """, (
            contact_person,
            email,
            user_id
        ))


        # =================================================
        # COMMIT
        # =================================================

        conn.commit()


        # =================================================
        # UPDATE CURRENT SESSION
        # =================================================

        session["user_name"] = contact_person


        # =================================================
        # SUCCESS
        # =================================================

        flash(
            "Industry profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("industry_profile")
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.IntegrityError as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("INDUSTRY PROFILE UPDATE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Profile update failed. Please check your information.",
            "error"
        )

        return redirect(
            url_for("industry_profile_edit")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("INDUSTRY PROFILE UPDATE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update industry profile.",
            "error"
        )

        return redirect(
            url_for("industry_profile_edit")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY REQUIREMENTS - LIST
# =========================================================

@app.route("/industry/requirements")
@industry_required
def industry_requirements():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # DATABASE CONNECTION
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        # =================================================
        # INDUSTRY NOT FOUND
        # =================================================

        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # FETCH REQUIREMENTS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                industry_id,
                title,
                opportunity_type,
                description,
                required_skills,
                eligibility_criteria,
                location,
                work_mode,
                stipend,
                package,
                application_deadline,
                status,
                created_at,
                updated_at

            FROM opportunities

            WHERE industry_id = %s

            ORDER BY created_at DESC
        """, (
            industry_id,
        ))

        requirements = cursor.fetchall()


        # =================================================
        # APPLICATION COUNT
        #
        # Applications module will be connected later.
        # Currently showing 0 safely.
        # =================================================

        for requirement in requirements:

            cursor.execute("""
                SELECT COUNT(*) AS total

                FROM student_applications

                WHERE opportunity_id = %s
            """, (
                requirement["id"],
            ))

            requirement["application_count"] = (
                cursor.fetchone()["total"]
            )

        # =================================================
        # STATISTICS
        # =================================================

        total_requirements = len(
            requirements
        )


        open_requirements = sum(
            1
            for requirement in requirements
            if requirement["status"] == "OPEN"
        )


        closed_requirements = sum(
            1
            for requirement in requirements
            if requirement["status"] == "CLOSED"
        )


        # =================================================
        # UPCOMING DEADLINES
        # =================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total

            FROM opportunities

            WHERE industry_id = %s

              AND status = 'OPEN'

              AND application_deadline IS NOT NULL

              AND application_deadline >= CURDATE()
        """, (
            industry_id,
        ))

        upcoming_deadlines = cursor.fetchone()["total"]


        # =================================================
        # RENDER REQUIREMENTS PAGE
        # =================================================

        return render_template(
            "industry/requirements.html",

            dashboard="requirements",

            requirements=requirements,

            total_requirements=total_requirements,

            open_requirements=open_requirements,

            closed_requirements=closed_requirements,

            upcoming_deadlines=upcoming_deadlines
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY REQUIREMENTS DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load requirements.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("=" * 70)
        print("INDUSTRY REQUIREMENTS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load requirements.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY REQUIREMENT - CREATE
# =========================================================

@app.route(
    "/industry/requirements/create",
    methods=["GET", "POST"]
)
@industry_required
def industry_create_requirement():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # DATABASE CONNECTION
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id,
                status

            FROM industries

            WHERE user_id = %s

            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        # =================================================
        # INDUSTRY NOT FOUND
        # =================================================

        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        # =================================================
        # CHECK INDUSTRY STATUS
        # =================================================

        if industry["status"] != "ACTIVE":

            flash(
                "Your industry account is not active.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # GET REQUEST
        # =================================================

        if request.method == "GET":

            return render_template(
                "industry/create_requirement.html",

                dashboard="requirements"
            )


        # =================================================
        # POST DATA
        # =================================================

        title = request.form.get(
            "title",
            ""
        ).strip()


        opportunity_type = request.form.get(
            "opportunity_type",
            ""
        ).strip().upper()


        status = request.form.get(
            "status",
            "DRAFT"
        ).strip().upper()


        description = request.form.get(
            "description",
            ""
        ).strip()


        required_skills = request.form.get(
            "required_skills",
            ""
        ).strip()


        eligibility_criteria = request.form.get(
            "eligibility_criteria",
            ""
        ).strip()


        location = request.form.get(
            "location",
            ""
        ).strip()


        work_mode = request.form.get(
            "work_mode",
            ""
        ).strip().upper()


        stipend = request.form.get(
            "stipend",
            ""
        ).strip()


        package_value = request.form.get(
            "package",
            ""
        ).strip()


        application_deadline = request.form.get(
            "application_deadline",
            ""
        ).strip()


        # =================================================
        # VALIDATION
        # =================================================

        allowed_types = [
            "JOB",
            "INTERNSHIP",
            "PROJECT",
            "TRAINING",
            "COLLABORATION"
        ]


        allowed_statuses = [
            "OPEN",
            "DRAFT"
        ]


        allowed_work_modes = [
            "ONSITE",
            "REMOTE",
            "HYBRID"
        ]


        if len(title) < 3:

            flash(
                "Requirement title must be at least 3 characters.",
                "error"
            )

            return render_template(
                "industry/create_requirement.html",
                dashboard="requirements"
            )


        if opportunity_type not in allowed_types:

            flash(
                "Invalid opportunity type.",
                "error"
            )

            return render_template(
                "industry/create_requirement.html",
                dashboard="requirements"
            )


        if status not in allowed_statuses:

            flash(
                "Invalid requirement status.",
                "error"
            )

            return render_template(
                "industry/create_requirement.html",
                dashboard="requirements"
            )


        if work_mode not in allowed_work_modes:

            flash(
                "Invalid work mode.",
                "error"
            )

            return render_template(
                "industry/create_requirement.html",
                dashboard="requirements"
            )


        if len(description) < 10:

            flash(
                "Description must be at least 10 characters.",
                "error"
            )

            return render_template(
                "industry/create_requirement.html",
                dashboard="requirements"
            )


        # =================================================
        # GENERATE REQUIREMENT ID
        # =================================================

        requirement_id = str(
            uuid.uuid4()
        )


        # =================================================
        # INSERT REQUIREMENT
        # =================================================

        cursor.execute("""
            INSERT INTO opportunities (
                id,
                industry_id,
                title,
                opportunity_type,
                description,
                required_skills,
                eligibility_criteria,
                location,
                work_mode,
                stipend,
                package,
                application_deadline,
                status
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                NULLIF(%s, ''),
                NULLIF(%s, ''),
                NULLIF(%s, ''),
                %s
            )
        """, (
            requirement_id,
            industry_id,
            title,
            opportunity_type,
            description,
            required_skills,
            eligibility_criteria,
            location,
            work_mode,
            stipend,
            package_value,
            application_deadline,
            status
        ))


        # =================================================
        # COMMIT
        # =================================================

        conn.commit()


        # =================================================
        # SUCCESS
        # =================================================

        flash(
            "Requirement created successfully.",
            "success"
        )


        return redirect(
            url_for(
                "industry_requirement_detail",
                requirement_id=requirement_id
            )
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()


        print("=" * 70)
        print("INDUSTRY REQUIREMENT CREATE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)


        flash(
            "Unable to create requirement. Please check the database.",
            "error"
        )


        return redirect(
            url_for("industry_requirements")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()


        print("=" * 70)
        print("INDUSTRY REQUIREMENT CREATE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)


        flash(
            "Unable to create requirement.",
            "error"
        )


        return redirect(
            url_for("industry_requirements")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY REQUIREMENT - DETAIL
# =========================================================

@app.route(
    "/industry/requirements/<requirement_id>"
)
@industry_required
def industry_requirement_detail(requirement_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # GET REQUIREMENT
        #
        # VERY IMPORTANT:
        # industry_id is also checked.
        #
        # So Industry A cannot open Industry B's
        # requirement by changing the URL.
        # =================================================

        cursor.execute("""
            SELECT
                id,
                industry_id,
                title,
                opportunity_type,
                description,
                required_skills,
                eligibility_criteria,
                location,
                work_mode,
                stipend,
                package,
                application_deadline,
                status,
                created_at,
                updated_at

            FROM opportunities

            WHERE id = %s

              AND industry_id = %s

            LIMIT 1
        """, (
            requirement_id,
            industry_id
        ))

        requirement = cursor.fetchone()


        if not requirement:

            flash(
                "Requirement not found.",
                "error"
            )

            return redirect(
                url_for("industry_requirements")
            )


        # =================================================
        # APPLICATION COUNT
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications

            WHERE opportunity_id = %s
        """, (
            requirement["id"],
        ))

        requirement["application_count"] = (
            cursor.fetchone()["total"]
        )


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "industry/requirement_detail.html",

            dashboard="requirements",

            requirement=requirement
        )


    except mysql.connector.Error as e:

        print("=" * 70)
        print("REQUIREMENT DETAIL DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load requirement.",
            "error"
        )

        return redirect(
            url_for("industry_requirements")
        )


    except Exception as e:

        print("=" * 70)
        print("REQUIREMENT DETAIL ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load requirement.",
            "error"
        )

        return redirect(
            url_for("industry_requirements")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY REQUIREMENT - EDIT
# =========================================================

@app.route(
    "/industry/requirements/<requirement_id>/edit",
    methods=["GET", "POST"]
)
@industry_required
def industry_edit_requirement(requirement_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id,
                status
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # GET REQUIREMENT
        # =================================================

        cursor.execute("""
            SELECT
                id,
                industry_id,
                title,
                opportunity_type,
                description,
                required_skills,
                eligibility_criteria,
                location,
                work_mode,
                stipend,
                package,
                application_deadline,
                status,
                created_at,
                updated_at

            FROM opportunities

            WHERE id = %s

              AND industry_id = %s

            LIMIT 1
        """, (
            requirement_id,
            industry_id
        ))

        requirement = cursor.fetchone()


        if not requirement:

            flash(
                "Requirement not found.",
                "error"
            )

            return redirect(
                url_for("industry_requirements")
            )


        # =================================================
        # GET REQUEST
        # =================================================

        if request.method == "GET":

            return render_template(
                "industry/edit_requirement.html",

                dashboard="requirements",

                requirement=requirement
            )


        # =================================================
        # FORM DATA
        # =================================================

        title = request.form.get(
            "title",
            ""
        ).strip()

        opportunity_type = request.form.get(
            "opportunity_type",
            ""
        ).strip().upper()

        description = request.form.get(
            "description",
            ""
        ).strip()

        required_skills = request.form.get(
            "required_skills",
            ""
        ).strip()

        eligibility_criteria = request.form.get(
            "eligibility_criteria",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        work_mode = request.form.get(
            "work_mode",
            ""
        ).strip().upper()

        stipend = request.form.get(
            "stipend",
            ""
        ).strip()

        package_value = request.form.get(
            "package",
            ""
        ).strip()

        application_deadline = request.form.get(
            "application_deadline",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "OPEN"
        ).strip().upper()


        # =================================================
        # VALIDATION
        # =================================================

        allowed_types = [
            "JOB",
            "INTERNSHIP",
            "PROJECT",
            "TRAINING",
            "COLLABORATION"
        ]

        allowed_statuses = [
            "OPEN",
            "DRAFT",
            "CLOSED"
        ]

        allowed_work_modes = [
            "",
            "ONSITE",
            "REMOTE",
            "HYBRID"
        ]


        if not title:

            flash(
                "Requirement title is required.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_edit_requirement",
                    requirement_id=requirement_id
                )
            )


        if len(title) < 3:

            flash(
                "Requirement title must contain at least 3 characters.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_edit_requirement",
                    requirement_id=requirement_id
                )
            )


        if opportunity_type not in allowed_types:

            flash(
                "Invalid requirement type.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_edit_requirement",
                    requirement_id=requirement_id
                )
            )


        if not description:

            flash(
                "Requirement description is required.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_edit_requirement",
                    requirement_id=requirement_id
                )
            )


        if len(description) < 10:

            flash(
                "Description must contain at least 10 characters.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_edit_requirement",
                    requirement_id=requirement_id
                )
            )


        if status not in allowed_statuses:

            flash(
                "Invalid requirement status.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_edit_requirement",
                    requirement_id=requirement_id
                )
            )


        if work_mode not in allowed_work_modes:

            flash(
                "Invalid work mode.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_edit_requirement",
                    requirement_id=requirement_id
                )
            )


        # =================================================
        # UPDATE
        # =================================================

        cursor.execute("""
            UPDATE opportunities

            SET
                title = %s,
                opportunity_type = %s,
                description = %s,
                required_skills = %s,
                eligibility_criteria = %s,
                location = %s,
                work_mode = %s,
                stipend = %s,
                package = %s,
                application_deadline = NULLIF(%s, ''),
                status = %s,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = %s

              AND industry_id = %s
        """, (
            title,
            opportunity_type,
            description,
            required_skills or None,
            eligibility_criteria or None,
            location or None,
            work_mode or None,
            stipend or None,
            package_value or None,
            application_deadline,
            status,
            requirement_id,
            industry_id
        ))


        # =================================================
        # CHECK UPDATE
        # =================================================

        if cursor.rowcount == 0:

            conn.rollback()

            flash(
                "No changes were made or requirement was not found.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_requirement_detail",
                    requirement_id=requirement_id
                )
            )


        # =================================================
        # COMMIT
        # =================================================

        conn.commit()


        # =================================================
        # SUCCESS
        # =================================================

        flash(
            "Requirement updated successfully.",
            "success"
        )


        return redirect(
            url_for(
                "industry_requirement_detail",
                requirement_id=requirement_id
            )
        )


    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("EDIT REQUIREMENT DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update requirement.",
            "error"
        )

        return redirect(
            url_for(
                "industry_edit_requirement",
                requirement_id=requirement_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("EDIT REQUIREMENT ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update requirement.",
            "error"
        )

        return redirect(
            url_for(
                "industry_edit_requirement",
                requirement_id=requirement_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY REQUIREMENT - CLOSE
# =========================================================

@app.route(
    "/industry/requirements/<requirement_id>/close",
    methods=["POST"]
)
@industry_required
def industry_close_requirement(requirement_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # CHECK REQUIREMENT
        # =================================================

        cursor.execute("""
            SELECT
                id,
                status
            FROM opportunities

            WHERE id = %s

              AND industry_id = %s

            LIMIT 1
        """, (
            requirement_id,
            industry_id
        ))

        requirement = cursor.fetchone()


        if not requirement:

            flash(
                "Requirement not found.",
                "error"
            )

            return redirect(
                url_for("industry_requirements")
            )


        if requirement["status"] == "CLOSED":

            flash(
                "Requirement is already closed.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_requirement_detail",
                    requirement_id=requirement_id
                )
            )


        # =================================================
        # CLOSE REQUIREMENT
        # =================================================

        cursor.execute("""
            UPDATE opportunities

            SET
                status = 'CLOSED',
                updated_at = CURRENT_TIMESTAMP

            WHERE id = %s

              AND industry_id = %s
        """, (
            requirement_id,
            industry_id
        ))


        conn.commit()


        flash(
            "Requirement closed successfully.",
            "success"
        )


        return redirect(
            url_for(
                "industry_requirement_detail",
                requirement_id=requirement_id
            )
        )


    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("CLOSE REQUIREMENT DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to close requirement.",
            "error"
        )

        return redirect(
            url_for(
                "industry_requirement_detail",
                requirement_id=requirement_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("CLOSE REQUIREMENT ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to close requirement.",
            "error"
        )

        return redirect(
            url_for(
                "industry_requirement_detail",
                requirement_id=requirement_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()    

# =========================================================
# INDUSTRY APPLICATIONS - LIST
# =========================================================

@app.route("/industry/applications")
@industry_required
def industry_applications():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # DATABASE CONNECTION
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id,
                company_name,
                status
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        # =================================================
        # INDUSTRY NOT FOUND
        # =================================================

        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # FETCH APPLICATIONS
        #
        # student_applications
        #        ↓
        # opportunities
        #        ↓
        # industries
        #
        # Only applications belonging to CURRENT industry
        # are returned.
        # =================================================

        cursor.execute("""
            SELECT

                sa.id AS application_id,
                sa.student_id,
                sa.opportunity_id,

                sa.application_date,
                sa.status,

                sa.resume_url,
                sa.cover_letter,

                sa.created_at,
                sa.updated_at,

                o.title AS opportunity_title,
                o.opportunity_type,
                o.location,
                o.work_mode,
                o.application_deadline,

                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.phone,
                s.cgpa,

                u.name AS student_name,
                u.email AS student_email,

                c.college_name,
                c.college_code

            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            WHERE i.id = %s

            ORDER BY sa.application_date DESC

        """, (
            industry_id,
        ))

        applications = cursor.fetchall()


        # =================================================
        # STATISTICS
        # =================================================

        total_applications = len(
            applications
        )


        applied_applications = sum(
            1
            for application in applications
            if application["status"] == "APPLIED"
        )


        shortlisted_applications = sum(
            1
            for application in applications
            if application["status"] == "SHORTLISTED"
        )


        selected_applications = sum(
            1
            for application in applications
            if application["status"] == "SELECTED"
        )


        rejected_applications = sum(
            1
            for application in applications
            if application["status"] == "REJECTED"
        )


        withdrawn_applications = sum(
            1
            for application in applications
            if application["status"] == "WITHDRAWN"
        )


        # =================================================
        # RENDER APPLICATIONS PAGE
        # =================================================

        return render_template(
            "industry/applications.html",

            dashboard="applications",

            applications=applications,

            total_applications=total_applications,

            applied_applications=applied_applications,

            shortlisted_applications=shortlisted_applications,

            selected_applications=selected_applications,

            rejected_applications=rejected_applications,

            withdrawn_applications=withdrawn_applications
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY APPLICATIONS DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load applications.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("=" * 70)
        print("INDUSTRY APPLICATIONS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load applications.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY APPLICATION - DETAIL
# =========================================================

@app.route(
    "/industry/applications/<application_id>"
)
@industry_required
def industry_application_detail(application_id):

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # DATABASE CONNECTION
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id,
                company_name,
                status
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        # =================================================
        # INDUSTRY NOT FOUND
        # =================================================

        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # FETCH APPLICATION DETAIL
        #
        # IMPORTANT:
        # Application must belong to an opportunity
        # owned by CURRENT INDUSTRY.
        # =================================================

        cursor.execute("""
            SELECT

                sa.id AS application_id,
                sa.student_id,
                sa.opportunity_id,

                sa.application_date,
                sa.status,

                sa.resume_url,
                sa.cover_letter,

                sa.created_at,
                sa.updated_at,

                o.title AS opportunity_title,
                o.opportunity_type,
                o.description AS opportunity_description,
                o.required_skills,
                o.eligibility_criteria,
                o.location,
                o.work_mode,
                o.stipend,
                o.package,
                o.application_deadline,
                o.status AS opportunity_status,

                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.phone,
                s.dob,
                s.gender,
                s.address,
                s.cgpa,
                s.current_sgpa,
                s.active_backlogs,
                s.linkedin_url,
                s.github_url,
                s.portfolio_url,

                u.name AS student_name,
                u.email AS student_email,

                c.college_name,
                c.college_code,
                c.university_name,
                c.city AS college_city,
                c.state AS college_state

            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            WHERE sa.id = %s

              AND i.id = %s

            LIMIT 1

        """, (
            application_id,
            industry_id
        ))

        application = cursor.fetchone()


        # =================================================
        # APPLICATION NOT FOUND
        # =================================================

        if not application:

            flash(
                "Application not found.",
                "error"
            )

            return redirect(
                url_for("industry_applications")
            )


        # =================================================
        # RENDER DETAIL
        # =================================================

        return render_template(
            "industry/application_detail.html",

            dashboard="applications",

            application=application
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY APPLICATION DETAIL DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load application.",
            "error"
        )

        return redirect(
            url_for("industry_applications")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("=" * 70)
        print("INDUSTRY APPLICATION DETAIL ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load application.",
            "error"
        )

        return redirect(
            url_for("industry_applications")
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY APPLICATION - UPDATE STATUS
# =========================================================

@app.route(
    "/industry/applications/<application_id>/status",
    methods=["POST"]
)
@industry_required
def industry_update_application_status(application_id):

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT INDUSTRY USER
        # =================================================

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # GET NEW STATUS
        # =================================================

        new_status = request.form.get(
            "status",
            ""
        ).strip().upper()


        # =================================================
        # ALLOWED APPLICATION STATUSES
        # =================================================

        allowed_statuses = [
            "APPLIED",
            "SHORTLISTED",
            "REJECTED",
            "SELECTED",
            "WITHDRAWN"
        ]


        if new_status not in allowed_statuses:

            flash(
                "Invalid application status.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_application_detail",
                    application_id=application_id
                )
            )


        # =================================================
        # DATABASE
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # VERIFY APPLICATION BELONGS TO INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                sa.id,
                sa.status

            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            WHERE sa.id = %s

              AND o.industry_id = %s

            LIMIT 1

        """, (
            application_id,
            industry_id
        ))

        application = cursor.fetchone()


        if not application:

            flash(
                "Application not found.",
                "error"
            )

            return redirect(
                url_for("industry_applications")
            )


        # =================================================
        # UPDATE STATUS
        # =================================================

        cursor.execute("""
            UPDATE student_applications

            SET
                status = %s,
                updated_at = CURRENT_TIMESTAMP

            WHERE id = %s
        """, (
            new_status,
            application_id
        ))


        # =================================================
        # COMMIT
        # =================================================

        conn.commit()


        # =================================================
        # SUCCESS
        # =================================================

        flash(
            f"Application status changed to {new_status}.",
            "success"
        )


        return redirect(
            url_for(
                "industry_application_detail",
                application_id=application_id
            )
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("UPDATE APPLICATION STATUS DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update application status.",
            "error"
        )

        return redirect(
            url_for(
                "industry_application_detail",
                application_id=application_id
            )
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("UPDATE APPLICATION STATUS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update application status.",
            "error"
        )

        return redirect(
            url_for(
                "industry_application_detail",
                application_id=application_id
            )
        )


    # =====================================================
    # CLOSE DATABASE
    # =====================================================

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY - COLLEGES LIST
# =========================================================

@app.route("/industry/colleges")
@industry_required
def industry_colleges():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET REGISTERED COLLEGES
        # =================================================

        cursor.execute("""
            SELECT
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,

                u.name AS user_name,

                COUNT(DISTINCT s.id) AS student_count

            FROM colleges c

            LEFT JOIN users u
                ON c.user_id = u.id

            LEFT JOIN students s
                ON c.id = s.college_id

            WHERE c.status = 'ACTIVE'

            GROUP BY
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,
                u.name

            ORDER BY c.college_name ASC
        """)

        colleges = cursor.fetchall()


        # =================================================
        # STATES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                state
            FROM colleges

            WHERE status = 'ACTIVE'

              AND state IS NOT NULL

              AND state != ''

            ORDER BY state ASC
        """)

        states = [
            row["state"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # COLLABORATION COUNT
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM collaborations

            WHERE industry_id = (
                SELECT id
                FROM industries
                WHERE user_id = %s
                LIMIT 1
            )
        """, (
            user_id,
        ))

        collaboration_count = (
            cursor.fetchone()["total"]
        )


        # =================================================
        # COLLABORATION REQUEST COUNT
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM collaborations

            WHERE industry_id = (
                SELECT id
                FROM industries
                WHERE user_id = %s
                LIMIT 1
            )

              AND status = 'PENDING'
        """, (
            user_id,
        ))

        collaboration_request_count = (
            cursor.fetchone()["total"]
        )


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "industry/colleges.html",

            dashboard="colleges",

            colleges=colleges,

            states=states,

            collaboration_count=collaboration_count,

            collaboration_request_count=collaboration_request_count
        )


    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY COLLEGES DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load colleges.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    except Exception as e:

        print("=" * 70)
        print("INDUSTRY COLLEGES ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load colleges.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY - COLLEGE DETAIL
# =========================================================

@app.route("/industry/colleges/<college_id>")
@industry_required
def industry_college_detail(college_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # GET COLLEGE
        # =================================================

        cursor.execute("""
            SELECT
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,

                u.name AS user_name,
                u.email AS user_email,

                COUNT(DISTINCT s.id) AS student_count

            FROM colleges c

            LEFT JOIN users u
                ON c.user_id = u.id

            LEFT JOIN students s
                ON c.id = s.college_id

            WHERE c.id = %s

              AND c.status = 'ACTIVE'

            GROUP BY
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,
                u.name,
                u.email

            LIMIT 1
        """, (
            college_id,
        ))

        college = cursor.fetchone()


        # =================================================
        # NOT FOUND
        # =================================================

        if not college:

            flash(
                "College not found.",
                "error"
            )

            return redirect(
                url_for("industry_colleges")
            )


        # =================================================
        # CHECK EXISTING COLLABORATION
        # =================================================

        cursor.execute("""
            SELECT
                id,
                title,
                collaboration_type,
                status,
                start_date,
                end_date,
                created_at

            FROM collaborations

            WHERE college_id = %s

              AND industry_id = (
                  SELECT id
                  FROM industries
                  WHERE user_id = %s
                  LIMIT 1
              )

            ORDER BY created_at DESC

            LIMIT 1
        """, (
            college_id,
            user_id
        ))

        existing_collaboration = (
            cursor.fetchone()
        )


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "industry/college_detail.html",

            dashboard="college_detail",

            college=college,

            existing_collaboration=existing_collaboration
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY COLLEGE DETAIL DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load college details.",
            "error"
        )

        return redirect(
            url_for("industry_colleges")
        )


    except Exception as e:

        print("=" * 70)
        print("INDUSTRY COLLEGE DETAIL ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load college details.",
            "error"
        )

        return redirect(
            url_for("industry_colleges")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY - COLLABORATION REQUESTS
# =========================================================

@app.route("/industry/collaboration")
@industry_required
def industry_collaboration_requests():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            flash("Industry session expired. Please login again.", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()

        cursor = conn.cursor(dictionary=True)

        # =================================================
        # CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id,
                company_name
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()

        if not industry:
            flash("Industry profile not found.", "error")
            return redirect(url_for("industry_dashboard"))

        industry_id = industry["id"]

        # =================================================
        # GET COLLABORATION REQUESTS
        # =================================================

        cursor.execute("""
            SELECT

                c.id,
                c.college_id,
                c.industry_id,

                c.title,
                c.description,
                c.collaboration_type,

                c.start_date,
                c.end_date,

                c.status,

                c.created_at,
                c.updated_at,

                cl.college_name,
                cl.college_code,
                cl.university_name,
                cl.city,
                cl.state,
                cl.email AS college_email,
                cl.phone AS college_phone

            FROM collaborations c

            INNER JOIN colleges cl
                ON c.college_id = cl.id

            WHERE c.industry_id = %s

            ORDER BY c.created_at DESC
        """, (
            industry_id,
        ))

        requests = cursor.fetchall()

        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "industry/collaboration_requests.html",

            dashboard="collaboration",

            requests=requests
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("INDUSTRY COLLABORATION DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load collaboration requests.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )

    except Exception as e:

        print("=" * 70)
        print("INDUSTRY COLLABORATION ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load collaboration requests.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY - SEND COLLABORATION REQUEST
# =========================================================

@app.route(
    "/industry/colleges/<college_id>/collaboration",
    methods=["POST"]
)
@industry_required
def industry_send_collaboration_request(college_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            flash("Industry session expired. Please login again.", "error")
            return redirect(url_for("login"))

        # =================================================
        # FORM DATA
        # =================================================

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        collaboration_type = request.form.get(
            "collaboration_type",
            ""
        ).strip().upper()

        # =================================================
        # VALIDATION
        # =================================================

        if not title:

            flash(
                "Collaboration title is required.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_college_detail",
                    college_id=college_id
                )
            )


        if not collaboration_type:

            flash(
                "Please select a collaboration type.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_college_detail",
                    college_id=college_id
                )
            )


        allowed_types = [
            "INTERNSHIP",
            "LIVE_PROJECT",
            "INDUSTRY_PROJECT",
            "TRAINING",
            "WORKSHOP",
            "RESEARCH",
            "PLACEMENT"
        ]


        if collaboration_type not in allowed_types:

            flash(
                "Invalid collaboration type.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_college_detail",
                    college_id=college_id
                )
            )


        # =================================================
        # DATABASE
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id,
                company_name
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # VERIFY COLLEGE
        # =================================================

        cursor.execute("""
            SELECT
                id,
                college_name,
                status
            FROM colleges
            WHERE id = %s
            LIMIT 1
        """, (
            college_id,
        ))

        college = cursor.fetchone()


        if not college:

            flash(
                "College not found.",
                "error"
            )

            return redirect(
                url_for("industry_colleges")
            )


        if college["status"] != "ACTIVE":

            flash(
                "Collaboration can only be requested from an active college.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_college_detail",
                    college_id=college_id
                )
            )


        # =================================================
        # DUPLICATE ACTIVE/PENDING REQUEST CHECK
        # =================================================

        cursor.execute("""
            SELECT
                id,
                status

            FROM collaborations

            WHERE college_id = %s

              AND industry_id = %s

              AND status IN (
                  'PENDING',
                  'ACTIVE'
              )

            LIMIT 1
        """, (
            college_id,
            industry_id
        ))

        existing = cursor.fetchone()


        if existing:

            if existing["status"] == "PENDING":

                flash(
                    "A collaboration request is already pending for this college.",
                    "error"
                )

            else:

                flash(
                    "An active collaboration already exists with this college.",
                    "error"
                )


            return redirect(
                url_for(
                    "industry_college_detail",
                    college_id=college_id
                )
            )


        # =================================================
        # GENERATE UUID
        # =================================================

        collaboration_id = str(
            uuid.uuid4()
        )


        # =================================================
        # INSERT REQUEST
        # =================================================

        cursor.execute("""
            INSERT INTO collaborations (
                id,
                college_id,
                industry_id,
                title,
                description,
                collaboration_type,
                status
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'PENDING'
            )
        """, (
            collaboration_id,
            college_id,
            industry_id,
            title,
            description,
            collaboration_type
        ))


        conn.commit()


        flash(
            "Collaboration request sent successfully.",
            "success"
        )


        return redirect(
            url_for(
                "industry_collaboration_requests"
            )
        )


    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("SEND COLLABORATION REQUEST DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to send collaboration request.",
            "error"
        )

        return redirect(
            url_for(
                "industry_college_detail",
                college_id=college_id
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("SEND COLLABORATION REQUEST ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to send collaboration request.",
            "error"
        )

        return redirect(
            url_for(
                "industry_college_detail",
                college_id=college_id
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# INDUSTRY - CANCEL COLLABORATION REQUEST
# =========================================================

@app.route(
    "/industry/collaboration/<collaboration_id>/cancel",
    methods=["POST"]
)
@industry_required
def industry_cancel_collaboration(
    collaboration_id
):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Industry session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # CURRENT INDUSTRY
        # =================================================

        cursor.execute("""
            SELECT
                id
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_dashboard")
            )


        industry_id = industry["id"]


        # =================================================
        # VERIFY REQUEST OWNERSHIP
        # =================================================

        cursor.execute("""
            SELECT
                id,
                status

            FROM collaborations

            WHERE id = %s

              AND industry_id = %s

            LIMIT 1
        """, (
            collaboration_id,
            industry_id
        ))

        collaboration = cursor.fetchone()


        if not collaboration:

            flash(
                "Collaboration request not found.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_collaboration_requests"
                )
            )


        # =================================================
        # ONLY PENDING REQUEST CAN BE CANCELLED
        # =================================================

        if collaboration["status"] != "PENDING":

            flash(
                "Only pending collaboration requests can be cancelled.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_collaboration_requests"
                )
            )


        # =================================================
        # CANCEL
        # =================================================

        cursor.execute("""
            UPDATE collaborations

            SET
                status = 'CANCELLED',
                updated_at = CURRENT_TIMESTAMP

            WHERE id = %s

              AND industry_id = %s
        """, (
            collaboration_id,
            industry_id
        ))


        conn.commit()


        flash(
            "Collaboration request cancelled successfully.",
            "success"
        )


        return redirect(
            url_for(
                "industry_collaboration_requests"
            )
        )


    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("CANCEL COLLABORATION DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to cancel collaboration request.",
            "error"
        )

        return redirect(
            url_for(
                "industry_collaboration_requests"
            )
        )


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("CANCEL COLLABORATION ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to cancel collaboration request.",
            "error"
        )

        return redirect(
            url_for(
                "industry_collaboration_requests"
            )
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

@app.route("/industry/students")
@industry_required
def industry_students():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        search_query = request.args.get("q", "").strip()
        selected_course = request.args.get("course", "").strip()
        selected_branch = request.args.get("branch", "").strip()
        selected_college = request.args.get("college_id", "").strip()


        # ---------------------------------------------------------
        # Dropdown values
        # ---------------------------------------------------------

        cursor.execute("""
            SELECT DISTINCT course
            FROM students
            WHERE course IS NOT NULL
              AND course != ''
            ORDER BY course
        """)

        courses = [
            row["course"]
            for row in cursor.fetchall()
        ]


        cursor.execute("""
            SELECT DISTINCT branch
            FROM students
            WHERE branch IS NOT NULL
              AND branch != ''
            ORDER BY branch
        """)

        branches = [
            row["branch"]
            for row in cursor.fetchall()
        ]


        cursor.execute("""
            SELECT id, college_name
            FROM colleges
            WHERE status = 'ACTIVE'
            ORDER BY college_name
        """)

        colleges = cursor.fetchall()


        # ---------------------------------------------------------
        # Main student query
        # ---------------------------------------------------------

        query = """
            SELECT
                s.id,
                s.user_id,
                s.college_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.phone,
                s.dob,
                s.gender,
                s.address,
                s.cgpa,
                s.current_sgpa,
                s.active_backlogs,
                s.linkedin_url,
                s.github_url,
                s.portfolio_url,
                s.resume_url,
                s.profile_completed,

                u.name AS name,
                u.email AS email,

                c.college_name,
                c.university_name,
                c.city AS college_city,
                c.state AS college_state

            FROM students s

            LEFT JOIN users u
                ON s.user_id = u.id

            LEFT JOIN colleges c
                ON s.college_id = c.id

            WHERE 1 = 1
        """

        params = []


        # Search
        if search_query:

            query += """
                AND (
                    u.name LIKE %s
                    OR u.email LIKE %s
                    OR s.enrollment_no LIKE %s
                    OR s.course LIKE %s
                    OR s.branch LIKE %s
                )
            """

            search_value = f"%{search_query}%"

            params.extend([
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ])


        # Course
        if selected_course:

            query += """
                AND s.course = %s
            """

            params.append(selected_course)


        # Branch
        if selected_branch:

            query += """
                AND s.branch = %s
            """

            params.append(selected_branch)


        # College
        if selected_college:

            query += """
                AND s.college_id = %s
            """

            params.append(selected_college)


        query += """
            ORDER BY u.name ASC
        """


        cursor.execute(query, params)

        students = cursor.fetchall()


        # ---------------------------------------------------------
        # Skill data
        # ---------------------------------------------------------

        student_ids = [
            student["id"]
            for student in students
        ]


        skills_by_student = {}

        if student_ids:

            placeholders = ", ".join(
                ["%s"] * len(student_ids)
            )

            cursor.execute(
                f"""
                    SELECT
                        student_id,
                        skill_name,
                        proficiency_level,
                        assessment_percentage,
                        verification_status,
                        last_assessed_at

                    FROM student_skills

                    WHERE student_id IN ({placeholders})

                    ORDER BY
                        assessment_percentage DESC,
                        skill_name ASC
                """,
                student_ids
            )

            skill_rows = cursor.fetchall()


            for skill in skill_rows:

                student_id = skill["student_id"]

                if student_id not in skills_by_student:
                    skills_by_student[student_id] = []

                skills_by_student[student_id].append(skill)


        # Attach skills to student records
        for student in students:

            student["skills"] = skills_by_student.get(
                student["id"],
                []
            )


        # ---------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
        """)

        total_students = cursor.fetchone()["total"]


        cursor.execute("""
            SELECT COUNT(DISTINCT course) AS total
            FROM students
            WHERE course IS NOT NULL
              AND course != ''
        """)

        total_courses = cursor.fetchone()["total"]


        cursor.execute("""
            SELECT COUNT(DISTINCT college_id) AS total
            FROM students
            WHERE college_id IS NOT NULL
        """)

        total_colleges = cursor.fetchone()["total"]


        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE profile_completed = 1
        """)

        completed_profiles = cursor.fetchone()["total"]


        return render_template(
            "industry/students.html",

            dashboard="students",

            students=students,

            courses=courses,
            branches=branches,
            colleges=colleges,

            search_query=search_query,
            selected_course=selected_course,
            selected_branch=selected_branch,
            selected_college=selected_college,

            total_students=total_students,
            total_courses=total_courses,
            total_colleges=total_colleges,
            completed_profiles=completed_profiles
        )


    except Exception as e:

        print("Industry Students Error:", e)

        flash(
            "Unable to load student directory.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

@app.route("/industry/students/<student_id>")
@industry_required
def industry_student_detail(student_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)


        # ---------------------------------------------------------
        # Student details
        # ---------------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                s.college_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.phone,
                s.dob,
                s.gender,
                s.address,
                s.cgpa,
                s.current_sgpa,
                s.active_backlogs,
                s.linkedin_url,
                s.github_url,
                s.portfolio_url,
                s.resume_url,
                s.profile_completed,

                u.name AS name,
                u.email AS email,

                c.college_name,
                c.college_code,
                c.university_name,
                c.email AS college_email,
                c.phone AS college_phone,
                c.address AS college_address,
                c.city AS college_city,
                c.state AS college_state,
                c.pincode AS college_pincode,
                c.website AS college_website

            FROM students s

            LEFT JOIN users u
                ON s.user_id = u.id

            LEFT JOIN colleges c
                ON s.college_id = c.id

            WHERE s.id = %s

            LIMIT 1
        """, (student_id,))


        student = cursor.fetchone()


        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("industry_students")
            )


        # ---------------------------------------------------------
        # Student skill assessments
        # ---------------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                skill_name,
                proficiency_level,
                assessment_percentage,
                verification_status,
                last_assessed_at,
                created_at

            FROM student_skills

            WHERE student_id = %s

            ORDER BY
                assessment_percentage DESC,
                skill_name ASC
        """, (student_id,))


        skills = cursor.fetchall()


        return render_template(
            "industry/student_detail.html",

            dashboard="student_detail",

            student=student,
            skills=skills
        )


    except Exception as e:

        print(
            "Industry Student Detail Error:",
            e
        )

        flash(
            "Unable to load student profile.",
            "error"
        )

        return redirect(
            url_for("industry_students")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY - MESSAGES / COMMUNICATION
# =========================================================

@app.route("/industry/messages")
@industry_required
def industry_messages():

    connection = None
    cursor = None

    try:

        user_id = session.get("user_id")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # TOTAL MESSAGES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total_messages
            FROM messages
            WHERE sender_id = %s
               OR receiver_id = %s
            """,
            (user_id, user_id)
        )

        total_messages = cursor.fetchone()["total_messages"] or 0


        # -------------------------------------------------
        # UNREAD RECEIVED MESSAGES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS unread_messages
            FROM messages
            WHERE receiver_id = %s
              AND is_read = 0
            """,
            (user_id,)
        )

        unread_messages = cursor.fetchone()["unread_messages"] or 0


        # -------------------------------------------------
        # SENT MESSAGES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS sent_messages
            FROM messages
            WHERE sender_id = %s
            """,
            (user_id,)
        )

        sent_messages = cursor.fetchone()["sent_messages"] or 0


        # -------------------------------------------------
        # RECEIVED MESSAGES
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS received_messages
            FROM messages
            WHERE receiver_id = %s
            """,
            (user_id,)
        )

        received_messages = cursor.fetchone()["received_messages"] or 0


        # -------------------------------------------------
        # MESSAGE LIST
        #
        # For every message:
        # - if Industry sent it -> show receiver
        # - if Industry received it -> show sender
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                m.id,
                m.sender_id,
                m.receiver_id,
                m.subject,
                m.message,
                m.is_read,
                m.created_at,
                m.updated_at,

                CASE
                    WHEN m.sender_id = %s
                        THEN receiver.name
                    ELSE sender.name
                END AS other_user_name,

                CASE
                    WHEN m.sender_id = %s
                        THEN receiver.email
                    ELSE sender.email
                END AS other_user_email

            FROM messages m

            INNER JOIN users sender
                ON sender.id = m.sender_id

            INNER JOIN users receiver
                ON receiver.id = m.receiver_id

            WHERE m.sender_id = %s
               OR m.receiver_id = %s

            ORDER BY m.created_at DESC
            """,
            (
                user_id,
                user_id,
                user_id,
                user_id
            )
        )

        messages = cursor.fetchall()


        # -------------------------------------------------
        # RECIPIENTS
        #
        # Industry can communicate with:
        # STUDENT
        # COLLEGE
        # PLACEMENT CELL
        #
        # Exclude current Industry account.
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                email,
                role

            FROM users

            WHERE id != %s

              AND role IN (
                  'STUDENT',
                  'COLLEGE',
                  'PLACEMENT_CELL'
              )

            ORDER BY name ASC
            """,
            (user_id,)
        )

        recipients = cursor.fetchall()


        return render_template(
            "industry/messages.html",
            dashboard="messages",
            messages=messages,
            recipients=recipients,
            total_messages=total_messages,
            unread_messages=unread_messages,
            sent_messages=sent_messages,
            received_messages=received_messages
        )


    except Exception as e:

        print("Industry Messages Error:", e)

        flash(
            "Unable to load messages.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# INDUSTRY - SEND MESSAGE
# =========================================================

@app.route(
    "/industry/messages/send",
    methods=["POST"]
)
@industry_required
def industry_send_message():

    connection = None
    cursor = None

    try:

        sender_id = session.get("user_id")

        receiver_id = request.form.get(
            "receiver_id",
            ""
        ).strip()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()


        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not receiver_id:

            flash(
                "Please select a recipient.",
                "error"
            )

            return redirect(
                url_for("industry_messages")
            )


        if not subject:

            flash(
                "Please enter a subject.",
                "error"
            )

            return redirect(
                url_for("industry_messages")
            )


        if not message:

            flash(
                "Please enter a message.",
                "error"
            )

            return redirect(
                url_for("industry_messages")
            )


        if len(subject) > 200:

            flash(
                "Subject cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("industry_messages")
            )


        # -------------------------------------------------
        # PREVENT SELF MESSAGE
        # -------------------------------------------------

        if sender_id == receiver_id:

            flash(
                "You cannot send a message to yourself.",
                "error"
            )

            return redirect(
                url_for("industry_messages")
            )


        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)


        # -------------------------------------------------
        # VERIFY RECEIVER
        #
        # Only registered Student / College /
        # Placement Cell users are allowed.
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                name,
                role

            FROM users

            WHERE id = %s

              AND role IN (
                  'STUDENT',
                  'COLLEGE',
                  'PLACEMENT_CELL'
              )
            """,
            (receiver_id,)
        )

        receiver = cursor.fetchone()


        if not receiver:

            flash(
                "Invalid message recipient.",
                "error"
            )

            return redirect(
                url_for("industry_messages")
            )


        # -------------------------------------------------
        # INSERT MESSAGE
        # -------------------------------------------------

        import uuid

        message_id = str(uuid.uuid4())


        cursor.execute(
            """
            INSERT INTO messages (
                id,
                sender_id,
                receiver_id,
                subject,
                message,
                is_read
            )

            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                0
            )
            """,
            (
                message_id,
                sender_id,
                receiver_id,
                subject,
                message
            )
        )


        connection.commit()


        flash(
            "Message sent successfully.",
            "success"
        )


        return redirect(
            url_for("industry_messages")
        )


    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "Industry Send Message Error:",
            e
        )

        flash(
            "Unable to send message.",
            "error"
        )

        return redirect(
            url_for("industry_messages")
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# INDUSTRY - MARK MESSAGE AS READ
# =========================================================

@app.route(
    "/industry/messages/<message_id>/read",
    methods=["POST"]
)
@industry_required
def industry_mark_message_read(message_id):

    connection = None
    cursor = None

    try:

        user_id = session.get("user_id")

        connection = get_db_connection()
        cursor = connection.cursor()


        # -------------------------------------------------
        # Only receiver can mark message as read.
        # -------------------------------------------------

        cursor.execute(
            """
            UPDATE messages

            SET is_read = 1

            WHERE id = %s
              AND receiver_id = %s
            """,
            (
                message_id,
                user_id
            )
        )


        connection.commit()


        return {
            "success": True
        }


    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "Industry Mark Message Read Error:",
            e
        )

        return {
            "success": False,
            "message": "Unable to mark message as read."
        }, 500


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# ============================================================
# INDUSTRY - NOTIFICATIONS
# ============================================================

@app.route("/industry/notifications")
@industry_required
def industry_notifications():

    conn = None
    cursor = None

    try:
        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ----------------------------------------------------
        # TOTAL NOTIFICATIONS
        # ----------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM notifications
            WHERE user_id = %s
        """, (user_id,))

        total_notifications = cursor.fetchone()["total"] or 0

        # ----------------------------------------------------
        # UNREAD NOTIFICATIONS
        # ----------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS unread
            FROM notifications
            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        unread_notifications = cursor.fetchone()["unread"] or 0

        # ----------------------------------------------------
        # READ NOTIFICATIONS
        # ----------------------------------------------------
        read_notifications = total_notifications - unread_notifications

        # ----------------------------------------------------
        # ALL NOTIFICATIONS
        # Latest first
        # ----------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                user_id,
                title,
                message,
                notification_type,
                is_read,
                created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        notifications = cursor.fetchall()

        return render_template(
            "industry/notifications.html",
            dashboard="notifications",
            notifications=notifications,
            total_notifications=total_notifications,
            unread_notifications=unread_notifications,
            read_notifications=read_notifications
        )

    except Exception as e:

        print("Industry Notifications Error:", e)

        flash(
            "Unable to load notifications.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# MARK SINGLE NOTIFICATION AS READ
# ============================================================

@app.route(
    "/industry/notifications/<notification_id>/read",
    methods=["POST"]
)
@industry_required
def industry_mark_notification_read(notification_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor()

        # ----------------------------------------------------
        # Make sure notification belongs to logged-in industry
        # ----------------------------------------------------
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = %s
              AND user_id = %s
        """, (
            notification_id,
            user_id
        ))

        conn.commit()

        flash(
            "Notification marked as read.",
            "success"
        )

        return redirect(
            url_for("industry_notifications")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Mark Industry Notification Read Error:",
            e
        )

        flash(
            "Unable to update notification.",
            "error"
        )

        return redirect(
            url_for("industry_notifications")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

@app.route(
    "/industry/notifications/mark-all-read",
    methods=["POST"]
)
@industry_required
def industry_mark_all_notifications_read():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        conn.commit()

        flash(
            "All notifications marked as read.",
            "success"
        )

        return redirect(
            url_for("industry_notifications")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Mark All Industry Notifications Error:",
            e
        )

        flash(
            "Unable to update notifications.",
            "error"
        )

        return redirect(
            url_for("industry_notifications")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ============================================================
# NOTIFICATION HELPER
# ============================================================

def create_notification(
    user_id,
    title,
    message,
    notification_type=None
):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor()

        notification_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO notifications (
                id,
                user_id,
                title,
                message,
                notification_type,
                is_read
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                0
            )
        """, (
            notification_id,
            user_id,
            title,
            message,
            notification_type
        ))

        conn.commit()

        return True

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "Create Notification Error:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ============================================================
# INDUSTRY REPORTS / ACTIVITY
# ============================================================

@app.route("/industry/reports")
@industry_required
def industry_reports():

    connection = None
    cursor = None

    try:
        user_id = session.get("user_id")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # GET CURRENT INDUSTRY
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                company_name,
                company_type,
                industry_sector,
                contact_person,
                email,
                phone
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        industry = cursor.fetchone()

        if not industry:
            flash("Industry profile not found.", "error")
            return redirect(url_for("industry_dashboard"))

        industry_id = industry["id"]

        # ====================================================
        # REQUIREMENT STATISTICS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE industry_id = %s
        """, (industry_id,))

        total_requirements = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE industry_id = %s
              AND status = 'OPEN'
        """, (industry_id,))

        open_requirements = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE industry_id = %s
              AND status = 'CLOSED'
        """, (industry_id,))

        closed_requirements = cursor.fetchone()["total"]

        # ====================================================
        # APPLICATION STATISTICS
        # Applications are connected through opportunities
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa
            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id
            WHERE o.industry_id = %s
        """, (industry_id,))

        total_applications = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa
            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id
            WHERE o.industry_id = %s
              AND sa.status = 'APPLIED'
        """, (industry_id,))

        applied_applications = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa
            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id
            WHERE o.industry_id = %s
              AND sa.status = 'SHORTLISTED'
        """, (industry_id,))

        shortlisted_applications = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa
            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id
            WHERE o.industry_id = %s
              AND sa.status = 'SELECTED'
        """, (industry_id,))

        selected_applications = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa
            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id
            WHERE o.industry_id = %s
              AND sa.status = 'REJECTED'
        """, (industry_id,))

        rejected_applications = cursor.fetchone()["total"]

        # ====================================================
        # COLLABORATION STATISTICS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE industry_id = %s
        """, (industry_id,))

        total_collaborations = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE industry_id = %s
              AND status = 'PENDING'
        """, (industry_id,))

        pending_collaborations = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE industry_id = %s
              AND status = 'ACTIVE'
        """, (industry_id,))

        active_collaborations = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE industry_id = %s
              AND status = 'COMPLETED'
        """, (industry_id,))

        completed_collaborations = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE industry_id = %s
              AND status = 'REJECTED'
        """, (industry_id,))

        rejected_collaborations = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE industry_id = %s
              AND status = 'CANCELLED'
        """, (industry_id,))

        cancelled_collaborations = cursor.fetchone()["total"]

        # ====================================================
        # MESSAGE STATISTICS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM messages
            WHERE sender_id = %s
        """, (user_id,))

        messages_sent = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM messages
            WHERE receiver_id = %s
        """, (user_id,))

        messages_received = cursor.fetchone()["total"]

        total_messages = messages_sent + messages_received

        # ====================================================
        # NOTIFICATION STATISTICS
        # ====================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM notifications
            WHERE user_id = %s
        """, (user_id,))

        total_notifications = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM notifications
            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        unread_notifications = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM notifications
            WHERE user_id = %s
              AND is_read = 1
        """, (user_id,))

        read_notifications = cursor.fetchone()["total"]

        # ====================================================
        # RECENT ACTIVITY
        # ====================================================
        #
        # Activity sources:
        # 1. Requirements
        # 2. Applications
        # 3. Collaborations
        # 4. Messages
        # 5. Notifications
        #
        # Only current Industry's activity is returned.
        # ====================================================

        cursor.execute("""
            SELECT *
            FROM (
                
                SELECT
                    o.id AS activity_id,
                    o.created_at AS activity_date,
                    'REQUIREMENT' AS activity_type,
                    o.title AS activity_title,
                    CONCAT(
                        'Requirement created: ',
                        o.title
                    ) AS activity_description,
                    o.status AS activity_status
                FROM opportunities o
                WHERE o.industry_id = %s


                UNION ALL


                SELECT
                    sa.id AS activity_id,
                    sa.application_date AS activity_date,
                    'APPLICATION' AS activity_type,
                    o.title AS activity_title,
                    CONCAT(
                        'Student application received for ',
                        o.title
                    ) AS activity_description,
                    sa.status AS activity_status
                FROM student_applications sa
                INNER JOIN opportunities o
                    ON sa.opportunity_id = o.id
                WHERE o.industry_id = %s


                UNION ALL


                SELECT
                    c.id AS activity_id,
                    c.created_at AS activity_date,
                    'COLLABORATION' AS activity_type,
                    c.title AS activity_title,
                    CONCAT(
                        'Collaboration request: ',
                        c.title
                    ) AS activity_description,
                    c.status AS activity_status
                FROM collaborations c
                WHERE c.industry_id = %s


                UNION ALL


                SELECT
                    m.id AS activity_id,
                    m.created_at AS activity_date,
                    'MESSAGE' AS activity_type,
                    m.subject AS activity_title,
                    CONCAT(
                        'Message: ',
                        m.subject
                    ) AS activity_description,
                    CASE
                        WHEN m.receiver_id = %s THEN 'RECEIVED'
                        ELSE 'SENT'
                    END AS activity_status
                FROM messages m
                WHERE
                    m.sender_id = %s
                    OR m.receiver_id = %s


                UNION ALL


                SELECT
                    n.id AS activity_id,
                    n.created_at AS activity_date,
                    'NOTIFICATION' AS activity_type,
                    n.title AS activity_title,
                    n.message AS activity_description,
                    CASE
                        WHEN n.is_read = 1 THEN 'READ'
                        ELSE 'UNREAD'
                    END AS activity_status
                FROM notifications n
                WHERE n.user_id = %s

            ) AS activity_data

            ORDER BY activity_date DESC
            LIMIT 50
        """, (
            industry_id,
            industry_id,
            industry_id,
            user_id,
            user_id,
            user_id,
            user_id
        ))

        recent_activities = cursor.fetchall()

        # ====================================================
        # REPORT DATA
        # ====================================================

        report_data = {
            "requirements": {
                "total": total_requirements,
                "open": open_requirements,
                "closed": closed_requirements
            },

            "applications": {
                "total": total_applications,
                "applied": applied_applications,
                "shortlisted": shortlisted_applications,
                "selected": selected_applications,
                "rejected": rejected_applications
            },

            "collaborations": {
                "total": total_collaborations,
                "pending": pending_collaborations,
                "active": active_collaborations,
                "completed": completed_collaborations,
                "rejected": rejected_collaborations,
                "cancelled": cancelled_collaborations
            },

            "messages": {
                "total": total_messages,
                "sent": messages_sent,
                "received": messages_received
            },

            "notifications": {
                "total": total_notifications,
                "unread": unread_notifications,
                "read": read_notifications
            }
        }

        return render_template(
            "industry/reports.html",
            dashboard="reports",
            industry=industry,
            report_data=report_data,
            recent_activities=recent_activities
        )

    except Exception as e:

        print("Industry Reports Error:", e)

        flash(
            "Unable to load reports right now.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# INDUSTRY REPORT EXPORT
# ============================================================

@app.route("/industry/reports/export")
@industry_required
def industry_reports_export():

    connection = None
    cursor = None

    try:

        user_id = session.get("user_id")

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # ----------------------------------------------------
        # CURRENT INDUSTRY
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                company_name,
                company_type,
                industry_sector,
                contact_person,
                email,
                phone
            FROM industries
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        industry = cursor.fetchone()

        if not industry:
            flash("Industry profile not found.", "error")
            return redirect(url_for("industry_dashboard"))

        industry_id = industry["id"]

        # ----------------------------------------------------
        # CSV OUTPUT
        # ----------------------------------------------------

        output = StringIO()

        writer = csv.writer(output)

        # ====================================================
        # REPORT HEADER
        # ====================================================

        writer.writerow([
            "SIH Academia-Industry Collaboration Portal"
        ])

        writer.writerow([
            "Industry Activity Report"
        ])

        writer.writerow([])

        # ====================================================
        # INDUSTRY INFORMATION
        # ====================================================

        writer.writerow([
            "INDUSTRY INFORMATION"
        ])

        writer.writerow([
            "Company Name",
            industry.get("company_name") or ""
        ])

        writer.writerow([
            "Company Type",
            industry.get("company_type") or ""
        ])

        writer.writerow([
            "Industry Sector",
            industry.get("industry_sector") or ""
        ])

        writer.writerow([
            "Contact Person",
            industry.get("contact_person") or ""
        ])

        writer.writerow([
            "Email",
            industry.get("email") or ""
        ])

        writer.writerow([
            "Phone",
            industry.get("phone") or ""
        ])

        writer.writerow([])

        # ====================================================
        # REQUIREMENTS
        # ====================================================

        writer.writerow([
            "REQUIREMENTS"
        ])

        writer.writerow([
            "Metric",
            "Count"
        ])

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE industry_id = %s
        """, (industry_id,))

        total_requirements = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE industry_id = %s
              AND status = 'OPEN'
        """, (industry_id,))

        open_requirements = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE industry_id = %s
              AND status = 'CLOSED'
        """, (industry_id,))

        closed_requirements = cursor.fetchone()["total"]

        writer.writerow([
            "Total Requirements",
            total_requirements
        ])

        writer.writerow([
            "Open Requirements",
            open_requirements
        ])

        writer.writerow([
            "Closed Requirements",
            closed_requirements
        ])

        writer.writerow([])

        # ====================================================
        # APPLICATIONS
        # ====================================================

        writer.writerow([
            "APPLICATIONS"
        ])

        writer.writerow([
            "Metric",
            "Count"
        ])

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(sa.status = 'APPLIED') AS applied,
                SUM(sa.status = 'SHORTLISTED') AS shortlisted,
                SUM(sa.status = 'SELECTED') AS selected,
                SUM(sa.status = 'REJECTED') AS rejected
            FROM student_applications sa
            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id
            WHERE o.industry_id = %s
        """, (industry_id,))

        application_stats = cursor.fetchone()

        writer.writerow([
            "Total Applications",
            application_stats["total"] or 0
        ])

        writer.writerow([
            "Applied",
            application_stats["applied"] or 0
        ])

        writer.writerow([
            "Shortlisted",
            application_stats["shortlisted"] or 0
        ])

        writer.writerow([
            "Selected",
            application_stats["selected"] or 0
        ])

        writer.writerow([
            "Rejected",
            application_stats["rejected"] or 0
        ])

        writer.writerow([])

        # ====================================================
        # COLLABORATIONS
        # ====================================================

        writer.writerow([
            "COLLABORATIONS"
        ])

        writer.writerow([
            "Metric",
            "Count"
        ])

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(status = 'PENDING') AS pending,
                SUM(status = 'ACTIVE') AS active,
                SUM(status = 'COMPLETED') AS completed,
                SUM(status = 'REJECTED') AS rejected,
                SUM(status = 'CANCELLED') AS cancelled
            FROM collaborations
            WHERE industry_id = %s
        """, (industry_id,))

        collaboration_stats = cursor.fetchone()

        writer.writerow([
            "Total Collaborations",
            collaboration_stats["total"] or 0
        ])

        writer.writerow([
            "Pending",
            collaboration_stats["pending"] or 0
        ])

        writer.writerow([
            "Active",
            collaboration_stats["active"] or 0
        ])

        writer.writerow([
            "Completed",
            collaboration_stats["completed"] or 0
        ])

        writer.writerow([
            "Rejected",
            collaboration_stats["rejected"] or 0
        ])

        writer.writerow([
            "Cancelled",
            collaboration_stats["cancelled"] or 0
        ])

        writer.writerow([])

        # ====================================================
        # COMMUNICATION
        # ====================================================

        writer.writerow([
            "COMMUNICATION"
        ])

        writer.writerow([
            "Metric",
            "Count"
        ])

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM messages
            WHERE sender_id = %s
        """, (user_id,))

        sent = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM messages
            WHERE receiver_id = %s
        """, (user_id,))

        received = cursor.fetchone()["total"]

        writer.writerow([
            "Messages Sent",
            sent
        ])

        writer.writerow([
            "Messages Received",
            received
        ])

        writer.writerow([
            "Total Messages",
            sent + received
        ])

        writer.writerow([])

        # ====================================================
        # NOTIFICATIONS
        # ====================================================

        writer.writerow([
            "NOTIFICATIONS"
        ])

        writer.writerow([
            "Metric",
            "Count"
        ])

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(is_read = 0) AS unread,
                SUM(is_read = 1) AS read_count
            FROM notifications
            WHERE user_id = %s
        """, (user_id,))

        notification_stats = cursor.fetchone()

        writer.writerow([
            "Total Notifications",
            notification_stats["total"] or 0
        ])

        writer.writerow([
            "Unread",
            notification_stats["unread"] or 0
        ])

        writer.writerow([
            "Read",
            notification_stats["read_count"] or 0
        ])

        writer.writerow([])

        # ====================================================
        # RECENT ACTIVITY
        # ====================================================

        writer.writerow([
            "RECENT ACTIVITY"
        ])

        writer.writerow([
            "Date",
            "Type",
            "Title",
            "Description",
            "Status"
        ])

        cursor.execute("""
            SELECT *
            FROM (

                SELECT
                    o.created_at AS activity_date,
                    'REQUIREMENT' AS activity_type,
                    o.title AS activity_title,
                    CONCAT(
                        'Requirement created: ',
                        o.title
                    ) AS activity_description,
                    o.status AS activity_status
                FROM opportunities o
                WHERE o.industry_id = %s


                UNION ALL


                SELECT
                    sa.application_date AS activity_date,
                    'APPLICATION' AS activity_type,
                    o.title AS activity_title,
                    CONCAT(
                        'Student application received for ',
                        o.title
                    ) AS activity_description,
                    sa.status AS activity_status
                FROM student_applications sa
                INNER JOIN opportunities o
                    ON sa.opportunity_id = o.id
                WHERE o.industry_id = %s


                UNION ALL


                SELECT
                    c.created_at AS activity_date,
                    'COLLABORATION' AS activity_type,
                    c.title AS activity_title,
                    CONCAT(
                        'Collaboration request: ',
                        c.title
                    ) AS activity_description,
                    c.status AS activity_status
                FROM collaborations c
                WHERE c.industry_id = %s


                UNION ALL


                SELECT
                    m.created_at AS activity_date,
                    'MESSAGE' AS activity_type,
                    m.subject AS activity_title,
                    CONCAT(
                        'Message: ',
                        m.subject
                    ) AS activity_description,
                    CASE
                        WHEN m.receiver_id = %s
                        THEN 'RECEIVED'
                        ELSE 'SENT'
                    END AS activity_status
                FROM messages m
                WHERE
                    m.sender_id = %s
                    OR m.receiver_id = %s


                UNION ALL


                SELECT
                    n.created_at AS activity_date,
                    'NOTIFICATION' AS activity_type,
                    n.title AS activity_title,
                    n.message AS activity_description,
                    CASE
                        WHEN n.is_read = 1
                        THEN 'READ'
                        ELSE 'UNREAD'
                    END AS activity_status
                FROM notifications n
                WHERE n.user_id = %s

            ) AS activity_data

            ORDER BY activity_date DESC
            LIMIT 100
        """, (
            industry_id,
            industry_id,
            industry_id,
            user_id,
            user_id,
            user_id,
            user_id
        ))

        activities = cursor.fetchall()

        for activity in activities:

            writer.writerow([
                activity["activity_date"],
                activity["activity_type"],
                activity["activity_title"],
                activity["activity_description"],
                activity["activity_status"]
            ])

        # ====================================================
        # RESPONSE
        # ====================================================

        response = make_response(
            output.getvalue()
        )

        response.headers["Content-Type"] = (
            "text/csv; charset=utf-8"
        )

        response.headers["Content-Disposition"] = (
            "attachment; filename=industry_activity_report.csv"
        )

        return response

    except Exception as e:

        print(
            "Industry Reports Export Error:",
            e
        )

        flash(
            "Unable to export report right now.",
            "error"
        )

        return redirect(
            url_for("industry_reports")
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

# =========================================================
# INDUSTRY SETTINGS
# =========================================================

@app.route("/industry/settings", methods=["GET", "POST"])
@industry_required
def industry_settings():

    conn = None
    cursor = None

    industry_user_id = session.get("user_id")

    if not industry_user_id:
        flash("Please login first.", "error")
        return redirect(url_for("login"))

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # GET CURRENT USER
        # =================================================

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                status,
                created_at
            FROM users
            WHERE id = %s
            LIMIT 1
        """, (industry_user_id,))

        user = cursor.fetchone()

        if not user:
            flash("Industry account not found.", "error")
            return redirect(url_for("login"))

        # =================================================
        # GET / CREATE INDUSTRY SETTINGS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id,
                language,
                timezone,
                date_format,
                dashboard_view,

                application_notifications,
                collaboration_notifications,
                message_notifications,
                system_notifications,
                email_notifications,

                profile_visibility,
                college_contact,
                opportunity_visibility,

                interface_density

            FROM industry_settings

            WHERE user_id = %s

            LIMIT 1
        """, (industry_user_id,))

        settings = cursor.fetchone()

        # -------------------------------------------------
        # CREATE DEFAULT SETTINGS IF NOT EXISTS
        # -------------------------------------------------

        if not settings:

            settings_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO industry_settings (

                    id,
                    user_id,

                    language,
                    timezone,
                    date_format,
                    dashboard_view,

                    application_notifications,
                    collaboration_notifications,
                    message_notifications,
                    system_notifications,
                    email_notifications,

                    profile_visibility,
                    college_contact,
                    opportunity_visibility,

                    interface_density

                )

                VALUES (

                    %s,
                    %s,

                    %s,
                    %s,
                    %s,
                    %s,

                    %s,
                    %s,
                    %s,
                    %s,
                    %s,

                    %s,
                    %s,
                    %s,

                    %s
                )
            """, (

                settings_id,
                industry_user_id,

                "English",
                "Asia/Kolkata",
                "DD/MM/YYYY",
                "overview",

                True,
                True,
                True,
                True,
                True,

                True,
                True,
                True,

                "comfortable"
            ))

            conn.commit()

            # Fetch again
            cursor.execute("""
                SELECT
                    id,
                    user_id,
                    language,
                    timezone,
                    date_format,
                    dashboard_view,

                    application_notifications,
                    collaboration_notifications,
                    message_notifications,
                    system_notifications,
                    email_notifications,

                    profile_visibility,
                    college_contact,
                    opportunity_visibility,

                    interface_density

                FROM industry_settings

                WHERE user_id = %s

                LIMIT 1
            """, (industry_user_id,))

            settings = cursor.fetchone()

        # =================================================
        # POST
        # =================================================

        if request.method == "POST":

            # -------------------------------------------------
            # New Settings Forms
            # -------------------------------------------------

            section = request.form.get(
                "section",
                ""
            ).strip().lower()

            # =================================================
            # ACCOUNT PREFERENCES
            # =================================================

            if section == "account":

                language = request.form.get(
                    "language",
                    "English"
                ).strip()

                timezone = request.form.get(
                    "timezone",
                    "Asia/Kolkata"
                ).strip()

                date_format = request.form.get(
                    "date_format",
                    "DD/MM/YYYY"
                ).strip()

                dashboard_view = request.form.get(
                    "dashboard_view",
                    "overview"
                ).strip()

                allowed_languages = [
                    "English",
                    "Hindi"
                ]

                allowed_timezones = [
                    "Asia/Kolkata",
                    "UTC"
                ]

                allowed_date_formats = [
                    "DD/MM/YYYY",
                    "MM/DD/YYYY",
                    "YYYY-MM-DD"
                ]

                allowed_dashboard_views = [
                    "overview",
                    "requirements",
                    "applications"
                ]

                if language not in allowed_languages:
                    flash("Invalid language selected.", "error")
                    return redirect(
                        url_for("industry_settings")
                    )

                if timezone not in allowed_timezones:
                    flash("Invalid timezone selected.", "error")
                    return redirect(
                        url_for("industry_settings")
                    )

                if date_format not in allowed_date_formats:
                    flash("Invalid date format selected.", "error")
                    return redirect(
                        url_for("industry_settings")
                    )

                if dashboard_view not in allowed_dashboard_views:
                    flash("Invalid dashboard view selected.", "error")
                    return redirect(
                        url_for("industry_settings")
                    )

                cursor.execute("""
                    UPDATE industry_settings

                    SET
                        language = %s,
                        timezone = %s,
                        date_format = %s,
                        dashboard_view = %s

                    WHERE user_id = %s
                """, (
                    language,
                    timezone,
                    date_format,
                    dashboard_view,
                    industry_user_id
                ))

                # Also update account information if supplied
                name = request.form.get("name", "").strip()
                email = request.form.get("email", "").strip().lower()

                if name and email:

                    if "@" not in email or "." not in email:
                        flash(
                            "Please enter a valid email address.",
                            "error"
                        )
                        conn.rollback()

                        return redirect(
                            url_for("industry_settings")
                        )

                    cursor.execute("""
                        SELECT id
                        FROM users
                        WHERE email = %s
                          AND id <> %s
                        LIMIT 1
                    """, (
                        email,
                        industry_user_id
                    ))

                    existing_user = cursor.fetchone()

                    if existing_user:
                        flash(
                            "This email address is already registered.",
                            "error"
                        )
                        conn.rollback()

                        return redirect(
                            url_for("industry_settings")
                        )

                    cursor.execute("""
                        UPDATE users
                        SET
                            name = %s,
                            email = %s
                        WHERE id = %s
                    """, (
                        name,
                        email,
                        industry_user_id
                    ))

                    session["user_name"] = name
                    session["user_email"] = email

                conn.commit()

                flash(
                    "Account preferences saved successfully.",
                    "success"
                )

                return redirect(
                    url_for("industry_settings") + "#account"
                )

            # =================================================
            # NOTIFICATION PREFERENCES
            # =================================================

            elif section == "notifications":

                application_notifications = (
                    request.form.get(
                        "application_notifications"
                    ) is not None
                )

                collaboration_notifications = (
                    request.form.get(
                        "collaboration_notifications"
                    ) is not None
                )

                message_notifications = (
                    request.form.get(
                        "message_notifications"
                    ) is not None
                )

                system_notifications = (
                    request.form.get(
                        "system_notifications"
                    ) is not None
                )

                email_notifications = (
                    request.form.get(
                        "email_notifications"
                    ) is not None
                )

                cursor.execute("""
                    UPDATE industry_settings

                    SET
                        application_notifications = %s,
                        collaboration_notifications = %s,
                        message_notifications = %s,
                        system_notifications = %s,
                        email_notifications = %s

                    WHERE user_id = %s
                """, (
                    application_notifications,
                    collaboration_notifications,
                    message_notifications,
                    system_notifications,
                    email_notifications,
                    industry_user_id
                ))

                conn.commit()

                flash(
                    "Notification preferences saved successfully.",
                    "success"
                )

                return redirect(
                    url_for("industry_settings") + "#notifications"
                )

            # =================================================
            # PRIVACY
            # =================================================

            elif section == "privacy":

                profile_visibility = (
                    request.form.get(
                        "profile_visibility"
                    ) is not None
                )

                college_contact = (
                    request.form.get(
                        "college_contact"
                    ) is not None
                )

                opportunity_visibility = (
                    request.form.get(
                        "opportunity_visibility"
                    ) is not None
                )

                cursor.execute("""
                    UPDATE industry_settings

                    SET
                        profile_visibility = %s,
                        college_contact = %s,
                        opportunity_visibility = %s

                    WHERE user_id = %s
                """, (
                    profile_visibility,
                    college_contact,
                    opportunity_visibility,
                    industry_user_id
                ))

                conn.commit()

                flash(
                    "Privacy settings saved successfully.",
                    "success"
                )

                return redirect(
                    url_for("industry_settings") + "#privacy"
                )

            # =================================================
            # APPEARANCE
            # =================================================

            elif section == "appearance":

                interface_density = request.form.get(
                    "interface_density",
                    "comfortable"
                ).strip().lower()

                if interface_density not in [
                    "comfortable",
                    "compact"
                ]:
                    flash(
                        "Invalid interface density selected.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#appearance"
                    )

                cursor.execute("""
                    UPDATE industry_settings

                    SET
                        interface_density = %s

                    WHERE user_id = %s
                """, (
                    interface_density,
                    industry_user_id
                ))

                conn.commit()

                flash(
                    "Appearance settings saved successfully.",
                    "success"
                )

                return redirect(
                    url_for("industry_settings") + "#appearance"
                )

            # =================================================
            # SECURITY - CHANGE PASSWORD
            # =================================================

            elif section == "security":

                current_password = request.form.get(
                    "current_password",
                    ""
                ).strip()

                new_password = request.form.get(
                    "new_password",
                    ""
                ).strip()

                confirm_password = request.form.get(
                    "confirm_password",
                    ""
                ).strip()

                if not current_password:
                    flash(
                        "Current password is required.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#security"
                    )

                if not new_password:
                    flash(
                        "New password is required.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#security"
                    )

                if len(new_password) < 6:
                    flash(
                        "New password must be at least 6 characters long.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#security"
                    )

                if new_password != confirm_password:
                    flash(
                        "New passwords do not match.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#security"
                    )

                # -------------------------------------------------
                # CURRENT PROJECT PASSWORD SYSTEM
                # -------------------------------------------------

                cursor.execute("""
                    SELECT password
                    FROM users
                    WHERE id = %s
                    LIMIT 1
                """, (
                    industry_user_id,
                ))

                password_row = cursor.fetchone()

                if not password_row:
                    flash(
                        "Unable to verify your account.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#security"
                    )

                stored_password = password_row["password"]

                # Existing project stores password directly.
                if current_password != stored_password:
                    flash(
                        "Current password is incorrect.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#security"
                    )

                if current_password == new_password:
                    flash(
                        "New password must be different from your current password.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings") + "#security"
                    )

                cursor.execute("""
                    UPDATE users

                    SET password = %s

                    WHERE id = %s
                """, (
                    new_password,
                    industry_user_id
                ))

                conn.commit()

                flash(
                    "Password changed successfully.",
                    "success"
                )

                return redirect(
                    url_for("industry_settings") + "#security"
                )

            # =================================================
            # LEGACY ACCOUNT UPDATE
            # =================================================

            elif request.form.get("action") == "update_account":

                name = request.form.get(
                    "name",
                    ""
                ).strip()

                email = request.form.get(
                    "email",
                    ""
                ).strip().lower()

                if not name:
                    flash(
                        "Name is required.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                if not email:
                    flash(
                        "Email is required.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                if "@" not in email or "." not in email:
                    flash(
                        "Please enter a valid email address.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                cursor.execute("""
                    SELECT id
                    FROM users
                    WHERE email = %s
                      AND id <> %s
                    LIMIT 1
                """, (
                    email,
                    industry_user_id
                ))

                existing_user = cursor.fetchone()

                if existing_user:
                    flash(
                        "This email address is already registered.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                cursor.execute("""
                    UPDATE users
                    SET
                        name = %s,
                        email = %s
                    WHERE id = %s
                """, (
                    name,
                    email,
                    industry_user_id
                ))

                conn.commit()

                session["user_name"] = name
                session["user_email"] = email

                flash(
                    "Account information updated successfully.",
                    "success"
                )

                return redirect(
                    url_for("industry_settings")
                )

            # =================================================
            # LEGACY PASSWORD UPDATE
            # =================================================

            elif request.form.get("action") == "change_password":

                current_password = request.form.get(
                    "current_password",
                    ""
                ).strip()

                new_password = request.form.get(
                    "new_password",
                    ""
                ).strip()

                confirm_password = request.form.get(
                    "confirm_password",
                    ""
                ).strip()

                if not current_password:
                    flash(
                        "Current password is required.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                if not new_password:
                    flash(
                        "New password is required.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                if not confirm_password:
                    flash(
                        "Please confirm your new password.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                if new_password != confirm_password:
                    flash(
                        "New password and confirmation password do not match.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                if len(new_password) < 6:
                    flash(
                        "New password must be at least 6 characters long.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                cursor.execute("""
                    SELECT password
                    FROM users
                    WHERE id = %s
                    LIMIT 1
                """, (
                    industry_user_id,
                ))

                password_row = cursor.fetchone()

                if not password_row:
                    flash(
                        "Unable to verify your account.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                stored_password = password_row["password"]

                if current_password != stored_password:
                    flash(
                        "Current password is incorrect.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                if current_password == new_password:
                    flash(
                        "New password must be different from your current password.",
                        "error"
                    )

                    return redirect(
                        url_for("industry_settings")
                    )

                cursor.execute("""
                    UPDATE users
                    SET password = %s
                    WHERE id = %s
                """, (
                    new_password,
                    industry_user_id
                ))

                conn.commit()

                flash(
                    "Password changed successfully.",
                    "success"
                )

                return redirect(
                    url_for("industry_settings")
                )

            # =================================================
            # INVALID ACTION
            # =================================================

            else:

                flash(
                    "Invalid settings action.",
                    "error"
                )

                return redirect(
                    url_for("industry_settings")
                )

        # =================================================
        # GET ACCOUNT REQUEST STATUS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                request_type,
                status,
                reason,
                created_at,
                updated_at

            FROM industry_account_requests

            WHERE user_id = %s

            ORDER BY created_at DESC

            LIMIT 10
        """, (
            industry_user_id,
        ))

        account_requests = cursor.fetchall()

        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "industry/settings.html",

            dashboard="settings",

            user=user,

            settings=settings,

            account_requests=account_requests
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("INDUSTRY SETTINGS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load or update settings.",
            "error"
        )

        return redirect(
            url_for("industry_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY DEACTIVATE ACCOUNT
# =========================================================

@app.route(
    "/industry/settings/deactivate",
    methods=["POST"]
)
@industry_required
def industry_deactivate_account():

    conn = None
    cursor = None

    industry_user_id = session.get(
        "user_id"
    )

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # CHECK ACTIVE ACCOUNT
        # =================================================

        cursor.execute("""
            SELECT
                id,
                status

            FROM users

            WHERE id = %s

            LIMIT 1
        """, (
            industry_user_id,
        ))

        user = cursor.fetchone()


        if not user:

            flash(
                "Industry account not found.",
                "error"
            )

            return redirect(
                url_for(
                    "industry_settings"
                )
            )


        if user["status"] != "ACTIVE":

            flash(
                "Your account is already inactive.",
                "warning"
            )

            return redirect(
                url_for(
                    "industry_settings"
                )
            )


        # =================================================
        # CREATE DEACTIVATION REQUEST
        # =================================================

        cursor.execute("""
            SELECT
                id

            FROM industry_account_requests

            WHERE user_id = %s

              AND request_type = 'DEACTIVATE'

              AND status = 'PENDING'

            LIMIT 1
        """, (
            industry_user_id,
        ))

        existing_request = cursor.fetchone()


        if existing_request:

            flash(
                "A deactivation request is already pending.",
                "warning"
            )

            return redirect(
                url_for(
                    "industry_settings"
                ) + "#danger"
            )


        request_id = str(
            uuid.uuid4()
        )


        cursor.execute("""
            INSERT INTO industry_account_requests (

                id,
                user_id,
                request_type,
                status,
                reason

            )

            VALUES (

                %s,
                %s,
                'DEACTIVATE',
                'PENDING',
                %s

            )
        """, (

            request_id,

            industry_user_id,

            "Industry account deactivation requested from Settings."

        ))


        conn.commit()


        flash(
            "Account deactivation request submitted.",
            "success"
        )


        return redirect(
            url_for(
                "industry_settings"
            ) + "#danger"
        )


    except Exception as e:

        if conn:
            conn.rollback()


        print(
            "INDUSTRY DEACTIVATE ERROR:",
            e
        )


        flash(
            "Unable to submit deactivation request.",
            "error"
        )


        return redirect(
            url_for(
                "industry_settings"
            ) + "#danger"
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# INDUSTRY DELETE ACCOUNT REQUEST
# =========================================================

@app.route(
    "/industry/settings/delete",
    methods=["POST"]
)
@industry_required
def industry_delete_account():

    conn = None
    cursor = None

    industry_user_id = session.get(
        "user_id"
    )

    try:

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # CHECK USER
        # =================================================

        cursor.execute("""
            SELECT
                id,
                status

            FROM users

            WHERE id = %s

            LIMIT 1
        """, (
            industry_user_id,
        ))

        user = cursor.fetchone()


        if not user:

            flash(
                "Industry account not found.",
                "error"
            )

            return redirect(
                url_for(
                    "login"
                )
            )


        # =================================================
        # CHECK EXISTING REQUEST
        # =================================================

        cursor.execute("""
            SELECT
                id

            FROM industry_account_requests

            WHERE user_id = %s

              AND request_type = 'DELETE'

              AND status = 'PENDING'

            LIMIT 1
        """, (
            industry_user_id,
        ))

        existing_request = cursor.fetchone()


        if existing_request:

            flash(
                "An account deletion request is already pending.",
                "warning"
            )

            return redirect(
                url_for(
                    "industry_settings"
                ) + "#danger"
            )


        # =================================================
        # CREATE DELETE REQUEST
        # =================================================

        request_id = str(
            uuid.uuid4()
        )


        cursor.execute("""
            INSERT INTO industry_account_requests (

                id,
                user_id,
                request_type,
                status,
                reason

            )

            VALUES (

                %s,
                %s,
                'DELETE',
                'PENDING',
                %s

            )
        """, (

            request_id,

            industry_user_id,

            "Industry account deletion requested from Settings."

        ))


        conn.commit()


        flash(
            "Account deletion request submitted for review.",
            "success"
        )


        return redirect(
            url_for(
                "industry_settings"
            ) + "#danger"
        )


    except Exception as e:

        if conn:
            conn.rollback()


        print(
            "INDUSTRY DELETE ACCOUNT ERROR:",
            e
        )


        flash(
            "Unable to submit account deletion request.",
            "error"
        )


        return redirect(
            url_for(
                "industry_settings"
            ) + "#danger"
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# COLLEGE DASHBOARD
# =========================================================

@app.route("/college/dashboard")
@college_required
def college_dashboard():
    conn = None
    cursor = None

    try:
        user_id = session.get("user_id")

        if not user_id:
            flash("College session expired. Please login again.", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =========================================================
        # COLLEGE PROFILE
        # =========================================================
        cursor.execute("""
            SELECT
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,
                u.name AS contact_person,
                u.email AS account_email
            FROM colleges c
            INNER JOIN users u
                ON c.user_id = u.id
            WHERE c.user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("login"))

        college_id = college["id"]

        # =========================================================
        # ACCOUNT STATUS
        # =========================================================
        if college["status"] != "ACTIVE":
            session.clear()
            flash("Your college account is not active.", "error")
            return redirect(url_for("login"))

        # =========================================================
        # PROFILE COMPLETION
        # =========================================================
        profile_fields = [
            "college_name",
            "college_code",
            "university_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "website"
        ]

        completed_fields = 0

        for field in profile_fields:
            value = college.get(field)

            if value is not None and str(value).strip():
                completed_fields += 1

        profile_completion = round(
            (completed_fields / len(profile_fields)) * 100
        )

        # =========================================================
        # TOTAL STUDENTS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (college_id,))

        total_students = cursor.fetchone()["total"] or 0

        # =========================================================
        # TOTAL DEPARTMENTS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM departments
            WHERE college_id = %s
        """, (college_id,))

        total_departments = cursor.fetchone()["total"] or 0

        # =========================================================
        # ACTIVE DEPARTMENTS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM departments
            WHERE college_id = %s
              AND status = 'ACTIVE'
        """, (college_id,))

        active_departments = cursor.fetchone()["total"] or 0

        # =========================================================
        # PLACEMENT CELLS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM placement_cells
            WHERE college_id = %s
        """, (college_id,))

        total_placement_cells = cursor.fetchone()["total"] or 0

        # =========================================================
        # COLLABORATIONS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE college_id = %s
        """, (college_id,))

        total_collaborations = cursor.fetchone()["total"] or 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE college_id = %s
              AND status = 'ACTIVE'
        """, (college_id,))

        active_collaborations = cursor.fetchone()["total"] or 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE college_id = %s
              AND status = 'PENDING'
        """, (college_id,))

        pending_collaborations = cursor.fetchone()["total"] or 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM collaborations
            WHERE college_id = %s
              AND status = 'COMPLETED'
        """, (college_id,))

        completed_collaborations = cursor.fetchone()["total"] or 0

        # =========================================================
        # OPEN INDUSTRY OPPORTUNITIES
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE status = 'OPEN'
        """)

        open_opportunities = cursor.fetchone()["total"] or 0

        # =========================================================
        # STUDENT APPLICATIONS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa
            INNER JOIN students s
                ON sa.student_id = s.id
            WHERE s.college_id = %s
        """, (college_id,))

        total_applications = cursor.fetchone()["total"] or 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications sa
            INNER JOIN students s
                ON sa.student_id = s.id
            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
        """, (college_id,))

        selected_applications = cursor.fetchone()["total"] or 0

        # =========================================================
        # UNREAD NOTIFICATIONS
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM notifications
            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        unread_notifications = cursor.fetchone()["total"] or 0

        # =========================================================
        # UNREAD MESSAGES
        # =========================================================
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM messages
            WHERE receiver_id = %s
              AND is_read = 0
        """, (user_id,))

        unread_messages = cursor.fetchone()["total"] or 0

        # =========================================================
        # DEPARTMENT OVERVIEW
        # =========================================================
        cursor.execute("""
            SELECT
                d.id,
                d.department_name,
                d.department_code,
                d.description,
                d.status,
                d.created_at,
                COUNT(s.id) AS student_count
            FROM departments d
            LEFT JOIN students s
                ON s.department_id = d.id
            WHERE d.college_id = %s
            GROUP BY
                d.id,
                d.department_name,
                d.department_code,
                d.description,
                d.status,
                d.created_at
            ORDER BY
                d.status = 'ACTIVE' DESC,
                d.department_name ASC
            LIMIT 8
        """, (college_id,))

        department_overview = cursor.fetchall()

        # =========================================================
        # RECENT COLLABORATIONS
        # =========================================================
        cursor.execute("""
            SELECT
                col.id,
                col.title,
                col.description,
                col.collaboration_type,
                col.start_date,
                col.end_date,
                col.status,
                col.created_at,
                i.company_name AS industry_name
            FROM collaborations col
            INNER JOIN industries i
                ON col.industry_id = i.id
            WHERE col.college_id = %s
            ORDER BY col.created_at DESC
            LIMIT 5
        """, (college_id,))

        recent_collaborations = cursor.fetchall()

        # =========================================================
        # RECENT OPEN OPPORTUNITIES
        # =========================================================
        cursor.execute("""
            SELECT
                o.id,
                o.title,
                o.opportunity_type,
                o.location,
                o.work_mode,
                o.application_deadline,
                o.status,
                o.created_at,
                i.company_name AS industry_name
            FROM opportunities o
            INNER JOIN industries i
                ON o.industry_id = i.id
            WHERE o.status = 'OPEN'
            ORDER BY o.created_at DESC
            LIMIT 5
        """)

        recent_opportunities = cursor.fetchall()

        # =========================================================
        # RECENT STUDENTS
        # =========================================================
        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.phone,
                s.created_at,
                s.department_id,
                u.name,
                u.email,
                u.status AS user_status,
                d.department_name,
                d.department_code
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            LEFT JOIN departments d
                ON s.department_id = d.id
            WHERE s.college_id = %s
            ORDER BY s.created_at DESC
            LIMIT 6
        """, (college_id,))

        recent_students = cursor.fetchall()

        # =========================================================
        # DASHBOARD
        # =========================================================
        return render_template(
            "college/dashboard.html",

            dashboard="dashboard",

            college=college,

            profile_completion=profile_completion,

            total_students=total_students,
            total_departments=total_departments,
            active_departments=active_departments,
            total_placement_cells=total_placement_cells,

            total_collaborations=total_collaborations,
            active_collaborations=active_collaborations,
            pending_collaborations=pending_collaborations,
            completed_collaborations=completed_collaborations,

            open_opportunities=open_opportunities,

            total_applications=total_applications,
            selected_applications=selected_applications,

            unread_notifications=unread_notifications,
            unread_messages=unread_messages,

            department_overview=department_overview,
            recent_collaborations=recent_collaborations,
            recent_opportunities=recent_opportunities,
            recent_students=recent_students
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("COLLEGE DASHBOARD DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash("Unable to load college dashboard.", "error")
        return redirect(url_for("login"))

    except Exception as e:

        print("=" * 70)
        print("COLLEGE DASHBOARD ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash("Unable to load college dashboard.", "error")
        return redirect(url_for("login"))

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ============================================================
# COLLEGE PROFILE
# ============================================================

@app.route("/college/profile")
@college_required
def college_profile():
    conn = None
    cursor = None

    try:
        user_id = session.get("user_id")

        if not user_id:
            flash("College session expired. Please login again.", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,
                u.name AS contact_person,
                u.email AS account_email,
                u.status AS account_status
            FROM colleges c
            INNER JOIN users u
                ON c.user_id = u.id
            WHERE c.user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("login"))

        if college["status"] != "ACTIVE":
            session.clear()
            flash("Your college account is not active.", "error")
            return redirect(url_for("login"))

        # --------------------------------------------------------
        # PROFILE COMPLETION
        # --------------------------------------------------------

        profile_fields = [
            "college_name",
            "college_code",
            "university_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "pincode",
            "website"
        ]

        completed_fields = 0

        for field in profile_fields:
            value = college.get(field)

            if value is not None and str(value).strip():
                completed_fields += 1

        profile_completion = round(
            (completed_fields / len(profile_fields)) * 100
        )

        return render_template(
            "college/profile/view.html",
            college=college,
            profile_completion=profile_completion,
            profile="profile"
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("COLLEGE PROFILE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash("Unable to load college profile.", "error")
        return redirect(url_for("college_dashboard"))

    except Exception as e:

        print("=" * 70)
        print("COLLEGE PROFILE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash("Unable to load college profile.", "error")
        return redirect(url_for("college_dashboard"))

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# EDIT COLLEGE PROFILE
# ============================================================

@app.route("/college/profile/edit", methods=["GET", "POST"])
@college_required
def college_profile_edit():
    conn = None
    cursor = None

    try:
        user_id = session.get("user_id")

        if not user_id:
            flash("College session expired. Please login again.", "error")
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # --------------------------------------------------------
        # GET CURRENT PROFILE
        # --------------------------------------------------------

        cursor.execute("""
            SELECT
                c.id,
                c.user_id,
                c.college_name,
                c.college_code,
                c.university_name,
                c.email,
                c.phone,
                c.address,
                c.city,
                c.state,
                c.pincode,
                c.website,
                c.status,
                c.created_at,
                c.updated_at,
                u.name AS contact_person,
                u.email AS account_email
            FROM colleges c
            INNER JOIN users u
                ON c.user_id = u.id
            WHERE c.user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("login"))

        if college["status"] != "ACTIVE":
            session.clear()
            flash("Your college account is not active.", "error")
            return redirect(url_for("login"))

        # --------------------------------------------------------
        # SAVE CHANGES
        # --------------------------------------------------------

        if request.method == "POST":

            college_name = request.form.get(
                "college_name", ""
            ).strip()

            university_name = request.form.get(
                "university_name", ""
            ).strip()

            contact_person = request.form.get(
                "contact_person", ""
            ).strip()

            phone = request.form.get(
                "phone", ""
            ).strip()

            address = request.form.get(
                "address", ""
            ).strip()

            city = request.form.get(
                "city", ""
            ).strip()

            state = request.form.get(
                "state", ""
            ).strip()

            pincode = request.form.get(
                "pincode", ""
            ).strip()

            website = request.form.get(
                "website", ""
            ).strip()

            # ----------------------------------------------------
            # VALIDATION
            # ----------------------------------------------------

            errors = []

            if not college_name:
                errors.append("College name is required.")

            if not university_name:
                errors.append("University name is required.")

            if not contact_person:
                errors.append("Contact person is required.")

            if not phone:
                errors.append("Phone number is required.")

            elif not phone.isdigit() or len(phone) != 10:
                errors.append(
                    "Phone number must contain exactly 10 digits."
                )

            if not address:
                errors.append("Address is required.")

            if not city:
                errors.append("City is required.")

            if not state:
                errors.append("State is required.")

            if not pincode:
                errors.append("Pincode is required.")

            elif not pincode.isdigit() or len(pincode) != 6:
                errors.append(
                    "Pincode must contain exactly 6 digits."
                )

            if website and not (
                website.startswith("http://")
                or website.startswith("https://")
            ):
                errors.append(
                    "Website must start with http:// or https://."
                )

            # ----------------------------------------------------
            # SHOW ERRORS
            # ----------------------------------------------------

            if errors:

                for error in errors:
                    flash(error, "error")

                # Keep entered values in the form
                college["college_name"] = college_name
                college["university_name"] = university_name
                college["contact_person"] = contact_person
                college["phone"] = phone
                college["address"] = address
                college["city"] = city
                college["state"] = state
                college["pincode"] = pincode
                college["website"] = website

                return render_template(
                    "college/profile/edit.html",
                    college=college,
                    profile="profile"
                )

            # ----------------------------------------------------
            # UPDATE COLLEGE
            # ----------------------------------------------------

            cursor.execute("""
                UPDATE colleges
                SET
                    college_name = %s,
                    university_name = %s,
                    phone = %s,
                    address = %s,
                    city = %s,
                    state = %s,
                    pincode = %s,
                    website = %s
                WHERE user_id = %s
            """, (
                college_name,
                university_name,
                phone,
                address,
                city,
                state,
                pincode,
                website,
                user_id
            ))

            # ----------------------------------------------------
            # UPDATE CONTACT PERSON
            # ----------------------------------------------------

            cursor.execute("""
                UPDATE users
                SET name = %s
                WHERE id = %s
                  AND role = 'COLLEGE'
            """, (
                contact_person,
                user_id
            ))

            conn.commit()

            # Keep session name synchronized
            session["user_name"] = contact_person
            session["name"] = contact_person

            flash(
                "College profile updated successfully.",
                "success"
            )

            return redirect(url_for("college_profile"))

        # --------------------------------------------------------
        # GET REQUEST
        # --------------------------------------------------------

        return render_template(
            "college/profile/edit.html",
            college=college,
            profile="profile"
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("COLLEGE PROFILE UPDATE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update college profile.",
            "error"
        )

        return redirect(url_for("college_profile"))

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("COLLEGE PROFILE UPDATE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update college profile.",
            "error"
        )

        return redirect(url_for("college_profile"))

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ============================================================
# COLLEGE DEPARTMENTS
# ============================================================

@app.route("/college/departments")
@college_required
def college_departments():
    conn = None
    cursor = None

    try:
        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get current college
        cursor.execute("""
            SELECT id, college_name, college_code, status
            FROM colleges
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("login"))

        if college["status"] != "ACTIVE":
            session.clear()
            flash("Your college account is not active.", "error")
            return redirect(url_for("login"))

        college_id = college["id"]

        # Department list with student count
        cursor.execute("""
            SELECT
                d.id,
                d.department_name,
                d.department_code,
                d.description,
                d.status,
                d.created_at,
                d.updated_at,
                COUNT(s.id) AS student_count
            FROM departments d
            LEFT JOIN students s
                ON s.department_id = d.id
            WHERE d.college_id = %s
            GROUP BY
                d.id,
                d.department_name,
                d.department_code,
                d.description,
                d.status,
                d.created_at,
                d.updated_at
            ORDER BY d.department_name ASC
        """, (college_id,))

        departments = cursor.fetchall()

        # Statistics
        total_departments = len(departments)

        active_departments = sum(
            1 for d in departments
            if d["status"] == "ACTIVE"
        )

        inactive_departments = sum(
            1 for d in departments
            if d["status"] == "INACTIVE"
        )

        total_department_students = sum(
            d["student_count"] or 0
            for d in departments
        )

        return render_template(
            "college/departments/list.html",
            dashboard="departments",
            college=college,
            departments=departments,
            total_departments=total_departments,
            active_departments=active_departments,
            inactive_departments=inactive_departments,
            total_department_students=total_department_students
        )

    except mysql.connector.Error as e:

        print("COLLEGE DEPARTMENTS DATABASE ERROR:", e)

        flash(
            "Unable to load departments.",
            "error"
        )

        return redirect(url_for("college_dashboard"))

    except Exception as e:

        print("COLLEGE DEPARTMENTS ERROR:", e)

        flash(
            "Unable to load departments.",
            "error"
        )

        return redirect(url_for("college_dashboard"))

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# ADD DEPARTMENT
# ============================================================

@app.route("/college/departments/add", methods=["GET", "POST"])
@college_required
def college_department_add():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, college_name, college_code, status
            FROM colleges
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("login"))

        if college["status"] != "ACTIVE":
            session.clear()
            flash("Your college account is not active.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":

            department_name = request.form.get(
                "department_name", ""
            ).strip()

            department_code = request.form.get(
                "department_code", ""
            ).strip().upper()

            description = request.form.get(
                "description", ""
            ).strip()

            status = request.form.get(
                "status",
                "ACTIVE"
            ).strip().upper()

            errors = []

            if not department_name:
                errors.append(
                    "Department name is required."
                )

            if not department_code:
                errors.append(
                    "Department code is required."
                )

            elif not department_code.replace("-", "").replace("_", "").isalnum():
                errors.append(
                    "Department code contains invalid characters."
                )

            if status not in ["ACTIVE", "INACTIVE"]:
                errors.append(
                    "Invalid department status."
                )

            # Duplicate code within same college
            cursor.execute("""
                SELECT id
                FROM departments
                WHERE college_id = %s
                  AND department_code = %s
                LIMIT 1
            """, (
                college["id"],
                department_code
            ))

            existing = cursor.fetchone()

            if existing:
                errors.append(
                    "This department code already exists."
                )

            if errors:

                for error in errors:
                    flash(error, "error")

                department = {
                    "department_name": department_name,
                    "department_code": department_code,
                    "description": description,
                    "status": status
                }

                return render_template(
                    "college/departments/add.html",
                    dashboard="departments",
                    college=college,
                    department=department
                )

            cursor.execute("""
                INSERT INTO departments
                (
                    id,
                    college_id,
                    department_name,
                    department_code,
                    description,
                    status
                )
                VALUES
                (
                    UUID(),
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                college["id"],
                department_name,
                department_code,
                description or None,
                status
            ))

            conn.commit()

            flash(
                "Department added successfully.",
                "success"
            )

            return redirect(
                url_for("college_departments")
            )

        return render_template(
            "college/departments/add.html",
            dashboard="departments",
            college=college,
            department={}
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("ADD DEPARTMENT DATABASE ERROR:", e)

        flash(
            "Unable to add department.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("ADD DEPARTMENT ERROR:", e)

        flash(
            "Unable to add department.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# EDIT DEPARTMENT
# ============================================================

@app.route(
    "/college/departments/<string:department_id>/edit",
    methods=["GET", "POST"]
)
@college_required
def college_department_edit(department_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Current college
        cursor.execute("""
            SELECT id, college_name, college_code, status
            FROM colleges
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("login"))

        # Department must belong to current college
        cursor.execute("""
            SELECT
                id,
                college_id,
                department_name,
                department_code,
                description,
                status,
                created_at,
                updated_at
            FROM departments
            WHERE id = %s
              AND college_id = %s
            LIMIT 1
        """, (
            department_id,
            college["id"]
        ))

        department = cursor.fetchone()

        if not department:
            flash(
                "Department not found.",
                "error"
            )
            return redirect(
                url_for("college_departments")
            )

        if request.method == "POST":

            department_name = request.form.get(
                "department_name", ""
            ).strip()

            department_code = request.form.get(
                "department_code", ""
            ).strip().upper()

            description = request.form.get(
                "description", ""
            ).strip()

            status = request.form.get(
                "status",
                "ACTIVE"
            ).strip().upper()

            errors = []

            if not department_name:
                errors.append(
                    "Department name is required."
                )

            if not department_code:
                errors.append(
                    "Department code is required."
                )

            if status not in [
                "ACTIVE",
                "INACTIVE"
            ]:
                errors.append(
                    "Invalid department status."
                )

            # Duplicate code excluding current department
            cursor.execute("""
                SELECT id
                FROM departments
                WHERE college_id = %s
                  AND department_code = %s
                  AND id != %s
                LIMIT 1
            """, (
                college["id"],
                department_code,
                department_id
            ))

            duplicate = cursor.fetchone()

            if duplicate:
                errors.append(
                    "Another department already uses this code."
                )

            if errors:

                for error in errors:
                    flash(error, "error")

                department["department_name"] = department_name
                department["department_code"] = department_code
                department["description"] = description
                department["status"] = status

                return render_template(
                    "college/departments/edit.html",
                    dashboard="departments",
                    college=college,
                    department=department
                )

            cursor.execute("""
                UPDATE departments
                SET
                    department_name = %s,
                    department_code = %s,
                    description = %s,
                    status = %s
                WHERE id = %s
                  AND college_id = %s
            """, (
                department_name,
                department_code,
                description or None,
                status,
                department_id,
                college["id"]
            ))

            conn.commit()

            flash(
                "Department updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "college_department_detail",
                    department_id=department_id
                )
            )

        return render_template(
            "college/departments/edit.html",
            dashboard="departments",
            college=college,
            department=department
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("EDIT DEPARTMENT DATABASE ERROR:", e)

        flash(
            "Unable to update department.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("EDIT DEPARTMENT ERROR:", e)

        flash(
            "Unable to update department.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# DEPARTMENT DETAIL
# ============================================================

@app.route(
    "/college/departments/<string:department_id>"
)
@college_required
def college_department_detail(department_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Current college
        cursor.execute("""
            SELECT
                id,
                college_name,
                college_code,
                status
            FROM colleges
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash(
                "College profile not found.",
                "error"
            )
            return redirect(url_for("login"))

        # Department
        cursor.execute("""
            SELECT
                d.id,
                d.college_id,
                d.department_name,
                d.department_code,
                d.description,
                d.status,
                d.created_at,
                d.updated_at,
                COUNT(s.id) AS student_count
            FROM departments d
            LEFT JOIN students s
                ON s.department_id = d.id
            WHERE d.id = %s
              AND d.college_id = %s
            GROUP BY
                d.id,
                d.college_id,
                d.department_name,
                d.department_code,
                d.description,
                d.status,
                d.created_at,
                d.updated_at
            LIMIT 1
        """, (
            department_id,
            college["id"]
        ))

        department = cursor.fetchone()

        if not department:

            flash(
                "Department not found.",
                "error"
            )

            return redirect(
                url_for("college_departments")
            )

        # Students of department
        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.phone,
                s.created_at,
                u.name,
                u.email,
                u.status AS user_status
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.college_id = %s
              AND s.department_id = %s
            ORDER BY s.created_at DESC
        """, (
            college["id"],
            department_id
        ))

        students = cursor.fetchall()

        return render_template(
            "college/departments/detail.html",
            dashboard="departments",
            college=college,
            department=department,
            students=students
        )

    except mysql.connector.Error as e:

        print(
            "DEPARTMENT DETAIL DATABASE ERROR:",
            e
        )

        flash(
            "Unable to load department details.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    except Exception as e:

        print(
            "DEPARTMENT DETAIL ERROR:",
            e
        )

        flash(
            "Unable to load department details.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# DELETE DEPARTMENT
# ============================================================

@app.route(
    "/college/departments/<string:department_id>/delete",
    methods=["POST"]
)
@college_required
def college_department_delete(department_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Current college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash(
                "College profile not found.",
                "error"
            )
            return redirect(url_for("login"))

        college_id = college["id"]

        # Check department
        cursor.execute("""
            SELECT
                id,
                department_name
            FROM departments
            WHERE id = %s
              AND college_id = %s
            LIMIT 1
        """, (
            department_id,
            college_id
        ))

        department = cursor.fetchone()

        if not department:

            flash(
                "Department not found.",
                "error"
            )

            return redirect(
                url_for("college_departments")
            )

        # Don't delete if students are assigned
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE department_id = %s
        """, (department_id,))

        student_count = cursor.fetchone()["total"] or 0

        if student_count > 0:

            flash(
                "Department cannot be deleted because "
                f"{student_count} student(s) are assigned to it. "
                "Reassign the students first.",
                "error"
            )

            return redirect(
                url_for(
                    "college_department_detail",
                    department_id=department_id
                )
            )

        cursor.execute("""
            DELETE FROM departments
            WHERE id = %s
              AND college_id = %s
        """, (
            department_id,
            college_id
        ))

        conn.commit()

        flash(
            "Department deleted successfully.",
            "success"
        )

        return redirect(
            url_for("college_departments")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print(
            "DELETE DEPARTMENT DATABASE ERROR:",
            e
        )

        flash(
            "Unable to delete department.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "DELETE DEPARTMENT ERROR:",
            e
        )

        flash(
            "Unable to delete department.",
            "error"
        )

        return redirect(
            url_for("college_departments")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# STUDENTS
# =========================================================
@app.route("/college/students")
@college_required
def college_students():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Student statistics
        cursor.execute("""
            SELECT COUNT(*) AS total_students
            FROM students
            WHERE college_id = %s
        """, (college_id,))

        total_students = cursor.fetchone()["total_students"]

        cursor.execute("""
            SELECT COUNT(*) AS active_students
            FROM students s
            INNER JOIN users u ON s.user_id = u.id
            WHERE s.college_id = %s
              AND u.status = 'ACTIVE'
        """, (college_id,))

        active_students = cursor.fetchone()["active_students"]

        cursor.execute("""
            SELECT COUNT(*) AS inactive_students
            FROM students s
            INNER JOIN users u ON s.user_id = u.id
            WHERE s.college_id = %s
              AND u.status != 'ACTIVE'
        """, (college_id,))

        inactive_students = cursor.fetchone()["inactive_students"]

        # Department count
        cursor.execute("""
            SELECT COUNT(DISTINCT department_id) AS department_count
            FROM students
            WHERE college_id = %s
              AND department_id IS NOT NULL
        """, (college_id,))

        department_count = cursor.fetchone()["department_count"]

        # Students list
        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.phone,
                s.department_id,
                s.created_at,

                u.name,
                u.email,
                u.status AS user_status,

                d.department_name,
                d.department_code

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN departments d
                ON s.department_id = d.id
                AND d.college_id = %s

            WHERE s.college_id = %s

            ORDER BY s.created_at DESC
        """, (college_id, college_id))

        students = cursor.fetchall()

        return render_template(
            "college/students/list.html",
            students=students,
            total_students=total_students,
            active_students=active_students,
            inactive_students=inactive_students,
            department_count=department_count,
            dashboard="students"
        )

    except Exception as e:
        print("College Students Error:", e)
        flash("Unable to load students.", "error")
        return redirect(url_for("college_dashboard"))

    finally:
        cursor.close()
        conn.close()

@app.route("/college/students/<string:student_id>")
@college_required
def college_student_detail(student_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Student detail
        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.phone,
                s.department_id,
                s.created_at,

                u.name,
                u.email,
                u.status AS user_status,

                d.department_name,
                d.department_code

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN departments d
                ON s.department_id = d.id
                AND d.college_id = %s

            WHERE s.id = %s
              AND s.college_id = %s

            LIMIT 1
        """, (college_id, student_id, college_id))

        student = cursor.fetchone()

        if not student:
            flash("Student not found.", "error")
            return redirect(url_for("college_students"))

        return render_template(
            "college/students/detail.html",
            student=student,
            dashboard="students"
        )

    except Exception as e:
        print("College Student Detail Error:", e)
        flash("Unable to load student details.", "error")
        return redirect(url_for("college_students"))

    finally:
        cursor.close()
        conn.close()

@app.route("/college/industries")
@college_required
def college_industries():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        # Existing active industries
        cursor.execute("""
            SELECT
                i.id,
                i.user_id,
                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.phone,
                i.email,
                i.website,
                i.address,
                i.city,
                i.state,
                i.description,
                i.status,
                i.created_at,
                i.updated_at,

                u.name AS account_name,
                u.email AS account_email,
                u.status AS user_status

            FROM industries i

            INNER JOIN users u
                ON i.user_id = u.id

            WHERE i.status = 'ACTIVE'

            ORDER BY i.company_name ASC
        """)

        industries = cursor.fetchall()

        # Total active industries
        total_industries = len(industries)

        # Company / industry types
        cursor.execute("""
            SELECT COUNT(DISTINCT company_type) AS total_types
            FROM industries
            WHERE status = 'ACTIVE'
              AND company_type IS NOT NULL
              AND company_type != ''
        """)

        total_types = cursor.fetchone()["total_types"]

        # Cities represented
        cursor.execute("""
            SELECT COUNT(DISTINCT city) AS total_cities
            FROM industries
            WHERE status = 'ACTIVE'
              AND city IS NOT NULL
              AND city != ''
        """)

        total_cities = cursor.fetchone()["total_cities"]

        # Industries with website
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM industries
            WHERE status = 'ACTIVE'
              AND website IS NOT NULL
              AND website != ''
        """)

        industries_with_website = cursor.fetchone()["total"]

        return render_template(
            "college/industries/list.html",
            industries=industries,
            total_industries=total_industries,
            total_types=total_types,
            total_cities=total_cities,
            industries_with_website=industries_with_website,
            dashboard="industries"
        )

    except Exception as e:
        print("College Industries Error:", repr(e))
        raise

    finally:
        cursor.close()
        conn.close()

@app.route("/college/industries/<string:industry_id>")
@college_required
def college_industry_detail(industry_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        # Existing active industry
        cursor.execute("""
            SELECT
                i.id,
                i.user_id,
                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.phone,
                i.email,
                i.website,
                i.address,
                i.city,
                i.state,
                i.description,
                i.status,
                i.created_at,
                i.updated_at,

                u.name AS account_name,
                u.email AS account_email,
                u.status AS user_status

            FROM industries i

            INNER JOIN users u
                ON i.user_id = u.id

            WHERE i.id = %s
              AND i.status = 'ACTIVE'

            LIMIT 1
        """, (industry_id,))

        industry = cursor.fetchone()

        if not industry:
            flash("Industry not found.", "error")
            return redirect(url_for("college_industries"))

        return render_template(
            "college/industries/detail.html",
            industry=industry,
            dashboard="industries"
        )

    except Exception as e:
        print("College Industry Detail Error:", repr(e))
        raise

    finally:
        cursor.close()
        conn.close()

#------------------------------
#REQUESTS
#------------------------------
@app.route("/college/requests/sent")
@college_required
def college_sent_requests():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Requests initiated by this college
        cursor.execute("""
            SELECT
                c.id,
                c.college_id,
                c.industry_id,
                c.initiated_by,
                c.title,
                c.description,
                c.collaboration_type,
                c.start_date,
                c.end_date,
                c.status,
                c.created_at,
                c.updated_at,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.email AS industry_email,
                i.phone AS industry_phone,
                i.city AS industry_city,
                i.state AS industry_state

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.college_id = %s
              AND c.initiated_by = 'COLLEGE'

            ORDER BY c.created_at DESC
        """, (college_id,))

        requests = cursor.fetchall()

        # Statistics
        total_requests = len(requests)
        pending_requests = sum(
            1 for request in requests
            if request["status"] == "PENDING"
        )
        active_requests = sum(
            1 for request in requests
            if request["status"] == "ACTIVE"
        )
        completed_requests = sum(
            1 for request in requests
            if request["status"] == "COMPLETED"
        )

        return render_template(
            "college/requests/sent.html",
            requests=requests,
            total_requests=total_requests,
            pending_requests=pending_requests,
            active_requests=active_requests,
            completed_requests=completed_requests,
            dashboard="requests"
        )

    except Exception as e:
        print("College Sent Requests Error:", repr(e))
        raise

    finally:
        cursor.close()
        conn.close()

@app.route("/college/requests/received")
@college_required
def college_received_requests():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Requests initiated by industries
        cursor.execute("""
            SELECT
                c.id,
                c.college_id,
                c.industry_id,
                c.initiated_by,
                c.title,
                c.description,
                c.collaboration_type,
                c.start_date,
                c.end_date,
                c.status,
                c.created_at,
                c.updated_at,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.email AS industry_email,
                i.phone AS industry_phone,
                i.city AS industry_city,
                i.state AS industry_state

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.college_id = %s
              AND c.initiated_by = 'INDUSTRY'

            ORDER BY c.created_at DESC
        """, (college_id,))

        requests = cursor.fetchall()

        # Statistics
        total_requests = len(requests)
        pending_requests = sum(
            1 for request in requests
            if request["status"] == "PENDING"
        )
        active_requests = sum(
            1 for request in requests
            if request["status"] == "ACTIVE"
        )
        completed_requests = sum(
            1 for request in requests
            if request["status"] == "COMPLETED"
        )

        return render_template(
            "college/requests/received.html",
            requests=requests,
            total_requests=total_requests,
            pending_requests=pending_requests,
            active_requests=active_requests,
            completed_requests=completed_requests,
            dashboard="requests"
        )

    except Exception as e:
        print("College Received Requests Error:", repr(e))
        raise

    finally:
        cursor.close()
        conn.close()

@app.route("/college/requests/<string:request_id>")
@college_required
def college_request_detail(request_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT
                c.id,
                c.college_name
            FROM colleges c
            WHERE c.user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Get request belonging to this college
        cursor.execute("""
            SELECT
                c.id,
                c.college_id,
                c.industry_id,
                c.initiated_by,
                c.title,
                c.description,
                c.collaboration_type,
                c.start_date,
                c.end_date,
                c.status,
                c.created_at,
                c.updated_at,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.phone AS industry_phone,
                i.email AS industry_email,
                i.website AS industry_website,
                i.address AS industry_address,
                i.city AS industry_city,
                i.state AS industry_state,
                i.description AS industry_description

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.id = %s
              AND c.college_id = %s

            LIMIT 1
        """, (request_id, college_id))

        request = cursor.fetchone()

        if not request:
            flash("Collaboration request not found.", "error")
            return redirect(url_for("college_sent_requests"))

        return render_template(
            "college/requests/detail.html",
            request=request,
            dashboard="requests"
        )

    except Exception as e:
        print("College Request Detail Error:", repr(e))
        raise

    finally:
        cursor.close()
        conn.close()

@app.route("/college/collaborations")
@college_required
def college_collaborations():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Get collaborations belonging to this college
        cursor.execute("""
            SELECT
                c.id,
                c.college_id,
                c.industry_id,
                c.initiated_by,
                c.title,
                c.description,
                c.collaboration_type,
                c.start_date,
                c.end_date,
                c.status,
                c.created_at,
                c.updated_at,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.phone AS industry_phone,
                i.email AS industry_email,
                i.website,
                i.address AS industry_address,
                i.city AS industry_city,
                i.state AS industry_state

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.college_id = %s

            ORDER BY c.created_at DESC
        """, (college_id,))

        collaborations = cursor.fetchall()

        # Stats
        total_collaborations = len(collaborations)

        active_collaborations = sum(
            1 for c in collaborations
            if c["status"] == "ACTIVE"
        )

        completed_collaborations = sum(
            1 for c in collaborations
            if c["status"] == "COMPLETED"
        )

        pending_collaborations = sum(
            1 for c in collaborations
            if c["status"] == "PENDING"
        )

        return render_template(
            "college/collaborations/list.html",
            collaborations=collaborations,
            total_collaborations=total_collaborations,
            active_collaborations=active_collaborations,
            completed_collaborations=completed_collaborations,
            pending_collaborations=pending_collaborations,
            dashboard="collaborations"
        )

    except Exception as e:
        print("College Collaborations Error:", e)
        flash("Unable to load collaborations.", "error")
        return redirect(url_for("college_dashboard"))

    finally:
        cursor.close()
        conn.close()


@app.route("/college/collaborations/<string:collaboration_id>")
@college_required
def college_collaboration_detail(collaboration_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get logged-in college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (session["user_id"],))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Get collaboration
        cursor.execute("""
            SELECT
                c.id,
                c.college_id,
                c.industry_id,
                c.initiated_by,
                c.title,
                c.description,
                c.collaboration_type,
                c.start_date,
                c.end_date,
                c.status,
                c.created_at,
                c.updated_at,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.phone AS industry_phone,
                i.email AS industry_email,
                i.website,
                i.address AS industry_address,
                i.city AS industry_city,
                i.state AS industry_state

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.id = %s
              AND c.college_id = %s

            LIMIT 1
        """, (collaboration_id, college_id))

        collaboration = cursor.fetchone()

        if not collaboration:
            flash("Collaboration not found.", "error")
            return redirect(url_for("college_collaborations"))

        return render_template(
            "college/collaborations/detail.html",
            collaboration=collaboration,
            dashboard="collaborations"
        )

    except Exception as e:
        print("College Collaboration Detail Error:", e)
        flash("Unable to load collaboration details.", "error")
        return redirect(url_for("college_collaborations"))

    finally:
        cursor.close()
        conn.close()

# ============================================================
# COLLEGE — PROJECTS & ACTIVITIES
# ============================================================

@app.route("/college/activities")
@college_required
def college_activities():
    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get current college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Get all projects belonging to students of this college
        cursor.execute("""
            SELECT
                p.id,
                p.student_id,
                p.industry_id,
                p.title,
                p.description,
                p.technology_stack,
                p.start_date,
                p.end_date,
                p.status,
                p.project_url,
                p.report_url,
                p.created_at,
                p.updated_at,

                s.enrollment_no,
                s.course,
                s.branch,

                u.name AS student_name,
                u.email AS student_email,

                d.department_name,
                d.department_code,

                i.company_name,
                i.company_type,
                i.industry_sector

            FROM student_projects p

            INNER JOIN students s
                ON p.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN departments d
                ON s.department_id = d.id
                AND d.college_id = %s

            LEFT JOIN industries i
                ON p.industry_id = i.id

            WHERE s.college_id = %s

            ORDER BY p.created_at DESC
        """, (college_id, college_id))

        projects = cursor.fetchall()

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        total_projects = len(projects)

        ongoing_projects = sum(
            1 for p in projects
            if p["status"] == "ONGOING"
        )

        completed_projects = sum(
            1 for p in projects
            if p["status"] == "COMPLETED"
        )

        cancelled_projects = sum(
            1 for p in projects
            if p["status"] == "CANCELLED"
        )

        return render_template(
            "college/activities/list.html",
            dashboard="activities",
            projects=projects,
            total_projects=total_projects,
            ongoing_projects=ongoing_projects,
            completed_projects=completed_projects,
            cancelled_projects=cancelled_projects
        )

    finally:
        cursor.close()
        conn.close()


# ============================================================
# ADD PROJECT
# ============================================================

@app.route("/college/activities/add", methods=["GET", "POST"])
@college_required
def college_activity_add():

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get current college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            student_id = request.form.get("student_id", "").strip()
            industry_id = request.form.get("industry_id", "").strip() or None
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            technology_stack = request.form.get("technology_stack", "").strip()
            start_date = request.form.get("start_date", "").strip() or None
            end_date = request.form.get("end_date", "").strip() or None
            status = request.form.get("status", "ONGOING").strip()
            project_url = request.form.get("project_url", "").strip() or None
            report_url = request.form.get("report_url", "").strip() or None

            # Required field validation
            if not student_id or not title:
                flash("Student and project title are required.", "error")
                return redirect(url_for("college_activity_add"))

            # Validate student belongs to current college
            cursor.execute("""
                SELECT id
                FROM students
                WHERE id = %s
                AND college_id = %s
            """, (student_id, college_id))

            student = cursor.fetchone()

            if not student:
                flash("Invalid student selected.", "error")
                return redirect(url_for("college_activity_add"))

            # Validate industry if provided
            if industry_id:

                cursor.execute("""
                    SELECT id
                    FROM industries
                    WHERE id = %s
                    AND status = 'ACTIVE'
                """, (industry_id,))

                industry = cursor.fetchone()

                if not industry:
                    flash("Invalid industry selected.", "error")
                    return redirect(url_for("college_activity_add"))

            # Validate status
            allowed_statuses = {
                "ONGOING",
                "COMPLETED",
                "CANCELLED"
            }

            if status not in allowed_statuses:
                flash("Invalid project status.", "error")
                return redirect(url_for("college_activity_add"))

            # Validate dates
            if start_date and end_date and end_date < start_date:
                flash("End date cannot be before start date.", "error")
                return redirect(url_for("college_activity_add"))

            # Insert project
            project_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO student_projects (
                    id,
                    student_id,
                    industry_id,
                    title,
                    description,
                    technology_stack,
                    start_date,
                    end_date,
                    status,
                    project_url,
                    report_url
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
            """, (
                project_id,
                student_id,
                industry_id,
                title,
                description or None,
                technology_stack or None,
                start_date,
                end_date,
                status,
                project_url,
                report_url
            ))

            conn.commit()

            flash("Project added successfully.", "success")

            return redirect(
                url_for(
                    "college_activity_detail",
                    activity_id=project_id
                )
            )

        # ----------------------------------------------------
        # GET — Students
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                u.name AS student_name
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.college_id = %s
            ORDER BY u.name ASC
        """, (college_id,))

        students = cursor.fetchall()

        # ----------------------------------------------------
        # GET — Active Industries
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                company_name,
                company_type,
                industry_sector
            FROM industries
            WHERE status = 'ACTIVE'
            ORDER BY company_name ASC
        """)

        industries = cursor.fetchall()

        return render_template(
            "college/activities/add.html",
            dashboard="activities",
            students=students,
            industries=industries
        )

    finally:
        cursor.close()
        conn.close()


# ============================================================
# EDIT PROJECT
# ============================================================

@app.route(
    "/college/activities/<string:activity_id>/edit",
    methods=["GET", "POST"]
)
@college_required
def college_activity_edit(activity_id):

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get current college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Get project and verify ownership through student
        cursor.execute("""
            SELECT
                p.*
            FROM student_projects p
            INNER JOIN students s
                ON p.student_id = s.id
            WHERE p.id = %s
            AND s.college_id = %s
        """, (activity_id, college_id))

        project = cursor.fetchone()

        if not project:
            flash("Project not found.", "error")
            return redirect(url_for("college_activities"))

        # ----------------------------------------------------
        # POST
        # ----------------------------------------------------

        if request.method == "POST":

            student_id = request.form.get("student_id", "").strip()
            industry_id = request.form.get("industry_id", "").strip() or None
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            technology_stack = request.form.get("technology_stack", "").strip()
            start_date = request.form.get("start_date", "").strip() or None
            end_date = request.form.get("end_date", "").strip() or None
            status = request.form.get("status", "ONGOING").strip()
            project_url = request.form.get("project_url", "").strip() or None
            report_url = request.form.get("report_url", "").strip() or None

            if not student_id or not title:
                flash("Student and project title are required.", "error")
                return redirect(
                    url_for(
                        "college_activity_edit",
                        activity_id=activity_id
                    )
                )

            # Student must belong to this college
            cursor.execute("""
                SELECT id
                FROM students
                WHERE id = %s
                AND college_id = %s
            """, (student_id, college_id))

            if not cursor.fetchone():
                flash("Invalid student selected.", "error")
                return redirect(
                    url_for(
                        "college_activity_edit",
                        activity_id=activity_id
                    )
                )

            # Industry validation
            if industry_id:

                cursor.execute("""
                    SELECT id
                    FROM industries
                    WHERE id = %s
                    AND status = 'ACTIVE'
                """, (industry_id,))

                if not cursor.fetchone():
                    flash("Invalid industry selected.", "error")
                    return redirect(
                        url_for(
                            "college_activity_edit",
                            activity_id=activity_id
                        )
                    )

            allowed_statuses = {
                "ONGOING",
                "COMPLETED",
                "CANCELLED"
            }

            if status not in allowed_statuses:
                flash("Invalid project status.", "error")
                return redirect(
                    url_for(
                        "college_activity_edit",
                        activity_id=activity_id
                    )
                )

            if start_date and end_date and end_date < start_date:
                flash("End date cannot be before start date.", "error")
                return redirect(
                    url_for(
                        "college_activity_edit",
                        activity_id=activity_id
                    )
                )

            # Update
            cursor.execute("""
                UPDATE student_projects
                SET
                    student_id = %s,
                    industry_id = %s,
                    title = %s,
                    description = %s,
                    technology_stack = %s,
                    start_date = %s,
                    end_date = %s,
                    status = %s,
                    project_url = %s,
                    report_url = %s
                WHERE id = %s
            """, (
                student_id,
                industry_id,
                title,
                description or None,
                technology_stack or None,
                start_date,
                end_date,
                status,
                project_url,
                report_url,
                activity_id
            ))

            conn.commit()

            flash("Project updated successfully.", "success")

            return redirect(
                url_for(
                    "college_activity_detail",
                    activity_id=activity_id
                )
            )

        # ----------------------------------------------------
        # GET — Students
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                u.name AS student_name
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.college_id = %s
            ORDER BY u.name ASC
        """, (college_id,))

        students = cursor.fetchall()

        # ----------------------------------------------------
        # GET — Industries
        # ----------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                company_name,
                company_type,
                industry_sector
            FROM industries
            WHERE status = 'ACTIVE'
            ORDER BY company_name ASC
        """)

        industries = cursor.fetchall()

        return render_template(
            "college/activities/edit.html",
            dashboard="activities",
            project=project,
            students=students,
            industries=industries
        )

    finally:
        cursor.close()
        conn.close()


# ============================================================
# PROJECT DETAIL
# ============================================================

@app.route("/college/activities/<string:activity_id>")
@college_required
def college_activity_detail(activity_id):

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Current college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Project detail with student + department + industry
        cursor.execute("""
            SELECT
                p.id,
                p.student_id,
                p.industry_id,
                p.title,
                p.description,
                p.technology_stack,
                p.start_date,
                p.end_date,
                p.status,
                p.project_url,
                p.report_url,
                p.created_at,
                p.updated_at,

                s.enrollment_no,
                s.course,
                s.branch,
                s.phone,

                u.name AS student_name,
                u.email AS student_email,

                d.department_name,
                d.department_code,

                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.designation,
                i.email AS industry_email,
                i.phone AS industry_phone,
                i.website,
                i.address AS industry_address,
                i.city AS industry_city,
                i.state AS industry_state

            FROM student_projects p

            INNER JOIN students s
                ON p.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN departments d
                ON s.department_id = d.id
                AND d.college_id = %s

            LEFT JOIN industries i
                ON p.industry_id = i.id

            WHERE p.id = %s
            AND s.college_id = %s
        """, (college_id, activity_id, college_id))

        project = cursor.fetchone()

        if not project:
            flash("Project not found.", "error")
            return redirect(url_for("college_activities"))

        return render_template(
            "college/activities/detail.html",
            dashboard="activities",
            project=project
        )

    finally:
        cursor.close()
        conn.close()


# ============================================================
# DELETE PROJECT
# ============================================================

@app.route(
    "/college/activities/<string:activity_id>/delete",
    methods=["POST"]
)
@college_required
def college_activity_delete(activity_id):

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Current college
        cursor.execute("""
            SELECT id
            FROM colleges
            WHERE user_id = %s
        """, (user_id,))

        college = cursor.fetchone()

        if not college:
            flash("College profile not found.", "error")
            return redirect(url_for("college_dashboard"))

        college_id = college["id"]

        # Verify ownership
        cursor.execute("""
            SELECT p.id
            FROM student_projects p
            INNER JOIN students s
                ON p.student_id = s.id
            WHERE p.id = %s
            AND s.college_id = %s
        """, (activity_id, college_id))

        project = cursor.fetchone()

        if not project:
            flash("Project not found.", "error")
            return redirect(url_for("college_activities"))

        cursor.execute("""
            DELETE FROM student_projects
            WHERE id = %s
        """, (activity_id,))

        conn.commit()

        flash("Project deleted successfully.", "success")

        return redirect(url_for("college_activities"))

    finally:
        cursor.close()
        conn.close()

# ============================================================
# COLLEGE — NOTIFICATIONS
# ============================================================

@app.route("/college/notifications")
@college_required
def college_notifications():

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                id,
                user_id,
                title,
                message,
                notification_type,
                is_read,
                created_at
            FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))

        notifications = cursor.fetchall()

        unread_count = sum(
            1 for notification in notifications
            if not notification["is_read"]
        )

        total_count = len(notifications)

        return render_template(
            "college/notifications/list.html",
            dashboard="notifications",
            notifications=notifications,
            unread_count=unread_count,
            total_count=total_count
        )

    finally:
        cursor.close()
        conn.close()


# ============================================================
# MARK SINGLE NOTIFICATION AS READ
# ============================================================

@app.route(
    "/college/notifications/<string:notification_id>/read",
    methods=["POST"]
)
@college_required
def college_notification_mark_read(notification_id):

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = %s
            AND user_id = %s
        """, (notification_id, user_id))

        conn.commit()

        return redirect(
            url_for("college_notifications")
        )

    finally:
        cursor.close()
        conn.close()


# ============================================================
# MARK ALL NOTIFICATIONS AS READ
# ============================================================

@app.route(
    "/college/notifications/mark-all-read",
    methods=["POST"]
)
@college_required
def college_notifications_mark_all_read():

    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = %s
            AND is_read = 0
        """, (user_id,))

        conn.commit()

        flash("All notifications marked as read.", "success")

        return redirect(
            url_for("college_notifications")
        )

    finally:
        cursor.close()
        conn.close()

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
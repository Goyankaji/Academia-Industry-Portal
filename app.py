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
from datetime import datetime


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
# STUDENT AUTHENTICATION DECORATOR
# =========================================================

def student_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        # -------------------------------------------------
        # LOGIN CHECK
        # -------------------------------------------------

        if "user_id" not in session:

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        # -------------------------------------------------
        # ROLE CHECK
        # -------------------------------------------------

        if session.get("role") != "STUDENT":

            flash(
                "Student access required.",
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
            # PLACEMENT CELL
            # -------------------------------------------------

            if user["role"] == "PLACEMENT_CELL":

                return redirect(
                    url_for("placement_dashboard")
                )
            
            # -------------------------------------------------
            # STUDENT
            # -------------------------------------------------

            if user["role"] == "STUDENT":

                return redirect(
                    url_for("student_dashboard")
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
# PLACEMENT CELL AUTHENTICATION DECORATOR
# =========================================================

def placement_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # -------------------------------------------------
        # LOGIN CHECK
        # -------------------------------------------------

        if "user_id" not in session:

            flash(
                "Please login first.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # -------------------------------------------------
        # ROLE CHECK
        # -------------------------------------------------

        if session.get("role") != "PLACEMENT_CELL":

            flash(
                "Placement Cell access required.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        conn = None
        cursor = None

        try:

            conn = get_db_connection()

            cursor = conn.cursor(
                dictionary=True
            )


            # -------------------------------------------------
            # GET CURRENT PLACEMENT CELL
            # -------------------------------------------------

            cursor.execute("""
                SELECT
                    pc.id AS placement_cell_id,
                    pc.college_id,
                    pc.status AS placement_cell_status,

                    u.status AS user_status,

                    c.college_name,
                    c.college_code,
                    c.status AS college_status

                FROM placement_cells pc

                INNER JOIN users u
                    ON pc.user_id = u.id

                INNER JOIN colleges c
                    ON pc.college_id = c.id

                WHERE pc.user_id = %s

                LIMIT 1
            """, (
                session["user_id"],
            ))

            placement_cell = cursor.fetchone()


            # -------------------------------------------------
            # PLACEMENT CELL NOT FOUND
            # -------------------------------------------------

            if not placement_cell:

                session.clear()

                flash(
                    "Placement Cell profile not found.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )


            # -------------------------------------------------
            # ACCOUNT STATUS CHECK
            # -------------------------------------------------

            if (
                placement_cell["user_status"] != "ACTIVE"
                or placement_cell["placement_cell_status"] != "ACTIVE"
                or placement_cell["college_status"] != "ACTIVE"
            ):

                session.clear()

                flash(
                    "Your Placement Cell account is not active.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )


            # -------------------------------------------------
            # STORE PLACEMENT CONTEXT IN SESSION
            # -------------------------------------------------

            session["placement_cell_id"] = (
                placement_cell["placement_cell_id"]
            )

            session["college_id"] = (
                placement_cell["college_id"]
            )

            session["college_name"] = (
                placement_cell["college_name"]
            )

            session["college_code"] = (
                placement_cell["college_code"]
            )


            return f(*args, **kwargs)


        except mysql.connector.Error as e:

            print("=" * 70)
            print("PLACEMENT AUTH DATABASE ERROR:")
            print(type(e).__name__)
            print(e)
            print("=" * 70)

            flash(
                "Unable to verify Placement Cell access.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        except Exception as e:

            print("=" * 70)
            print("PLACEMENT AUTH ERROR:")
            print(type(e).__name__)
            print(e)
            print("=" * 70)

            flash(
                "Unable to verify Placement Cell access.",
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


    return decorated_function

# =========================================================
# PLACEMENT CELL DASHBOARD
# =========================================================

# =========================================================
# PLACEMENT CELL DASHBOARD
# =========================================================

@app.route("/placement/dashboard")
@placement_required
def placement_dashboard():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Placement Cell session expired. Please login again.",
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
        # CURRENT PLACEMENT CELL
        # =================================================

        cursor.execute("""
            SELECT

                pc.id AS placement_cell_id,
                pc.user_id,
                pc.college_id,
                pc.status AS placement_cell_status,

                u.name AS representative_name,
                u.email AS account_email,
                u.status AS user_status,

                c.college_name,
                c.college_code,
                c.university_name

            FROM placement_cells pc

            INNER JOIN users u
                ON pc.user_id = u.id

            INNER JOIN colleges c
                ON pc.college_id = c.id

            WHERE pc.user_id = %s

            LIMIT 1
        """, (
            user_id,
        ))

        placement_cell = cursor.fetchone()


        # =================================================
        # PLACEMENT CELL NOT FOUND
        # =================================================

        if not placement_cell:

            session.clear()

            flash(
                "Placement Cell profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        college_id = placement_cell["college_id"]


        # =================================================
        # TOTAL STUDENTS
        # Current Placement Cell's college only
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (
            college_id,
        ))

        total_students = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # STUDENTS WITH COMPLETED PROFILES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
              AND profile_completed = 1
        """, (
            college_id,
        ))

        profile_completed_students = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # ACTIVE / OPEN OPPORTUNITIES
        #
        # Opportunities are industry-wide because an
        # opportunity can be available to students of
        # different colleges.
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities
            WHERE status = 'OPEN'
        """)

        active_opportunities = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # TOTAL APPLICATIONS
        # Only students belonging to this college
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
        """, (
            college_id,
        ))

        total_applications = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # APPLIED
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'APPLIED'
        """, (
            college_id,
        ))

        applied_applications = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # SHORTLISTED
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'SHORTLISTED'
        """, (
            college_id,
        ))

        shortlisted_applications = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # SELECTED
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
        """, (
            college_id,
        ))

        selected_applications = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # REJECTED
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'REJECTED'
        """, (
            college_id,
        ))

        rejected_applications = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # WITHDRAWN
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'WITHDRAWN'
        """, (
            college_id,
        ))

        withdrawn_applications = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # UNREAD NOTIFICATIONS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM notifications

            WHERE user_id = %s
              AND is_read = 0
        """, (
            user_id,
        ))

        unread_notifications = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # UNREAD MESSAGES
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM messages

            WHERE receiver_id = %s
              AND is_read = 0
        """, (
            user_id,
        ))

        unread_messages = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # RECENT APPLICATIONS
        # =================================================

        cursor.execute("""
            SELECT

                sa.id AS application_id,
                sa.status,
                sa.application_date,
                sa.created_at,

                s.id AS student_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.cgpa,

                u.name AS student_name,

                o.id AS opportunity_id,
                o.title AS opportunity_title,
                o.opportunity_type,

                i.company_name

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE s.college_id = %s

            ORDER BY
                sa.application_date DESC,
                sa.created_at DESC

            LIMIT 6
        """, (
            college_id,
        ))

        recent_applications = cursor.fetchall()


        # =================================================
        # RECENT OPEN OPPORTUNITIES
        # =================================================

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

                i.company_name

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE o.status = 'OPEN'

            ORDER BY o.created_at DESC

            LIMIT 6
        """)

        recent_opportunities = cursor.fetchall()


        # =================================================
        # RECENT STUDENTS
        # =================================================

        cursor.execute("""
            SELECT

                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.cgpa,
                s.created_at,

                u.name AS student_name,
                u.email AS student_email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.college_id = %s

            ORDER BY s.created_at DESC

            LIMIT 6
        """, (
            college_id,
        ))

        recent_students = cursor.fetchall()


        # =================================================
        # APPLICATION PIPELINE
        # =================================================

        application_pipeline = {
            "applied": applied_applications,
            "shortlisted": shortlisted_applications,
            "selected": selected_applications,
            "rejected": rejected_applications,
            "withdrawn": withdrawn_applications
        }


        # =================================================
        # RENDER DASHBOARD
        # =================================================

        return render_template(

            "placement/dashboard.html",

            dashboard="dashboard",

            placement_cell=placement_cell,

            total_students=total_students,

            profile_completed_students=profile_completed_students,

            active_opportunities=active_opportunities,

            total_applications=total_applications,

            applied_applications=applied_applications,

            shortlisted_applications=shortlisted_applications,

            selected_applications=selected_applications,

            rejected_applications=rejected_applications,

            withdrawn_applications=withdrawn_applications,

            unread_notifications=unread_notifications,

            unread_messages=unread_messages,

            application_pipeline=application_pipeline,

            recent_applications=recent_applications,

            recent_opportunities=recent_opportunities,

            recent_students=recent_students
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("PLACEMENT DASHBOARD DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Placement Cell dashboard.",
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
        print("PLACEMENT DASHBOARD ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Placement Cell dashboard.",
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
# PLACEMENT CELL - STUDENTS
# =========================================================

@app.route("/placement/students")
@placement_required
def placement_students():

    conn = None
    cursor = None

    try:

        college_id = session.get("college_id")

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------

        search_query = request.args.get(
            "search",
            ""
        ).strip()

        selected_branch = request.args.get(
            "branch",
            ""
        ).strip()

        selected_status = request.args.get(
            "placement_status",
            ""
        ).strip().upper()


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # STUDENT QUERY
        # ONLY CURRENT PLACEMENT CELL COLLEGE
        # =================================================

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
                u.status AS user_status,
                u.created_at AS user_created_at,

                c.college_name,
                c.college_code

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            WHERE s.college_id = %s
        """

        params = [
            college_id
        ]


        # =================================================
        # SEARCH
        # =================================================

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


        # =================================================
        # BRANCH FILTER
        # =================================================

        if selected_branch:

            query += """
                AND s.branch = %s
            """

            params.append(
                selected_branch
            )


        query += """
            ORDER BY u.name ASC
        """


        cursor.execute(
            query,
            params
        )

        students = cursor.fetchall()


        # =================================================
        # PLACEMENT STATUS
        #
        # Priority:
        # SELECTED > SHORTLISTED > APPLIED > REJECTED
        # =================================================

        student_ids = [
            student["id"]
            for student in students
        ]


        placement_status_map = {}


        if student_ids:

            placeholders = ", ".join(
                ["%s"] * len(student_ids)
            )


            cursor.execute(
                f"""
                    SELECT

                        sa.student_id,

                        CASE

                            WHEN MAX(
                                CASE
                                    WHEN sa.status = 'SELECTED'
                                    THEN 4
                                    WHEN sa.status = 'SHORTLISTED'
                                    THEN 3
                                    WHEN sa.status = 'APPLIED'
                                    THEN 2
                                    WHEN sa.status = 'WITHDRAWN'
                                    THEN 1
                                    ELSE 0
                                END
                            ) = 4
                            THEN 'SELECTED'


                            WHEN MAX(
                                CASE
                                    WHEN sa.status = 'SHORTLISTED'
                                    THEN 3
                                    WHEN sa.status = 'APPLIED'
                                    THEN 2
                                    WHEN sa.status = 'WITHDRAWN'
                                    THEN 1
                                    ELSE 0
                                END
                            ) = 3
                            THEN 'SHORTLISTED'


                            WHEN MAX(
                                CASE
                                    WHEN sa.status = 'APPLIED'
                                    THEN 2
                                    WHEN sa.status = 'WITHDRAWN'
                                    THEN 1
                                    ELSE 0
                                END
                            ) = 2
                            THEN 'APPLIED'


                            WHEN MAX(
                                CASE
                                    WHEN sa.status = 'WITHDRAWN'
                                    THEN 1
                                    ELSE 0
                                END
                            ) = 1
                            THEN 'WITHDRAWN'


                            ELSE 'REJECTED'

                        END AS placement_status

                    FROM student_applications sa

                    WHERE sa.student_id IN ({placeholders})

                    GROUP BY sa.student_id
                """,
                student_ids
            )


            status_rows = cursor.fetchall()


            for row in status_rows:

                placement_status_map[
                    row["student_id"]
                ] = row["placement_status"]


        # =================================================
        # ATTACH STATUS TO STUDENTS
        # =================================================

        for student in students:

            student["placement_status"] = (
                placement_status_map.get(
                    student["id"],
                    "NOT APPLIED"
                )
            )


        # =================================================
        # STATUS FILTER
        # =================================================

        if selected_status:

            students = [
                student
                for student in students
                if student["placement_status"] == selected_status
            ]


        # =================================================
        # BRANCHES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                branch

            FROM students

            WHERE college_id = %s
              AND branch IS NOT NULL
              AND branch != ''

            ORDER BY branch ASC
        """, (
            college_id,
        ))


        branches = [
            row["branch"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # STATISTICS
        # =================================================

        total_students = len(
            students
        )


        applied_count = sum(
            1
            for student in students
            if student["placement_status"] == "APPLIED"
        )


        shortlisted_count = sum(
            1
            for student in students
            if student["placement_status"] == "SHORTLISTED"
        )


        selected_count = sum(
            1
            for student in students
            if student["placement_status"] == "SELECTED"
        )


        # =================================================
        # RENDER
        # =================================================

        return render_template(

            "placement/students.html",

            dashboard="students",

            students=students,

            branches=branches,

            search_query=search_query,

            selected_branch=selected_branch,

            selected_status=selected_status,

            total_students=total_students,

            applied_count=applied_count,

            shortlisted_count=shortlisted_count,

            selected_count=selected_count
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT STUDENTS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load students.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - STUDENT DETAILS
# =========================================================

@app.route("/placement/students/<student_id>")
@placement_required
def placement_student_details(student_id):

    conn = None
    cursor = None

    try:

        college_id = session.get("college_id")

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # STUDENT
        #
        # IMPORTANT:
        # student must belong to Placement Cell's college
        # =================================================

        cursor.execute("""
            SELECT

                s.*,

                u.name AS name,
                u.email AS email,
                u.status AS user_status,
                u.created_at AS user_created_at,

                c.college_name,
                c.college_code,
                c.university_name,
                c.city AS college_city,
                c.state AS college_state

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            WHERE s.id = %s
              AND s.college_id = %s

            LIMIT 1
        """, (
            student_id,
            college_id
        ))


        student = cursor.fetchone()


        # =================================================
        # SECURITY / NOT FOUND
        # =================================================

        if not student:

            flash(
                "Student not found or access denied.",
                "error"
            )

            return redirect(
                url_for("placement_students")
            )


        # =================================================
        # STUDENT SKILLS
        # =================================================

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
        """, (
            student_id,
        ))


        skills = cursor.fetchall()


        # =================================================
        # APPLICATION HISTORY
        # =================================================

        cursor.execute("""
            SELECT

                sa.id AS application_id,
                sa.status,
                sa.application_date,
                sa.updated_at,

                o.id AS opportunity_id,
                o.title AS opportunity_title,
                o.opportunity_type,
                o.location,
                o.work_mode,

                i.id AS industry_id,
                i.company_name

            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE sa.student_id = %s

            ORDER BY
                sa.application_date DESC

        """, (
            student_id,
        ))


        applications = cursor.fetchall()


        # =================================================
        # PLACEMENT STATUS
        # =================================================

        placement_status = "NOT APPLIED"


        if applications:

            statuses = [
                application["status"]
                for application in applications
            ]


            if "SELECTED" in statuses:

                placement_status = "SELECTED"

            elif "SHORTLISTED" in statuses:

                placement_status = "SHORTLISTED"

            elif "APPLIED" in statuses:

                placement_status = "APPLIED"

            elif "WITHDRAWN" in statuses:

                placement_status = "WITHDRAWN"

            elif "REJECTED" in statuses:

                placement_status = "REJECTED"


        student["placement_status"] = (
            placement_status
        )


        # =================================================
        # RENDER
        # =================================================

        return render_template(

            "placement/student-details.html",

            dashboard="students",

            student=student,

            skills=skills,

            applications=applications
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT STUDENT DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load student details.",
            "error"
        )

        return redirect(
            url_for("placement_students")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - OPPORTUNITIES
# =========================================================

@app.route("/placement/opportunities")
@placement_required
def placement_opportunities():

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        search = request.args.get("search", "").strip()
        opportunity_type = request.args.get("type", "").strip().upper()
        work_mode = request.args.get("work_mode", "").strip().upper()

        query = """
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

                i.company_name,
                i.company_type,
                i.industry_sector

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE o.status = 'OPEN'
              AND i.status = 'ACTIVE'
        """

        params = []

        if search:

            query += """
                AND (
                    o.title LIKE %s
                    OR o.description LIKE %s
                    OR o.required_skills LIKE %s
                    OR i.company_name LIKE %s
                )
            """

            value = f"%{search}%"

            params.extend([
                value,
                value,
                value,
                value
            ])

        if opportunity_type:

            query += """
                AND o.opportunity_type = %s
            """

            params.append(opportunity_type)

        if work_mode:

            query += """
                AND o.work_mode = %s
            """

            params.append(work_mode)

        query += """
            ORDER BY
                CASE
                    WHEN o.application_deadline IS NULL THEN 1
                    ELSE 0
                END,
                o.application_deadline ASC,
                o.created_at DESC
        """

        cursor.execute(query, params)

        opportunities = cursor.fetchall()

        # -------------------------------------------------
        # APPLICATION COUNT FOR CURRENT COLLEGE
        # -------------------------------------------------

        college_id = session.get("college_id")

        for opportunity in opportunities:

            cursor.execute("""
                SELECT COUNT(*) AS total

                FROM student_applications sa

                INNER JOIN students s
                    ON sa.student_id = s.id

                WHERE sa.opportunity_id = %s
                  AND s.college_id = %s
            """, (
                opportunity["id"],
                college_id
            ))

            opportunity["application_count"] = (
                cursor.fetchone()["total"] or 0
            )

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities o
            INNER JOIN industries i
                ON o.industry_id = i.id
            WHERE o.status = 'OPEN'
              AND i.status = 'ACTIVE'
        """)

        total_opportunities = cursor.fetchone()["total"] or 0

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM opportunities o
            INNER JOIN industries i
                ON o.industry_id = i.id
            WHERE o.status = 'OPEN'
              AND i.status = 'ACTIVE'
              AND o.application_deadline IS NOT NULL
              AND o.application_deadline >= CURDATE()
        """)

        upcoming_deadlines = cursor.fetchone()["total"] or 0

        cursor.execute("""
            SELECT COUNT(DISTINCT industry_id) AS total
            FROM opportunities
            WHERE status = 'OPEN'
        """)

        hiring_industries = cursor.fetchone()["total"] or 0

        return render_template(
            "placement/opportunities.html",

            dashboard="opportunities",

            opportunities=opportunities,

            total_opportunities=total_opportunities,

            upcoming_deadlines=upcoming_deadlines,

            hiring_industries=hiring_industries,

            search=search,

            opportunity_type=opportunity_type,

            work_mode=work_mode
        )

    except Exception as e:

        print("=" * 70)
        print("PLACEMENT OPPORTUNITIES ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load opportunities.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - OPPORTUNITY DETAILS
# =========================================================

@app.route("/placement/opportunities/<opportunity_id>")
@placement_required
def placement_opportunity_details(opportunity_id):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        college_id = session.get("college_id")

        # -------------------------------------------------
        # OPPORTUNITY
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
                i.contact_person,
                i.designation,
                i.email AS industry_email,
                i.website,
                i.city,
                i.state

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE o.id = %s

            LIMIT 1
        """, (
            opportunity_id,
        ))

        opportunity = cursor.fetchone()

        if not opportunity:

            flash(
                "Opportunity not found.",
                "error"
            )

            return redirect(
                url_for("placement_opportunities")
            )

        # -------------------------------------------------
        # CURRENT COLLEGE APPLICATIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE sa.opportunity_id = %s
              AND s.college_id = %s
        """, (
            opportunity_id,
            college_id
        ))

        application_count = (
            cursor.fetchone()["total"] or 0
        )

        # -------------------------------------------------
        # COLLEGE STUDENT COUNT
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (
            college_id,
        ))

        total_students = cursor.fetchone()["total"] or 0

        return render_template(
            "placement/opportunity-details.html",

            dashboard="opportunities",

            opportunity=opportunity,

            application_count=application_count,

            total_students=total_students
        )

    except Exception as e:

        print("=" * 70)
        print("PLACEMENT OPPORTUNITY DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load opportunity details.",
            "error"
        )

        return redirect(
            url_for("placement_opportunities")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - ELIGIBLE STUDENTS
# =========================================================

@app.route("/placement/opportunities/<opportunity_id>/eligible-students")
@placement_required
def placement_eligible_students(opportunity_id):

    conn = None
    cursor = None

    try:

        college_id = session.get("college_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # OPPORTUNITY
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                o.id,
                o.title,
                o.opportunity_type,
                o.required_skills,
                o.eligibility_criteria,
                o.application_deadline,
                o.status,

                i.company_name

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE o.id = %s

            LIMIT 1
        """, (
            opportunity_id,
        ))

        opportunity = cursor.fetchone()

        if not opportunity:

            flash(
                "Opportunity not found.",
                "error"
            )

            return redirect(
                url_for("placement_opportunities")
            )

        # -------------------------------------------------
        # CURRENT COLLEGE STUDENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                s.id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.cgpa,
                s.active_backlogs,
                s.profile_completed,

                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.college_id = %s

            ORDER BY
                s.cgpa DESC,
                u.name ASC
        """, (
            college_id,
        ))

        students = cursor.fetchall()

        # -------------------------------------------------
        # REQUIRED SKILLS
        # -------------------------------------------------

        required_skills_text = (
            opportunity["required_skills"] or ""
        ).lower()

        required_skills = [
            skill.strip()
            for skill in required_skills_text.replace(
                ";", ","
            ).split(",")
            if skill.strip()
        ]

        # -------------------------------------------------
        # APPLICATION STATUS
        # -------------------------------------------------

        student_ids = [
            student["id"]
            for student in students
        ]

        application_map = {}

        if student_ids:

            placeholders = ", ".join(
                ["%s"] * len(student_ids)
            )

            cursor.execute(
                f"""
                    SELECT
                        student_id,
                        status

                    FROM student_applications

                    WHERE opportunity_id = %s

                      AND student_id IN ({placeholders})
                """,
                [opportunity_id] + student_ids
            )

            for row in cursor.fetchall():

                application_map[
                    row["student_id"]
                ] = row["status"]

        # -------------------------------------------------
        # STUDENT SKILLS
        # -------------------------------------------------

        skills_map = {}

        if student_ids:

            placeholders = ", ".join(
                ["%s"] * len(student_ids)
            )

            cursor.execute(
                f"""
                    SELECT
                        student_id,
                        skill_name

                    FROM student_skills

                    WHERE student_id IN ({placeholders})
                """,
                student_ids
            )

            for row in cursor.fetchall():

                skills_map.setdefault(
                    row["student_id"],
                    []
                ).append(
                    row["skill_name"]
                )

        # -------------------------------------------------
        # ELIGIBILITY CALCULATION
        # -------------------------------------------------

        eligible_students = []

        for student in students:

            student_skills = [
                str(skill).lower()
                for skill in skills_map.get(
                    student["id"],
                    []
                )
            ]

            matched_skills = []

            for required_skill in required_skills:

                if any(
                    required_skill in skill
                    or skill in required_skill
                    for skill in student_skills
                ):
                    matched_skills.append(
                        required_skill
                    )

            # ---------------------------------------------
            # BASIC ELIGIBILITY
            # ---------------------------------------------

            cgpa_ok = True

            criteria_text = (
                opportunity["eligibility_criteria"]
                or ""
            ).lower()

            import re

            cgpa_matches = re.findall(
                r'(?:cgpa|minimum cgpa|cgpa of)\s*(?:>=|:|is)?\s*(\d+(?:\.\d+)?)',
                criteria_text
            )

            if cgpa_matches and student["cgpa"] is not None:

                required_cgpa = float(
                    cgpa_matches[0]
                )

                cgpa_ok = float(
                    student["cgpa"]
                ) >= required_cgpa

            elif cgpa_matches:

                cgpa_ok = False

            # ---------------------------------------------
            # BACKLOG CHECK
            # ---------------------------------------------

            backlog_ok = (
                not student["active_backlogs"]
                or student["active_backlogs"] == 0
            )

            # ---------------------------------------------
            # SKILL CHECK
            # ---------------------------------------------

            skills_ok = (
                not required_skills
                or bool(matched_skills)
            )

            # ---------------------------------------------
            # FINAL
            # ---------------------------------------------

            student["matched_skills"] = matched_skills

            student["application_status"] = (
                application_map.get(
                    student["id"]
                )
            )

            student["cgpa_ok"] = cgpa_ok
            student["backlog_ok"] = backlog_ok
            student["skills_ok"] = skills_ok

            student["eligible"] = (
                cgpa_ok
                and backlog_ok
                and skills_ok
            )

            if student["eligible"]:

                eligible_students.append(
                    student
                )

        return render_template(
            "placement/eligible-students.html",

            dashboard="opportunities",

            opportunity=opportunity,

            students=eligible_students,

            total_eligible=len(
                eligible_students
            ),

            total_students=len(
                students
            )
        )

    except Exception as e:

        print("=" * 70)
        print("PLACIBLE STUDENTS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to calculate eligible students.",
            "error"
        )

        return redirect(
            url_for(
                "placement_opportunity_details",
                opportunity_id=opportunity_id
            )
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - APPLICATIONS
# =========================================================

@app.route("/placement/applications")
@placement_required
def placement_applications():

    conn = None
    cursor = None

    try:

        college_id = session.get("college_id")

        if not college_id:
            flash(
                "College information not found.",
                "error"
            )
            return redirect(
                url_for("placement_dashboard")
            )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------

        search = request.args.get(
            "search",
            ""
        ).strip()

        selected_status = request.args.get(
            "status",
            ""
        ).strip().upper()

        selected_opportunity = request.args.get(
            "opportunity_id",
            ""
        ).strip()

        # -------------------------------------------------
        # APPLICATIONS
        # ONLY STUDENTS FROM CURRENT COLLEGE
        # -------------------------------------------------

        query = """
            SELECT

                sa.id AS application_id,
                sa.status,
                sa.application_date,
                sa.created_at,
                sa.updated_at,

                s.id AS student_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.cgpa,
                s.active_backlogs,

                u.name AS student_name,
                u.email AS student_email,

                o.id AS opportunity_id,
                o.title AS opportunity_title,
                o.opportunity_type,
                o.location,
                o.work_mode,
                o.application_deadline,

                i.id AS industry_id,
                i.company_name,
                i.company_type,
                i.industry_sector

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE s.college_id = %s
        """

        params = [
            college_id
        ]

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        if search:

            query += """
                AND (
                    u.name LIKE %s
                    OR u.email LIKE %s
                    OR s.enrollment_no LIKE %s
                    OR o.title LIKE %s
                    OR i.company_name LIKE %s
                )
            """

            value = f"%{search}%"

            params.extend([
                value,
                value,
                value,
                value,
                value
            ])

        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        if selected_status:

            query += """
                AND sa.status = %s
            """

            params.append(
                selected_status
            )

        # -------------------------------------------------
        # OPPORTUNITY FILTER
        # -------------------------------------------------

        if selected_opportunity:

            query += """
                AND sa.opportunity_id = %s
            """

            params.append(
                selected_opportunity
            )

        # -------------------------------------------------
        # ORDER
        # -------------------------------------------------

        query += """
            ORDER BY
                sa.application_date DESC,
                sa.created_at DESC
        """

        cursor.execute(
            query,
            params
        )

        applications = cursor.fetchall()

        # -------------------------------------------------
        # OPPORTUNITY DROPDOWN
        # -------------------------------------------------

        cursor.execute("""
            SELECT DISTINCT
                o.id,
                o.title

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            WHERE s.college_id = %s

            ORDER BY o.title ASC
        """, (
            college_id,
        ))

        opportunities = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN sa.status = 'APPLIED'
                        THEN 1
                        ELSE 0
                    END
                ) AS applied,

                SUM(
                    CASE
                        WHEN sa.status = 'SHORTLISTED'
                        THEN 1
                        ELSE 0
                    END
                ) AS shortlisted,

                SUM(
                    CASE
                        WHEN sa.status = 'SELECTED'
                        THEN 1
                        ELSE 0
                    END
                ) AS selected,

                SUM(
                    CASE
                        WHEN sa.status = 'REJECTED'
                        THEN 1
                        ELSE 0
                    END
                ) AS rejected,

                SUM(
                    CASE
                        WHEN sa.status = 'WITHDRAWN'
                        THEN 1
                        ELSE 0
                    END
                ) AS withdrawn

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
        """, (
            college_id,
        ))

        stats = cursor.fetchone()

        return render_template(
            "placement/applications.html",

            dashboard="applications",

            applications=applications,
            opportunities=opportunities,

            stats=stats,

            search=search,
            selected_status=selected_status,
            selected_opportunity=selected_opportunity
        )

    except Exception as e:

        print("=" * 70)
        print("PLACEMENT APPLICATIONS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load applications.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - APPLICATION DETAILS
# =========================================================

@app.route(
    "/placement/applications/<application_id>"
)
@placement_required
def placement_application_details(
    application_id
):

    conn = None
    cursor = None

    try:

        college_id = session.get(
            "college_id"
        )

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # APPLICATION
        #
        # IMPORTANT:
        # Student's college is checked here.
        # This prevents another college's application
        # from being opened by changing the URL.
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                sa.id AS application_id,
                sa.status,
                sa.application_date,
                sa.created_at,
                sa.updated_at,

                s.id AS student_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.cgpa,
                s.current_sgpa,
                s.active_backlogs,
                s.phone,
                s.dob,
                s.gender,
                s.address,
                s.linkedin_url,
                s.github_url,
                s.portfolio_url,
                s.resume_url,
                s.profile_completed,

                u.name AS student_name,
                u.email AS student_email,

                c.college_name,
                c.college_code,
                c.university_name,

                o.id AS opportunity_id,
                o.title AS opportunity_title,
                o.opportunity_type,
                o.description,
                o.required_skills,
                o.eligibility_criteria,
                o.location,
                o.work_mode,
                o.stipend,
                o.package,
                o.application_deadline,
                o.status AS opportunity_status,

                i.id AS industry_id,
                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.email AS industry_email,
                i.phone AS industry_phone

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE sa.id = %s
              AND s.college_id = %s

            LIMIT 1
        """, (
            application_id,
            college_id
        ))

        application = cursor.fetchone()

        if not application:

            flash(
                "Application not found or access denied.",
                "error"
            )

            return redirect(
                url_for(
                    "placement_applications"
                )
            )

        # -------------------------------------------------
        # STUDENT SKILLS
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                id,
                skill_name,
                proficiency_level,
                assessment_percentage,
                verification_status

            FROM student_skills

            WHERE student_id = %s

            ORDER BY
                assessment_percentage DESC,
                skill_name ASC
        """, (
            application["student_id"],
        ))

        skills = cursor.fetchall()

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------

        return render_template(
            "placement/application-details.html",

            dashboard="applications",

            application=application,
            skills=skills
        )

    except Exception as e:

        print("=" * 70)
        print("PLACEMENT APPLICATION DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load application details.",
            "error"
        )

        return redirect(
            url_for(
                "placement_applications"
            )
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - PLACEMENTS
# =========================================================

@app.route("/placement/placements")
@placement_required
def placement_placements():

    conn = None
    cursor = None

    try:

        college_id = session.get("college_id")

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # FILTERS
        # =================================================

        search_query = request.args.get(
            "search",
            ""
        ).strip()

        selected_branch = request.args.get(
            "branch",
            ""
        ).strip()

        selected_company = request.args.get(
            "company_id",
            ""
        ).strip()


        # =================================================
        # PLACEMENT RECORDS
        #
        # A placement record is created from a
        # SELECTED student application.
        # =================================================

        query = """
            SELECT

                sa.id AS application_id,
                sa.status AS placement_status,
                sa.application_date,
                sa.updated_at,

                s.id AS student_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.cgpa,
                s.current_sgpa,
                s.active_backlogs,

                u.name AS student_name,
                u.email AS student_email,

                o.id AS opportunity_id,
                o.title AS opportunity_title,
                o.opportunity_type,
                o.location,
                o.work_mode,
                o.stipend,
                o.package,
                o.application_deadline,

                i.id AS company_id,
                i.company_name,
                i.company_type,
                i.industry_sector

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
        """

        params = [
            college_id
        ]


        # =================================================
        # SEARCH
        # =================================================

        if search_query:

            query += """
                AND (
                    u.name LIKE %s
                    OR u.email LIKE %s
                    OR s.enrollment_no LIKE %s
                    OR o.title LIKE %s
                    OR i.company_name LIKE %s
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


        # =================================================
        # BRANCH FILTER
        # =================================================

        if selected_branch:

            query += """
                AND s.branch = %s
            """

            params.append(
                selected_branch
            )


        # =================================================
        # COMPANY FILTER
        # =================================================

        if selected_company:

            query += """
                AND i.id = %s
            """

            params.append(
                selected_company
            )


        query += """
            ORDER BY
                sa.updated_at DESC,
                sa.application_date DESC
        """


        cursor.execute(
            query,
            params
        )

        placements = cursor.fetchall()


        # =================================================
        # BRANCH DROPDOWN
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                s.branch

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
              AND s.branch IS NOT NULL
              AND s.branch != ''

            ORDER BY s.branch ASC
        """, (
            college_id,
        ))

        branches = [
            row["branch"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # COMPANY DROPDOWN
        # =================================================

        cursor.execute("""
            SELECT DISTINCT

                i.id,
                i.company_name

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'

            ORDER BY i.company_name ASC
        """, (
            college_id,
        ))

        companies = cursor.fetchall()


        # =================================================
        # BASIC STATISTICS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (
            college_id,
        ))

        total_students = (
            cursor.fetchone()["total"] or 0
        )


        cursor.execute("""
            SELECT COUNT(DISTINCT sa.student_id) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
        """, (
            college_id,
        ))

        placed_students = (
            cursor.fetchone()["total"] or 0
        )


        cursor.execute("""
            SELECT COUNT(DISTINCT i.id) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
        """, (
            college_id,
        ))

        hiring_companies = (
            cursor.fetchone()["total"] or 0
        )


        placement_rate = 0

        if total_students > 0:

            placement_rate = round(
                (
                    placed_students
                    / total_students
                ) * 100,
                2
            )


        return render_template(
            "placement/placements.html",

            dashboard="placements",

            placements=placements,

            branches=branches,
            companies=companies,

            search_query=search_query,
            selected_branch=selected_branch,
            selected_company=selected_company,

            total_students=total_students,
            placed_students=placed_students,
            hiring_companies=hiring_companies,
            placement_rate=placement_rate
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT RECORDS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load placement records.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - PLACEMENT DETAILS
# =========================================================

@app.route(
    "/placement/placements/<application_id>"
)
@placement_required
def placement_placement_details(
    application_id
):

    conn = None
    cursor = None

    try:

        college_id = session.get(
            "college_id"
        )

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # PLACEMENT DETAILS
        #
        # Only SELECTED applications are considered
        # actual placement records.
        # =================================================

        cursor.execute("""
            SELECT

                sa.id AS application_id,
                sa.status AS placement_status,
                sa.application_date,
                sa.created_at,
                sa.updated_at,

                s.id AS student_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,
                s.cgpa,
                s.current_sgpa,
                s.active_backlogs,
                s.phone,
                s.dob,
                s.gender,
                s.address,
                s.linkedin_url,
                s.github_url,
                s.portfolio_url,
                s.resume_url,
                s.profile_completed,

                u.name AS student_name,
                u.email AS student_email,

                c.college_name,
                c.college_code,
                c.university_name,

                o.id AS opportunity_id,
                o.title AS opportunity_title,
                o.opportunity_type,
                o.description,
                o.required_skills,
                o.eligibility_criteria,
                o.location,
                o.work_mode,
                o.stipend,
                o.package,
                o.application_deadline,
                o.status AS opportunity_status,

                i.id AS company_id,
                i.company_name,
                i.company_type,
                i.industry_sector,
                i.contact_person,
                i.email AS company_email,
                i.phone AS company_phone

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            INNER JOIN colleges c
                ON s.college_id = c.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE sa.id = %s
              AND s.college_id = %s
              AND sa.status = 'SELECTED'

            LIMIT 1
        """, (
            application_id,
            college_id
        ))

        placement = cursor.fetchone()


        if not placement:

            flash(
                "Placement record not found or access denied.",
                "error"
            )

            return redirect(
                url_for("placement_placements")
            )


        # =================================================
        # STUDENT SKILLS
        # =================================================

        cursor.execute("""
            SELECT

                id,
                skill_name,
                proficiency_level,
                assessment_percentage,
                verification_status

            FROM student_skills

            WHERE student_id = %s

            ORDER BY
                assessment_percentage DESC,
                skill_name ASC
        """, (
            placement["student_id"],
        ))

        skills = cursor.fetchall()


        return render_template(
            "placement/placement-details.html",

            dashboard="placement_details",

            placement=placement,
            skills=skills
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load placement details.",
            "error"
        )

        return redirect(
            url_for("placement_placements")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - PLACEMENT STATISTICS
# =========================================================

@app.route(
    "/placement/placement-statistics"
)
@placement_required
def placement_statistics():

    conn = None
    cursor = None

    try:

        college_id = session.get(
            "college_id"
        )

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # TOTAL STUDENTS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (
            college_id,
        ))

        total_students = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # PLACED STUDENTS
        # DISTINCT STUDENTS
        # =================================================

        cursor.execute("""
            SELECT COUNT(DISTINCT sa.student_id) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
        """, (
            college_id,
        ))

        placed_students = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # NOT PLACED
        # =================================================

        not_placed_students = max(
            total_students - placed_students,
            0
        )


        # =================================================
        # PLACEMENT RATE
        # =================================================

        placement_rate = 0

        if total_students > 0:

            placement_rate = round(
                (
                    placed_students
                    / total_students
                ) * 100,
                2
            )


        # =================================================
        # COMPANIES
        # =================================================

        cursor.execute("""
            SELECT COUNT(DISTINCT i.id) AS total

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'
        """, (
            college_id,
        ))

        total_companies = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # BRANCH-WISE STATISTICS
        # =================================================

        cursor.execute("""
            SELECT

                s.branch,

                COUNT(DISTINCT s.id)
                    AS total_students,

                COUNT(
                    DISTINCT
                    CASE
                        WHEN sa.status = 'SELECTED'
                        THEN s.id
                    END
                ) AS placed_students

            FROM students s

            LEFT JOIN student_applications sa
                ON sa.student_id = s.id

            WHERE s.college_id = %s

            GROUP BY s.branch

            ORDER BY
                placed_students DESC,
                s.branch ASC
        """, (
            college_id,
        ))

        branch_statistics = cursor.fetchall()


        # Add placement percentage

        for row in branch_statistics:

            total = (
                row["total_students"]
                or 0
            )

            placed = (
                row["placed_students"]
                or 0
            )

            row["placement_rate"] = (
                round(
                    (placed / total) * 100,
                    2
                )
                if total > 0
                else 0
            )


        # =================================================
        # COMPANY-WISE STATISTICS
        # =================================================

        cursor.execute("""
            SELECT

                i.id AS company_id,
                i.company_name,

                COUNT(
                    DISTINCT sa.student_id
                ) AS selected_students

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE s.college_id = %s
              AND sa.status = 'SELECTED'

            GROUP BY
                i.id,
                i.company_name

            ORDER BY
                selected_students DESC,
                i.company_name ASC
        """, (
            college_id,
        ))

        company_statistics = cursor.fetchall()


        return render_template(
            "placement/placement-statistics.html",

            dashboard="placement_statistics",

            total_students=total_students,
            placed_students=placed_students,
            not_placed_students=not_placed_students,

            placement_rate=placement_rate,

            total_companies=total_companies,

            branch_statistics=branch_statistics,
            company_statistics=company_statistics
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT STATISTICS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load placement statistics.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - INDUSTRIES
# =========================================================

@app.route("/placement/industries")
@placement_required
def placement_industries():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT PLACEMENT CELL
        # =================================================

        college_id = session.get("college_id")

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # FILTERS
        # =================================================

        search = request.args.get(
            "search",
            ""
        ).strip()

        company_type = request.args.get(
            "company_type",
            ""
        ).strip()

        industry_sector = request.args.get(
            "industry_sector",
            ""
        ).strip()


        # =================================================
        # INDUSTRY LIST
        #
        # Only ACTIVE industries are visible.
        # =================================================

        query = """
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

                u.name AS user_name,
                u.email AS user_email,

                COUNT(
                    DISTINCT o.id
                ) AS opportunity_count,

                COUNT(
                    DISTINCT c.id
                ) AS collaboration_count

            FROM industries i

            INNER JOIN users u
                ON i.user_id = u.id

            LEFT JOIN opportunities o
                ON o.industry_id = i.id

            LEFT JOIN collaborations c
                ON c.industry_id = i.id

            WHERE i.status = 'ACTIVE'
        """

        params = []


        # =================================================
        # SEARCH
        # =================================================

        if search:

            query += """
                AND (
                    i.company_name LIKE %s
                    OR i.company_type LIKE %s
                    OR i.industry_sector LIKE %s
                    OR i.contact_person LIKE %s
                    OR i.city LIKE %s
                    OR i.state LIKE %s
                )
            """

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ])


        # =================================================
        # COMPANY TYPE
        # =================================================

        if company_type:

            query += """
                AND i.company_type = %s
            """

            params.append(
                company_type
            )


        # =================================================
        # INDUSTRY SECTOR
        # =================================================

        if industry_sector:

            query += """
                AND i.industry_sector = %s
            """

            params.append(
                industry_sector
            )


        # =================================================
        # GROUP
        # =================================================

        query += """
            GROUP BY

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

                u.name,
                u.email

            ORDER BY
                i.company_name ASC
        """


        cursor.execute(
            query,
            params
        )

        industries = cursor.fetchall()


        # =================================================
        # COMPANY TYPES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                company_type

            FROM industries

            WHERE status = 'ACTIVE'

              AND company_type IS NOT NULL

              AND company_type != ''

            ORDER BY company_type ASC
        """)

        company_types = [
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

            WHERE status = 'ACTIVE'

              AND industry_sector IS NOT NULL

              AND industry_sector != ''

            ORDER BY industry_sector ASC
        """)

        industry_sectors = [
            row["industry_sector"]
            for row in cursor.fetchall()
        ]


        # =================================================
        # SUMMARY
        # =================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total_industries

            FROM industries

            WHERE status = 'ACTIVE'
        """)

        total_industries = (
            cursor.fetchone()["total_industries"]
            or 0
        )


        cursor.execute("""
            SELECT
                COUNT(*) AS total_opportunities

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE i.status = 'ACTIVE'
              AND o.status = 'OPEN'
        """)

        total_opportunities = (
            cursor.fetchone()["total_opportunities"]
            or 0
        )


        cursor.execute("""
            SELECT
                COUNT(*) AS total_collaborations

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE i.status = 'ACTIVE'
        """)

        total_collaborations = (
            cursor.fetchone()["total_collaborations"]
            or 0
        )


        return render_template(
            "placement/industries.html",

            dashboard="industries",

            industries=industries,

            company_types=company_types,
            industry_sectors=industry_sectors,

            total_industries=total_industries,
            total_opportunities=total_opportunities,
            total_collaborations=total_collaborations,

            search=search,
            company_type=company_type,
            industry_sector=industry_sector
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT INDUSTRIES ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load industries.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - INDUSTRY DETAILS
# =========================================================

@app.route(
    "/placement/industries/<industry_id>"
)
@placement_required
def placement_industry_details(
    industry_id
):

    conn = None
    cursor = None

    try:

        college_id = session.get(
            "college_id"
        )

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # INDUSTRY INFORMATION
        # =================================================

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

                u.name AS user_name,
                u.email AS user_email

            FROM industries i

            INNER JOIN users u
                ON i.user_id = u.id

            WHERE i.id = %s
              AND i.status = 'ACTIVE'

            LIMIT 1
        """, (
            industry_id,
        ))

        industry = cursor.fetchone()


        if not industry:

            flash(
                "Industry not found or is not active.",
                "error"
            )

            return redirect(
                url_for("placement_industries")
            )


        # =================================================
        # OPPORTUNITIES
        # =================================================

        cursor.execute("""
            SELECT

                o.id,
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
                o.created_at

            FROM opportunities o

            WHERE o.industry_id = %s

              AND o.status = 'OPEN'

            ORDER BY
                o.application_deadline IS NULL ASC,
                o.application_deadline ASC,
                o.created_at DESC
        """, (
            industry_id,
        ))

        opportunities = cursor.fetchall()


        # =================================================
        # COLLABORATIONS
        # =================================================

        cursor.execute("""
            SELECT

                c.id,
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
                cl.city,
                cl.state

            FROM collaborations c

            INNER JOIN colleges cl
                ON c.college_id = cl.id

            WHERE c.industry_id = %s

            ORDER BY
                c.created_at DESC

            LIMIT 10
        """, (
            industry_id,
        ))

        collaborations = cursor.fetchall()


        # =================================================
        # COUNTS
        # =================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total

            FROM opportunities

            WHERE industry_id = %s
              AND status = 'OPEN'
        """, (
            industry_id,
        ))

        opportunity_count = (
            cursor.fetchone()["total"]
            or 0
        )


        cursor.execute("""
            SELECT
                COUNT(*) AS total

            FROM collaborations

            WHERE industry_id = %s
        """, (
            industry_id,
        ))

        collaboration_count = (
            cursor.fetchone()["total"]
            or 0
        )


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "placement/industry-details.html",

            dashboard="industry_details",

            industry=industry,

            opportunities=opportunities,
            collaborations=collaborations,

            opportunity_count=opportunity_count,
            collaboration_count=collaboration_count
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT INDUSTRY DETAILS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load industry details.",
            "error"
        )

        return redirect(
            url_for("placement_industries")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# PLACEMENT CELL - SEND COLLABORATION
# ============================================================

@app.route("/placement/collaborations/send", methods=["GET", "POST"])
@placement_required
def placement_send_collaboration():

    college_id = session.get("college_id")

    if not college_id:
        flash("College information not found.", "error")
        return redirect(url_for("placement_dashboard"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ----------------------------------------------------
        # GET ACTIVE INDUSTRIES
        # ----------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                company_name,
                company_type,
                industry_sector,
                contact_person,
                designation,
                email,
                phone,
                website,
                address,
                city,
                state
            FROM industries
            WHERE status = 'ACTIVE'
            ORDER BY company_name ASC
        """)

        industries = cursor.fetchall()

        # ----------------------------------------------------
        # POST - SEND COLLABORATION REQUEST
        # ----------------------------------------------------
        if request.method == "POST":

            industry_id = request.form.get("industry_id", "").strip()
            title = request.form.get("title", "").strip()
            collaboration_type = request.form.get(
                "collaboration_type", ""
            ).strip()
            description = request.form.get("description", "").strip()
            start_date = request.form.get("start_date", "").strip()
            end_date = request.form.get("end_date", "").strip()

            # ---------------- VALIDATION ----------------

            if not industry_id:
                flash("Please select an industry.", "error")
                return render_template(
                    "placement/send-collaboration.html",
                    industries=industries
                )

            if not title:
                flash("Collaboration title is required.", "error")
                return render_template(
                    "placement/send-collaboration.html",
                    industries=industries
                )

            if not collaboration_type:
                flash("Please select collaboration type.", "error")
                return render_template(
                    "placement/send-collaboration.html",
                    industries=industries
                )

            if not description:
                flash("Collaboration description is required.", "error")
                return render_template(
                    "placement/send-collaboration.html",
                    industries=industries
                )

            # ------------------------------------------------
            # VERIFY INDUSTRY EXISTS & ACTIVE
            # ------------------------------------------------
            cursor.execute("""
                SELECT id, company_name
                FROM industries
                WHERE id = %s
                  AND status = 'ACTIVE'
                LIMIT 1
            """, (industry_id,))

            industry = cursor.fetchone()

            if not industry:
                flash("Selected industry is not available.", "error")
                return render_template(
                    "placement/send-collaboration.html",
                    industries=industries
                )

            # ------------------------------------------------
            # CHECK DUPLICATE PENDING REQUEST
            # ------------------------------------------------
            cursor.execute("""
                SELECT id
                FROM collaborations
                WHERE college_id = %s
                  AND industry_id = %s
                  AND status = 'PENDING'
                LIMIT 1
            """, (college_id, industry_id))

            existing_request = cursor.fetchone()

            if existing_request:
                flash(
                    "A pending collaboration request already exists with this industry.",
                    "warning"
                )
                return render_template(
                    "placement/send-collaboration.html",
                    industries=industries
                )

            # ------------------------------------------------
            # INSERT COLLABORATION
            # ------------------------------------------------
            cursor.execute("""
                INSERT INTO collaborations (
                    college_id,
                    industry_id,
                    initiated_by,
                    title,
                    description,
                    collaboration_type,
                    start_date,
                    end_date,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING'
                )
            """, (
                college_id,
                industry_id,
                "PLACEMENT_CELL",
                title,
                description,
                collaboration_type,
                start_date if start_date else None,
                end_date if end_date else None
            ))

            collaboration_id = cursor.lastrowid

            conn.commit()

            # ------------------------------------------------
            # NOTIFICATION FOR INDUSTRY
            # ------------------------------------------------
            try:
                cursor.execute("""
                    SELECT user_id
                    FROM industries
                    WHERE id = %s
                    LIMIT 1
                """, (industry_id,))

                industry_user = cursor.fetchone()

                if industry_user and industry_user.get("user_id"):

                    cursor.execute("""
                        INSERT INTO notifications (
                            user_id,
                            title,
                            message,
                            notification_type,
                            is_read,
                            created_at
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, NOW()
                        )
                    """, (
                        industry_user["user_id"],
                        "New Collaboration Request",
                        f"Your industry has received a new collaboration request: {title}",
                        "COLLABORATION",
                        0
                    ))

                    conn.commit()

            except Exception as notification_error:
                # Collaboration already saved successfully.
                # Notification failure should not rollback request.
                print(
                    "Collaboration notification error:",
                    notification_error
                )

            flash(
                f"Collaboration request sent successfully to {industry['company_name']}.",
                "success"
            )

            return redirect(
                url_for("placement_receive_collaborations")
            )

        # ----------------------------------------------------
        # GET REQUEST
        # ----------------------------------------------------
        return render_template(
            "placement/send-collaboration.html",
            industries=industries
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("Placement Send Collaboration Error:", e)

        flash(
            "Something went wrong while sending the collaboration request.",
            "error"
        )

        return render_template(
            "placement/send-collaboration.html",
            industries=[]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# PLACEMENT CELL - RECEIVE COLLABORATIONS
# ============================================================

@app.route("/placement/collaborations/receive")
@placement_required
def placement_receive_collaborations():

    college_id = session.get("college_id")

    if not college_id:
        flash("College information not found.", "error")
        return redirect(url_for("placement_dashboard"))

    search = request.args.get("search", "").strip()
    selected_status = request.args.get("status", "").strip().upper()
    selected_type = request.args.get("collaboration_type", "").strip()

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ====================================================
        # RECEIVE COLLABORATIONS
        # Only INDUSTRY-initiated requests
        # belonging to current college
        # ====================================================

        query = """
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
                i.website AS industry_website,
                i.address AS industry_address,
                i.city AS industry_city,
                i.state AS industry_state

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.college_id = %s
              AND UPPER(c.initiated_by) = 'INDUSTRY'
        """

        params = [college_id]

        # ====================================================
        # SEARCH
        # ====================================================

        if search:
            query += """
                AND (
                    c.title LIKE %s
                    OR c.description LIKE %s
                    OR c.collaboration_type LIKE %s
                    OR i.company_name LIKE %s
                    OR i.industry_sector LIKE %s
                    OR i.contact_person LIKE %s
                )
            """

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ])

        # ====================================================
        # STATUS FILTER
        # ====================================================

        if selected_status:
            query += """
                AND UPPER(c.status) = %s
            """
            params.append(selected_status)

        # ====================================================
        # COLLABORATION TYPE FILTER
        # ====================================================

        if selected_type:
            query += """
                AND c.collaboration_type = %s
            """
            params.append(selected_type)

        query += """
            ORDER BY c.created_at DESC
        """

        cursor.execute(query, tuple(params))

        collaborations = cursor.fetchall()

        # ====================================================
        # AVAILABLE COLLABORATION TYPES
        # ====================================================

        cursor.execute("""
            SELECT DISTINCT collaboration_type
            FROM collaborations
            WHERE college_id = %s
              AND UPPER(initiated_by) = 'INDUSTRY'
              AND collaboration_type IS NOT NULL
              AND collaboration_type != ''
            ORDER BY collaboration_type
        """, (college_id,))

        collaboration_types = cursor.fetchall()

        # ====================================================
        # STATISTICS
        # ====================================================

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(
                    CASE
                        WHEN UPPER(status) = 'PENDING'
                        THEN 1 ELSE 0
                    END
                ) AS pending,
                SUM(
                    CASE
                        WHEN UPPER(status) = 'ACTIVE'
                        THEN 1 ELSE 0
                    END
                ) AS active,
                SUM(
                    CASE
                        WHEN UPPER(status) = 'COMPLETED'
                        THEN 1 ELSE 0
                    END
                ) AS completed,
                SUM(
                    CASE
                        WHEN UPPER(status) IN ('REJECTED', 'CANCELLED')
                        THEN 1 ELSE 0
                    END
                ) AS closed
            FROM collaborations
            WHERE college_id = %s
              AND UPPER(initiated_by) = 'INDUSTRY'
        """, (college_id,))

        stats = cursor.fetchone() or {}

        stats = {
            "total": stats.get("total") or 0,
            "pending": stats.get("pending") or 0,
            "active": stats.get("active") or 0,
            "completed": stats.get("completed") or 0,
            "closed": stats.get("closed") or 0
        }

        return render_template(
            "placement/receive-collaboration.html",
            collaborations=collaborations,
            collaboration_types=collaboration_types,
            stats=stats,
            search=search,
            selected_status=selected_status,
            selected_type=selected_type
        )

    except Exception as e:

        print("Placement Receive Collaboration Error:", e)

        flash(
            "Unable to load received collaboration requests.",
            "error"
        )

        return render_template(
            "placement/receive-collaboration.html",
            collaborations=[],
            collaboration_types=[],
            stats={
                "total": 0,
                "pending": 0,
                "active": 0,
                "completed": 0,
                "closed": 0
            },
            search=search,
            selected_status=selected_status,
            selected_type=selected_type
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ============================================================
# PLACEMENT CELL - NOTIFICATIONS
# ============================================================

@app.route("/placement/notifications")
@placement_required
def placement_notifications():

    user_id = session.get("user_id")

    if not user_id:
        flash("Session expired. Please login again.", "error")
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()
    selected_filter = request.args.get("filter", "all").strip().lower()

    if selected_filter not in ["all", "unread", "read"]:
        selected_filter = "all"

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT
                id,
                title,
                message,
                notification_type,
                is_read,
                created_at
            FROM notifications
            WHERE user_id = %s
        """

        params = [user_id]

        # Search
        if search:
            query += """
                AND (
                    title LIKE %s
                    OR message LIKE %s
                )
            """
            search_value = f"%{search}%"
            params.extend([search_value, search_value])

        # Filter
        if selected_filter == "unread":
            query += " AND is_read = 0"

        elif selected_filter == "read":
            query += " AND is_read = 1"

        query += " ORDER BY created_at DESC"

        cursor.execute(query, tuple(params))
        notifications = cursor.fetchall()

        # Statistics
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM notifications
            WHERE user_id = %s
        """, (user_id,))

        total_notifications = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS unread
            FROM notifications
            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        unread_count = cursor.fetchone()["unread"]

        cursor.execute("""
            SELECT COUNT(*) AS read_count
            FROM notifications
            WHERE user_id = %s
              AND is_read = 1
        """, (user_id,))

        read_count = cursor.fetchone()["read_count"]

        return render_template(
            "placement/notifications.html",
            notifications=notifications,
            total_notifications=total_notifications,
            unread_count=unread_count,
            read_count=read_count,
            search=search,
            selected_filter=selected_filter
        )

    except Exception as e:
        print("=" * 70)
        print("PLACEMENT NOTIFICATIONS ERROR:")
        print(type(e).__name__)
        print(str(e))
        print("=" * 70)

        flash("Unable to load notifications.", "error")
        return redirect(url_for("placement_dashboard"))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================
# PLACEMENT CELL - MARK NOTIFICATION AS READ
# ============================================================

@app.route(
    "/placement/notifications/<int:notification_id>/read",
    methods=["POST"]
)
@placement_required
def placement_mark_notification_read(notification_id):

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Session expired."
        }), 401

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE id = %s
              AND user_id = %s
        """, (notification_id, user_id))

        conn.commit()

        return jsonify({
            "success": True
        })

    except Exception as e:
        if conn:
            conn.rollback()

        print("PLACEMENT MARK NOTIFICATION ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": "Unable to mark notification as read."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============================================================
# PLACEMENT CELL - MARK ALL NOTIFICATIONS AS READ
# ============================================================

@app.route(
    "/placement/notifications/mark-all-read",
    methods=["POST"]
)
@placement_required
def placement_mark_all_notifications_read():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Session expired."
        }), 401

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        conn.commit()

        return jsonify({
            "success": True
        })

    except Exception as e:
        if conn:
            conn.rollback()

        print("PLACEMENT MARK ALL NOTIFICATIONS ERROR:", str(e))

        return jsonify({
            "success": False,
            "message": "Unable to mark notifications as read."
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - REPORTS
# =========================================================

@app.route("/placement/reports")
@placement_required
def placement_reports():

    conn = None
    cursor = None

    try:

        # =================================================
        # CURRENT PLACEMENT CELL / COLLEGE
        # =================================================

        college_id = session.get("college_id")

        if not college_id:

            flash(
                "College information not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # TOTAL STUDENTS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (
            college_id,
        ))

        total_students = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # APPLICATION STATISTICS
        # ONLY CURRENT COLLEGE STUDENTS
        # =================================================

        cursor.execute("""
            SELECT

                COUNT(*) AS total_applications,

                SUM(
                    CASE
                        WHEN sa.status = 'APPLIED'
                        THEN 1
                        ELSE 0
                    END
                ) AS applied,

                SUM(
                    CASE
                        WHEN sa.status = 'SHORTLISTED'
                        THEN 1
                        ELSE 0
                    END
                ) AS shortlisted,

                SUM(
                    CASE
                        WHEN sa.status = 'SELECTED'
                        THEN 1
                        ELSE 0
                    END
                ) AS selected,

                SUM(
                    CASE
                        WHEN sa.status = 'REJECTED'
                        THEN 1
                        ELSE 0
                    END
                ) AS rejected,

                SUM(
                    CASE
                        WHEN sa.status = 'WITHDRAWN'
                        THEN 1
                        ELSE 0
                    END
                ) AS withdrawn

            FROM student_applications sa

            INNER JOIN students s
                ON sa.student_id = s.id

            WHERE s.college_id = %s
        """, (
            college_id,
        ))

        application_stats = cursor.fetchone()


        total_applications = (
            application_stats["total_applications"] or 0
        )

        applied = (
            application_stats["applied"] or 0
        )

        shortlisted = (
            application_stats["shortlisted"] or 0
        )

        selected = (
            application_stats["selected"] or 0
        )

        rejected = (
            application_stats["rejected"] or 0
        )

        withdrawn = (
            application_stats["withdrawn"] or 0
        )


        # =================================================
        # PLACEMENT RATE
        # =================================================

        placement_rate = 0

        if total_students > 0:

            placement_rate = round(
                (
                    selected / total_students
                ) * 100,
                2
            )


        # =================================================
        # REPORT DATA
        # =================================================

        return render_template(
            "placement/reports.html",

            dashboard="reports",

            total_students=total_students,

            total_applications=total_applications,

            applied=applied,

            shortlisted=shortlisted,

            selected=selected,

            rejected=rejected,

            withdrawn=withdrawn,

            placement_rate=placement_rate
        )


    except mysql.connector.Error as e:

        print("=" * 70)
        print("PLACEMENT REPORTS DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Placement Cell reports.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT REPORTS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Placement Cell reports.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - PROFILE
# =========================================================

@app.route("/placement/profile")
@placement_required
def placement_profile():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Placement Cell session expired. Please login again.",
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
        # FETCH PLACEMENT CELL PROFILE
        # =================================================

        cursor.execute("""
            SELECT

                pc.id AS placement_cell_id,
                pc.user_id,
                pc.college_id,

                pc.representative_name,
                pc.designation,
                pc.phone,
                pc.email AS placement_email,
                pc.status AS placement_cell_status,

                u.name AS account_name,
                u.email AS account_email,
                u.status AS user_status,
                u.created_at AS account_created_at,

                c.college_name,
                c.college_code,
                c.university_name,
                c.status AS college_status

            FROM placement_cells pc

            INNER JOIN users u
                ON pc.user_id = u.id

            INNER JOIN colleges c
                ON pc.college_id = c.id

            WHERE pc.user_id = %s

            LIMIT 1
        """, (
            user_id,
        ))


        placement_cell = cursor.fetchone()


        # =================================================
        # PROFILE NOT FOUND
        # =================================================

        if not placement_cell:

            flash(
                "Placement Cell profile not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        # =================================================
        # PROFILE COMPLETION
        # =================================================

        profile_fields = [
            placement_cell.get("representative_name"),
            placement_cell.get("designation"),
            placement_cell.get("phone"),
            placement_cell.get("placement_email"),
            placement_cell.get("college_name"),
            placement_cell.get("college_code"),
            placement_cell.get("university_name")
        ]

        completed_fields = 0

        for value in profile_fields:

            if value is not None and str(value).strip():

                completed_fields += 1


        profile_completion = round(
            (
                completed_fields /
                len(profile_fields)
            ) * 100
        )


        # =================================================
        # COLLEGE STUDENT COUNT
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM students
            WHERE college_id = %s
        """, (
            placement_cell["college_id"],
        ))

        student_count = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # RENDER PROFILE
        # =================================================

        return render_template(
            "placement/profile.html",

            dashboard="profile",

            placement_cell=placement_cell,

            profile=placement_cell,

            profile_completion=profile_completion,

            student_count=student_count
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        print("=" * 70)
        print("PLACEMENT PROFILE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Placement Cell profile.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        print("=" * 70)
        print("PLACEMENT PROFILE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Placement Cell profile.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - UPDATE PROFILE
# =========================================================

@app.route(
    "/placement/profile/update",
    methods=["POST"]
)
@placement_required
def placement_update_profile():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Placement Cell session expired. Please login again.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # FORM DATA
        # =================================================

        representative_name = request.form.get(
            "representative_name",
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


        # =================================================
        # BASIC VALIDATION
        # =================================================

        if not representative_name:

            flash(
                "Representative name is required.",
                "error"
            )

            return redirect(
                url_for("placement_profile")
            )


        if not email:

            flash(
                "Email address is required.",
                "error"
            )

            return redirect(
                url_for("placement_profile")
            )


        if "@" not in email or "." not in email:

            flash(
                "Please enter a valid email address.",
                "error"
            )

            return redirect(
                url_for("placement_profile")
            )


        # =================================================
        # DATABASE CONNECTION
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # CHECK CURRENT PLACEMENT CELL
        # =================================================

        cursor.execute("""
            SELECT
                id,
                college_id,
                email
            FROM placement_cells
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        placement_cell = cursor.fetchone()


        if not placement_cell:

            flash(
                "Placement Cell profile not found.",
                "error"
            )

            return redirect(
                url_for("placement_dashboard")
            )


        # =================================================
        # CHECK EMAIL ALREADY USED BY ANOTHER USER
        # =================================================

        cursor.execute("""
            SELECT
                id
            FROM users
            WHERE email = %s
              AND id <> %s
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
                url_for("placement_profile")
            )


        # =================================================
        # UPDATE PLACEMENT CELL
        # =================================================

        cursor.execute("""
            UPDATE placement_cells
            SET
                representative_name = %s,
                designation = %s,
                phone = %s,
                email = %s
            WHERE user_id = %s
        """, (
            representative_name,
            designation if designation else None,
            phone if phone else None,
            email,
            user_id
        ))


        # =================================================
        # UPDATE USER ACCOUNT
        # =================================================

        cursor.execute("""
            UPDATE users
            SET
                name = %s,
                email = %s
            WHERE id = %s
        """, (
            representative_name,
            email,
            user_id
        ))


        # =================================================
        # COMMIT
        # =================================================

        conn.commit()


        # =================================================
        # UPDATE SESSION
        # =================================================

        session["user_name"] = representative_name
        session["user_email"] = email


        # =================================================
        # SUCCESS
        # =================================================

        flash(
            "Placement Cell profile updated successfully.",
            "success"
        )


        return redirect(
            url_for("placement_profile")
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT PROFILE UPDATE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update Placement Cell profile.",
            "error"
        )

        return redirect(
            url_for("placement_profile")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT PROFILE UPDATE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update Placement Cell profile.",
            "error"
        )

        return redirect(
            url_for("placement_profile")
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
# PLACEMENT CELL - MESSAGES
# =========================================================

@app.route("/placement/messages")
@placement_required
def placement_messages():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Placement Cell session expired. Please login again.",
                "error"
            )
            return redirect(url_for("login"))

        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------

        search = request.args.get(
            "search",
            ""
        ).strip()

        selected_folder = request.args.get(
            "folder",
            "inbox"
        ).strip().lower()

        if selected_folder not in [
            "inbox",
            "sent"
        ]:
            selected_folder = "inbox"


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # INBOX
        # =================================================

        if selected_folder == "inbox":

            query = """
                SELECT

                    m.id,
                    m.sender_id,
                    m.receiver_id,
                    m.subject,
                    m.message,
                    m.is_read,
                    m.created_at,

                    u.name AS sender_name,
                    u.email AS sender_email,
                    u.role AS sender_role

                FROM messages m

                INNER JOIN users u
                    ON m.sender_id = u.id

                WHERE m.receiver_id = %s
            """

            params = [
                user_id
            ]


            if search:

                query += """
                    AND (
                        m.subject LIKE %s
                        OR m.message LIKE %s
                        OR u.name LIKE %s
                        OR u.email LIKE %s
                    )
                """

                search_value = f"%{search}%"

                params.extend([
                    search_value,
                    search_value,
                    search_value,
                    search_value
                ])


            query += """
                ORDER BY m.created_at DESC
            """


        # =================================================
        # SENT
        # =================================================

        else:

            query = """
                SELECT

                    m.id,
                    m.sender_id,
                    m.receiver_id,
                    m.subject,
                    m.message,
                    m.is_read,
                    m.created_at,

                    u.name AS receiver_name,
                    u.email AS receiver_email,
                    u.role AS receiver_role

                FROM messages m

                INNER JOIN users u
                    ON m.receiver_id = u.id

                WHERE m.sender_id = %s
            """

            params = [
                user_id
            ]


            if search:

                query += """
                    AND (
                        m.subject LIKE %s
                        OR m.message LIKE %s
                        OR u.name LIKE %s
                        OR u.email LIKE %s
                    )
                """

                search_value = f"%{search}%"

                params.extend([
                    search_value,
                    search_value,
                    search_value,
                    search_value
                ])


            query += """
                ORDER BY m.created_at DESC
            """


        cursor.execute(
            query,
            tuple(params)
        )

        messages = cursor.fetchall()


        # =================================================
        # MESSAGE STATISTICS
        # =================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM messages
            WHERE receiver_id = %s
        """, (
            user_id,
        ))

        total_received = (
            cursor.fetchone()["total"] or 0
        )


        cursor.execute("""
            SELECT COUNT(*) AS unread
            FROM messages
            WHERE receiver_id = %s
              AND is_read = 0
        """, (
            user_id,
        ))

        unread_count = (
            cursor.fetchone()["unread"] or 0
        )


        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM messages
            WHERE sender_id = %s
        """, (
            user_id,
        ))

        total_sent = (
            cursor.fetchone()["total"] or 0
        )


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "placement/messages.html",

            messages=messages,

            selected_folder=selected_folder,
            search=search,

            total_received=total_received,
            unread_count=unread_count,
            total_sent=total_sent
        )


    except mysql.connector.Error as e:

        print("=" * 70)
        print("PLACEMENT MESSAGES DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load messages.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT MESSAGES ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load messages.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - SEND MESSAGE
# =========================================================

@app.route(
    "/placement/messages/send",
    methods=["POST"]
)
@placement_required
def placement_send_message():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            return jsonify({
                "success": False,
                "message": "Session expired. Please login again."
            }), 401


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


        # =================================================
        # VALIDATION
        # =================================================

        if not receiver_id:

            return jsonify({
                "success": False,
                "message": "Please select a recipient."
            }), 400


        if not subject:

            return jsonify({
                "success": False,
                "message": "Subject is required."
            }), 400


        if not message:

            return jsonify({
                "success": False,
                "message": "Message is required."
            }), 400


        if receiver_id == user_id:

            return jsonify({
                "success": False,
                "message": "You cannot send a message to yourself."
            }), 400


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # VERIFY RECEIVER
        # =================================================

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role,
                status
            FROM users
            WHERE id = %s
            LIMIT 1
        """, (
            receiver_id,
        ))

        receiver = cursor.fetchone()


        if not receiver:

            return jsonify({
                "success": False,
                "message": "Recipient not found."
            }), 404


        if receiver["status"] != "ACTIVE":

            return jsonify({
                "success": False,
                "message": "Recipient account is not active."
            }), 400


        # =================================================
        # INSERT MESSAGE
        # =================================================

        cursor.execute("""
            INSERT INTO messages (
                sender_id,
                receiver_id,
                subject,
                message,
                is_read,
                created_at
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                0,
                NOW()
            )
        """, (
            user_id,
            receiver_id,
            subject,
            message
        ))


        conn.commit()


        return jsonify({
            "success": True,
            "message": "Message sent successfully."
        })


    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT SEND MESSAGE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return jsonify({
            "success": False,
            "message": "Unable to send message."
        }), 500


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT SEND MESSAGE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return jsonify({
            "success": False,
            "message": "Something went wrong."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - MARK MESSAGE AS READ
# =========================================================

@app.route(
    "/placement/messages/<int:message_id>/read",
    methods=["POST"]
)
@placement_required
def placement_mark_message_read(message_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            return jsonify({
                "success": False,
                "message": "Session expired."
            }), 401


        conn = get_db_connection()

        cursor = conn.cursor()


        # =================================================
        # ONLY RECEIVER CAN MARK AS READ
        # =================================================

        cursor.execute("""
            UPDATE messages
            SET is_read = 1
            WHERE id = %s
              AND receiver_id = %s
        """, (
            message_id,
            user_id
        ))


        conn.commit()


        if cursor.rowcount == 0:

            return jsonify({
                "success": False,
                "message": "Message not found."
            }), 404


        return jsonify({
            "success": True,
            "message": "Message marked as read."
        })


    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT MARK MESSAGE READ DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return jsonify({
            "success": False,
            "message": "Unable to update message."
        }), 500


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT MARK MESSAGE READ ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return jsonify({
            "success": False,
            "message": "Something went wrong."
        }), 500


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# PLACEMENT CELL - SETTINGS
# =========================================================

@app.route("/placement/settings")
@placement_required
def placement_settings():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Placement Cell session expired. Please login again.",
                "error"
            )
            return redirect(url_for("login"))


        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        # =================================================
        # ACCOUNT
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
        """, (
            user_id,
        ))

        account = cursor.fetchone()


        if not account:

            flash(
                "Account not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # GET SETTINGS
        # =================================================

        cursor.execute("""
            SELECT
                id,
                user_id,
                notify_messages,
                notify_opportunities,
                notify_collaborations,
                theme_preference
            FROM placement_cell_settings
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        settings = cursor.fetchone()


        # =================================================
        # CREATE DEFAULT SETTINGS
        # =================================================

        if not settings:

            cursor.execute("""
                INSERT INTO placement_cell_settings (
                    user_id,
                    notify_messages,
                    notify_opportunities,
                    notify_collaborations,
                    theme_preference
                )
                VALUES (
                    %s,
                    TRUE,
                    TRUE,
                    TRUE,
                    'light'
                )
            """, (
                user_id,
            ))

            conn.commit()


            settings = {
                "notify_messages": True,
                "notify_opportunities": True,
                "notify_collaborations": True,
                "theme_preference": "light"
            }


        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "placement/settings.html",

            dashboard="settings",

            account=account,

            settings=settings
        )


    except mysql.connector.Error as e:

        print("=" * 70)
        print("PLACEMENT SETTINGS DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load settings.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    except Exception as e:

        print("=" * 70)
        print("PLACEMENT SETTINGS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load settings.",
            "error"
        )

        return redirect(
            url_for("placement_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PLACEMENT CELL - UPDATE NOTIFICATION SETTINGS
# =========================================================

@app.route(
    "/placement/settings/notifications",
    methods=["POST"]
)
@placement_required
def placement_update_notification_settings():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            return {
                "success": False,
                "message": "Session expired. Please login again."
            }, 401


        notify_messages = (
            request.form.get("notify_messages")
            == "true"
        )

        notify_opportunities = (
            request.form.get("notify_opportunities")
            == "true"
        )

        notify_collaborations = (
            request.form.get("notify_collaborations")
            == "true"
        )


        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute("""
            INSERT INTO placement_cell_settings (
                user_id,
                notify_messages,
                notify_opportunities,
                notify_collaborations
            )
            VALUES (
                %s,
                %s,
                %s,
                %s
            )
            ON DUPLICATE KEY UPDATE

                notify_messages =
                    VALUES(notify_messages),

                notify_opportunities =
                    VALUES(notify_opportunities),

                notify_collaborations =
                    VALUES(notify_collaborations)
        """, (
            user_id,
            notify_messages,
            notify_opportunities,
            notify_collaborations
        ))


        conn.commit()


        return {
            "success": True,
            "message": "Notification preferences saved."
        }


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT NOTIFICATION SETTINGS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

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
# PLACEMENT CELL - UPDATE APPEARANCE
# =========================================================

@app.route(
    "/placement/settings/appearance",
    methods=["POST"]
)
@placement_required
def placement_update_appearance():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            return {
                "success": False,
                "message": "Session expired."
            }, 401


        theme = request.form.get(
            "theme",
            "light"
        ).strip().lower()


        if theme not in [
            "light",
            "dark"
        ]:

            return {
                "success": False,
                "message": "Invalid theme selected."
            }, 400


        conn = get_db_connection()

        cursor = conn.cursor()


        cursor.execute("""
            INSERT INTO placement_cell_settings (
                user_id,
                theme_preference
            )
            VALUES (
                %s,
                %s
            )
            ON DUPLICATE KEY UPDATE

                theme_preference =
                    VALUES(theme_preference)
        """, (
            user_id,
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

        print("=" * 70)
        print("PLACEMENT APPEARANCE SETTINGS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

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
# PLACEMENT CELL - CHANGE PASSWORD
# =========================================================

@app.route(
    "/placement/settings/password",
    methods=["POST"]
)
@placement_required
def placement_change_password():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")


        if not user_id:

            return {
                "success": False,
                "message": "Session expired. Please login again."
            }, 401


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


        # =================================================
        # VALIDATION
        # =================================================

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
                "message":
                    "Password must be at least 6 characters."
            }, 400


        if new_password != confirm_password:

            return {
                "success": False,
                "message":
                    "New passwords do not match."
            }, 400


        if current_password == new_password:

            return {
                "success": False,
                "message":
                    "New password must be different from current password."
            }, 400


        # =================================================
        # DATABASE
        # =================================================

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )


        cursor.execute("""
            SELECT
                password
            FROM users
            WHERE id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        account = cursor.fetchone()


        if not account:

            return {
                "success": False,
                "message": "Account not found."
            }, 404


        # =================================================
        # VERIFY CURRENT PASSWORD
        # =================================================

        if account["password"] != current_password:

            return {
                "success": False,
                "message": "Current password is incorrect."
            }, 400


        # =================================================
        # UPDATE PASSWORD
        # =================================================

        cursor.execute("""
            UPDATE users
            SET password = %s
            WHERE id = %s
        """, (
            new_password,
            user_id
        ))


        conn.commit()


        return {
            "success": True,
            "message": "Password changed successfully."
        }


    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("PLACEMENT CHANGE PASSWORD ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

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
# STUDENT DASHBOARD
# =========================================================

@app.route("/student/dashboard")
@student_required
def student_dashboard():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =========================================================
        # CURRENT STUDENT
        # =========================================================

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

                u.name,
                u.email,

                c.college_name,
                c.college_code

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN colleges c
                ON s.college_id = c.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(url_for("login"))

        student_id = student["id"]

        # =========================================================
        # 1. APPLICATIONS
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications
            WHERE student_id = %s
        """, (student_id,))

        total_applications = (
            cursor.fetchone()["total"] or 0
        )

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_applications
            WHERE student_id = %s
              AND status IN (
                  'PENDING',
                  'SHORTLISTED',
                  'SELECTED'
              )
        """, (student_id,))

        active_applications = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 2. SKILLS
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_skills
            WHERE student_id = %s
        """, (student_id,))

        total_skills = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 3. CERTIFICATIONS
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_certifications
            WHERE student_id = %s
        """, (student_id,))

        total_certifications = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 4. PROJECTS
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_projects
            WHERE student_id = %s
        """, (student_id,))

        total_projects = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 5. ACHIEVEMENTS
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_achievements
            WHERE student_id = %s
        """, (student_id,))

        total_achievements = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 6. SKILL SCORE
        # Latest completed assessment percentage
        # =========================================================

        cursor.execute("""
            SELECT
                percentage
            FROM student_skill_assessment_attempts

            WHERE student_id = %s
              AND status = 'PASSED'
              AND percentage IS NOT NULL

            ORDER BY completed_at DESC

            LIMIT 1
        """, (student_id,))

        skill_score_row = cursor.fetchone()

        if skill_score_row:
            skill_score = round(
                float(skill_score_row["percentage"] or 0),
                2
            )
        else:
            skill_score = 0

        # =========================================================
        # 7. SKILL GAPS
        # Count unresolved skill gaps
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_skill_gaps

            WHERE student_id = %s
              AND status <> 'RESOLVED'
        """, (student_id,))

        skill_gaps = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 8. ACTIVE INTERNSHIP
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM internships

            WHERE student_id = %s

              AND status IN (
                  'OFFERED',
                  'ACCEPTED',
                  'IN_PROGRESS'
              )
        """, (student_id,))

        active_internships = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 9. UNREAD NOTIFICATIONS
        # =========================================================

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM notifications

            WHERE user_id = %s
              AND is_read = 0
        """, (user_id,))

        unread_notifications = (
            cursor.fetchone()["total"] or 0
        )

        # =========================================================
        # 10. RECENT APPLICATIONS
        # =========================================================

        cursor.execute("""
            SELECT
                sa.id AS application_id,
                sa.status,
                sa.application_date,
                sa.created_at,

                o.id AS opportunity_id,
                o.title AS opportunity_title,
                o.opportunity_type,

                i.company_name

            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE sa.student_id = %s

            ORDER BY
                sa.application_date DESC,
                sa.created_at DESC

            LIMIT 5
        """, (student_id,))

        recent_applications = cursor.fetchall()

        # =========================================================
        # 11. RECENT OPPORTUNITIES
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

                i.company_name

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE o.status = 'OPEN'

            ORDER BY o.created_at DESC

            LIMIT 5
        """)

        recent_opportunities = cursor.fetchall()

        # =========================================================
        # 12. PROFILE COMPLETION
        # =========================================================

        profile_completion = (
            student.get("profile_completed", 0) or 0
        )

        # =========================================================
        # DASHBOARD
        # =========================================================

        return render_template(
            "student/dashboard.html",

            dashboard="dashboard",
            active_page="dashboard",

            page_title="Student Dashboard",
            page_subtitle="Track your academic and career journey.",

            student=student,

            # Main intelligence metrics
            profile_completion=profile_completion,
            skill_score=skill_score,
            skill_gaps=skill_gaps,
            total_applications=total_applications,
            active_internships=active_internships,
            total_projects=total_projects,
            total_certifications=total_certifications,
            total_achievements=total_achievements,

            # Existing metrics
            active_applications=active_applications,
            total_skills=total_skills,
            unread_notifications=unread_notifications,

            # Recent sections
            recent_applications=recent_applications,
            recent_opportunities=recent_opportunities
        )

    except mysql.connector.Error as e:

        print(
            "STUDENT DASHBOARD DB ERROR:",
            e
        )

        flash(
            "Unable to load dashboard.",
            "error"
        )

        return redirect(url_for("login"))

    except Exception as e:

        print(
            "STUDENT DASHBOARD ERROR:",
            e
        )

        flash(
            "Unable to load dashboard.",
            "error"
        )

        return redirect(url_for("login"))

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================================
# STUDENT PROFILE
# =========================================================

@app.route("/student/profile", methods=["GET", "POST"])
@student_required
def student_profile():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Student session expired. Please login again.",
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
        # UPDATE PROFILE
        # =================================================

        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            dob = request.form.get(
                "dob",
                ""
            ).strip()

            gender = request.form.get(
                "gender",
                ""
            ).strip()

            address = request.form.get(
                "address",
                ""
            ).strip()

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

            resume_url = request.form.get(
                "resume_url",
                ""
            ).strip()


            # -------------------------------------------------
            # BASIC VALIDATION
            # -------------------------------------------------

            if not name:

                flash(
                    "Name is required.",
                    "error"
                )

                return redirect(
                    url_for("student_profile")
                )


            # -------------------------------------------------
            # UPDATE USER NAME
            # -------------------------------------------------

            cursor.execute(
                """
                UPDATE users

                SET name = %s

                WHERE id = %s
                """,
                (
                    name,
                    user_id
                )
            )


            # -------------------------------------------------
            # UPDATE STUDENT PROFILE
            # -------------------------------------------------

            cursor.execute(
                """
                UPDATE students

                SET
                    phone = NULLIF(%s, ''),
                    dob = NULLIF(%s, ''),
                    gender = NULLIF(%s, ''),
                    address = NULLIF(%s, ''),
                    linkedin_url = NULLIF(%s, ''),
                    github_url = NULLIF(%s, ''),
                    portfolio_url = NULLIF(%s, ''),
                    resume_url = NULLIF(%s, '')

                WHERE user_id = %s
                """,
                (
                    phone,
                    dob,
                    gender,
                    address,
                    linkedin_url,
                    github_url,
                    portfolio_url,
                    resume_url,
                    user_id
                )
            )
            # =================================================
            # CREATE INTERNSHIP WHEN APPLICATION IS SELECTED
            # =================================================

            if new_status == "SELECTED":

                cursor.execute("""
                    SELECT
                        sa.student_id,
                        sa.opportunity_id,
                        o.industry_id
                    FROM student_applications sa

                    INNER JOIN opportunities o
                        ON sa.opportunity_id = o.id

                    WHERE sa.id = %s

                    LIMIT 1
                """, (
                    application_id,
                ))

                selected_application = cursor.fetchone()

                if selected_application:

                    # Check whether internship already exists
                    cursor.execute("""
                        SELECT id
                        FROM internships
                        WHERE application_id = %s
                        LIMIT 1
                    """, (
                        application_id,
                    ))

                    existing_internship = cursor.fetchone()

                    # Create only if it does not already exist
                    if not existing_internship:

                        internship_id = str(uuid.uuid4())

                        cursor.execute("""
                            INSERT INTO internships
                            (
                                id,
                                application_id,
                                student_id,
                                opportunity_id,
                                industry_id,
                                status,
                                progress_percentage
                            )

                            VALUES
                            (
                                %s,
                                %s,
                                %s,
                                %s,
                                %s,
                                'OFFERED',
                                0.00
                            )
                        """, (
                            internship_id,
                            application_id,
                            selected_application["student_id"],
                            selected_application["opportunity_id"],
                            selected_application["industry_id"]
                        ))

            # -------------------------------------------------
            # COMMIT
            # -------------------------------------------------

            conn.commit()


            # -------------------------------------------------
            # SUCCESS
            # -------------------------------------------------

            session["user_name"] = name

            flash(
                "Profile updated successfully.",
                "success"
            )

            return redirect(
                url_for("student_profile")
            )


        # =================================================
        # LOAD STUDENT PROFILE
        # =================================================

        cursor.execute(
            """
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
                c.university_name

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN colleges c
                ON s.college_id = c.id

            WHERE s.user_id = %s

            LIMIT 1
            """,
            (
                user_id,
            )
        )


        student = cursor.fetchone()


        # =================================================
        # STUDENT NOT FOUND
        # =================================================

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # RENDER PROFILE
        # =================================================

        return render_template(
            "student/profile.html",

            dashboard="profile",
            active_page="profile",

            page_title="My Profile",
            page_subtitle="Manage your personal and professional information.",

            student=student
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT PROFILE DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update Student Profile.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT PROFILE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Student Profile.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT ACADEMIC
# =========================================================

@app.route("/student/academic", methods=["GET", "POST"])
@student_required
def student_academic():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:

            flash(
                "Student session expired. Please login again.",
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
        # UPDATE ACADEMIC INFORMATION
        # =================================================

        if request.method == "POST":

            semester = request.form.get(
                "semester",
                ""
            ).strip()

            passing_year = request.form.get(
                "passing_year",
                ""
            ).strip()

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
            # VALIDATION
            # -------------------------------------------------

            try:

                if semester:
                    semester_value = int(semester)
                else:
                    semester_value = None


                if passing_year:
                    passing_year_value = int(passing_year)
                else:
                    passing_year_value = None


                if cgpa:
                    cgpa_value = float(cgpa)
                else:
                    cgpa_value = None


                if current_sgpa:
                    current_sgpa_value = float(current_sgpa)
                else:
                    current_sgpa_value = None


                if active_backlogs:
                    active_backlogs_value = int(
                        active_backlogs
                    )
                else:
                    active_backlogs_value = 0


            except ValueError:

                flash(
                    "Please enter valid academic values.",
                    "error"
                )

                return redirect(
                    url_for("student_academic")
                )


            # -------------------------------------------------
            # RANGE VALIDATION
            # -------------------------------------------------

            if semester_value is not None:

                if semester_value < 1 or semester_value > 12:

                    flash(
                        "Semester must be between 1 and 12.",
                        "error"
                    )

                    return redirect(
                        url_for("student_academic")
                    )


            if cgpa_value is not None:

                if cgpa_value < 0 or cgpa_value > 10:

                    flash(
                        "CGPA must be between 0 and 10.",
                        "error"
                    )

                    return redirect(
                        url_for("student_academic")
                    )


            if current_sgpa_value is not None:

                if current_sgpa_value < 0 or current_sgpa_value > 10:

                    flash(
                        "Current SGPA must be between 0 and 10.",
                        "error"
                    )

                    return redirect(
                        url_for("student_academic")
                    )


            if active_backlogs_value < 0:

                flash(
                    "Active backlogs cannot be negative.",
                    "error"
                )

                return redirect(
                    url_for("student_academic")
                )


            # -------------------------------------------------
            # UPDATE DATABASE
            # -------------------------------------------------

            cursor.execute(
                """
                UPDATE students

                SET
                    semester = %s,
                    passing_year = %s,
                    cgpa = %s,
                    current_sgpa = %s,
                    active_backlogs = %s

                WHERE user_id = %s
                """,
                (
                    semester_value,
                    passing_year_value,
                    cgpa_value,
                    current_sgpa_value,
                    active_backlogs_value,
                    user_id
                )
            )


            # -------------------------------------------------
            # COMMIT
            # -------------------------------------------------

            conn.commit()


            flash(
                "Academic information updated successfully.",
                "success"
            )

            return redirect(
                url_for("student_academic")
            )


        # =================================================
        # LOAD ACADEMIC INFORMATION
        # =================================================

        cursor.execute(
            """
            SELECT

                s.id,
                s.user_id,
                s.college_id,

                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.passing_year,

                s.cgpa,
                s.current_sgpa,
                s.active_backlogs,

                u.name AS name,
                u.email AS email,

                c.college_name,
                c.college_code,
                c.university_name

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN colleges c
                ON s.college_id = c.id

            WHERE s.user_id = %s

            LIMIT 1
            """,
            (
                user_id,
            )
        )


        student = cursor.fetchone()


        # =================================================
        # STUDENT NOT FOUND
        # =================================================

        if not student:

            flash(
                "Student academic profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # =================================================
        # RENDER ACADEMIC PAGE
        # =================================================

        return render_template(
            "student/academic.html",

            dashboard="academic",
            active_page="academic",

            page_title="Academic Information",
            page_subtitle="View and manage your academic details.",

            student=student
        )


    # =====================================================
    # DATABASE ERROR
    # =====================================================

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT ACADEMIC DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update Academic Information.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT ACADEMIC ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load Academic Information.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )


    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - SKILLS
# =========================================================

@app.route("/student/skills")
@student_required
def student_skills():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET STUDENT SKILLS
        # -------------------------------------------------

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
        """, (
            student_id,
        ))

        skills = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        total_skills = len(skills)

        assessed_skills = 0
        verified_skills = 0

        for skill in skills:

            if skill["assessment_percentage"] is not None:
                assessed_skills += 1

            if str(
                skill["verification_status"] or ""
            ).upper() == "VERIFIED":
                verified_skills += 1

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------

        return render_template(
            "student/skills.html",

            dashboard="skills",
            active_page="skills",

            page_title="My Skills",
            page_subtitle="Build and manage your technical and professional skills.",

            student=student,
            skills=skills,

            total_skills=total_skills,
            assessed_skills=assessed_skills,
            verified_skills=verified_skills
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("STUDENT SKILLS DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load your skills.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT SKILLS ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load your skills.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - ADD SKILL
# =========================================================

@app.route(
    "/student/skills/add",
    methods=["POST"]
)
@student_required
def student_skill_add():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        skill_name = (
            request.form.get("skill_name", "")
            .strip()
        )

        proficiency_level = (
            request.form.get("proficiency_level", "")
            .strip()
            .upper()
        )

        assessment_percentage = (
            request.form.get(
                "assessment_percentage",
                ""
            )
            .strip()
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not skill_name:

            flash(
                "Skill name is required.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        if len(skill_name) > 150:

            flash(
                "Skill name cannot exceed 150 characters.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        # -------------------------------------------------
        # ACTUAL DB VALUES ARE UPPERCASE
        # BEGINNER / INTERMEDIATE / ADVANCED / EXPERT
        # -------------------------------------------------

        allowed_levels = [
            "BEGINNER",
            "INTERMEDIATE",
            "ADVANCED",
            "EXPERT"
        ]

        if proficiency_level not in allowed_levels:

            flash(
                "Please select a valid proficiency level.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        # -------------------------------------------------
        # ASSESSMENT PERCENTAGE
        # -------------------------------------------------

        if assessment_percentage == "":

            assessment_value = None

        else:

            try:

                assessment_value = float(
                    assessment_percentage
                )

            except ValueError:

                flash(
                    "Assessment percentage must be a valid number.",
                    "error"
                )

                return redirect(
                    url_for("student_skills")
                )

            if (
                assessment_value < 0
                or assessment_value > 100
            ):

                flash(
                    "Assessment percentage must be between 0 and 100.",
                    "error"
                )

                return redirect(
                    url_for("student_skills")
                )

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_db_connection()

        cursor = conn.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # GET CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id
            FROM student_skills
            WHERE student_id = %s
              AND LOWER(TRIM(skill_name))
                  = LOWER(TRIM(%s))
            LIMIT 1
        """, (
            student_id,
            skill_name
        ))

        existing_skill = cursor.fetchone()

        if existing_skill:

            flash(
                "This skill is already added.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        # -------------------------------------------------
        # INSERT
        #
        # ID IS GENERATED HERE BECAUSE student_skills.id
        # DOES NOT HAVE A DATABASE DEFAULT.
        # -------------------------------------------------

        skill_id = str(
            uuid.uuid4()
        )

        cursor.execute("""
            INSERT INTO student_skills
            (
                id,
                student_id,
                skill_name,
                proficiency_level,
                assessment_percentage
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            skill_id,
            student_id,
            skill_name,
            proficiency_level,
            assessment_value
        ))

        conn.commit()

        flash(
            "Skill added successfully.",
            "success"
        )

        return redirect(
            url_for("student_skills")
        )

    # -----------------------------------------------------
    # DATABASE ERROR
    # -----------------------------------------------------

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("ADD STUDENT SKILL DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to add skill. Check terminal for database error.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    # -----------------------------------------------------
    # GENERAL ERROR
    # -----------------------------------------------------

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("ADD STUDENT SKILL ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to add skill.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    # -----------------------------------------------------
    # CLOSE
    # -----------------------------------------------------

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - UPDATE SKILL
# =========================================================

@app.route(
    "/student/skills/<skill_id>/update",
    methods=["POST"]
)
@student_required
def student_skill_update(skill_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        skill_name = (
            request.form.get("skill_name")
            or ""
        ).strip()

        proficiency_level = (
            request.form.get("proficiency_level")
            or ""
        ).strip()

        assessment_percentage = (
            request.form.get("assessment_percentage")
            or ""
        ).strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not skill_name:

            flash(
                "Skill name is required.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        if len(skill_name) > 150:

            flash(
                "Skill name cannot exceed 150 characters.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        allowed_levels = [
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert"
        ]

        if proficiency_level not in allowed_levels:

            flash(
                "Please select a valid proficiency level.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        # -------------------------------------------------
        # PERCENTAGE
        # -------------------------------------------------

        if assessment_percentage == "":
            assessment_value = 0

        else:

            try:

                assessment_value = float(
                    assessment_percentage
                )

            except ValueError:

                flash(
                    "Assessment percentage must be a number.",
                    "error"
                )

                return redirect(
                    url_for("student_skills")
                )

            if (
                assessment_value < 0
                or assessment_value > 100
            ):

                flash(
                    "Assessment percentage must be between 0 and 100.",
                    "error"
                )

                return redirect(
                    url_for("student_skills")
                )

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # CHECK OWNERSHIP
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM student_skills

            WHERE id = %s
              AND student_id = %s

            LIMIT 1
        """, (
            skill_id,
            student_id
        ))

        existing_skill = cursor.fetchone()

        if not existing_skill:

            flash(
                "Skill not found.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM student_skills

            WHERE student_id = %s
              AND LOWER(TRIM(skill_name)) = LOWER(TRIM(%s))
              AND id != %s

            LIMIT 1
        """, (
            student_id,
            skill_name,
            skill_id
        ))

        duplicate = cursor.fetchone()

        if duplicate:

            flash(
                "Another skill with this name already exists.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        cursor.execute("""
            UPDATE student_skills

            SET
                skill_name = %s,
                proficiency_level = %s,
                assessment_percentage = %s

            WHERE id = %s
              AND student_id = %s
        """, (
            skill_name,
            proficiency_level,
            assessment_value,
            skill_id,
            student_id
        ))

        conn.commit()

        flash(
            "Skill updated successfully.",
            "success"
        )

        return redirect(
            url_for("student_skills")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("UPDATE STUDENT SKILL DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update skill.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("UPDATE STUDENT SKILL ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update skill.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - DELETE SKILL
# =========================================================

@app.route(
    "/student/skills/<skill_id>/delete",
    methods=["POST"]
)
@student_required
def student_skill_delete(skill_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # DELETE ONLY OWN SKILL
        # -------------------------------------------------

        cursor.execute("""
            DELETE FROM student_skills

            WHERE id = %s
              AND student_id = %s
        """, (
            skill_id,
            student_id
        ))

        if cursor.rowcount == 0:

            flash(
                "Skill not found.",
                "error"
            )

            return redirect(
                url_for("student_skills")
            )

        conn.commit()

        flash(
            "Skill deleted successfully.",
            "success"
        )

        return redirect(
            url_for("student_skills")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("DELETE STUDENT SKILL DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to delete skill.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("DELETE STUDENT SKILL ERROR:")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to delete skill.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - CERTIFICATIONS
# =========================================================

@app.route("/student/certifications")
@student_required
def student_certifications():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET CERTIFICATIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                student_id,
                certificate_name,
                issuing_organization,
                credential_id,
                issue_date,
                expiry_date,
                certificate_url,
                certificate_file,
                description,
                created_at,
                updated_at
            FROM student_certifications
            WHERE student_id = %s
            ORDER BY
                issue_date DESC,
                created_at DESC
        """, (
            student_id,
        ))

        certifications = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        total_certifications = len(certifications)

        valid_certifications = 0
        expired_certifications = 0
        no_expiry_certifications = 0

        for certification in certifications:

            expiry_date = certification.get(
                "expiry_date"
            )

            if not expiry_date:

                no_expiry_certifications += 1

            elif expiry_date >= __import__("datetime").date.today():

                valid_certifications += 1

            else:

                expired_certifications += 1

        return render_template(
            "student/certifications.html",

            student=student,

            certifications=certifications,

            total_certifications=total_certifications,

            valid_certifications=valid_certifications,

            expired_certifications=expired_certifications,

            no_expiry_certifications=no_expiry_certifications,

            active_page="certifications",

            page_title="My Certifications",

            page_subtitle="Manage your professional certifications and credentials."
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT CERTIFICATIONS ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load certifications.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADD CERTIFICATION
# =========================================================

@app.route(
    "/student/certifications/add",
    methods=["POST"]
)
@student_required
def student_certification_add():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        certificate_name = (
            request.form.get(
                "certificate_name",
                ""
            )
            .strip()
        )

        issuing_organization = (
            request.form.get(
                "issuing_organization",
                ""
            )
            .strip()
        )

        credential_id = (
            request.form.get(
                "credential_id",
                ""
            )
            .strip()
        )

        issue_date = (
            request.form.get(
                "issue_date",
                ""
            )
            .strip()
        )

        expiry_date = (
            request.form.get(
                "expiry_date",
                ""
            )
            .strip()
        )

        certificate_url = (
            request.form.get(
                "certificate_url",
                ""
            )
            .strip()
        )

        description = (
            request.form.get(
                "description",
                ""
            )
            .strip()
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not certificate_name:

            flash(
                "Certificate name is required.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        if len(certificate_name) > 200:

            flash(
                "Certificate name cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        if issuing_organization and len(
            issuing_organization
        ) > 200:

            flash(
                "Issuing organization cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        if credential_id and len(
            credential_id
        ) > 150:

            flash(
                "Credential ID cannot exceed 150 characters.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        if certificate_url and len(
            certificate_url
        ) > 255:

            flash(
                "Certificate URL cannot exceed 255 characters.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        # -------------------------------------------------
        # DATE VALIDATION
        # -------------------------------------------------

        if issue_date and expiry_date:

            if expiry_date < issue_date:

                flash(
                    "Expiry date cannot be before issue date.",
                    "error"
                )

                return redirect(
                    url_for("student_certifications")
                )

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

        if credential_id:

            cursor.execute("""
                SELECT id
                FROM student_certifications
                WHERE student_id = %s
                  AND credential_id = %s
                LIMIT 1
            """, (
                student_id,
                credential_id
            ))

            duplicate = cursor.fetchone()

            if duplicate:

                flash(
                    "A certification with this Credential ID already exists.",
                    "error"
                )

                return redirect(
                    url_for("student_certifications")
                )

        # -------------------------------------------------
        # FILE UPLOAD
        # -------------------------------------------------

        certificate_file_path = None

        uploaded_file = request.files.get(
            "certificate_file"
        )

        if uploaded_file and uploaded_file.filename:

            original_filename = secure_filename(
                uploaded_file.filename
            )

            if original_filename:

                upload_directory = os.path.join(
                    app.root_path,
                    "static",
                    "uploads",
                    "certificates"
                )

                os.makedirs(
                    upload_directory,
                    exist_ok=True
                )

                unique_filename = (
                    str(uuid.uuid4())
                    + "_"
                    + original_filename
                )

                file_path = os.path.join(
                    upload_directory,
                    unique_filename
                )

                uploaded_file.save(
                    file_path
                )

                certificate_file_path = (
                    "uploads/certificates/"
                    + unique_filename
                )

        # -------------------------------------------------
        # INSERT
        # -------------------------------------------------

        certification_id = str(
            uuid.uuid4()
        )

        cursor.execute("""
            INSERT INTO student_certifications
            (
                id,
                student_id,
                certificate_name,
                issuing_organization,
                credential_id,
                issue_date,
                expiry_date,
                certificate_url,
                certificate_file,
                description
            )
            VALUES
            (
                %s, %s, %s, %s, %s,
                NULLIF(%s, ''),
                NULLIF(%s, ''),
                %s, %s, %s
            )
        """, (
            certification_id,
            student_id,
            certificate_name,
            issuing_organization or None,
            credential_id or None,
            issue_date,
            expiry_date,
            certificate_url or None,
            certificate_file_path,
            description or None
        ))

        conn.commit()

        flash(
            "Certification added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student_certifications"
            )
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("ADD CERTIFICATION ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to add certification.",
            "error"
        )

        return redirect(
            url_for("student_certifications")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# UPDATE CERTIFICATION
# =========================================================

@app.route(
    "/student/certifications/<certification_id>/update",
    methods=["POST"]
)
@student_required
def student_certification_update(
    certification_id
):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        certificate_name = (
            request.form.get(
                "certificate_name",
                ""
            )
            .strip()
        )

        issuing_organization = (
            request.form.get(
                "issuing_organization",
                ""
            )
            .strip()
        )

        credential_id = (
            request.form.get(
                "credential_id",
                ""
            )
            .strip()
        )

        issue_date = (
            request.form.get(
                "issue_date",
                ""
            )
            .strip()
        )

        expiry_date = (
            request.form.get(
                "expiry_date",
                ""
            )
            .strip()
        )

        certificate_url = (
            request.form.get(
                "certificate_url",
                ""
            )
            .strip()
        )

        description = (
            request.form.get(
                "description",
                ""
            )
            .strip()
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not certificate_name:

            flash(
                "Certificate name is required.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        if issue_date and expiry_date:

            if expiry_date < issue_date:

                flash(
                    "Expiry date cannot be before issue date.",
                    "error"
                )

                return redirect(
                    url_for("student_certifications")
                )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # VERIFY OWNERSHIP
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                certificate_file
            FROM student_certifications
            WHERE id = %s
              AND student_id = %s
            LIMIT 1
        """, (
            certification_id,
            student_id
        ))

        existing = cursor.fetchone()

        if not existing:

            flash(
                "Certification not found.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        old_file = existing.get(
            "certificate_file"
        )

        # -------------------------------------------------
        # DUPLICATE CREDENTIAL CHECK
        # -------------------------------------------------

        if credential_id:

            cursor.execute("""
                SELECT id
                FROM student_certifications
                WHERE student_id = %s
                  AND credential_id = %s
                  AND id <> %s
                LIMIT 1
            """, (
                student_id,
                credential_id,
                certification_id
            ))

            duplicate = cursor.fetchone()

            if duplicate:

                flash(
                    "Another certification already uses this Credential ID.",
                    "error"
                )

                return redirect(
                    url_for("student_certifications")
                )

        # -------------------------------------------------
        # OPTIONAL NEW FILE
        # -------------------------------------------------

        new_file_path = old_file

        uploaded_file = request.files.get(
            "certificate_file"
        )

        if uploaded_file and uploaded_file.filename:

            original_filename = secure_filename(
                uploaded_file.filename
            )

            if original_filename:

                upload_directory = os.path.join(
                    app.root_path,
                    "static",
                    "uploads",
                    "certificates"
                )

                os.makedirs(
                    upload_directory,
                    exist_ok=True
                )

                unique_filename = (
                    str(uuid.uuid4())
                    + "_"
                    + original_filename
                )

                file_path = os.path.join(
                    upload_directory,
                    unique_filename
                )

                uploaded_file.save(
                    file_path
                )

                new_file_path = (
                    "uploads/certificates/"
                    + unique_filename
                )

                # Delete old file if it exists
                if old_file:

                    old_file_path = os.path.join(
                        app.root_path,
                        "static",
                        old_file
                    )

                    if os.path.exists(
                        old_file_path
                    ):

                        try:
                            os.remove(
                                old_file_path
                            )
                        except Exception:
                            pass

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        cursor.execute("""
            UPDATE student_certifications
            SET
                certificate_name = %s,
                issuing_organization = %s,
                credential_id = %s,
                issue_date = NULLIF(%s, ''),
                expiry_date = NULLIF(%s, ''),
                certificate_url = %s,
                certificate_file = %s,
                description = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND student_id = %s
        """, (
            certificate_name,
            issuing_organization or None,
            credential_id or None,
            issue_date,
            expiry_date,
            certificate_url or None,
            new_file_path,
            description or None,
            certification_id,
            student_id
        ))

        conn.commit()

        flash(
            "Certification updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student_certifications"
            )
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("UPDATE CERTIFICATION ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update certification.",
            "error"
        )

        return redirect(
            url_for("student_certifications")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# DELETE CERTIFICATION
# =========================================================

@app.route(
    "/student/certifications/<certification_id>/delete",
    methods=["POST"]
)
@student_required
def student_certification_delete(
    certification_id
):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET CERTIFICATION
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                certificate_file
            FROM student_certifications
            WHERE id = %s
              AND student_id = %s
            LIMIT 1
        """, (
            certification_id,
            student_id
        ))

        certification = cursor.fetchone()

        if not certification:

            flash(
                "Certification not found.",
                "error"
            )

            return redirect(
                url_for("student_certifications")
            )

        # -------------------------------------------------
        # DELETE DATABASE RECORD
        # -------------------------------------------------

        cursor.execute("""
            DELETE FROM student_certifications
            WHERE id = %s
              AND student_id = %s
        """, (
            certification_id,
            student_id
        ))

        conn.commit()

        # -------------------------------------------------
        # DELETE FILE
        # -------------------------------------------------

        certificate_file = certification.get(
            "certificate_file"
        )

        if certificate_file:

            file_path = os.path.join(
                app.root_path,
                "static",
                certificate_file
            )

            if os.path.exists(
                file_path
            ):

                try:
                    os.remove(
                        file_path
                    )
                except Exception:
                    pass

        flash(
            "Certification deleted successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student_certifications"
            )
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("DELETE CERTIFICATION ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to delete certification.",
            "error"
        )

        return redirect(
            url_for("student_certifications")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - PROJECTS
# =========================================================

@app.route("/student/projects")
@student_required
def student_projects():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET STUDENT PROJECTS
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

                i.company_name AS industry_name

            FROM student_projects sp

            LEFT JOIN industries i
                ON sp.industry_id = i.id

            WHERE sp.student_id = %s

            ORDER BY
                sp.created_at DESC
        """, (
            student_id,
        ))

        projects = cursor.fetchall()

        # -------------------------------------------------
        # GET ACTIVE INDUSTRIES
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                company_name
            FROM industries
            WHERE status = 'ACTIVE'
            ORDER BY company_name ASC
        """)

        industries = cursor.fetchall()

        # -------------------------------------------------
        # PROJECT STATISTICS
        # -------------------------------------------------

        total_projects = len(projects)

        ongoing_projects = 0
        completed_projects = 0
        cancelled_projects = 0

        for project in projects:

            status = project.get("status")

            if status == "ONGOING":
                ongoing_projects += 1

            elif status == "COMPLETED":
                completed_projects += 1

            elif status == "CANCELLED":
                cancelled_projects += 1

        return render_template(
            "student/projects.html",

            student=student,

            projects=projects,

            industries=industries,

            total_projects=total_projects,

            ongoing_projects=ongoing_projects,

            completed_projects=completed_projects,

            cancelled_projects=cancelled_projects,

            active_page="projects",

            page_title="My Projects",

            page_subtitle="Manage and showcase your academic and professional projects."
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT PROJECTS ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load projects.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADD PROJECT
# =========================================================

@app.route(
    "/student/projects/add",
    methods=["POST"]
)
@student_required
def student_project_add():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        industry_id = (
            request.form.get(
                "industry_id",
                ""
            )
            .strip()
            or None
        )

        title = (
            request.form.get(
                "title",
                ""
            )
            .strip()
        )

        description = (
            request.form.get(
                "description",
                ""
            )
            .strip()
        )

        technology_stack = (
            request.form.get(
                "technology_stack",
                ""
            )
            .strip()
        )

        start_date = (
            request.form.get(
                "start_date",
                ""
            )
            .strip()
            or None
        )

        end_date = (
            request.form.get(
                "end_date",
                ""
            )
            .strip()
            or None
        )

        status = (
            request.form.get(
                "status",
                "ONGOING"
            )
            .strip()
            .upper()
        )

        project_url = (
            request.form.get(
                "project_url",
                ""
            )
            .strip()
            or None
        )

        report_url = (
            request.form.get(
                "report_url",
                ""
            )
            .strip()
            or None
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Project title is required.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        if len(title) > 200:

            flash(
                "Project title cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        allowed_statuses = {
            "ONGOING",
            "COMPLETED",
            "CANCELLED"
        }

        if status not in allowed_statuses:

            flash(
                "Invalid project status.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        if start_date and end_date:

            if end_date < start_date:

                flash(
                    "End date cannot be before start date.",
                    "error"
                )

                return redirect(
                    url_for("student_projects")
                )

        if project_url and len(project_url) > 255:

            flash(
                "Project URL cannot exceed 255 characters.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        if report_url and len(report_url) > 255:

            flash(
                "Report URL cannot exceed 255 characters.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # INDUSTRY VALIDATION
        # -------------------------------------------------

        if industry_id:

            cursor.execute("""
                SELECT id
                FROM industries
                WHERE id = %s
                  AND status = 'ACTIVE'
                LIMIT 1
            """, (
                industry_id,
            ))

            industry = cursor.fetchone()

            if not industry:

                flash(
                    "Invalid industry selected.",
                    "error"
                )

                return redirect(
                    url_for("student_projects")
                )

        # -------------------------------------------------
        # INSERT PROJECT
        # -------------------------------------------------

        project_id = str(
            uuid.uuid4()
        )

        cursor.execute("""
            INSERT INTO student_projects
            (
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
            VALUES
            (
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

        flash(
            "Project added successfully.",
            "success"
        )

        return redirect(
            url_for("student_projects")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("ADD STUDENT PROJECT ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to add project.",
            "error"
        )

        return redirect(
            url_for("student_projects")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PROJECT DETAILS
# =========================================================

@app.route(
    "/student/projects/<project_id>"
)
@student_required
def student_project_detail(project_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET PROJECT
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

                i.company_name AS industry_name

            FROM student_projects sp

            LEFT JOIN industries i
                ON sp.industry_id = i.id

            WHERE sp.id = %s
              AND sp.student_id = %s

            LIMIT 1
        """, (
            project_id,
            student_id
        ))

        project = cursor.fetchone()

        if not project:

            flash(
                "Project not found.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        return render_template(
            "student/project_detail.html",
            project=project,
            active_page="projects",
            page_title=project["title"],
            page_subtitle="Project details"
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT PROJECT DETAIL ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load project details.",
            "error"
        )

        return redirect(
            url_for("student_projects")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# UPDATE PROJECT
# =========================================================

@app.route(
    "/student/projects/<project_id>/update",
    methods=["POST"]
)
@student_required
def student_project_update(project_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        industry_id = (
            request.form.get(
                "industry_id",
                ""
            )
            .strip()
            or None
        )

        title = (
            request.form.get(
                "title",
                ""
            )
            .strip()
        )

        description = (
            request.form.get(
                "description",
                ""
            )
            .strip()
        )

        technology_stack = (
            request.form.get(
                "technology_stack",
                ""
            )
            .strip()
        )

        start_date = (
            request.form.get(
                "start_date",
                ""
            )
            .strip()
            or None
        )

        end_date = (
            request.form.get(
                "end_date",
                ""
            )
            .strip()
            or None
        )

        status = (
            request.form.get(
                "status",
                "ONGOING"
            )
            .strip()
            .upper()
        )

        project_url = (
            request.form.get(
                "project_url",
                ""
            )
            .strip()
            or None
        )

        report_url = (
            request.form.get(
                "report_url",
                ""
            )
            .strip()
            or None
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Project title is required.",
                "error"
            )

            return redirect(
                url_for(
                    "student_project_detail",
                    project_id=project_id
                )
            )

        allowed_statuses = {
            "ONGOING",
            "COMPLETED",
            "CANCELLED"
        }

        if status not in allowed_statuses:

            flash(
                "Invalid project status.",
                "error"
            )

            return redirect(
                url_for(
                    "student_project_detail",
                    project_id=project_id
                )
            )

        if start_date and end_date:

            if end_date < start_date:

                flash(
                    "End date cannot be before start date.",
                    "error"
                )

                return redirect(
                    url_for(
                        "student_project_detail",
                        project_id=project_id
                    )
                )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # OWNERSHIP CHECK
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM student_projects
            WHERE id = %s
              AND student_id = %s
            LIMIT 1
        """, (
            project_id,
            student_id
        ))

        existing_project = cursor.fetchone()

        if not existing_project:

            flash(
                "Project not found.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        # -------------------------------------------------
        # INDUSTRY VALIDATION
        # -------------------------------------------------

        if industry_id:

            cursor.execute("""
                SELECT id
                FROM industries
                WHERE id = %s
                  AND status = 'ACTIVE'
                LIMIT 1
            """, (
                industry_id,
            ))

            if not cursor.fetchone():

                flash(
                    "Invalid industry selected.",
                    "error"
                )

                return redirect(
                    url_for(
                        "student_project_detail",
                        project_id=project_id
                    )
                )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        cursor.execute("""
            UPDATE student_projects
            SET
                industry_id = %s,
                title = %s,
                description = %s,
                technology_stack = %s,
                start_date = %s,
                end_date = %s,
                status = %s,
                project_url = %s,
                report_url = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND student_id = %s
        """, (
            industry_id,
            title,
            description or None,
            technology_stack or None,
            start_date,
            end_date,
            status,
            project_url,
            report_url,
            project_id,
            student_id
        ))

        conn.commit()

        flash(
            "Project updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student_project_detail",
                project_id=project_id
            )
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("UPDATE STUDENT PROJECT ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update project.",
            "error"
        )

        return redirect(
            url_for(
                "student_projects"
            )
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# DELETE PROJECT
# =========================================================

@app.route(
    "/student/projects/<project_id>/delete",
    methods=["POST"]
)
@student_required
def student_project_delete(project_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # DELETE ONLY OWN PROJECT
        # -------------------------------------------------

        cursor.execute("""
            DELETE FROM student_projects
            WHERE id = %s
              AND student_id = %s
        """, (
            project_id,
            student_id
        ))

        if cursor.rowcount == 0:

            flash(
                "Project not found.",
                "error"
            )

            return redirect(
                url_for("student_projects")
            )

        conn.commit()

        flash(
            "Project deleted successfully.",
            "success"
        )

        return redirect(
            url_for("student_projects")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("DELETE STUDENT PROJECT ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to delete project.",
            "error"
        )

        return redirect(
            url_for("student_projects")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - ACHIEVEMENTS
# =========================================================

@app.route("/student/achievements")
@student_required
def student_achievements():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET ACHIEVEMENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                student_id,
                title,
                description,
                achievement_type,
                achievement_date,
                issuing_organization,
                proof_url,
                created_at,
                updated_at
            FROM student_achievements
            WHERE student_id = %s
            ORDER BY
                achievement_date DESC,
                created_at DESC
        """, (
            student_id,
        ))

        achievements = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        total_achievements = len(achievements)

        dated_achievements = 0
        with_proof = 0
        organizations_count = set()

        for achievement in achievements:

            if achievement.get("achievement_date"):
                dated_achievements += 1

            if achievement.get("proof_url"):
                with_proof += 1

            organization = (
                achievement.get(
                    "issuing_organization"
                )
            )

            if organization:
                organizations_count.add(
                    organization.strip().lower()
                )

        total_organizations = len(
            organizations_count
        )

        return render_template(
            "student/achievements.html",

            student=student,

            achievements=achievements,

            total_achievements=total_achievements,

            dated_achievements=dated_achievements,

            with_proof=with_proof,

            total_organizations=total_organizations,

            active_page="achievements",

            page_title="My Achievements",

            page_subtitle="Showcase your accomplishments, awards and recognitions."
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT ACHIEVEMENTS ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load achievements.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# ADD ACHIEVEMENT
# =========================================================

@app.route(
    "/student/achievements/add",
    methods=["POST"]
)
@student_required
def student_achievement_add():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        title = (
            request.form.get(
                "title",
                ""
            )
            .strip()
        )

        description = (
            request.form.get(
                "description",
                ""
            )
            .strip()
        )

        achievement_type = (
            request.form.get(
                "achievement_type",
                ""
            )
            .strip()
        )

        achievement_date = (
            request.form.get(
                "achievement_date",
                ""
            )
            .strip()
            or None
        )

        issuing_organization = (
            request.form.get(
                "issuing_organization",
                ""
            )
            .strip()
        )

        proof_url = (
            request.form.get(
                "proof_url",
                ""
            )
            .strip()
            or None
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Achievement title is required.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if len(title) > 200:

            flash(
                "Achievement title cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if achievement_type and len(
            achievement_type
        ) > 100:

            flash(
                "Achievement type cannot exceed 100 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if issuing_organization and len(
            issuing_organization
        ) > 200:

            flash(
                "Issuing organization cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if proof_url and len(proof_url) > 255:

            flash(
                "Proof URL cannot exceed 255 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # INSERT
        # -------------------------------------------------

        achievement_id = str(
            uuid.uuid4()
        )

        cursor.execute("""
            INSERT INTO student_achievements
            (
                id,
                student_id,
                title,
                description,
                achievement_type,
                achievement_date,
                issuing_organization,
                proof_url
            )
            VALUES
            (
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
            achievement_id,
            student_id,
            title,
            description or None,
            achievement_type or None,
            achievement_date,
            issuing_organization or None,
            proof_url
        ))

        conn.commit()

        flash(
            "Achievement added successfully.",
            "success"
        )

        return redirect(
            url_for("student_achievements")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("ADD STUDENT ACHIEVEMENT ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to add achievement.",
            "error"
        )

        return redirect(
            url_for("student_achievements")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# UPDATE ACHIEVEMENT
# =========================================================

@app.route(
    "/student/achievements/<achievement_id>/update",
    methods=["POST"]
)
@student_required
def student_achievement_update(
    achievement_id
):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        title = (
            request.form.get(
                "title",
                ""
            )
            .strip()
        )

        description = (
            request.form.get(
                "description",
                ""
            )
            .strip()
        )

        achievement_type = (
            request.form.get(
                "achievement_type",
                ""
            )
            .strip()
        )

        achievement_date = (
            request.form.get(
                "achievement_date",
                ""
            )
            .strip()
            or None
        )

        issuing_organization = (
            request.form.get(
                "issuing_organization",
                ""
            )
            .strip()
        )

        proof_url = (
            request.form.get(
                "proof_url",
                ""
            )
            .strip()
            or None
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not title:

            flash(
                "Achievement title is required.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if len(title) > 200:

            flash(
                "Achievement title cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if achievement_type and len(
            achievement_type
        ) > 100:

            flash(
                "Achievement type cannot exceed 100 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if issuing_organization and len(
            issuing_organization
        ) > 200:

            flash(
                "Issuing organization cannot exceed 200 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        if proof_url and len(proof_url) > 255:

            flash(
                "Proof URL cannot exceed 255 characters.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # OWNERSHIP CHECK
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM student_achievements
            WHERE id = %s
              AND student_id = %s
            LIMIT 1
        """, (
            achievement_id,
            student_id
        ))

        existing = cursor.fetchone()

        if not existing:

            flash(
                "Achievement not found.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        cursor.execute("""
            UPDATE student_achievements
            SET
                title = %s,
                description = %s,
                achievement_type = %s,
                achievement_date = %s,
                issuing_organization = %s,
                proof_url = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND student_id = %s
        """, (
            title,
            description or None,
            achievement_type or None,
            achievement_date,
            issuing_organization or None,
            proof_url,
            achievement_id,
            student_id
        ))

        conn.commit()

        flash(
            "Achievement updated successfully.",
            "success"
        )

        return redirect(
            url_for("student_achievements")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("UPDATE STUDENT ACHIEVEMENT ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to update achievement.",
            "error"
        )

        return redirect(
            url_for("student_achievements")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# DELETE ACHIEVEMENT
# =========================================================

@app.route(
    "/student/achievements/<achievement_id>/delete",
    methods=["POST"]
)
@student_required
def student_achievement_delete(
    achievement_id
):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # DELETE ONLY OWN ACHIEVEMENT
        # -------------------------------------------------

        cursor.execute("""
            DELETE FROM student_achievements
            WHERE id = %s
              AND student_id = %s
        """, (
            achievement_id,
            student_id
        ))

        if cursor.rowcount == 0:

            flash(
                "Achievement not found.",
                "error"
            )

            return redirect(
                url_for("student_achievements")
            )

        conn.commit()

        flash(
            "Achievement deleted successfully.",
            "success"
        )

        return redirect(
            url_for("student_achievements")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("DELETE STUDENT ACHIEVEMENT ERROR")
        print(type(e).__name__)
        print(e)
        print(e)
        print("=" * 70)

        flash(
            "Unable to delete achievement.",
            "error"
        )

        return redirect(
            url_for("student_achievements")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - DIGITAL PORTFOLIO
# =========================================================

@app.route("/student/portfolio")
@student_required
def student_portfolio():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email,
                s.phone,
                s.github_url,
                s.linkedin_url,
                s.portfolio_url
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET PORTFOLIO
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                student_id,
                headline,
                bio,
                public_slug,
                is_public,
                created_at,
                updated_at
            FROM student_portfolios
            WHERE student_id = %s
            LIMIT 1
        """, (
            student_id,
        ))

        portfolio = cursor.fetchone()

        # -------------------------------------------------
        # GET SKILLS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                skill_name,
                proficiency_level,
                assessment_percentage,
                verification_status
            FROM student_skills
            WHERE student_id = %s
            ORDER BY
                assessment_percentage DESC,
                skill_name ASC
        """, (
            student_id,
        ))

        skills = cursor.fetchall()

        # -------------------------------------------------
        # GET CERTIFICATIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                certificate_name,
                issuing_organization,
                credential_id,
                issue_date,
                expiry_date,
                certificate_url,
                certificate_file,
                description
            FROM student_certifications
            WHERE student_id = %s
            ORDER BY
                issue_date DESC,
                created_at DESC
        """, (
            student_id,
        ))

        certifications = cursor.fetchall()

        # -------------------------------------------------
        # GET PROJECTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                sp.id,
                sp.title,
                sp.description,
                sp.technology_stack,
                sp.start_date,
                sp.end_date,
                sp.status,
                sp.project_url,
                sp.report_url,
                i.company_name AS industry_name
            FROM student_projects sp
            LEFT JOIN industries i
                ON sp.industry_id = i.id
            WHERE sp.student_id = %s
            ORDER BY
                sp.created_at DESC
        """, (
            student_id,
        ))

        projects = cursor.fetchall()

        # -------------------------------------------------
        # GET ACHIEVEMENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                title,
                description,
                achievement_type,
                achievement_date,
                issuing_organization,
                proof_url
            FROM student_achievements
            WHERE student_id = %s
            ORDER BY
                achievement_date DESC,
                created_at DESC
        """, (
            student_id,
        ))

        achievements = cursor.fetchall()

        # -------------------------------------------------
        # COUNTS
        # -------------------------------------------------

        portfolio_stats = {
            "skills": len(skills),
            "certifications": len(certifications),
            "projects": len(projects),
            "achievements": len(achievements)
        }

        return render_template(
            "student/digital_portfolio.html",

            student=student,

            portfolio=portfolio,

            skills=skills,

            certifications=certifications,

            projects=projects,

            achievements=achievements,

            portfolio_stats=portfolio_stats,

            active_page="portfolio",

            page_title="Digital Portfolio",

            page_subtitle="Build and showcase your professional profile."
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT PORTFOLIO ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load digital portfolio.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# CREATE / UPDATE DIGITAL PORTFOLIO
# =========================================================

@app.route(
    "/student/portfolio/save",
    methods=["POST"]
)
@student_required
def student_portfolio_save():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        # -------------------------------------------------
        # FORM DATA
        # -------------------------------------------------

        headline = (
            request.form.get(
                "headline",
                ""
            )
            .strip()
        )

        bio = (
            request.form.get(
                "bio",
                ""
            )
            .strip()
        )

        public_slug = (
            request.form.get(
                "public_slug",
                ""
            )
            .strip()
            .lower()
        )

        is_public = (
            request.form.get(
                "is_public"
            ) == "1"
        )

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if headline and len(headline) > 255:

            flash(
                "Headline cannot exceed 255 characters.",
                "error"
            )

            return redirect(
                url_for("student_portfolio")
            )

        # -------------------------------------------------
        # SLUG
        # -------------------------------------------------

        if public_slug:

            public_slug = re.sub(
                r"[^a-z0-9-]",
                "-",
                public_slug
            )

            public_slug = re.sub(
                r"-+",
                "-",
                public_slug
            )

            public_slug = public_slug.strip("-")

        if not public_slug:

            base_name = (
                student_name_for_slug
                if False
                else "student"
            )

            public_slug = (
                base_name
                + "-"
                + str(uuid.uuid4())[:8]
            )

        if len(public_slug) > 150:

            public_slug = public_slug[:150].rstrip("-")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                u.name
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # IF SLUG WAS NOT PROVIDED
        # GENERATE FROM STUDENT NAME
        # -------------------------------------------------

        if (
            not request.form.get(
                "public_slug",
                ""
            ).strip()
        ):

            generated_slug = re.sub(
                r"[^a-z0-9]+",
                "-",
                student["name"].lower()
            ).strip("-")

            if not generated_slug:

                generated_slug = "student"

            public_slug = (
                generated_slug
                + "-"
                + str(uuid.uuid4())[:8]
            )

        # -------------------------------------------------
        # CHECK EXISTING PORTFOLIO
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                public_slug
            FROM student_portfolios
            WHERE student_id = %s
            LIMIT 1
        """, (
            student_id,
        ))

        existing = cursor.fetchone()

        # -------------------------------------------------
        # CHECK SLUG DUPLICATE
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                student_id
            FROM student_portfolios
            WHERE public_slug = %s
            LIMIT 1
        """, (
            public_slug,
        ))

        slug_record = cursor.fetchone()

        if (
            slug_record
            and slug_record["student_id"] != student_id
        ):

            flash(
                "This public portfolio URL is already in use. Choose another slug.",
                "error"
            )

            return redirect(
                url_for("student_portfolio")
            )

        # -------------------------------------------------
        # UPDATE EXISTING
        # -------------------------------------------------

        if existing:

            cursor.execute("""
                UPDATE student_portfolios
                SET
                    headline = %s,
                    bio = %s,
                    public_slug = %s,
                    is_public = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE student_id = %s
            """, (
                headline or None,
                bio or None,
                public_slug,
                1 if is_public else 0,
                student_id
            ))

            message = (
                "Digital portfolio updated successfully."
            )

        # -------------------------------------------------
        # CREATE NEW
        # -------------------------------------------------

        else:

            portfolio_id = str(
                uuid.uuid4()
            )

            cursor.execute("""
                INSERT INTO student_portfolios
                (
                    id,
                    student_id,
                    headline,
                    bio,
                    public_slug,
                    is_public
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                portfolio_id,
                student_id,
                headline or None,
                bio or None,
                public_slug,
                1 if is_public else 0
            ))

            message = (
                "Digital portfolio created successfully."
            )

        conn.commit()

        flash(
            message,
            "success"
        )

        return redirect(
            url_for("student_portfolio")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("SAVE STUDENT PORTFOLIO ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to save digital portfolio.",
            "error"
        )

        return redirect(
            url_for("student_portfolio")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PUBLIC DIGITAL PORTFOLIO
# =========================================================

@app.route(
    "/portfolio/<public_slug>"
)
def public_student_portfolio(public_slug):

    conn = None
    cursor = None

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET PORTFOLIO
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                sp.id,
                sp.student_id,
                sp.headline,
                sp.bio,
                sp.public_slug,
                sp.is_public,

                u.name,
                u.email,

                s.github_url,
                s.linkedin_url,
                s.portfolio_url

            FROM student_portfolios sp

            INNER JOIN students s
                ON sp.student_id = s.id

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE sp.public_slug = %s
              AND sp.is_public = 1

            LIMIT 1
        """, (
            public_slug,
        ))

        portfolio = cursor.fetchone()

        if not portfolio:

            return render_template(
                "student/portfolio_not_found.html"
            ), 404

        student_id = portfolio["student_id"]

        # -------------------------------------------------
        # SKILLS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                skill_name,
                proficiency_level,
                assessment_percentage,
                verification_status
            FROM student_skills
            WHERE student_id = %s
            ORDER BY
                assessment_percentage DESC,
                skill_name ASC
        """, (
            student_id,
        ))

        skills = cursor.fetchall()

        # -------------------------------------------------
        # CERTIFICATIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                certificate_name,
                issuing_organization,
                credential_id,
                issue_date,
                expiry_date,
                certificate_url,
                certificate_file,
                description
            FROM student_certifications
            WHERE student_id = %s
            ORDER BY
                issue_date DESC,
                created_at DESC
        """, (
            student_id,
        ))

        certifications = cursor.fetchall()

        # -------------------------------------------------
        # PROJECTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                sp.title,
                sp.description,
                sp.technology_stack,
                sp.start_date,
                sp.end_date,
                sp.status,
                sp.project_url,
                sp.report_url,
                i.company_name AS industry_name
            FROM student_projects sp
            LEFT JOIN industries i
                ON sp.industry_id = i.id
            WHERE sp.student_id = %s
            ORDER BY
                sp.created_at DESC
        """, (
            student_id,
        ))

        projects = cursor.fetchall()

        # -------------------------------------------------
        # ACHIEVEMENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                title,
                description,
                achievement_type,
                achievement_date,
                issuing_organization,
                proof_url
            FROM student_achievements
            WHERE student_id = %s
            ORDER BY
                achievement_date DESC,
                created_at DESC
        """, (
            student_id,
        ))

        achievements = cursor.fetchall()

        return render_template(
            "student/public_portfolio.html",

            portfolio=portfolio,

            skills=skills,

            certifications=certifications,

            projects=projects,

            achievements=achievements
        )

    except Exception as e:

        print("=" * 70)
        print("PUBLIC PORTFOLIO ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        return "Unable to load portfolio.", 500

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - SKILL ASSESSMENT
# STEP 3.2
# =========================================================

@app.route("/student/skill-assessment")
@student_required
def student_skill_assessment():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # ACTIVE ASSESSMENTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                sa.id,
                sa.skill_id,
                sa.title,
                sa.description,
                sa.duration_minutes,
                sa.total_questions,
                sa.passing_percentage,

                sk.skill_name,
                sk.skill_category,

                COUNT(DISTINCT sq.id) AS question_count,

                (
                    SELECT COUNT(*)
                    FROM student_skill_assessment_attempts saa2
                    WHERE saa2.student_id = %s
                      AND saa2.assessment_id = sa.id
                      AND saa2.status IN ('COMPLETED', 'PASSED', 'FAILED')
                ) AS completed_before,

                (
                    SELECT saa3.id
                    FROM student_skill_assessment_attempts saa3
                    WHERE saa3.student_id = %s
                      AND saa3.assessment_id = sa.id
                      AND saa3.status = 'IN_PROGRESS'
                    ORDER BY saa3.started_at DESC
                    LIMIT 1
                ) AS in_progress_attempt_id

            FROM skill_assessments sa

            INNER JOIN skills sk
                ON sa.skill_id = sk.id

            LEFT JOIN skill_assessment_questions sq
                ON sq.assessment_id = sa.id

            WHERE sa.status = 'ACTIVE'
              AND sk.status = 'ACTIVE'

            GROUP BY
                sa.id,
                sa.skill_id,
                sa.title,
                sa.description,
                sa.duration_minutes,
                sa.total_questions,
                sa.passing_percentage,
                sk.skill_name,
                sk.skill_category

            HAVING COUNT(DISTINCT sq.id) > 0

            ORDER BY
                sk.skill_name ASC,
                sa.created_at DESC
        """, (
            student_id,
            student_id
        ))

        assessments = cursor.fetchall()

        # -------------------------------------------------
        # CURRENT IN-PROGRESS ATTEMPT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                saa.id,
                saa.assessment_id,
                saa.started_at,

                sa.title,
                sa.duration_minutes,
                sa.total_questions,

                sk.skill_name

            FROM student_skill_assessment_attempts saa

            INNER JOIN skill_assessments sa
                ON saa.assessment_id = sa.id

            INNER JOIN skills sk
                ON sa.skill_id = sk.id

            WHERE saa.student_id = %s
              AND saa.status = 'IN_PROGRESS'
              AND sa.status = 'ACTIVE'

            ORDER BY saa.started_at DESC

            LIMIT 1
        """, (
            student_id,
        ))

        active_attempt = cursor.fetchone()

        return render_template(
            "student/skill_assessment.html",

            dashboard="skill-assessment",
            active_page="skill-assessment",

            page_title="Skill Assessment",
            page_subtitle="Test your knowledge and measure your skill level.",

            student=student,

            assessments=assessments,

            active_attempt=active_attempt
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("STUDENT SKILL ASSESSMENT DATABASE ERROR:")
        print(type(e).__name__)
        print(e)
        print(e)

        flash(
            "Unable to load skill assessments.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT SKILL ASSESSMENT ERROR:")
        print(type(e).__name__)
        print(e)

        flash(
            "Unable to load skill assessments.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# START ASSESSMENT
# =========================================================

@app.route(
    "/student/skill-assessment/start/<assessment_id>"
)
@student_required
def student_skill_assessment_start(assessment_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # ASSESSMENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                sa.id,
                sa.skill_id,
                sa.title,
                sa.description,
                sa.duration_minutes,
                sa.total_questions,
                sa.passing_percentage,

                sk.skill_name,
                sk.skill_category

            FROM skill_assessments sa

            INNER JOIN skills sk
                ON sa.skill_id = sk.id

            WHERE sa.id = %s
              AND sa.status = 'ACTIVE'
              AND sk.status = 'ACTIVE'

            LIMIT 1
        """, (
            assessment_id,
        ))

        assessment = cursor.fetchone()

        if not assessment:

            flash(
                "Assessment submitted successfully. Your score has been recorded.",
                "success"
            )

            return redirect(
                url_for(
                    "student_assessment_result",
                    attempt_id=attempt_id
                )
            )
        # -------------------------------------------------
        # COUNT QUESTIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM skill_assessment_questions
            WHERE assessment_id = %s
        """, (
            assessment_id,
        ))

        question_count = (
            cursor.fetchone()["total"] or 0
        )

        if question_count == 0:

            flash(
                "This assessment has no questions yet.",
                "error"
            )

            return redirect(
                url_for("student_skill_assessment")
            )

        # -------------------------------------------------
        # RESUME EXISTING ATTEMPT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM student_skill_assessment_attempts

            WHERE student_id = %s
              AND assessment_id = %s
              AND status = 'IN_PROGRESS'

            ORDER BY started_at DESC

            LIMIT 1
        """, (
            student_id,
            assessment_id
        ))

        existing_attempt = cursor.fetchone()

        if existing_attempt:

            return redirect(
                url_for(
                    "student_skill_assessment_take",
                    attempt_id=existing_attempt["id"]
                )
            )

        # -------------------------------------------------
        # CREATE NEW ATTEMPT
        # -------------------------------------------------

        attempt_id = str(
            uuid.uuid4()
        )

        cursor.execute("""
            INSERT INTO student_skill_assessment_attempts
            (
                id,
                student_id,
                assessment_id,
                score,
                total_marks,
                percentage,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                0.00,
                0.00,
                0.00,
                'IN_PROGRESS'
            )
        """, (
            attempt_id,
            student_id,
            assessment_id
        ))

        conn.commit()

        return redirect(
            url_for(
                "student_skill_assessment_take",
                attempt_id=attempt_id
            )
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("START SKILL ASSESSMENT DATABASE ERROR:")
        print(type(e).__name__)
        print(e)

        flash(
            "Unable to start assessment.",
            "error"
        )

        return redirect(
            url_for("student_skill_assessment")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("START SKILL ASSESSMENT ERROR:")
        print(type(e).__name__)
        print(e)

        flash(
            "Unable to start assessment.",
            "error"
        )

        return redirect(
            url_for("student_skill_assessment")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# TAKE / RESUME ASSESSMENT
# =========================================================

@app.route(
    "/student/skill-assessment/take/<attempt_id>"
)
@student_required
def student_skill_assessment_take(attempt_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # GET STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                user_id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET OWN ATTEMPT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                saa.id,
                saa.student_id,
                saa.assessment_id,
                saa.started_at,
                saa.status,

                sa.title,
                sa.description,
                sa.duration_minutes,
                sa.total_questions,
                sa.passing_percentage,

                sk.skill_name

            FROM student_skill_assessment_attempts saa

            INNER JOIN skill_assessments sa
                ON saa.assessment_id = sa.id

            INNER JOIN skills sk
                ON sa.skill_id = sk.id

            WHERE saa.id = %s
              AND saa.student_id = %s
              AND saa.status = 'IN_PROGRESS'

            LIMIT 1
        """, (
            attempt_id,
            student_id
        ))

        attempt = cursor.fetchone()

        if not attempt:

            flash(
                "Assessment attempt not found or already completed.",
                "error"
            )

            return redirect(
                url_for("student_skill_assessment")
            )

        # -------------------------------------------------
        # QUESTIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                assessment_id,
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                marks,
                question_order

            FROM skill_assessment_questions

            WHERE assessment_id = %s

            ORDER BY
                question_order ASC,
                created_at ASC
        """, (
            attempt["assessment_id"],
        ))

        questions = cursor.fetchall()

        if not questions:

            flash(
                "No questions are available for this assessment.",
                "error"
            )

            return redirect(
                url_for("student_skill_assessment")
            )

        assessment = {
            "title": attempt["title"],
            "description": attempt["description"],
            "duration_minutes": attempt["duration_minutes"],
            "total_questions": len(questions),
            "passing_percentage": attempt["passing_percentage"],
            "skill_name": attempt["skill_name"]
        }

        return render_template(
            "student/skill_assessment_take.html",

            dashboard="skill-assessment",
            active_page="skill-assessment",

            page_title=attempt["title"],
            page_subtitle="Complete the assessment before the timer ends.",

            student=student,
            attempt=attempt,
            assessment=assessment,
            questions=questions
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("TAKE SKILL ASSESSMENT DATABASE ERROR:")
        print(type(e).__name__)
        print(e)

        flash(
            "Unable to load assessment.",
            "error"
        )

        return redirect(
            url_for("student_skill_assessment")
        )

    except Exception as e:

        print("=" * 70)
        print("TAKE SKILL ASSESSMENT ERROR:")
        print(type(e).__name__)
        print(e)

        flash(
            "Unable to load assessment.",
            "error"
        )

        return redirect(
            url_for("student_skill_assessment")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# SUBMIT ASSESSMENT
# =========================================================

@app.route(
    "/student/skill-assessment/submit/<attempt_id>",
    methods=["POST"]
)
@student_required
def student_skill_assessment_submit(attempt_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # OWN IN-PROGRESS ATTEMPT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                saa.id,
                saa.assessment_id,

                sa.passing_percentage,

                sk.skill_name

            FROM student_skill_assessment_attempts saa

            INNER JOIN skill_assessments sa
                ON saa.assessment_id = sa.id

            INNER JOIN skills sk
                ON sa.skill_id = sk.id

            WHERE saa.id = %s
              AND saa.student_id = %s
              AND saa.status = 'IN_PROGRESS'

            LIMIT 1
        """, (
            attempt_id,
            student_id
        ))

        attempt = cursor.fetchone()

        if not attempt:

            flash(
                "Assessment attempt is invalid or already completed.",
                "error"
            )

            return redirect(
                url_for("student_skill_assessment")
            )

        assessment_id = attempt["assessment_id"]

        # -------------------------------------------------
        # GET QUESTIONS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                correct_option,
                marks

            FROM skill_assessment_questions

            WHERE assessment_id = %s

            ORDER BY
                question_order ASC,
                created_at ASC
        """, (
            assessment_id,
        ))

        questions = cursor.fetchall()

        if not questions:

            flash(
                "Assessment questions were not found.",
                "error"
            )

            return redirect(
                url_for("student_skill_assessment")
            )

        # -------------------------------------------------
        # REMOVE ANY PREVIOUS ANSWERS
        # -------------------------------------------------

        cursor.execute("""
            DELETE FROM skill_assessment_answers
            WHERE attempt_id = %s
        """, (
            attempt_id,
        ))

        total_marks = 0.00
        score = 0.00

        # -------------------------------------------------
        # EVALUATE + SAVE ANSWERS
        # -------------------------------------------------

        for question in questions:

            question_id = question["id"]

            selected_option = (
                request.form.get(
                    "question_" + str(question_id)
                )
                or ""
            ).strip().upper()

            if selected_option not in [
                "A",
                "B",
                "C",
                "D"
            ]:

                selected_option = None

            marks = float(
                question["marks"] or 0
            )

            total_marks += marks

            is_correct = (
                selected_option is not None
                and selected_option
                    == str(
                        question["correct_option"]
                    ).upper()
            )

            marks_obtained = (
                marks
                if is_correct
                else 0.00
            )

            if is_correct:
                score += marks

            answer_id = str(
                uuid.uuid4()
            )

            cursor.execute("""
                INSERT INTO skill_assessment_answers
                (
                    id,
                    attempt_id,
                    question_id,
                    selected_option,
                    is_correct,
                    marks_obtained
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            """, (
                answer_id,
                attempt_id,
                question_id,
                selected_option,
                1 if is_correct else 0,
                marks_obtained
            ))

        # -------------------------------------------------
        # CALCULATE PERCENTAGE
        # -------------------------------------------------

        if total_marks > 0:

            percentage = (
                score / total_marks
            ) * 100

        else:

            percentage = 0.00

        passing_percentage = float(
            attempt["passing_percentage"] or 0
        )

        passed = (
            percentage >= passing_percentage
        )

        status = (
            "PASSED"
            if passed
            else "FAILED"
        )

        # -------------------------------------------------
        # UPDATE ATTEMPT
        # -------------------------------------------------

        cursor.execute("""
            UPDATE student_skill_assessment_attempts

            SET
                completed_at = CURRENT_TIMESTAMP,
                score = %s,
                total_marks = %s,
                percentage = %s,
                status = %s

            WHERE id = %s
              AND student_id = %s
        """, (
            round(score, 2),
            round(total_marks, 2),
            round(percentage, 2),
            status,
            attempt_id,
            student_id
        ))

        # -------------------------------------------------
        # UPDATE EXISTING STUDENT SKILL
        # -------------------------------------------------
        # Assessment result is reflected in student_skills
        # only when the student already has that skill.

        cursor.execute("""
            UPDATE student_skills ss

            INNER JOIN skills sk
                ON LOWER(TRIM(ss.skill_name))
                 = LOWER(TRIM(sk.skill_name))

            SET
                ss.assessment_percentage = %s,
                ss.last_assessed_at = CURRENT_TIMESTAMP

            WHERE ss.student_id = %s
              AND sk.id = (
                    SELECT skill_id
                    FROM skill_assessments
                    WHERE id = %s
              )
        """, (
            round(percentage, 2),
            student_id,
            assessment_id
        ))

        conn.commit()

        flash(
            "Assessment submitted successfully. Your score has been recorded.",
            "success"
        )

        # 3.3 will provide the dedicated result page.
        return redirect(
            url_for("student_skill_assessment")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("SUBMIT SKILL ASSESSMENT DATABASE ERROR:")
        print(type(e).__name__)
        print(e)

        flash(
            "Unable to submit assessment.",
            "error"
        )

        return redirect(
            url_for("student_skill_assessment")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("SUBMIT SKILL ASSESSMENT ERROR:")
        print(type(e).__name__)
        print(e)

        flash(
            "Unable to submit assessment.",
            "error"
        )

        return redirect(
            url_for("student_skill_assessment")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - ASSESSMENT RESULT
# STEP 3.3
# =========================================================

@app.route(
    "/student/assessment-result/<attempt_id>"
)
@student_required
def student_assessment_result(attempt_id):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET OWN COMPLETED ATTEMPT
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                saa.id,
                saa.student_id,
                saa.assessment_id,

                saa.started_at,
                saa.completed_at,

                saa.score,
                saa.total_marks,
                saa.percentage,

                saa.status,

                sa.title,
                sa.description,
                sa.duration_minutes,
                sa.total_questions,
                sa.passing_percentage,

                sk.id AS skill_id,
                sk.skill_name,
                sk.skill_category

            FROM student_skill_assessment_attempts saa

            INNER JOIN skill_assessments sa
                ON saa.assessment_id = sa.id

            INNER JOIN skills sk
                ON sa.skill_id = sk.id

            WHERE saa.id = %s
              AND saa.student_id = %s
              AND saa.status IN (
                    'COMPLETED',
                    'PASSED',
                    'FAILED'
              )

            LIMIT 1
        """, (
            attempt_id,
            student_id
        ))

        attempt = cursor.fetchone()

        if not attempt:

            flash(
                "Assessment result not found.",
                "error"
            )

            return redirect(
                url_for(
                    "student_skill_assessment"
                )
            )

        # -------------------------------------------------
        # QUESTIONS + ANSWERS
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                q.id AS question_id,
                q.question_text,

                q.option_a,
                q.option_b,
                q.option_c,
                q.option_d,

                q.correct_option,
                q.marks,
                q.question_order,

                a.selected_option,
                a.is_correct,
                a.marks_obtained

            FROM skill_assessment_questions q

            LEFT JOIN skill_assessment_answers a
                ON q.id = a.question_id
                AND a.attempt_id = %s

            WHERE q.assessment_id = %s

            ORDER BY
                q.question_order ASC,
                q.created_at ASC

        """, (
            attempt_id,
            attempt["assessment_id"]
        ))

        questions = cursor.fetchall()

        # -------------------------------------------------
        # RESULT STATISTICS
        # -------------------------------------------------

        total_questions = len(
            questions
        )

        correct_answers = 0
        incorrect_answers = 0
        unanswered = 0

        for question in questions:

            selected = question[
                "selected_option"
            ]

            if not selected:

                unanswered += 1

            elif question[
                "is_correct"
            ]:

                correct_answers += 1

            else:

                incorrect_answers += 1

        # -------------------------------------------------
        # STATUS LABEL
        # -------------------------------------------------

        status = (
            attempt["status"]
            or "FAILED"
        )

        if status == "PASSED":

            status_label = "Passed"

        elif status == "FAILED":

            status_label = "Failed"

        else:

            status_label = "Completed"

        # -------------------------------------------------
        # RENDER RESULT
        # -------------------------------------------------

        return render_template(
            "student/assessment_result.html",

            dashboard="assessment-results",
            active_page="assessment-results",

            page_title="Assessment Result",
            page_subtitle="Review your assessment performance.",

            student=student,

            attempt=attempt,

            questions=questions,

            total_questions=total_questions,

            correct_answers=correct_answers,

            incorrect_answers=incorrect_answers,

            unanswered=unanswered,

            status_label=status_label
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print(
            "STUDENT ASSESSMENT RESULT "
            "DATABASE ERROR:"
        )
        print(
            type(e).__name__
        )
        print(e)
        print("=" * 70)

        flash(
            "Unable to load assessment result.",
            "error"
        )

        return redirect(
            url_for(
                "student_skill_assessment"
            )
        )

    except Exception as e:

        print("=" * 70)
        print(
            "STUDENT ASSESSMENT RESULT ERROR:"
        )
        print(
            type(e).__name__
        )
        print(e)
        print("=" * 70)

        flash(
            "Unable to load assessment result.",
            "error"
        )

        return redirect(
            url_for(
                "student_skill_assessment"
            )
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - ASSESSMENT RESULT HISTORY
# =========================================================

@app.route(
    "/student/assessment-results"
)
@student_required
def student_assessment_results():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(
            dictionary=True
        )

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # COMPLETED RESULTS
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                saa.id,
                saa.assessment_id,

                saa.completed_at,
                saa.score,
                saa.total_marks,
                saa.percentage,
                saa.status,

                sa.title,

                sk.skill_name,
                sk.skill_category

            FROM student_skill_assessment_attempts saa

            INNER JOIN skill_assessments sa
                ON saa.assessment_id = sa.id

            INNER JOIN skills sk
                ON sa.skill_id = sk.id

            WHERE saa.student_id = %s

              AND saa.status IN (
                    'COMPLETED',
                    'PASSED',
                    'FAILED'
              )

            ORDER BY
                saa.completed_at DESC

        """, (
            student_id,
        ))

        results = cursor.fetchall()

        return render_template(
            "student/assessment_result.html",

            dashboard="assessment-results",
            active_page="assessment-results",

            page_title="Assessment Results",
            page_subtitle="Review your completed skill assessments.",

            student=student,

            results=results,

            result_history=True
        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print(
            "ASSESSMENT RESULT HISTORY "
            "DATABASE ERROR:"
        )
        print(
            type(e).__name__
        )
        print(e)
        print("=" * 70)

        flash(
            "Unable to load assessment results.",
            "error"
        )

        return redirect(
            url_for(
                "student_skill_assessment"
            )
        )

    except Exception as e:

        print("=" * 70)
        print(
            "ASSESSMENT RESULT HISTORY ERROR:"
        )
        print(
            type(e).__name__
        )
        print(e)
        print("=" * 70)

        flash(
            "Unable to load assessment results.",
            "error"
        )

        return redirect(
            url_for(
                "student_skill_assessment"
            )
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - SKILL PROFILE
# STEP 3.4
# =========================================================

@app.route("/student/skill-profile")
@student_required
def student_skill_profile():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(url_for("login"))

        student_id = student["id"]

        # -------------------------------------------------
        # SYNC STUDENT SKILLS -> SKILL PROFILES
        #
        # Only skills which exist in the master `skills`
        # table are synchronized.
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                ss.id,
                ss.skill_name,
                ss.proficiency_level,
                ss.assessment_percentage,
                ss.verification_status

            FROM student_skills ss

            WHERE ss.student_id = %s

            ORDER BY ss.skill_name ASC
        """, (student_id,))

        student_skills_data = cursor.fetchall()

        for skill in student_skills_data:

            cursor.execute("""
                SELECT
                    id,
                    skill_name

                FROM skills

                WHERE skill_name = %s
                  AND status = 'ACTIVE'

                LIMIT 1
            """, (
                skill["skill_name"],
            ))

            master_skill = cursor.fetchone()

            # If the skill is not yet in Skill Master,
            # don't create an invalid profile because
            # student_skill_profiles.skill_id is a FK.
            if not master_skill:
                continue

            # -------------------------------------------------
            # PROFICIENCY
            # -------------------------------------------------

            proficiency = (
                skill["proficiency_level"]
                or "BEGINNER"
            ).upper()

            allowed_levels = [
                "BEGINNER",
                "INTERMEDIATE",
                "ADVANCED",
                "EXPERT"
            ]

            if proficiency not in allowed_levels:

                proficiency = "BEGINNER"

            # -------------------------------------------------
            # SCORE
            # -------------------------------------------------

            assessment_percentage = (
                skill["assessment_percentage"]
            )

            if assessment_percentage is None:
                assessment_percentage = 0

            # -------------------------------------------------
            # SOURCE
            # -------------------------------------------------

            source = "SELF_DECLARED"

            if assessment_percentage > 0:
                source = "ASSESSMENT"

            verified = 0

            if (
                skill["verification_status"]
                and str(
                    skill["verification_status"]
                ).upper()
                in [
                    "VERIFIED",
                    "APPROVED"
                ]
            ):
                verified = 1
                source = "VERIFIED"

            # -------------------------------------------------
            # UPSERT PROFILE
            # -------------------------------------------------

            profile_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO student_skill_profiles
                (
                    id,
                    student_id,
                    skill_id,
                    proficiency_level,
                    skill_score,
                    source,
                    verified,
                    last_assessed_at
                )

                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    CASE
                        WHEN %s > 0
                        THEN CURRENT_TIMESTAMP
                        ELSE NULL
                    END
                )

                ON DUPLICATE KEY UPDATE

                    proficiency_level = VALUES(
                        proficiency_level
                    ),

                    skill_score = VALUES(
                        skill_score
                    ),

                    source = VALUES(
                        source
                    ),

                    verified = VALUES(
                        verified
                    ),

                    last_assessed_at =
                        CASE
                            WHEN VALUES(skill_score) > 0
                            THEN CURRENT_TIMESTAMP
                            ELSE last_assessed_at
                        END
            """, (
                profile_id,
                student_id,
                master_skill["id"],
                proficiency,
                assessment_percentage,
                source,
                verified,
                assessment_percentage
            ))

        conn.commit()

        # -------------------------------------------------
        # LOAD FINAL SKILL PROFILE
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                p.id,
                p.student_id,
                p.skill_id,

                sk.skill_name,
                sk.skill_category,
                sk.description,

                p.proficiency_level,
                p.skill_score,
                p.source,
                p.verified,

                p.last_assessed_at,
                p.created_at,
                p.updated_at

            FROM student_skill_profiles p

            INNER JOIN skills sk
                ON p.skill_id = sk.id

            WHERE p.student_id = %s

            ORDER BY
                p.skill_score DESC,
                sk.skill_name ASC
        """, (
            student_id,
        ))

        profiles = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        total_skills = len(profiles)

        assessed_skills = 0
        verified_skills = 0

        total_score = 0

        beginner_count = 0
        intermediate_count = 0
        advanced_count = 0
        expert_count = 0

        for profile in profiles:

            score = (
                float(
                    profile["skill_score"]
                    or 0
                )
            )

            total_score += score

            if score > 0:
                assessed_skills += 1

            if profile["verified"]:
                verified_skills += 1

            level = (
                profile["proficiency_level"]
                or "BEGINNER"
            )

            if level == "BEGINNER":
                beginner_count += 1

            elif level == "INTERMEDIATE":
                intermediate_count += 1

            elif level == "ADVANCED":
                advanced_count += 1

            elif level == "EXPERT":
                expert_count += 1

        average_score = (
            round(
                total_score / total_skills,
                2
            )
            if total_skills > 0
            else 0
        )

        return render_template(
            "student/skill_profile.html",

            dashboard="skill-profile",
            active_page="skill-profile",

            page_title="My Skill Profile",
            page_subtitle=(
                "View your skills, proficiency "
                "and assessment performance."
            ),

            student=student,

            profiles=profiles,

            total_skills=total_skills,
            assessed_skills=assessed_skills,
            verified_skills=verified_skills,
            average_score=average_score,

            beginner_count=beginner_count,
            intermediate_count=intermediate_count,
            advanced_count=advanced_count,
            expert_count=expert_count
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT SKILL PROFILE DATABASE ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load your skill profile.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT SKILL PROFILE ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load your skill profile.",
            "error"
        )

        return redirect(
            url_for("student_skills")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - SKILL GAP
# STEP 3.5
# =========================================================

@app.route("/student/skill-gap")
@student_required
def student_skill_gap():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.id
            WHERE s.user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(url_for("login"))

        student_id = student["id"]

        # -------------------------------------------------
        # GET SKILL GAPS
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                g.id,
                g.student_id,
                g.skill_id,

                g.current_level,
                g.required_level,

                g.gap_score,
                g.priority,
                g.status,

                sk.skill_name,
                sk.skill_category,
                sk.description,

                g.created_at,
                g.updated_at

            FROM student_skill_gaps g

            INNER JOIN skills sk
                ON g.skill_id = sk.id

            WHERE g.student_id = %s

            ORDER BY

                CASE g.priority
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END,

                g.gap_score DESC,

                sk.skill_name ASC
        """, (student_id,))

        gaps = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        total_gaps = len(gaps)

        critical_gaps = 0
        high_gaps = 0
        medium_gaps = 0
        low_gaps = 0

        open_gaps = 0
        improving_gaps = 0
        resolved_gaps = 0

        total_gap_score = 0

        for gap in gaps:

            gap_score = float(
                gap["gap_score"] or 0
            )

            total_gap_score += gap_score

            # Priority
            if gap["priority"] == "CRITICAL":
                critical_gaps += 1

            elif gap["priority"] == "HIGH":
                high_gaps += 1

            elif gap["priority"] == "MEDIUM":
                medium_gaps += 1

            elif gap["priority"] == "LOW":
                low_gaps += 1

            # Status
            if gap["status"] == "OPEN":
                open_gaps += 1

            elif gap["status"] == "IMPROVING":
                improving_gaps += 1

            elif gap["status"] == "RESOLVED":
                resolved_gaps += 1

        average_gap_score = (
            round(
                total_gap_score / total_gaps,
                2
            )
            if total_gaps > 0
            else 0
        )

        return render_template(
            "student/skill_gap.html",

            dashboard="skill-gap",
            active_page="skill-gap",

            page_title="Skill Gap",
            page_subtitle=(
                "Identify the skills you need to "
                "improve for your career goals."
            ),

            student=student,

            gaps=gaps,

            total_gaps=total_gaps,

            critical_gaps=critical_gaps,
            high_gaps=high_gaps,
            medium_gaps=medium_gaps,
            low_gaps=low_gaps,

            open_gaps=open_gaps,
            improving_gaps=improving_gaps,
            resolved_gaps=resolved_gaps,

            average_gap_score=average_gap_score
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT SKILL GAP DATABASE ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load skill gaps.",
            "error"
        )

        return redirect(
            url_for("student_skill_profile")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print("STUDENT SKILL GAP ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load skill gaps.",
            "error"
        )

        return redirect(
            url_for("student_skill_profile")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - LEARNING RECOMMENDATIONS
# STEP 3.6
# =========================================================

@app.route("/student/learning-recommendations")
@student_required
def student_learning_recommendations():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        student_id = student["id"]

        # -------------------------------------------------
        # GET LEARNING RECOMMENDATIONS
        #
        # Student Skill Gap
        #      ↓
        # learning_program_skills
        #      ↓
        # learning_programs
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                g.id AS gap_id,
                g.skill_id,
                g.current_level,
                g.required_level,
                g.gap_score,
                g.priority,
                g.status AS gap_status,

                sk.skill_name,
                sk.skill_category,

                lp.id AS program_id,
                lp.title,
                lp.provider,
                lp.description,
                lp.learning_type,
                lp.level,
                lp.duration,
                lp.url,

                lps.relevance_score

            FROM student_skill_gaps g

            INNER JOIN skills sk
                ON g.skill_id = sk.id

            INNER JOIN learning_program_skills lps
                ON g.skill_id = lps.skill_id

            INNER JOIN learning_programs lp
                ON lps.program_id = lp.id

            WHERE g.student_id = %s

              AND lp.status = 'ACTIVE'

              AND g.status != 'RESOLVED'

            ORDER BY

                CASE g.priority
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    WHEN 'MEDIUM' THEN 3
                    WHEN 'LOW' THEN 4
                    ELSE 5
                END,

                lps.relevance_score DESC,

                lp.title ASC
        """, (student_id,))

        recommendation_rows = cursor.fetchall()

        # -------------------------------------------------
        # GROUP RECOMMENDATIONS BY SKILL
        # -------------------------------------------------

        recommendations = {}

        for row in recommendation_rows:

            skill_id = row["skill_id"]

            if skill_id not in recommendations:

                recommendations[skill_id] = {
                    "skill_id": skill_id,
                    "skill_name": row["skill_name"],
                    "skill_category": row["skill_category"],
                    "current_level": row["current_level"],
                    "required_level": row["required_level"],
                    "gap_score": row["gap_score"],
                    "priority": row["priority"],
                    "gap_status": row["gap_status"],
                    "programs": []
                }

            recommendations[skill_id]["programs"].append({
                "program_id": row["program_id"],
                "title": row["title"],
                "provider": row["provider"],
                "description": row["description"],
                "learning_type": row["learning_type"],
                "level": row["level"],
                "duration": row["duration"],
                "url": row["url"],
                "relevance_score": row["relevance_score"]
            })

        recommendations = list(
            recommendations.values()
        )

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        total_recommendations = 0
        total_skills = len(recommendations)

        high_priority_skills = 0
        critical_priority_skills = 0

        for recommendation in recommendations:

            total_recommendations += len(
                recommendation["programs"]
            )

            if recommendation["priority"] == "HIGH":
                high_priority_skills += 1

            elif recommendation["priority"] == "CRITICAL":
                critical_priority_skills += 1

        return render_template(
            "student/learning_recommendations.html",

            dashboard="learning-recommendations",
            active_page="learning-recommendations",

            page_title="Learning Recommendations",
            page_subtitle=(
                "Personalized learning resources "
                "based on your skill gaps."
            ),

            student=student,

            recommendations=recommendations,

            total_recommendations=
                total_recommendations,

            total_skills=
                total_skills,

            high_priority_skills=
                high_priority_skills,

            critical_priority_skills=
                critical_priority_skills
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print(
            "STUDENT LEARNING RECOMMENDATIONS "
            "DATABASE ERROR"
        )
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load learning recommendations.",
            "error"
        )

        return redirect(
            url_for("student_skill_gap")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print("=" * 70)
        print(
            "STUDENT LEARNING RECOMMENDATIONS ERROR"
        )
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load learning recommendations.",
            "error"
        )

        return redirect(
            url_for("student_skill_gap")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - OPPORTUNITIES
# PHASE 4.1 - OPPORTUNITIES UPGRADE
# =========================================================

@app.route("/student/opportunities")
@student_required
def student_opportunities():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Student session expired. Please login again.",
                "error"
            )
            return redirect(url_for("login"))

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id AS student_id,
                s.enrollment_no,
                s.course,
                s.branch,
                s.semester,
                s.cgpa,
                s.active_backlogs,
                s.profile_completed,
                s.resume_url,

                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        student_id = student["student_id"]

        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------

        search = request.args.get(
            "search",
            ""
        ).strip()

        opportunity_type = request.args.get(
            "opportunity_type",
            ""
        ).strip().upper()

        work_mode = request.args.get(
            "work_mode",
            ""
        ).strip().upper()

        # -------------------------------------------------
        # STUDENT SKILLS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                skill_name,
                proficiency_level,
                assessment_percentage

            FROM student_skills

            WHERE student_id = %s
        """, (student_id,))

        student_skill_rows = cursor.fetchall()

        student_skills = []

        for skill in student_skill_rows:

            skill_name = (
                str(skill["skill_name"])
                .strip()
                .lower()
            )

            if skill_name:
                student_skills.append(
                    skill_name
                )

        # -------------------------------------------------
        # APPLICATION MAP
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                opportunity_id,
                status

            FROM student_applications

            WHERE student_id = %s
        """, (student_id,))

        application_rows = cursor.fetchall()

        application_map = {}

        for application in application_rows:

            application_map[
                application["opportunity_id"]
            ] = application["status"]

        # -------------------------------------------------
        # BASE OPPORTUNITY QUERY
        # -------------------------------------------------

        query = """
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

                i.company_name,
                i.company_type,
                i.industry_sector

            FROM opportunities o

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE o.status = 'OPEN'

              AND i.status = 'ACTIVE'

              AND (
                    o.application_deadline IS NULL
                    OR o.application_deadline >= CURDATE()
              )
        """

        params = []

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        if search:

            query += """
                AND (
                    o.title LIKE %s
                    OR o.description LIKE %s
                    OR o.required_skills LIKE %s
                    OR i.company_name LIKE %s
                )
            """

            search_value = (
                "%" + search + "%"
            )

            params.extend([
                search_value,
                search_value,
                search_value,
                search_value
            ])

        # -------------------------------------------------
        # OPPORTUNITY TYPE
        # -------------------------------------------------

        allowed_types = [
            "INTERNSHIP",
            "PLACEMENT",
            "PROJECT",
            "TRAINING",
            "JOB"
        ]

        if opportunity_type in allowed_types:

            query += """
                AND o.opportunity_type = %s
            """

            params.append(
                opportunity_type
            )

        # -------------------------------------------------
        # WORK MODE
        # -------------------------------------------------

        allowed_work_modes = [
            "ONSITE",
            "REMOTE",
            "HYBRID"
        ]

        if work_mode in allowed_work_modes:

            query += """
                AND o.work_mode = %s
            """

            params.append(
                work_mode
            )

        # -------------------------------------------------
        # ORDER
        # -------------------------------------------------

        query += """

            ORDER BY

                CASE
                    WHEN o.application_deadline IS NULL
                    THEN 1
                    ELSE 0
                END,

                o.application_deadline ASC,

                o.created_at DESC
        """

        cursor.execute(
            query,
            params
        )

        opportunities = cursor.fetchall()

        # -------------------------------------------------
        # PROCESS EACH OPPORTUNITY
        # -------------------------------------------------

        processed_opportunities = []

        for opportunity in opportunities:

            # ---------------------------------------------
            # REQUIRED SKILLS
            # ---------------------------------------------

            required_text = (
                opportunity["required_skills"]
                or ""
            )

            required_text = (
                required_text
                .replace(";", ",")
                .replace("\n", ",")
            )

            required_skills = [
                skill.strip().lower()
                for skill in required_text.split(",")
                if skill.strip()
            ]

            # ---------------------------------------------
            # MATCHED SKILLS
            # ---------------------------------------------

            matched_skills = []

            for required_skill in required_skills:

                for student_skill in student_skills:

                    if (
                        required_skill in student_skill
                        or
                        student_skill in required_skill
                    ):

                        matched_skills.append(
                            required_skill
                        )

                        break

            # Remove duplicates
            matched_skills = list(
                dict.fromkeys(
                    matched_skills
                )
            )

            # ---------------------------------------------
            # SKILL MATCH PERCENTAGE
            # ---------------------------------------------

            if required_skills:

                skill_match_percentage = round(
                    (
                        len(matched_skills)
                        /
                        len(required_skills)
                    ) * 100,
                    2
                )

            else:

                skill_match_percentage = 100

            # ---------------------------------------------
            # MISSING SKILLS
            # ---------------------------------------------

            missing_skills = [
                skill
                for skill in required_skills
                if skill not in matched_skills
            ]

            # ---------------------------------------------
            # CGPA ELIGIBILITY
            # ---------------------------------------------

            criteria_text = (
                opportunity[
                    "eligibility_criteria"
                ]
                or ""
            ).lower()

            cgpa_ok = True

            cgpa_matches = re.findall(
                r'(?:minimum\s*)?cgpa'
                r'\s*(?:>=|>|:|is|of)?'
                r'\s*(\d+(?:\.\d+)?)',
                criteria_text
            )

            if cgpa_matches:

                required_cgpa = float(
                    cgpa_matches[0]
                )

                if student["cgpa"] is None:

                    cgpa_ok = False

                else:

                    cgpa_ok = (
                        float(student["cgpa"])
                        >= required_cgpa
                    )

            # ---------------------------------------------
            # BACKLOG ELIGIBILITY
            # ---------------------------------------------

            backlog_ok = True

            if student["active_backlogs"]:

                try:

                    backlog_ok = (
                        int(
                            student[
                                "active_backlogs"
                            ]
                        ) == 0
                    )

                except (ValueError, TypeError):

                    backlog_ok = False

            # ---------------------------------------------
            # SKILL ELIGIBILITY
            #
            # Existing project logic considers a student
            # skill-eligible when at least one required
            # skill matches.
            # ---------------------------------------------

            skills_ok = (
                not required_skills
                or bool(matched_skills)
            )

            # ---------------------------------------------
            # FINAL ELIGIBILITY
            # ---------------------------------------------

            eligible = (
                cgpa_ok
                and backlog_ok
                and skills_ok
            )

            # ---------------------------------------------
            # APPLICATION STATUS
            # ---------------------------------------------

            application_status = (
                application_map.get(
                    opportunity["id"]
                )
            )

            # ---------------------------------------------
            # DEADLINE DAYS
            # ---------------------------------------------

            deadline = (
                opportunity[
                    "application_deadline"
                ]
            )

            days_left = None

            if deadline:

                try:

                    days_left = (
                        deadline
                        - datetime.now().date()
                    ).days

                except Exception:

                    days_left = None

            # ---------------------------------------------
            # ATTACH CALCULATED DATA
            # ---------------------------------------------

            opportunity[
                "required_skills_list"
            ] = required_skills

            opportunity[
                "matched_skills"
            ] = matched_skills

            opportunity[
                "missing_skills"
            ] = missing_skills

            opportunity[
                "skill_match_percentage"
            ] = skill_match_percentage

            opportunity[
                "cgpa_ok"
            ] = cgpa_ok

            opportunity[
                "backlog_ok"
            ] = backlog_ok

            opportunity[
                "skills_ok"
            ] = skills_ok

            opportunity[
                "eligible"
            ] = eligible

            opportunity[
                "application_status"
            ] = application_status

            opportunity[
                "days_left"
            ] = days_left

            processed_opportunities.append(
                opportunity
            )

        # -------------------------------------------------
        # STATS
        # -------------------------------------------------

        total_opportunities = len(
            processed_opportunities
        )

        eligible_opportunities = sum(
            1
            for opportunity
            in processed_opportunities
            if opportunity["eligible"]
        )

        high_match_opportunities = sum(
            1
            for opportunity
            in processed_opportunities
            if opportunity[
                "skill_match_percentage"
            ] >= 75
        )

        active_deadlines = sum(
            1
            for opportunity
            in processed_opportunities
            if (
                opportunity["application_deadline"]
                is not None
            )
        )

        total_applications = len(
            application_rows
        )

        shortlisted_applications = sum(
            1
            for application
            in application_rows
            if application["status"]
            == "SHORTLISTED"
        )

        return render_template(

            "student/opportunities.html",

            dashboard="opportunities",
            active_page="opportunities",

            student=student,

            opportunities=
                processed_opportunities,

            total_opportunities=
                total_opportunities,

            eligible_opportunities=
                eligible_opportunities,

            high_match_opportunities=
                high_match_opportunities,

            active_deadlines=
                active_deadlines,

            total_applications=
                total_applications,

            shortlisted_applications=
                shortlisted_applications,

            search=search,

            opportunity_type=
                opportunity_type,

            work_mode=
                work_mode

        )

    except mysql.connector.Error as e:

        print("=" * 70)
        print("STUDENT OPPORTUNITIES DATABASE ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load opportunities.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    except Exception as e:

        print("=" * 70)
        print("STUDENT OPPORTUNITIES ERROR")
        print(type(e).__name__)
        print(e)
        print("=" * 70)

        flash(
            "Unable to load opportunities.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# PHASE 4.2 - STUDENT OPPORTUNITY DETAILS
# =========================================================

@app.route("/student/opportunities/<opportunity_id>")
@student_required
def student_opportunity_detail(opportunity_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # GET ACTUAL STUDENT ID
        # -------------------------------------------------

        user_id = session.get("user_id")

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student_row = cursor.fetchone()

        if not student_row:
            return "Student profile not found.", 404

        student_id = student_row["id"]


        # -------------------------------------------------
        # GET STUDENT SKILLS
        # -------------------------------------------------

        cursor.execute("""
            SELECT skill_name, proficiency_level
            FROM student_skills
            WHERE student_id = %s
        """, (student_id,))

        student_skill_rows = cursor.fetchall()

        student_skills = {
            str(row["skill_name"]).strip().lower()
            for row in student_skill_rows
            if row.get("skill_name")
        }

        # -------------------------------------------------
        # GET OPPORTUNITY
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
                i.industry_sector

            FROM opportunities o

            JOIN industries i
                ON o.industry_id = i.id

            WHERE o.id = %s
              AND o.status = 'OPEN'
        """, (opportunity_id,))

        opportunity = cursor.fetchone()

        # -------------------------------------------------
        # OPPORTUNITY NOT FOUND
        # -------------------------------------------------

        if not opportunity:
            return "OPPORTUNITY NOT FOUND", 404
        # -------------------------------------------------
        # PARSE REQUIRED SKILLS
        # -------------------------------------------------

        required_skills = []

        raw_required_skills = opportunity.get("required_skills")

        if raw_required_skills:

            required_skills = [
                skill.strip()
                for skill in re.split(
                    r"[,;\n]+",
                    raw_required_skills
                )
                if skill.strip()
            ]

        # -------------------------------------------------
        # SKILL MATCH
        # -------------------------------------------------

        matched_skills = []
        missing_skills = []

        for required_skill in required_skills:

            required_lower = required_skill.lower()

            matched = False

            for student_skill in student_skills:

                if (
                    required_lower in student_skill
                    or student_skill in required_lower
                ):
                    matched = True
                    break

            if matched:
                matched_skills.append(required_skill)
            else:
                missing_skills.append(required_skill)

        # -------------------------------------------------
        # MATCH PERCENTAGE
        # -------------------------------------------------

        if required_skills:

            skill_match_percentage = round(
                (
                    len(matched_skills)
                    / len(required_skills)
                ) * 100,
                2
            )

        else:

            skill_match_percentage = 100.0

        # -------------------------------------------------
        # STUDENT BASIC ELIGIBILITY DATA
        # -------------------------------------------------

        cursor.execute("""
            SELECT 
                s.id AS student_id, 
                s.college_id, 
                s.course, 
                s.branch, 
                s.semester, 
                s.cgpa, 
                s.active_backlogs, 
                s.profile_completed, 
                s.resume_url, 

                u.name, 
                u.email 

            FROM students s 

            INNER JOIN users u 
                ON s.user_id = u.id 

            WHERE s.user_id = %s 

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "STUDENT PROFILE NOT FOUND FOR CURRENT USER", 404
        # -------------------------------------------------
        # ELIGIBILITY
        # -------------------------------------------------

        cgpa_ok = True
        backlog_ok = True
        skills_ok = True

        eligibility_text = (
            opportunity.get("eligibility_criteria")
            or ""
        )

        # -----------------------------------------------
        # CGPA CHECK
        # -----------------------------------------------

        cgpa_match = re.search(
            r"cgpa\s*(?:>=|>|:)?\s*(\d+(?:\.\d+)?)",
            eligibility_text,
            re.IGNORECASE
        )

        if cgpa_match:

            required_cgpa = float(
                cgpa_match.group(1)
            )

            student_cgpa = float(
                student.get("cgpa") or 0
            )

            cgpa_ok = student_cgpa >= required_cgpa

        # -----------------------------------------------
        # BACKLOG CHECK
        # -----------------------------------------------

        if re.search(
            r"no\s+backlog|no\s+active\s+backlog|zero\s+backlog",
            eligibility_text,
            re.IGNORECASE
        ):

            active_backlogs = int(
                student.get("active_backlogs") or 0
            )

            backlog_ok = active_backlogs == 0

        # -----------------------------------------------
        # SKILL CHECK
        # -----------------------------------------------

        if required_skills:

            skills_ok = len(matched_skills) > 0

        # -------------------------------------------------
        # FINAL ELIGIBILITY
        # -------------------------------------------------

        eligible = (
            cgpa_ok
            and backlog_ok
            and skills_ok
        )

        # -------------------------------------------------
        # DAYS LEFT
        # -------------------------------------------------

        days_left = None

        if opportunity.get("application_deadline"):

            from datetime import date

            deadline = opportunity[
                "application_deadline"
            ]

            days_left = (
                deadline - date.today()
            ).days

        # -------------------------------------------------
        # APPLICATION STATUS
        # -------------------------------------------------

        application_status = None

        cursor.execute("""
            SELECT status
            FROM student_applications
            WHERE student_id = %s
              AND opportunity_id = %s
            LIMIT 1
        """, (
            student_id,
            opportunity_id
        ))

        application = cursor.fetchone()

        if application:

            application_status = application.get(
                "status"
            )

        # -------------------------------------------------
        # ADD CALCULATED DATA
        # -------------------------------------------------

        opportunity[
            "required_skills_list"
        ] = required_skills

        opportunity[
            "matched_skills"
        ] = matched_skills

        opportunity[
            "missing_skills"
        ] = missing_skills

        opportunity[
            "skill_match_percentage"
        ] = skill_match_percentage

        opportunity[
            "cgpa_ok"
        ] = cgpa_ok

        opportunity[
            "backlog_ok"
        ] = backlog_ok

        opportunity[
            "skills_ok"
        ] = skills_ok

        opportunity[
            "eligible"
        ] = eligible

        opportunity[
            "days_left"
        ] = days_left

        opportunity[
            "application_status"
        ] = application_status

        # -------------------------------------------------
        # RENDER DETAILS PAGE
        # -------------------------------------------------

        return render_template(
            "student/opportunity_detail.html",
            opportunity=opportunity,
            student=student
        )

    except Exception as e:
        print("STUDENT OPPORTUNITY DETAIL ERROR:", repr(e))
        import traceback
        traceback.print_exc()
        return f"STUDENT OPPORTUNITY DETAIL ERROR: {e}", 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PHASE 4.3 - STUDENT APPLICATIONS
# =========================================================
# ---------------------------------------------------------
# APPLY FOR OPPORTUNITY
# ---------------------------------------------------------

@app.route(
    "/student/opportunities/<opportunity_id>/apply",
    methods=["POST"]
)
@student_required
def student_apply_opportunity(opportunity_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT USER
        # -------------------------------------------------

        user_id = session.get("user_id")


        # -------------------------------------------------
        # GET ACTUAL STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id AS student_id,
                s.course,
                s.branch,
                s.semester,
                s.cgpa,
                s.active_backlogs,
                s.resume_url,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found.", 404

        student_id = student["student_id"]


        # -------------------------------------------------
        # GET OPPORTUNITY
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                o.id,
                o.title,
                o.opportunity_type,
                o.application_deadline,
                o.status

            FROM opportunities o

            WHERE o.id = %s

            LIMIT 1
        """, (opportunity_id,))

        opportunity = cursor.fetchone()

        if not opportunity:
            return "Opportunity not found.", 404


        # -------------------------------------------------
        # STATUS CHECK
        # -------------------------------------------------

        if opportunity["status"] != "OPEN":

            return (
                "This opportunity is no longer open for applications.",
                400
            )


        # -------------------------------------------------
        # DEADLINE CHECK
        # -------------------------------------------------

        if opportunity["application_deadline"]:

            from datetime import date

            if opportunity["application_deadline"] < date.today():

                return (
                    "Application deadline has passed.",
                    400
                )


        # -------------------------------------------------
        # DUPLICATE APPLICATION CHECK
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                status

            FROM student_applications

            WHERE student_id = %s
              AND opportunity_id = %s

            LIMIT 1
        """, (
            student_id,
            opportunity_id
        ))

        existing_application = cursor.fetchone()


        if existing_application:

            return redirect(
                url_for(
                    "student_application_detail",
                    application_id=existing_application["id"]
                )
            )


        # -------------------------------------------------
        # RESUME
        # -------------------------------------------------

        resume_url = student.get("resume_url")


        # -------------------------------------------------
        # COVER LETTER
        # -------------------------------------------------

        cover_letter = request.form.get(
            "cover_letter",
            ""
        ).strip()


        # -------------------------------------------------
        # CREATE APPLICATION
        # -------------------------------------------------

        application_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO student_applications
            (
                id,
                student_id,
                opportunity_id,
                application_date,
                status,
                resume_url,
                cover_letter
            )

            VALUES
            (
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP,
                'APPLIED',
                %s,
                %s
            )
        """, (
            application_id,
            student_id,
            opportunity_id,
            resume_url,
            cover_letter
        ))


        connection.commit()


        # -------------------------------------------------
        # REDIRECT TO APPLICATION DETAIL
        # -------------------------------------------------

        return redirect(
            url_for(
                "student_application_detail",
                application_id=application_id
            )
        )


    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "STUDENT APPLY OPPORTUNITY ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return (
            f"STUDENT APPLY OPPORTUNITY ERROR: {e}",
            500
        )


    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# MY APPLICATIONS
# ---------------------------------------------------------

@app.route("/student/applications")
@student_required
def student_applications():

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session.get("user_id")

        cursor.execute("""
            SELECT s.id
            FROM students s
            WHERE s.user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        cursor.execute("""
            SELECT
                sa.id,
                sa.application_date,
                sa.status,
                sa.resume_url,
                sa.cover_letter,

                o.id AS opportunity_id,
                o.title,
                o.opportunity_type,
                o.location,
                o.work_mode,
                o.application_deadline,

                i.company_name,
                i.industry_sector

            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE sa.student_id = %s

            ORDER BY sa.application_date DESC
        """, (student_id,))

        applications = cursor.fetchall()

        return render_template(
            "student/applications.html",
            applications=applications
        )

    except Exception as e:

        print(
            "STUDENT APPLICATIONS ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return f"STUDENT APPLICATIONS ERROR: {e}", 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# APPLICATION DETAIL
# ---------------------------------------------------------

@app.route("/student/applications/<application_id>")
@student_required
def student_application_detail(application_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session.get("user_id")

        cursor.execute("""
            SELECT s.id
            FROM students s
            WHERE s.user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        cursor.execute("""
            SELECT
                sa.id,
                sa.application_date,
                sa.status,
                sa.resume_url,
                sa.cover_letter,
                sa.created_at,
                sa.updated_at,

                o.id AS opportunity_id,
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

                i.company_name,
                i.industry_sector

            FROM student_applications sa

            INNER JOIN opportunities o
                ON sa.opportunity_id = o.id

            INNER JOIN industries i
                ON o.industry_id = i.id

            WHERE sa.id = %s
              AND sa.student_id = %s

            LIMIT 1
        """, (
            application_id,
            student_id
        ))

        application = cursor.fetchone()

        if not application:
            return "Application not found", 404

        return render_template(
            "student/application_detail.html",
            application=application
        )

    except Exception as e:

        print(
            "STUDENT APPLICATION DETAIL ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return f"STUDENT APPLICATION DETAIL ERROR: {e}", 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ---------------------------------------------------------
# WITHDRAW APPLICATION
# ---------------------------------------------------------

@app.route(
    "/student/applications/<application_id>/withdraw",
    methods=["POST"]
)
@student_required
def student_withdraw_application(application_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session.get("user_id")

        cursor.execute("""
            SELECT s.id
            FROM students s
            WHERE s.user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        cursor.execute("""
            SELECT id, status
            FROM student_applications
            WHERE id = %s
              AND student_id = %s
            LIMIT 1
        """, (
            application_id,
            student_id
        ))

        application = cursor.fetchone()

        if not application:
            return "Application not found", 404

        # Only active APPLIED applications can be withdrawn

        if application["status"] != "APPLIED":

            return redirect(
                url_for(
                    "student_application_detail",
                    application_id=application_id
                )
            )

        cursor.execute("""
            UPDATE student_applications
            SET
                status = 'WITHDRAWN',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND student_id = %s
        """, (
            application_id,
            student_id
        ))

        connection.commit()

        return redirect(
            url_for(
                "student_application_detail",
                application_id=application_id
            )
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "STUDENT WITHDRAW APPLICATION ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return f"STUDENT WITHDRAW APPLICATION ERROR: {e}", 500

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PHASE 5.1 - STUDENT INTERNSHIPS
# =========================================================

@app.route("/student/internships")
@student_required
def student_internships():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT USER
        # -------------------------------------------------

        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("login"))

        # -------------------------------------------------
        # GET ACTUAL STUDENT ID
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found.", 404

        student_id = student["id"]

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        search = request.args.get(
            "search",
            ""
        ).strip()

        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        status_filter = request.args.get(
            "status",
            ""
        ).strip().upper()

        allowed_statuses = [
            "OFFERED",
            "ACCEPTED",
            "IN_PROGRESS",
            "COMPLETED",
            "TERMINATED"
        ]

        if status_filter not in allowed_statuses:
            status_filter = ""

        # -------------------------------------------------
        # BASE QUERY
        # -------------------------------------------------

        query = """
            SELECT

                ins.id,
                ins.application_id,
                ins.student_id,
                ins.opportunity_id,
                ins.industry_id,

                ins.start_date,
                ins.expected_end_date,
                ins.actual_end_date,

                ins.status,
                ins.progress_percentage,

                ins.created_at,
                ins.updated_at,

                o.title,
                o.opportunity_type,
                o.location,
                o.work_mode,

                i.company_name,
                i.company_type,
                i.industry_sector

            FROM internships ins

            INNER JOIN opportunities o
                ON ins.opportunity_id = o.id

            INNER JOIN industries i
                ON ins.industry_id = i.id

            WHERE ins.student_id = %s
        """

        params = [
            student_id
        ]

        # -------------------------------------------------
        # SEARCH FILTER
        # -------------------------------------------------

        if search:

            query += """
                AND (
                    o.title LIKE %s
                    OR i.company_name LIKE %s
                    OR i.industry_sector LIKE %s
                )
            """

            search_value = "%" + search + "%"

            params.extend([
                search_value,
                search_value,
                search_value
            ])

        # -------------------------------------------------
        # STATUS FILTER
        # -------------------------------------------------

        if status_filter:

            query += """
                AND ins.status = %s
            """

            params.append(
                status_filter
            )

        # -------------------------------------------------
        # ORDER
        # -------------------------------------------------

        query += """
            ORDER BY
                CASE
                    WHEN ins.status = 'IN_PROGRESS' THEN 1
                    WHEN ins.status = 'ACCEPTED' THEN 2
                    WHEN ins.status = 'OFFERED' THEN 3
                    WHEN ins.status = 'COMPLETED' THEN 4
                    ELSE 5
                END,
                ins.start_date DESC,
                ins.created_at DESC
        """

        cursor.execute(
            query,
            params
        )

        internships = cursor.fetchall()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COUNT(*) AS total,

                SUM(
                    status = 'OFFERED'
                ) AS offered_count,

                SUM(
                    status = 'ACCEPTED'
                ) AS accepted_count,

                SUM(
                    status = 'IN_PROGRESS'
                ) AS in_progress_count,

                SUM(
                    status = 'COMPLETED'
                ) AS completed_count,

                SUM(
                    status = 'TERMINATED'
                ) AS terminated_count

            FROM internships

            WHERE student_id = %s
        """, (
            student_id,
        ))

        stats = cursor.fetchone()

        # -------------------------------------------------
        # NORMALIZE NULL COUNTS
        # -------------------------------------------------

        stats = stats or {}

        total = stats.get("total") or 0
        offered = stats.get("offered_count") or 0
        accepted = stats.get("accepted_count") or 0
        in_progress = stats.get("in_progress_count") or 0
        completed = stats.get("completed_count") or 0
        terminated = stats.get("terminated_count") or 0

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------

        return render_template(
            "student/internships.html",

            internships=internships,

            total_internships=total,
            offered_internships=offered,
            accepted_internships=accepted,
            in_progress_internships=in_progress,
            completed_internships=completed,
            terminated_internships=terminated,

            search=search,
            status_filter=status_filter,

            active_page="internships"
        )

    except Exception as e:

        print(
            "STUDENT INTERNSHIPS ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return (
            f"STUDENT INTERNSHIPS ERROR: {e}",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# STUDENT INTERNSHIP DETAIL
# =========================================================

@app.route(
    "/student/internships/<internship_id>"
)
@student_required
def student_internship_detail(internship_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        user_id = session.get("user_id")

        # -------------------------------------------------
        # GET STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (
            user_id,
        ))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found.", 404

        student_id = student["id"]

        # -------------------------------------------------
        # GET INTERNSHIP
        # -------------------------------------------------

        cursor.execute("""
            SELECT

                ins.id,
                ins.application_id,
                ins.student_id,
                ins.opportunity_id,
                ins.industry_id,

                ins.start_date,
                ins.expected_end_date,
                ins.actual_end_date,

                ins.status,
                ins.progress_percentage,

                ins.created_at,
                ins.updated_at,

                o.title,
                o.opportunity_type,
                o.description,
                o.required_skills,
                o.location,
                o.work_mode,
                o.stipend,
                o.package,

                i.company_name,
                i.company_type,
                i.industry_sector,

                i.website

            FROM internships ins

            INNER JOIN opportunities o
                ON ins.opportunity_id = o.id

            INNER JOIN industries i
                ON ins.industry_id = i.id

            WHERE ins.id = %s
              AND ins.student_id = %s

            LIMIT 1
        """, (
            internship_id,
            student_id
        ))

        internship = cursor.fetchone()

        if not internship:
            return "Internship not found.", 404

        # -------------------------------------------------
        # PROGRESS RECORDS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                title,
                description,
                progress_percentage,
                progress_date,
                status,
                created_at

            FROM internship_progress

            WHERE internship_id = %s

            ORDER BY
                progress_date DESC,
                created_at DESC
        """, (
            internship_id,
        ))

        progress_records = cursor.fetchall()

        # -------------------------------------------------
        # MENTORS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                mentor_name,
                mentor_email,
                mentor_phone,
                designation,
                assigned_at

            FROM internship_mentors

            WHERE internship_id = %s

            ORDER BY assigned_at DESC
        """, (
            internship_id,
        ))

        mentors = cursor.fetchall()

        # -------------------------------------------------
        # FEEDBACK
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                f.id,
                f.rating,
                f.feedback,
                f.technical_skills_rating,
                f.communication_rating,
                f.teamwork_rating,
                f.professionalism_rating,
                f.created_at,

                u.name AS submitted_by_name,
                u.email AS submitted_by_email

            FROM internship_feedback f

            INNER JOIN users u
                ON f.submitted_by = u.id

            WHERE f.internship_id = %s

            ORDER BY f.created_at DESC
        """, (
            internship_id,
        ))

        feedback = cursor.fetchall()

        # -------------------------------------------------
        # COMPLETION
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                id,
                completion_date,
                certificate_url,
                final_rating,
                remarks,
                created_at

            FROM internship_completions

            WHERE internship_id = %s

            LIMIT 1
        """, (
            internship_id,
        ))

        completion = cursor.fetchone()

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------

        return render_template(
            "student/internship_detail.html",

            internship=internship,
            progress_records=progress_records,
            mentors=mentors,
            feedback=feedback,
            completion=completion,

            active_page="internships"
        )

    except Exception as e:

        print(
            "STUDENT INTERNSHIP DETAIL ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return (
            f"STUDENT INTERNSHIP DETAIL ERROR: {e}",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PHASE 5.3 - STUDENT INTERNSHIP PROGRESS
# =========================================================

@app.route(
    "/student/internships/<internship_id>/progress",
    methods=["GET", "POST"]
)
@student_required
def student_internship_progress(internship_id):

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # CURRENT USER
        # -------------------------------------------------

        user_id = session.get("user_id")

        if not user_id:
            return "Unauthorized", 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # FIND STUDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
            """,
            (user_id,)
        )

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # VERIFY INTERNSHIP OWNERSHIP
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                i.id,
                i.student_id,
                i.start_date,
                i.expected_end_date,
                i.actual_end_date,
                i.status,
                i.progress_percentage,
                o.title AS opportunity_title,
                ind.name AS industry_name
            FROM internships i
            JOIN opportunities o
                ON i.opportunity_id = o.id
            JOIN industries ind
                ON i.industry_id = ind.id
            WHERE i.id = %s
              AND i.student_id = %s
            LIMIT 1
            """,
            (internship_id, student_id)
        )

        internship = cursor.fetchone()

        if not internship:
            return "Internship not found", 404

        # -------------------------------------------------
        # POST - ADD PROGRESS UPDATE
        # -------------------------------------------------

        if request.method == "POST":

            title = request.form.get(
                "title",
                ""
            ).strip()

            description = request.form.get(
                "description",
                ""
            ).strip()

            progress_percentage = request.form.get(
                "progress_percentage",
                "0"
            ).strip()

            progress_date = request.form.get(
                "progress_date",
                ""
            ).strip()

            status = request.form.get(
                "status",
                "IN_PROGRESS"
            ).strip().upper()

            # ---------------------------------------------
            # VALIDATE TITLE
            # ---------------------------------------------

            if not title:

                flash(
                    "Progress title is required.",
                    "error"
                )

                return redirect(
                    url_for(
                        "student_internship_progress",
                        internship_id=internship_id
                    )
                )

            # ---------------------------------------------
            # VALIDATE PROGRESS PERCENTAGE
            # ---------------------------------------------

            try:

                progress_percentage = float(
                    progress_percentage
                )

            except (ValueError, TypeError):

                flash(
                    "Progress percentage must be a valid number.",
                    "error"
                )

                return redirect(
                    url_for(
                        "student_internship_progress",
                        internship_id=internship_id
                    )
                )

            if progress_percentage < 0:

                progress_percentage = 0

            if progress_percentage > 100:

                progress_percentage = 100

            # ---------------------------------------------
            # VALIDATE DATE
            # ---------------------------------------------

            if not progress_date:

                flash(
                    "Progress date is required.",
                    "error"
                )

                return redirect(
                    url_for(
                        "student_internship_progress",
                        internship_id=internship_id
                    )
                )

            # ---------------------------------------------
            # VALIDATE STATUS
            # ---------------------------------------------

            allowed_statuses = [
                "PENDING",
                "IN_PROGRESS",
                "COMPLETED"
            ]

            if status not in allowed_statuses:

                status = "IN_PROGRESS"

            # ---------------------------------------------
            # AUTO COMPLETE AT 100%
            # ---------------------------------------------

            if progress_percentage >= 100:

                progress_percentage = 100
                status = "COMPLETED"

            # ---------------------------------------------
            # CREATE PROGRESS ID
            # ---------------------------------------------

            progress_id = str(uuid.uuid4())

            # ---------------------------------------------
            # INSERT PROGRESS
            # ---------------------------------------------

            cursor.execute(
                """
                INSERT INTO internship_progress
                (
                    id,
                    internship_id,
                    title,
                    description,
                    progress_percentage,
                    progress_date,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    progress_id,
                    internship_id,
                    title,
                    description if description else None,
                    progress_percentage,
                    progress_date,
                    status
                )
            )

            # ---------------------------------------------
            # UPDATE OVERALL INTERNSHIP PROGRESS
            # ---------------------------------------------

            cursor.execute(
                """
                UPDATE internships
                SET
                    progress_percentage = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                  AND student_id = %s
                """,
                (
                    progress_percentage,
                    internship_id,
                    student_id
                )
            )

            # ---------------------------------------------
            # COMMIT
            # ---------------------------------------------

            connection.commit()

            flash(
                "Internship progress updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "student_internship_progress",
                    internship_id=internship_id
                )
            )

        # -------------------------------------------------
        # GET - PROGRESS HISTORY
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                title,
                description,
                progress_percentage,
                progress_date,
                status,
                created_at
            FROM internship_progress
            WHERE internship_id = %s
            ORDER BY
                progress_date DESC,
                created_at DESC
            """,
            (internship_id,)
        )

        progress_updates = cursor.fetchall()

        # -------------------------------------------------
        # RENDER PAGE
        # -------------------------------------------------

        return render_template(
            "student/internship_progress.html",
            internship=internship,
            progress_updates=progress_updates
        )

    except Exception as e:

        if connection:

            connection.rollback()

        print(
            "STUDENT INTERNSHIP PROGRESS ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return (
            f"STUDENT INTERNSHIP PROGRESS ERROR: {e}",
            500
        )

    finally:

        if cursor:

            cursor.close()

        if connection:

            connection.close()


# =========================================================
# PHASE 5.4 - STUDENT MENTOR FEEDBACK
# =========================================================

@app.route("/student/internships/<internship_id>/mentor-feedback")
@student_required
def student_mentor_feedback(internship_id):

    connection = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            return "Unauthorized", 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # FIND STUDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
            """,
            (user_id,)
        )

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # VERIFY INTERNSHIP
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                i.id,
                i.student_id,
                i.start_date,
                i.expected_end_date,
                i.actual_end_date,
                i.status,
                i.progress_percentage,
                o.title AS opportunity_title,
                ind.name AS industry_name
            FROM internships i
            JOIN opportunities o
                ON i.opportunity_id = o.id
            JOIN industries ind
                ON i.industry_id = ind.id
            WHERE i.id = %s
              AND i.student_id = %s
            LIMIT 1
            """,
            (internship_id, student_id)
        )

        internship = cursor.fetchone()

        if not internship:
            return "Internship not found", 404

        # -------------------------------------------------
        # MENTOR DETAILS
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                mentor_name,
                mentor_email,
                mentor_phone,
                designation,
                assigned_at
            FROM internship_mentors
            WHERE internship_id = %s
            ORDER BY assigned_at DESC
            """,
            (internship_id,)
        )

        mentors = cursor.fetchall()

        # -------------------------------------------------
        # FEEDBACK
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                f.id,
                f.rating,
                f.feedback,
                f.technical_skills_rating,
                f.communication_rating,
                f.teamwork_rating,
                f.professionalism_rating,
                f.created_at,
                u.full_name AS submitted_by_name,
                u.role AS submitted_by_role
            FROM internship_feedback f
            LEFT JOIN users u
                ON f.submitted_by = u.id
            WHERE f.internship_id = %s
            ORDER BY f.created_at DESC
            """,
            (internship_id,)
        )

        feedback_list = cursor.fetchall()

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------

        return render_template(
            "student/mentor_feedback.html",
            internship=internship,
            mentors=mentors,
            feedback_list=feedback_list
        )

    except Exception as e:

        print(
            "STUDENT MENTOR FEEDBACK ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return (
            f"STUDENT MENTOR FEEDBACK ERROR: {e}",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PHASE 5.5 - STUDENT INTERNSHIP COMPLETION
# =========================================================

@app.route("/student/internships/<internship_id>/completion")
@student_required
def student_internship_completion(internship_id):

    connection = None
    cursor = None

    try:

        # -------------------------------------------------
        # CURRENT USER
        # -------------------------------------------------

        user_id = session.get("user_id")

        if not user_id:
            return "Unauthorized", 401

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # FIND STUDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
            """,
            (user_id,)
        )

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # VERIFY INTERNSHIP
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                i.id,
                i.student_id,
                i.start_date,
                i.expected_end_date,
                i.actual_end_date,
                i.status,
                i.progress_percentage,
                o.title AS opportunity_title,
                ind.name AS industry_name
            FROM internships i
            JOIN opportunities o
                ON i.opportunity_id = o.id
            JOIN industries ind
                ON i.industry_id = ind.id
            WHERE i.id = %s
              AND i.student_id = %s
            LIMIT 1
            """,
            (internship_id, student_id)
        )

        internship = cursor.fetchone()

        if not internship:
            return "Internship not found", 404

        # -------------------------------------------------
        # COMPLETION RECORD
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                internship_id,
                completion_date,
                certificate_url,
                final_rating,
                remarks,
                created_at
            FROM internship_completions
            WHERE internship_id = %s
            LIMIT 1
            """,
            (internship_id,)
        )

        completion = cursor.fetchone()

        # -------------------------------------------------
        # FEEDBACK SUMMARY
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                AVG(rating) AS average_rating,
                AVG(technical_skills_rating)
                    AS technical_rating,
                AVG(communication_rating)
                    AS communication_rating,
                AVG(teamwork_rating)
                    AS teamwork_rating,
                AVG(professionalism_rating)
                    AS professionalism_rating
            FROM internship_feedback
            WHERE internship_id = %s
            """,
            (internship_id,)
        )

        feedback_summary = cursor.fetchone()

        # -------------------------------------------------
        # RENDER
        # -------------------------------------------------

        return render_template(
            "student/internship_completion.html",
            internship=internship,
            completion=completion,
            feedback_summary=feedback_summary
        )

    except Exception as e:

        print(
            "STUDENT INTERNSHIP COMPLETION ERROR:",
            repr(e)
        )

        import traceback
        traceback.print_exc()

        return (
            f"STUDENT INTERNSHIP COMPLETION ERROR: {e}",
            500
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# PHASE 6.1 - STUDENT WORKSHOPS
# =========================================================

@app.route("/student/workshops")
@student_required
def student_workshops():

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get actual student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Get workshops + student's registration status
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                w.id,
                w.title,
                w.description,
                w.topic,
                w.start_date,
                w.end_date,
                w.mode,
                w.registration_deadline,
                w.status,
                w.created_at,

                swr.id AS registration_id,
                swr.attendance_status,
                swr.registration_date,
                swr.attended_at,
                swr.completed_at

            FROM workshops w

            LEFT JOIN student_workshop_registrations swr
                ON swr.workshop_id = w.id
                AND swr.student_id = %s

            WHERE w.status IN ('OPEN', 'ONGOING', 'COMPLETED')

            ORDER BY
                CASE
                    WHEN w.status = 'OPEN' THEN 1
                    WHEN w.status = 'ONGOING' THEN 2
                    ELSE 3
                END,
                w.start_date ASC
        """, (student_id,))

        workshops = cursor.fetchall()

        # -------------------------------------------------
        # Stats
        # -------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS total_registered
            FROM student_workshop_registrations
            WHERE student_id = %s
        """, (student_id,))

        total_registered = cursor.fetchone()["total_registered"]

        cursor.execute("""
            SELECT COUNT(*) AS total_attended
            FROM student_workshop_registrations
            WHERE student_id = %s
              AND attendance_status IN ('ATTENDED', 'COMPLETED')
        """, (student_id,))

        total_attended = cursor.fetchone()["total_attended"]

        cursor.execute("""
            SELECT COUNT(*) AS total_completed
            FROM student_workshop_registrations
            WHERE student_id = %s
              AND attendance_status = 'COMPLETED'
        """, (student_id,))

        total_completed = cursor.fetchone()["total_completed"]

        return render_template(
            "student/workshops.html",
            workshops=workshops,
            total_registered=total_registered,
            total_attended=total_attended,
            total_completed=total_completed,
            active_page="workshops"
        )

    finally:
        cursor.close()
        conn.close()


# =========================================================
# REGISTER FOR WORKSHOP
# =========================================================

@app.route(
    "/student/workshops/<workshop_id>/register",
    methods=["POST"]
)
@student_required
def student_register_workshop(workshop_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Check workshop
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                title,
                status,
                registration_deadline
            FROM workshops
            WHERE id = %s
            LIMIT 1
        """, (workshop_id,))

        workshop = cursor.fetchone()

        if not workshop:
            return "Workshop not found", 404

        if workshop["status"] not in ("OPEN", "ONGOING"):
            return "Workshop registration is not available", 400

        # -------------------------------------------------
        # Check deadline
        # -------------------------------------------------
        if workshop["registration_deadline"]:
            today = datetime.now().date()

            if workshop["registration_deadline"] < today:
                return "Workshop registration deadline has passed", 400

        # -------------------------------------------------
        # Check existing registration
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM student_workshop_registrations
            WHERE workshop_id = %s
              AND student_id = %s
            LIMIT 1
        """, (workshop_id, student_id))

        existing = cursor.fetchone()

        if existing:
            return redirect(url_for("student_workshops"))

        # -------------------------------------------------
        # Register student
        # -------------------------------------------------
        registration_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO student_workshop_registrations
            (
                id,
                workshop_id,
                student_id,
                attendance_status
            )
            VALUES (%s, %s, %s, 'REGISTERED')
        """, (
            registration_id,
            workshop_id,
            student_id
        ))

        conn.commit()

        return redirect(url_for("student_workshops"))

    except Exception as e:
        conn.rollback()
        print("Workshop registration error:", e)
        return "Unable to register for workshop", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# MARK WORKSHOP ATTENDANCE
# =========================================================

@app.route(
    "/student/workshops/<workshop_id>/attend",
    methods=["POST"]
)
@student_required
def student_attend_workshop(workshop_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        cursor.execute("""
            SELECT id, attendance_status
            FROM student_workshop_registrations
            WHERE workshop_id = %s
              AND student_id = %s
            LIMIT 1
        """, (workshop_id, student_id))

        registration = cursor.fetchone()

        if not registration:
            return "You are not registered for this workshop", 400

        if registration["attendance_status"] == "COMPLETED":
            return redirect(url_for("student_workshops"))

        cursor.execute("""
            UPDATE student_workshop_registrations
            SET
                attendance_status = 'ATTENDED',
                attended_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (registration["id"],))

        conn.commit()

        return redirect(url_for("student_workshops"))

    except Exception as e:
        conn.rollback()
        print("Workshop attendance error:", e)
        return "Unable to mark attendance", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# COMPLETE WORKSHOP
# =========================================================

@app.route(
    "/student/workshops/<workshop_id>/complete",
    methods=["POST"]
)
@student_required
def student_complete_workshop(workshop_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Get registration
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                swr.id,
                swr.attendance_status,
                w.title
            FROM student_workshop_registrations swr

            INNER JOIN workshops w
                ON w.id = swr.workshop_id

            WHERE swr.workshop_id = %s
              AND swr.student_id = %s

            LIMIT 1
        """, (workshop_id, student_id))

        registration = cursor.fetchone()

        if not registration:
            return "You are not registered for this workshop", 400

        if registration["attendance_status"] not in (
            "ATTENDED",
            "COMPLETED"
        ):
            return "Workshop must be attended before completion", 400

        # -------------------------------------------------
        # Mark completed
        # -------------------------------------------------
        cursor.execute("""
            UPDATE student_workshop_registrations
            SET
                attendance_status = 'COMPLETED',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (registration["id"],))

        # -------------------------------------------------
        # Achievement check
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM student_achievements
            WHERE student_id = %s
              AND title = %s
            LIMIT 1
        """, (
            student_id,
            registration["title"]
        ))

        achievement = cursor.fetchone()

        # -------------------------------------------------
        # Create achievement automatically
        # -------------------------------------------------
        if not achievement:

            achievement_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO student_achievements
                (
                    id,
                    student_id,
                    title,
                    description,
                    achievement_type,
                    achievement_date,
                    issuing_organization
                )
                SELECT
                    %s,
                    %s,
                    w.title,
                    CONCAT(
                        'Successfully completed workshop: ',
                        w.title
                    ),
                    'WORKSHOP',
                    COALESCE(w.end_date, CURDATE()),
                    'SIH Academia–Industry Collaboration Portal'
                FROM workshops w
                WHERE w.id = %s
            """, (
                achievement_id,
                student_id,
                workshop_id
            ))

        conn.commit()

        return redirect(url_for("student_workshops"))

    except Exception as e:
        conn.rollback()
        print("Workshop completion error:", e)
        return "Unable to complete workshop", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# PHASE 6.2 - STUDENT MENTORSHIP
# =========================================================

@app.route("/student/mentorship")
@student_required
def student_mentorship():

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get actual student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Available mentors
        # users.name is the actual column
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                u.id,
                u.name,
                u.email,
                u.profile_image,

                m.id AS mentorship_id,
                m.title AS mentorship_title,
                m.goals,
                m.start_date,
                m.end_date,
                m.status AS mentorship_status,
                m.created_at AS mentorship_created_at

            FROM users u

            LEFT JOIN mentorships m
                ON m.mentor_user_id = u.id
                AND m.student_id = %s
                AND m.status IN ('REQUESTED', 'ACTIVE')

            WHERE u.role = 'MENTOR'
              AND u.status = 'ACTIVE'

            ORDER BY u.name ASC
        """, (student_id,))

        mentors = cursor.fetchall()

        # -------------------------------------------------
        # My mentorships
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                m.id,
                m.title,
                m.goals,
                m.start_date,
                m.end_date,
                m.status,
                m.created_at,

                u.name AS mentor_name,
                u.email AS mentor_email,
                u.profile_image AS mentor_profile_image

            FROM mentorships m

            INNER JOIN users u
                ON u.id = m.mentor_user_id

            WHERE m.student_id = %s

            ORDER BY m.created_at DESC
        """, (student_id,))

        my_mentorships = cursor.fetchall()

        # -------------------------------------------------
        # Stats
        # -------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM mentorships
            WHERE student_id = %s
        """, (student_id,))

        total_requests = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM mentorships
            WHERE student_id = %s
              AND status = 'REQUESTED'
        """, (student_id,))

        pending_requests = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM mentorships
            WHERE student_id = %s
              AND status = 'ACTIVE'
        """, (student_id,))

        active_mentorships = cursor.fetchone()["total"]

        return render_template(
            "student/mentorship.html",
            mentors=mentors,
            my_mentorships=my_mentorships,
            total_requests=total_requests,
            pending_requests=pending_requests,
            active_mentorships=active_mentorships,
            active_page="mentorship"
        )

    finally:
        cursor.close()
        conn.close()


# =========================================================
# REQUEST MENTORSHIP
# =========================================================

@app.route(
    "/student/mentorship/<mentor_user_id>/request",
    methods=["POST"]
)
@student_required
def student_request_mentorship(mentor_user_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Verify mentor
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                name,
                email
            FROM users
            WHERE id = %s
              AND role = 'MENTOR'
              AND status = 'ACTIVE'
            LIMIT 1
        """, (mentor_user_id,))

        mentor = cursor.fetchone()

        if not mentor:
            return "Mentor not found", 404

        # -------------------------------------------------
        # Prevent duplicate active/requested mentorship
        # -------------------------------------------------
        cursor.execute("""
            SELECT id, status
            FROM mentorships
            WHERE student_id = %s
              AND mentor_user_id = %s
              AND status IN ('REQUESTED', 'ACTIVE')
            LIMIT 1
        """, (student_id, mentor_user_id))

        existing = cursor.fetchone()

        if existing:
            return redirect(url_for("student_mentorship"))

        # -------------------------------------------------
        # Optional form data
        # -------------------------------------------------
        title = request.form.get(
            "title",
            "Student Mentorship Request"
        ).strip()

        goals = request.form.get(
            "goals",
            ""
        ).strip()

        if not title:
            title = "Student Mentorship Request"

        # -------------------------------------------------
        # Create request
        # -------------------------------------------------
        mentorship_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO mentorships
            (
                id,
                student_id,
                mentor_user_id,
                title,
                goals,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                'REQUESTED'
            )
        """, (
            mentorship_id,
            student_id,
            mentor_user_id,
            title,
            goals
        ))

        conn.commit()

        return redirect(url_for("student_mentorship"))

    except Exception as e:
        conn.rollback()
        print("Mentorship request error:", e)
        return "Unable to send mentorship request", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# PHASE 6.3 - STUDENT LIVE PROJECTS
# =========================================================

@app.route("/student/live-projects")
@student_required
def student_live_projects():

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get actual student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Live projects + student's participation
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                lp.id,
                lp.title,
                lp.description,
                lp.technology_stack,
                lp.start_date,
                lp.end_date,
                lp.application_deadline,
                lp.status,
                lp.project_url,
                lp.created_at,

                u.name AS organizer_name,
                u.email AS organizer_email,

                slp.id AS participation_id,
                slp.status AS participation_status,
                slp.applied_at,
                slp.started_at,
                slp.completed_at

            FROM live_projects lp

            INNER JOIN users u
                ON u.id = lp.organizer_user_id

            LEFT JOIN student_live_projects slp
                ON slp.live_project_id = lp.id
                AND slp.student_id = %s

            WHERE lp.status IN (
                'OPEN',
                'ONGOING',
                'COMPLETED'
            )

            ORDER BY
                CASE
                    WHEN lp.status = 'OPEN' THEN 1
                    WHEN lp.status = 'ONGOING' THEN 2
                    ELSE 3
                END,
                lp.start_date ASC
        """, (student_id,))

        live_projects = cursor.fetchall()

        # -------------------------------------------------
        # My project count
        # -------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_live_projects
            WHERE student_id = %s
        """, (student_id,))

        total_projects = cursor.fetchone()["total"]

        # -------------------------------------------------
        # Selected / active
        # -------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_live_projects
            WHERE student_id = %s
              AND status IN ('SELECTED', 'IN_PROGRESS')
        """, (student_id,))

        active_projects = cursor.fetchone()["total"]

        # -------------------------------------------------
        # Completed
        # -------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM student_live_projects
            WHERE student_id = %s
              AND status = 'COMPLETED'
        """, (student_id,))

        completed_projects = cursor.fetchone()["total"]

        return render_template(
            "student/live_projects.html",
            live_projects=live_projects,
            total_projects=total_projects,
            active_projects=active_projects,
            completed_projects=completed_projects,
            active_page="live-projects"
        )

    finally:
        cursor.close()
        conn.close()


# =========================================================
# APPLY FOR LIVE PROJECT
# =========================================================

@app.route(
    "/student/live-projects/<project_id>/apply",
    methods=["POST"]
)
@student_required
def student_apply_live_project(project_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Verify project
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                title,
                status,
                application_deadline
            FROM live_projects
            WHERE id = %s
            LIMIT 1
        """, (project_id,))

        project = cursor.fetchone()

        if not project:
            return "Live project not found", 404

        if project["status"] != "OPEN":
            return "Applications are not open for this project", 400

        # -------------------------------------------------
        # Deadline
        # -------------------------------------------------
        if project["application_deadline"]:

            if project["application_deadline"] < datetime.now().date():
                return "Application deadline has passed", 400

        # -------------------------------------------------
        # Duplicate application
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM student_live_projects
            WHERE live_project_id = %s
              AND student_id = %s
            LIMIT 1
        """, (project_id, student_id))

        existing = cursor.fetchone()

        if existing:
            return redirect(
                url_for("student_live_projects")
            )

        # -------------------------------------------------
        # Apply
        # -------------------------------------------------
        participation_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO student_live_projects
            (
                id,
                live_project_id,
                student_id,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                'APPLIED'
            )
        """, (
            participation_id,
            project_id,
            student_id
        ))

        conn.commit()

        return redirect(
            url_for("student_live_projects")
        )

    except Exception as e:
        conn.rollback()
        print("Live project application error:", e)
        return "Unable to apply for live project", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# START LIVE PROJECT
# =========================================================

@app.route(
    "/student/live-projects/<project_id>/start",
    methods=["POST"]
)
@student_required
def student_start_live_project(project_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        cursor.execute("""
            SELECT id, status
            FROM student_live_projects
            WHERE live_project_id = %s
              AND student_id = %s
            LIMIT 1
        """, (project_id, student_id))

        participation = cursor.fetchone()

        if not participation:
            return "Project participation not found", 404

        if participation["status"] != "SELECTED":
            return "Project must be selected before starting", 400

        cursor.execute("""
            UPDATE student_live_projects
            SET
                status = 'IN_PROGRESS',
                started_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (participation["id"],))

        conn.commit()

        return redirect(
            url_for("student_live_projects")
        )

    except Exception as e:
        conn.rollback()
        print("Live project start error:", e)
        return "Unable to start live project", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# COMPLETE LIVE PROJECT
# =========================================================

@app.route(
    "/student/live-projects/<project_id>/complete",
    methods=["POST"]
)
@student_required
def student_complete_live_project(project_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Participation
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                slp.id,
                slp.status,
                lp.title
            FROM student_live_projects slp

            INNER JOIN live_projects lp
                ON lp.id = slp.live_project_id

            WHERE slp.live_project_id = %s
              AND slp.student_id = %s

            LIMIT 1
        """, (project_id, student_id))

        participation = cursor.fetchone()

        if not participation:
            return "Project participation not found", 404

        if participation["status"] != "IN_PROGRESS":
            return "Project must be in progress before completion", 400

        # -------------------------------------------------
        # Complete participation
        # -------------------------------------------------
        cursor.execute("""
            UPDATE student_live_projects
            SET
                status = 'COMPLETED',
                completed_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (participation["id"],))

        # -------------------------------------------------
        # Achievement check
        # -------------------------------------------------
        achievement_title = (
            "Live Project: " + participation["title"]
        )

        cursor.execute("""
            SELECT id
            FROM student_achievements
            WHERE student_id = %s
              AND title = %s
            LIMIT 1
        """, (
            student_id,
            achievement_title
        ))

        achievement = cursor.fetchone()

        # -------------------------------------------------
        # Add achievement
        # -------------------------------------------------
        if not achievement:

            achievement_id = str(uuid.uuid4())

            cursor.execute("""
                INSERT INTO student_achievements
                (
                    id,
                    student_id,
                    title,
                    description,
                    achievement_type,
                    achievement_date,
                    issuing_organization
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    CURDATE(),
                    %s
                )
            """, (
                achievement_id,
                student_id,
                achievement_title,
                "Successfully completed the live project: "
                + participation["title"],
                "LIVE_PROJECT",
                "SIH Academia–Industry Collaboration Portal"
            ))

        conn.commit()

        return redirect(
            url_for("student_live_projects")
        )

    except Exception as e:
        conn.rollback()
        print("Live project completion error:", e)
        return "Unable to complete live project", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# PHASE 6.4 - STUDENT INNOVATION CHALLENGES
# =========================================================

@app.route("/student/innovation-challenges")
@student_required
def student_innovation_challenges():

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get actual student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Get challenges
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                ic.id,
                ic.title,
                ic.description,
                ic.organizer_user_id,
                ic.registration_deadline,
                ic.start_date,
                ic.end_date,
                ic.status,
                ic.created_at,

                u.name AS organizer_name,
                u.email AS organizer_email,

                icp.id AS participant_id,
                icp.team_name,
                icp.submission_url,
                icp.status AS participation_status,
                icp.created_at AS participation_created_at

            FROM innovation_challenges ic

            LEFT JOIN users u
                ON u.id = ic.organizer_user_id

            LEFT JOIN innovation_challenge_participants icp
                ON icp.challenge_id = ic.id
                AND icp.student_id = %s

            WHERE ic.status IN (
                'OPEN',
                'CLOSED',
                'COMPLETED'
            )

            ORDER BY
                CASE
                    WHEN ic.status = 'OPEN' THEN 1
                    WHEN ic.status = 'CLOSED' THEN 2
                    ELSE 3
                END,
                ic.start_date ASC
        """, (student_id,))

        challenges = cursor.fetchall()

        # -------------------------------------------------
        # Statistics
        # -------------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM innovation_challenge_participants
            WHERE student_id = %s
        """, (student_id,))

        total_participations = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM innovation_challenge_participants
            WHERE student_id = %s
              AND status IN ('SUBMITTED', 'SHORTLISTED')
        """, (student_id,))

        submitted_count = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM innovation_challenge_participants
            WHERE student_id = %s
              AND status = 'WINNER'
        """, (student_id,))

        winner_count = cursor.fetchone()["total"]

        return render_template(
            "student/innovation_challenges.html",
            challenges=challenges,
            total_participations=total_participations,
            submitted_count=submitted_count,
            winner_count=winner_count,
            active_page="innovation-challenges"
        )

    finally:
        cursor.close()
        conn.close()


# =========================================================
# REGISTER FOR INNOVATION CHALLENGE
# =========================================================

@app.route(
    "/student/innovation-challenges/<challenge_id>/register",
    methods=["POST"]
)
@student_required
def student_register_innovation_challenge(challenge_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Verify challenge
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                id,
                title,
                status,
                registration_deadline
            FROM innovation_challenges
            WHERE id = %s
            LIMIT 1
        """, (challenge_id,))

        challenge = cursor.fetchone()

        if not challenge:
            return "Innovation challenge not found", 404

        if challenge["status"] != "OPEN":
            return "Registration is not open for this challenge", 400

        # -------------------------------------------------
        # Check deadline using MySQL date
        # -------------------------------------------------
        if challenge["registration_deadline"]:

            cursor.execute("""
                SELECT
                    CASE
                        WHEN %s < CURDATE()
                        THEN 1
                        ELSE 0
                    END AS expired
            """, (challenge["registration_deadline"],))

            deadline_check = cursor.fetchone()

            if deadline_check["expired"] == 1:
                return "Registration deadline has passed", 400

        # -------------------------------------------------
        # Prevent duplicate registration
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM innovation_challenge_participants
            WHERE challenge_id = %s
              AND student_id = %s
            LIMIT 1
        """, (challenge_id, student_id))

        existing = cursor.fetchone()

        if existing:
            return redirect(
                url_for("student_innovation_challenges")
            )

        # -------------------------------------------------
        # Team name
        # -------------------------------------------------
        team_name = request.form.get(
            "team_name",
            ""
        ).strip()

        if not team_name:
            team_name = "Individual Participant"

        # -------------------------------------------------
        # Register
        # -------------------------------------------------
        participant_id = str(uuid.uuid4())

        cursor.execute("""
            INSERT INTO innovation_challenge_participants
            (
                id,
                challenge_id,
                student_id,
                team_name,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'REGISTERED'
            )
        """, (
            participant_id,
            challenge_id,
            student_id,
            team_name
        ))

        conn.commit()

        return redirect(
            url_for("student_innovation_challenges")
        )

    except Exception as e:
        conn.rollback()
        print("Innovation challenge registration error:", e)
        return "Unable to register for challenge", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# SUBMIT INNOVATION CHALLENGE
# =========================================================

@app.route(
    "/student/innovation-challenges/<challenge_id>/submit",
    methods=["POST"]
)
@student_required
def student_submit_innovation_challenge(challenge_id):

    user_id = session.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # -------------------------------------------------
        # Get student
        # -------------------------------------------------
        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:
            return "Student profile not found", 404

        student_id = student["id"]

        # -------------------------------------------------
        # Verify participant
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                icp.id,
                icp.status,
                ic.status AS challenge_status
            FROM innovation_challenge_participants icp

            INNER JOIN innovation_challenges ic
                ON ic.id = icp.challenge_id

            WHERE icp.challenge_id = %s
              AND icp.student_id = %s

            LIMIT 1
        """, (challenge_id, student_id))

        participant = cursor.fetchone()

        if not participant:
            return "You are not registered for this challenge", 404

        if participant["status"] not in (
            "REGISTERED",
            "SUBMITTED"
        ):
            return "Submission is not available for your current status", 400

        # -------------------------------------------------
        # Submission URL
        # -------------------------------------------------
        submission_url = request.form.get(
            "submission_url",
            ""
        ).strip()

        if not submission_url:
            return "Submission URL is required", 400

        # -------------------------------------------------
        # Save submission
        # -------------------------------------------------
        cursor.execute("""
            UPDATE innovation_challenge_participants
            SET
                submission_url = %s,
                status = 'SUBMITTED'
            WHERE id = %s
        """, (
            submission_url,
            participant["id"]
        ))

        conn.commit()

        return redirect(
            url_for("student_innovation_challenges")
        )

    except Exception as e:
        conn.rollback()
        print("Innovation challenge submission error:", e)
        return "Unable to submit challenge solution", 500

    finally:
        cursor.close()
        conn.close()


# =========================================================
# STUDENT NOTIFICATIONS
# =========================================================

@app.route("/student/notifications", methods=["GET"])
@student_required
def student_notifications():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.user_id,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(url_for("login"))

        # -------------------------------------------------
        # SEARCH + FILTER
        # -------------------------------------------------

        search = request.args.get(
            "search",
            ""
        ).strip()

        selected_type = request.args.get(
            "type",
            ""
        ).strip()

        # -------------------------------------------------
        # NOTIFICATION TYPES
        # -------------------------------------------------

        cursor.execute("""
            SELECT DISTINCT
                notification_type

            FROM notifications

            WHERE user_id = %s

              AND notification_type IS NOT NULL

              AND notification_type <> ''

            ORDER BY notification_type
        """, (user_id,))

        notification_types = cursor.fetchall()

        # -------------------------------------------------
        # NOTIFICATIONS
        # -------------------------------------------------

        query = """
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
        """

        params = [user_id]

        # SEARCH
        if search:

            query += """
                AND (
                    title LIKE %s
                    OR message LIKE %s
                    OR notification_type LIKE %s
                )
            """

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
                search_value
            ])

        # TYPE FILTER
        if selected_type:

            query += """
                AND notification_type = %s
            """

            params.append(selected_type)

        # LATEST FIRST
        query += """
            ORDER BY created_at DESC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        notifications = cursor.fetchall()

        # -------------------------------------------------
        # NOTIFICATION STATISTICS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COUNT(*) AS total,

                COALESCE(
                    SUM(
                        CASE
                            WHEN is_read = 0
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS unread,

                COALESCE(
                    SUM(
                        CASE
                            WHEN is_read = 1
                            THEN 1
                            ELSE 0
                        END
                    ),
                    0
                ) AS read_count

            FROM notifications

            WHERE user_id = %s
        """, (user_id,))

        notification_stats = cursor.fetchone()

        stats = {
            "total": notification_stats["total"] or 0,
            "unread": notification_stats["unread"] or 0,
            "read": notification_stats["read_count"] or 0
        }

        # -------------------------------------------------
        # PAGE
        # -------------------------------------------------

        return render_template(
            "student/notifications.html",

            dashboard="notifications",
            active_page="notifications",

            page_title="Notifications",
            page_subtitle=(
                "Stay updated with important "
                "activities and portal updates."
            ),

            student=student,

            notifications=notifications,
            notification_types=notification_types,

            stats=stats,
            unread_notifications=stats["unread"],

            search=search,
            selected_type=selected_type
        )

    except mysql.connector.Error as e:

        print(
            "STUDENT NOTIFICATIONS DB ERROR:",
            e
        )

        flash(
            "Unable to load notifications.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    except Exception as e:

        print(
            "STUDENT NOTIFICATIONS ERROR:",
            e
        )

        flash(
            "Unable to load notifications.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# MARK SINGLE NOTIFICATION AS READ
# =========================================================

@app.route(
    "/student/notifications/<notification_id>/read",
    methods=["POST"]
)
@student_required
def student_mark_notification_read(
    notification_id
):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor()

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
            url_for("student_notifications")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print(
            "MARK NOTIFICATION READ DB ERROR:",
            e
        )

        flash(
            "Unable to update notification.",
            "error"
        )

        return redirect(
            url_for("student_notifications")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "MARK NOTIFICATION READ ERROR:",
            e
        )

        flash(
            "Unable to update notification.",
            "error"
        )

        return redirect(
            url_for("student_notifications")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# MARK ALL STUDENT NOTIFICATIONS AS READ
# =========================================================

@app.route(
    "/student/notifications/mark-all-read",
    methods=["POST"]
)
@student_required
def student_mark_all_notifications_read():

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
            url_for("student_notifications")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print(
            "MARK ALL NOTIFICATIONS DB ERROR:",
            e
        )

        flash(
            "Unable to update notifications.",
            "error"
        )

        return redirect(
            url_for("student_notifications")
        )

    except Exception as e:

        if conn:
            conn.rollback()

        print(
            "MARK ALL NOTIFICATIONS ERROR:",
            e
        )

        flash(
            "Unable to update notifications.",
            "error"
        )

        return redirect(
            url_for("student_notifications")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT SETTINGS
# =========================================================

@app.route("/student/settings")
@student_required
def student_settings():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -------------------------------------------------
        # CURRENT STUDENT / ACCOUNT
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                u.id,
                u.name,
                u.email,
                u.role,
                u.status,
                u.created_at,

                s.id AS student_id,
                s.profile_completed

            FROM users u

            LEFT JOIN students s
                ON s.user_id = u.id

            WHERE u.id = %s

            LIMIT 1
        """, (user_id,))

        account = cursor.fetchone()

        if not account:

            flash(
                "Account information not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        # -------------------------------------------------
        # ACCOUNT REQUEST STATUS
        # -------------------------------------------------

        deactivation_request = None
        deletion_request = None

        # These tables will be created in the next step.
        # Keep safe defaults until then.

        try:

            cursor.execute("""
                SELECT
                    id,
                    reason,
                    status,
                    requested_at
                FROM student_account_requests

                WHERE student_id = %s
                  AND request_type = 'DEACTIVATION'
                  AND status = 'PENDING'

                ORDER BY requested_at DESC

                LIMIT 1
            """, (account["student_id"],))

            deactivation_request = cursor.fetchone()

        except mysql.connector.Error:

            conn.rollback()


        try:

            cursor.execute("""
                SELECT
                    id,
                    reason,
                    status,
                    requested_at
                FROM student_account_requests

                WHERE student_id = %s
                  AND request_type = 'DELETION'
                  AND status = 'PENDING'

                ORDER BY requested_at DESC

                LIMIT 1
            """, (account["student_id"],))

            deletion_request = cursor.fetchone()

        except mysql.connector.Error:

            conn.rollback()

        # -------------------------------------------------
        # SETTINGS PAGE
        # -------------------------------------------------

        return render_template(
            "student/settings.html",

            dashboard="settings",
            active_page="settings",

            page_title="Settings",
            page_subtitle=(
                "Manage your account, privacy "
                "and account controls."
            ),

            student=account,
            account=account,

            deactivation_request=deactivation_request,
            deletion_request=deletion_request
        )

    except mysql.connector.Error as e:

        print(
            "STUDENT SETTINGS DB ERROR:",
            e
        )

        flash(
            "Unable to load settings.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    except Exception as e:

        print(
            "STUDENT SETTINGS ERROR:",
            e
        )

        flash(
            "Unable to load settings.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT ACCOUNT DEACTIVATION REQUEST
# =========================================================

@app.route(
    "/student/settings/deactivation-request",
    methods=["POST"]
)
@student_required
def student_request_deactivation():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")
        reason = request.form.get(
            "reason",
            ""
        ).strip()

        if not reason:

            flash(
                "Please provide a reason for deactivation.",
                "error"
            )

            return redirect(
                url_for("student_settings")
            )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # CURRENT STUDENT

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        student_id = student["id"]

        # CHECK EXISTING REQUEST

        cursor.execute("""
            SELECT id
            FROM student_account_requests

            WHERE student_id = %s
              AND request_type = 'DEACTIVATION'
              AND status = 'PENDING'

            LIMIT 1
        """, (student_id,))

        existing = cursor.fetchone()

        if existing:

            flash(
                "A deactivation request is already pending.",
                "warning"
            )

            return redirect(
                url_for("student_settings")
            )

        # CREATE REQUEST

        cursor.execute("""
            INSERT INTO student_account_requests
            (
                id,
                student_id,
                request_type,
                reason,
                status
            )

            VALUES
            (
                %s,
                %s,
                'DEACTIVATION',
                %s,
                'PENDING'
            )
        """, (
            str(uuid.uuid4()),
            student_id,
            reason
        ))

        conn.commit()

        flash(
            "Account deactivation request submitted.",
            "success"
        )

        return redirect(
            url_for("student_settings")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print(
            "DEACTIVATION REQUEST DB ERROR:",
            e
        )

        flash(
            "Unable to submit deactivation request.",
            "error"
        )

        return redirect(
            url_for("student_settings")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT ACCOUNT DELETION REQUEST
# =========================================================

@app.route(
    "/student/settings/deletion-request",
    methods=["POST"]
)
@student_required
def student_request_deletion():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")
        reason = request.form.get(
            "reason",
            ""
        ).strip()

        confirmation = request.form.get(
            "confirm_delete"
        )

        if not reason:

            flash(
                "Please provide a reason for account deletion.",
                "error"
            )

            return redirect(
                url_for("student_settings")
            )

        if confirmation != "YES":

            flash(
                "Please confirm the account deletion request.",
                "error"
            )

            return redirect(
                url_for("student_settings")
            )

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # CURRENT STUDENT

        cursor.execute("""
            SELECT id
            FROM students
            WHERE user_id = %s
            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        student_id = student["id"]

        # CHECK EXISTING REQUEST

        cursor.execute("""
            SELECT id
            FROM student_account_requests

            WHERE student_id = %s
              AND request_type = 'DELETION'
              AND status = 'PENDING'

            LIMIT 1
        """, (student_id,))

        existing = cursor.fetchone()

        if existing:

            flash(
                "An account deletion request is already pending.",
                "warning"
            )

            return redirect(
                url_for("student_settings")
            )

        # CREATE REQUEST

        cursor.execute("""
            INSERT INTO student_account_requests
            (
                id,
                student_id,
                request_type,
                reason,
                status
            )

            VALUES
            (
                %s,
                %s,
                'DELETION',
                %s,
                'PENDING'
            )
        """, (
            str(uuid.uuid4()),
            student_id,
            reason
        ))

        conn.commit()

        flash(
            "Account deletion request submitted for admin review.",
            "success"
        )

        return redirect(
            url_for("student_settings")
        )

    except mysql.connector.Error as e:

        if conn:
            conn.rollback()

        print(
            "DELETION REQUEST DB ERROR:",
            e
        )

        flash(
            "Unable to submit deletion request.",
            "error"
        )

        return redirect(
            url_for("student_settings")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - COLLABORATIONS
# =========================================================

@app.route("/student/collaborations")
@student_required
def student_collaborations():

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        if not user_id:
            flash(
                "Student session expired. Please login again.",
                "error"
            )
            return redirect(url_for("login"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # CURRENT STUDENT
        # =================================================

        cursor.execute("""
            SELECT
                s.id AS student_id,
                s.user_id,
                s.college_id,

                u.name,
                u.email,

                c.college_name,
                c.college_code,
                c.university_name

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            LEFT JOIN colleges c
                ON s.college_id = c.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        college_id = student["college_id"]

        if not college_id:

            flash(
                "College information is not available.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        # =================================================
        # FILTERS
        # =================================================

        search = request.args.get(
            "search",
            ""
        ).strip()

        selected_status = request.args.get(
            "status",
            ""
        ).strip().upper()

        selected_type = request.args.get(
            "collaboration_type",
            ""
        ).strip().upper()

        # =================================================
        # COLLABORATIONS
        # =================================================

        query = """
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

                i.website AS industry_website,

                i.address AS industry_address,
                i.city AS industry_city,
                i.state AS industry_state

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.college_id = %s
        """

        params = [college_id]

        # =================================================
        # SEARCH
        # =================================================

        if search:

            query += """
                AND (
                    c.title LIKE %s
                    OR c.description LIKE %s
                    OR c.collaboration_type LIKE %s

                    OR i.company_name LIKE %s
                    OR i.company_type LIKE %s
                    OR i.industry_sector LIKE %s
                    OR i.contact_person LIKE %s
                )
            """

            search_value = f"%{search}%"

            params.extend([
                search_value,
                search_value,
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ])

        # =================================================
        # STATUS FILTER
        # =================================================

        if selected_status:

            query += """
                AND UPPER(c.status) = %s
            """

            params.append(
                selected_status
            )

        # =================================================
        # TYPE FILTER
        # =================================================

        if selected_type:

            query += """
                AND UPPER(c.collaboration_type) = %s
            """

            params.append(
                selected_type
            )

        # =================================================
        # ORDER
        # =================================================

        query += """
            ORDER BY

                CASE
                    WHEN UPPER(c.status) = 'ACTIVE'
                    THEN 1

                    WHEN UPPER(c.status) = 'PENDING'
                    THEN 2

                    WHEN UPPER(c.status) = 'COMPLETED'
                    THEN 3

                    ELSE 4
                END,

                c.created_at DESC
        """

        cursor.execute(
            query,
            tuple(params)
        )

        collaborations = cursor.fetchall()

        # =================================================
        # COLLABORATION TYPES
        # =================================================

        cursor.execute("""
            SELECT DISTINCT
                collaboration_type

            FROM collaborations

            WHERE college_id = %s

              AND collaboration_type IS NOT NULL

              AND TRIM(collaboration_type) <> ''

            ORDER BY collaboration_type
        """, (college_id,))

        collaboration_types = cursor.fetchall()

        # =================================================
        # STATISTICS
        # =================================================

        cursor.execute("""
            SELECT

                COUNT(*) AS total,

                SUM(
                    CASE
                        WHEN UPPER(status) = 'PENDING'
                        THEN 1
                        ELSE 0
                    END
                ) AS pending,

                SUM(
                    CASE
                        WHEN UPPER(status) = 'ACTIVE'
                        THEN 1
                        ELSE 0
                    END
                ) AS active,

                SUM(
                    CASE
                        WHEN UPPER(status) = 'COMPLETED'
                        THEN 1
                        ELSE 0
                    END
                ) AS completed,

                SUM(
                    CASE
                        WHEN UPPER(status)
                        IN ('REJECTED', 'CANCELLED')
                        THEN 1
                        ELSE 0
                    END
                ) AS closed

            FROM collaborations

            WHERE college_id = %s
        """, (college_id,))

        stats_row = cursor.fetchone() or {}

        stats = {
            "total": stats_row.get("total") or 0,
            "pending": stats_row.get("pending") or 0,
            "active": stats_row.get("active") or 0,
            "completed": stats_row.get("completed") or 0,
            "closed": stats_row.get("closed") or 0
        }

        # =================================================
        # ACTIVE INDUSTRY PARTNERS
        # =================================================

        cursor.execute("""
            SELECT COUNT(
                DISTINCT c.industry_id
            ) AS total

            FROM collaborations c

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.college_id = %s

              AND i.status = 'ACTIVE'
        """, (college_id,))

        active_industry_partners = (
            cursor.fetchone()["total"] or 0
        )

        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "student/collaborations.html",
            
            dashboard="collaborations",
            active_page="collaborations",

            page_title="Collaborations",
            page_subtitle=(
                "Explore industry collaborations "
                "associated with your college."
            ),

            student=student,

            collaborations=collaborations,
            collaboration_types=collaboration_types,

            stats=stats,
            active_industry_partners=active_industry_partners,

            search=search,
            selected_status=selected_status,
            selected_type=selected_type
        )

    except mysql.connector.Error as e:

        print(
            "STUDENT COLLABORATIONS DATABASE ERROR:",
            e
        )

        flash(
            "Unable to load collaborations.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    except Exception as e:

        print(
            "STUDENT COLLABORATIONS ERROR:",
            e
        )

        flash(
            "Unable to load collaborations.",
            "error"
        )

        return redirect(
            url_for("student_dashboard")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =========================================================
# STUDENT - COLLABORATION DETAIL
# =========================================================

@app.route(
    "/student/collaborations/<collaboration_id>"
)
@student_required
def student_collaboration_detail(
    collaboration_id
):

    conn = None
    cursor = None

    try:

        user_id = session.get("user_id")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # =================================================
        # CURRENT STUDENT
        # =================================================

        cursor.execute("""
            SELECT
                s.id AS student_id,
                s.college_id,
                u.name,
                u.email

            FROM students s

            INNER JOIN users u
                ON s.user_id = u.id

            WHERE s.user_id = %s

            LIMIT 1
        """, (user_id,))

        student = cursor.fetchone()

        if not student:

            flash(
                "Student profile not found.",
                "error"
            )

            return redirect(
                url_for("student_dashboard")
            )

        # =================================================
        # COLLABORATION
        # Ownership is verified through student's college
        # =================================================

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

                col.college_name,
                col.college_code,
                col.university_name,

                i.company_name,
                i.company_type,
                i.industry_sector,

                i.contact_person,
                i.designation,

                i.email AS industry_email,
                i.phone AS industry_phone,

                i.website AS industry_website,

                i.address AS industry_address,
                i.city AS industry_city,
                i.state AS industry_state

            FROM collaborations c

            INNER JOIN colleges col
                ON c.college_id = col.id

            INNER JOIN industries i
                ON c.industry_id = i.id

            WHERE c.id = %s

              AND c.college_id = %s

            LIMIT 1
        """, (
            collaboration_id,
            student["college_id"]
        ))

        collaboration = cursor.fetchone()

        if not collaboration:

            flash(
                "Collaboration not found.",
                "error"
            )

            return redirect(
                url_for("student_collaborations")
            )

        # =================================================
        # RENDER
        # =================================================

        return render_template(
            "student/collaborations/collaboration_detail.html",

            dashboard="collaborations",
            active_page="collaborations",

            page_title="Collaboration Details",

            student=student,
            collaboration=collaboration
        )

    except mysql.connector.Error as e:

        print(
            "STUDENT COLLABORATION DETAIL DB ERROR:",
            e
        )

        flash(
            "Unable to load collaboration details.",
            "error"
        )

        return redirect(
            url_for("student_collaborations")
        )

    except Exception as e:

        print(
            "STUDENT COLLABORATION DETAIL ERROR:",
            e
        )

        flash(
            "Unable to load collaboration details.",
            "error"
        )

        return redirect(
            url_for("student_collaborations")
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


#=============================================
#LOGOUT
#=============================================

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

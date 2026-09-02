from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
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

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
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

            if not user:
                flash("Invalid email or password.", "error")
                return render_template("login.html")

            if user["status"] != "ACTIVE":
                flash("Your account is not active.", "error")
                return render_template("login.html")

            if not check_password_hash(
                user["password"],
                password
            ):
                flash("Invalid email or password.", "error")
                return render_template("login.html")

            # Store user information in session
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            # Admin
            if user["role"] == "ADMIN":
                return redirect(
                    url_for("admin_dashboard")
                )

            # Other roles will be handled later
            flash(
                "You are not authorized for the Admin Panel.",
                "error"
            )

            session.clear()

            return redirect(
                url_for("login")
            )

        except Exception as e:

            print("=" * 60)
            print("LOGIN ERROR:")
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
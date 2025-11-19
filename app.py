from flask import Flask, render_template, request, redirect, session, flash
import psycopg2
import psycopg2.extras
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "CHANGE_THIS_SECRET_KEY"   # Change this in your final submission

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db():
    return psycopg2.connect(
        dbname="company",
        user="owner",
        #password="password",
        host="localhost"
    )

# ---------------------------
# LOGIN REQUIRED DECORATOR
# ---------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

# ---------------------------
# LOGIN ROUTE (A1)
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("SELECT * FROM app_user WHERE username=%s", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect("/")
        else:
            flash("Invalid username or password")

    return render_template("login.html")

# ---------------------------
# LOGOUT (A1)
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------------
# HOME ROUTE (A2)
# ---------------------------
@app.route("/")
@login_required
def home():
    search = request.args.get("search", "")
    sort = request.args.get("sort", "name_asc")

    # Sorting whitelist (A2 requirement: safe ORDER BY)
    allowed_sorts = {
        "name_asc": "e.lname ASC, e.fname ASC",
        "name_desc": "e.lname DESC, e.fname DESC",
        "hours_asc": "total_hours ASC",
        "hours_desc": "total_hours DESC"
    }
    order_by = allowed_sorts.get(sort, "e.lname ASC")

    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    query = f"""
        SELECT
            e.ssn,
            e.fname || ' ' || e.lname AS full_name,
            d.dname,
            COALESCE(dep.count_dep, 0) AS num_dependents,
            COALESCE(w.count_proj, 0) AS num_projects,
            COALESCE(w.total_hours, 0) AS total_hours
        FROM employee e
        JOIN department d ON e.dno = d.dnumber

        LEFT JOIN (
            SELECT essn, COUNT(*) AS count_dep
            FROM dependent
            GROUP BY essn
        ) dep ON dep.essn = e.ssn

        LEFT JOIN (
            SELECT essn, COUNT(*) AS count_proj, SUM(hours) AS total_hours
            FROM works_on
            GROUP BY essn
        ) w ON w.essn = e.ssn

        WHERE e.fname ILIKE %s OR e.lname ILIKE %s
        ORDER BY {order_by};
    """

    cur.execute(query, (f"%{search}%", f"%{search}%"))
    employees = cur.fetchall()

    return render_template("home.html", employees=employees)
    
# ---------------------------
# EXPORT ROUTE
# ---------------------------  

from flask import Response
import csv
from io import StringIO

@app.route("/export/employees")
@login_required
def export_employees():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            e.fname || ' ' || e.lname AS full_name,
            d.dname,
            COALESCE(dep.count_dep, 0) AS num_dependents,
            COALESCE(w.count_proj, 0) AS num_projects,
            COALESCE(w.total_hours, 0) AS total_hours
        FROM employee e
        JOIN department d ON e.dno = d.dnumber
        LEFT JOIN (
            SELECT essn, COUNT(*) AS count_dep
            FROM dependent
            GROUP BY essn
        ) dep ON dep.essn = e.ssn
        LEFT JOIN (
            SELECT essn, COUNT(*) AS count_proj, SUM(hours) AS total_hours
            FROM works_on
            GROUP BY essn
        ) w ON w.essn = e.ssn
        ORDER BY e.lname ASC;
    """)

    rows = cur.fetchall()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["full_name", "department", "dependents", "projects", "total_hours"])
    writer.writerows(rows)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees.csv"}
    )


# ---------------------------
# RUN FLASK APP
# ---------------------------

if __name__ == "__main__":
    app.run(debug=True)

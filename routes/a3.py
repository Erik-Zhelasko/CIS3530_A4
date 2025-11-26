# import the Flask library
from flask import Flask, redirect, render_template, request, jsonify, Blueprint
import psycopg
import base64

a3bp = Blueprint("a3", __name__)

DATABASE_CONFIG = {
    "dbname": "assn4",
    "user": "postgres",
    "password": base64.b64decode("VHZva2lkcw==").decode('utf-8'),
    "host": "localhost",
    "port": "5432",
}

def get_db_connection():
    conn = psycopg.connect(**DATABASE_CONFIG)
    return conn

#Route for project page
@a3bp.route("/a3")
def a3_page():
    return render_template("a3.html")

# Route for project details (TESTING TO SEE IF WEBSITE LINK WORKS)
#@a3bp.route("/project/<int:project_id>")
#def project_detail(project_id):
#    return f"This is the project page for {project_id}"

@a3bp.route("/project/<int:project_id>")
def project_detail_page(project_id):
    return render_template("a4.html", project_id=project_id)

@a3bp.get("/API/project/<int:project_id>")
def api_project_details(project_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT pname
        FROM Project
        WHERE pnumber = %s;
    """, (project_id,))
    proj = cur.fetchone()

    if not proj:
        return jsonify({"error": "Project not found"}), 404

    cur.execute("""
        SELECT CONCAT(E.fname, ' ', E.lname) AS full_name,
               W.hours
        FROM Works_On W
        JOIN Employee E ON W.essn = E.ssn
        WHERE W.pno = %s
        ORDER BY full_name;
    """, (project_id,))
    employees = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "project_name": proj[0],
        "employees": [
            {"full_name": e[0], "hours": e[1]}
            for e in employees
        ]
    })

@a3bp.post("/API/project_hours")
def upsert_hours():
    pno = request.form.get("project_id")
    emp_id = request.form.get("employee_id")
    hours = request.form.get("hours")

    conn = get_db_connection()
    cur = conn.cursor()

    sql = """
        INSERT INTO Works_On (Essn, Pno, Hours)
        VALUES (%s, %s, %s)
        ON CONFLICT (Essn, Pno)
        DO UPDATE SET Hours = Works_On.Hours + EXCLUDED.Hours;
    """

    cur.execute(sql, (emp_id, pno, hours))
    conn.commit()

    cur.close()
    conn.close()

    return redirect(f"/project/{pno}")


@a3bp.get("/API/employees/A4")
def employees_for_a4():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT ssn, fname || ' ' || lname AS full_name
        FROM Employee
        ORDER BY lname, fname;
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    employees = [
        {"ssn": r[0], "full_name": r[1]}
    for r in rows ]

    return jsonify(employees)


@a3bp.post("/API/project/upsert")
def upsert_workson():
    data = request.get_json()

    project_id = data.get("project_id")
    essn = data.get("essn")
    hours = data.get("hours")

    # convert hours to int
    try:
        hours = float(hours)
    except:
        return jsonify({"message": "Invalid hours"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO Works_On (Essn, Pno, Hours)
        VALUES (%s, %s, %s)
        ON CONFLICT (Essn, Pno)
        DO UPDATE SET Hours = Works_On.Hours + EXCLUDED.Hours;
    """

    cursor.execute(query, (essn, project_id, hours))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Hours updated successfully!"})



@a3bp.get("/API/projects")
def projects():
    return get_projects_table()

def get_projects_table():

    sort = request.args.get("sort", "")
    direction = request.args.get("dir", "asc").lower()

    allowed = ["headcount", "total_hours"]
    sort_clause = ""

    #default direction when not sorting by headcount or total_hours (by Project Name)
    if direction not in ["asc", "desc"]:
        direction = "asc"

    if sort in allowed:
        if sort == "headcount":
            sort_expr = "COUNT(DISTINCT W.essn)"
        elif sort == "total_hours":
            sort_expr = "COALESCE(SUM(W.hours),0)"
        sort_clause = f" ORDER BY {sort_expr} {direction}"

    #sort_clause gets added to query so that it groups the data and returns it sorted as needed
    query = f"""
    SELECT P.pnumber AS project_id, P.pname AS project_name, COALESCE(D.dname,'No Dept') AS department_name, COUNT(DISTINCT W.essn) AS headcount, COALESCE(SUM(W.hours),0) AS total_hours
    FROM Project P
    LEFT JOIN Department D ON P.dnum = D.dnumber
    LEFT JOIN Works_On W ON P.pnumber = W.pno
    GROUP BY P.pnumber, P.pname, D.dname
    """ + sort_clause + ";"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    result = []

    for r in rows:
        project_id = r[0]
        project_name = r[1]
        department_name = r[2]
        headcount = r[3]
        total_hours = r[4]

        if total_hours is None:
            total_hours = 0

        row_dict = {
            "project_id": project_id,
            "project_name": project_name,
            "department_name": department_name,
            "headcount": headcount,
            "total_hours": total_hours
        }
        result.append(row_dict)


    return jsonify(result)

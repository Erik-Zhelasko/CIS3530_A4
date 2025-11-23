# import the Flask library
from flask import Flask, render_template, request, jsonify, Blueprint
import psycopg
import base64

a3bp = Blueprint("a3", __name__)

DATABASE_CONFIG = {
    "dbname": "assn4",
    "user": "postgres",
    "password": "uku04vrr!",
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

# Route for project details
@a3bp.route("/project/<int:project_id>")
def project_detail(project_id):
    return f"This is the project page for {project_id}"

#@app.route("/project/<int:project_id>")
#def project_detail_page(project_id):
    #return render_template("a4.html", project_id=project_id)


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



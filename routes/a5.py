# import the Flask library
from flask import Flask, render_template, request, jsonify, Blueprint
import psycopg
import base64

a5bp = Blueprint("a5", __name__)

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


# Default route added using a decorator, for view function 'welcome'
# We pass a simple string to the frontend browser
@a5bp.route('/a5')
def welcome():
    return render_template("a5.html")

@a5bp.route("/API/employee",methods=["GET","POST","DELETE","PATCH","HEAD"])
def employee():
    if request.method == "GET":
        return get_employee_table()
    elif request.method == "POST":
        return addEmployee(request)
    elif request.method =="DELETE":
        return deleteEmployee(request)
    elif request.method =="PATCH":
        return editEmployee(request)
    elif request.method =="HEAD":
        return get_table_headers()

def get_employee_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM EMPLOYEE ORDER BY ssn ASC ")
    table = cursor.fetchall()
    return jsonify(table)

def get_table_headers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM EMPLOYEE ORDER BY ssn ASC ")
    headers = []
    for x in cursor.description:
        headers.append(cursor.description[x][0])
    print(headers)
    return jsonify(headers)

def addEmployee(request):
    json = request.get_json()
    print (json)
    # {'First Name': 'usadi', 'Middle Initial': 'asdu', 'Last Name': 'i', 'SSN': 'ih', 'Address': 'iu', 'Sex': 'iu', 'Salary': 'uihu', 'Supervisor SSN': 'uiudsa', 'Department Number': 'xzui', 'Date of Birth': 'huxczui', 'Employment Date': 'uh'}
    query = "INSERT INTO employee (fname,minit,lname,ssn,address,sex,salary,super_ssn,dno,bdate,empdate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
    values = []
    for x in json.values():
        t = x if x.strip() != '' else None
        values.append(t)
    print(query)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()    
        if cursor.rowcount > 0:
            return ("Sucess",201)
        else:
            return("No Rows Inserted",200)
    except psycopg.Error as e:
        return (str(e),500)



def editEmployee(request):
    json = request.get_json()

    ssn = json["ssn"]
    address = json["address"]
    salary = json["salary"]
    dno = json["dno"]


    query = "UPDATE employee SET "
    end = " WHERE ssn = %s;" 
    query = query + " address = %s, " if address != None else query
    query = query + " salary = %s, " if salary != None else query
    query = query + " dno = %s " if dno != None else query
    query = query + end
    print(query)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query,(address,salary,dno,ssn))
        conn.commit()
        if cursor.rowcount > 0:
            return ("OK",200)
        else:
            return ("NoChange",201)
    except psycopg.Error as e:
        return (str(e),500)

def deleteEmployee(request):
    json = request.get_json()
    ssn = json["ssn"]
    query = "DELETE FROM employee WHERE ssn=%s;"
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query,(ssn,))
        conn.commit()
        return ("OK",200)
    except psycopg.errors.RestrictViolation as error:
        return ("RestrictViolation",500)
    except psycopg.Error as e:
        return (str(e),500)






# # Start with flask web app, with debug as True,# only if this is the starting page
# if(__name__ == "__main__"):
#     app.run(debug=True)
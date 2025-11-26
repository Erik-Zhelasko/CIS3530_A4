# import the Flask library
from flask import Flask, render_template, request, jsonify, Blueprint
import psycopg
import base64

a6bp = Blueprint("a6", __name__)

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
@a6bp.route("/a6")
def a6_page():
    return render_template("a6.html")

@a6bp.get("/API/manager_overview")
def projects():
    return get_mOverview_table()

def get_mOverview_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM managers_overview ORDER BY dnumber ASC")
    table = cursor.fetchall()
    return jsonify(table)

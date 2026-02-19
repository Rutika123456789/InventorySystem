from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"


# DATABASE CONNECTION
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rutika@16",
        database="inventory_system"
    )


# FORCE RESET ADMIN USER (CLEAN STATE)
def reset_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete old admin completely
    cursor.execute("DELETE FROM users WHERE username = %s", ("admin",))

    # Create new hashed admin
    hashed_password = generate_password_hash("admin123")

    cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (%s, %s, %s)
    """, ("admin", hashed_password, "admin"))

    conn.commit()
    cursor.close()
    conn.close()


reset_admin()


# LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid Credentials")

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("index.html", items=items)


# ADD ITEM (ADMIN ONLY)
@app.route("/add", methods=["POST"])
def add_item():
    if session.get("role") != "admin":
        return "Unauthorized Access"

    name = request.form["name"]
    quantity = request.form["quantity"]
    min_quantity = request.form["min_quantity"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items (name, quantity, min_quantity)
        VALUES (%s, %s, %s)
    """, (name, quantity, min_quantity))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("dashboard"))


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

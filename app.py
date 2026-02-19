from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "inventory_secret_key"

# DATABASE CONNECTION
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rutika@16",
    database="inventory_system"
)

cursor = db.cursor()


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# HOME PAGE
@app.route("/", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["item_name"]
        quantity = request.form["quantity"]
        min_quantity = request.form["min_quantity"]

        cursor.execute(
            "INSERT INTO items (name, quantity, min_quantity) VALUES (%s, %s, %s)",
            (name, quantity, min_quantity)
        )
        db.commit()

        return redirect("/")

    search_query = request.args.get("search")

    if search_query:
        cursor.execute(
            "SELECT * FROM items WHERE name LIKE %s",
            ('%' + search_query + '%',)
        )
    else:
        cursor.execute("SELECT * FROM items")

    items = cursor.fetchall()

    return render_template("index.html", items=items, user=session["user"])


# EDIT PAGE
@app.route("/edit/<int:id>")
def edit(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute("SELECT * FROM items WHERE id=%s", (id,))
    item = cursor.fetchone()

    return render_template("edit.html", item=item)


# UPDATE ITEM
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    if "user" not in session:
        return redirect("/login")

    name = request.form["item_name"]
    quantity = request.form["quantity"]
    min_quantity = request.form["min_quantity"]

    cursor.execute(
        "UPDATE items SET name=%s, quantity=%s, min_quantity=%s WHERE id=%s",
        (name, quantity, min_quantity, id)
    )
    db.commit()

    return redirect("/")


# DELETE ITEM
@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect("/login")

    cursor.execute("DELETE FROM items WHERE id=%s", (id,))
    db.commit()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# DATABASE CONNECTION
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Rutika@16",
    database="inventory_system"
)

cursor = db.cursor()


# HOME PAGE + SEARCH + ADD
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["item_name"]
        quantity = request.form["quantity"]
        min_quantity = request.form["min_quantity"]

        sql = "INSERT INTO items (name, quantity, min_quantity) VALUES (%s, %s, %s)"
        values = (name, quantity, min_quantity)
        cursor.execute(sql, values)
        db.commit()

        return redirect("/")

    search_query = request.args.get("search")

    if search_query:
        cursor.execute("SELECT * FROM items WHERE name LIKE %s", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT * FROM items")

    items = cursor.fetchall()

    return render_template("index.html", items=items)


# EDIT PAGE
@app.route("/edit/<int:id>")
def edit(id):
    cursor.execute("SELECT * FROM items WHERE id=%s", (id,))
    item = cursor.fetchone()
    return render_template("edit.html", item=item)


# UPDATE ITEM
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    name = request.form["item_name"]
    quantity = request.form["quantity"]
    min_quantity = request.form["min_quantity"]

    sql = "UPDATE items SET name=%s, quantity=%s, min_quantity=%s WHERE id=%s"
    values = (name, quantity, min_quantity, id)

    cursor.execute(sql, values)
    db.commit()

    return redirect("/")


# DELETE ITEM
@app.route("/delete/<int:id>")
def delete(id):
    cursor.execute("DELETE FROM items WHERE id=%s", (id,))
    db.commit()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)

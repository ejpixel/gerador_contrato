import os

from flask import Flask, render_template, request, send_file, redirect, session
from flask_sqlalchemy import SQLAlchemy as sql
import hashlib
from helpers import *
import json

app = Flask(__name__)

app.secret_key = os.environ["SECRET_KEY"]

try:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]

except KeyError:
    raise ValueError("É necessário definir variável de ambiente DATABASE_URI com a chave de acesso do banco de dados.")

db = sql(app)
start_db(db)

@app.route("/access", methods=["GET", "POST"])
def access():
    if request.method == "POST":
        name = request.form["name"]
        hash_result = hashlib.sha256(request.form["key"].encode()).hexdigest()
        result = db.engine.execute("SELECT name, permissions FROM users INNER JOIN roles ON users.role_id=roles.id WHERE name = %s AND password = %s", name, hash_result).first()
        if result:
            session["user_id"] = result[0]
            session["roles"] = result[1]
            return redirect("/")
        else:
            flash("Username or password incorrect")
    return render_template("access.html")

@app.route("/")
@login_required
@admin_role
def index():
    contracts = db.engine.execute("SELECT COUNT(*) FROM services").first()[0]
    no_payments_contracts = db.engine.execute("SELECT COUNT(*) FROM services WHERE first_payment is null").first()[0]
    no_accepted_contracts = db.engine.execute("SELECT COUNT(*) FROM services WHERE acceptance_date is null").first()[0]
    clients = db.engine.execute("SELECT COUNT(*) FROM clients").first()[0]
    return render_template("index.html", contracts=contracts, no_payments_contracts=no_payments_contracts, no_accepted_contracts=no_accepted_contracts, clients=clients)

@app.route("/logout")
@login_required
def logout():
    session["user_id"] = None
    session["roles"] = None
    return redirect("/")

@app.route("/contracts_manager")
@login_required
@admin_role
def contracts_manager():
    contracts = db.engine.execute("SELECT * FROM services ORDER BY id")
    return render_template("contracts_manager.html", contracts=list(contracts))

@app.route("/clients_manager")
@login_required
@admin_role
def clients_manager():
    clients = db.engine.execute("SELECT * FROM clients ORDER BY id")
    return render_template("clients_manager.html", clients=list(clients))

@app.route("/access_manager")
@login_required
@admin_role
def access_manager():
    raw_accounts = db.engine.execute("SELECT name, role_id, permissions FROM users INNER JOIN roles on role_id=id ")
    accounts = [[name, role, " ".join(permissions)] for name, role, permissions in raw_accounts]
    roles = db.engine.execute("SELECT * FROM roles")
    return render_template("access_manager.html", accounts=list(accounts), roles=list(roles))

@app.route("/ata_manager")
@login_required
@admin_role
def ata_manager():
    atas = db.engine.execute("SELECT * FROM ej ORDER BY ata_date")
    return render_template("ata_manager.html", atas=list(atas))

@app.route("/access_creation", methods=["POST"])
@login_required
@admin_role
def access_creation():
    name = request.form['username']
    hash = hashlib.sha256(request.form['password'].encode()).hexdigest()
    role_id = request.form['role']
    db.engine.execute("INSERT INTO users(name, password, role_id) VALUES(%(name)s, %(hash)s, %(role)s)", name=name, hash=hash, role=role_id)
    return redirect(url_for("access_manager"))

@app.route("/role_creation", methods=["POST"])
@login_required
@admin_role
def role_creation():
    permissions = normalize_array(request.form['permissions'])
    db.engine.execute("INSERT INTO roles(permissions) VALUES(%(p)s)", p=permissions)
    return redirect(url_for("access_manager"))

@app.route("/edit_accounts", methods=["POST"])
@login_required
@admin_role
def edit_accounts():
    complete_request = json.loads(request.get_data().decode("utf-8"))
    for req in complete_request:
        old = db.engine.execute("SELECT * FROM users WHERE name=%s", req["username"]).first()
        if len(old) == 0:
            flash("Cannot edit username")
            return redirect(url_for("access_manager"))
        db.engine.execute("UPDATE users SET role_id=%s WHERE name=%s", int(req["role id"]), req["username"])
    flash("Success")
    return redirect(url_for("access_manager"))

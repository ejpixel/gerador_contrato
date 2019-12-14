import os

from flask import Flask, render_template, request, send_file, redirect, session
from flask_sqlalchemy import SQLAlchemy as sql
import gerador_contrato
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
        hash = hashlib.sha256(request.form["key"].encode()).hexdigest()
        result = db.engine.execute("SELECT name, permissions FROM users INNER JOIN roles ON users.role_id=roles.id WHERE password = %s", hash).first()
        if result:
            session["user_id"] = result[0]
            session["roles"] = result[1]
        return redirect("/")
    return render_template("access.html")

@app.route("/")
@login_required
@role(roles=[Roles.CREATION.name, Roles.ADMIN.name])
def index():
    return render_template("index.html")

@app.route("/generate_contract", methods=["GET", "POST"])
@login_required
@role(roles=[Roles.CREATION.name, Roles.ADMIN.name])
def generate():
    if request.method == "GET":
        try:
            open(gerador_contrato.OUTPUT).close()
        except:
            return redirect("/")
        return send_file(gerador_contrato.OUTPUT, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", as_attachment=True, attachment_filename=gerador_contrato.OUTPUT)
    service, client, ej = req_to_profiles(request, db)
    info = gerador_contrato.gen_info(service, client, ej)
    gerador_contrato.gen_contract(gerador_contrato.TEMPLATE, info, gerador_contrato.OUTPUT)


    return redirect("/generate_contract")

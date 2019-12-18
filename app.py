import os

from flask import Flask, render_template, request, send_file, redirect, session, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy as sql
import gerador_contrato
import hashlib
from helpers import *

app = Flask(__name__)

app.secret_key = os.environ["SECRET_KEY"]

try:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URI"]

except KeyError:
    raise ValueError("É necessário definir variável de ambiente DATABASE_URI com a chave de acesso do banco de dados.")

db = sql(app)
start_db(db)

env = os.getenv("CEREBRO_ENV", "prod") if os.getenv("CEREBRO_ENV", "prod") in ["dev", "prod"] else "dev"

@app.before_request
def before_request():
    if not request.is_secure and env == "prod":
        app.config["SESSION_COOKIE_SECURE"] = True
        url = request.url.replace('http://', 'https://', 1)
        code = 301
        return redirect(url, code=code)


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
@creation_role
def index():
    return render_template("index.html")

@app.route("/logout")
@login_required
def logout():
    session["user_id"] = None
    session["roles"] = None
    return redirect("/")


@app.route("/generate_contract", methods=["GET", "POST"])
@login_required
@creation_role
def generate_contract():
    if request.method == "GET":
        try:
            open(gerador_contrato.OUTPUT).close()
        except:
            return redirect("/")
        return send_file(gerador_contrato.OUTPUT, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", as_attachment=True, attachment_filename=gerador_contrato.OUTPUT)
    service, client, ej = req_to_profiles(request, db)
    if not client.client.cpf or (not client.store.cnpj and not client.client.cpf):
        flash("CPF and CNPJ (if pj) is necessary to create a contract. Check if cpf has 11 digits or cnpj has 14 digits and both are just numbers")
        return redirect("/")

    update_data(service, client, db)
    info = gerador_contrato.gen_info(service, client, ej)
    gerador_contrato.gen_contract(gerador_contrato.TEMPLATE, info, gerador_contrato.OUTPUT)
    event_new_contract(client.store.name, client.client.name, service.short_service_description)

    return redirect("/generate_contract")

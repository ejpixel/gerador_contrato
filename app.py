import os

from flask import Flask, render_template, request, send_file, redirect, session
from flask_sqlalchemy import SQLAlchemy as sql
from profiles import *
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
        result = db.engine.execute("SELECT * FROM users WHERE password = %s", hash).first()
        if result:
            session["user_id"] = result[0]
        return redirect("/")
    return render_template("access.html")

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/generate", methods=["GET", "POST"])
@login_required
def generate():
    if request.method == "GET":
        try:
            open(gerador_contrato.OUTPUT).close()
        except:
            return redirect("/")
        return send_file(gerador_contrato.OUTPUT, mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document", as_attachment=True, attachment_filename=gerador_contrato.OUTPUT)
    type_contract = request.form['type_contract']
    deadline = request.form['deadline']
    short_description = request.form['short_description']
    price = request.form['price']
    payment = request.form['payment']
    payment_price = request.form['payment_price']
    short_service_list = request.form['short_service_list'].strip().split("\r\n")
    client_store_name = request.form['client_store_name']
    client_address = request.form['client_address']
    client_cep = request.form['client_cep']
    client_cnpj = request.form['client_cnpj']
    client_name = request.form['client_name']
    client_rg = request.form['client_rg']
    client_cpf = request.form['client_cpf']
    client_email = request.form['client_email']
    service = Service(type_contract, deadline, short_description, price, payment, payment_price, short_service_list)
    client = Client(client_name, client_store_name, client_rg, client_cpf, client_cnpj, client_address)
    current_ej = db.engine.execute("SELECT * FROM ej ORDER BY ata_date limit 1").first()
    ej = EJ(*current_ej)
    info = gerador_contrato.gen_info(service, client, ej)
    gerador_contrato.gen_contract(gerador_contrato.TEMPLATE, info, gerador_contrato.OUTPUT)

    descriptions = json.dumps({"short_description": short_description, "service_list": short_service_list})
    id = db.engine.execute('INSERT INTO services("username", "type", "days_to_finish", "total_price", "payment_price", "payment", "description") VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id', session["user_id"], type_contract, deadline, price, payment_price, payment, descriptions).first()
    db.engine.execute('INSERT INTO clients("store_name","address","cep","cnpj","client_name","rg","cpf","email","service_id") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', client_store_name, client_address, client_cep, client_cnpj, client_name, client_rg, client_cpf, client_email, id[0])
    return redirect("/generate")

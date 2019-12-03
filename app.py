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
    #
    # client_id = db.engine.execute("SELECT id from clients WHERE store_name=%(store_name)s AND address=%(address)s AND cep=%(cep)s AND cnpj=%(cnpj)s AND client_name=%(name)s AND rg=%(rg)s AND cpf=%(cpf)s AND email=%(email)s", store_name=client_store_name, address=client_address, cep=client_cep, cnpj=client_cnpj, name=client_name, rg=client_rg, cpf=client_cpf, email=client_email).first()
    # if not list(client_id):
    #     client_id = "INSERT INTO clients ("store_name","address","cep","cnpj","client_name","rg","cpf","email")"
    client_id = db.engine.execute('''
    with possible_client as (
        SELECT id from clients
        WHERE store_name=%(store_name)s AND address=%(address)s AND cep=%(cep)s AND cnpj=%(cnpj)s AND client_name=%(name)s AND rg=%(rg)s AND cpf=%(cpf)s AND email=%(email)s
    ), i as (
        INSERT INTO clients (store_name,address,cep,cnpj,client_name,rg,cpf,email)
            SELECT %(store_name)s, %(address)s, %(cep)s, %(cnpj)s, %(name)s, %(rg)s, %(cpf)s, %(email)s
            WHERE NOT EXISTS (SELECT 1 FROM possible_client)
            RETURNING id
    )
    select id
    from i
    union all
    select id
    from possible_client
     ''', store_name=client_store_name, address=client_address, cep=client_cep, cnpj=client_cnpj, name=client_name, rg=client_rg, cpf=client_cpf, email=client_email).first()[0]
    db.engine.execute('''
    WITH upsert as (
        UPDATE services
        SET 
            username=%(username)s,
            type=%(type_contract)s,
            days_to_finish=%(deadline)s,
            total_price=%(price)s,
            payment_price=%(payment_price)s,
            payment=%(payment)s,
            description=%(description)s,
            client_id=%(client_id)s
        WHERE
            username=%(username)s AND
            type=%(type_contract)s AND
            days_to_finish=%(deadline)s AND
            total_price=%(price)s AND
            payment_price=%(payment_price)s AND
            payment=%(payment)s AND
            client_id=%(client_id)s
        RETURNING *
    )
    INSERT INTO services("username", "type", "days_to_finish", "total_price", "payment_price", "payment", "description", "client_id")
        SELECT %(username)s, %(type_contract)s, %(deadline)s, %(price)s, %(payment_price)s, %(payment)s, %(description)s, %(client_id)s
        WHERE NOT EXISTS(SELECT 1 FROM upsert)
    ''', username=session["user_id"], type_contract=type_contract, deadline=deadline, price=price, payment_price=payment_price, payment=payment, description=descriptions, client_id=client_id)#, session["user_id"], type_contract, deadline, price, payment_price, payment, client_id, session["user_id"], type_contract, deadline, price, payment_price, payment, descriptions, client_id)
    # db.engine.execute('INSERT INTO clients("store_name","address","cep","cnpj","client_name","rg","cpf","email","service_id") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', client_store_name, client_address, client_cep, client_cnpj, client_name, client_rg, client_cpf, client_email, id[0])
    return redirect("/generate")

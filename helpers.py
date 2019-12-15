from functools import wraps
from flask import session, request, redirect, url_for, flash
from enum import Enum
from profiles import *
import json
import datetime
import sapixel


class Roles(Enum):
    CREATION = "CREATION"
    ADMIN = "ADMIN"


def start_db(db):
    commands = ['''
    CREATE TABLE IF NOT EXISTS ej (
        id serial primary key,
        ata_date date not null,
        president text not null,
        president_rg text not null,
        president_cpf text not null,
        vice_president text not null,
        vice_president_rg text not null,
        vice_president_cpf text not null
        )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS roles (
        id serial primary key,
        permissions text[]
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS users (
        id serial primary key,
        name text not null unique,
        password text not null,
        role_id integer REFERENCES roles(id) not null
        )
    ''',
        '''
    CREATE TABLE IF NOT EXISTS clients (
        id serial primary key,
        store_name text,
        street text not null,
        number text not null,
        neighborhood text not null,
        city text not null,
        state text not null,
        country text not null,
        cep text not null,
        cnpj text,
        client_name text not null,
        rg text not null,
        cpf text not null,
        email text not null,
        removed boolean not null default false
        )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS services (
        id serial primary key,
        username text not null,
        type text not null,
        days_to_finish integer not null,
        total_price float not null,
        payment_price float not null,
        payment integer not null,
        description json not null,
        contract_generation_date date not null default now(),
        acceptance_date date,
        first_payment date,
        client_id integer REFERENCES clients(id) not null,
        removed boolean not null default false
        )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS payments (
        id serial primary key,
        payment serial not null,
        price float not null,
        service_id integer REFERENCES services(id)
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS service_payment_data (
        id serial primary key,
        service_id integer REFERENCES services(id) not null,
        aliquota float not null,
        cst integer not null,
        cnae integer not null,
        cfps integer not null,
        aedf integer not null,
        baseCalcSubst integer not null
    )
    '''
    ]
    for command in commands:
        db.engine.execute(command)

def check_roles(roles, user_roles):
    for role in roles:
        if role in user_roles:
            return True
    return False

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            return f(*args, **kwargs)
        return redirect(url_for('access'))
    return decorated_function

def creation_role(f):
    return role(f, roles=[Roles.CREATION.name])

def admin_role(f):
    return role(f, roles=[Roles.ADMIN.name])

def role(f, roles):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") and session.get("roles") and check_roles(roles, session["roles"]):
            return f(*args, **kwargs)
        flash("You don't have permission to see this page")
        return redirect(url_for('access'))
    return decorated_function

def req_to_profiles(req, db):
    type_contract = req.form['type_contract']
    deadline = req.form['deadline']
    short_description = req.form['short_description']
    price = req.form['price']
    payment = req.form['payment']
    payment_price = req.form['payment_price']
    short_service_list = req.form['short_service_list'].strip().split("\r\n")
    client_store_name = req.form['client_store_name']
    client_street = req.form["client_street"]
    client_number = req.form["client_number"]
    client_neighborhood = req.form["client_neighborhood"]
    client_city = req.form["client_city"]
    client_state = req.form["client_state"]
    client_country = req.form["client_country"]
    client_cep = req.form['client_cep']
    client_cnpj = req.form['client_cnpj']
    client_name = req.form['client_name']
    client_rg = req.form['client_rg']
    client_cpf = req.form['client_cpf']
    client_email = req.form['client_email']
    service = Service(type_contract, deadline, short_description, price, payment, payment_price, short_service_list)
    client = Client(client_name, client_store_name, client_rg, client_cpf, client_cnpj, client_street, client_number, client_neighborhood, client_city, client_state, client_country, client_cep, client_email)
    current_ej = db.engine.execute("SELECT ata_date, president, president_rg, president_cpf, vice_president, vice_president_rg, vice_president_cpf FROM ej ORDER BY ata_date limit 1").first()
    ej = EJ(*current_ej)
    return service, client, ej


def update_data(service, client, db):
    descriptions = json.dumps({"short_description": service.short_service_description, "service_list": service.service_list})
    clients_args = {
        "store_name": client.store.name,
        "street": client.street,
        "number": client.number,
        "neighborhood": client.neighborhood,
        "city": client.city,
        "state": client.state,
        "country": client.country,
        "cep": client.cep,
        "cnpj": client.store.cnpj,
        "name": client.client.name,
        "rg": client.client.rg,
        "cpf": client.client.cpf,
        "email": client.email
    }

    db.engine.execute('''
    INSERT INTO clients (store_name, street, number, neighborhood, city, state, country, cep, cnpj, client_name, rg, cpf, email)
        SELECT %(store_name)s, %(street)s, %(number)s, %(neighborhood)s, %(city)s, %(state)s, %(country)s, %(cep)s, %(cnpj)s, %(name)s, %(rg)s, %(cpf)s, %(email)s
        WHERE NOT EXISTS (SELECT 1 FROM clients WHERE store_name=%(store_name)s AND street=%(street)s AND number=%(number)s AND neighborhood=%(neighborhood)s AND city=%(city)s AND state=%(state)s AND country=%(country)s AND cep=%(cep)s AND client_name=%(name)s AND rg=%(rg)s AND cpf=%(cpf)s AND email=%(email)s)
    ''', **clients_args)

    client_id = db.engine.execute('''
    SELECT id from clients
        WHERE store_name=%(store_name)s AND street=%(street)s AND number=%(number)s AND neighborhood=%(neighborhood)s AND city=%(city)s AND state=%(state)s AND country=%(country)s AND cep=%(cep)s AND client_name=%(name)s AND rg=%(rg)s AND cpf=%(cpf)s AND email=%(email)s
     ''', **clients_args).first()[0]

    services_args = {
        "username": session["user_id"],
        "type_contract": service.type_contract,
        "deadline": service.deadline,
        "price": service.price,
        "payment_price": service.payment_price,
        "payment": service.payment,
        "description": descriptions,
        "client_id": client_id
    }

    db.engine.execute('''
    UPDATE services
    SET 
        username = %(username)s,
        type = %(type_contract)s,
        days_to_finish = %(deadline)s,
        total_price = %(price)s,
        payment_price = %(payment_price)s,
        payment = %(payment)s,
        description = %(description)s,
        client_id = %(client_id)s
    WHERE
        type=%(type_contract)s AND
        days_to_finish=%(deadline)s AND
        total_price=%(price)s AND
        payment_price=%(payment_price)s AND
        payment=%(payment)s AND
        client_id=%(client_id)s
    ''', **services_args)

    db.engine.execute('''
    INSERT INTO services("username", "type", "days_to_finish", "total_price", "payment_price", "payment", "description", "client_id")
        SELECT %(username)s, %(type_contract)s, %(deadline)s, %(price)s, %(payment_price)s, %(payment)s, %(description)s, %(client_id)s
        WHERE NOT EXISTS(SELECT 1 FROM services WHERE username=%(username)s AND type=%(type_contract)s AND days_to_finish=%(deadline)s AND total_price=%(price)s AND payment_price=%(payment_price)s AND payment=%(payment)s AND client_id=%(client_id)s)
    ''', **services_args)

def normalize_array(array):
    return array.replace(" ", "").split(",")

def event_new_contract(client_store_name, client_name, short_description):
    start_date = datetime.datetime.now() + datetime.timedelta(days=30)
    end_date = datetime.datetime.now() + datetime.timedelta(days=30)
    title = f" {client_store_name} de {client_name}"
    description = " pelo serviço " + short_description
    model = "accept_contract"
    sapixel.new_calendar_event_from_model(model_name=model, start_date=start_date, end_date=end_date, title=title, description=description)

from functools import wraps
from flask import session, request, redirect, url_for
from enum import Enum


class Roles(Enum):
    CREATION = "CREATION"


def start_db(db):
    commands = ['''
    CREATE TABLE IF NOT EXISTS ej (
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
        name text not null,
        password text not null,
        role_id integer REFERENCES roles(id) not null
        )
    ''',
        '''
    CREATE TABLE IF NOT EXISTS clients (
        id serial primary key,
        store_name text,
        address text not null,
        cep text not null,
        cnpj text,
        client_name text not null,
        rg text not null,
        cpf text not null,
        email text not null
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
        client_id integer REFERENCES clients(id) not null
        )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS payments (
        id serial primary key,
        payment serial not null,
        price float not null,
        service_id integer REFERENCES services(id)
    )
    '''
    ]
    for command in commands:
        db.engine.execute(command)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            return f(*args, **kwargs)
        return redirect(url_for('access'))
    return decorated_function

def creation_role(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") and session.get("roles") and Roles.CREATION.name in session["roles"]:
            return f(*args, **kwargs)
        return redirect(url_for('access'))
    return decorated_function

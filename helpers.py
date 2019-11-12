from functools import wraps
from flask import session, request, redirect, url_for

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
    CREATE TABLE IF NOT EXISTS users (
        name text not null,
        password text not null
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
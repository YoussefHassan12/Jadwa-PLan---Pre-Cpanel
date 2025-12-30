# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024
"""

from flask import render_template, redirect, request, url_for, session
from apps.authentication import blueprint
from apps.config import config
import psycopg2


def check_user(usr_email,usr_pass):
    conn = None
    try:
        db_params = config()
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        sql = "SELECT id FROM public.users WHERE email = '{}' AND password = '{}';".format(usr_email,usr_pass)
        cur.execute(sql)
        results = cur.fetchall()

        cur.close()       
    except (Exception, psycopg2.DatabaseError) as error:
        return (False, error )
    finally:
        if conn is not None:
            conn.close()
    return (True, results)

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

@blueprint.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        usr_email = request.form.get('email')
        usr_pass = request.form.get('pass')
        if usr_email != '' and usr_pass != '': 
            status, results = check_user(usr_email,usr_pass)
            if  status == False:
                return render_template('accounts/login.html', msg=results)
            elif len(results) > 0:
                # print('user access: ',results[0][0])
                session['username'] = usr_email
                session['user_id'] = results[0][0]  # <-- NEW line
                # print(session['user_id'])
                return redirect(url_for('home_blueprint.index'))
            else:
                return render_template('accounts/login.html', msg="Check again your email address and password !!")
                
    return render_template('accounts/login.html', msg = 'Enter your email address and password to access your account.')

@blueprint.route('/logout')
def logout():
    session.pop("username", None)
    session.clear()
    return redirect(url_for('authentication_blueprint.login'))
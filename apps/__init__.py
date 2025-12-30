# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024
"""

from flask import Flask

# from flask_login import LoginManager
from importlib import import_module
import secrets
from datetime import timedelta
from apps.config import flask_config

# login_manager = LoginManager()

# def register_extensions(app):
    # login_manager.init_app(app)

def register_blueprints(app):
    for module_name in ('authentication', 'home'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def create_app():
    app = Flask(__name__)
    # app.secret_key = secrets.token_hex(16)

    cfg = flask_config()

    # Secret key from config file
    app.secret_key = cfg.get('secret_key', 'fallback-key-for-development')
    # Session configuration
    # Session settings
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=int(cfg.get('session_lifetime_days', 7)))
    app.config['SESSION_COOKIE_SECURE'] = True       # HTTPS only
    app.config['SESSION_COOKIE_HTTPONLY'] = True     # No JavaScript access
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CSRF protection
    register_blueprints(app)
    return app

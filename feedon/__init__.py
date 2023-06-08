import flask
import os

import feedon.blueprints.landing_pages as landing_pages
import feedon.blueprints.auth as auth

def create_app():
    app = flask.Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'helloWorld')

    app.register_blueprint(landing_pages.bp)
    app.register_blueprint(auth.bp)

    return app

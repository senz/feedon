import flask

import feedon.blueprints.static as bp_static

def create_app():
    app = flask.Flask(__name__)

    app.register_blueprint(bp_static.bp)

    return app

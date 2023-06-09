from flask import Flask, g, session, flash, redirect
import datetime
import os

import feedon.db as db
import feedon.utils as utils
import feedon.blueprints.landing_pages as landing_pages
import feedon.blueprints.auth as auth
import feedon.blueprints.feeds as feeds
import feedon.blueprints.timelines as timelines

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ['SECRET_KEY']

    app.register_blueprint(landing_pages.bp)
    app.register_blueprint(timelines.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(feeds.bp)

    @app.errorhandler(utils.AccessTokenInvalidError)
    def handle_access_token(exception):
        g.current_user = None
        session.clear()
        flash('Session expired, please log in again.')
        return redirect('/')

    @app.before_request
    def authenticate():
        if 'user_id' not in session:
            g.current_user = None
            return

        user = db.User.get_or_none(session['user_id'])
        if user is None:
            g.current_user = None
            session.clear()
            return

        g.current_user = user

    return app

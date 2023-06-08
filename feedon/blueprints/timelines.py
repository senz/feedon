from flask import Blueprint, g, render_template, redirect
import requests

import feedon.db as db
import feedon.services.timelines as timelines

bp = Blueprint('timelines', __name__, url_prefix='/timelines')

@bp.before_request
def check_auth():
    if g.current_user == None:
        return redirect('/')

@bp.route('/')
def index():
    tls = timelines.sync_timelines(g.current_user)
    return render_template('timelines/index.html', timelines=tls)

from flask import Blueprint, g, render_template, redirect, flash
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

@bp.route('/<timeline_id>/regenerate-url', methods=['POST'])
def regenerate_url(timeline_id):
    timeline = db.Timeline.select().where(
        (db.Timeline.user_id == g.current_user.id) &
        (db.Timeline.id == timeline_id)
    ).first()

    timeline.password = db.Timeline.generate_password()
    timeline.save()

    flash(f"{timeline.title} timeline's URL has been regenerated")
    return redirect('/timelines')

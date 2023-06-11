from flask import Blueprint, render_template, abort, Response
import os
import datetime

import feedon.db as db
import feedon.services.timelines as timelines

bp = Blueprint('feeds', __name__, url_prefix='/feeds')

@bp.route('/<int:user_id>/<password>/atom.xml')
def render_feed(user_id, password):
    user = db.User.get_or_none(user_id)
    if user is None:
        abort(404)

    timeline = user.timelines.where(db.Timeline.password == password).first()
    if timeline is None:
        return abort(404)

    toots = timelines.fetch_timeline(user, timeline)

    rendered_tpl = render_template(
        'feeds/atom.xml',
        user=user,
        timeline=timeline,
        toots=toots,
        last_update_time=datetime.datetime.utcnow(),
        base_url=os.environ.get('BASE_URL'),
        feed_url=f"{os.environ.get('BASE_URL')}/feeds/{user_id}/{password}/atom.xml",
    )

    resp = Response(rendered_tpl)
    resp.headers['Content-Type'] = 'application/atom+xml'
    return resp

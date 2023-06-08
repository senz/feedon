from flask import Blueprint, render_template, abort

import feedon.db as db
import feedon.services.timelines as timelines

bp = Blueprint('rss', __name__, url_prefix='/rss')

@bp.route('/<int:user_id>/<password>')
def render_feed(user_id, password):
    user = db.User.get(user_id)
    timeline = user.timelines.where(db.Timeline.password == password).first()

    if timeline is None:
        return abort(404)

    toots = timelines.fetch_timeline(user, timeline)
    import pprint; pprint.pprint(toots)
    return render_template(
        'rss/feed.xml',
        user=user,
        timeline=timeline,
        toots=toots,
    )

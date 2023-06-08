import secrets

import feedon.utils as utils
import feedon.db as db

def sync_timelines(user: db.User):
    client = user.get_client()
    remote_lists = client.get(user.instance_url('/api/v1/lists'))
    utils.validate_request(remote_lists)

    remote_ids = {l['id'] for l in remote_lists.json()}

    local_lists = db.Timeline.select().where(
        db.Timeline.user_id == user.id
    )
    local_ids = {l.remote_id for l in local_lists}

    # Delete any lists that we have stored locally but no longer exist on
    # their account
    to_delete = local_lists - remote_ids - {-1, -2, -3}
    db.Timeline.delete().where(
        db.Timeline.id.in_(to_delete) &
        db.Timeline.user_id == user.id
    )

    # Update all existing lists
    for remote_list in remote_lists.json():
        tl = db.Timeline.get_or_none(
            (db.Timeline.user_id == user.id) &
            (db.Timeline.remote_id == remote_list['id'])
        )
        if tl == None:
            tl = db.Timeline(
                remote_id=remote_list['id'],
                user_id=user.id,
                password=secrets.token_urlsafe(12),
            )

        tl.title = remote_list['title']
        tl.save()

    # Ensure we have home/local/federated feeds
    home_timeline = db.Timeline.get_or_none(
        (db.Timeline.user_id == user.id) &
        (db.Timeline.remote_id == -1)
    )
    local_timeline = db.Timeline.get_or_none(
        (db.Timeline.user_id == user.id) &
        (db.Timeline.remote_id == -2)
    )
    federated_timeline = db.Timeline.get_or_none(
        (db.Timeline.user_id == user.id) &
        (db.Timeline.remote_id == -3)
    )

    if not home_timeline:
        db.Timeline.create(
            title="Home",
            user_id=user.id,
            remote_id=-1,
            password=secrets.token_urlsafe(12),
        )
    if not local_timeline:
        db.Timeline.create(
            title="Local",
            user_id=user.id,
            remote_id=-2,
            password=secrets.token_urlsafe(12),
        )
    if not federated_timeline:
        db.Timeline.create(
            title="Federated",
            user_id=user.id,
            remote_id=-3,
            password=secrets.token_urlsafe(12),
        )

    return db.Timeline.select().where(
        db.Timeline.user_id == user.id
    )

def fetch_timeline(user: db.User, timeline: db.Timeline):
    client = user.get_client()
    
    if timeline.remote_id == -1:
        tl = client.get(user.instance_url('/api/v1/timelines/home'))
    elif timeline.remote_id == -2:
        tl = client.get(user.instance_url('/api/v1/timelines/local'))
    elif timeline.remote_id == -3:
        tl = client.get(user.instance_url('/api/v1/timelines/public'))
    else:
        tl = client.get(user.instance_url(f'/api/v1/timelines/list/{timeline.remote_id}'))

    utils.validate_request(tl)

    return tl.json()

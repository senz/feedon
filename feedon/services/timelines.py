import requests
import logging

import feedon.utils as utils
import feedon.db as db

HOME_TIMELINE_ID = -3
LOCAL_TIMELINE_ID = -2
PUBLIC_TIMELINE_ID = -1

def sync_timelines(user: db.User):
    client = user.get_client()
    logging.error(user.instance_url('/api/v1/lists'))
    remote_lists = client.get(user.instance_url('/api/v1/lists'))
    # utils.validate_and_parse_request(remote_lists)

    remote_ids = {int(l['id']) for l in remote_lists.json()}

    local_lists = db.Timeline.select().where(
        db.Timeline.user_id == user.id
    )
    local_ids = {int(l.remote_id) for l in local_lists}

    # Delete any lists that we have stored locally but no longer exist on
    # their account
    to_delete = local_ids - remote_ids - {-1, -2, -3}
    db.Timeline.delete().where(
        (db.Timeline.remote_id.in_(to_delete)) &
        (db.Timeline.user_id == user.id)
    ).execute()

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
                password=db.Timeline.generate_password(),
            )

        tl.title = remote_list['title']
        tl.save()

    # Ensure we have home/local/federated feeds
    home_timeline = db.Timeline.get_or_none(
        (db.Timeline.user_id == user.id) &
        (db.Timeline.remote_id == -3)
    )
    local_timeline = db.Timeline.get_or_none(
        (db.Timeline.user_id == user.id) &
        (db.Timeline.remote_id == -2)
    )
    federated_timeline = db.Timeline.get_or_none(
        (db.Timeline.user_id == user.id) &
        (db.Timeline.remote_id == -1)
    )

    if not home_timeline:
        db.Timeline.create(
            title="Home",
            user_id=user.id,
            remote_id=-3,
            password=db.Timeline.generate_password(),
        )
    if not local_timeline:
        db.Timeline.create(
            title="Local",
            user_id=user.id,
            remote_id=-2,
            password=db.Timeline.generate_password(),
        )
    if not federated_timeline:
        db.Timeline.create(
            title="Federated",
            user_id=user.id,
            remote_id=-1,
            password=db.Timeline.generate_password(),
        )

    return db.Timeline.select().where(
        db.Timeline.user_id == user.id
    ).order_by(db.Timeline.remote_id.asc())

def __process_status(status):
    status['content'] = status['content'].replace('<br>', '<br />')
    if 'reblog' in status and status['reblog']:
        status['reblog']['content'] = status['reblog']['content'].replace('<br>', '<br />')

    return status

def fetch_timeline(user: db.User, timeline: db.Timeline):
    client = user.get_client()
    
    if timeline.remote_id == HOME_TIMELINE_ID:
        tl = client.get(user.instance_url('/api/v1/timelines/home'))
    elif timeline.remote_id == LOCAL_TIMELINE_ID:
        tl = client.get(user.instance_url('/api/v1/timelines/public?local=1'))
    elif timeline.remote_id == PUBLIC_TIMELINE_ID:
        tl = client.get(user.instance_url('/api/v1/timelines/public'))
    else:
        tl = client.get(user.instance_url(f'/api/v1/timelines/list/{timeline.remote_id}'))

    tl = utils.validate_and_parse_request(tl)

    return [__process_status(s) for s in tl]

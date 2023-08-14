import requests
import os
from flask import Blueprint, flash, render_template, request, redirect, session, g

import feedon.db as db

bp = Blueprint('auth', __name__, url_prefix="/auth")
scope = 'read'

def generate_redirect_uri(instance_domain):
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    return f'{base_url}/auth/complete?instance_domain={instance_domain}'

@bp.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect('/')

@bp.route('/login', methods=['GET'])
def login():
    if g.current_user:
        return redirect('/')

    return render_template('auth/login.html')

@bp.route('/begin', methods=['POST'])
def begin():
    if g.current_user:
        return redirect('/')

    instance_domain = request.form.get('instance_domain', '')
    if len(instance_domain) == 0:
        flash('Instance domain is required')
        return redirect('/auth/login')

    instance = (
        db.Instance
        .get_or_none(db.Instance.instance_domain == instance_domain)
    )

    if instance is None:
        resp = requests.post(
            url=f"https://{instance_domain}/api/v1/apps",
            data={
                'client_name': 'FeedOn',
                'redirect_uris': generate_redirect_uri(instance_domain),
                'scope': scope,
                'website': os.environ.get('BASE_URL'),
            },
        )

        credentials = resp.json()
        instance = db.Instance.create(
            instance_domain=instance_domain,
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret'],
            full_response=credentials,
        )

    url = f"https://{instance.instance_domain}/oauth/authorize" \
        + f"?client_id={instance.client_id}" \
        + f"&scope=read" \
        + f"&redirect_uri={generate_redirect_uri(instance_domain)}" \
        + f"&response_type=code"

    return redirect(url)

@bp.route('/complete', methods=['GET'])
def complete():
    if g.current_user:
        return redirect('/')

    instance_domain = request.args.get('instance_domain', None)

    instance = (
        db.Instance
        .get(db.Instance.instance_domain == instance_domain)
    )

    auth_resp = requests.post(
        url=f"https://{instance.instance_domain}/oauth/token",
        data={
            'client_id': instance.client_id,
            'client_secret': instance.client_secret,
            'redirect_uri': generate_redirect_uri(instance_domain),
            'grant_type': 'authorization_code',
            'code': request.args.get('code'),
            'scope': scope,
        },
    )
    access_token = auth_resp.json()['access_token']

    verify_resp = requests.get(
        url=f"https://{instance.instance_domain}/api/v1/accounts/verify_credentials",
        headers={
            'Authorization': f'Bearer {access_token}',
        },
    )

    user_data = verify_resp.json()

    # Check to see if the user already exists
    user = db.User.get_or_none(
        (db.User.instance_domain == instance_domain) &
        (db.User.handle == user_data['username'])
    )
    if user is None:
        user = db.User.create(
            instance_domain=instance_domain,
            access_token=access_token,
            handle=user_data['username'],
        )
    else:
        user.access_token = access_token
        user.save()

    session['user_id'] = user.id

    return redirect('/')

@bp.route('/delete', methods=['GET'])
def delete_account():
    if request.args.get('confirm') != 'yes':
        return render_template('auth/delete.html')

    g.current_user.delete_account()

    session.clear()
    flash('You are now logged out and all of your account\'s data has been deleted from the database. It was fun while it lasted!')
    return redirect('/')

import requests
import os
from flask import Blueprint, flash, render_template, request, redirect

import feedon.db as db

bp = Blueprint('auth', __name__, url_prefix="/auth")
scope = 'read'

def generate_redirect_uri(instance):
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    return f'{base_url}/auth/complete?instance_domain={instance.instance_domain}'

@bp.route('/login', methods=['GET'])
def login():
    return render_template('auth/login.html')

@bp.route('/begin', methods=['POST'])
def begin():
    instance_domain = request.form.get('instance_domain', '')
    print(instance_domain)
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
                'client_name': 'Feed On This!',
                'redirect_uris': generate_redirect_uri(instance),
                'scope': scope,
                'website': 'https://localhost:5000',
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
        + f"&redirect_uri={generate_redirect_uri(instance)}" \
        + f"&response_type=code"

    return redirect(url)

@bp.route('/complete', methods=['GET'])
def complete():
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
            'redirect_uri': generate_redirect_uri(instance),
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
    user = db.User(
        instance_domain=instance_domain,
        access_token=access_token,
        handle=user_data['username'],
    )

    user.save()

    return f"logged in as {verify_resp.json()['username']}"

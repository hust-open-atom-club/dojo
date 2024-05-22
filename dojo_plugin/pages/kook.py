import sys

import requests
import logging
from CTFd.cache import cache
from CTFd.models import db
from CTFd.utils.decorators import authed_only
from CTFd.utils.user import get_current_user
from flask import Blueprint, abort, current_app, redirect, request, url_for
from itsdangerous.url_safe import URLSafeTimedSerializer
from sqlalchemy.exc import IntegrityError

from ..config import KOOK_APP_ID, KOOK_CLIENT_ID
from ..models import KookUsers
from ..utils.kook import get_kook_user_from_auth_code, get_kook_user

kook = Blueprint("kook", __name__)
kook_oauth_serializer = URLSafeTimedSerializer(
    current_app.config["SECRET_KEY"], "KOOK_OAUTH"
)

OAUTH_ENDPOINT = "https://www.kookapp.cn/app/oauth2/authorize"


@kook.route("/kook/connect")
@authed_only
def kook_connect():
    if not KOOK_CLIENT_ID:
        abort(501)

    state = kook_oauth_serializer.dumps(get_current_user().id)
    params = dict(
        id=KOOK_APP_ID,
        client_id=KOOK_CLIENT_ID,
        redirect_uri=url_for("kook.kook_redirect", _external=True),
        response_type="code",
        scope="get_user_info",
        state=state,
    )
    oauth_url = requests.Request("GET", OAUTH_ENDPOINT, params=params).prepare().url

    if not oauth_url:
        return "Failed to generate OAuth URL", 400
    return redirect(oauth_url)


@kook.route("/kook/redirect")
@authed_only
def kook_redirect():
    if not KOOK_CLIENT_ID:
        abort(501)

    state = request.args.get("state")
    code = request.args.get("code")

    if not state or not code:
        abort(400)

    try:
        redirect_user_id = kook_oauth_serializer.loads(state, max_age=60)
        print(get_current_user())
        user_id = get_current_user().id
        assert user_id == redirect_user_id, (user_id, redirect_user_id)
        kook_user = get_kook_user_from_auth_code(code)
        kook_id = kook_user["id"]
    except Exception as e:
        logging.error(f"ERROR: kook redirect failed: {e}")
        return {"success": False, "error": "kook redirect failed"}, 400

    try:
        existing_kook_user = KookUsers.query.filter_by(user_id=user_id).first()
        if not existing_kook_user:
            kook_user = KookUsers(user_id=user_id, kook_id=kook_id)
            db.session.add(kook_user)
        else:
            existing_kook_user.kook_id = kook_id
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"success": False, "error": "kook user already in use"}, 400

    return redirect("/settings#kook")

@kook.route("/kook/disconnect")
@authed_only
def kook_disconnect():
    user_id = get_current_user().id
    kook_user = KookUsers.query.filter_by(user_id=user_id).first()
    if kook_user:
        db.session.delete(kook_user)
        db.session.commit()
    return redirect("/settings#kook")

import datetime
import hashlib
import itertools
import re

from flask import Blueprint, Response, render_template, abort, url_for,request,redirect
from sqlalchemy.sql import and_, or_
from CTFd.utils.user import get_current_user
from CTFd.utils.decorators import authed_only
from CTFd.utils.security.auth import login_user, logout_user

from ..api.v1.sso_login import CASBackend
from ..models import Dojos, DojoModules, DojoChallenges
from ..config import DATA_DIR
from ..utils.scores import dojo_scores, module_scores
from ..utils.awards import get_belts, get_viewable_emojis

sso = Blueprint("pwncollege_sso", __name__)


@sso.route('/cas-login/')
def cas_login():
    ticket = request.args.get('ticket')
    casbackend = CASBackend()
    if ticket:
        user = casbackend.authenticate(ticket)
        if user:
            # 用户认证成功，创建本地会话等
            login_user(user)
            return redirect(url_for('views.settings'))
        else:
            return redirect(url_for("auth.login"))
    else:
        return redirect(CASBackend.get_login_url())


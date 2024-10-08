import datetime
import asyncio

from CTFd.cache import cache
from CTFd.models import db, Users
from flask import url_for

from .kook import KookChannels, get_kook_user, send_group_message

from ..models import Dojos, Belts, Emojis, DojoChallenges


BELT_ORDER = [ "orange", "yellow", "green", "purple", "blue", "brown", "red", "black" ]
BELT_REQUIREMENTS = {
    "orange": "welcome",
    "yellow": "pwntools",
    "green": "saffron",
    "purple": "viridian",
    "blue": "leagueconference",
}

def belt_asset(color):
    belt = color + ".png" if color in BELT_REQUIREMENTS else "white.png"
    return url_for("views.themes", path=f"img/dojo/{belt}")

def get_user_emojis(user):
    emojis = [ ]
    for dojo in Dojos.query.all():
        emoji = dojo.award and dojo.award.get('emoji', None)
        if not emoji:
            continue
        if dojo.completed(user):
            emojis.append((emoji, dojo.name, dojo.hex_dojo_id))
    return emojis

def get_belts():
    result = dict(dates={}, users={}, ranks={})
    for color in reversed(BELT_ORDER):
        result["dates"][color] = {}
        result["ranks"][color] = []

    belts = (
        Belts.query
        .join(Users)
        .filter(Belts.name.in_(BELT_ORDER), ~Users.hidden)
        .with_entities(
            Belts.date,
            Belts.name.label("color"),
            Users.id.label("user_id"),
            Users.name.label("handle"),
            Users.website.label("site"),
        )
    ).all()
    belts.sort(key=lambda belt: (-BELT_ORDER.index(belt.color), belt.date))

    for belt in belts:
        result["dates"][belt.color][belt.user_id] = str(belt.date)
        if belt.user_id not in result["users"]:
            result["users"][belt.user_id] = dict(
                handle=belt.handle,
                site=belt.site,
                color=belt.color,
                date=str(belt.date)
            )
            result["ranks"][belt.color].append(belt.user_id)

    return result

def get_viewable_emojis(user):
    result = { }
    viewable_dojo_urls = {
        dojo.hex_dojo_id: url_for("pwncollege_dojo.listing", dojo=dojo.reference_id)
        for dojo in Dojos.viewable(user=user).where(Dojos.data["type"] != "example")
    }
    emojis = (
        Emojis.query
        .join(Users)
        .filter(~Users.hidden, db.or_(Emojis.category.in_(viewable_dojo_urls.keys()), Emojis.category == None))
        .order_by(Emojis.date)
        .with_entities(
            Emojis.name,
            Emojis.description,
            Emojis.category,
            Users.id.label("user_id"),
        )
    )
    for emoji in emojis:
        result.setdefault(emoji.user_id, []).append({
            "text": emoji.description,
            "emoji": emoji.name,
            "count": 1,
            "url": viewable_dojo_urls.get(emoji.category, "#"),
        })
    return result

def update_awards(user, challenge):
    current_belts = [belt.name for belt in Belts.query.filter_by(user=user)]
    for belt, dojo_id in BELT_REQUIREMENTS.items():
        if belt in current_belts:
            continue
        dojo = Dojos.query.filter(Dojos.official, Dojos.id == dojo_id).first()
        if not (dojo and dojo.completed(user)):
            break
        db.session.add(Belts(user=user, name=belt))
        db.session.commit()
        current_belts.append(belt)

    kook_user = get_kook_user(user.id)
    dojo_challenge = DojoChallenges.query.filter_by(challenge_id=challenge.id).first()
    if kook_user and dojo_challenge:
        award = dojo_challenge.module.name
        user_mention = f"(met){kook_user.id}(met)"
        message = f"{user_mention} 恭喜 {user.name} 完成 《{award}》 ！:tada:"
        send_group_message(message, KookChannels.AWARD)

    current_emojis = get_user_emojis(user)
    for emoji,dojo_name,dojo_id in current_emojis:
        # note: the category filter is critical, since SQL seems to be unable to query by emoji!
        emoji_award = Emojis.query.filter_by(user=user, name=emoji, category=dojo_id).first()
        if emoji_award:
            continue
        db.session.add(Emojis(user=user, name=emoji, description=f"Awarded for completing the {dojo_name} dojo.", category=dojo_id))
        db.session.commit()

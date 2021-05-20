"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from .models import get_user_id

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth.user, 'index.html')
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        #my_callback_url = URL('my_callback', signer=url_signer),
        load_posts_url = URL('load_posts', signer=url_signer),
        add_post_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer),
        get_thumb_url = URL('get_thumb', signer=url_signer),
        add_thumb_url = URL('add_thumb', signer=url_signer)
    )

# This is our very first API function.
@action('load_posts')
@action.uses(url_signer.verify(), db)
def load_posts():
    rows = db(db.posts).select().as_list()
    return dict(rows=rows)

@action('add_post', method="POST")
@action.uses(url_signer.verify(), db)
def add_post():
    r = db(db.auth_user.email == get_user_email()).select().first()
    full_name = r.first_name + " " + r.last_name if r is not None else "Unknown"
    id = db.posts.insert(
        content=request.json.get('content'),
        full_name=full_name
    )
    return dict(id=id, user_id=get_user_id(),full_name=full_name)

@action('delete_post')
@action.uses(url_signer.verify(), db)
def delete_post():
    id = request.params.get('id')
    assert id is not None
    db(db.posts.id == id).delete()
    return "ok"
@action('get_thumb')
@action.uses(url_signer.verify(), db)
def get_thumb():
    post_id = request.params.get('post_id')
    assert id is not None
    row = db((db.thumbs.post_id == post_id) &
             (db.thumbs.user_id == get_user_id())).select().first()
    thumb = row.thumb if row is not None else None
    return dict(thumb=thumb)

@action('add_thumb', method="POST")
@action.uses(url_signer.verify(), db)
def add_thumb():
    post_id=request.json.get('post_id')
    request_thumb = request.json.get('bool')
    assert post_id is not None
    assert request_thumb is not None
    db.thumbs.update_or_insert(
        ((db.thumbs.post_id == post_id) & (db.thumbs.user_id == get_user_id())),
        post_id=post_id,
        user_id=get_user_id(),
        thumb=request_thumb,
        thumb=request_thumb
    )

    return dict(bool=request_thumb)

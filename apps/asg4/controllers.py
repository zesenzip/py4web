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
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash, Field
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth.user, 'index.html')
def index():
    print("User:", get_user_email())
    contacts = db(db.contact.user_email == get_user_email()).select().as_list()
    phones = db(
        (db.phone.contact_id == db.contact.id)
    ).select().as_list()
    for contact in contacts:
        s = ""
        for phone in phones:
            if(phone['phone']['contact_id'] == contact['id']):
                s = s + phone['phone']['number'] +" ("+ phone['phone']['name']+ "), "
        contact["phone_numbers"] = s.rstrip(", ")
    return dict(contacts=contacts,
                url_signer=url_signer)


@action('edit_contact/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'edit.html')
def edit(contact_id=None):
    assert contact_id is not None
    # We read the contact being edited from the db.
    # p = db(db.contact.id == contact_id).select().first()
    p = db.contact[contact_id]
    if p is None:
        # Nothing found to be edited!
        redirect(URL('index'))
    if p.user_email != get_user_email():
        redirect(URL('index'))
    # Edit form: it has record=
    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # The update already happened!
        redirect(URL('index'))
    return dict(form=form)

@action('add_contact', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'edit.html')
def add_contact():
    # Insert form: no record= in it.
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We simply redirect; the insertion already happened.
        redirect(URL('index'))
    # Either this is a GET request, or this is a POST but not accepted = with errors.
    return dict(form=form)

@action('delete_contact/<contact_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_contact(contact_id=None):
    assert contact_id is not None
    contact = db.contact[contact_id]
    db(db.contact.id == contact_id).delete()
    redirect(URL('index'))

@action('edit_phones/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'edit_phones.html')
def edit_phones(contact_id=None):
    assert contact_id is not None
    # We read the contact being edited from the db.
    # p = db(db.contact.id == contact_id).select().first()
    p = db(db.contact.id == contact_id).select().first()
    if p is None:
        # Nothing found to be edited!
        redirect(URL('index'))
    if p.user_email != get_user_email():
        redirect(URL('index'))

    phones = db(
        (db.phone.contact_id == contact_id)
    ).select()

    return dict(phones=phones,contact_id=contact_id,url_signer=url_signer)

@action('add_phone/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_phone.html')
def add_phone(contact_id=None):
    assert contact_id is not None
    # We read the contact being edited from the db.
    # p = db(db.contact.id == contact_id).select().first()
    p = db(db.contact.id == contact_id).select().first()
    if p is None:
        # Nothing found to be edited!
        redirect(URL('index'))
    if p.user_email != get_user_email():
        redirect(URL('index'))
    form = Form([Field('number', 'string'),Field('name', 'string')],
                csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        db.phone.insert(
            contact_id=contact_id,
            number=form.vars["number"],
            name=form.vars["name"]
        )
        redirect(URL('edit_phones',contact_id))
    return dict(form=form, first=p.first, last=p.last)

@action('edit_phone/<contact_id:int>/<phone_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_phone.html')
def edit_phones(contact_id=None, phone_id=None):
    assert contact_id is not None
    assert phone_id is not None
    # We read the phone being edited from the db.
    p = db(db.phone.id == phone_id).select().first()
    b = db(db.contact.id == contact_id).select().first()
    if p is None or b is None:
        # Nothing found to be edited!
        redirect(URL('edit_phones',contact_id))
    if b.user_email != get_user_email():
        redirect(URL('edit_phones',contact_id))
    if (b.id != p.contact_id):
        redirect(URL('edit_phones',contact_id))
    form = Form(db.phone, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We simply redirect; the insertion already happened.
        redirect(URL('edit_phones',contact_id))
    return dict(form=form, first=b.first, last=b.last, url_signer=url_signer)

@action('delete_phone/<contact_id:int>/<phone_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_phone(contact_id=None, phone_id=None):
    assert contact_id is not None
    assert phone_id is not None
    phone = db.phone[phone_id]
    db(db.phone.id == phone_id).delete()
    redirect(URL('edit_phones',contact_id))
"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()
def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
db.define_table('posts',
                Field('content', type="string", requires=IS_NOT_EMPTY),
                Field('user_id', type="reference auth_user", default=get_user_id),
                Field('full_name', type="string", requires=IS_NOT_EMPTY)
)
db.define_table('thumbs',
                Field('post_id', type="reference posts"),
                Field('user_id', type="reference auth_user", default=get_user_id),
                Field('full_name', type="string"),
                Field('thumb',type="boolean",default=None)
)
db.commit()

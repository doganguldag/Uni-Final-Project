
from flask_login import current_user
from wtforms import validators
from flask import redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))
    
class UserModelView(MyModelView):
    column_exclude_list = ["password_hash"]
    form_excluded_columns = ["password_hash"]
    column_searchable_list = ["username", "email"]

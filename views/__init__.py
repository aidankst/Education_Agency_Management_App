from flask import Blueprint

bp_views = Blueprint('views', __name__)

from . import index

bp_views.register_blueprint(index.bp_index, url_prefix='/')

from . import accounts

bp_views.register_blueprint(accounts.bp_accounts, url_prefix='/')

from . import admin

bp_views.register_blueprint(admin.bp_admin, url_prefix='/admin')

from . import client

bp_views.register_blueprint(client.bp_client, url_prefix='/client')
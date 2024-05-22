import os
import sys
from flask import Flask, render_template, flash
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, AnonymousUserMixin
from dotenv import load_dotenv
from models import db, User, Steps


load_dotenv()

now = datetime.now()
current_date = now.strftime('%Y-%m-%d %H:%M:%S')


admin_email = os.getenv('admin_email')
admin_password = os.getenv('admin_password')
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS')

print(sys.path)

app = Flask(__name__, instance_relative_config=False)

app.config.from_pyfile('config.py')

app.debug = True

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


    user_id = User.generate_user_id()
       
    if not User.check_exists(email=admin_email):
        if User.add_new_user(user_id, 'Aidan', admin_email, admin_password, 'admin', 'admin'):
            flash('You have successfully registered. Please check your email to login.', 'success')
        else:
            flash('There is an error creating an account.', 'danger')

    if not db.session.query(Steps).filter_by(id=1).first():
        steps = Steps(id=1, name='Client needs to fill personal forms (Account Settings > Personal Form)')
        db.session.add(steps)
        db.session.commit()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/master/404.html'), 404
    
@app.context_processor
def inject_datetime():
    return {'datetime': datetime}


class MyAnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'views.bp_accounts.login'
login_manager.anonymous_user = MyAnonymousUser

@login_manager.user_loader
def load_user(user_id):
    user = db.session.query(User).get(user_id)
    return user

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from views import bp_views

app.register_blueprint(bp_views)


if __name__ == '__main__':
    app.run(debug=True)
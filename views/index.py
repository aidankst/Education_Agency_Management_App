from flask import Blueprint, render_template, request, flash, redirect
from emails import send_contact_email
from flask_login import current_user

bp_index = Blueprint('bp_index', __name__)

majorTypes = ['bachelor', 'master']
majors = ['medicine', 'computer science', 'business related', 'others']

@bp_index.route('/')
def index():
    return render_template('/master/index.html')

@bp_index.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        subject = request.form['subject']
        message = request.form['message']
        print('Hello')
        try:
            send_contact_email(name, email, phone, address, subject, message)
            flash('Your message has been sent!', 'success')
            return redirect('/contact')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/master/contact.html', current_user=current_user, logged_in=False)


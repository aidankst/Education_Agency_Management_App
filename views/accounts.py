from flask import Blueprint, render_template, redirect, request, flash
from models import db, User, Verification, Client
from emails import forgot_password_email, personal_form_change_email
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from functools import wraps

bp_accounts = Blueprint('bp_accounts', __name__)

now = datetime.now()
current_date = now.strftime('%Y-%m-%d %H:%M:%S')

def requires_roles(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            # Check if role is not set or if the role is not allowed
            if not current_user.is_authenticated or current_user.role not in roles:
                return render_template('/master/unauthorized.html', logged_in=True)
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@bp_accounts.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            user_id = request.form['id']
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']

            if not User.check_exists(email):
                if not db.session.query(User).filter_by(id=user_id).first():
                    if User.add_new_user(user_id, name, email, password, role, ''):
                        flash('You have successfully registered. Please check your email to login.', 'success')
                    else:
                        flash('There is an error creating an account.', 'danger')
                else:
                    flash('There is an account with another email.', 'danger')
            else:
                flash('Email already exists', 'danger')
        return render_template('/auth/register.html', logged_in=False)
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
        return render_template('/auth/register.html', logged_in=False)
    
@bp_accounts.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            if email and password:
                user = User.query.filter_by(email=email).first()
                if user and User.check_password(email, password):
                    if not user.suspended:
                        if user.active:
                            login_user(user)
                            user.last_login_at = current_date
                            user.login_count += 1
                            user.last_login_ip = request.remote_addr
                            db.session.commit()
                            if user.role == 'admin':
                                return redirect('/admin/dashboard')
                            elif user.role == 'client':
                                client = Client.query.filter_by(id=current_user.id).first()
                                if not client:
                                    client = Client(id=current_user.id, steps_id=1, user=user)
                                    db.session.add(client)
                                    db.session.commit()
                                return redirect('/client/dashboard')
                        else:
                            return render_template('/auth/verify_account.html', user_id=user.id, logged_in=False)
                    else:
                        flash('Your account has been suspended.', 'danger')
                else:
                    flash('Invalid email or password', 'danger')
            else:
                flash('Email and password are required', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/auth/login.html', logged_in=False)

@bp_accounts.route('/verify_account/<int:user_id>', methods=['GET', 'POST'])
def verify_account(user_id):
    if request.method == 'POST':
        try:
            verification_code = request.form['verification_code']
            user = User.query.filter_by(id=user_id).first()
            print(user.verification.code)
            if check_password_hash(user.verification.code, str(verification_code)):
                user.active = True
                user.confirmed_at = current_date
                db.session.add(user)
                db.session.delete(user.verification)
                db.session.commit()
                login_user(user)

                user.last_login_at = current_date
                user.login_count += 1
                user.last_login_ip = request.remote_addr
                db.session.commit()
                if user.role == 'admin':
                    return redirect('/admin/dashboard')
                elif user.role == 'client':
                    client = Client.query.filter_by(id=current_user.id).first()
                    if not client:
                        client = Client(id=current_user.id, steps_id=1, user=user)
                        db.session.add(client)
                        db.session.commit()
                    return redirect('/client/dashboard')
            else:
                flash('Invalid verification code', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/auth/verify_account.html', user_id=user.id, logged_in=False)


@bp_accounts.route('/settings')
@login_required
def settings():
    return redirect('/account_details')


@bp_accounts.route('/account_details', methods=['GET', 'POST'])
@login_required
def account_details():
    if request.method == 'POST':
        try:
            name = request.form['name']
            user = User.query.filter_by(id=current_user.id).first()
            user.username = name
            db.session.add(user)
            db.session.commit()
            flash('Account details updated successfully','success')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/master/account_details.html', current_user=current_user, logged_in=True)

@bp_accounts.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        try:
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            if new_password != confirm_password:
                flash('Passwords do not match', 'danger')
            else:
                user = User.query.filter_by(id=current_user.id).first()
                if User.check_password(user.email, old_password):
                    user.password = User.create_password(new_password)
                    db.session.add(user)
                    db.session.commit()
                    flash('Password changed successfully', 'success')
                else:
                    flash('Invalid old password', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/master/change_password.html', current_user=current_user, logged_in=True)

@bp_accounts.route('/change_data', methods=['GET', 'POST'])
@login_required
def change_data():
    if request.method == 'POST':
        try:
            id = request.form['id']
            name = request.form['name']
            national_id = request.form['national_id']
            phone = request.form['phone']
            date_of_birth = request.form['date_of_birth']

            passport_num = request.form['passport_num']
            passport_type = request.form['passport_type']
            passport_issue_date = request.form['passport_issue_date']
            passport_expiry_date = request.form['passport_expiry_date']
            place_of_birth = request.form['place_of_birth']
            passport_country = request.form['passport_country']

            street = request.form['street']
            house_number = request.form['house_number']
            township = request.form['township']
            postcode = request.form['postcode']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']

            father_name = request.form['father_name']
            father_id = request.form['father_id']
            mother_name = request.form['mother_name']
            mother_id = request.form['mother_id']

            major_type = request.form['major_type']
            major_name = request.form['major_name']
            priority_uni1 = request.form['priority_uni1']
            priority_uni2 = request.form['priority_uni2']
            priority_uni3 = request.form['priority_uni3']

            institution = request.form['institution']
            institution_city = request.form['institution_city']
            institution_country = request.form['institution_country']
            general_description = request.form['general_description']

            user = db.session.query(User).filter_by(id=id).first()
            client = db.session.query(Client).filter_by(id=id).first()

            user.username = name

            if client:
                user.client.national_id = national_id
                user.client.steps_id = 2
                user.client.phone = phone
                if date_of_birth:
                    user.client.date_of_birth = date_of_birth
                user.client.passport_num = passport_num
                user.client.passport_type_id = passport_type
                if passport_issue_date:
                    user.client.passport_issue_date = passport_issue_date
                if passport_expiry_date:
                    user.client.passport_expiry_date = passport_expiry_date
                user.client.place_of_birth = place_of_birth
                user.client.passport_country = passport_country
                user.client.street = street
                user.client.house_number = house_number
                user.client.township = township
                user.client.postcode = postcode
                user.client.city = city
                user.client.state = state
                user.client.country = country
                user.client.father_name = father_name
                user.client.father_id = father_id
                user.client.mother_name = mother_name
                user.client.mother_id = mother_id
                user.client.major_type = major_type
                user.client.major_name = major_name
                user.client.priority_uni1 = priority_uni1
                user.client.priority_uni2 = priority_uni2
                user.client.priority_uni3 = priority_uni3
                user.client.institution = institution
                user.client.institution_city = institution_city
                user.client.institution_country = institution_country
                user.client.general_description = general_description
                
            else:
                client = Client(user=user, id=id, steps_id=2, national_id=national_id, phone=phone, date_of_birth=date_of_birth, passport_num=passport_num, passport_type_id=passport_type, passport_issue_date=passport_issue_date, passport_expiry_date=passport_expiry_date, place_of_birth=place_of_birth, passport_country=passport_country, street=street, house_number=house_number, township=township, postcode=postcode, city=city, state=state, country=country, father_name=father_name, father_id=father_id, mother_name=mother_name, mother_id=mother_id, major_type=major_type, major_name=major_name, priority_uni1=priority_uni1, priority_uni2=priority_uni2, priority_uni3=priority_uni3, institution=institution, institution_city=institution_city, institution_country=institution_country, general_description=general_description)
                db.session.add(client)
            
            db.session.commit()
            personal_form_change_email(user.username, user.email)
            
        except Exception as e:
            flash(f'Form submission failed. Error: {e}', 'danger')
    if current_user.role == 'admin':
        flash('Form submitted successfully!','success')
        return redirect('/admin/find_user')
    else:
        flash('Form submitted successfully!','success')
        return redirect('/client/personal_form')
    
@bp_accounts.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            email = request.form['email']
            user = User.query.filter_by(email=email).first()
            if user:
                user.active = False

                user_id = user.id
                new_password = User.generate_random_password(12)
                user.password = User.create_password(new_password)
                verification_code = Verification.generate_verification_code()

                if not user.verification:
                    verification = Verification(id=user_id, code=User.create_password(str(verification_code)), user=user)
                    db.session.add(verification)
                else:
                    user.verification.code = User.create_password(str(verification_code))
                db.session.commit()
                
                forgot_password_email(name=user.username, email=email, password=new_password, verification_code=verification_code)
                flash('Please check your email to login.', 'info')
                return redirect('/login')
            else:
                flash('Email does not exist', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/auth/forgot_password.html', logged_in=False)

@bp_accounts.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
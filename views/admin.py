from flask import Blueprint, render_template, redirect, request, flash, session
from flask_login import current_user, login_required
from .accounts import requires_roles
from models import db, User, Client, PassportType, Invoice, Steps, Payment, Service, Package, Item, Profit
from sqlalchemy import asc, func
from datetime import datetime, timedelta
from emails import send_invoice_email, new_step_add_email, add_remark_email, suspend_user_email, delete_user_email, send_profit_email, payment_record_email, payment_record_email, invoice_delete_email, sell_package_email
from .index import majors, majorTypes

bp_admin = Blueprint('bp_admin', __name__)


@bp_admin.route('/dashboard')
@login_required
@requires_roles('admin')
def dashboard():
    try:
    # generate_invoice_pdf(202405011268013)
        client_count = db.session.query(Client).count()
        total_amount_eur = db.session.query(func.sum(Invoice.amount_eur)).filter(func.extract('year', Invoice.date) == datetime.now().year, Invoice.status == 'paid').scalar()
        total_amount_mmk = db.session.query(func.sum(Invoice.amount_mmk)).filter(func.extract('year', Invoice.date) == datetime.now().year, Invoice.status == 'paid').scalar()
        profits = Profit.query.filter(func.extract('year', Invoice.date) == datetime.now().year).all()
        packages = Package.query.order_by(asc(Package.id)).all()
        steps = Steps.query.order_by(asc(Steps.id)).all()
        clients = Client.query.order_by(asc(Client.id)).all()

        if profits:
            leveling_profit_eur = 0
            leveling_profit_mmk = 0
            ayes_profit_eur = 0
            ayes_profit_mmk = 0

            for profit in profits:
                leveling_profit_eur += profit.leveling_profit_eur
                leveling_profit_mmk += profit.leveling_profit_mmk
                ayes_profit_eur += profit.ayes_profit_eur
                ayes_profit_mmk += profit.ayes_profit_mmk
            
            profits = {
                'leveling_profit_eur': leveling_profit_eur,
                'leveling_profit_mmk': leveling_profit_mmk,
                'ayes_profit_eur': ayes_profit_eur,
                'ayes_profit_mmk': ayes_profit_mmk
            }
        return render_template('/admin/dashboard.html', clients=clients, client_count=client_count, steps=steps, total_amount_eur=total_amount_eur, total_amount_mmk=total_amount_mmk, profits=profits, packages=packages, current_user=current_user, logged_in=True)
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
        return redirect('/login')

@bp_admin.route('/account_management', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def account_management():
    return redirect('/admin/all_users')

@bp_admin.route('/all_users', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def all_users():
    try:
        users = User.query.order_by(asc(User.role)).all()
        return render_template('/admin/account_management/all_users.html', users=users, current_user=current_user, logged_in=True)
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
        return redirect('/login')


@bp_admin.route('/register_new_user', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def register_new_user():
    if request.method == 'POST':
        try:
            user_id = request.form['id']
            name = request.form['name']
            email = request.form['email']
            role = request.form['role']

            password = User.generate_random_password(12)

            if not User.check_exists(email):
                if not db.session.query(User).filter_by(id=user_id).first():
                    if User.add_new_user(user_id, name, email, password, role, 'admin'):
                        flash('You have successfully registered.', 'success')
                    else:
                        flash('There is an error creating an account.', 'danger')
                else:
                    flash('There is an account with another email', 'danger')
            else:
                flash('Email already exists', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/account_management/register_new_user.html', current_user=current_user, logged_in=True)

@bp_admin.route('/find_user', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def find_user():
    if request.method == 'POST':
        try:
            user_id = request.form['id']
            if db.session.query(User).filter_by(id=user_id).first():
                return redirect(f'/admin/edit_user/{user_id}')
            else:
                flash(f'There is no account with ID: {user_id}.', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/account_management/find_user.html', current_user=current_user, logged_in=True)

@bp_admin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def activate_user(user_id):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        client = db.session.query(Client).filter_by(id=user_id).first()
        passport_types = PassportType.query.order_by(asc(PassportType.id)).all()
        steps = Steps.query.order_by(asc(Steps.id)).all()
        return render_template('/admin/account_management/edit_user.html', user=user, client=client, passport_types=passport_types, majors=majors, majorTypes=majorTypes, steps=steps, current_user=current_user, logged_in=True)
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
        return redirect('/admin/find_user')
    

@bp_admin.route('/add_step_to_client/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_step_to_client(id):
    if request.method == 'POST':
        try:
            step_id = request.form['step_id']
            client = db.session.query(Client).filter_by(id=id).first()
            new_step_add_email(client.user.username, client.user.email, client.steps_id, step_id)
            client.steps_id = step_id
            db.session.commit()
            flash('Step added successfully','success')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
        return redirect(f'/admin/edit_user/{id}')

@bp_admin.route('/add_remark/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_remark(id):
    if request.method == 'POST':
        try:
            remark = request.form['remark']
            user = db.session.query(User).filter_by(id=id).first()
            user.remark = remark
            db.session.commit()
            if remark != '':
                add_remark_email(user.username, user.email)
            flash('Remark added successfully','success')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect(f'/admin/edit_user/{id}')

@bp_admin.route('/suspend_user', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def suspend_user():
    if request.method == 'POST':
        try:
            user_id = request.form['id']
            user = db.session.query(User).filter_by(id=user_id).first()
            if user:
                user.active = False
                user.suspended = True
                if user.verification:
                    db.session.delete(user.verification)
                db.session.commit()
                suspend_user_email(user.username, user.email)
                flash('User suspended successfully','success')
            else:
                flash('User does not exist', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/account_management/suspend_user.html', current_user=current_user, logged_in=True)

@bp_admin.route('/delete_user', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def delete_user():
    if request.method == 'POST':
        try:
            user_id = request.form['id']
            user = db.session.query(User).filter_by(id=user_id).first()
            if user:
                if user.client:
                    if user.client.invoices:
                        for invoice in user.client.invoices:
                            if invoice.payment:
                                db.session.delete(invoice.payment)
                                db.session.commit()
                            db.session.delete(invoice)
                            db.session.commit()
                    if user.client.packages:
                        for package in user.client.packages:
                            user.client.packages.remove(package)
                            db.session.commit()
                    # client = db.session.query(Client).filter_by(id=user_id).first()
                    db.session.delete(user.client)
                    db.session.commit()
                if user.verification:
                    # verification = db.session.query(Verification).filter_by(id=user_id).first()
                    db.session.delete(user.verification)
                    db.session.commit()
                db.session.delete(user)
                db.session.commit()
                delete_user_email(user.username, user.email)
                flash('User deleted successfully','success')
            else:
                flash('User does not exist', 'danger')
        except Exception as e:
            flash(f'There is an error deleting the user: {e}', 'danger')
    return render_template('/admin/account_management/delete_user.html', current_user=current_user, logged_in=True)

@bp_admin.route('/add_google_drive', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_google_drive():
    if request.method == 'POST':
        try:
            user_id = request.form['user_id']
            google_drive = request.form['google_drive']
            user = db.session.query(User).filter_by(id=user_id).first()

            if user:
                user.google_drive = google_drive
                db.session.commit()
                flash('Google drive added successfully','success')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/dashboard')

@bp_admin.route('/passport_types')
@login_required
@requires_roles('admin')
def passport_types():
    try:
        passport_types = PassportType.query.order_by(asc(PassportType.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/account_management/passport_types.html', passport_types=passport_types, current_user=current_user, logged_in=True)



@bp_admin.route('/steps')
@login_required
@requires_roles('admin')
def steps():
    try:
        steps = Steps.query.order_by(asc(Steps.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/account_management/steps.html', steps=steps, current_user=current_user, logged_in=True)

@bp_admin.route('/add_new_passport_type', methods=['GET','POST'])
@login_required
@requires_roles('admin')
def add_new_passport_type():
    if request.method == 'POST':
        try:
            name = (request.form['name']).upper()
            if not db.session.query(PassportType).filter_by(name=name).first():
                passport_type = PassportType(name=name)
                db.session.add(passport_type)
                db.session.commit()
                flash('Passport type added successfully','success')
            else:
                flash('Passport type already exists', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/passport_types')

@bp_admin.route('/add_new_step', methods=['GET','POST'])
@login_required
@requires_roles('admin')
def add_new_step():
    if request.method == 'POST':
        try:
            id = request.form['id']
            name = request.form['name']
            if not db.session.query(Steps).filter_by(id=id).first():
                step = Steps(id=id, name=name)
                db.session.add(step)
                db.session.commit()
                flash('Step added successfully','success')
            else:
                flash(f'Step {id} already exists', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/steps')

@bp_admin.route('/remove_passport_type', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def remove_passport_type():
    if request.method == 'POST':
        try:
            id = request.form['id']
            passport_type = db.session.query(PassportType).filter_by(id=id).first()
            if passport_type:
                db.session.delete(passport_type)
                db.session.commit()
                flash('Passport type deleted successfully','success')
            else:
                flash('Passport type does not exist', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/passport_types')

@bp_admin.route('/remove_step', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def remove_step():
    if request.method == 'POST':
        try:
            id = request.form['id']
            step = db.session.query(Steps).filter_by(id=id).first()
            if step:
                db.session.delete(step)
                db.session.commit()
                flash('Step deleted successfully','success')
            else:
                flash('Step does not exist', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/steps')


@bp_admin.route('/payments', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def payments():
    return redirect('/admin/invoices')

@bp_admin.route('/invoices', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def invoices():
    try:
        unpaid_invoices = db.session.query(Invoice).filter(Invoice.status == 'unpaid').order_by(asc(Invoice.id)).all()
        paid_invoices = db.session.query(Invoice).filter(Invoice.status == 'paid').order_by(asc(Invoice.id)).all()
        # payments = db.session.query(Payment).order_by(asc(Payment.id)).all()
        clients = db.session.query(Client).order_by(asc(Client.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/payments/invoices.html', clients=clients, unpaid_invoices=unpaid_invoices, paid_invoices=paid_invoices, current_user=current_user, logged_in=True)

@bp_admin.route('/invoice_second_step', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def invoice_second_step():
    if request.method == 'GET':
        try:
            user_id = request.args.get('user_id')
            date = request.args.get('date')
            terms = int(request.args.get('terms'))

            date = datetime.strptime(date, '%Y-%m-%d')
            deadline = date + timedelta(days=terms)
            print(date)
            client = db.session.query(Client).filter_by(id=user_id).first()
            if client.packages:
                for package in client.packages:
                        package_id = package.id

                id = Invoice.generate_invoice_id(date, package_id, user_id)

                if id:
                    package = db.session.query(Package).filter_by(id=package_id).first()

                    session['invoice'] = {
                        'id': id,
                        'client_id': user_id,
                        'date': date,
                        'terms': terms,
                        'deadline': deadline,
                    }
                    db.session.commit()
                    return render_template('/admin/payments/invoice_second_step.html', client=client, package=package, current_user=current_user, logged_in=True)
                else:
                    flash('Invoice already exists', 'danger')
            else:
                flash('Client does not have any packages', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    else:
        flash('Please enter a valid invoice')
    return redirect('/admin/invoices')
    
@bp_admin.route('/preview_invoice', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def preview_invoice():
    if request.method == 'GET':
        try:
            date = request.args.get('date')
            deadline = request.args.get('deadline')
            discount = request.args.get('discount')
            if not discount:
                discount = 0

            client = db.session.query(Client).filter_by(id=session['invoice']['client_id']).first()
            items = request.args.getlist('items')

            item_list = []
            total = 0

            for item in items:
                item = db.session.query(Item).filter_by(id=int(item)).first()
                item_list.append(item)
                total += item.amount_eur
            
            total -= float(discount)
            print(session['invoice'])

            session['invoice'] = {
                'id': session['invoice']['id'],
                'client_id': session['invoice']['client_id'],
                'date': datetime.strptime(date, '%Y-%m-%d'),
                'terms': session['invoice']['terms'],
                'deadline': datetime.strptime(deadline, '%Y-%m-%d'),
                'discount': float(discount),
                'amount_eur': total,
            }
            session['items'] = items
            db.session.commit()
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/payments/preview_invoice.html', client=client, items=item_list, current_user=current_user, logged_in=True)
    
@bp_admin.route('/send_invoice', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def send_invoice():
    try:
        invoice_data = session['invoice']
        invoice = Invoice(id=int(invoice_data['id']), user_id=int(invoice_data['client_id']), discount=invoice_data['discount'], amount_eur=invoice_data['amount_eur'], date=invoice_data['date'], issuer=current_user.username, deadline=invoice_data['deadline'], status='unpaid', client=db.session.query(Client).filter_by(id=int(invoice_data['client_id'])).first())
        db.session.add(invoice)
        db.session.commit()
        client = db.session.query(Client).filter_by(id=invoice.user_id).first()

        for item_id in session['items']:
            invoice_item = db.session.query(Item).filter_by(id=int(item_id)).first()
            invoice.items.append(invoice_item)
            db.session.commit()

        # invoice_path = generate_invoice_pdf(invoice.id)
        send_invoice_email(client, invoice)
        session.pop('invoice', None)
        session.pop('items', None)
        db.session.commit()
        flash('Invoice sent successfully','success')
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/invoices')


@bp_admin.route('/pay_invoice/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def pay_invoice(id):
    if request.method == 'POST':
        try:
            invoice = db.session.query(Invoice).filter_by(id=id).first()
            leveling_percent = 70
            ayes_percent = 30
            if invoice.exchange_rate is None:
                exchange_rate = float(request.form['exchange_rate'])
                invoice.exchange_rate = exchange_rate
                invoice.amount_mmk = round(float(invoice.amount_eur * exchange_rate), 2)
                db.session.commit()
                flash('MMK calculation success!','success')
            else:
                payment = Payment(invoice=invoice, id=id, date=invoice.date, payment_registerer=current_user.username)
                db.session.add(payment)
                invoice.status = 'paid'
                service_fees_eur = 0
                db.session.commit()

                for item in invoice.items:
                    if not item.extra_charges:
                        service_fees_eur += item.amount_eur

                service_fees_mmk = service_fees_eur * invoice.exchange_rate

                leveling_profit_eur = round(float((leveling_percent / 100) * service_fees_eur), 2)
                leveling_profit_mmk = round(float((leveling_percent / 100) * service_fees_mmk), 2)
                ayes_profit_eur = round(float((ayes_percent / 100) * service_fees_eur), 2)
                ayes_profit_mmk = round(float((ayes_percent / 100) * service_fees_mmk), 2)

                profit = Profit(id=id, date=payment.date, leveling_profit_eur=leveling_profit_eur, leveling_profit_mmk=leveling_profit_mmk, ayes_profit_eur=ayes_profit_eur, ayes_profit_mmk=ayes_profit_mmk)
                db.session.add(profit)

                db.session.commit()
                send_profit_email(invoice.client.user.username, profit)
                payment_record_email(invoice.client.user.username, invoice.client.user.email, invoice.id)
                flash('Invoice paid successfully','success')
            
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/invoices')

@bp_admin.route('/delete_invoice/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def delete_invoice(id):
    try:
        invoice = db.session.query(Invoice).filter_by(id=id).first()
        if invoice:
            if invoice.payment:
                db.session.delete(invoice.payment)
                db.session.commit()
            profit = db.session.query(Profit).filter_by(id=id).first()
            invoice_delete_email(invoice.client.user.username, invoice.client.user.email, invoice.id)
            db.session.delete(invoice)
            if profit:
                db.session.delete(profit)
            db.session.commit()
            flash('Invoice deleted successfully','success')
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/invoices')

@bp_admin.route('/sell_package', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def sell_package():
    try:
        packages = db.session.query(Package).order_by(asc(Package.id)).all()
        clients = db.session.query(Client).order_by(asc(Client.id)).all()

        if request.method == 'POST':
            client_id = request.form['user_id']
            package_id = request.form['package_id']
            client = db.session.query(Client).filter_by(id=client_id).first()
            package = db.session.query(Package).filter_by(id=package_id).first()
            
            if not package in client.packages:
                print('Enter')
                client.packages.append(package)
                client.contract_date = datetime.now()
                db.session.commit()
                sell_package_email(client.user.username, client.user.email, package)
                flash('Package added successfully','success')
            else:
                flash('Package already exists', 'danger')
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/admin/payments/sell_package.html', clients=clients, packages=packages, current_user=current_user, logged_in=True)

@bp_admin.route('/remove_package_from_user', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def remove_package_from_user():
    if request.method == 'POST':
        try:
            client_id = request.form['user_id']
            package_id = request.form['package_id']
            client = db.session.query(Client).filter_by(id=client_id).first()
            package = db.session.query(Package).filter_by(id=package_id).first()
            client.packages.remove(package)
            client.contract_date = None
            db.session.commit()
            flash('Package removed successfully','success')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/sell_package')


@bp_admin.route('/services')
@login_required
@requires_roles('admin')
def services():
    try:
        services = db.session.query(Service).order_by(asc(Service.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('admin/payments/services.html', services=services, current_user=current_user, logged_in=True)

@bp_admin.route('/add_new_service', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_new_service():
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            if not db.session.query(Service).filter_by(name=name).first():
                service = Service(name=name, description=description)
                db.session.add(service)
                db.session.commit()
                flash('Service added successfully','success')
            else:
                flash(f'Service {id} already exists', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/services')

@bp_admin.route('/delete_service/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def remove_service(id):
    try:
        service = db.session.query(Service).filter_by(id=id).first()
        if service:
            db.session.delete(service)
            db.session.commit()
            flash('Service deleted successfully','success')
        else:
            flash('Service does not exist', 'danger')
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/services')
    
@bp_admin.route('/packages')
@login_required
@requires_roles('admin')
def packages():
    try:
        packages = db.session.query(Package).order_by(asc(Package.id)).all()
        services = db.session.query(Service).order_by(asc(Service.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('admin/payments/packages.html', packages=packages, services=services, current_user=current_user, logged_in=True)

@bp_admin.route('/add_new_package', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_new_package():
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            amount = request.form['amount']
            services = request.form.getlist('services')
            if not db.session.query(Package).filter_by(name=name).first():
                package = Package(name=name, description=description, amount_eur=amount)
                db.session.add(package)
                db.session.commit()
                for service in services:
                    package.services.append(db.session.query(Service).filter_by(id=int(service)).first())
                db.session.commit()
                flash('Package added successfully','success')
            else:
                flash(f'Package {name} already exists', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/packages')

@bp_admin.route('/add_service_to_package', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_service_to_package():
    if request.method == 'POST':
        try:
            package_id = request.form['package_id']
            service_id = request.form['service_id']
            package = db.session.query(Package).filter_by(id=int(package_id)).first()
            service_exists = False
            for service in package.services:
                if service.id == int(service_id):
                    service_exists = True
                    break
            if not service_exists:
                package.services.append(db.session.query(Service).filter_by(id=int(service_id)).first())
                db.session.commit()
                flash('Service added successfully','success')
            else:
                flash(f'Service already exists in package {package.name}', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/packages')

@bp_admin.route('/remove_service_from_package', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def remove_service_from_package():
    if request.method == 'POST':
        try:
            package_id = request.form['package_id']
            service_id = request.form['service_id']
            package = db.session.query(Package).filter_by(id=int(package_id)).first()
            service_exists = False
            for service in package.services:
                if service.id == int(service_id):
                    service_exists = True
                    break
            if service_exists:
                package.services.remove(db.session.query(Service).filter_by(id=int(service_id)).first())
                db.session.commit()
                flash('Service removed successfully','success')
            else:
                flash('Service does not exist in package.', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/packages')

@bp_admin.route('/delete_package/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def remove_package(id):
    try:
        package = db.session.query(Package).filter_by(id=id).first()
        if package:
            db.session.delete(package)
            db.session.commit()
            flash('Package deleted successfully','success')
        else:
            flash('Package does not exist', 'danger')
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/packages')

@bp_admin.route('/items')
@login_required
@requires_roles('admin')
def items():
    try:
        items = db.session.query(Item).order_by(asc(Item.id)).all()
        packages = db.session.query(Package).order_by(asc(Package.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('admin/payments/items.html', items=items, packages=packages, current_user=current_user, logged_in=True)

@bp_admin.route('/add_new_item', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_new_item():
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form['description']
            amount = request.form['amount']
            package_id = request.form['package_id']
            extra_charges = request.form['extra_charges']

            if extra_charges == 'true':
                extra_charges = True
            else:
                extra_charges = False

            item = db.session.query(Item).filter_by(name=name).first()
            package = db.session.query(Package).filter_by(id=int(package_id)).first()

            if package:
                if item in package.items:
                    flash(f'Item {name} already exists', 'danger')
                else:
                    item = Item(name=name, description=description, amount_eur=amount, package_id=package_id, package=package, extra_charges=extra_charges)
                    db.session.add(item)
                    db.session.commit()
                    flash('Item added successfully','success')
            else:
                flash('Package does not exist', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/items')

@bp_admin.route('/delete_item/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def remove_item(id):
    try:
        item = db.session.query(Item).filter_by(id=id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            flash('Item deleted successfully','success')
        else:
            flash('Item does not exist', 'danger')
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/items')

@bp_admin.route('/edit_item', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def edit_item():
    if request.method == 'POST':
        try:
            id = request.form['id']
            name = request.form['name']
            description = request.form['description']
            amount = request.form['amount']
            package_id = request.form['package_id']

            item = db.session.query(Item).filter_by(id=int(id)).first()
            
            if item:
                if name:
                    item.name = name
                if description:
                    item.description = description
                if amount:
                    item.amount_eur = amount
                item.package_id = package_id

                db.session.commit()
                flash('Item updated successfully','success')
            else:
                flash('Item does not exist', 'danger')
        except Exception as e:
            flash(f'Something went wrong: {e}', 'danger')
    return redirect('/admin/items')
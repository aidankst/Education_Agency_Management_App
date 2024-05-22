from flask import Blueprint, render_template, redirect, flash
from flask_login import current_user, login_required
from models import db, User, Client, PassportType, Steps, Invoice
from sqlalchemy import asc
from .accounts import requires_roles
from .index import majors, majorTypes

bp_client = Blueprint('bp_client', __name__)

@bp_client.route('/dashboard')
@login_required
@requires_roles('client')
def client_dashboard():
    try:
        user_id = current_user.id
        user = db.session.query(User).filter_by(id=user_id).first()
        progress = round((user.client.steps_id / db.session.query(Steps).count()) * 100, 2)
        next_steps = db.session.query(Steps).filter_by(id=user.client.steps_id +1).first()
        steps = Steps.query.order_by(asc(Steps.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/client/dashboard.html', user=user, steps=steps,  progress=progress, next_steps=next_steps, current_user=current_user, logged_in=True)

@bp_client.route('/personal_form', methods=['GET', 'POST'])
@login_required
@requires_roles('client')
def client_personal_form():
    try:
        user_id = current_user.id
        user = db.session.query(User).filter_by(id=user_id).first()
        client = db.session.query(Client).filter_by(id=user_id).first()
        passport_types = PassportType.query.order_by(asc(PassportType.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/client/personal_form.html', user=user, client=client, passport_types=passport_types, majorTypes=majorTypes, majors=majors, current_user=current_user, logged_in=True)

@bp_client.route('/items', methods=['GET', 'POST'])
@login_required
@requires_roles('client')
def client_items():
    return redirect('/client/invoices')

@bp_client.route('/invoices', methods=['GET', 'POST'])
@login_required
@requires_roles('client')
def client_invoices():
    try:
        unpaid_invoices = db.session.query(Invoice).filter(Invoice.user_id == current_user.id, Invoice.status == 'unpaid').order_by(asc(Invoice.id)).all()
        paid_invoices = db.session.query(Invoice).filter(Invoice.user_id == current_user.id, Invoice.status == 'paid').order_by(asc(Invoice.id)).all()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/client/items/invoices.html', unpaid_invoices=unpaid_invoices, paid_invoices=paid_invoices, current_user=current_user, logged_in=True)

@bp_client.route('/services', methods=['GET', 'POST'])
@login_required
@requires_roles('client')
def client_services():
    try:
        user_id = current_user.id
        user = db.session.query(User).filter_by(id=user_id).first()
    except Exception as e:
        flash(f'Something went wrong: {e}', 'danger')
    return render_template('/client/items/services.html', user=user, current_user=current_user, logged_in=True)


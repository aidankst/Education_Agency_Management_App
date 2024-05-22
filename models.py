import random
import sqlalchemy as sa
from sqlalchemy import Column, Table, ForeignKey, Integer, BIGINT
from flask_login import UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from emails import send_verification_email, register_account_by_admin_email
from passlib.pwd import genword


db = SQLAlchemy()

client_package_association = Table('client_package_association', db.Model.metadata,
    Column('client_id', Integer, ForeignKey('client.id'), primary_key=True),
    Column('package_id', Integer, ForeignKey('package.id'), primary_key=True)
)

package_service_association = Table('package_service_association', db.Model.metadata,
    Column('package_id', Integer, ForeignKey('package.id')),
    Column('service_id', Integer, ForeignKey('service.id'))
)

invoice_items_association = Table('invoice_package_association', db.Model.metadata,
    Column('invoice_id', BIGINT, ForeignKey('invoice.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('item.id'), primary_key=True)
)


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id                  = Column(sa.Integer(), primary_key=True)
    email               = Column(sa.String(255), unique=True)
    username            = Column(sa.String(120), nullable=True)
    password            = Column(sa.String(120), nullable=False)
    last_login_at       = Column(sa.DateTime(), nullable=True)
    last_login_ip       = Column(sa.String(100), nullable=True)
    login_count         = Column(sa.Integer(), nullable=True)
    active              = Column(sa.Boolean(), nullable=True)
    suspended           = Column(sa.Boolean(), nullable=True)
    fs_uniquifier       = Column(sa.String(255), unique=True, nullable=True)
    confirmed_at        = Column(sa.DateTime(), nullable=True)
    role                = Column(sa.String(30), nullable=False)
    remark              = Column(sa.String(255), nullable=True)
    google_drive        = Column(sa.String(255), nullable=True)
    
    client              = db.relationship('Client', backref='user', uselist=False, lazy=True)
    verification        = db.relationship('Verification', backref='user', uselist=False, lazy=True)

    @staticmethod
    def add_new_user(id, username, email, password, role, current):
        try:
            verification_code = Verification.generate_verification_code()
            user = User(id=id, username=username, email=email, password=User.create_password(password), role=role, active=False, login_count=0)
            verification = Verification(id=id, code=User.create_password(str(verification_code)), user=user)
            db.session.add(user)
            db.session.add(verification)
            db.session.commit()
            if current != 'admin':
                send_verification_email(id=id, name=username, email=email, role=role, verification_code=verification_code)
            else:
                register_account_by_admin_email(id=id, name=username, email=email, role=role, password=password, verification_code=verification_code)
            return True
        except Exception:
            return False

    @staticmethod
    def check_exists(email):
        user = db.session.query(User).filter_by(email=email).first()
        return user is not None
        
    @staticmethod
    def generate_user_id():
        status = True
        while status:
            user_id = random.randint(100000, 999999)
            check = db.session.query(User).filter_by(id=user_id).first()
            if not check:
                status = False
        return user_id

    @staticmethod
    def create_password(password):
        hashed_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8,
        )
        return hashed_password

    @staticmethod
    def check_password(email, password):
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            return check_password_hash(user.password, str(password))
        return False
    
    @staticmethod
    def generate_random_password(length=12):
        password = genword(length=length)
        return password
    
class Client(db.Model):
    __tablename__ = 'client'
    id                  = Column(sa.Integer(), sa.ForeignKey('user.id'), unique=True, primary_key=True)
    steps_id            = Column(sa.Integer(), sa.ForeignKey('steps.id'))
    contract_date       = Column(sa.DateTime(), nullable=True)

    national_id         = Column(sa.String(30), nullable=True)
    phone               = Column(sa.String(15), nullable=True)
    date_of_birth       = Column(sa.DateTime(), nullable=True)

    passport_num        = Column(sa.String(50), nullable=True)
    passport_type_id    = Column(sa.Integer(), sa.ForeignKey('passport_type.id'))
    passport_issue_date = Column(sa.DateTime(), nullable=True)
    passport_expiry_date= Column(sa.DateTime(), nullable=True)
    place_of_birth      = Column(sa.String(50), nullable=True)
    passport_country    = Column(sa.String(50), nullable=True)

    street              = Column(sa.String(40), nullable= True)
    house_number        = Column(sa.String(10), nullable=True)
    township            = Column(sa.String(30), nullable=True)
    postcode            = Column(sa.String(10), nullable=True)
    city                = Column(sa.String(30), nullable=True)
    state               = Column(sa.String(50), nullable=True)
    country             = Column(sa.String(30), nullable=True)

    father_name         = Column(sa.String(80), nullable=True)
    father_id           = Column(sa.String(80), nullable=True)
    mother_name         = Column(sa.String(80), nullable=True)
    mother_id           = Column(sa.String(80), nullable=True)

    major_type          = Column(sa.String(10), nullable=True)
    major_name          = Column(sa.String(80), nullable=True)
    priority_uni1       = Column(sa.String(100), nullable=True)
    priority_uni2       = Column(sa.String(100), nullable=True)
    priority_uni3       = Column(sa.String(100), nullable=True)

    institution         = Column(sa.String(100), nullable=True)
    institution_city    = Column(sa.String(30), nullable=True)
    institution_country = Column(sa.String(30), nullable=True)
    general_description = Column(sa.String(100), nullable=True)

    invoices            = db.relationship('Invoice', backref='client', lazy=True)
    packages            = db.relationship('Package', secondary=client_package_association, backref='client', lazy=True)

class Steps(db.Model):
    __tablename__ ='steps'
    id                  = Column(sa.Integer(), primary_key=True, unique=True)
    name                = Column(sa.String(255), nullable=False)
    clients             = db.relationship("Client", backref="steps", lazy=True)

class PassportType(db.Model):
    __tablename__ ='passport_type'
    id                  = Column(sa.Integer(), primary_key=True, unique=True)
    name                = Column(sa.String(80), nullable=False)
    clients             = db.relationship("Client", backref="passport_type", lazy=True)

class Verification(db.Model):
    __tablename__ ='verification'
    id                  = Column(sa.Integer(), sa.ForeignKey('user.id'), primary_key=True)
    code                = Column(sa.String(120), nullable=False)

    @staticmethod
    def generate_verification_code():
        verification_code = random.randint(100000, 999999)
        return verification_code
    
class Invoice(db.Model):
    __tablename__ = 'invoice'
    id                  = Column(sa.BIGINT(), primary_key=True, unique=True)
    user_id             = Column(sa.Integer(), sa.ForeignKey('client.id'), nullable=False)
    payment             = db.relationship('Payment', backref='invoice', uselist=False, lazy=True)
    items               = db.relationship('Item', secondary=invoice_items_association, backref='invoice', lazy=True)

    discount            = Column(sa.Float(), nullable=True)
    amount_eur          = Column(sa.Float(), nullable=False)
    exchange_rate       = Column(sa.Float(), nullable=True)
    amount_mmk          = Column(sa.Float(), nullable=True)

    date                = Column(sa.DateTime(), nullable=False)
    issuer              = Column(sa.String(80), nullable=False)
    deadline            = Column(sa.DateTime(), nullable=False)
    status              = Column(sa.String(20), nullable=True)

    @staticmethod
    def generate_invoice_id(date, package_id, user_id):
        # date = datetime.strptime(date_str, '%Y-%m-%d')
        invoice_id = str(date.strftime("%Y%m%d")) + str(package_id) + str(user_id)
        check = db.session.query(Invoice).filter_by(id=invoice_id).first()
        if check:
            invoice_id = False
            return invoice_id
        else:
            return invoice_id

class Payment(db.Model):
    __tablename__ = 'payment'
    id                  = Column(sa.BIGINT(), sa.ForeignKey('invoice.id'), unique=True, primary_key=True)
    date                = Column(sa.DateTime(), nullable=False)
    payment_registerer  = Column(sa.String(80), nullable=False)

class Package(db.Model):
    __tablename__ = 'package'
    id                  = Column(sa.Integer(), primary_key=True, unique=True)
    name                = Column(sa.String(80), nullable=False)
    description         = Column(sa.String(255), nullable=False)
    amount_eur          = Column(sa.Float(), nullable=False)
    services            = db.relationship('Service', secondary=package_service_association, back_populates='packages')
    items               = db.relationship('Item', backref='package', lazy=True)

class Service(db.Model):
    __tablename__ = 'service'
    id                  = Column(sa.Integer(), primary_key=True, unique=True)
    name                = Column(sa.String(80), nullable=False)
    description         = Column(sa.String(255), nullable=False)
    packages            = db.relationship('Package', secondary=package_service_association, back_populates='services')


class Item(db.Model):
    __tablename__ = 'item'
    id                  = Column(sa.Integer(), primary_key=True, unique=True)
    package_id          = Column(sa.Integer(), sa.ForeignKey('package.id'), nullable=False)
    name                = Column(sa.String(80), nullable=False)
    description         = Column(sa.String(255), nullable=False)
    amount_eur          = Column(sa.Float(), nullable=False)
    extra_charges       = Column(sa.Boolean(), nullable=False)

class Profit(db.Model):
    __tablename__ = 'profit'
    id                  = Column(sa.BIGINT(), primary_key=True, unique=True)
    date                = Column(sa.DateTime(), nullable=False)
    leveling_profit_eur = Column(sa.Float(), nullable=False)
    leveling_profit_mmk = Column(sa.Float(), nullable=False)
    ayes_profit_eur     = Column(sa.Float(), nullable=False)
    ayes_profit_mmk     = Column(sa.Float(), nullable=False)
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()

email_user = os.getenv('email_user')
email_password = os.getenv('email_password')

def send_contact_email(name, email, address, phone, subject, message):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <br>Greetings from <b>Leveling Education Service</b>!<br>
            <br>We have received your contact message filled via our website www.leveling.pl/contact.<br>
            <br><b>Message Content:</b><br>
            <br><b>Name:</b> { name }
            <br><b>Email:</b> { email }
            <br><b>Address:</b> { address }
            <br><b>Phone:</b> { phone }
            <br><b>Subject:</b> { subject }
            <br><b>Message:</b> <pre>{ message }</pre><br>
            <br>We will get back to you as soon as possible. If you haven't hear from us within 3 days, please call us @ +959 51 88 613.<br>
            <br>Thank you for contacting us!<br>
            <br>Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl', 'yuyuthandar78@gmail.com']
    send_email(email, html_body, subject)

def send_verification_email(id, name, email, role, verification_code):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <br>Greetings from <b>Leveling Education Service</b>!<br>
            <br>Thank you for registering at Leveling Education Service.<br>
            <br><b>Account Details:</b><br>
            <br><b>User ID:</b> { id }
            <br><b>Name:</b> { name }
            <br><b>Email:</b> { email }
            <br><b>Role:</b> { role.capitalize() }<br>
            <br><b>Verification Code:</b> { verification_code }<br>
            <br>Please use the verification code to activate your account. We strongly encourage you to use the laptop to login for the best view.<br>
            <br>Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email]
    subject = 'Account Registered | Leveling Education Service'
    send_email(email, html_body, subject)

def register_account_by_admin_email(id, name, email, role, password, verification_code):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <br>Greetings from <b>Leveling Education Service</b>!<br>
            <br>Thank you for registering at Leveling Education Service.<br>
            <br><b>Account Details:</b><br>
            <br><b>User ID:</b> { id }
            <br><b>Name:</b> { name }
            <br><b>Email:</b> { email }
            <br><b>Role:</b> { role.capitalize() }
            <br><b>Password:</b> { password }<br>
            <br><b>Verification Code:</b> { verification_code }<br>
            <br>Please use the verification code to activate your account. We strongly encourage you to use the laptop to login for the best view.<br>
            <br>Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email]
    subject = 'Account Registered | Leveling Education Service'
    send_email(email, html_body, subject)

def forgot_password_email(name, email, password, verification_code):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <br>Greetings from <b>Leveling Education Service</b>!<br>
            <br>You have requested to reset a password. Your account has been deactivated now.<br>
            <br><b>Account Details:</b><br>
            <br><b>Email:</b> { email }
            <br><b>New Password:</b> { password }<br>
            <br><b>Verification Code:</b> { verification_code }<br>
            <br>Please use the verification code to activate your account.<br>
            <br>You didn't request to reset your password? Please enter your account and change your password immediately.
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email]
    subject = 'Reset Password | Leveling Education Service'
    send_email(email, html_body, subject)

def personal_form_change_email(name, email):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <p>Greetings from <b>Leveling Education Service</b>!</p>
            <p>There is some data changes in your personal form. Please check it and if there is any errors, please inform the admins immediately.</pr>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl']
    subject = 'Personal Form Changed | Leveling Education Service'
    send_email(email, html_body, subject)


def new_step_add_email(name, email, previous_step, new_step):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <p>Greetings from <b>Leveling Education Service</b>!</p>
            <p>You have been added to a new step.</pr>
            <p>Step: Step {previous_step} -> Step {new_step}</p>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl']
    subject = 'New Step Added | Leveling Education Service'
    send_email(email, html_body, subject)

def add_remark_email(name, email):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <p>Greetings from <b>Leveling Education Service</b>!</p>
            <p>There is a new remark added by the admins. Please login to your account to see the remark.</pr>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl']
    subject = 'Remark Added | Leveling Education Service'
    send_email(email, html_body, subject)

def suspend_user_email(name, email):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <p>Greetings from <b>Leveling Education Service</b>!</p>
            <p>Your account has been suspended.</pr>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl']
    subject = 'Account Suspended | Leveling Education Service'
    send_email(email, html_body, subject)


def delete_user_email(name, email):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <p>Greetings from <b>Leveling Education Service</b>!</p>
            <p>Your account has been deleted permanently.</pr>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl']
    subject = 'Account Deleted | Leveling Education Service'
    send_email(email, html_body, subject)


def payment_record_email(name, email, invoice_number):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <p>Greetings from <b>Leveling Education Service</b>!</p>
            <p>Payment for Invoice #{invoice_number} has been recorded.</pr>
            <p>Please login to your account to view your invoices. Menu > Items > Invoices > Invoice ID</pr>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email]
    subject = f'Payment Recorded for Invoice #{invoice_number} | Leveling Education Service'
    send_email(email, html_body, subject)

def invoice_delete_email(name, email, invoice_number):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <p>Greetings from <b>Leveling Education Service</b>!</p>
            <p>Invoice #{invoice_number} has been deleted.</pr>
            <p>Please login to your account to view your invoices. Menu > Items > Invoices > Invoice ID</pr>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl']
    subject = f'Invoice #{invoice_number} Deleted | Leveling Education Service'
    send_email(email, html_body, subject)


def sell_package_email(name, email, package):
    html_body = f"""
    <html>
        <body>
            <p>Dear <b>{ name }</b>, <br>
            <br>Greetings from <b>Leveling Education Service</b>!<br>
            <br>You have been added to the {package.name}.<br>
            <br><b>Package Details:</b><br>
            <br><b>Name :</b> { package.name }
            <br><b>Description :</b> { package.description }
            <br><b>Amount :</b> &euro; { package.amount_eur }
            <p>Please sign the contract and send us as soon as possible! You can view the contract in your client panel.</p>
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = [email, 'kontakt@leveling.pl']
    subject = 'Package Added | Leveling Education Service'
    send_email(email, html_body, subject)

def send_profit_email(client_name, profit):
    html_body = f"""
    <html>
        <body>
            <p>Dear Partners, <br>
            <br>Greetings from <b>Leveling Education Service</b>!<br>
            <br>Invoice #{profit.id} for {client_name} has been paid. <br>Please see the profit below.<br>
            <br><b>Profit for Leveling Education Service :</b><br>
            <br><b>Amount &euro; :</b> &euro; { profit.leveling_profit_eur }
            <br><b>Amount MMK :</b> { profit.leveling_profit_mmk } MMK<br>
            <br><b>Profit for Ayar Yadanar Education Service :</b><br>
            <br><b>Amount &euro; :</b> &euro; { profit.ayes_profit_eur }
            <br><b>Amount MMK :</b> { profit.ayes_profit_mmk } MMK
            <p>If you have any questions or inquiries, please contact us at kontakt@leveling.pl.</p>
            Best regards,
            <br><strong>Leveling Education Service</strong>
            <br>ul. Zamknieta 10, 30-554, Krakow, Poland
            <br>kontakt@leveling.pl
            <br>www.leveling.pl
        </body>
    </html>
    """
    email = ['kontakt@leveling.pl', 'yuyuthandar78@gmail.com']
    subject = f'Profit #{profit.id} | Leveling Education Service'
    send_email(email, html_body, subject)


def send_invoice_email(client, invoice):
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ width: 100%; padding: 40px; background-color: #f6f6f6; }}
            .content {{ margin: 0 auto; max-width: 600px; background-color: #FFFFFF; border: 1px solid #000; }}
            .header, .footer {{ padding: 20px; }}
            .invoice-details {{ background: #f9f9f9; border-bottom: 1px solid #eee; }}
            .bill-to-title {{ padding-left: 20px; }}
            .bill-to {{ padding-left: 40px; }}
            .amount {{ border-bottom: 2px solid #000; border-top: 2px solid #000; padding: 5px 0; font-size: 18px;}}
            .body {{ padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <div class="header">
                    <table width="100%">
                        <tr>
                            <td>
                                <a href="http://www.leveling.pl" target="_blank">
                                    <img src="cid:logoimage" alt="Leveling Education Service Logo" style="height: auto; width: 100px">
                                </a>
                            </td>
                            <td style="text-align: right; color: #eb5324; font-size: 15px;">
                                <strong>Leveling Education Service</strong><br>
                                Invoice #{invoice.id}<br>
                                Date : {invoice.date.strftime('%Y-%m-%d')}<br>
                                Deadline : {invoice.deadline.strftime('%Y-%m-%d')}
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="invoice-details">
                    <table width="100%">
                        <tr>
                            <td class="bill-to-title"><strong>Bill To:</strong></td>
                        </tr>
                        <tr>
                            <td class="bill-to">
                                {client.user.username}<br>
                                {client.house_number}, {client.street}, {client.township}<br>
                                {client.postcode}, {client.city}<br>
                                {client.state}, {client.country}
                            </td>
                        </tr>
                    </table>
                </div>
                <div class="body">
                    <p>Please log in to your client account to view the detailed invoice.</p>
                    <table width="100%">
                        <tr>
                            <td class="amount">Amount to be paid</td>
                            <td class="amount" style="text-align: right;">€ {invoice.amount_eur}</td>
                        </tr>
                    </table>
                </div>
                <div class="footer">
                    <table width="100%">
                        <tr>
                            <td style="font-size: 12px;">
                                <strong>Questions?</strong><br>
                                Please contact our admins with any questions.
                            </td>
                            <td style="font-size: 12px;">
                                <strong>Leveling Education Service</strong><br>
                                ul. Zamknieta 10, lok 1.5<br>
                                30-554 Krakow, Poland<br>
                                NIP: 677 249 64 12
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    email = [client.user.email, 'kontakt@leveling.pl']
    subject = f'Invoice #{invoice.id} | Leveling Education Service'
    send_email_with_attachment(email, html_body, subject, "static/images/logo.png", '<logoimage>')

def send_email(emails, html_body, subject):

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = ", ".join(emails)

    part = MIMEText(html_body, 'html')
    msg.attach(part)


    server = smtplib.SMTP('smtp.zoho.eu', 587)  
    server.starttls() 
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()


def send_email_with_attachment(emails, html_body, subject, attachment_path, content_id):
    from app import app
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = ", ".join(emails)

    part = MIMEText(html_body, 'html')
    msg.attach(part)

    with open(attachment_path, 'rb') as img_file:  # Correct path to your image
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', content_id)  # Same ID as used in the HTML img src
        msg.attach(img)

    server = smtplib.SMTP('smtp.zoho.eu', 587)  
    server.starttls() 
    server.login(email_user, email_password)
    server.send_message(msg)
    server.quit()
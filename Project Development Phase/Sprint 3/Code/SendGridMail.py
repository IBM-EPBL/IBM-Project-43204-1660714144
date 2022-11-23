import os
from dotenv import load_dotenv
load_dotenv()
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def sendMail(to_email, mail_subject, message):
    message = Mail(
        from_email=os.getenv('FROM_EMAIL'),
        to_emails=to_email,
        subject=mail_subject,
        html_content='<strong> {} </strong>'.format(message))
    try:
        sg = SendGridAPIClient(os.getenv('API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e)
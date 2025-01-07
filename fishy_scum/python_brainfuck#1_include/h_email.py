import os.path
import smtplib
import urllib.parse
import re

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import Header
from email.utils import COMMASPACE, formatdate
from email import encoders

from h_types     import *

# ###
def send_mail(send_from, send_to, subject, message, files=[],
              server="velia.creditup.com.ua", port = 25, username='', password='',
              use_tls = true):
    msg = MIMEMultipart()
    msg.set_charset('utf-8')
    msg['From']    = send_from
    msg['Date']    = formatdate(localtime=True)
    msg['Subject'] = subject
    msg['To']      = COMMASPACE.join(send_to)

    msg.attach(MIMEText(message))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        fn = os.path.basename(path)
        fn = urllib.parse.quote(fn)
        part.add_header('Content-Disposition',
                        f"attachment; filename*=UTF-8''{fn}")
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login('analytic4@creditup.com.ua', '')
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()
    print(f'email sent to:{send_to}')


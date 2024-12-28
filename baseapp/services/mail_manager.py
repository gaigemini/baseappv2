import logging
logger = logging.getLogger()

from baseapp.config import email_smtp

class MailManager:
    def __init__(self):
        self.mail_manager = email_smtp.EmailSender()

    def send_mail(self, data: dict):
        logger.debug(f"data task: {data} type data: {type(data)}")
        msg_val = {
            "to":data.get("email"), # mandatory | kalau lebih dari satu jadi array ["aldian@gai.co.id","charly@gai.co.id"]
            "subject": "Request Forgot Password",
            "body_mail": f"Berikut kode OTP Anda: {data.get('otp')}"
        }

        body_mail, bcc_recipients = self.mail_manager.body_msg(msg_val)
        mail_sending = self.mail_manager.send_email(body_mail, bcc_recipients)

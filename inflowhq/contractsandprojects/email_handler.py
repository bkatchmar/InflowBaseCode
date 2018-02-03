from django.core.mail import EmailMessage
from django.template.loader import get_template
from contractsandprojects.models import Contract

class EmailHandler():
    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/base.html").render(context)

            msg = EmailMessage("Statement of Truth", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/clientemailrevision.html").render(context)

            msg = EmailMessage("Client Email Revision", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/clientemailsigned.html").render(context)

            msg = EmailMessage("Client Email Signed", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/contract.creation.confirm.client.html").render(context)

            msg = EmailMessage("Contract From", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/contract.creation.confirm.freelancer.html").render(context)

            msg = EmailMessage("Contract Sent", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/freelanceemailrevision.html").render(context)

            msg = EmailMessage("Freelance Email Revision", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/freelanceemailsigned.html").render(context)

            msg = EmailMessage("Freelance Email Signed", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_base_email(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            context = {}
            mail_body = get_template("email_templates/reveivedemail.html").render(context)

            msg = EmailMessage("Received Email", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

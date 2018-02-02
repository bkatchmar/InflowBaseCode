from django.core.mail import EmailMessage
from django.template.loader import get_template
from contractsandprojects.models import Contract

class EmailHandler():
    def send_for_initial_client(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            mail_body = ("<p>Dear [NAME],</p>"
                  "<p>The attached contract, 'Mobile App,' is from Josh Blank. Please review&nbsp;"
                  "the contract with any corrections by 12/30/17. Feel free to contact&nbsp;"
                  "InFlow with any questions at info@inflow.com</p>"
                  "<p>Your lovers,<br />InFlow</p>"
                  )

            msg = EmailMessage("Contract Sent to [CLIENT]", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

    def send_for_initial_freelancer(self,contract_to_generate):
        if (isinstance(contract_to_generate, Contract)):
            mail_body = ("<p>Contract From [FREELANCER],</p><br />"
                  "<p>The attached contract, 'Mobile App,' was sent to AT&T at 5:35pm on&nbsp;"
                  "12/22/17. You may view the status of your contract on your <a href='#'>Dashboard</a> any time.</p>"
                  "<p>Your lovers,<br />InFlow</p>"
                  )

            msg = EmailMessage("Contract From [FREELANCER]", mail_body, to=["bkatchmar@gmail.com"], from_email="brian@workinflow.co")
            msg.content_subtype = "html"
            msg.send()
        else:
            raise TypeError("Argument 'contract_to_generate' is not of a Model.Contract type")

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

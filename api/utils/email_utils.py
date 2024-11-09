from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_application_confirmation_email(application):
    """Send confirmation email to job seeker when they apply for a job"""
    subject = f"Application Submitted: {application.job.title}"

    context = {
        "applicant_name": application.applicant.user.email,
        "job_title": application.job.title,
        "company_name": application.job.employer.company_name,
        "application_date": datetime.now().strftime("%B %d, %Y"),
    }

    html_message = render_to_string("emails/application_confirmation.html", context)
    plain_message = render_to_string("emails/application_confirmation.txt", context)

    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.applicant.user.email],
        fail_silently=False,
    )


def send_employer_notification_email(application):
    """Send notification email to employer when they receive a new application"""
    subject = f"New Application Received: {application.job.title}"

    context = {
        "employer_name": application.job.employer.company_name,
        "job_title": application.job.title,
        "applicant_email": application.applicant.user.email,
        "application_date": application.applied_date.strftime("%B %d, %Y"),
        "cover_letter": application.cover_letter,
    }

    html_message = render_to_string("emails/employer_notification.html", context)
    plain_message = render_to_string("emails/employer_notification.txt", context)

    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.job.employer.user.email],
        fail_silently=False,
    )

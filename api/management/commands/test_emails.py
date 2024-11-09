from unittest.mock import Mock

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Application, Employer, Job, JobSeeker
from api.utils.email_utils import (
    send_application_confirmation_email,
    send_employer_notification_email,
)


class Command(BaseCommand):
    help = "Test email notifications for job applications"

    def add_arguments(self, parser):
        parser.add_argument(
            "--applicant-email",
            type=str,
            help="Email address for the applicant",
            default="frd.barros@gmail.com",
        )
        parser.add_argument(
            "--employer-email",
            type=str,
            help="Email address for the employer",
            default="frd.barros@gmail.com",
        )

    def handle(self, *args, **kwargs):
        try:
            # Create mock objects
            mock_user_applicant = Mock()
            mock_user_applicant.email = kwargs["applicant_email"]

            mock_user_employer = Mock()
            mock_user_employer.email = kwargs["employer_email"]

            mock_job_seeker = Mock()
            mock_job_seeker.user = mock_user_applicant

            mock_employer = Mock()
            mock_employer.user = mock_user_employer
            mock_employer.company_name = "Test Company"

            mock_job = Mock()
            mock_job.title = "Test Job Position"
            mock_job.employer = mock_employer

            mock_application = Mock()
            mock_application.applicant = mock_job_seeker
            mock_application.job = mock_job
            mock_application.applied_date = timezone.now()
            mock_application.cover_letter = "This is a test cover letter."

            # Test applicant confirmation email
            try:
                send_application_confirmation_email(mock_application)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully sent confirmation email to {kwargs['applicant_email']}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to send confirmation email: {str(e)}")
                )

            # Test employer notification email
            try:
                send_employer_notification_email(mock_application)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully sent notification email to {kwargs['employer_email']}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to send employer notification: {str(e)}")
                )

            self.stdout.write(self.style.SUCCESS("Test completed"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Test failed: {str(e)}"))

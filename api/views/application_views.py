import logging

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Application, Job
from api.serializers.application_serializers import ApplicationSerializer
from api.utils.email_utils import (
    send_application_confirmation_email,
    send_employer_notification_email,
)

logger = logging.getLogger(__name__)


class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if user is a job seeker
        if not hasattr(request.user, "jobseeker"):
            return Response(
                {"error": "Only job seekers can apply for jobs"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the job
        try:
            job = Job.objects.get(id=request.data.get("job"))
            if job.status != Job.Status.ACTIVE:
                return Response(
                    {"error": "This job is not accepting applications"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Check if already applied
        existing_application = Application.objects.filter(
            job=job, applicant=request.user.jobseeker
        ).exists()

        if existing_application:
            return Response(
                {"error": "You have already applied for this job"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            applicant=request.user.jobseeker,
            status="P",  # Set initial status to Pending
        )
        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        if response.status_code == status.HTTP_201_CREATED:
            application = Application.objects.get(id=response.data["id"])

            # Send confirmation email to applicant
            try:
                send_application_confirmation_email(application)
            except Exception as e:
                # Log the error but don't fail the request
                logger.error(f"Failed to send application confirmation email: {str(e)}")

            # Send notification to employer
            try:
                send_employer_notification_email(application)
            except Exception as e:
                # Log the error but don't fail the request
                logger.error(f"Failed to send employer notification email: {str(e)}")

        return response

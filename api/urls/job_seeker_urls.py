from django.urls import path

from api.views.job_seeker_views import JobSeekerUpdateView

urlpatterns = [
    path("job-seeker/profile/", JobSeekerUpdateView.as_view(), name="jobseeker-update"),
]

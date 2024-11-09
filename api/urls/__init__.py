from django.urls import include, path

urlpatterns = [
    path("", include("api.urls.auth_urls")),
    path("", include("api.urls.job_urls")),
    path("", include("api.urls.order_urls")),
    path("", include("api.urls.application_urls")),
    path("", include("api.urls.job_seeker_urls")),
    path("", include("api.urls.employer_urls")),
]

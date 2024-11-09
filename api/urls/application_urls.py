from django.urls import path

from api.views.application_views import ApplicationCreateView

urlpatterns = [
    path("applications/", ApplicationCreateView.as_view(), name="application-create"),
]

from django.urls import path

from api.views.employer_views import EmployerUpdateView

urlpatterns = [
    path('employer/profile/', EmployerUpdateView.as_view(), name='employer-update'),
]
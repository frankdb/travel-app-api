from django.urls import include, path

urlpatterns = [
    path("", include("api.urls.auth_urls")),
]

from django.urls import path

from api.views import CustomTokenRefreshView, LoginView, LogoutView, RegisterView
from api.views.auth_views import (
    ChangePasswordView,
    GoogleLoginView,
    ResetPasswordConfirmView,
    ResetPasswordEmailView,
    SetUserTypeView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("password/change/", ChangePasswordView.as_view(), name="change-password"),
    path("password/reset/", ResetPasswordEmailView.as_view(), name="reset-password"),
    path(
        "password/reset/confirm/",
        ResetPasswordConfirmView.as_view(),
        name="reset-password-confirm",
    ),
    path("auth/google/", GoogleLoginView.as_view(), name="google-login"),
    path("user/type/", SetUserTypeView.as_view(), name="set-user-type"),
]

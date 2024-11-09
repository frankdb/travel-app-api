import logging
import secrets

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from api.models.auth import PasswordResetToken
from api.models.job_board import Employer, JobSeeker
from api.models.user import CustomUser
from api.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from api.serializers.auth_serializers import (
    ChangePasswordSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordEmailSerializer,
    SetUserTypeSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            if user.user_type == "EM":
                Employer.objects.create(user=user)
            elif user.user_type == "JS":
                JobSeeker.objects.create(user=user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "message": "User created successfully",
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                {
                    "refresh_token": serializer.validated_data["refresh_token"],
                    "access_token": serializer.validated_data["access_token"],
                    "user": serializer.get_user(serializer.validated_data),
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"Logout attempt for user: {request.user.email}")
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                logger.warning(
                    f"Logout failed for user {request.user.email}: Refresh token not provided"
                )
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info(f"User {request.user.email} logged out successfully")
            return Response(
                {"success": "User logged out successfully"}, status=status.HTTP_200_OK
            )

        except TokenError as e:
            logger.error(
                f"Logout failed for user {request.user.email}: Invalid token - {str(e)}"
            )
            return Response(
                {"error": f"Invalid token: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.exception(
                f"Unexpected error during logout for user {request.user.email}: {str(e)}"
            )
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f"Token refreshed successfully for user: {request.user}")
        else:
            logger.warning(f"Token refresh failed for user: {request.user}")
        return response


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data["old_password"]):
                user.set_password(serializer.data["new_password"])
                user.save()
                return Response({"message": "Password changed successfully"})
            return Response(
                {"error": "Incorrect old password"}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordEmailView(APIView):
    def post(self, request):
        serializer = ResetPasswordEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data["email"]
            try:
                user = CustomUser.objects.get(email=email)
                token = secrets.token_urlsafe(32)

                # Create password reset token
                reset_token = PasswordResetToken.objects.create(user=user, token=token)

                reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"

                send_mail(
                    "Password Reset Request",
                    f"Click the following link to reset your password: {reset_url}",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                return Response({"message": "Password reset email sent"})
            except CustomUser.DoesNotExist:
                return Response({"message": "Password reset email sent"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    def post(self, request):
        try:
            token = request.data.get("token")
            reset_token = PasswordResetToken.objects.get(token=token)

            if not reset_token.is_valid:
                return Response(
                    {"error": "Token has expired or already been used"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ResetPasswordConfirmSerializer(data=request.data)
            if serializer.is_valid():
                user = reset_token.user
                user.set_password(serializer.data["new_password"])
                user.save()

                # Mark token as used
                reset_token.used = True
                reset_token.save()

                return Response({"message": "Password reset successful"})

        except PasswordResetToken.DoesNotExist:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.FRONTEND_URL
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        try:
            # Process the social login
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                # Extract user from response data
                user_data = response.data.get("user", {})
                email = user_data.get("email")

                # Check if user exists
                try:
                    user = CustomUser.objects.get(email=email)
                except CustomUser.DoesNotExist:
                    # Create new user
                    user = CustomUser.objects.create(
                        email=email,
                        user_type="JS",  # Default to JobSeeker
                        is_active=True,
                    )
                    # Create JobSeeker profile
                    JobSeeker.objects.create(
                        user=user,
                        first_name=user_data.get("first_name", ""),
                        last_name=user_data.get("last_name", ""),
                    )

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    }
                )

            return response

        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return Response(
                {"error": "Failed to process Google login"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SetUserTypeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.user_type:
            return Response(
                {"error": "User type already set"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SetUserTypeSerializer(data=request.data)
        if serializer.is_valid():
            user_type = serializer.validated_data["user_type"]
            request.user.user_type = user_type
            request.user.save()

            if user_type == "EM":
                Employer.objects.create(user=request.user)
            elif user_type == "JS":
                JobSeeker.objects.create(user=request.user)

            return Response(
                {
                    "message": "User type set successfully",
                    "user": UserSerializer(request.user).data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

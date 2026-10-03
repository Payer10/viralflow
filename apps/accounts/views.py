from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from apps.accounts.models import User
from apps.accounts.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
)


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def _error(code, message, http_status):
    return Response(
        {"error": {"code": code, "message": message}}, status=http_status
    )


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/"""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": _tokens_for_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/v1/auth/login/"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": _tokens_for_user(user),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/v1/auth/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token so it can no longer be used to
    obtain new access tokens. Requires
    'rest_framework_simplejwt.token_blacklist' in INSTALLED_APPS.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return _error(
                "INVALID_REQUEST", "'refresh' token is required.", status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return _error(
                "INVALID_REQUEST", "Token is invalid or already blacklisted.",
                status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_205_RESET_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/v1/auth/me/
    PATCH /api/v1/auth/me/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return UpdateProfileSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = True  # always partial — this is PATCH-style profile editing
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(instance).data)


class ChangePasswordView(APIView):
    """POST /api/v1/auth/change-password/ — standard addition beyond the base spec list."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        return Response({"detail": "Password updated successfully."})
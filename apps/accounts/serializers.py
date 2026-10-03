from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user — used for /auth/me/ and nested elsewhere."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "email", "is_active", "created_at", "updated_at"]


class RegisterSerializer(serializers.ModelSerializer):
    """POST /api/v1/auth/register/"""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm", "first_name", "last_name"]

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """POST /api/v1/auth/login/"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not user:
            raise serializers.ValidationError(
                {"error": {"code": "UNAUTHORIZED", "message": "Invalid email or password."}}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"error": {"code": "FORBIDDEN", "message": "This account is disabled."}}
            )

        attrs["user"] = user
        return attrs


class UpdateProfileSerializer(serializers.ModelSerializer):
    """PATCH /api/v1/auth/me/"""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar"]


class ChangePasswordSerializer(serializers.Serializer):
    """Optional: POST /api/v1/auth/change-password/ (not in v1 spec list but standard practice)."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
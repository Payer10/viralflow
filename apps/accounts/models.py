import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .manager import UserManager


def avatar_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    return f"accounts/avatars/{instance.id}.{ext}"


class User(AbstractBaseUser, PermissionsMixin):
    """
    ViralFlow custom user model (spec section 11).
    Email is the unique identifier — no username field.

    UUID primary key is used instead of an auto-increment int so
    user ids are never sequentially guessable across the API
    (assets, projects, generations all key off this — see spec
    section 59, "Security Architecture" / ownership checks).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to=avatar_upload_path, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    ROLE_CHOICES = (
        ("candidate", "Candidate"),
        ("employer", "Employer"),
    )

    username = None

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    # Candidate Details
    full_name = models.CharField(
        max_length=150,
        blank=True
    )

    current_role = models.CharField(
        max_length=100,
        blank=True
    )

    # Employer Details
    company_name = models.CharField(
        max_length=200,
        blank=True
    )

    hr_name = models.CharField(
        max_length=150,
        blank=True
    )

    # Common Fields
    phone = models.CharField(
        max_length=15,
        blank=True
    )

    website = models.URLField(
        blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        if self.role == "candidate":
            return self.full_name or self.email

        return self.company_name or self.email
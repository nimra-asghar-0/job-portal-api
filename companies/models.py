from django.conf import settings
from django.db import models


class Company(models.Model):

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies",
    )

    name = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
    )

    website = models.URLField(
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    logo = models.ImageField(
        upload_to="companies/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name
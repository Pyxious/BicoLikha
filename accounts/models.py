from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_column='PHONE_NUMBER',
    )

    class Meta:
        db_table = 'auth_user'


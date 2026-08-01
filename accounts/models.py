from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
# Create your models here.
class User(AbstractUser):

    class UserRole(models.TextChoices):
        CANDIDATE="candidate","Candidate"
        RECRUITER="recruiter","Recruiter"

    # username=None
    username = models.CharField(max_length=150, unique=True)
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=20, blank=True)
    profile_image=models.ImageField(upload_to="profiles/", blank=True, null=True)
    user_role=models.CharField(max_length=20, choices=UserRole.choices,default=UserRole.CANDIDATE,)
    is_verified=models.BooleanField(default=False)
    objects=UserManager()
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["username"]
    def __str__(self):
        return self.email

# adminpanel/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class AdminUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Admins must have a username")
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

class AdminUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    objects = AdminUserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

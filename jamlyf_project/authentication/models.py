from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from jamlyf.base_model import BaseModel
from .manager import UserManager


class User(BaseModel, AbstractBaseUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    phone_no = models.CharField(max_length=50, unique=True)

    # NOTE: This should eventually change to a list of countries
    country = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_no", "country"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def get_work_spots_uuids(self):
        work_spots = self.manager_spots.all().union(self.steward_spots.all())
        return work_spots.values_list("uuid", flat=True)


class OtpCode(BaseModel):
    mobile = models.CharField(max_length=50, verbose_name="phone number", blank=True)
    email = models.EmailField(verbose_name="email", blank=True)
    email_code = models.CharField(max_length=8, verbose_name="Email Verification Code")
    phone_code = models.CharField(max_length=8, verbose_name="Phone Verification Code")
    add_time = models.DateTimeField(verbose_name="Generation time", auto_now_add=True)
    counter = models.IntegerField(default=0, blank=False)

    def __str__(self):
        return str(self.mobile)

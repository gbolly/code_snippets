import random
from django.contrib.auth.hashers import make_password
import factory
from .models import User, OtpCode


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    password = make_password("a1b2c3d4e5f6")
    first_name = "Test"
    last_name = "User"
    phone_no = factory.LazyAttribute(lambda _: ''.join(map(str, random.sample(range(1, 19), 10))))
    email = factory.Sequence(lambda n: f"user_{n}@sample.com")
    country = "Canada"


class OtpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OtpCode

    mobile = factory.LazyAttribute(lambda _: ''.join(map(str, random.sample(range(1, 19), 10))))
    email = factory.Sequence(lambda n: f"user_{n}@sample.com")
    counter = 0

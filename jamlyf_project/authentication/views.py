import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.template import loader

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.state import token_backend
from rest_framework_simplejwt.exceptions import TokenBackendError

from jamlyf.utilities import send_email
from apps.notification.services import get_service_client_token
from .constants import (
    JAMLYF_INCORRECT_CREDENTIALS_MESSAGE,
    JAMLYF_RESET_PASSWORD_MESSAGE,
)
from .models import User
from .serializers import (
    CreateUserSerializer,
    ReadUserSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)


@api_view(["POST"])
@permission_classes([])
def create_user(request):
    # TODO: Remove hardcoded country we location feature
    # is ready.
    try:
        request.data['country'] = "Nigeria"
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token_object = RefreshToken.for_user(user)

        response_data = {
            "refresh_token": str(token_object),
            "access_token": str(token_object.access_token),
            "user": ReadUserSerializer(user).data
        }
        subject = 'Welcome onboard'
        context = {
            'first_name': user.first_name
        }
        htmltemp = loader.get_template('main/welcome_email.html')
        html_message = htmltemp.render(context)
        plain_message = f'Welcome {user.first_name}'

        try:
            send_email(
                subject=subject,
                plain_message=plain_message,
                html_message=html_message,
                recipient=[user.email]
            )
        except SMTPException as e:
            logging.info(e)
        return Response(response_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(data=e.detail, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        validate_email(email)
        user = User.objects.get(email=email)
        is_password_valid = check_password(password, user.password)
        assert is_password_valid

        token_object = RefreshToken.for_user(user)
        work_spots = {str(spot_uuid): True for spot_uuid in user.get_work_spots_uuids()}
        response_data = {
            "refresh_token": str(token_object),
            "access_token": str(token_object.access_token),
            "firebase_token": get_service_client_token(
                str(user.id), {"uuid": str(user.uuid), **work_spots}
            ),
            "user": ReadUserSerializer(user).data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except (User.DoesNotExist, AssertionError, ValidationError):
        raise AuthenticationFailed(JAMLYF_INCORRECT_CREDENTIALS_MESSAGE)


@api_view(["PUT"])
def password_change(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    request.user.set_password(serializer.validated_data['new_password'])
    request.user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def password_reset(request):
    serializer = PasswordResetSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.filter(
        email__iexact=serializer.data["email"]).first()

    if user:
        token_object = RefreshToken.for_user(user)
        token = str(token_object.access_token)
        redirect_url = f'{settings.CLIENT_HOST}/newpassword/{token}'
        subject = 'JamLfy Account Password Reset'
        context = {
            'base_url': settings.BASE_URL,
            'redirect_url': redirect_url
        }
        htmltemp = loader.get_template('main/password/password_reset_email.html')
        html_message = htmltemp.render(context)
        plain_message = f'Copy and paste the url in your broweser.\n\n {redirect_url}'

        try:
            send_email(
                subject=subject,
                plain_message=plain_message,
                html_message=html_message,
                recipient=[user.email]
            )
        except SMTPException as e:
            logging.info(e)

    return Response({'message': JAMLYF_RESET_PASSWORD_MESSAGE}, status=status.HTTP_200_OK)


@api_view(["PUT"])
@authentication_classes([])
@permission_classes([])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    token = serializer.validated_data.get('token')

    if not token:
        raise AuthenticationFailed(JAMLYF_INCORRECT_CREDENTIALS_MESSAGE)
    try:
        token_payload = token_backend.decode(token, verify=True)
    except TokenBackendError:
        raise AuthenticationFailed(JAMLYF_INCORRECT_CREDENTIALS_MESSAGE)

    user_id = token_payload['user_id']
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise AuthenticationFailed(JAMLYF_INCORRECT_CREDENTIALS_MESSAGE)

    user.set_password(serializer.validated_data.get('new_password'))
    user.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["PATCH"])
def update_user(request):
    data = request.data
    serializer = CreateUserSerializer(request.user, data=data, partial=True)
    serializer.is_valid(raise_exception=True)

    if "password" in data:
        raise AuthenticationFailed("Password field cannot be modified")
    user = serializer.save()

    response_data = {
        "user": ReadUserSerializer(user).data
    }

    return Response(response_data, status=status.HTTP_200_OK)

from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class SystemUserException(Exception):
    message = "You don't have permission to login as system user"


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if user.is_staff:
            raise SystemUserException()

        try:
            user.labuser
            token["user_type"] = settings.LAB_USER
        except AttributeError:
            pass

        try:
            user.patient
            token["user_type"] = settings.PATIENT_USER
        except AttributeError:
            pass

        token['first_name'] = user.first_name
        token['email'] = user.email
        token['username'] = user.username

        return token

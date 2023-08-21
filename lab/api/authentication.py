from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


class LabAuthentication(JWTAuthentication):

    def authenticate(self, request):
        if self.get_header(request) is None:
            return None
        try:
            user = super().authenticate(request)[0]
        except (AuthenticationFailed, InvalidToken) as _:
            return None
        try:
            lab_user = user.labuser  # reverse relation with labuser model
        except Exception:
            return None
        user.lab_user = lab_user
        request.user = user
        return user, None

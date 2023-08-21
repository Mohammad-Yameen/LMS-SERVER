from rest_framework.authentication import BaseAuthentication


class PatientAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        Returns a `Patient` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the session-based user from the underlying HttpRequest object
        user = getattr(request._request, 'patient', None)

        # Unauthenticated, CSRF validation not required
        if not user or not user.is_active:
            return None

        return user, None
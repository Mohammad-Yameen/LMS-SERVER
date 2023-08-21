from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView

from new_lms.api.serializers import SystemUserException
from rest_framework_simplejwt.authentication import JWTAuthentication


class LoginAPIVIew(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except SystemUserException as exc:
            return Response({'error': exc.message}, status=status.HTTP_403_FORBIDDEN)


class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            refresh_token = RefreshToken(request.data["refresh_token"])
            refresh_token.blacklist()

            return Response({'message': 'logged out successfully'})
        except Exception as exc:
            return Response({'error': 'Token is blacklisted'}, status=status.HTTP_400_BAD_REQUEST)

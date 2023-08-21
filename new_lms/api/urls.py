from django.urls import path

from .views import *

urlpatterns = [
    path('login/', LoginAPIVIew.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),

]

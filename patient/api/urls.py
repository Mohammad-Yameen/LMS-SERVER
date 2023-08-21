from django.urls import path

from .views import *


urlpatterns = [
    path('', PatientAPIVIew.as_view()),
    path('<int:pk>', PatientAPIVIew.as_view()),
]

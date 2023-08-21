from django.urls import path

from .views import *

urlpatterns = [
    path('', LabAPIView.as_view()),
    path('member/', MemberAPIView.as_view()),
    path('patient/', PatientAPIView.as_view()),
    path('bill/', BillAPIView.as_view()),
    path('bill/print/', BillPrintAPIView.as_view()),
    path('fill/test/', FillTestAPIView.as_view()),
    path('patient/report/', ReportAPIView.as_view()),
]

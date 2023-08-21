from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('new_lms.api.urls')),
    path('api/lab/', include("lab.api.urls")),
    path('api/patient/', include("patient.api.urls"))
]

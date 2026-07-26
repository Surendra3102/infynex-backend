from django.urls import path

from .views import ContactAPIView, EmployerRequestAPIView


urlpatterns = [
    path("", ContactAPIView.as_view(), name="contact"),
    path("request/",
        EmployerRequestAPIView.as_view(),
        name="employer-request",)
]
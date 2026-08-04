from django.urls import path

from .views import ApplicationCreateView, ApplicationListView


urlpatterns = [
    path("", ApplicationListView.as_view(), name="application-list"),
    path("create/", ApplicationCreateView.as_view(), name="application-create"),
]

from django.urls import path

from .views import (
    ApplicationCreateView,
    ApplicationListView,
    RecruiterApplicationListView,
    RecruiterApplicationStatusUpdateView,
)


urlpatterns = [
    path("", ApplicationListView.as_view(), name="application-list"),
    path("create/", ApplicationCreateView.as_view(), name="application-create"),

    path(
        "recruiter/",
        RecruiterApplicationListView.as_view(),
        name="recruiter-application-list",
    ),

    path(
        "<int:pk>/status/",
        RecruiterApplicationStatusUpdateView.as_view(),
        name="recruiter-application-status-update",
    ),
]


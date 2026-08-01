from django.urls import path
from .views import RegisterView
from .views import MeView
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
]

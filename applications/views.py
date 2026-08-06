from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Application
from .permissions import IsCandidate, IsRecruiter
from .serializers import (
    ApplicationSerializer,
    ApplicationStatusSerializer,
)


class ApplicationCreateView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def perform_create(self, serializer):
        serializer.save(candidate=self.request.user)


class ApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        return Application.objects.filter(
            candidate=self.request.user
        ).order_by("-created_at")


class RecruiterApplicationListView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsRecruiter]

    def get_queryset(self):
        return Application.objects.filter(
            job__recruiter=self.request.user
        ).order_by("-created_at")


class RecruiterApplicationStatusUpdateView(generics.UpdateAPIView):
    serializer_class = ApplicationStatusSerializer
    permission_classes = [IsAuthenticated, IsRecruiter]

    http_method_names = ["patch"]

    def get_queryset(self):
        return Application.objects.filter(
            job__recruiter=self.request.user
        )
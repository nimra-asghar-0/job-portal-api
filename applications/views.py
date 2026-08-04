from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Application
from .serializers import ApplicationSerializer
from .permissions import IsCandidate


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
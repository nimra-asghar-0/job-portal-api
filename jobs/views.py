from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Job
from .serializers import JobSerializer
from .permissions import IsRecruiterOwner
from .filters import JobFilter
from rest_framework.filters import SearchFilter

class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = JobFilter

    search_fields = [
        "title",
        "description",
        "company",
        "skills",
    ]

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, IsRecruiterOwner]
from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    recruiter = serializers.ReadOnlyField(source="recruiter.email")

    class Meta:
        model = Job
        fields = [
            "id",
            "recruiter",
            "title",
            "description",
            "company",
            "location",
            "employment_type",
            "experience_level",
            "salary_min",
            "salary_max",
            "skills",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recruiter",
            "created_at",
            "updated_at",
        ]
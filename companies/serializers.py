from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):

    recruiter = serializers.ReadOnlyField(
        source="recruiter.email"
    )

    class Meta:
        model = Company
        fields = [
            "id",
            "recruiter",
            "name",
            "description",
            "website",
            "location",
            "logo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "recruiter",
            "created_at",
            "updated_at",
        ]

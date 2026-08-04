from rest_framework import serializers

from .models import Application
from jobs.models import Job


class ApplicationSerializer(serializers.ModelSerializer):
    candidate = serializers.ReadOnlyField(source="candidate.email")

    job = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all()
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "candidate",
            "cover_letter",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "candidate",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        candidate = request.user
        job = attrs.get("job")

        if Application.objects.filter(
            job=job,
            candidate=candidate,
        ).exists():
            raise serializers.ValidationError(
                {
                    "job": "You have already applied for this job."
                }
            )

        return attrs
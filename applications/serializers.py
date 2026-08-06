
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
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        request = self.context.get("request")

        # For PATCH requests, job may not be included.
        # In that case, use the application's existing job.
        job = attrs.get("job")

        if job is None and self.instance is not None:
            job = self.instance.job

        # Only perform job-related validation when we have a job.
        if job is not None:

            # Prevent applications to closed jobs.
            if (
                request
                and request.method == "POST"
                and job.status == Job.JobStatus.CLOSED
            ):
                raise serializers.ValidationError(
                    {
                        "job": "You cannot apply for a closed job."
                    }
                )

            # Prevent duplicate applications.
            if (
                request
                and request.method == "POST"
                and Application.objects.filter(
                    job=job,
                    candidate=request.user,
                ).exists()
            ):
                raise serializers.ValidationError(
                    {
                        "job": "You have already applied for this job."
                    }
                )

        return attrs


class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status"]

    def validate_status(self, value):
        if value not in [
            Application.Status.ACCEPTED,
            Application.Status.REJECTED,
        ]:
            raise serializers.ValidationError(
                "Status must be either 'accepted' or 'rejected'."
            )

        return value


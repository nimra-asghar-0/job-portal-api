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

    def validate(self, attrs):
        salary_min = attrs.get("salary_min")
        salary_max = attrs.get("salary_max")

        # During PATCH, use existing values when one salary isn't provided.
        if self.instance is not None:
            if salary_min is None:
                salary_min = self.instance.salary_min
            if salary_max is None:
                salary_max = self.instance.salary_max

        # Prevent negative salaries.
        if salary_min is not None and salary_min < 0:
            raise serializers.ValidationError({
                "salary_min": "Salary cannot be negative."
            })

        if salary_max is not None and salary_max < 0:
            raise serializers.ValidationError({
                "salary_max": "Salary cannot be negative."
            })

        # Minimum salary cannot exceed maximum salary.
        if (
            salary_min is not None
            and salary_max is not None
            and salary_min > salary_max
        ):
            raise serializers.ValidationError({
                "salary": "salary_min cannot be greater than salary_max."
            })

        return attrs
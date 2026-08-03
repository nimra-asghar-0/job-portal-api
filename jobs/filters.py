import django_filters

from .models import Job


class JobFilter(django_filters.FilterSet):

    class Meta:
        model = Job
        fields = [
            "location",
            "employment_type",
            "experience_level",
            "status",
        ]
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Job

User = get_user_model()


class JobAPITests(APITestCase):

    def setUp(self):
        self.recruiter = User.objects.create_user(
            username="test_recruiter",
            email="testrecruiter@example.com",
            password="TestPass123!",
            user_role="recruiter",
        )

        self.candidate = User.objects.create_user(
            username="test_candidate",
            email="testcandidate@example.com",
            password="TestPass123!",
            user_role="candidate",
        )

        self.job_data = {
            "title": "Python Developer",
            "description": "Python and Django developer required.",
            "company": "Test Company",
            "location": "Lahore",
            "employment_type": "full_time",
            "experience_level": "entry",
            "salary_min": "50000.00",
            "salary_max": "80000.00",
            "skills": "Python, Django, SQL",
            "status": "open",
        }

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_recruiter_can_create_job(self):
        self.authenticate(self.recruiter)

        response = self.client.post(
            "/api/jobs/",
            self.job_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(Job.objects.count(), 1)

    def test_candidate_cannot_create_job(self):
        self.authenticate(self.candidate)

        response = self.client.post(
            "/api/jobs/",
            self.job_data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Job.objects.count(), 0)

    def test_negative_salary_is_rejected(self):
        self.authenticate(self.recruiter)

        data = self.job_data.copy()
        data["salary_min"] = "-5000.00"

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("salary_min", response.data)

    def test_salary_min_cannot_exceed_salary_max(self):
        self.authenticate(self.recruiter)

        data = self.job_data.copy()
        data["salary_min"] = "90000.00"
        data["salary_max"] = "50000.00"

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("salary", response.data)


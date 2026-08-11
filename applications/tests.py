from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from jobs.models import Job
from .models import Application

User = get_user_model()


class ApplicationAPITests(APITestCase):

    def setUp(self):
        self.recruiter = User.objects.create_user(
            username="test_recruiter",
            email="testrecruiter@example.com",
            password="TestPass123!",
            user_role="recruiter",
        )

        self.recruiter2 = User.objects.create_user(
            username="test_recruiter2",
            email="testrecruiter2@example.com",
            password="TestPass123!",
            user_role="recruiter",
        )

        self.candidate = User.objects.create_user(
            username="test_candidate",
            email="testcandidate@example.com",
            password="TestPass123!",
            user_role="candidate",
        )

        self.candidate2 = User.objects.create_user(
            username="test_candidate2",
            email="testcandidate2@example.com",
            password="TestPass123!",
            user_role="candidate",
        )

        self.job = Job.objects.create(
            recruiter=self.recruiter,
            title="Python Developer",
            description="Python and Django developer required.",
            company="Test Company",
            location="Lahore",
            employment_type="full_time",
            experience_level="entry",
            salary_min="50000.00",
            salary_max="80000.00",
            skills="Python, Django, SQL",
            status="open",
        )

        self.job2 = Job.objects.create(
            recruiter=self.recruiter2,
            title="Django Backend Developer",
            description="Django backend developer required.",
            company="Another Company",
            location="Lahore",
            employment_type="full_time",
            experience_level="entry",
            salary_min="60000.00",
            salary_max="90000.00",
            skills="Python, Django, REST API",
            status="open",
        )

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_candidate_can_apply_for_job(self):
        self.authenticate(self.candidate)

        response = self.client.post(
            "/api/applications/create/",
            {
                "job": self.job.id,
                "cover_letter": "I am interested in this Python Developer position.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Application.objects.count(),
            1,
        )

        application = Application.objects.first()

        self.assertEqual(
            application.candidate,
            self.candidate,
        )

        self.assertEqual(
            application.job,
            self.job,
        )

        self.assertEqual(
            application.status,
            Application.Status.PENDING,
        )

    def test_recruiter_cannot_apply_for_job(self):
        self.authenticate(self.recruiter)

        response = self.client.post(
            "/api/applications/create/",
            {
                "job": self.job.id,
                "cover_letter": "I want to apply for this job.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(
            Application.objects.count(),
            0,
        )

    def test_candidate_cannot_apply_twice_for_same_job(self):
        Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="First application.",
        )

        self.authenticate(self.candidate)

        response = self.client.post(
            "/api/applications/create/",
            {
                "job": self.job.id,
                "cover_letter": "Second application.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "job",
            response.data,
        )

        self.assertEqual(
            Application.objects.count(),
            1,
        )

    def test_candidate_cannot_apply_for_closed_job(self):
        self.job.status = Job.JobStatus.CLOSED
        self.job.save()

        self.authenticate(self.candidate)

        response = self.client.post(
            "/api/applications/create/",
            {
                "job": self.job.id,
                "cover_letter": "I want to apply for this job.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "job",
            response.data,
        )

        self.assertEqual(
            Application.objects.count(),
            0,
        )

    def test_candidate_can_only_see_own_applications(self):
        Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="My application.",
        )

        Application.objects.create(
            job=self.job2,
            candidate=self.candidate2,
            cover_letter="Another candidate application.",
        )

        self.authenticate(self.candidate)

        response = self.client.get(
            "/api/applications/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["candidate"],
            self.candidate.email,
        )

    def test_recruiter_can_see_applications_for_own_jobs(self):
        Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="Application for recruiter 1.",
        )

        Application.objects.create(
            job=self.job2,
            candidate=self.candidate2,
            cover_letter="Application for recruiter 2.",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/applications/recruiter/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

        self.assertEqual(
            response.data["results"][0]["job"],
            self.job.id,
        )

    def test_recruiter_cannot_see_another_recruiters_applications(self):
        Application.objects.create(
            job=self.job2,
            candidate=self.candidate,
            cover_letter="Application for another recruiter.",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/applications/recruiter/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            0,
        )

    def test_recruiter_can_accept_application(self):
        application = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="Please consider my application.",
        )

        self.authenticate(self.recruiter)

        response = self.client.patch(
            f"/api/applications/{application.id}/status/",
            {
                "status": "accepted",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.ACCEPTED,
        )

    def test_recruiter_can_reject_application(self):
        application = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="Please consider my application.",
        )

        self.authenticate(self.recruiter)

        response = self.client.patch(
            f"/api/applications/{application.id}/status/",
            {
                "status": "rejected",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.REJECTED,
        )

    def test_recruiter_cannot_update_another_recruiters_application(self):
        application = Application.objects.create(
            job=self.job2,
            candidate=self.candidate,
            cover_letter="Application for recruiter 2.",
        )

        self.authenticate(self.recruiter)

        response = self.client.patch(
            f"/api/applications/{application.id}/status/",
            {
                "status": "accepted",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.PENDING,
        )

    def test_candidate_cannot_update_application_status(self):
        application = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="My application.",
        )

        self.authenticate(self.candidate)

        response = self.client.patch(
            f"/api/applications/{application.id}/status/",
            {
                "status": "accepted",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.PENDING,
        )

    def test_invalid_application_status_is_rejected(self):
        application = Application.objects.create(
            job=self.job,
            candidate=self.candidate,
            cover_letter="My application.",
        )

        self.authenticate(self.recruiter)

        response = self.client.patch(
            f"/api/applications/{application.id}/status/",
            {
                "status": "pending",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "status",
            response.data,
        )

        application.refresh_from_db()

        self.assertEqual(
            application.status,
            Application.Status.PENDING,
        )
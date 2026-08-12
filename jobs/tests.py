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
            "description": "Python developer required.",
            "company": "Test Company",
            "location": "Lahore",
            "employment_type": "full_time",
            "experience_level": "entry",
            "salary_min": "50000.00",
            "salary_max": "80000.00",
            "skills": "Python, SQL",
            "status": "open",
        }

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def create_job(self, **overrides):
        data = self.job_data.copy()
        data.update(overrides)

        self.authenticate(self.recruiter)

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            response.data,
        )

        return response

    # ---------------------------------------------------------
    # CREATE JOB
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # SALARY VALIDATION
    # ---------------------------------------------------------

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

    def test_negative_salary_max_is_rejected(self):
        self.authenticate(self.recruiter)

        data = self.job_data.copy()
        data["salary_max"] = "-5000.00"

        response = self.client.post(
            "/api/jobs/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("salary_max", response.data)

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

    # ---------------------------------------------------------
    # UPDATE
    # ---------------------------------------------------------

    def test_recruiter_can_update_own_job(self):
        response = self.create_job()

        job_id = response.data["id"]

        response = self.client.patch(
            f"/api/jobs/{job_id}/",
            {
                "title": "Senior Python Developer",
                "location": "Islamabad",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["title"],
            "Senior Python Developer",
        )

        self.assertEqual(
            response.data["location"],
            "Islamabad",
        )

    def test_recruiter_cannot_update_another_recruiters_job(self):
        response = self.create_job()

        job_id = response.data["id"]

        another_recruiter = User.objects.create_user(
            username="another_recruiter",
            email="anotherrecruiter@example.com",
            password="TestPass123!",
            user_role="recruiter",
        )

        self.authenticate(another_recruiter)

        response = self.client.patch(
            f"/api/jobs/{job_id}/",
            {
                "title": "Hacked Job",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_candidate_cannot_update_job(self):
        response = self.create_job()

        job_id = response.data["id"]

        self.authenticate(self.candidate)

        response = self.client.patch(
            f"/api/jobs/{job_id}/",
            {
                "title": "Candidate Updated Job",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ---------------------------------------------------------
    # RETRIEVE
    # ---------------------------------------------------------

    def test_candidate_can_view_job(self):
        response = self.create_job()

        job_id = response.data["id"]

        self.authenticate(self.candidate)

        response = self.client.get(
            f"/api/jobs/{job_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            job_id,
        )

    # ---------------------------------------------------------
    # DELETE
    # ---------------------------------------------------------

    def test_recruiter_can_delete_own_job(self):
        response = self.create_job()

        job_id = response.data["id"]

        response = self.client.delete(
            f"/api/jobs/{job_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Job.objects.filter(id=job_id).exists()
        )

    def test_recruiter_cannot_delete_another_recruiters_job(self):
        response = self.create_job()

        job_id = response.data["id"]

        another_recruiter = User.objects.create_user(
            username="delete_recruiter",
            email="deleterecruiter@example.com",
            password="TestPass123!",
            user_role="recruiter",
        )

        self.authenticate(another_recruiter)

        response = self.client.delete(
            f"/api/jobs/{job_id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def test_search_by_title(self):
        self.create_job(
            title="Python Developer",
            description="Python developer required.",
            skills="Python, SQL",
        )

        self.create_job(
            title="Django Backend Engineer",
            description="Backend engineer required.",
            skills="DRF, REST API",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?search=Django"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["title"],
            "Django Backend Engineer",
        )

    def test_search_by_company(self):
        self.create_job(
            title="Python Developer",
            company="Tech Solutions",
        )

        self.create_job(
            title="Frontend Developer",
            company="Design House",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?search=Tech%20Solutions"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["company"],
            "Tech Solutions",
        )

    def test_search_by_location(self):
        self.create_job(
            title="Python Developer",
            location="Lahore",
        )

        self.create_job(
            title="Frontend Developer",
            location="Islamabad",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?search=Islamabad"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["location"],
            "Islamabad",
        )

    # ---------------------------------------------------------
    # FILTERING
    # ---------------------------------------------------------

    def test_filter_by_employment_type(self):
        self.create_job(
            title="Python Developer",
            employment_type="full_time",
        )

        self.create_job(
            title="Python Intern",
            employment_type="internship",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?employment_type=internship"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["employment_type"],
            "internship",
        )

    def test_filter_by_experience_level(self):
        self.create_job(
            title="Junior Python Developer",
            experience_level="entry",
        )

        self.create_job(
            title="Senior Python Developer",
            experience_level="senior",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?experience_level=senior"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["experience_level"],
            "senior",
        )

    def test_filter_by_status(self):
        self.create_job(
            title="Open Python Developer",
            status="open",
        )

        self.create_job(
            title="Closed Python Developer",
            status="closed",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?status=closed"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["status"],
            "closed",
        )

    # ---------------------------------------------------------
    # SALARY FILTERING
    # ---------------------------------------------------------

    def test_filter_by_salary_min(self):
        self.create_job(
            title="Low Salary Job",
            salary_min="40000.00",
            salary_max="60000.00",
        )

        self.create_job(
            title="High Salary Job",
            salary_min="100000.00",
            salary_max="150000.00",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?salary_min=90000"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["title"],
            "High Salary Job",
        )

    def test_filter_by_salary_max(self):
        self.create_job(
            title="Low Salary Job",
            salary_min="40000.00",
            salary_max="60000.00",
        )

        self.create_job(
            title="High Salary Job",
            salary_min="100000.00",
            salary_max="150000.00",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?salary_max=70000"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertEqual(
            len(results),
            1,
        )

        self.assertEqual(
            results[0]["title"],
            "Low Salary Job",
        )

    # ---------------------------------------------------------
    # ORDERING
    # ---------------------------------------------------------

    def test_ordering_by_salary_min(self):
        self.create_job(
            title="Low Salary Job",
            salary_min="40000.00",
            salary_max="60000.00",
        )

        self.create_job(
            title="High Salary Job",
            salary_min="100000.00",
            salary_max="150000.00",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?ordering=salary_min"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertGreaterEqual(
            len(results),
            2,
        )

        self.assertEqual(
            results[0]["title"],
            "Low Salary Job",
        )

        self.assertEqual(
            results[1]["title"],
            "High Salary Job",
        )

    def test_ordering_by_created_at_descending(self):
        self.create_job(
            title="First Job",
        )

        self.create_job(
            title="Second Job",
        )

        self.authenticate(self.recruiter)

        response = self.client.get(
            "/api/jobs/?ordering=-created_at"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        results = response.data["results"]

        self.assertGreaterEqual(
            len(results),
            2,
        )

        self.assertEqual(
            results[0]["title"],
            "Second Job",
        )

        self.assertEqual(
            results[1]["title"],
            "First Job",
        )
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Company


User = get_user_model()


class CompanyAPITests(APITestCase):

    def setUp(self):
        self.recruiter = User.objects.create_user(
            email="recruiter1@example.com",
            username="recruiter1",
            password="TestPass123!",
            user_role="recruiter",
        )

        self.recruiter2 = User.objects.create_user(
            email="recruiter2@example.com",
            username="recruiter2",
            password="TestPass123!",
            user_role="recruiter",
        )

        self.candidate = User.objects.create_user(
            email="candidate1@example.com",
            username="candidate1",
            password="TestPass123!",
            user_role="candidate",
        )

        self.company = Company.objects.create(
            recruiter=self.recruiter,
            name="Test Company",
            description="Test company description",
            website="https://example.com",
            location="Lahore",
        )

        self.list_url = reverse("company-list-create")
        self.detail_url = reverse(
            "company-detail",
            kwargs={"pk": self.company.pk},
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_recruiter_can_create_company(self):
        self.authenticate(self.recruiter)

        response = self.client.post(
            self.list_url,
            {
                "name": "New Company",
                "description": "New company description",
                "website": "https://newcompany.com",
                "location": "Lahore",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Company")
        self.assertEqual(
            response.data["recruiter"],
            self.recruiter.email,
        )

    def test_candidate_cannot_create_company(self):
        self.authenticate(self.candidate)

        response = self.client.post(
            self.list_url,
            {
                "name": "Candidate Company",
                "description": "Should not be created",
                "website": "https://example.com",
                "location": "Lahore",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_recruiter_can_get_own_company(self):
        self.authenticate(self.recruiter)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.company.id)

    def test_recruiter_can_update_own_company(self):
        self.authenticate(self.recruiter)

        response = self.client.patch(
            self.detail_url,
            {
                "name": "Updated Company",
                "description": "Updated description",
                "website": "https://updated.com",
                "location": "Islamabad",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.company.refresh_from_db()

        self.assertEqual(
            self.company.name,
            "Updated Company",
        )
        self.assertEqual(
            self.company.location,
            "Islamabad",
        )

    def test_recruiter_can_delete_own_company(self):
        self.authenticate(self.recruiter)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            Company.objects.filter(id=self.company.id).exists()
        )

    def test_other_recruiter_cannot_update_company(self):
        self.authenticate(self.recruiter2)

        response = self.client.patch(
            self.detail_url,
            {
                "name": "Unauthorized Update",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_recruiter_cannot_delete_company(self):
        self.authenticate(self.recruiter2)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertTrue(
            Company.objects.filter(id=self.company.id).exists()
        )

    def test_invalid_website_is_rejected(self):
        self.authenticate(self.recruiter)

        response = self.client.patch(
            self.detail_url,
            {
                "website": "not-a-valid-url",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_cannot_create_company(self):
        response = self.client.post(
            self.list_url,
            {
                "name": "Unauthorized Company",
                "description": "Should not be created",
                "website": "https://example.com",
                "location": "Lahore",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class AccountsAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_candidate",
            email="candidate@example.com",
            password="TestPass123!",
            user_role="candidate",
        )

        self.register_url = reverse("register")
        self.me_url = reverse("me")

    def authenticate(self, user=None):
        user = user or self.user

        refresh = RefreshToken.for_user(user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_user_can_register(self):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPass123!",
            "phone_number": "03001234567",
            "user_role": "candidate",
        }

        response = self.client.post(
            self.register_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            User.objects.filter(
                email="newuser@example.com"
            ).exists()
        )

    def test_registration_requires_password(self):
        data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "phone_number": "03001234567",
            "user_role": "candidate",
        }

        response = self.client.post(
            self.register_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn("password", response.data)

    def test_unauthenticated_user_cannot_access_me(self):
        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_view_profile(self):
        self.authenticate()

        response = self.client.get(self.me_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["email"],
            "candidate@example.com",
        )

        self.assertEqual(
            response.data["user_role"],
            "candidate",
        )

    def test_authenticated_user_can_update_profile(self):
        self.authenticate()

        data = {
            "first_name": "Nimra",
            "last_name": "Asghar",
            "phone_number": "03001234567",
            "bio": "Python and Django developer.",
            "skills": "Python, Django, DRF, SQL, Git",
        }

        response = self.client.patch(
            self.me_url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Nimra",
        )

        self.assertEqual(
            self.user.last_name,
            "Asghar",
        )

        self.assertEqual(
            self.user.phone_number,
            "03001234567",
        )

        self.assertEqual(
            self.user.bio,
            "Python and Django developer.",
        )

        self.assertEqual(
            self.user.skills,
            "Python, Django, DRF, SQL, Git",
        )

    def test_user_cannot_change_email(self):
        self.authenticate()

        original_email = self.user.email

        response = self.client.patch(
            self.me_url,
            {
                "email": "changed@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            original_email,
        )

    def test_user_cannot_change_role(self):
        self.authenticate()

        original_role = self.user.user_role

        response = self.client.patch(
            self.me_url,
            {
                "user_role": "recruiter",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.user_role,
            original_role,
        )

    def test_user_cannot_change_verification_status(self):
        self.authenticate()

        original_status = self.user.is_verified

        response = self.client.patch(
            self.me_url,
            {
                "is_verified": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.is_verified,
            original_status,
        )
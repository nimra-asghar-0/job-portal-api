
"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


def api_home(request):
    return JsonResponse(
        {
            "message": "Job Portal API is running",
            "docs": "/api/docs/",
            "schema": "/api/schema/",
        }
    )


urlpatterns = [
    # API home
    path("", api_home, name="api-home"),

    # Django admin
    path("admin/", admin.site.urls),

    # API documentation
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Accounts
    path(
        "api/accounts/",
        include("accounts.urls"),
    ),

    # JWT authentication
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    # Jobs
    path(
        "api/jobs/",
        include("jobs.urls"),
    ),

    # Applications
    path(
        "api/applications/",
        include("applications.urls"),
    ),
    path("api/companies/", include("companies.urls")),
]
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
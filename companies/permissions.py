from rest_framework import permissions


class IsRecruiter(permissions.BasePermission):
    """
    Only users with the recruiter role can create/manage companies.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.user_role == "recruiter"
        )


class IsCompanyOwner(permissions.BasePermission):
    """
    Only the recruiter who owns the company can modify or delete it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.recruiter == request.user